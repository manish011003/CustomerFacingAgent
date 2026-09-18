from abc import ABC, abstractmethod

from models.schemas import Booking, Customer, ExtractedRequest, PolicyEvaluation


class PolicyHandler(ABC):
    """Product: apply one structured request against already-computed baseline entitlements."""

    @abstractmethod
    def apply(
        self,
        evaluation: PolicyEvaluation,
        customer: Customer,
        booking: Booking,
        request: ExtractedRequest,
        fare_difference_inr: int | None = None,
    ) -> None:
        raise NotImplementedError
