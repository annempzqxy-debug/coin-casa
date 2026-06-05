import customtkinter as ctk


THEME_NAME = "Rose"

COLORS = {
    "page": "#fedcdb",
    "surface": "#feb1b7",
    "surface_alt": "#febecc",
    "primary": "#fe6694",
    "primary_hover": "#fd788b",
    "text": "#3F2B33",
    "muted": "#6B5A61",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
}


def is_pink_theme(mode: str) -> bool:
    return mode.strip().lower() == THEME_NAME.lower()


def apply_pink_theme(app) -> None:
    """Apply the rose palette to existing CustomTkinter widgets."""
    ctk.set_appearance_mode("light")
    setattr(app, "active_color_theme", THEME_NAME)

    _configure_tree(app)

    if hasattr(app, "nav_buttons") and getattr(app, "active_button", None):
        app.active_button.configure(
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
        )


def reset_to_standard_theme(app, mode: str) -> None:
    was_pink = getattr(app, "active_color_theme", None) == THEME_NAME
    setattr(app, "active_color_theme", mode)
    ctk.set_appearance_mode(mode.lower())

    if was_pink and getattr(app, "current_user", None) is not None:
        if hasattr(app, "sidebar"):
            app.sidebar.destroy()
        if hasattr(app, "container"):
            app.container.destroy()
        app.create_sidebar()
        app.create_container()
        app.create_pages()
        app.show_page("Settings")


def _configure_tree(widget) -> None:
    _configure_widget(widget)
    for child in widget.winfo_children():
        _configure_tree(child)


def _configure_widget(widget) -> None:
    if isinstance(widget, ctk.CTk):
        widget.configure(fg_color=COLORS["page"])
        return

    if isinstance(widget, ctk.CTkScrollableFrame):
        _safe_configure(widget, fg_color=COLORS["page"], scrollbar_button_color=COLORS["primary"])
        return

    if isinstance(widget, ctk.CTkFrame):
        current = _current_color(widget, "fg_color")
        if current == "transparent":
            return
        _safe_configure(widget, fg_color=COLORS["surface"], border_color=COLORS["surface_alt"])
        return

    if isinstance(widget, ctk.CTkButton):
        text = widget.cget("text")
        if text == "Sign Out" or "Delete" in text:
            _safe_configure(widget, fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"], text_color="white")
            return
        if _current_color(widget, "fg_color") == "transparent":
            _safe_configure(widget, hover_color=COLORS["surface_alt"], text_color=COLORS["text"])
            return
        _safe_configure(widget, fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"], text_color="white")
        return

    if isinstance(widget, ctk.CTkLabel):
        current = _current_color(widget, "text_color")
        if current not in ("white", "#EF4444", "#22C55E", "#F59E0B", "#F97316"):
            _safe_configure(widget, text_color=COLORS["text"])
        return

    if isinstance(widget, ctk.CTkEntry):
        _safe_configure(
            widget,
            fg_color="#FFF7F8",
            border_color=COLORS["surface_alt"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["muted"],
        )
        return

    if isinstance(widget, ctk.CTkOptionMenu):
        _safe_configure(widget, fg_color=COLORS["primary"], button_color=COLORS["primary_hover"], text_color="white")
        return

    if isinstance(widget, ctk.CTkCheckBox):
        _safe_configure(widget, fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"], text_color=COLORS["text"])
        return

    if isinstance(widget, ctk.CTkSlider):
        _safe_configure(widget, progress_color=COLORS["primary"], button_color=COLORS["primary"])


def _safe_configure(widget, **kwargs) -> None:
    try:
        widget.configure(**kwargs)
    except Exception:
        pass


def _current_color(widget, option: str):
    try:
        return widget.cget(option)
    except Exception:
        return None
