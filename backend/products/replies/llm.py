from models.schemas import CustomerAgentContext
from products.replies.base import ReplyRenderer


class LlmPolishedReplyRenderer(ReplyRenderer):
    def __init__(self, fallback: ReplyRenderer):
        self._fallback = fallback

    def render(self, ctx: CustomerAgentContext, utterance: str) -> str:
        import os

        approved = self._fallback.render(ctx, utterance)
        if not os.getenv("OPENAI_API_KEY"):
            return approved
        try:
            from openai import OpenAI
            from agent.context import render_respond_prompt

            client = OpenAI()
            completion = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "Rewrite the approved reply more naturally. Do not add benefits, amounts, or flights that are not in the provided reply or context packet.",
                    },
                    {"role": "user", "content": render_respond_prompt(ctx, utterance) + "\nApproved reply:\n" + approved},
                ],
                temperature=0.2,
            )
            return (completion.choices[0].message.content or "").strip() or approved
        except Exception:
            return approved
