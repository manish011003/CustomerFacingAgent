from factories.reply_factory import ReplyFactory


def render_reply(ctx, utterance: str) -> str:
    """Facade — always goes through ReplyFactory."""
    return ReplyFactory.create("template").render(ctx, utterance)
