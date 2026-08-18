"""실행: python 06_openai_tts.py"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
output_path = Path(__file__).with_name("travel-guide.mp3")

with client.audio.speech.with_streaming_response.create(
    model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
    voice=os.getenv("OPENAI_TTS_VOICE", "coral"),
    input="서울역에서 출발하기 전 승차권의 시간과 플랫폼을 확인하세요.",
    instructions="한국어로 또렷하고 따뜻한 여행 가이드처럼 말하세요.",
) as response:
    response.stream_to_file(output_path)

print("AI 합성 음성을 생성했습니다:", output_path)
