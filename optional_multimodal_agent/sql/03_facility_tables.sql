CREATE TABLE IF NOT EXISTS multimodal_facilities (
    facility_id text PRIMARY KEY,
    name text NOT NULL,
    location text NOT NULL
);
CREATE TABLE IF NOT EXISTS multimodal_programs (
    program_id text PRIMARY KEY,
    facility_id text NOT NULL REFERENCES multimodal_facilities(facility_id),
    name text NOT NULL,
    audience text NOT NULL,
    fee integer NOT NULL CHECK (fee >= 0)
);
CREATE TABLE IF NOT EXISTS multimodal_program_sessions (
    session_id text PRIMARY KEY,
    program_id text NOT NULL REFERENCES multimodal_programs(program_id),
    starts_at timestamptz NOT NULL,
    capacity integer NOT NULL CHECK (capacity > 0),
    reserved integer NOT NULL CHECK (reserved >= 0 AND reserved <= capacity),
    status text NOT NULL CHECK (status IN ('open', 'cancelled')),
    updated_at timestamptz NOT NULL DEFAULT now()
);
