from __future__ import annotations

import os

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
            return LlmPolishedReplyRenderer(fallback=template)
        if kind == "auto":
            return LlmPolishedReplyRenderer(fallback=template) if os.getenv("OPENAI_API_KEY") else template
        raise ValueError(f"Unknown reply renderer: {kind}")
