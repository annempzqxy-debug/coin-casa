from typing import Any


class AppMixin:
    # Shared state attributes declared here so Pylance can resolve them
    # across all mixin subclasses without false "unknown attribute" errors.
    db: Any
    current_user: Any
    total_limit: float
    current_budget_limit: float
    current_budget_type: Any
    current_notifications_enabled: int
    current_streak_current: int
    current_streak_best: int
    current_streak_last_success: Any
    current_streak_last_checked: Any
    categories: list
    category_totals: dict
    pages: dict
    container: Any
    period: str
    profile_image: Any

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(name)