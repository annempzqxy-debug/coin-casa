import sqlite3
from datetime import datetime, date, timedelta
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import DB


from mixin_base import AppMixin
class DashboardMixin(AppMixin):

    def create_overview_page(self):
        page = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent"
        )

        header_frame = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        welcome_text = (self.current_user.get_nickname() or self.current_user.get_username()) if self.current_user else ""

        ctk.CTkLabel(
            header_frame,
            text=f"Hello, {welcome_text} 👋",
            font=("Segoe UI", 34, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Here's your financial overview",
            font=("Segoe UI", 18),
            text_color="#9CA3AF"
        ).pack(anchor="w", pady=(0, 10))

        cards_frame = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )
        cards_frame.pack(fill="x", padx=20, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.balance_card_frame = ctk.CTkFrame(
            cards_frame,
            corner_radius=24,
            fg_color="#059669",
            height=200
        )
        self.balance_card_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        ctk.CTkLabel(
            self.balance_card_frame,
            text="Current Budget Limit",
            font=("Segoe UI", 20),
            text_color="white"
        ).pack(anchor="w", padx=25, pady=(25, 5))

        self.balance_card = ctk.CTkLabel(
            self.balance_card_frame,
            text="₱0.00",
            font=("Segoe UI", 42, "bold"),
            text_color="white"
        )
        self.balance_card.pack(anchor="w", padx=25)

        self.streak_card = ctk.CTkFrame(
            cards_frame,
            corner_radius=24,
            height=200
        )
        self.streak_card.grid(row=0, column=1, sticky="nsew", padx=10)

        ctk.CTkLabel(
            self.streak_card,
            text="Saving Streak",
            font=("Segoe UI", 18)
        ).pack(anchor="w", padx=20, pady=(25, 10))

        self.streak_value = ctk.CTkLabel(
            self.streak_card,
            text="🔥 0",
            font=("Segoe UI", 36, "bold"),
            text_color="#F59E0B"
        )
        self.streak_value.pack(anchor="w", padx=20)

        # Budget Status redesigned: show remaining budget as main indicator
        self.expense_card_frame = ctk.CTkFrame(
            cards_frame,
            corner_radius=24,
            height=200
        )
        self.expense_card_frame.grid(row=0, column=2, sticky="nsew", padx=10)

        ctk.CTkLabel(
            self.expense_card_frame,
            text="Remaining Budget",
            font=("Segoe UI", 18)
        ).pack(anchor="w", padx=20, pady=(25, 10))

        self.expense_card = ctk.CTkLabel(
            self.expense_card_frame,
            text="₱0.00",
            font=("Segoe UI", 34, "bold"),
            text_color="#22C55E"
        )
        self.expense_card.pack(anchor="w", padx=20)

        overview_row = ctk.CTkFrame(
            page,
            fg_color="transparent",
            height=330
        )
        overview_row.pack(fill="x", padx=20, pady=(8, 12))
        overview_row.pack_propagate(False)
        overview_row.grid_columnconfigure(0, weight=1, uniform="overview_middle")
        overview_row.grid_columnconfigure(1, weight=1, uniform="overview_middle")
        overview_row.grid_rowconfigure(0, weight=1)

        analytics_frame = ctk.CTkFrame(
            overview_row,
            corner_radius=24
        )
        analytics_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        analytics_header = ctk.CTkFrame(
            analytics_frame,
            fg_color="transparent"
        )
        analytics_header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            analytics_header,
            text="Spending Overview",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        self.overview_chart_frame = ctk.CTkFrame(
            analytics_frame,
            corner_radius=20,
            height=185
        )
        self.overview_chart_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.chart_container = ctk.CTkFrame(
            self.overview_chart_frame,
            fg_color="transparent"
        )
        self.chart_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        transaction_frame = ctk.CTkFrame(
            overview_row,
            corner_radius=24
        )
        transaction_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        top = ctk.CTkFrame(
            transaction_frame,
            fg_color="transparent"
        )
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            top,
            text="Recent Transactions",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        self.recent_transactions_frame = ctk.CTkScrollableFrame(
            transaction_frame,
            height=155,
            corner_radius=18
        )
        self.recent_transactions_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10)
        )

        ctk.CTkButton(
            transaction_frame,
            text="View All Transactions",
            height=40,
            command=lambda: self.show_page("Transactions")
        ).pack(fill="x", padx=20, pady=(0, 20))

        bottom_frame = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )
        bottom_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )
        bottom_frame.grid_columnconfigure((0, 1), weight=1)

        # Goals & Progress simplified: just remaining budget
        self.goal_preview = ctk.CTkFrame(
            bottom_frame,
            corner_radius=24,
            height=185
        )
        self.goal_preview.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10
        )
        self.goal_preview.grid_propagate(False)

        ctk.CTkLabel(
            self.goal_preview,
            text="Goals & Progress",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.remaining_budget_label = ctk.CTkLabel(
            self.goal_preview,
            text="Remaining: ₱0.00",
            font=("Segoe UI", 26, "bold")
        )
        self.remaining_budget_label.pack(anchor="w", padx=20, pady=(0, 10))

        self.remaining_budget_bar = ctk.CTkProgressBar(
            self.goal_preview,
            height=18
        )
        self.remaining_budget_bar.pack(fill="x", padx=20, pady=(0, 14))
        self.remaining_budget_bar.set(0)

        # Goal Status card
        self.budget_preview = ctk.CTkFrame(
            bottom_frame,
            corner_radius=24,
            height=185
        )
        self.budget_preview.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=10
        )
        self.budget_preview.grid_propagate(False)

        ctk.CTkLabel(
            self.budget_preview,
            text="Goal Status",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 8))

        self.goal_status_frame = ctk.CTkScrollableFrame(
            self.budget_preview,
            fg_color="transparent",
            corner_radius=0
        )
        self.goal_status_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 12)
        )

        return page

    # =====================
    # SUMMARY PAGE (RENAMED FROM BUDGETS)
    # =====================


    def create_summary_page(self):
        page = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent"
        )

        header = ctk.CTkFrame(page, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="Summary",
            font=("Segoe UI", 30, "bold")
        ).pack(side="left")

        self.summary_filter_var = ctk.StringVar(value="Today")
        ctk.CTkOptionMenu(
            header,
            values=["Today", "Daily", "Weekly", "Monthly", "Yearly"],
            variable=self.summary_filter_var,
            command=lambda _: self.refresh_dashboard(),
            width=160
        ).pack(side="right")

        self.current_budget_card = ctk.CTkFrame(
            page,
            corner_radius=24,
            fg_color="#0F766E",
            height=140
        )
        self.current_budget_card.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            self.current_budget_card,
            text="Current Budget Limit",
            font=("Segoe UI", 18),
            text_color="white"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        self.current_budget_amount = ctk.CTkLabel(
            self.current_budget_card,
            text="₱0.00",
            font=("Segoe UI", 36, "bold"),
            text_color="white"
        )
        self.current_budget_amount.pack(anchor="w", padx=25)

        self.budget_status_label = ctk.CTkLabel(
            self.current_budget_card,
            text="",
            font=("Segoe UI", 14),
            text_color="white"
        )
        self.budget_status_label.pack(anchor="w", padx=25, pady=(5, 5))

        self.progressbars = {}

        colors = [
            "#10B981",
            "#F59E0B",
            "#3B82F6",
            "#8B5CF6",
            "#EF4444",
            "#EC4899",
            "#22C55E",
            "#6366F1"
        ]

        for i, category in enumerate(self.categories):
            card = ctk.CTkFrame(
                page,
                corner_radius=20
            )
            card.pack(fill="x", padx=20, pady=10)

            top = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            top.pack(fill="x", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                top,
                text=category,
                font=("Segoe UI", 18, "bold")
            ).pack(side="left")

            amount_label = ctk.CTkLabel(
                top,
                text="₱0 / ₱0",
                font=("Segoe UI", 14)
            )
            amount_label.pack(side="right")

            pb = ctk.CTkProgressBar(
                card,
                progress_color=colors[i % len(colors)],
                height=15
            )
            pb.pack(fill="x", padx=15, pady=(0, 15))
            pb.set(0)

            self.progressbars[category] = (pb, amount_label)

        # Recent transactions for Summary (5 only, card layout)
        recent_frame = ctk.CTkFrame(
            page,
            corner_radius=24
        )
        recent_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(20, 20)
        )

        top_recent = ctk.CTkFrame(recent_frame, fg_color="transparent")
        top_recent.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            top_recent,
            text="Recent Transactions",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        self.summary_recent_transactions_frame = ctk.CTkScrollableFrame(
            recent_frame,
            height=220,
            corner_radius=18
        )
        self.summary_recent_transactions_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10)
        )

        ctk.CTkButton(
            recent_frame,
            text="View All Transactions",
            height=40,
            command=lambda: self.show_page("Transactions")
        ).pack(fill="x", padx=20, pady=(0, 20))

        return page

    # =====================
    # TRANSACTIONS PAGE (CARD LIST)
    # =====================


    def refresh_dashboard(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return

        spent, limit, remaining, over, amount_over, budget_type = \
            self.db.get_budget_status_for_user(self.current_user.get_user_id())

        self.current_budget_limit = limit
        self.current_budget_type = budget_type

        self.balance_card.configure(
            text=f"₱{limit:,.2f}"
        )

        if hasattr(self, "current_budget_amount"):
            self.current_budget_amount.configure(
                text=f"₱{limit:,.2f}"
            )

        # Remaining budget as main metric
        self.expense_card.configure(
            text=f"₱{remaining:,.2f}"
        )

        # Update simplified Goals & Progress (remaining money from budget)
        if hasattr(self, "remaining_budget_label"):
            self.remaining_budget_label.configure(
                text=f"Remaining: ₱{remaining:,.2f}"
            )
        if hasattr(self, "remaining_budget_bar"):
            progress = 0
            if limit > 0:
                progress = max(0, min(remaining / limit, 1.0))
            self.remaining_budget_bar.set(progress)

        # Goal Status card
        if hasattr(self, "goal_status_frame"):
            for w in self.goal_status_frame.winfo_children():
                w.destroy()
            import sqlite3
            from config import DB as _DB
            try:
                conn = sqlite3.connect(_DB)
                cur = conn.cursor()
                cur.execute("SELECT name, target, saved FROM goals ORDER BY id")
                goal_rows = cur.fetchall()
                conn.close()
            except Exception:
                goal_rows = []

            if not goal_rows:
                ctk.CTkLabel(
                    self.goal_status_frame,
                    text="No goals yet. Set one now →",
                    font=("Segoe UI", 13),
                    text_color="#9CA3AF"
                ).pack(anchor="w", padx=6, pady=8)
            else:
                for g_name, g_target, g_saved in goal_rows:
                    pct = (g_saved / g_target * 100) if g_target > 0 else 0
                    row_f = ctk.CTkFrame(self.goal_status_frame, fg_color="transparent")
                    row_f.pack(fill="x", pady=(0, 6))

                    top_f = ctk.CTkFrame(row_f, fg_color="transparent")
                    top_f.pack(fill="x")
                    ctk.CTkLabel(
                        top_f,
                        text=g_name,
                        font=("Segoe UI", 12, "bold")
                    ).pack(side="left")
                    pct_color = "#22C55E" if pct >= 100 else "#3B82F6"
                    ctk.CTkLabel(
                        top_f,
                        text=f"₱{g_saved:,.0f} / ₱{g_target:,.0f}  ({pct:.1f}%)",
                        font=("Segoe UI", 11),
                        text_color=pct_color
                    ).pack(side="right")

                    bar = ctk.CTkProgressBar(row_f, height=8, corner_radius=4,
                                             progress_color=pct_color)
                    bar.set(min(pct / 100, 1.0))
                    bar.pack(fill="x", pady=(2, 0))

        streak_summary = self.db.sync_streak_summary_for_user(self.current_user.get_user_id())
        self.current_streak_current = streak_summary["current"]
        self.current_streak_best = streak_summary["best"]
        if hasattr(self, "streak_value"):
            self.streak_value.configure(
                text=f"Current streak: {streak_summary['current']} | Best: {streak_summary['best']}"
            )

        self.load_transactions()
        self.render_recent_transactions_cards()
        self.render_summary_recent_transactions()

        if hasattr(self, "progressbars"):
            self.update_budget_progress()
            self.refresh_reports()


    def update_overview_chart(self):
        if not hasattr(self, "chart_container"):
            return

        for widget in self.chart_container.winfo_children():
            widget.destroy()

        labels = []
        values = []

        for category, amount in self.category_totals.items():
            if amount > 0:
                labels.append(category)
                values.append(amount)

        if not values:
            ctk.CTkLabel(
                self.chart_container,
                text="No analytics data yet.",
                font=("Segoe UI", 18),
                text_color="#9CA3AF"
            ).pack(expand=True)
            return

        fig = Figure(
            figsize=(4.2, 2.8),
            dpi=100
        )
        ax = fig.add_subplot(111)

        colors = [
            "#10B981",
            "#F59E0B",
            "#3B82F6",
            "#8B5CF6",
            "#EF4444",
            "#EC4899",
            "#22C55E",
            "#6366F1"
        ]

        result = ax.pie(
            values,
            colors=colors[:len(values)],
            startangle=90,
            wedgeprops=dict(width=0.38)
        )

        wedges, texts = result[:2]

        ax.legend(
            wedges,
            labels,
            loc="center left",
            bbox_to_anchor=(0.98, 0.5),
            fontsize=8
        )

        ax.set_aspect("equal")
        fig.patch.set_facecolor("#242424")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def render_recent_transactions_cards(self):
        if not hasattr(self, "recent_transactions_frame") or not self.current_user or self.current_user.get_user_id() is None:
            return

        for widget in self.recent_transactions_frame.winfo_children():
            widget.destroy()

        rows = self.db.get_transactions(self.current_user.get_user_id())[:5]

        for row in rows:
            tid, user_id, ttype, amount, category, desc, dstr = row

            card = ctk.CTkFrame(
                self.recent_transactions_frame,
                corner_radius=18
            )
            card.pack(fill="x", padx=10, pady=6)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(10, 4))

            icon_label = ctk.CTkLabel(
                top_row,
                text="●",
                font=("Segoe UI", 18)
            )
            icon_label.pack(side="left", padx=(0, 8))

            name_label = ctk.CTkLabel(
                top_row,
                text=desc,
                font=("Segoe UI", 14, "bold")
            )
            name_label.pack(side="left")

            amount_label = ctk.CTkLabel(
                top_row,
                text=f"₱{amount:,.2f}",
                font=("Segoe UI", 14, "bold"),
                text_color="#EF4444"
            )
            amount_label.pack(side="right")

            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=15, pady=(0, 10))

            category_label = ctk.CTkLabel(
                bottom_row,
                text=category,
                font=("Segoe UI", 12),
                text_color="#9CA3AF"
            )
            category_label.pack(side="left")

            date_label = ctk.CTkLabel(
                bottom_row,
                text=dstr,
                font=("Segoe UI", 12),
                text_color="#9CA3AF"
            )
            date_label.pack(side="right")


    def render_summary_recent_transactions(self):
        if not hasattr(self, "summary_recent_transactions_frame") or not self.current_user or self.current_user.get_user_id() is None:
            return

        for widget in self.summary_recent_transactions_frame.winfo_children():
            widget.destroy()

        rows = self.db.get_transactions(self.current_user.get_user_id())[:5]

        for row in rows:
            tid, user_id, ttype, amount, category, desc, dstr = row

            card = ctk.CTkFrame(
                self.summary_recent_transactions_frame,
                corner_radius=18
            )
            card.pack(fill="x", padx=10, pady=6)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(10, 4))

            icon_label = ctk.CTkLabel(
                top_row,
                text="●",
                font=("Segoe UI", 18)
            )
            icon_label.pack(side="left", padx=(0, 8))

            name_label = ctk.CTkLabel(
                top_row,
                text=desc,
                font=("Segoe UI", 14, "bold")
            )
            name_label.pack(side="left")

            amount_label = ctk.CTkLabel(
                top_row,
                text=f"₱{amount:,.2f}",
                font=("Segoe UI", 14, "bold"),
                text_color="#EF4444"
            )
            amount_label.pack(side="right")

            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=15, pady=(0, 10))

            category_label = ctk.CTkLabel(
                bottom_row,
                text=category,
                font=("Segoe UI", 12),
                text_color="#9CA3AF"
            )
            category_label.pack(side="left")

            date_label = ctk.CTkLabel(
                bottom_row,
                text=dstr,
                font=("Segoe UI", 12),
                text_color="#9CA3AF"
            )
            date_label.pack(side="right")