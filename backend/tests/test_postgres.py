from __future__ import annotations

import os
from uuid import uuid4

import pytest

from models.schemas import Customer
from products.knowledge.postgres_store import PostgresKnowledgeStore

pytestmark = pytest.mark.skipif(
    not os.getenv("AERORESOLVE_TEST_POSTGRES"),
    reason="set AERORESOLVE_TEST_POSTGRES=1 with a reachable DATABASE_URL",
)


def test_postgres_keeps_self_service_passenger_across_store_instances():
    first = PostgresKnowledgeStore()
    email = f"persist-{uuid4().hex[:8]}@example.com"
    customer_id = f"CUST-{uuid4().hex[:8].upper()}"
    first.register_passenger(
        Customer(
            id=customer_id,
            name="Persisted Passenger",
            loyalty_tier="Standard",
            email=email,
            phone="+91-00",
            account_origin="self_service",
        ),
        "hash-from-test",
    )

    second = PostgresKnowledgeStore()
    found = second.identify(customer_id=customer_id)
    assert found is not None
    assert found.email.lower() == email
    account = second.account_for_email(email)
    assert account is not None
    assert account["password_hash"] == "hash-from-test"
    priya = second.identify(name="Priya Nair")
    assert priya is not None
    assert priya.id == "CUST-PRIYA"
