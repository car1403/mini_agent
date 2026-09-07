from mcp_server.database.connection import query

def programs(term: str):
    return query("SELECT p.*, f.name AS facility_name FROM multimodal_programs p JOIN multimodal_facilities f USING(facility_id) WHERE p.program_id ILIKE %s OR p.name ILIKE %s OR f.name ILIKE %s ORDER BY p.program_id LIMIT 10", (f"%{term}%",)*3)

def sessions(program_id: str, date_from, date_to):
    return query("SELECT session_id,program_id,starts_at,capacity,reserved,capacity-reserved AS remaining,status,updated_at FROM multimodal_program_sessions WHERE program_id=%s AND (starts_at AT TIME ZONE 'Asia/Seoul')::date BETWEEN %s AND %s ORDER BY starts_at", (program_id, date_from, date_to))
