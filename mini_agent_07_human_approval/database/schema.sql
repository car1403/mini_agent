CREATE TABLE IF NOT EXISTS hotels (
    hotel_id TEXT PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL,
    nightly_price INTEGER NOT NULL CHECK (nightly_price > 0),
    cancellation_policy TEXT NOT NULL, available_rooms INTEGER NOT NULL CHECK (available_rooms >= 0)
);
CREATE TABLE IF NOT EXISTS agent_runs (
    run_id TEXT PRIMARY KEY, actor_id TEXT NOT NULL, question TEXT NOT NULL,
    status TEXT NOT NULL, state JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS hotel_search_candidates (
    run_id TEXT NOT NULL REFERENCES agent_runs(run_id), hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id),
    snapshot JSONB NOT NULL, PRIMARY KEY (run_id, hotel_id)
);
CREATE TABLE IF NOT EXISTS approval_requests (
    approval_id UUID PRIMARY KEY, run_id TEXT NOT NULL UNIQUE REFERENCES agent_runs(run_id),
    actor_id TEXT NOT NULL, target JSONB NOT NULL, target_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('waiting','approved','rejected','consumed')),
    decided_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id UUID PRIMARY KEY, approval_id UUID NOT NULL UNIQUE REFERENCES approval_requests(approval_id),
    actor_id TEXT NOT NULL, hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id), check_in DATE NOT NULL,
    nights INTEGER NOT NULL CHECK (nights > 0), guests INTEGER NOT NULL CHECK (guests > 0),
    total_price INTEGER NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY, run_id TEXT NOT NULL REFERENCES agent_runs(run_id), actor_id TEXT NOT NULL,
    event_type TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
