import io
import fakeredis.aioredis
from fastapi.testclient import TestClient
from backend_python.app.main import app
from shared import media_storage
from tests.test_media import png

def test_upload_run_replay_and_followup(tmp_path,monkeypatch):
    monkeypatch.setattr(media_storage,"STORAGE",tmp_path)
    with TestClient(app) as client:
        app.state.redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        bad = client.post("/api/media/image",files={"file":("bad.png",b"not image","image/png")})
        assert bad.status_code==400
        image = client.post("/api/media/image",files={"file":("ok.png",png(),"image/png")}).json()["media_id"]
        assert client.get(f"/api/media/{image}").status_code==200
        created = client.post("/api/runs",json={"agent":"product","image_id":image,"question":"사용법"})
        assert created.status_code==202
        run_id = created.json()["run_id"]
        assert client.get(f"/api/runs/{run_id}").json()["status"]=="queued"
        assert client.post(f"/api/runs/{run_id}/input",json={"question":"더 알려줘"}).status_code==409
        assert client.get(f"/api/runs/{run_id}/events",headers={"Last-Event-ID":"invalid"}).status_code==400
        assert client.get("/api/runs/missing").status_code==404

def test_wrong_media_type_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(media_storage,"STORAGE",tmp_path)
    with TestClient(app) as client:
        app.state.redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        image = client.post("/api/media/image",files={"file":("ok.png",png(),"image/png")}).json()["media_id"]
        response = client.post("/api/runs",json={"agent":"product","image_id":image,"audio_id":image})
        assert response.status_code==400
