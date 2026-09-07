"""가상 문서와 촬영용 글자 카드를 생성합니다. 외부 이미지 다운로드는 없습니다."""
import json
import sys
from pathlib import Path

# `python scripts/create_samples.py` 실행도 지원합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw, ImageFont
from shared.config import ROOT

PRODUCTS = [
    ("MM-K100","모아 전기주전자","물을 MIN 0.3L 이상 MAX 1.0L 이하로 채우고 뚜껑을 닫은 뒤 스위치를 누릅니다. 물 없이 작동하지 마세요.","AC-K10"),
    ("MM-C200","모아 커피메이커","전용 종이 필터를 끼우고 분쇄 원두와 물을 넣어 추출 버튼을 누릅니다. 물통은 0.6L 이하로 채웁니다.","AC-C20"),
    ("MM-A300","모아 공기청정기","필터 비닐을 제거하고 벽에서 20cm 이상 떨어뜨려 설치합니다. 필터는 물로 씻지 마세요.","AC-A30"),
    ("MM-L400","모아 독서등","전용 어댑터를 연결하고 전원 버튼을 누릅니다. 밝기 버튼으로 3단계 밝기를 선택합니다.","AC-L40"),
    ("MM-V500","모아 청소기","배터리를 충전한 뒤 브러시를 연결하고 전원을 켭니다. 액체나 뜨거운 재는 흡입하지 마세요.","AC-V50"),
]
PROGRAMS = [
    ("PG-YOGA","초보 요가","F01","성인 초보자 참여 가능. 편한 운동복과 개인 요가 매트를 준비하세요."),
    ("PG-POTTERY","입문 도예","F01","만 14세 이상 참여 가능. 앞치마를 준비하세요. 흙과 도구는 제공됩니다."),
    ("PG-DRAW","기초 드로잉","F01","성인 초보자 참여 가능. 연필과 지우개를 준비하세요. 종이는 제공됩니다."),
    ("PG-BOOK","독서 모임","F02","성인 참여 가능. 읽은 책 한 권을 가져오세요. 참가비는 없습니다."),
    ("PG-CODE","파이썬 첫걸음","F02","만 14세 이상 초보자 참여 가능. Python이 설치된 개인 노트북을 준비하세요."),
    ("PG-STORY","어린이 이야기 시간","F02","7~10세 어린이가 보호자와 함께 참여합니다. 보호자는 수업 중 동반해야 합니다."),
]

def font(size):
    for name in ("C:/Windows/Fonts/malgun.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(name).is_file():
            return ImageFont.truetype(name,size)
    return ImageFont.load_default()

def card(path, title, code, lines):
    image = Image.new("RGB",(1200,760),"#f3f5f7")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40,40,1160,720),radius=24,fill="white",outline="#34546b",width=3)
    for y,text,size,color in [(90,"MULTIMODAL LAB / 가상 실습 자료",30,"#34546b"),
                              (170,title,48,"#172d3c"),(260,code,58,"#136950")]:
        draw.text((85,y),text,font=font(size),fill=color)
    for i,line in enumerate(lines):
        draw.text((85,370+i*64),line,font=font(30),fill="#253747")
    path.parent.mkdir(parents=True,exist_ok=True)
    image.save(path)

