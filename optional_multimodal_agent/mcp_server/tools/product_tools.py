from datetime import datetime, timezone
from mcp_server.database import product_queries as db

def find_products(term: str) -> dict:
    """사진에서 읽은 모델 코드나 제품명으로 제품 후보를 조회합니다. 여러 후보면 사용자의 확인이 필요합니다."""
    if not term.strip() or len(term)>100:
        raise ValueError("검색어는 1~100자입니다.")
    return {"items": db.find_products(term), "source": "products"}

def get_compatible_accessories(product_id: str) -> dict:
    """확인된 제품 ID의 호환 액세서리를 DB에서 조회합니다. 외형으로 호환성을 추측하지 않습니다."""
    return {"items": db.accessories(product_id), "source": "product_compatibility"}

def get_product_availability(product_id: str) -> dict:
    """제품 또는 액세서리 ID의 매장별 재고와 가격을 조회합니다. 0은 품절입니다."""
    return {"items": db.availability(product_id), "queried_at": datetime.now(timezone.utc).isoformat(), "source": "inventory"}
