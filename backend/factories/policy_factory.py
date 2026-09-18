from models.schemas import RequestType
from policy.handlers.base import PolicyHandler
from policy.handlers.cancellation import RebookHandler, RefundOriginalHandler, RefundOtherMethodHandler
from policy.handlers.delay import HotelFullNightHandler, HotelHoursHandler, LoungeHandler, MealVoucherHandler
from policy.handlers.exceptions import (
    BusinessUpgradeHandler,
    CompensationBeyondPolicyHandler,
    LegalNoOpHandler,
    NonAirlineExceptionHandler,
)
from policy.handlers.assist import BookingAssistHandler, HelpQuestionHandler
from policy.handlers.fare import FareWaiverHandler
from policy.handlers.status import StatusHandler


class PolicyHandlerFactory:
    """Maps a request type to a PolicyHandler. Engine never constructs handlers itself."""

    _registry: dict[RequestType, type[PolicyHandler]] = {
        RequestType.STATUS: StatusHandler,
        RequestType.GENERAL_HELP: HelpQuestionHandler,
        RequestType.HELP_QUESTION: HelpQuestionHandler,
        RequestType.BOOKING_ASSIST: BookingAssistHandler,
        RequestType.REBOOK_24H: RebookHandler,
        RequestType.REFUND_ORIGINAL: RefundOriginalHandler,
        RequestType.REFUND_OTHER_METHOD: RefundOtherMethodHandler,
        RequestType.MEAL_VOUCHER: MealVoucherHandler,
        RequestType.LOUNGE: LoungeHandler,
        RequestType.HOTEL_DELAYED_HOURS: HotelHoursHandler,
        RequestType.HOTEL_FULL_NIGHT: HotelFullNightHandler,
        RequestType.HIGHER_FARE_REBOOK: FareWaiverHandler,
        RequestType.FARE_WAIVER: FareWaiverHandler,
        RequestType.BUSINESS_UPGRADE: BusinessUpgradeHandler,
        RequestType.COMPENSATION_BEYOND_POLICY: CompensationBeyondPolicyHandler,
        RequestType.NON_AIRLINE_EXCEPTION: NonAirlineExceptionHandler,
        RequestType.LEGAL_OR_FORMAL: LegalNoOpHandler,
    }

    @classmethod
    def create(cls, request_type: RequestType) -> PolicyHandler:
        product = cls._registry.get(request_type)
        if not product:
            raise ValueError(f"No policy handler for {request_type}")
        return product()
