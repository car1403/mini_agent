CREATE TABLE IF NOT EXISTS multimodal_knowledge_documents (
    document_id text PRIMARY KEY,
    title text NOT NULL,
    source_path text NOT NULL,
    embedding_model text NOT NULL,
    embedding_dimensions integer NOT NULL CHECK (embedding_dimensions = 768)
);
CREATE TABLE IF NOT EXISTS multimodal_knowledge_chunks (
    document_id text REFERENCES multimodal_knowledge_documents(document_id) ON DELETE CASCADE,
    chunk_index integer NOT NULL,
    section text NOT NULL,
    content text NOT NULL,
    embedding vector(768) NOT NULL,
    PRIMARY KEY (document_id, chunk_index)
);
CREATE TABLE IF NOT EXISTS multimodal_product_documents (
    product_id text REFERENCES multimodal_products(product_id),
    document_id text REFERENCES multimodal_knowledge_documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, document_id)
);
CREATE TABLE IF NOT EXISTS multimodal_facility_documents (
    facility_id text REFERENCES multimodal_facilities(facility_id),
    document_id text REFERENCES multimodal_knowledge_documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (facility_id, document_id)
);
CREATE TABLE IF NOT EXISTS multimodal_program_documents (
    program_id text REFERENCES multimodal_programs(program_id),
    document_id text REFERENCES multimodal_knowledge_documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (program_id, document_id)
);
