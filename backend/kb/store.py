import os

from factories.knowledge_factory import KnowledgeStoreFactory

store = KnowledgeStoreFactory.create(os.getenv("AERORESOLVE_KB", "auto"))
