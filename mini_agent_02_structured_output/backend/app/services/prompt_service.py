def build_prompt(role: str, instruction: str, context: str, constraint: str) -> str:
    return (
        f"[Role]\n{role}\n\n"
        f"[Instruction]\n{instruction}\n\n"
        f"[Context]\n{context}\n\n"
        f"[Constraint]\n{constraint}"
    )
