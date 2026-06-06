import hashlib
import os
import re

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFilter

from mixin_base import AppMixin
from models import User


ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
BADGE_PATH = os.path.join(ASSET_DIR, "casa.png")
ICON_PATH = os.path.join(ASSET_DIR, "coinscasa_icon.png")
COIN_LEFT_PATH = os.path.join(ASSET_DIR, "3.png")
COIN_RIGHT_PATH = os.path.join(ASSET_DIR, "4.png")


def _remove_black_bg(image, threshold=80):
    """Remove black background with smooth edge falloff."""
    image = image.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            brightness = (r + g + b) / 3
            if brightness < threshold:
                pixels[x, y] = (r, g, b, 0)
            elif brightness < threshold * 2.0:
                alpha = int(255 * ((brightness - threshold) / threshold))
                pixels[x, y] = (r, g, b, alpha)
    return image


def _add_gold_ring(image, ring_width=6, color="#D8A338"):
    """Add a gold circular ring border around the badge image."""
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)
    w, h = image.size
    margin = ring_width // 2
    draw.ellipse(
        [margin, margin, w - margin - 1, h - margin - 1],
        outline=color,
        width=ring_width,
    )
    return image


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

    def _auth_ctk_image(self, path, size, opacity=1.0, remove_black=False, gold_ring=False):
        if not os.path.exists(path):
            return None
        image = Image.open(path).convert("RGBA")


        if remove_black:
            image = _remove_black_bg(image)
        if gold_ring:
            image = _add_gold_ring(image)
        if opacity < 1.0:
            r, g, b, a = image.split()
            a = a.point(lambda x: int(x * opacity))
            image = Image.merge("RGBA", (r, g, b, a))
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)

    def _set_auth_icon(self):
        if not os.path.exists(ICON_PATH):
            return
        try:
            icon_img = ImageTk.PhotoImage(Image.open(ICON_PATH).convert("RGBA"))
            self.iconphoto(True, icon_img)
            self._icon_ref = icon_img
        except Exception as exc:
            print("Icon error:", exc)

    def _make_auth_input(self, parent, icon_text, placeholder, show=None):
        row = ctk.CTkFrame(
            parent,
            width=486,
            height=62,
            corner_radius=10,
            fg_color="#17191C",
            border_width=1,
            border_color="#3B4149",
        )
        row.pack_propagate(False)

        ctk.CTkLabel(
            row,
            text=icon_text,
            width=42,
            font=("Segoe UI Emoji", 22),
            text_color="#9CA3AF",
        ).pack(side="left", padx=(14, 4))

        entry = ctk.CTkEntry(
            row,
            placeholder_text=placeholder,
            show=show,
            border_width=0,
            fg_color="#17191C",
            text_color="#E5E7EB",
            placeholder_text_color="#9CA3AF",
            height=44,
            font=("Segoe UI", 18),
        )
        entry.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)

        return row, entry

    def _make_password_input(self, parent, placeholder):
        row, entry = self._make_auth_input(parent, "🔒", placeholder, show="*")
        visible = ctk.BooleanVar(value=False)

        def toggle_visibility():
            visible.set(not visible.get())
            entry.configure(show="" if visible.get() else "*")
            toggle.configure(text="👁 Hide" if visible.get() else "👁 Show")

        toggle = ctk.CTkButton(
            row,
            text="👁 Show",
            width=90,
            height=42,
            fg_color="transparent",
            hover_color="#242A31",
            text_color="#B6BDC8",
            font=("Segoe UI Emoji", 14),
            command=toggle_visibility,
        )
        toggle.pack(side="right", padx=(0, 10))
        return row, entry

    def _make_auth_button(self, parent, text, color, hover, command):
        return ctk.CTkButton(
            parent,
            text=text,
            width=486,
            height=56,
            corner_radius=10,
            fg_color=color,
            hover_color=hover,
            text_color="white",
            font=("Segoe UI Emoji", 18, "bold"),
            command=command,
        )

    # =====================
    # AUTH PAGE
    # =====================

    def create_auth_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.title("CoinsCasa")
        self._set_auth_icon()
        self.auth_frame = ctk.CTkFrame(self, fg_color="#121416")
        self.auth_frame.pack(fill="both", expand=True)
        self.auth_frame.grid_rowconfigure(0, weight=1)
        self.auth_frame.grid_columnconfigure(0, weight=1)
        self._auth_images = []

        # =====================
        # BACKGROUND COINS
        # =====================

        left_coin_img = self._auth_ctk_image(
            COIN_LEFT_PATH,
            (600, 600),
            opacity=0.18,
            remove_black=False
        )

        if left_coin_img:
            self._auth_images.append(left_coin_img)

            self.left_coin = ctk.CTkLabel(
                self.auth_frame,
                text="",
                image=left_coin_img,
                fg_color="transparent"
            )

            self.left_coin.place(
                x=190,
                y=450,
                anchor="center"
            )

        right_coin_img = self._auth_ctk_image(
            COIN_RIGHT_PATH,
            (600, 600),
            opacity=0.18,
            remove_black=False
        )

        if right_coin_img:
            self._auth_images.append(right_coin_img)

            self.right_coin = ctk.CTkLabel(
                self.auth_frame,
                text="",
                image=right_coin_img,
                fg_color="transparent"
            )

            self.right_coin.place(
                x=1310,
                y=450,
                anchor="center"
            )

        glow = ctk.CTkFrame(
            self.auth_frame,
            width=600,
            height=820,
            corner_radius=34,
            fg_color="#111315",
        )
        glow.place(relx=0.5, rely=0.515, anchor="center")

        center = ctk.CTkFrame(
            self.auth_frame,
            width=560,
            height=790,
            corner_radius=30,
            fg_color="#1C1F22",
            border_width=1,
            border_color="#22262B",
        )

        center.place(relx=0.5, rely=0.5, anchor="center")
        center.pack_propagate(False)



        badge_img = self._auth_ctk_image(BADGE_PATH, (140, 140), gold_ring=True, remove_black=True)
        if badge_img:
            self._auth_images.append(badge_img)
            ctk.CTkLabel(
                center, text="", image=badge_img, fg_color="transparent"
            ).pack(pady=(20, 2))
        else:
            ctk.CTkLabel(
                center, text="$", font=("Georgia", 76, "bold"), text_color="#D8A338"
            ).pack(pady=(30, 4))

        title_row = ctk.CTkFrame(center, fg_color="transparent")
        title_row.pack(pady=(0, 8))
        title_font = ("Georgia", 42, "bold")
        ctk.CTkLabel(title_row, text="COINS", font=title_font, text_color="#F8F8F8").pack(side="left")
        ctk.CTkLabel(title_row, text="C", font=title_font, text_color="#D8A338").pack(side="left")
        ctk.CTkLabel(title_row, text="ASA", font=title_font, text_color="#F8F8F8").pack(side="left")

        ctk.CTkLabel(
            center,
            text="Login or Create an Account",
            font=("Segoe UI", 18),
            text_color="#9CA3AF",
        ).pack(pady=(0, 18))

        self.notifications_var = ctk.IntVar(value=0)

        self.username_row, self.username_entry = self._make_auth_input(
            center, "👤", "Username"
        )
        self.username_row.pack(pady=(0, 14))

        self.password_row, self.password_entry = self._make_password_input(
            center, "Password"
        )
        self.password_row.pack(pady=(0, 14))

        self.confirm_row, self.confirm_password_entry = self._make_password_input(
            center,
            "Confirm Password (for sign up)",
        )
        self.confirm_row.pack(pady=(0, 14))
        self.confirm_password_entry.bind("<KeyRelease>", self.check_password_match)

        self.nickname_label = ctk.CTkLabel(
            center,
            text="Create Your Nickname",
            font=("Segoe UI", 14, "bold"),
            text_color="#9CA3AF",
        )
        self.nickname_row, self.nickname_entry = self._make_auth_input(
            center, "✏️", "Nickname"
        )

        self.auth_status = ctk.CTkLabel(
            center,
            text="",
            width=486,
            height=22,
            font=("Segoe UI", 13),
            text_color="#F87171",
        )
        self.auth_status.pack(pady=(0, 10))

        self._make_auth_button(
            center,
            "→  Login",
            "#0F67A8",
            "#0C5A94",
            self.login_user,
        ).pack(pady=(0, 10))

        self._make_auth_button(
            center,
            "👤+  Sign Up",
            "#2F80FF",
            "#246FE5",
            self.signup_user,
        ).pack(pady=(0, 10))

        self._make_auth_button(
            center,
            "✕  Quit",
            "#EF1F2D",
            "#CF1824",
            self.destroy,
        ).pack(pady=(0, 16))

    def check_password_match(self, event=None):
        password = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        if password and confirm and password == confirm:
            if not self.nickname_row.winfo_ismapped():
                self.nickname_label.pack(before=self.auth_status, pady=(0, 6))
                self.nickname_row.pack(before=self.auth_status, pady=(0, 10))
        else:
            if self.nickname_label.winfo_ismapped():
                self.nickname_label.pack_forget()
            if self.nickname_row.winfo_ismapped():
                self.nickname_row.pack_forget()

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
                text="Invalid username or password.", text_color="red"
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
            self.auth_status.configure(text="Passwords do not match.", text_color="red")
            return
        if not nickname:
            nickname = username
        if len(username) < 3:
            self.auth_status.configure(text="Username must be at least 3 characters.")
            return
        if len(password) < 8:
            self.auth_status.configure(text="Password must be at least 8 characters.")
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
            self.auth_status.configure(text="Username already exists.", text_color="red")
            return
        self.auth_status.configure(
            text="Account created! You can now log in.", text_color="lightgreen"
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
            reminder, text="Enable Daily Expense Reminders?",
            font=("Consolas", 22, "bold")
        ).pack(pady=(30, 15))

        ctk.CTkLabel(
            reminder,
            text="You can receive a daily reminder to log\nyour expenses. Would you like to enable it?",
            font=("Consolas", 16), justify="center"
        ).pack(pady=10)

        button_frame = ctk.CTkFrame(reminder, fg_color="transparent")
        button_frame.pack(pady=25)

        def enable_reminder():
            self.current_notifications_enabled = 1
            if self.current_user and self.current_user.get_user_id() is not None:
                self.db.update_user_notifications(self.current_user.get_user_id(), True)
            reminder.destroy()
            if self.current_budget_limit and self.current_budget_limit > 0:
                self.initialize_main_app()
            else:
                self.show_budget_setup_page()

        def skip_reminder():
            self.current_notifications_enabled = 0
            if self.current_user and self.current_user.get_user_id() is not None:
                self.db.update_user_notifications(self.current_user.get_user_id(), False)
            reminder.destroy()
            if self.current_budget_limit and self.current_budget_limit > 0:
                self.initialize_main_app()
            else:
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
            budget, text="Set Your Budget Limit", font=("Segoe UI", 30, "bold")
        ).pack(pady=(30, 20))

        ctk.CTkLabel(
            budget,
            text="A spending limit helps you track expenses and build saving streaks.\n"
                 "You can change this amount and period later in Settings.",
            font=("Segoe UI", 16), justify="center"
        ).pack(pady=10)

        self.budget_type_var = ctk.StringVar(value="Weekly")

        period_frame = ctk.CTkFrame(budget, fg_color="transparent")
        period_frame.pack(pady=10)
        ctk.CTkLabel(
            period_frame, text="Budget Period:", font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 5))

        for option in ["Daily", "Weekly", "Monthly", "Yearly"]:
            ctk.CTkRadioButton(
                period_frame, text=option,
                variable=self.budget_type_var, value=option,
                font=("Segoe UI", 16)
            ).pack(pady=3)

        amount_frame = ctk.CTkFrame(budget, fg_color="transparent")
        amount_frame.pack(pady=10)
        ctk.CTkLabel(
            amount_frame, text="Enter Your Budget Amount:", font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 5))
        self.initial_budget_entry = ctk.CTkEntry(
            amount_frame, placeholder_text="e.g. 5000", width=220, height=44
        )
        self.initial_budget_entry.pack(pady=5)

        def continue_to_app():
            try:
                value_str = self.initial_budget_entry.get().strip()
                chosen = self.budget_type_var.get().lower()
                btype = {"daily": "daily", "weekly": "weekly",
                         "monthly": "monthly", "yearly": "yearly"}.get(chosen, "weekly")
                amount = float(value_str) if value_str else 0.0
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
            budget, text="Continue", width=250, height=44,
            command=continue_to_app
        ).pack(pady=30)