import os
import re
import time
import json
from typing import List
from dataclasses import dataclass
from handlers.tts_handler import TTSHandler
from RealtimeSTT import AudioToTextRecorder
import logging
from handlers.llm_handler import LLMHandler
import asyncio
from handlers.g1_handler import G1Handler


@dataclass
class Config:
    print_emotions: bool = True
    print_llm_text: bool = True
    use_tts: bool = False
    dbg_log: bool = True
    log_level_nondebug = logging.WARNING
    references_folder: str = "reference_wavs"
    stt_model: str = "tiny.en"
    stt_language: str = "en"
    stt_silence_duration: float = 0.2
    chat_params_file: str = "chat_params.json"    
    tts_config_file: str = "tts_config.json"
    use_g1_glasses: bool = True 


def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

class Main:
    def __init__(self, config: Config, g1_handler=None):
        self.config = config
        self.setup_logging()
        self.valid_emotions = self.get_valid_emotions()

        # Load chat parameters
        with open(config.chat_params_file, 'r') as f:
            self.chat_params = json.load(f)

        print("Loading STT")
        self.recorder = AudioToTextRecorder(
            model=config.stt_model,
            language=config.stt_language,
            spinner=False,
            post_speech_silence_duration=config.stt_silence_duration
        )
        self.llm_handler = LLMHandler()


        self.tts_handler = TTSHandler(config.tts_config_file) if config.use_tts else None        
        
        # Token processing state
        self.plain_text = ""
        self.last_plain_text = ""
        self.buffer = ""
        self.in_emotion = False
        self.last_char = ""
        self.assistant_text = ""  # New variable to store complete assistant response

        # Initialize G1Handler if use_g1_glasses is True
        self.g1_handler = None
        if config.use_g1_glasses:
            self.g1_handler = g1_handler
            if not self.g1_handler.connected:
                logging.warning("G1 glasses failed to connect, continuing without glasses")

    def setup_logging(self):
        level = logging.DEBUG if self.config.dbg_log else self.config.log_level_nondebug
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_valid_emotions(self) -> List[str]:
        with open(self.config.tts_config_file, 'r') as f:
            tts_config = json.load(f)
        references_folder = tts_config['references_folder']
        return [os.path.splitext(f)[0] for f in os.listdir(references_folder) if f.endswith('.wav')]        

    def print_available_emotions(self):
        emotions_str = ', '.join(f'(\033[0;91m{emotion.lower()}\033[0m)' for emotion in self.valid_emotions)
        print(f"Available emotions: {emotions_str}\n")

  
    def print_character_info(self):

        char_name = color_text(self.chat_params['char'], '96')  # Light Cyan

        print(f"Assistant Name: {char_name}")
        print()  # Extra line for spacing

    def process_llm_token(self, token: str):
        """Process a single token from the LLM response."""
        if not isinstance(token, str):
            logging.warning(f"Unexpected token type: {type(token)}")
            return
            
        for char in token:
            if not isinstance(char, str):
                continue
                
            self.assistant_text += char
            
            if char == '[':
                if self.buffer:
                    self.process_buffer()
                self.buffer = '['
                self.in_emotion = True
            elif char == ']' and self.in_emotion:
                self.buffer += ']'
                self.process_emotion()
                self.buffer = ""
                self.in_emotion = False
            else:
                self.buffer += char
                if not self.in_emotion and self.buffer:
                    self.process_buffer()
            self.last_char = char

        

    def process_buffer(self):
        new_text = self.process_plain_text(self.buffer)
        if self.tts_handler:
            self.tts_handler.sentence_queue.add_text(new_text)
        self.buffer = ""

    def process_plain_text(self, text: str) -> str:
        self.plain_text += text
        self.plain_text = re.sub(r'\n', '', self.plain_text)    # Remove all linebreaks
        self.plain_text = re.sub(r'^\s+', '', self.plain_text)
        self.plain_text = re.sub(r'\s+', ' ', self.plain_text)  # Replace multiple whitespaces with a single space
        new_text = self.plain_text[len(self.last_plain_text):]
        self.last_plain_text = self.plain_text
        if self.config.print_llm_text:
            print(f"\033[96m{new_text}\033[0m", end='', flush=True)
        return new_text

    def process_emotion(self):
        emotion = self.buffer[1:-1].lower()
        current_emotion = "neutral" if emotion not in self.valid_emotions else emotion
        if self.config.print_emotions:
            print(f"(\033[0;91m{current_emotion.lower()}\033[0m) ", end='', flush=True)
        if self.tts_handler:
            self.tts_handler.sentence_queue.add_emotion(current_emotion)

    async def run(self):
        self.print_available_emotions()
        self.print_character_info()
        #self.print_scenario()
       
        while True:
            user_text = self.get_user_input()
            if self.should_exit(user_text):
                break

            await self.process_user_input(user_text)

        self.cleanup()

    def get_user_input(self) -> str:
        user_name = color_text("User", '93')  # Light Green

        print(f"\n>>> {user_name}: ", end="", flush=True)

        user_text = ""
        while len(user_text.strip()) == 0:
            user_text = self.recorder.text()
        colored_user_text = color_text(user_text, '93')
        print(colored_user_text)
        return user_text

    def should_exit(self, user_text: str) -> bool:
        return len(user_text) <= 7 and "exit" in user_text.lower()

    async def process_user_input(self, user_text: str):
        char_name = color_text(self.chat_params['char'], '96')
        print(f"<<< {char_name}: ", end="", flush=True)


        # Reset token processing state
        self.plain_text = ""
        self.last_plain_text = ""
        self.buffer = ""
        self.in_emotion = False
        self.last_char = ""
        self.assistant_text = ""

        if self.tts_handler:
            self.tts_handler.initialize_pyaudio()
            self.tts_handler.start_threads()

        # Remove the await from the callback
        response = await self.llm_handler.generate_response(
            user_text,
            on_token=self.process_llm_token  # Pass the method directly
        )
        
        # Send token to G1 glasses if enabled
        if response and self.g1_handler:
            await self.g1_handler.send_text_async(response[-1])
        
        if self.buffer:
            self.process_buffer()

        if self.tts_handler:
            self.tts_handler.sentence_queue.finish_current_sentence()
            self.wait_for_tts_completion()

    def wait_for_tts_completion(self):
        if not self.tts_handler:
            return

        logging.debug("Waiting for TTS to finish processing...")
        not_playing_start_time = None
        while True:
            if self.tts_handler.sentence_queue.is_empty():
                finished_playout = (
                    not self.tts_handler.stream.is_playing() and
                    self.tts_handler.sentence_queue.is_empty() and
                    self.tts_handler.chunk_queue.empty()
                )
                if finished_playout:
                    if not_playing_start_time is None:
                        not_playing_start_time = time.time()
                    if time.time() - not_playing_start_time >= 0.5:
                        break
                else:
                    not_playing_start_time = None
            time.sleep(0.01)

        logging.debug("All sentences processed and TTS playback completed.")
        self.tts_handler.stop_event.set()
        self.tts_handler.tts_sentence_thread.join()
        self.tts_handler.shutdown_pyaudio()

    def cleanup(self):
        if self.tts_handler:
            logging.debug("Shutting down TTS engine...")
            self.tts_handler.engine.shutdown()
            logging.debug("TTS shutdown complete.")
            
        if self.g1_handler:
            logging.debug("Cleaning up G1 glasses connection...")
            self.g1_handler.cleanup()

async def setup():
    g1_handler = G1Handler()
    await g1_handler.initialize()
    return g1_handler

async def main_async():
    config = Config()
    g1_handler = await setup()
    main = Main(config, g1_handler)
    await main.run()

if __name__ == '__main__':
    asyncio.run(main_async())