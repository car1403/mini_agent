"""실제 로컬 HTTP MCP 전송을 검증합니다. DB·모델 API는 호출하지 않습니다."""
import asyncio
import os
import socket
import subprocess
import sys
import time
import pytest
from backend.app.mcp import client

def test_mcp_discovery_and_tool_error(monkeypatch):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port = sock.getsockname()[1]
    environment = dict(os.environ,MCP_PORT=str(port),MCP_HOST="127.0.0.1")
    process = subprocess.Popen([sys.executable,"-m","mcp_server.main"],env=environment,
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
    try:
        deadline = time.monotonic()+15
        while time.monotonic()<deadline:
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1",port))==0:
                    break
            if process.poll() is not None:
                pytest.fail("MCP Server exited during startup")
            time.sleep(.1)
        else:
            pytest.fail("MCP startup timeout")
        monkeypatch.setattr(client,"MCP_URL",f"http://127.0.0.1:{port}/mcp")
        async def check():
            async with client.tools_session() as session:
                listed = (await session.list_tools()).tools
                assert len(listed)==11
                assert {"analyze_scene","read_document","search_product_manuals","get_program_sessions"} <= {t.name for t in listed}
                with pytest.raises(RuntimeError,match="find_products"):
                    await client.call(session,"find_products",{"term":""},{"find_products"})
        asyncio.run(check())
    finally:
        process.terminate()
        process.wait(timeout=10)
