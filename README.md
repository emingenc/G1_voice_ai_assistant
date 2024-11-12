# Emotional AI Voice Chat 

Fast conversation with emotional AI with even-realities G1 smart glass connection

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
- Docker for redis and langraph

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




## Usage

Run the scripts in different terminals to start the system:

1. start the langraph

```bash
cd llm_agent
langgraph up
cd ..
```

2. start the redis

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

3. start g1 smart glass connection

```bash
python g1_smart_glass.py
```

4. start the voice ai assistant

```bash
python voice_ai_assistant.py
```




