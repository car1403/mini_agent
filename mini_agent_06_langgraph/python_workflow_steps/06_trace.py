def record(state: dict, node: str, status: str) -> dict:
    trace = [*state.get("trace", []), {"node": node, "status": status}]
    return {**state, "trace": trace}


state = record({}, "extract_request", "completed")
state = record(state, "validate_request", "completed")
state = record(state, "approval", "waiting_approval")
print(state)
