import io
import wave
import pytest
from PIL import Image
from shared.media_validation import validate
from shared import media_storage

def png():
    buffer = io.BytesIO()
    Image.new("RGB",(20,20)).save(buffer,"PNG")
    return buffer.getvalue()

def test_image_content_validation():
    assert validate(png(),"image")==".png"
    with pytest.raises(ValueError):
        validate(b"not really a PNG","image")

def test_audio_limit():
    buffer = io.BytesIO()
    with wave.open(buffer,"wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(8000)
        file.writeframes(b"\0\0"*8000*121)
    with pytest.raises(ValueError,match="120"):
        validate(buffer.getvalue(),"audio")

def test_storage_rejects_paths(tmp_path,monkeypatch):
    monkeypatch.setattr(media_storage,"STORAGE",tmp_path)
    media_id = media_storage.save(png(),"image")
    assert media_storage.resolve(media_id).read_bytes()==png()
    with pytest.raises(ValueError):
        media_storage.resolve("../../.env")
