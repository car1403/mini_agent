def build_prompt(role: str, instruction: str, context: str, constraint: str) -> str:
    return f"[Role]\n{role}\n\n[Instruction]\n{instruction}\n\n[Context]\n{context}\n\n[Constraint]\n{constraint}"
