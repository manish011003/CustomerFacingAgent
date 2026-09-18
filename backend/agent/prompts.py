"""Extract and respond prompt contracts.

Rendered from an assembled CustomerAgentContext. Never dump the data pack
into a mega-prompt. The assembler decides retrieve vs compute vs forbid;
these strings only phrase what is already in the packet.
"""

from agent.context import (
    RAW_POLICY_MARKERS,
    context_contains_forbidden,
    render_extract_prompt,
    render_respond_prompt,
)

# What the assembler may pull from ES/JSON for this passenger only.
RETRIEVE = (
    "this passenger profile",
    "this booking / affected leg",
    "this session's events",
    "this passenger's graph edges",
)

# What Python computes and injects as facts. The model does not recalculate these.
COMPUTE = (
    "entitlements and ALLOW/DENY/ASK/ESCALATE",
    "fare waiver versus ₹1500",
    "hotel delayed-hours versus full night",
    "Gold/Platinum = priority rebooking only, no extra compensation",
)

# Must never appear in extract or respond prompts as usable facts.
FORBID = (
    "other passengers",
    "raw policies.json for the model to reinterpret",
    "unstated inventory / replacement flight numbers",
    "prior-complaint outcomes as new benefits",
    "sample conversations as facts",
)

EXTRACT_FIELDS = (
    "emotion",
    "legal_or_formal",
    "requests",
    "mentioned_name",
    "mentioned_pnr",
)

EXTRACT_FORBIDDEN_FIELDS = (
    "eligible",
    "eligibility",
    "compensation",
    "policy_decision",
    "amount_inr",
)

__all__ = [
    "RETRIEVE",
    "COMPUTE",
    "FORBID",
    "EXTRACT_FIELDS",
    "EXTRACT_FORBIDDEN_FIELDS",
    "RAW_POLICY_MARKERS",
    "render_extract_prompt",
    "render_respond_prompt",
    "context_contains_forbidden",
]
