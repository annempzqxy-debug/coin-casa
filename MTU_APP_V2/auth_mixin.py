import hashlib
import re
import os
import customtkinter as ctk
from PIL import Image
from models import User

from mixin_base import AppMixin

class AuthMixin(AppMixin):

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[^A-Za-z0-9]", password):
            return False
        return True

    # =====================
    # AUTH PAGE
    # =====================

    def create_auth_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.auth_frame = ctk.CTkFrame(self)
        self.auth_frame.pack(fill="both", expand=True)

        # ── Side logos (grayscale) ──────────────────────────────────
        gray_logo_img = None
        gray_logo_path = os.path.join(os.path.dirname(__file__), "gray_casa.png")
        if os.path.exists(gray_logo_path):
            try:
                pil_gray = Image.open(gray_logo_path).resize((200, 200))
                gray_logo_img = ctk.CTkImage(
                    light_image=pil_gray,
                    dark_image=pil_gray,
                    size=(200, 200)
                )
            except Exception:
                gray_logo_img = None

        if gray_logo_img:
            left_logo = ctk.CTkLabel(
                self.auth_frame,
                text="",
                image=gray_logo_img
            )
            left_logo.place(relx=0.13, rely=0.5, anchor="center")

            right_logo = ctk.CTkLabel(
                self.auth_frame,
                text="",
                image=gray_logo_img
            )
            right_logo.place(relx=0.87, rely=0.5, anchor="center")

            # Background center logo (large, faint)
            try:
                pil_bg = Image.open(gray_logo_path).resize((320, 320))
                bg_logo_img = ctk.CTkImage(
                    light_image=pil_bg,
                    dark_image=pil_bg,
                    size=(320, 320)
                )
                bg_label = ctk.CTkLabel(
                    self.auth_frame,
                    text="",
                    image=bg_logo_img
                )
                bg_label.place(relx=0.5, rely=0.5, anchor="center")
                bg_label.lower()
            except Exception:
                pass

        # ── Center card ────────────────────────────────────────────
        center = ctk.CTkFrame(
            self.auth_frame,
            width=420,
            height=650,
            corner_radius=25
        )
        center.place(relx=0.5, rely=0.5, anchor="center")
        center.pack_propagate(False)

        # ── App title: CoinsCasa styled ────────────────────────────
        title_frame = ctk.CTkFrame(center, fg_color="transparent")
        title_frame.pack(pady=(32, 4))

        # "COINS" in white/dark, "C" in gold, "ASA" in white/dark
        title_lbl = ctk.CTkLabel(
            title_frame,
            text="COINSCASA",
            font=("Georgia", 34, "bold"),
            text_color="#C9A84C"
        )
        title_lbl.pack()

        # Render styled title with mixed colors using a canvas-like approach
        # We'll use two labels side by side for the gold-C effect
        title_lbl.destroy()

        styled_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        styled_row.pack()

        mode = ctk.get_appearance_mode()
        base_color = "white" if mode == "Dark" else "#1a1a1a"

        ctk.CTkLabel(
            styled_row,
            text="COINS",
            font=("Georgia", 34, "bold"),
            text_color=base_color
        ).pack(side="left")

        ctk.CTkLabel(
            styled_row,
            text="C",
            font=("Georgia", 34, "bold"),
            text_color="#C9A84C"
        ).pack(side="left")

        ctk.CTkLabel(
            styled_row,
            text="ASA",
            font=("Georgia", 34, "bold"),
            text_color=base_color
        ).pack(side="left")

        ctk.CTkLabel(
            center,
            text="Login or Create an Account",
            font=("Segoe UI", 16),
            text_color="#9CA3AF"
        ).pack(pady=(0, 20))

        self.notifications_var = ctk.IntVar(value=0)

        self.username_entry = ctk.CTkEntry(
            center,
            placeholder_text="Username",
            width=300,
            height=45
        )
        self.username_entry.pack(pady=10)

        pw_frame = ctk.CTkFrame(center, fg_color="transparent", width=300)
        pw_frame.pack(pady=10)
        self.password_entry = ctk.CTkEntry(
            pw_frame,
            placeholder_text="Password",
            show="*",
            width=255,
            height=45
        )
        self.password_entry.pack(side="left")
        pw_eye_var = ctk.BooleanVar(value=False)
        def toggle_pw():
            pw_eye_var.set(not pw_eye_var.get())
            self.password_entry.configure(show="" if pw_eye_var.get() else "*")
            pw_eye_btn.configure(text="Hide" if pw_eye_var.get() else "Show")
        pw_eye_btn = ctk.CTkButton(
            pw_frame, text="Show", width=40, height=45,
            fg_color="transparent", hover_color="#374151",
            command=toggle_pw
        )
        pw_eye_btn.pack(side="left", padx=(4, 0))

        confirm_frame = ctk.CTkFrame(center, fg_color="transparent", width=300)
        confirm_frame.pack(pady=10)
        self.confirm_password_entry = ctk.CTkEntry(
            confirm_frame,
            placeholder_text="Confirm Password (for sign up)",
            show="*",
            width=255,
            height=45
        )
        self.confirm_password_entry.pack(side="left")
        confirm_eye_var = ctk.BooleanVar(value=False)
        def toggle_confirm():
            confirm_eye_var.set(not confirm_eye_var.get())
            self.confirm_password_entry.configure(show="" if confirm_eye_var.get() else "*")
            confirm_eye_btn.configure(text="Hide" if confirm_eye_var.get() else "Show")
        confirm_eye_btn = ctk.CTkButton(
            confirm_frame, text="Show", width=40, height=45,
            fg_color="transparent", hover_color="#374151",
            command=toggle_confirm
        )
        confirm_eye_btn.pack(side="left", padx=(4, 0))

        self.nickname_label = ctk.CTkLabel(
            center,
            text="",
            font=("Segoe UI", 18)
        )

        self.nickname_entry = ctk.CTkEntry(
            center,
            placeholder_text="Nickname",
            width=300,
            height=45
        )

        self.confirm_password_entry.bind(
            "<KeyRelease>",
            self.check_password_match
        )

        self.auth_status = ctk.CTkLabel(
            center,
            text="",
            text_color="red"
        )
        self.auth_status.pack(pady=5)

        ctk.CTkButton(
            center,
            text="Login",
            width=300,
            height=45,
            command=self.login_user
        ).pack(pady=(10, 10))

        ctk.CTkButton(
            center,
            text="Sign Up",
            width=300,
            height=45,
            fg_color="#3B82F6",
            command=self.signup_user
        ).pack(pady=10)

        ctk.CTkButton(
            center,
            text="Quit",
            width=300,
            height=45,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self.destroy
        ).pack(pady=(10, 20))

    def check_password_match(self, event=None):
        password = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        if password and confirm and password == confirm:
            if not self.nickname_label.winfo_ismapped():
                self.nickname_label.configure(text="Create Your Nickname")
                self.nickname_label.pack(pady=(10, 5))
                self.nickname_entry.pack(pady=(0, 10))
        else:
            if self.nickname_label.winfo_ismapped():
                self.nickname_label.pack_forget()
            if self.nickname_entry.winfo_ismapped():
                self.nickname_entry.pack_forget()

    # =====================
    # LOGIN
    # =====================

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        hashed = self.hash_password(password)

        user = self.db.validate_user(username, hashed)
        if user:
            (uid, uname, pw, nick, budget_limit, notif,
             budget_type, streak_current, streak_best,
             streak_last_success, streak_last_checked) = user

            self.current_user = User(
                uid, uname, nick, budget_limit,
                budget_type, notif, streak_current, streak_best
            )
            self.current_budget_limit = budget_limit or 0
            self.current_budget_type = budget_type
            self.current_notifications_enabled = notif or 0
            self.current_streak_current = streak_current or 0
            self.current_streak_best = streak_best or 0
            self.current_streak_last_success = streak_last_success
            self.current_streak_last_checked = streak_last_checked
            self.total_limit = self.current_budget_limit

            self.auth_frame.destroy()
            self.show_reminder_prompt()
        else:
            self.auth_status.configure(
                text="Invalid username or password.",
                text_color="red"
            )

    # =====================
    # SIGNUP
    # =====================

    def signup_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        nickname = self.nickname_entry.get().strip()
        notifications_enabled = 0

        if password != confirm_password:
            self.auth_status.configure(
                text="Passwords do not match.",
                text_color="red"
            )
            return

        if not nickname:
            nickname = username

        if len(username) < 3:
            self.auth_status.configure(
                text="Username must be at least 3 characters."
            )
            return

        if len(password) < 8:
            self.auth_status.configure(
                text="Password must be at least 8 characters."
            )
            return

        if not self.validate_password(password):
            self.auth_status.configure(
                text="Password needs uppercase, number, special character.",
                text_color="red"
            )
            return

        hashed = self.hash_password(password)
        success = self.db.create_user(username, hashed, nickname, 0, notifications_enabled)
        if not success:
            self.auth_status.configure(
                text="Username already exists (DB).",
                text_color="red"
            )
            return

        self.auth_status.configure(
            text="Account created successfully! You can now log in.",
            text_color="lightgreen"
        )

    # =====================
    # REMINDER PROMPT
    # =====================

    def show_reminder_prompt(self):
        reminder = ctk.CTkToplevel(self)
        reminder.title("Daily Reminder")
        reminder.geometry("500x260")
        reminder.grab_set()

        ctk.CTkLabel(
            reminder,
            text="Enable Daily Expense Reminders?",
            font=("Consolas", 24, "bold")
        ).pack(pady=(30, 15))

        message = (
            "You can receive a daily reminder to log\n"
            "your expenses. Would you like to enable it?"
        )

        ctk.CTkLabel(
            reminder,
            text=message,
            font=("Consolas", 18),
            justify="center"
        ).pack(pady=10)

        button_frame = ctk.CTkFrame(reminder, fg_color="transparent")
        button_frame.pack(pady=25)

        def enable_reminder():
            self.current_notifications_enabled = 1
            if self.current_user and self.current_user.get_user_id() is not None:
                self.db.update_user_notifications(self.current_user.get_user_id(), True)
            reminder.destroy()
            self.show_budget_setup_page()

        def skip_reminder():
            self.current_notifications_enabled = 0
            if self.current_user and self.current_user.get_user_id() is not None:
                self.db.update_user_notifications(self.current_user.get_user_id(), False)
            reminder.destroy()
            self.show_budget_setup_page()

        ctk.CTkButton(
            button_frame, text="✓ Enable", width=140, height=40,
            command=enable_reminder
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame, text="Ignore", width=140, height=40,
            fg_color="#6B7280", command=skip_reminder
        ).pack(side="left", padx=10)

    # =====================
    # BUDGET SETUP PAGE
    # =====================

    def show_budget_setup_page(self):
        budget = ctk.CTkToplevel(self)
        budget.title("Budget Setup")
        budget.geometry("700x540")
        budget.grab_set()

        ctk.CTkLabel(
            budget,
            text="Set Your Budget Limit",
            font=("Segoe UI", 32, "bold")
        ).pack(pady=(30, 20))

        desc = (
            "A spending limit helps you track expenses and build saving streaks.\n"
            "You can change this amount and period later in Settings."
        )

        ctk.CTkLabel(
            budget,
            text=desc,
            font=("Segoe UI", 18),
            justify="center"
        ).pack(pady=10)

        self.budget_type_var = ctk.StringVar(value="Weekly")

        period_frame = ctk.CTkFrame(budget, fg_color="transparent")
        period_frame.pack(pady=10)

        ctk.CTkLabel(
            period_frame,
            text="Budget Period:",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 5))

        for option in ["Daily", "Weekly", "Monthly", "Yearly"]:
            ctk.CTkRadioButton(
                period_frame, text=option,
                variable=self.budget_type_var, value=option,
                font=("Segoe UI", 18)
            ).pack(pady=3)

        amount_frame = ctk.CTkFrame(budget, fg_color="transparent")
        amount_frame.pack(pady=10)

        ctk.CTkLabel(
            amount_frame,
            text="Enter Your Budget Amount:",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 5))

        self.initial_budget_entry = ctk.CTkEntry(
            amount_frame,
            placeholder_text="e.g. 5000",
            width=220,
            height=45
        )
        self.initial_budget_entry.pack(pady=5)

        def continue_to_app():
            try:
                value_str = self.initial_budget_entry.get().strip()
                chosen_type_label = self.budget_type_var.get().lower()
                map_type = {
                    "daily": "daily", "weekly": "weekly",
                    "monthly": "monthly", "yearly": "yearly"
                }
                btype = map_type.get(chosen_type_label, "weekly")
                amount = 0.0
                if value_str:
                    amount = float(value_str)
                self.total_limit = amount
                self.current_budget_limit = amount
                self.current_budget_type = btype
                if self.current_user and self.current_user.get_user_id() is not None and amount > 0:
                    self.db.update_user_budget(self.current_user.get_user_id(), btype, amount)
            except Exception as e:
                print("Initial budget parse error:", e)

            budget.destroy()
            self.initialize_main_app()

        ctk.CTkButton(
            budget,
            text="Continue",
            width=250,
            height=50,
            command=continue_to_app
        ).pack(pady=30)