import customtkinter as ctk

from mixin_base import AppMixin
from pink_theme import COLORS, THEME_NAME

class NavigationMixin(AppMixin):

    def initialize_main_app(self):
        if self.current_user is None:
            return

        user_id = self.current_user.get_user_id()
        self.categories = self.db.get_categories_for_user(user_id)

        self.create_sidebar()
        self.create_container()
        self.create_pages()

        self.show_page("Overview")
        _ = self.db.update_streak_for_user(user_id)
        self.refresh_everything()
        self.check_budget_warning()

    # =====================
    # SIDEBAR
    # =====================

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.brand_label = ctk.CTkLabel(
            self.sidebar,
            text="COINSCASA",
            font=("Georgia", 26, "bold"),
            text_color="#C9A84C"
        )
        self.brand_label.pack(pady=(18, 8))

        self.tagline_label = ctk.CTkLabel(
            self.sidebar,
            text="Track • Save • Grow",
            font=("Segoe UI", 12),
            text_color="#9CA3AF"
        )
        self.tagline_label.pack(pady=(0, 12))

        # =====================
        # PROFILE SECTION — transparent frame so circle shows cleanly
        # =====================

        self.profile_frame = ctk.CTkFrame(
            self.sidebar,
            width=92,
            height=92,
            corner_radius=46,
            fg_color="transparent",   # ← no background box
        )
        self.profile_frame.pack(pady=(10, 10))
        self.profile_frame.pack_propagate(False)

        self.profile_label = ctk.CTkLabel(
            self.profile_frame,
            text="👤",
            font=("Segoe UI", 40),
            fg_color="transparent",   # ← no background box
        )
        self.profile_label.pack(expand=True)

        self.load_profile_picture()

        nickname = (
            self.current_user.get_nickname() or self.current_user.get_username()
        ) if self.current_user else ""

        self.nickname_display = ctk.CTkLabel(
            self.sidebar,
            text=nickname,
            font=("Segoe UI", 22, "bold")
        )
        self.nickname_display.pack(pady=(0, 2))

        self.user_label = ctk.CTkLabel(
            self.sidebar,
            text=f"@{self.current_user.get_username() if self.current_user else ''}",
            font=("Segoe UI", 15),
            text_color="#9CA3AF"
        )
        self.user_label.pack(pady=(0, 12))

        self.nav_buttons = {}

        ctk.CTkButton(
            self.sidebar,
            text="Sign Out",
            fg_color="#B91C1C",
            hover_color="#991B1B",
            height=42,
            corner_radius=10,
            command=self.sign_out
        ).pack(side="bottom", fill="x", padx=12, pady=(0, 14))

        self.nav_frame = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent"
        )
        self.nav_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))

        pages = [
            "Overview",
            "Transactions",
            "Summary",
            "Goals & Streaks",
            "Reports",
            "Categories",
            "Settings"
        ]

        for page in pages:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=page,
                fg_color="transparent",
                anchor="w",
                height=40,
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[page] = btn

    def sign_out(self):
        self.current_user = None
        self.current_budget_limit = 0
        self.current_budget_type = None
        self.current_notifications_enabled = 0
        self.current_streak_current = 0
        self.current_streak_best = 0
        self.current_streak_last_success = None
        self.current_streak_last_checked = None
        self.total_limit = 0
        self.create_auth_page()

    # =====================
    # PAGE CONTAINER
    # =====================

    def create_container(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_page(self, page):
        for p in self.pages.values():
            p.grid_forget()

        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color=("black", "white"))

        if page in self.nav_buttons:
            if getattr(self, "active_color_theme", None) == THEME_NAME:
                self.nav_buttons[page].configure(
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_hover"],
                    text_color="white",
                )
            else:
                self.nav_buttons[page].configure(fg_color="#C9A84C", text_color="black")
            self.active_button = self.nav_buttons[page]

        self.pages[page].grid(row=0, column=0, sticky="nsew")

        if page == "Overview":
            self.refresh_everything()
        elif page == "Reports":
            self.refresh_reports()
        elif page == "Goals & Streaks":
            self.refresh_everything()
        elif page == "Categories":
            self.load_categories_ui()
        elif page == "Transactions":
            self.search_transactions()
        elif page == "Summary":
            self.refresh_dashboard()

    # =====================
    # PAGE CREATION
    # =====================

    def create_pages(self):
        self.pages = {}
        self.pages["Overview"] = self.create_overview_page()
        self.pages["Transactions"] = self.create_transactions_page()
        self.pages["Summary"] = self.create_summary_page()
        self.pages["Reports"] = self.create_reports_page()
        self.pages["Goals & Streaks"] = self.create_goals_page()
        self.pages["Settings"] = self.create_settings_page()
        self.pages["Categories"] = self.create_categories_page()

    def refresh_everything(self):
        self.refresh_dashboard()
        self.refresh_reports()

        if hasattr(self, "streak_history_box") and self.current_user is not None:
            self.refresh_streak_state()
            self.load_streak_history()
            self.load_goals()

        self.update_overview_chart()
        self.update_streak_calendar()
        if hasattr(self, "search_entry"):
            self.search_transactions()
