from typing import Any

import customtkinter as ctk
from PIL import Image, ImageDraw


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

    def get_flame_icon(self, active: bool, size: int = 24):
        if not hasattr(self, "_flame_icon_cache"):
            self._flame_icon_cache = {}

        key = (active, size)
        if key in self._flame_icon_cache:
            return self._flame_icon_cache[key]

        scale = 4
        canvas_size = size * scale
        image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        outer = "#F97316" if active else "#6B7280"
        inner = "#FDBA74" if active else "#9CA3AF"

        def pts(values):
            return [(int(x * canvas_size), int(y * canvas_size)) for x, y in values]

        draw.polygon(
            pts([
                (0.50, 0.05), (0.67, 0.30), (0.82, 0.47), (0.78, 0.72),
                (0.64, 0.92), (0.48, 0.99), (0.31, 0.91), (0.20, 0.73),
                (0.22, 0.54), (0.34, 0.36), (0.42, 0.22),
            ]),
            fill=outer,
        )
        draw.polygon(
            pts([
                (0.52, 0.34), (0.64, 0.53), (0.67, 0.70),
                (0.58, 0.87), (0.46, 0.93), (0.36, 0.82),
                (0.34, 0.66), (0.42, 0.51),
            ]),
            fill=inner,
        )

        icon = ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
        self._flame_icon_cache[key] = icon
        return icon
