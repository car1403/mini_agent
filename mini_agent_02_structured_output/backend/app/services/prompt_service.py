def build_prompt(
    role: str,
    instruction: str,
    context: str,
    constraint: str,
    output_format: str = "",
) -> str:
    prompt = (
        f"[Role]\n{role}\n\n"
        f"[Instruction]\n{instruction}\n\n"
        f"[Context]\n{context}\n\n"
        f"[Constraint]\n{constraint}"
    )
    if output_format:
        prompt += f"\n\n[Output Format]\n{output_format}"
    return prompt
