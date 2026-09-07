INSERT INTO multimodal_facilities (facility_id, name, location) VALUES
('F01','가상 모아문화센터','가상시 중앙로 10'),
('F02','가상 모아도서관','가상시 강변로 20')
ON CONFLICT (facility_id) DO UPDATE SET name=EXCLUDED.name, location=EXCLUDED.location;
INSERT INTO multimodal_programs (program_id, facility_id, name, audience, fee) VALUES
('PG-YOGA','F01','초보 요가','성인 초보자',10000),
('PG-POTTERY','F01','입문 도예','만 14세 이상',20000),
('PG-DRAW','F01','기초 드로잉','성인 초보자',15000),
('PG-BOOK','F02','독서 모임','성인',0),
('PG-CODE','F02','파이썬 첫걸음','만 14세 이상 초보자',5000),
('PG-STORY','F02','어린이 이야기 시간','7~10세 어린이와 보호자',0)
ON CONFLICT (program_id) DO UPDATE SET
facility_id=EXCLUDED.facility_id,
name=EXCLUDED.name,
audience=EXCLUDED.audience,
fee=EXCLUDED.fee;
