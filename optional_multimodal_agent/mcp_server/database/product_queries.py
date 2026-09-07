from mcp_server.database.connection import query

def find_products(term: str):
    return query("SELECT * FROM multimodal_products WHERE product_id ILIKE %s OR name ILIKE %s ORDER BY product_id LIMIT 10",
                 (f"%{term}%", f"%{term}%"))

def accessories(product_id: str):
    return query("SELECT p.* FROM multimodal_product_compatibility c JOIN multimodal_products p ON p.product_id=c.accessory_id WHERE c.product_id=%s", (product_id,))

def availability(product_id: str):
    return query("SELECT p.product_id,p.name,p.price,s.name AS store,i.quantity,i.updated_at FROM multimodal_inventory i JOIN multimodal_stores s USING(store_id) JOIN multimodal_products p USING(product_id) WHERE i.product_id=%s ORDER BY s.store_id", (product_id,))
