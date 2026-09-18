from products.knowledge.base import PassengerKnowledgeStore


class JsonKnowledgeStore(PassengerKnowledgeStore):
    """Concrete product: in-memory passenger KB seeded from the assignment JSON pack."""

    def _init_backend(self) -> None:
        self.backend = "json"
