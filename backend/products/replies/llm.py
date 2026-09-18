from __future__ import annotations

import re

from llm.client import LlmClient
from models.schemas import CustomerAgentContext
from products.replies.base import ReplyRenderer

# Asked only to "rewrite more naturally", Gemini answered with a menu of
# options — "Here are a few more natural ways to phrase that reply" — which is
# a sensible reading of the instruction and useless to a passenger. The shape
# of the output has to be stated, not implied.
SYSTEM = (
    "You rewrite an airline support reply so it reads naturally. "
    "Return ONLY the rewritten reply, as plain prose addressed to the passenger. "
    "No preamble, no alternatives, no markdown, no commentary. "
    "Keep every amount, entitlement, and decision exactly as given. "
    "Do not add benefits, amounts, or flights that are not in the provided reply or context packet."
)

# Digit groups of three or more, which is every rupee figure in this domain.
# Smaller numbers are delay hours and flight numbers, and a faithful rewrite is
# free to spell those as words ("six-hour"), so holding it to those would
# reject good output.
MONEY = re.compile(r"\d[\d,]{2,}")

# gpt-oss typesets: it returned "500\u202fINR" and "six\u2011hour", using a
# narrow no-break space and a non-breaking hyphen. Harmless on screen, but a
# thin space between digits reads as two numbers, which would fail the money
# check below on a rewrite that in fact changed nothing.
TYPOGRAPHIC = {"\u202f": " ", "\u00a0": " ", "\u2009": " ", "\u2011": "-"}
DIGIT_SEPARATOR = re.compile(r"(?<=\d)[\u202f\u00a0\u2009](?=\d)")


def normalise(text: str) -> str:
    """Plain ASCII spacing, so the same figure compares equal either side."""
    text = DIGIT_SEPARATOR.sub("", text)
    for fancy, plain in TYPOGRAPHIC.items():
        text = text.replace(fancy, plain)
    return text


def money_amounts(text: str) -> set[str]:
    return {match.group().replace(",", "") for match in MONEY.finditer(normalise(text))}


class LlmPolishedReplyRenderer(ReplyRenderer):
    """Phrasing only. The template reply is already policy-approved, and every
    path that does not produce a faithful rewrite returns that reply unchanged."""

    def __init__(self, fallback: ReplyRenderer, client: LlmClient | None = None):
        self._fallback = fallback
        self._client = client

    def _llm(self) -> LlmClient:
        if self._client is None:
            from factories.llm_factory import LlmFactory

            self._client = LlmFactory.create()
        return self._client

    def render(self, ctx: CustomerAgentContext, utterance: str) -> str:
        approved = self._fallback.render(ctx, utterance)
        client = self._llm()
        if not client.enabled:
            return approved

        from agent.context import render_respond_prompt

        result = client.complete(
            purpose="respond",
            system=SYSTEM,
            user=render_respond_prompt(ctx, utterance) + "\nApproved reply:\n" + approved,
            session_id=ctx.session_memory.session_id,
        )
        if result is None or not result.text:
            return approved

        # A rewrite may change any word. It may not change the money, in either
        # direction: an invented figure misleads, and a dropped one hides a
        # decision the passenger needs. Either way the approved text is correct,
        # so there is never a reason to ship the rewrite instead.
        if money_amounts(result.text) != money_amounts(approved):
            client.budget.note("respond_amount_drift", ctx.session_memory.session_id)
            return approved
        return normalise(result.text)
