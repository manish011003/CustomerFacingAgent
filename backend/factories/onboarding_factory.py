from factories.auth_factory import AuthFactory
from factories.hasher_factory import HasherFactory
from products.onboarding.base import PassengerOnboarding
from products.onboarding.self_service import PassengerSelfServiceOnboarding


class OnboardingFactory:
    @classmethod
    def create(cls, kind: str = "self_service") -> PassengerOnboarding:
        # Imported lazily: factories/__init__ loads this module, so a module-level
        # import of the store makes `import kb.store` circular for any caller.
        from kb.store import store

        if kind != "self_service":
            raise ValueError(f"Unknown onboarding: {kind}")
        return PassengerSelfServiceOnboarding(
            store=store,
            hasher=HasherFactory.create(),
            sessions=AuthFactory.create(),
        )
