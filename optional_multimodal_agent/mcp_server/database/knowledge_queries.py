from mcp_server.database.connection import query

def search(vector: str, kind: str, target_id: str, model: str):
    # 테이블명은 외부 입력으로 조합하지 않습니다.
    return query("""
      SELECT d.document_id,d.title,d.source_path,
             c.chunk_index,c.section,c.content,1-(c.embedding <=> %s::vector) AS similarity
      FROM multimodal_knowledge_chunks c JOIN multimodal_knowledge_documents d USING(document_id)
      WHERE d.embedding_model=%s AND d.embedding_dimensions=768
      AND (
        (%s='product' AND EXISTS (SELECT 1 FROM multimodal_product_documents x WHERE x.document_id=d.document_id AND x.product_id=%s))
        OR (%s='program' AND (
          EXISTS (SELECT 1 FROM multimodal_program_documents x WHERE x.document_id=d.document_id AND x.program_id=%s)
          OR EXISTS (SELECT 1 FROM multimodal_facility_documents x JOIN multimodal_programs p USING(facility_id) WHERE x.document_id=d.document_id AND p.program_id=%s)
        ))
      ) ORDER BY c.embedding <=> %s::vector LIMIT 4
    """, (vector,model,kind,target_id,kind,target_id,target_id,vector))
