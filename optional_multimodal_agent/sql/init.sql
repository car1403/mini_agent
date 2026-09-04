-- 이 파일은 초기화용이므로 이번 과정 전용 테이블을 정확한 구조로 다시 만든다.
-- documents, user_memories 등 다른 과정의 공용 테이블은 삭제하지 않는다.
DROP TABLE IF EXISTS optional_multimodal_travel_tool_data;
DROP TABLE IF EXISTS optional_multimodal_agent_runs;

-- =============================================================================
-- optional_multimodal_agent_runs
-- Python Agent와 LangGraph Agent의 실행 상태, 멀티모달 분석 결과, 승인 이력 및
-- 실행 Trace를 영속화한다. 이미지 원본이나 Base64는 저장하지 않으며,
-- image_analysis에는 구조화된 분석 결과만 저장한다.
-- =============================================================================
CREATE TABLE IF NOT EXISTS optional_multimodal_agent_runs (
    -- API에서 run_id로 사용하는 실행별 고유 식별자
    id UUID PRIMARY KEY,
    -- 요청자 식별자이며 승인 및 거절 권한 검사에 사용
    user_id TEXT NOT NULL,
    -- 실제 LLM 제공자: openai, gemini 또는 ollama
    provider TEXT NOT NULL,
    -- 실행에 사용한 실제 LLM 모델 이름
    model TEXT NOT NULL DEFAULT '',
    -- running, needs_input, waiting_approval, completed, rejected 중 현재 상태
    status TEXT NOT NULL,
    -- 현재 또는 마지막으로 처리한 Agent/LangGraph 단계
    current_node TEXT NOT NULL,
    -- 목적지, 날짜, 숙박일, 인원, 예산 등 구조화된 여행 요청
    request JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- TravelImageAnalysis 결과만 저장하며 이미지 원본과 Base64는 저장하지 않음
    image_analysis JSONB,
    -- LLM 계획, Memory, 근거 문서 및 예약 요청 초안을 포함한 결과
    result JSONB,
    -- 현재 상태를 사용자에게 보여주는 안내 문장
    message TEXT NOT NULL DEFAULT '',
    -- 사용자 승인 또는 거절을 기다리는 상태인지 표시
    requires_approval BOOLEAN NOT NULL DEFAULT FALSE,
    -- Node 실행 순서, LLM 호출 및 승인 기록으로 구성된 JSON 배열
    trace JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- 실행 레코드 최초 생성 시각
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- 상태 또는 결과가 마지막으로 변경된 시각
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS optional_multimodal_agent_runs_user_created_idx
    ON optional_multimodal_agent_runs (user_id, created_at DESC);

-- 사용자별 실행 이력을 최신순으로 조회하는 화면과 API를 위한 인덱스다.

-- =============================================================================
-- optional_multimodal_travel_tool_data
-- LLM이 선택한 여행 Tool이 조회하는 실제 PostgreSQL 데이터 카탈로그다.
-- Tool별로 서로 다른 결과 구조를 지원하기 위해 payload를 JSONB로 저장한다.
-- 현재 데이터는 교육용 초기 카탈로그이며 외부 예약이나 결제를 실행하지 않는다.
-- =============================================================================
CREATE TABLE IF NOT EXISTS optional_multimodal_travel_tool_data (
    -- Tool 데이터 항목의 고유 식별자
    id UUID PRIMARY KEY,
    -- get_weather, search_hotels 또는 search_attractions 중 허용 Tool 이름
    tool_name TEXT NOT NULL,
    -- Tool 검색 조건으로 사용하는 도시 이름
    city TEXT NOT NULL,
    -- 날씨, 가격, 수용 인원, 관광지 분류 등 Tool별 실제 응답 데이터
    payload JSONB NOT NULL,
    -- Tool 데이터가 마지막으로 갱신된 시각
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS optional_multimodal_travel_tool_lookup_idx
    ON optional_multimodal_travel_tool_data (tool_name, city);

-- Tool 이름과 도시가 함께 주어지는 조회 패턴을 최적화한다.

-- 초기 데이터는 고정 UUID와 ON CONFLICT를 사용하므로 init.sql을 반복 적용해도
-- 같은 행이 중복 삽입되지 않는다.
INSERT INTO optional_multimodal_travel_tool_data (id, tool_name, city, payload)
VALUES (
    '20000000-0000-0000-0000-000000000001'::uuid,
    'get_weather',
    '부산',
    jsonb_build_object(
        'condition', '맑음',
        'temperature_c', 26,
        'provider', 'database'
    )
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO optional_multimodal_travel_tool_data (id, tool_name, city, payload)
VALUES (
    '20000000-0000-0000-0000-000000000002'::uuid,
    'search_hotels',
    '부산',
    jsonb_build_object(
        'name', '바다 호텔',
        'price_per_night', 120000,
        'capacity', 4
    )
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO optional_multimodal_travel_tool_data (id, tool_name, city, payload)
VALUES (
    '20000000-0000-0000-0000-000000000003'::uuid,
    'search_hotels',
    '부산',
    jsonb_build_object(
        'name', '도시 호텔',
        'price_per_night', 90000,
        'capacity', 2
    )
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO optional_multimodal_travel_tool_data (id, tool_name, city, payload)
VALUES (
    '20000000-0000-0000-0000-000000000004'::uuid,
    'search_attractions',
    '부산',
    jsonb_build_object(
        'name', '부산 바다 박물관',
        'category', 'culture'
    )
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO optional_multimodal_travel_tool_data (id, tool_name, city, payload)
VALUES (
    '20000000-0000-0000-0000-000000000005'::uuid,
    'search_attractions',
    '부산',
    jsonb_build_object(
        'name', '부산 해변 산책로',
        'category', 'nature'
    )
)
ON CONFLICT (id) DO NOTHING;
