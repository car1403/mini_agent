"""mcp_server 디렉터리에서 실행: python main.py"""
import sys
from pathlib import Path

# 이 파일을 직접 실행해도 프로젝트 루트의 패키지를 찾을 수 있게 합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from shared.config import env
from mcp_server.tools.image_tools import analyze_scene, read_document
from mcp_server.tools.audio_tools import transcribe_audio, synthesize_speech
from mcp_server.tools.product_tools import find_products, get_compatible_accessories, get_product_availability
from mcp_server.tools.facility_tools import find_programs, get_program_sessions
from mcp_server.tools.rag_tools import search_product_manuals, search_facility_guides

mcp = FastMCP("multimodal-tools",host=env("MCP_HOST","127.0.0.1"),
              port=int(env("MCP_PORT","8020")),stateless_http=True,json_response=True)
for tool in (analyze_scene,read_document,transcribe_audio,synthesize_speech,
             find_products,get_compatible_accessories,get_product_availability,
             find_programs,get_program_sessions,search_product_manuals,search_facility_guides):
    mcp.tool()(tool)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
