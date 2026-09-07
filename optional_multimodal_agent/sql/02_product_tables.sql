CREATE TABLE IF NOT EXISTS multimodal_products (
    product_id text PRIMARY KEY,
    name text NOT NULL,
    category text NOT NULL,
    price integer NOT NULL CHECK (price >= 0),
    description text NOT NULL
);
CREATE TABLE IF NOT EXISTS multimodal_product_compatibility (
    product_id text REFERENCES multimodal_products(product_id),
    accessory_id text REFERENCES multimodal_products(product_id),
    PRIMARY KEY (product_id, accessory_id),
    CHECK (product_id <> accessory_id)
);
CREATE TABLE IF NOT EXISTS multimodal_stores (
    store_id text PRIMARY KEY,
    name text NOT NULL
);
CREATE TABLE IF NOT EXISTS multimodal_inventory (
    store_id text REFERENCES multimodal_stores(store_id),
    product_id text REFERENCES multimodal_products(product_id),
    quantity integer NOT NULL CHECK (quantity >= 0),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (store_id, product_id)
);
