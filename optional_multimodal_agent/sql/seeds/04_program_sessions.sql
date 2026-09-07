-- seed_database.py가 같은 연결에 설정하는 기준일을 사용합니다.
-- SQL 직접 실행 시 현재 날짜가 기본값입니다.
INSERT INTO multimodal_program_sessions (session_id, program_id, starts_at, capacity, reserved, status)
SELECT p.program_id || '-' || n,
 p.program_id,
 (COALESCE(NULLIF(current_setting('app.seed_date', true), '')::date, CURRENT_DATE)
 + ((6 - EXTRACT(ISODOW FROM COALESCE(NULLIF(current_setting('app.seed_date', true), '')::date, CURRENT_DATE))::int + 7) % 7)
 + (n-1)*7 + TIME '10:00') AT TIME ZONE 'Asia/Seoul',
 12, CASE WHEN p.program_id='PG-YOGA' AND n=1 THEN 12 ELSE 4 END,
 CASE WHEN p.program_id='PG-DRAW' AND n=2 THEN 'cancelled' ELSE 'open' END
FROM multimodal_programs p CROSS JOIN generate_series(1,4) AS n
ON CONFLICT (session_id) DO NOTHING;
