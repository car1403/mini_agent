from mcp_server.core.config import openai_client, env
from mcp_server.core.media import resolve, save_speech
from mcp_server.core.media_validation import validate

async def transcribe_audio(audio_id: str) -> dict:
    """녹음 파일 ID에 해당하는 WAV 음성을 한국어 질문 텍스트로 변환합니다."""
    path = resolve(audio_id)
    validate(path.read_bytes(), "audio")
    async with openai_client() as client:
        with path.open("rb") as audio:
            result = await client.audio.transcriptions.create(
                model=env("OPENAI_STT_MODEL","gpt-4o-mini-transcribe"),file=audio)
    return {"text":result.text}

async def synthesize_speech(text: str) -> dict:
    """최종 답변을 합성 음성으로 변환하고 MP3 파일 ID를 반환합니다. 최대 2000자입니다."""
    if not text.strip() or len(text)>2000:
        raise ValueError("음성으로 읽을 텍스트는 1~2000자입니다.")
    async with openai_client() as client:
        result = await client.audio.speech.create(
            model=env("OPENAI_TTS_MODEL","gpt-4o-mini-tts"),
            voice=env("OPENAI_TTS_VOICE","coral"),input=text,
            instructions="한국어로 친절하고 또렷하게 읽으세요.",response_format="mp3")
    return {"audio_id":save_speech(result.content),"format":"audio/mpeg","synthetic":True}
