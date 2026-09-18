from __future__ import annotations

from llm.client import LlmClient
from models.schemas import CustomerAgentContext
from products.replies.base import ReplyRenderer

SYSTEM = (
    "Rewrite the approved reply more naturally. Do not add benefits, amounts, "
    "or flights that are not in the provided reply or context packet."
)


class LlmPolishedReplyRenderer(ReplyRenderer):
    """Phrasing only. The template reply is already policy-approved, and every
    path that does not produce a model answer returns that reply unchanged."""

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
        if result is None:
            return approved
        return result.text or approved
