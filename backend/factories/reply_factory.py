from __future__ import annotations

from factories.llm_factory import LlmFactory
from products.replies.base import ReplyRenderer
from products.replies.llm import LlmPolishedReplyRenderer
from products.replies.template import TemplateReplyRenderer


class ReplyFactory:
    @classmethod
    def create(cls, kind: str = "auto") -> ReplyRenderer:
        template = TemplateReplyRenderer()
        if kind == "template":
            return template
        if kind == "llm":
            return LlmPolishedReplyRenderer(fallback=template, client=LlmFactory.create())
        if kind == "auto":
            client = LlmFactory.create()
            if client.enabled:
                return LlmPolishedReplyRenderer(fallback=template, client=client)
            return template
        raise ValueError(f"Unknown reply renderer: {kind}")
