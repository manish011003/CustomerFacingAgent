from abc import ABC, abstractmethod

from models.schemas import CustomerAgentContext


class ReplyRenderer(ABC):
    @abstractmethod
    def render(self, ctx: CustomerAgentContext, utterance: str) -> str:
        raise NotImplementedError
