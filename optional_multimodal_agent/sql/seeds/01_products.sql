INSERT INTO multimodal_products (product_id, name, category, price, description) VALUES
('MM-K100','모아 전기주전자','kettle',39000,'1리터 전기주전자'),
('MM-C200','모아 커피메이커','coffee',79000,'드립 커피메이커'),
('MM-A300','모아 공기청정기','air',129000,'소형 공기청정기'),
('MM-L400','모아 독서등','lamp',29000,'밝기 조절 독서등'),
('MM-V500','모아 청소기','vacuum',159000,'무선 소형 청소기'),
('AC-K10','주전자 필터','accessory',5000,'K100 전용 필터'),
('AC-C20','커피 필터','accessory',7000,'C200 전용 필터'),
('AC-A30','공기청정 필터','accessory',25000,'A300 전용 필터'),
('AC-L40','독서등 어댑터','accessory',12000,'L400 전용 어댑터'),
('AC-V50','청소기 브러시','accessory',15000,'V500 전용 브러시')
ON CONFLICT (product_id) DO UPDATE SET name=EXCLUDED.name, category=EXCLUDED.category,
price=EXCLUDED.price, description=EXCLUDED.description;
INSERT INTO multimodal_product_compatibility (product_id, accessory_id) VALUES
('MM-K100','AC-K10'),('MM-C200','AC-C20'),('MM-A300','AC-A30'),
('MM-L400','AC-L40'),('MM-V500','AC-V50') ON CONFLICT DO NOTHING;
