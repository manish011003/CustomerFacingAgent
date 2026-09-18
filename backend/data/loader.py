from pathlib import Path
import json

from models.schemas import Booking, Customer, ScenarioFixture

DATA_DIR = Path(__file__).resolve().parent


def load_json(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def load_customers() -> list[Customer]:
    return [Customer.model_validate(row) for row in load_json("customers.json")]


def load_bookings() -> list[Booking]:
    return [Booking.model_validate(row) for row in load_json("bookings.json")]


def load_policies() -> dict:
    return load_json("policies.json")


def load_fixtures() -> list[ScenarioFixture]:
    payload = load_json("scenario_fixtures.json")
    return [ScenarioFixture.model_validate(row) for row in payload["fixtures"]]


def load_style_samples() -> dict:
    return load_json("style_samples.json")
