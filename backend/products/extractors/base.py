from abc import ABC, abstractmethod

from models.schemas import Extraction, SessionMemory


class IntentExtractor(ABC):
    """Product: turn a customer utterance into structured extraction. Never decides policy."""

    @abstractmethod
    def extract(self, message: str, session: SessionMemory | None = None) -> Extraction:
        raise NotImplementedError
