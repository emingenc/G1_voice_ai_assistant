# Emotional AI Voice Chat 

Fast conversation with emotional AI

<details>
<summary>Click to show/hide video</summary>

  https://github.com/user-attachments/assets/85e786fb-4dad-438d-96a0-d01817f741ba

</details>

This project implements a real-time ai conversation system with emotional text-to-speech (TTS) capabilities. It uses a large language model (LLM) for generating responses and a TTS engine with voice-cloning for voice output.

Based on:
- Voice TTS/STT implementation from [LocalEmotionalAIVoiceChat](https://github.com/KoljaB/LocalEmotionalAIVoiceChat)
- LLM agent from [memory-agent](https://github.com/langchain-ai/memory-agent)

## Features

- Real-time speech-to-text input
- Cnversation generation powered by: Ollama, LMStudio, OpenAI, Anthropic or llama.cpp Webserver
- Emotion-aware realtime text-to-speech output
- Configurable system and user personas

## Requirements

- Python <=3.10 (3.10.9 is recommended)
- [CUDA-enabled GPU](#cuda-installation)

## Installation

1. Clone the repository
  
  ```bash
  git clone https://github.com/emingenc/G1_voice_ai_assistant.git
  cd G1_voice_ai_assistant
  ```
2. Install the required packages

  - venv (optional)

```bash
python -m venv venv
source venv/bin/activate
```
  - Install the required packages

```bash
pip install -r requirements.txt
```

3. setup the environment variables in llm_agent folder example .env file

```bash
cp llm_agent/.env.example llm_agent/.env
```

4. Langraph up and running

```bash
cd llm_agent
langraph up
```


## Usage

Run the main script after langgraph:

```
python main.py
```

The system will start a conversation based on the configured scenario. Speak into your microphone to interact with the AI character.

**Note:** When starting the application, you may see warnings similar to:

```
[ctranslate2] [warning] The compute type inferred from the saved model is float16, but the target device or backend do not support efficient float16 computation. The model weights have been automatically converted to use the float32 compute type instead.

FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
```

These warnings are normal and do not affect the functionality of the system. There's no need to worry about them.




