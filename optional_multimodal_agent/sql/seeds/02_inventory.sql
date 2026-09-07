INSERT INTO multimodal_stores (store_id, name) VALUES
('S01','가상 중앙점'),
('S02','가상 강변점')
ON CONFLICT (store_id) DO UPDATE SET name=EXCLUDED.name;
INSERT INTO multimodal_inventory (store_id, product_id, quantity)
SELECT s.store_id, p.product_id,
 CASE WHEN p.product_id='AC-A30' THEN 0 WHEN s.store_id='S01' THEN 5 ELSE 2 END
FROM multimodal_stores s CROSS JOIN multimodal_products p
ON CONFLICT (store_id, product_id) DO NOTHING;
