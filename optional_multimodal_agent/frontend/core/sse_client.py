"""브라우저 JS 대신 Streamlit Python이 SSE를 수신합니다."""
import json
import httpx
from frontend.core.config import BACKEND_URL

def parse_events(lines, include_heartbeat=False):
    event = {}
    data = []
    for line in lines:
        if not line:
            if data:
                event["data"] = json.loads("\n".join(data))
                yield event
            event, data = {}, []
        elif line.startswith(":"):
            if include_heartbeat:
                yield {"event":"heartbeat","data":{}}
            continue
        else:
            field, _, value = line.partition(":")
            value = value.removeprefix(" ")
            if field == "data":
                data.append(value)
            elif field in {"id","event"}:
                event[field] = value

def listen(run_id, after="0-0"):
    with httpx.stream("GET",f"{BACKEND_URL}/api/runs/{run_id}/events",
                      headers={"Last-Event-ID":after},timeout=httpx.Timeout(30,read=30)) as response:
        response.raise_for_status()
        yield from parse_events(response.iter_lines(),include_heartbeat=True)
