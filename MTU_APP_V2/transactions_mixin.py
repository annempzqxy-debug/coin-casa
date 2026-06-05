import sqlite3
from datetime import datetime, date, timedelta
import customtkinter as ctk
from config import DB
from date_utils import INVALID_DATE_MESSAGE, parse_flexible_date
from models import Expense

from mixin_base import AppMixin

class TransactionsMixin(AppMixin):

    def create_transactions_page(self):
        page = ctk.CTkScrollableFrame(self.container, fg_color="transparent")

        header = ctk.CTkFrame(page, corner_radius=24)
        header.pack(fill="x", padx=20, pady=(20, 15))

        ctk.CTkLabel(
            header,
            text="Transactions",
            font=("Segoe UI", 30, "bold")
        ).pack(side="left", padx=20, pady=20)

        filters_frame = ctk.CTkFrame(header, fg_color="transparent")
        filters_frame.pack(side="right", padx=20)

        ctk.CTkLabel(
            filters_frame, text="Filter:", font=("Segoe UI", 14, "bold")
        ).pack(anchor="e")

        self.transaction_time_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["All Time", "Today", "This Week", "This Month", "This Year"],
            command=lambda _: self.search_transactions()
        )
        self.transaction_time_filter.set("All Time")
        self.transaction_time_filter.pack(pady=(0, 5))

        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="Search transactions",
            width=220,
            height=40
        )
        self.search_entry.pack(side="right", padx=20)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_transactions())

        ctk.CTkButton(
            page,
            text="➕ Add Expense",
            height=48,
            font=("Segoe UI", 16, "bold"),
            command=lambda: self.transaction_popup("Expense")
        ).pack(fill="x", padx=20, pady=(0, 15))

        # Transaction ID delete row REMOVED per user request

        self.transactions_list_frame = ctk.CTkScrollableFrame(
            page, height=650, corner_radius=18
        )
        self.transactions_list_frame.pack(
            fill="both", expand=True, padx=20, pady=(0, 20)
        )

        return page

    # =====================
    # TRANSACTION POPUP
    # =====================

    def transaction_popup(self, ttype):
        win = ctk.CTkToplevel(self)
        win.title(f"Add {ttype}")
        win.geometry("430x530")

        ctk.CTkLabel(
            win, text=f"New {ttype}", font=("Segoe UI", 20, "bold")
        ).pack(pady=15)

        ctk.CTkLabel(
            win, text="* Required",
            font=("Segoe UI", 11, "bold"), text_color="#EF4444", anchor="w"
        ).pack(fill="x", padx=55, pady=(0, 2))

        amount_entry = ctk.CTkEntry(win, placeholder_text="Amount")
        amount_entry.pack(pady=(0, 10))

        self.categories = self.db.get_categories_for_user(self.current_user.get_user_id())
        category_combo = ctk.CTkComboBox(win, values=self.categories)
        category_combo.pack(pady=10)
        if self.categories:
            category_combo.set(self.categories[0])

        ctk.CTkLabel(
            win, text="* Not required",
            font=("Segoe UI", 11, "bold"), text_color="#9CA3AF", anchor="w"
        ).pack(fill="x", padx=55, pady=(4, 2))

        desc_entry = ctk.CTkEntry(win, placeholder_text=f"{ttype} Description")
        desc_entry.pack(pady=(0, 10))

        ctk.CTkLabel(
            win, text="* Not required",
            font=("Segoe UI", 11, "bold"), text_color="#9CA3AF", anchor="w"
        ).pack(fill="x", padx=55, pady=(4, 2))

        date_entry = ctk.CTkEntry(win, placeholder_text="Date")
        date_entry.pack(pady=(0, 10))

        input_status = ctk.CTkLabel(
            win, text="", font=("Segoe UI", 12),
            text_color="#EF4444", wraplength=360
        )
        input_status.pack(pady=(0, 5))

        def save():
            try:
                amount_str = amount_entry.get().strip()
                if not amount_str:
                    input_status.configure(text="Amount is required.")
                    return
                amount = float(amount_str)
                if amount <= 0:
                    input_status.configure(text="Amount must be positive.")
                    return

                desc = desc_entry.get().strip()
                try:
                    custom_date = parse_flexible_date(date_entry.get())
                except ValueError:
                    input_status.configure(text=INVALID_DATE_MESSAGE)
                    return

                transaction = Expense(
                    amount, category_combo.get(), desc, custom_date
                )
                self.db.add_transaction(
                    self.current_user.get_user_id(),
                    transaction.transaction_type(),
                    transaction.amount,
                    transaction.category,
                    transaction.description,
                    custom_date=transaction.date
                )

                streak_notifications = self.db.update_streak_for_user(
                    self.current_user.get_user_id()
                )
                win.destroy()
                self.show_streak_notifications(streak_notifications)
                self.refresh_everything()
                self.check_budget_warning()
            except Exception as e:
                print("Transaction save error:", e)

        ctk.CTkButton(win, text="Save Transaction", command=save).pack(pady=15)

    def show_streak_notifications(self, notifications):
        if not notifications:
            return

        for notification in notifications:
            if notification.get("type") not in {"over_now", "over_limit"}:
                continue

            spent = notification.get("spent", 0)
            limit = notification.get("limit", 0)
            amount_over = notification.get("amount_over", max(0, spent - limit))

            alert = ctk.CTkToplevel(self)
            alert.title("Streak Ended")
            alert.geometry("430x230")
            alert.grab_set()

            ctk.CTkLabel(
                alert, text="Your saving streak ended",
                font=("Segoe UI", 22, "bold"), text_color="#EF4444"
            ).pack(pady=(25, 10), padx=20)

            ctk.CTkLabel(
                alert,
                text=(
                    f"You went ₱{amount_over:,.2f} over your budget limit.\n"
                    f"Spent: ₱{spent:,.2f} / Limit: ₱{limit:,.2f}"
                ),
                font=("Segoe UI", 15),
                justify="center",
                wraplength=360
            ).pack(padx=20, pady=(0, 20))

            ctk.CTkButton(
                alert, text="OK", width=140, command=alert.destroy
            ).pack(pady=(0, 20))
            break

    # =====================
    # FILTERING HELPERS
    # =====================

    def _filter_by_time_range(self, rows, time_filter):
        if time_filter == "All Time":
            return rows

        today = date.today()
        filtered = []

        for row in rows:
            try:
                d = datetime.strptime(row[6], "%Y-%m-%d").date()
            except Exception:
                continue

            include = False
            if time_filter == "Today":
                include = (d == today)
            elif time_filter == "This Week":
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                include = (start_of_week <= d <= end_of_week)
            elif time_filter == "This Month":
                include = (d.year == today.year and d.month == today.month)
            elif time_filter == "This Year":
                include = (d.year == today.year)

            if include:
                filtered.append(row)

        return filtered

    def search_transactions(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return

        keyword = self.search_entry.get().lower() if hasattr(self, "search_entry") else ""
        rows = self.db.get_transactions(self.current_user.get_user_id())

        time_filter = "All Time"
        if hasattr(self, "transaction_time_filter"):
            time_filter = self.transaction_time_filter.get()
        rows = self._filter_by_time_range(rows, time_filter)

        if hasattr(self, "transactions_list_frame"):
            for w in self.transactions_list_frame.winfo_children():
                w.destroy()

        total = 0
        count = 0

        for row in rows:
            tid, user_id, ttype, amount, category, desc, dstr = row
            line = f"{desc} {category} {amount:,.2f} {dstr}"
            if keyword and keyword not in line.lower():
                continue

            total += amount
            count += 1

            card = ctk.CTkFrame(self.transactions_list_frame, corner_radius=18)
            card.pack(fill="x", padx=10, pady=6)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(10, 4))

            ctk.CTkLabel(
                top_row, text="●", font=("Segoe UI", 18)
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                top_row, text=desc, font=("Segoe UI", 14, "bold")
            ).pack(side="left")

            ctk.CTkLabel(
                top_row, text=f"₱{amount:,.2f}",
                font=("Segoe UI", 14, "bold"), text_color="#EF4444"
            ).pack(side="right")

            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=15, pady=(0, 10))

            ctk.CTkLabel(
                bottom_row, text=category,
                font=("Segoe UI", 12), text_color="#9CA3AF"
            ).pack(side="left")

            ctk.CTkLabel(
                bottom_row, text=dstr,
                font=("Segoe UI", 12), text_color="#9CA3AF"
            ).pack(side="right")

        if hasattr(self, "transactions_list_frame"):
            footer = ctk.CTkFrame(self.transactions_list_frame, corner_radius=18)
            footer.pack(fill="x", padx=10, pady=10)
            ctk.CTkLabel(
                footer,
                text=f"Total: ₱{total:,.2f}  ({count} entries)",
                font=("Segoe UI", 13, "bold")
            ).pack(padx=15, pady=10)

    # =====================
    # DASHBOARD REFRESH
    # =====================

    def load_transactions(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return

        rows = self.db.get_transactions(self.current_user.get_user_id())

        if hasattr(self, "budget_preview_text"):
            self.budget_preview_text.delete("1.0", "end")

        self.categories = self.db.get_categories_for_user(self.current_user.get_user_id())
        self.category_totals = {c: 0 for c in self.categories}

        for row in rows:
            if row[2] == "Expense" and row[4] in self.category_totals:
                self.category_totals[row[4]] += row[3]

    def delete_latest_transaction(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
        DELETE FROM transactions
        WHERE id = (SELECT MAX(id) FROM transactions WHERE user_id = ?)
        """, (self.current_user.get_user_id(),))
        conn.commit()
        conn.close()
        self.refresh_everything()

    def delete_transaction_by_id(self, tid):
        if not self.current_user or self.current_user.get_user_id() is None:
            return
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM transactions WHERE id=? AND user_id=?",
            (tid, self.current_user.get_user_id())
        )
        conn.commit()
        conn.close()
        self.refresh_everything()

    def handle_delete_by_id(self):
        if not hasattr(self, "delete_id_entry"):
            return
        text = self.delete_id_entry.get().strip()
        if not text.isdigit():
            print("Invalid ID")
            return
        self.delete_transaction_by_id(int(text))