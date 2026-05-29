import customtkinter as ctk


from mixin_base import AppMixin
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

    # =====================
    # SIDEBAR
    # =====================


    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.profile_frame = ctk.CTkFrame(
            self.sidebar,
            width=120,
            height=120,
            corner_radius=60
        )
        self.profile_frame.pack(pady=(25, 15))
        self.profile_frame.pack_propagate(False)

        self.profile_label = ctk.CTkLabel(
            self.profile_frame,
            text="👤",
            font=("Segoe UI", 50)
        )
        self.profile_label.pack(expand=True)

        self.load_profile_picture()

        nickname = (self.current_user.get_nickname() or self.current_user.get_username()) if self.current_user else ""

        self.nickname_display = ctk.CTkLabel(
            self.sidebar,
            text=nickname,
            font=("Segoe UI", 24, "bold")
        )
        self.nickname_display.pack(pady=(0, 2))

        self.user_label = ctk.CTkLabel(
            self.sidebar,
            text=f"@{self.current_user.get_username() if self.current_user else ''}",
            font=("Segoe UI", 15),
            text_color="#9CA3AF"
        )
        self.user_label.pack(pady=(0, 25))

        self.nav_buttons = {}

        pages = [
            "Overview",
            "Transactions",
            "Summary",          # Renamed from Budgets
            "Goals & Streaks",
            "Reports",
            "Categories",
            "Settings"
        ]

        for page in pages:
            btn = ctk.CTkButton(
                self.sidebar,
                text=page,
                fg_color="transparent",
                anchor="w",
                height=45,
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[page] = btn

        ctk.CTkButton(
            self.sidebar,
            text="Sign Out",
            fg_color="#EF4444",
            hover_color="#DC2626",
            height=40,
            command=self.sign_out
        ).pack(fill="x", padx=12, pady=(20, 12))


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
        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.container.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_page(self, page):
        for p in self.pages.values():
            p.grid_forget()

        for btn in self.nav_buttons.values():
            btn.configure(
                fg_color="transparent",
                text_color=("black", "white")
            )

        if page in self.nav_buttons:
            self.nav_buttons[page].configure(
                fg_color="#E5E7EB",
                text_color="black"
            )

        self.pages[page].grid(
            row=0,
            column=0,
            sticky="nsew"
        )

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
        self.pages["Summary"] = self.create_summary_page()   # renamed page
        self.pages["Reports"] = self.create_reports_page()
        self.pages["Goals & Streaks"] = self.create_goals_page()
        self.pages["Settings"] = self.create_settings_page()
        self.pages["Categories"] = self.create_categories_page()

    # =====================
    # OVERVIEW PAGE
    # =====================


    def refresh_everything(self):
        self.refresh_dashboard()
        self.refresh_reports()

        if hasattr(self, "streak_history_box") and self.current_user is not None:
            summary = self.db.sync_streak_summary_for_user(self.current_user.get_user_id())
            self.streak_display.configure(
                text=f"Current streak: {summary['current']} | Best: {summary['best']}"
            )
            self.load_streak_history()
            self.load_goals()

        self.update_overview_chart()
        self.update_streak_calendar()
        if hasattr(self, "search_entry"):
            self.search_transactions()