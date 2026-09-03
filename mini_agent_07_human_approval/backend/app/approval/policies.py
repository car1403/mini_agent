from typing import Literal


Risk = Literal["read", "change", "forbidden"]

CHANGE_TOOLS = frozenset({"place_order"})
FORBIDDEN_TOOLS = frozenset({"make_payment", "change_user_role"})


def action_risk(tool_name: str) -> Risk:
    if tool_name in FORBIDDEN_TOOLS:
        return "forbidden"
    if tool_name in CHANGE_TOOLS:
        return "change"
    return "read"
