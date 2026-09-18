"""Suite-wide isolation from whatever keys a developer has lying around.

`pytest` has to behave the same on a laptop whose `backend/.env` is full of
live keys as it does in a clean checkout, or the assertions about degradation
quietly start measuring the network instead. Two things have to be undone:
the key that `load_dotenv()` already put in the environment at import time,
and the reload itself, because `LlmFactory.create(refresh=True)` re-reads that
file and would hand a real key back to a run that just cleared it.
"""

from __future__ import annotations

import pytest

from factories import llm_factory
from factories.llm_factory import LlmFactory
from llm.config import PROVIDERS


@pytest.fixture(autouse=True)
def no_real_provider_key(monkeypatch):
    for spec in PROVIDERS.values():
        monkeypatch.delenv(spec["key_env"], raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setattr(llm_factory, "load_dotenv", lambda *args, **kwargs: None)
    LlmFactory.reset()
    yield
    LlmFactory.reset()
