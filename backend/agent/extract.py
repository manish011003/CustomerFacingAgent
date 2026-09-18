from factories.extractor_factory import ExtractorFactory


def extract(message: str):
    """Facade — always goes through ExtractorFactory."""
    return ExtractorFactory.create("heuristic").extract(message)