def generate():
    document_count = 0
    def document(doc_id,title,body,folder):
        nonlocal document_count
        relative = f"{folder}/{doc_id}.md"
        path = ROOT/"data/rag"/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(f"# {title}\n\n가상 실습 자료입니다. 대상 코드: {doc_id}\n\n{body}\n",encoding="utf-8")
        document_count += 1
    for code,name,usage,accessory in PRODUCTS:
        document(code,name+" 사용 설명서",
                 f"## 사용법\n{usage}\n\n## 호환 액세서리\n전용 액세서리 코드는 {accessory}입니다. 호환 관계와 현재 재고는 DB에서 확인하세요.\n\n## 관리\n청소 전 전원을 분리하세요. 본체를 물에 담그지 마세요.","products")
        card(ROOT/f"data/samples/product_labels/{code}.png",name,code,["제품 모델명 확인용 라벨","사용법은 모델별 매뉴얼을 확인하세요.","가격과 재고는 조회 시점에 확인합니다."])
    for code,name,facility,guide in PROGRAMS:
        document(code,name+" 참가 안내",
                 f"## 참가 조건과 준비물\n{guide}\n\n## 일정 확인\n운영 일정과 잔여 정원은 현재 DB에서 확인해야 합니다. 안내문의 모집 표시는 실시간 정보가 아닙니다.","facilities")
        card(ROOT/f"data/samples/facility_notices/{code}.png",name,code,[f"시설 코드: {facility}","토요일 오전 10시 / 모집 중 (게시 당시)","현재 잔여 정원은 별도로 확인하세요.","가상 게시일: 2026-01-01"])
    for code,name in [("F01","모아문화센터"),("F02","모아도서관")]:
        document(code,name+" 이용 규정",
                 "## 이용 안내\n시작 10분 전 도착하세요. 실내 음식물 섭취는 금지합니다.\n\n## 취소 규정\n수업 시작 24시간 전까지 취소할 수 있습니다. 이후 취소는 안내 데스크에 문의하세요. 취소된 회차에는 참여할 수 없습니다.","facilities")
    card(ROOT/"data/samples/product_labels/unclear.png","제품 라벨 일부 누락","MM-????",["모델 코드 판독 불가 실습","정확한 모델을 확인하도록 요청하세요."])
    scenarios = [
        {"id":"product_basic","image":"product_labels/MM-K100.png","question":"사용법과 호환 필터, 매장별 재고를 알려줘.","checks":["MM-K100 확인","매뉴얼 출처","AC-K10 호환 관계","재고 조회 시각"]},
        {"id":"out_of_stock","image":"product_labels/MM-A300.png","question":"필터 교체 시 주의사항과 호환 필터 재고를 알려줘.","checks":["필터 물세척 금지","AC-A30 품절"]},
        {"id":"unclear","image":"product_labels/unclear.png","question":"사용법 알려줘.","checks":["모델 확정 금지","추가 입력 요청"]},
        {"id":"facility_full","image":"facility_notices/PG-YOGA.png","question":"초보자도 가능한가요? 오늘부터 28일 동안 토요일 잔여 정원을 알려줘.","checks":["초보자 가능","개인 요가 매트","첫 회차 마감","안내문과 DB 차이"]},
        {"id":"cancelled","image":"facility_notices/PG-DRAW.png","question":"앞으로 28일간 일정과 준비물을 알려줘.","checks":["두 번째 회차 취소","연필과 지우개"]},
        {"id":"no_evidence","image":"product_labels/MM-K100.png","question":"이 제품의 해외 전압 호환 여부를 알려줘.","checks":["근거 없음 표시","전압 추측 금지"]}
    ]
    scenario_file = {
        "_comment": "두 Agent의 수동 실습 시나리오입니다. checks는 자동 채점 규칙이 아닙니다.",
        "_usage": [
            "Streamlit에서 image 파일을 올리고 question을 입력합니다.",
            "완료 후 checks가 분석·RAG·DB 결과에 반영됐는지 확인합니다.",
            "시설 일정은 seed 기준일에 따라 달라질 수 있습니다.",
        ],
        "_field_guide": {
            "id": "시나리오 식별자입니다.",
            "image": "data/samples 기준 샘플 이미지 상대 경로입니다.",
            "question": "Agent에 전달할 예제 질문입니다.",
            "checks": "학습자가 확인할 핵심 동작 목록입니다.",
        },
        "scenarios": scenarios,
    }
    (ROOT/"data/samples/scenarios.json").write_text(json.dumps(scenario_file,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"생성 완료: RAG 문서 {document_count}개, 촬영 카드 12개, 시나리오 6개")

if __name__ == "__main__":
    generate()
