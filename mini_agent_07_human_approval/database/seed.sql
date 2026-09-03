INSERT INTO hotels (hotel_id,name,city,nightly_price,cancellation_policy,available_rooms) VALUES
('hotel-busan-001','바다 호텔','부산',130000,'체크인 3일 전까지 전액 환불',5),
('hotel-busan-002','항구 호텔','부산',145000,'체크인 7일 전까지 전액 환불',3),
('hotel-seoul-001','도시 호텔','서울',120000,'체크인 2일 전까지 전액 환불',4),
('hotel-jeju-001','오름 호텔','제주',110000,'체크인 5일 전까지 전액 환불',6)
ON CONFLICT (hotel_id) DO NOTHING;
