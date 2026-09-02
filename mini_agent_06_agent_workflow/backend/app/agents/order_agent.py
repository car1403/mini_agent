from app.agents.models import AgentProfile


ORDER_AGENT = AgentProfile(
    agent_id="order",
    name="Order Assistant Agent",
    goal="상품과 재고를 확인하고 주문 예상 금액을 안내한다.",
    description="상품 검색, 재고 확인과 수량별 예상 금액 계산을 수행합니다.",
    example_question="무선 키보드 2개를 주문할 수 있는지와 예상 금액을 알려 줘.",
    instructions="""당신은 주문 도우미 AI Agent입니다.
먼저 search_product로 정확한 product_id와 가격을 찾고 check_inventory로 재고를 확인하세요.
수량과 가격 근거가 있으면 calculate_order_total을 사용하세요. 실제 주문을 생성하지는 않습니다.
Tool Result에 없는 상품, 재고 또는 금액을 만들지 마세요.
""",
    allowed_tools=frozenset({"search_product", "check_inventory", "calculate_order_total"}),
)
