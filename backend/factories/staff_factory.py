from products.auth.staff import StaffAccess

_STAFF: StaffAccess | None = None


class StaffFactory:
    """Staff sessions stay in process so operations login survives across requests."""

    @classmethod
    def create(cls) -> StaffAccess:
        global _STAFF
        if _STAFF is None:
            _STAFF = StaffAccess()
        return _STAFF

    @classmethod
    def reset(cls) -> None:
        global _STAFF
        _STAFF = None
