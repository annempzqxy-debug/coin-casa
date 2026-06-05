import sqlite3
from datetime import date, timedelta
import customtkinter as ctk
from config import DB


from mixin_base import AppMixin
class BudgetMixin(AppMixin):

    def set_budget_limit(self):
        try:
            value_str = self.limit_entry.get().strip()
            if not value_str:
                return
            amount = float(value_str)
            if amount <= 0:
                return

            selected_label = "Weekly"
            if hasattr(self, "settings_budget_type_var"):
                selected_label = self.settings_budget_type_var.get()
            btype = {
                "daily": "daily",
                "weekly": "weekly",
                "monthly": "monthly",
                "yearly": "yearly",
            }.get(selected_label.lower(), self.current_budget_type or "weekly")

            self.confirm_budget_reset(amount, btype)
        except Exception as e:
            print("Budget limit error:", e)


    def confirm_budget_reset(self, amount, btype):
        warning = ctk.CTkToplevel(self)
        warning.title("Confirm Budget Change")
        warning.geometry("460x260")
        warning.grab_set()

        ctk.CTkLabel(
            warning,
            text="Changing your budget will restart your streak",
            font=("Segoe UI", 20, "bold"),
            wraplength=400
        ).pack(pady=(25, 10), padx=20)

        ctk.CTkLabel(
            warning,
            text=(
                f"New budget: ₱{amount:,.2f} {btype}\n\n"
                "Your current streak and best streak will be reset to 0. "
                "This cannot be undone."
            ),
            font=("Segoe UI", 14),
            justify="center",
            wraplength=390
        ).pack(padx=20, pady=(0, 20))

        actions = ctk.CTkFrame(warning, fg_color="transparent")
        actions.pack(pady=(0, 20))

        def apply_change():
            if not self.current_user or self.current_user.get_user_id() is None:
                warning.destroy()
                return

            self.db.update_user_budget(self.current_user.get_user_id(), btype, amount)
            self.total_limit = amount
            self.current_budget_limit = amount
            self.current_budget_type = btype
            self.current_streak_current = 0
            self.current_streak_best = 0
            self.current_streak_last_success = None

            warning.destroy()
            self.update_budget_progress()
            self.refresh_everything()

        ctk.CTkButton(
            actions,
            text="Cancel",
            width=140,
            fg_color="#6B7280",
            command=warning.destroy
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            actions,
            text="Reset Streak & Apply",
            width=180,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=apply_change
        ).pack(side="left", padx=8)

    def check_budget_warning(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return
        if not self.current_notifications_enabled:
            return

        spent, limit, remaining, over, amount_over, btype = \
            self.db.get_budget_status_for_user(self.current_user.get_user_id())

        if limit <= 0 or over:
            return

        percent_remaining = (remaining / limit) * 100

        if 0 < percent_remaining <= 15:
            self._show_budget_warning_popup(spent, limit, remaining, percent_remaining, btype)

    def _show_budget_warning_popup(self, spent, limit, remaining, percent_remaining, btype):
        popup = ctk.CTkToplevel(self)
        popup.title("Budget Warning")
        popup.geometry("420x220")
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="⚠️ Budget Almost Exhausted!",
            font=("Segoe UI", 20, "bold"),
            text_color="#F97316"
        ).pack(pady=(25, 8), padx=20)

        ctk.CTkLabel(
            popup,
            text=(
                f"You have only ₱{remaining:,.2f} left "
                f"({percent_remaining:.1f}% remaining)\n"
                f"out of your {btype} budget of ₱{limit:,.2f}.\n"
                f"Spent so far: ₱{spent:,.2f}"
            ),
            font=("Segoe UI", 14),
            justify="center",
            wraplength=370
        ).pack(padx=20, pady=(0, 20))

        ctk.CTkButton(
            popup,
            text="Got it",
            width=160,
            height=40,
            command=popup.destroy
        ).pack()

    def _summary_filter_range(self):
        selected = "Today"
        if hasattr(self, "summary_filter_var"):
            selected = self.summary_filter_var.get()

        today = date.today()
        if selected in {"Today", "Daily"}:
            return selected, today, today
        if selected == "Weekly":
            start = today - timedelta(days=today.weekday())
            return selected, start, start + timedelta(days=6)
        if selected == "Monthly":
            return selected, today.replace(day=1), today
        if selected == "Yearly":
            return selected, date(today.year, 1, 1), today
        return selected, today, today


    def _summary_category_totals(self, user_id):
        label, start, end = self._summary_filter_range()
        totals = {category: 0 for category in self.categories}
        for row in self.db.get_transactions(user_id):
            if row[2] != "Expense" or row[4] not in totals:
                continue
            try:
                d = date.fromisoformat(row[6])
            except Exception:
                continue
            if start <= d <= end:
                totals[row[4]] += row[3]
        return label, totals

    def rebuild_summary_page(self):
        if not hasattr(self, "pages"):
            return

        if not self.current_user:
            return

        user_id = self.current_user.get_user_id()

        if "Summary" in self.pages:
            self.pages["Summary"].destroy()

        self.categories = self.db.get_categories_for_user(user_id)

        self.pages["Summary"] = self.create_summary_page()
        self.pages["Summary"].grid_forget()

    def update_budget_progress(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return

        user_id = self.current_user.get_user_id()
        spent, limit, remaining, over, amount_over, btype = \
            self.db.get_budget_status_for_user(user_id)
        filter_label, filtered_totals = self._summary_category_totals(user_id)
        filtered_spent = sum(filtered_totals.values())

        if hasattr(self, "budget_status_label"):
            if limit > 0 and spent > limit:
                self.budget_status_label.configure(
                    text=f"Current {btype} budget is ₱{amount_over:,.2f} over. Showing {filter_label.lower()} category spending.",
                    text_color="#F97316"
                )
            else:
                self.budget_status_label.configure(
                    text=f"Showing {filter_label.lower()} spending: ₱{filtered_spent:,.2f}",
                    text_color="white"
                )

        if limit <= 0:
            for category, (bar, label) in self.progressbars.items():
                bar.set(0)
                label.configure(text=f"₱0 / ₱{limit:,.0f}")
            return

        for category, (bar, label) in self.progressbars.items():
            spent_cat = filtered_totals.get(category, 0)
            progress = min(spent_cat / limit, 1.0)
            bar.set(progress)
            label.configure(
                text=f"₱{spent_cat:,.0f} / ₱{limit:,.0f}"
            )

    # =====================
    # GOALS & STREAKS PAGE (LAYOUT CLEANUP ONLY)
    # =====================


    def create_goals_page(self):
        page = ctk.CTkScrollableFrame(self.container)

        ctk.CTkLabel(
            page,
            text="Goals & Streaks",
            font=("Segoe UI", 30, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.streak_display = ctk.CTkLabel(
            page,
            text="Current streak: 0 | Best: 0",
            font=("Segoe UI", 20, "bold"),
            text_color="#F59E0B"
        )
        self.streak_display.pack(anchor="w", padx=20, pady=(0, 10))

        self.streak_history_box = ctk.CTkTextbox(
            page,
            height=170,
            font=("Consolas", 14),
            state="disabled"
        )
        self.streak_history_box.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # ── Create Goal form ──────────────────────────────────────
        ctk.CTkLabel(
            page,
            text="Savings Goals",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 8))

        new_goal_frame = ctk.CTkFrame(page, corner_radius=16)
        new_goal_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            new_goal_frame,
            text="New Goal",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self.goal_name = ctk.CTkEntry(
            new_goal_frame,
            placeholder_text="Goal Name",
            height=40
        )
        self.goal_name.pack(fill="x", padx=16, pady=4)

        self.goal_amount = ctk.CTkEntry(
            new_goal_frame,
            placeholder_text="Target Amount",
            height=40
        )
        self.goal_amount.pack(fill="x", padx=16, pady=4)

        ctk.CTkButton(
            new_goal_frame,
            text="＋ Create Goal",
            height=40,
            command=self.create_goal
        ).pack(fill="x", padx=16, pady=(4, 14))

        # ── Goal cards container ──────────────────────────────────
        self.goal_cards_frame = ctk.CTkScrollableFrame(
            page,
            height=420,
            corner_radius=16,
            label_text=""
        )
        self.goal_cards_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.calendar_frame = ctk.CTkFrame(
            page,
            corner_radius=24
        )
        self.calendar_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            self.calendar_frame,
            text="Streak Calendar",
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.calendar_visible_year = date.today().year
        self.calendar_visible_month = date.today().month

        calendar_nav = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        calendar_nav.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(
            calendar_nav,
            text="Previous",
            width=120,
            command=lambda: self.change_calendar_month(-1)
        ).pack(side="left")

        self.calendar_month = ctk.CTkLabel(
            calendar_nav,
            text="",
            font=("Segoe UI", 18, "bold")
        )
        self.calendar_month.pack(side="left", expand=True)

        ctk.CTkButton(
            calendar_nav,
            text="Next",
            width=120,
            command=lambda: self.change_calendar_month(1)
        ).pack(side="right")

        self.calendar_grid = ctk.CTkFrame(
            self.calendar_frame,
            fg_color="transparent"
        )
        self.calendar_grid.pack(
            padx=20,
            pady=(0, 20)
        )

        return page

    # =====================
    # REPORTS PAGE
    # =====================


    def change_calendar_month(self, step):
        year = getattr(self, "calendar_visible_year", date.today().year)
        month = getattr(self, "calendar_visible_month", date.today().month) + step

        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        if (year, month) < (2025, 1) or (year, month) > (2028, 12):
            return

        self.calendar_visible_year = year
        self.calendar_visible_month = month
        self.update_streak_calendar()


    def load_streak_history(self):
        if not hasattr(self, "streak_history_box") or not self.current_user:
            return

        summary = self.db.sync_streak_summary_for_user(self.current_user.get_user_id())

        # Keep streak_display label in sync
        if hasattr(self, "streak_display"):
            self.streak_display.configure(
                text=f"Current streak: {summary['current']} | Best: {summary['best']}"
            )

        self.streak_history_box.configure(state="normal")
        self.streak_history_box.delete("1.0", "end")
        self.streak_history_box.insert(
            "end",
            f"Current streak: {summary['current']} {summary['budget_type'] or ''} period(s)\n"
            f"Best streak: {summary['best']} {summary['budget_type'] or ''} period(s)\n\n"
        )

        history = summary["history"]
        if not history:
            self.streak_history_box.insert("end", "No streak history yet. Add expenses to start tracking.\n")
        else:
            for item in history[-12:]:
                status = "OK" if item["status"] == "success" else "ENDED"
                self.streak_history_box.insert(
                    "end",
                    f"{item['period']} | {status} | ₱{item['total']:,.2f} / ₱{item['limit']:,.2f} | streak {item['streak_after']}\n"
                )

        self.streak_history_box.configure(state="disabled")


    def _ensure_goal_tables(self, cur):
        """Create goals and goal_history tables if they don't exist."""
        cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target REAL NOT NULL,
            saved REAL NOT NULL DEFAULT 0
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS goal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT,
            date TEXT NOT NULL
        )
        """)

    def load_goals(self):
        if not hasattr(self, "goal_cards_frame"):
            return

        for w in self.goal_cards_frame.winfo_children():
            w.destroy()

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        self._ensure_goal_tables(cur)
        conn.commit()

        cur.execute("SELECT id, name, target, saved FROM goals ORDER BY id")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.goal_cards_frame,
                text="No goals yet. Create one above!",
                font=("Segoe UI", 14),
                text_color="#9CA3AF"
            ).pack(pady=30)
            return

        for goal_id, name, target, saved in rows:
            percent = (saved / target * 100) if target > 0 else 0
            self._build_goal_card(self.goal_cards_frame, goal_id, name, target, saved, percent)

    def _build_goal_card(self, parent, goal_id, name, target, saved, percent):
        card = ctk.CTkFrame(parent, corner_radius=14)
        card.pack(fill="x", padx=8, pady=6)

        # ── Header row ─────────────────────────────────────────────
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            header,
            text=name,
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        pct_color = "#22C55E" if percent >= 100 else "#3B82F6"
        ctk.CTkLabel(
            header,
            text=f"{percent:.1f}%",
            font=("Segoe UI", 13, "bold"),
            text_color=pct_color
        ).pack(side="right")

        # ── Progress bar ───────────────────────────────────────────
        bar = ctk.CTkProgressBar(card, height=10, corner_radius=5)
        bar.set(min(percent / 100, 1.0))
        bar.pack(fill="x", padx=14, pady=(0, 4))

        # ── Amounts ────────────────────────────────────────────────
        amounts = ctk.CTkFrame(card, fg_color="transparent")
        amounts.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            amounts,
            text=f"Saved: ₱{saved:,.2f}",
            font=("Segoe UI", 13),
            text_color="#22C55E"
        ).pack(side="left")

        ctk.CTkLabel(
            amounts,
            text=f"Target: ₱{target:,.2f}",
            font=("Segoe UI", 13),
            text_color="#9CA3AF"
        ).pack(side="right")

        # ── Action buttons ─────────────────────────────────────────
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkButton(
            btn_row,
            text="＋ Add Savings",
            width=130,
            height=34,
            fg_color="#22C55E",
            hover_color="#16A34A",
            command=lambda gid=goal_id, gname=name: self._goal_amount_popup(gid, gname, "deposit")
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_row,
            text="－ Withdraw",
            width=110,
            height=34,
            fg_color="#F97316",
            hover_color="#EA580C",
            command=lambda gid=goal_id, gname=name: self._goal_amount_popup(gid, gname, "withdraw")
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_row,
            text="History",
            width=90,
            height=34,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=lambda gid=goal_id, gname=name: self._show_goal_history(gid, gname)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_row,
            text="Delete",
            width=80,
            height=34,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=lambda gid=goal_id, gname=name: self._confirm_delete_goal(gid, gname)
        ).pack(side="right")

    def _goal_amount_popup(self, goal_id, goal_name, action):
        win = ctk.CTkToplevel(self)
        win.title("Add Savings" if action == "deposit" else "Withdraw Savings")
        win.geometry("380x280")
        win.grab_set()

        label = "Amount to Add" if action == "deposit" else "Amount to Withdraw"
        color = "#22C55E" if action == "deposit" else "#F97316"

        ctk.CTkLabel(
            win,
            text=f"{'➕' if action == 'deposit' else '➖'} {goal_name}",
            font=("Segoe UI", 18, "bold"),
            text_color=color
        ).pack(pady=(20, 8))

        ctk.CTkLabel(win, text=label, font=("Segoe UI", 14)).pack(pady=(0, 4))

        amount_entry = ctk.CTkEntry(win, placeholder_text="e.g. 500", width=260, height=40)
        amount_entry.pack(pady=4)

        ctk.CTkLabel(win, text="Note (optional)", font=("Segoe UI", 14)).pack(pady=(8, 4))

        note_entry = ctk.CTkEntry(win, placeholder_text="e.g. Birthday money", width=260, height=40)
        note_entry.pack(pady=4)

        status = ctk.CTkLabel(win, text="", text_color="#EF4444", font=("Segoe UI", 12))
        status.pack(pady=4)

        def save():
            try:
                amt_str = amount_entry.get().strip()
                if not amt_str:
                    status.configure(text="Amount is required.")
                    return
                amt = float(amt_str)
                if amt <= 0:
                    status.configure(text="Amount must be positive.")
                    return
                note = note_entry.get().strip()
                today = date.today().isoformat()

                conn = sqlite3.connect(DB)
                cur = conn.cursor()
                self._ensure_goal_tables(cur)

                cur.execute("SELECT saved FROM goals WHERE id=?", (goal_id,))
                row = cur.fetchone()
                if not row:
                    conn.close()
                    win.destroy()
                    return

                current_saved = row[0]
                if action == "withdraw":
                    if amt > current_saved:
                        conn.close()
                        status.configure(text=f"Cannot withdraw more than ₱{current_saved:,.2f} saved.")
                        return
                    new_saved = current_saved - amt
                else:
                    new_saved = current_saved + amt

                cur.execute("UPDATE goals SET saved=? WHERE id=?", (new_saved, goal_id))
                cur.execute(
                    "INSERT INTO goal_history (goal_id, action, amount, note, date) VALUES (?,?,?,?,?)",
                    (goal_id, action, amt, note, today)
                )
                conn.commit()
                conn.close()

                win.destroy()
                self.load_goals()
            except Exception as e:
                status.configure(text=f"Error: {e}")

        ctk.CTkButton(
            win,
            text="Save",
            width=260,
            height=40,
            fg_color=color,
            command=save
        ).pack(pady=12)

    def _show_goal_history(self, goal_id, goal_name):
        win = ctk.CTkToplevel(self)
        win.title(f"History – {goal_name}")
        win.geometry("480x400")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text=f"📋 {goal_name} – History",
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(16, 8), padx=20)

        box = ctk.CTkScrollableFrame(win, corner_radius=10)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        self._ensure_goal_tables(cur)
        cur.execute(
            "SELECT action, amount, note, date FROM goal_history WHERE goal_id=? ORDER BY id DESC",
            (goal_id,)
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                box,
                text="No history yet.",
                font=("Segoe UI", 13),
                text_color="#9CA3AF"
            ).pack(pady=20)
            return

        for action, amount, note, entry_date in rows:
            row_frame = ctk.CTkFrame(box, corner_radius=10)
            row_frame.pack(fill="x", padx=4, pady=4)

            icon = "＋" if action == "deposit" else "－"
            color = "#22C55E" if action == "deposit" else "#F97316"
            action_label = "Added" if action == "deposit" else "Withdrew"

            left = ctk.CTkFrame(row_frame, fg_color="transparent")
            left.pack(side="left", padx=12, pady=8)

            ctk.CTkLabel(
                left,
                text=f"{icon} {action_label}",
                font=("Segoe UI", 13, "bold"),
                text_color=color
            ).pack(anchor="w")

            if note:
                ctk.CTkLabel(
                    left,
                    text=note,
                    font=("Segoe UI", 12),
                    text_color="#9CA3AF"
                ).pack(anchor="w")

            right = ctk.CTkFrame(row_frame, fg_color="transparent")
            right.pack(side="right", padx=12, pady=8)

            ctk.CTkLabel(
                right,
                text=f"₱{amount:,.2f}",
                font=("Segoe UI", 14, "bold"),
                text_color=color
            ).pack(anchor="e")

            ctk.CTkLabel(
                right,
                text=entry_date,
                font=("Segoe UI", 11),
                text_color="#6B7280"
            ).pack(anchor="e")

    def _confirm_delete_goal(self, goal_id, goal_name):
        win = ctk.CTkToplevel(self)
        win.title("Delete Goal")
        win.geometry("400x210")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text=f'Delete "{goal_name}"?',
            font=("Segoe UI", 17, "bold")
        ).pack(pady=(24, 8), padx=20)

        ctk.CTkLabel(
            win,
            text="This will permanently delete the goal and all its history.",
            font=("Segoe UI", 13),
            text_color="#9CA3AF",
            wraplength=340,
            justify="center"
        ).pack(padx=20)

        btns = ctk.CTkFrame(win, fg_color="transparent")
        btns.pack(pady=24)

        def do_delete():
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            self._ensure_goal_tables(cur)
            cur.execute("DELETE FROM goal_history WHERE goal_id=?", (goal_id,))
            cur.execute("DELETE FROM goals WHERE id=?", (goal_id,))
            conn.commit()
            conn.close()
            win.destroy()
            self.load_goals()

        ctk.CTkButton(
            btns, text="Cancel", width=130, fg_color="#6B7280",
            command=win.destroy
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btns, text="Delete", width=130, fg_color="#EF4444",
            hover_color="#DC2626", command=do_delete
        ).pack(side="left", padx=8)


    def create_goal(self):
        try:
            name = self.goal_name.get().strip()
            target_str = self.goal_amount.get().strip()

            if not name:
                return
            if not target_str:
                return
            target = float(target_str)
            if target <= 0:
                return

            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            self._ensure_goal_tables(cur)

            cur.execute(
                "INSERT INTO goals (name, target, saved) VALUES (?, ?, 0)",
                (name, target)
            )

            conn.commit()
            conn.close()

            self.goal_name.delete(0, "end")
            self.goal_amount.delete(0, "end")

            self.load_goals()

        except Exception as e:
            print("Create goal error:", e)