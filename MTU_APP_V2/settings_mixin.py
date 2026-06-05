import customtkinter as ctk
from PIL import Image, ImageDraw
from tkinter import filedialog

from mixin_base import AppMixin

_CARD_PAD = 120


def crop_to_circle(image: Image.Image, size: int) -> Image.Image:
    """Resize image and crop it into a perfect circle with antialiasing."""
    # Resize to square first, then apply circular mask
    image = image.convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result


class SettingsMixin(AppMixin):

    def create_settings_page(self):
        page = ctk.CTkScrollableFrame(self.container, fg_color="transparent")

        ctk.CTkLabel(
            page, text="Settings", font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", padx=_CARD_PAD, pady=(20, 10))

        # ── Profile ───────────────────────────────────────────────
        profile_main = ctk.CTkFrame(page, corner_radius=20)
        profile_main.pack(fill="x", padx=_CARD_PAD, pady=(0, 12))

        ctk.CTkLabel(
            profile_main, text="Profile", font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        def _two_entries(parent, attr1, ph1, attr2, ph2):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=(0, 6))
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            e1 = ctk.CTkEntry(row, placeholder_text=ph1, height=38)
            e1.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            e2 = ctk.CTkEntry(row, placeholder_text=ph2, height=38)
            e2.grid(row=0, column=1, sticky="ew", padx=(4, 0))
            setattr(self, attr1, e1)
            setattr(self, attr2, e2)

        _two_entries(
            profile_main,
            "username_change_entry", "New Username",
            "username_current_password_entry", "Current Password"
        )
        ctk.CTkButton(
            profile_main, text="Update Username",
            width=180, height=36,
            command=self.update_username_with_password
        ).pack(anchor="w", padx=18, pady=(0, 10))

        def _pw_pair(parent, attr1, ph1, attr2, ph2):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=(0, 6))
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)

            col1 = ctk.CTkFrame(row, fg_color="transparent")
            col1.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            col1.grid_columnconfigure(0, weight=1)
            e1 = ctk.CTkEntry(col1, placeholder_text=ph1, height=38, show="*")
            e1.grid(row=0, column=0, sticky="ew")
            v1 = ctk.BooleanVar(value=False)
            b1 = ctk.CTkButton(col1, text="Show", width=46, height=38,
                               fg_color="transparent", hover_color="#374151",
                               command=lambda: None)
            b1.grid(row=0, column=1, padx=(3, 0))
            def t1(e=e1, v=v1, b=b1):
                v.set(not v.get()); e.configure(show="" if v.get() else "*")
                b.configure(text="Hide" if v.get() else "Show")
            b1.configure(command=t1)
            setattr(self, attr1, e1)

            col2 = ctk.CTkFrame(row, fg_color="transparent")
            col2.grid(row=0, column=1, sticky="ew", padx=(4, 0))
            col2.grid_columnconfigure(0, weight=1)
            e2 = ctk.CTkEntry(col2, placeholder_text=ph2, height=38, show="*")
            e2.grid(row=0, column=0, sticky="ew")
            v2 = ctk.BooleanVar(value=False)
            b2 = ctk.CTkButton(col2, text="Show", width=46, height=38,
                               fg_color="transparent", hover_color="#374151",
                               command=lambda: None)
            b2.grid(row=0, column=1, padx=(3, 0))
            def t2(e=e2, v=v2, b=b2):
                v.set(not v.get()); e.configure(show="" if v.get() else "*")
                b.configure(text="Hide" if v.get() else "Show")
            b2.configure(command=t2)
            setattr(self, attr2, e2)

        _pw_pair(profile_main,
                 "new_password_entry", "New Password",
                 "current_password_for_change_entry", "Current Password")
        ctk.CTkButton(
            profile_main, text="Update Password",
            width=180, height=36,
            command=self.update_password_with_verification
        ).pack(anchor="w", padx=18, pady=(0, 10))

        # Profile picture row
        pic_row = ctk.CTkFrame(profile_main, fg_color="transparent")
        pic_row.pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkButton(
            pic_row, text="Upload Profile Picture",
            width=200, height=36,
            command=self.upload_profile_picture
        ).pack(side="left", padx=(0, 10))

        self.profile_image_size_var = ctk.IntVar(
            value=getattr(self, "profile_image_size", 110)
        )
        slider_col = ctk.CTkFrame(pic_row, fg_color="transparent")
        slider_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            slider_col, text="Pic Size", font=("Segoe UI", 11)
        ).pack(anchor="w")
        ctk.CTkSlider(
            slider_col, from_=60, to=120, number_of_steps=6,
            variable=self.profile_image_size_var,
            command=self.resize_profile_picture
        ).pack(fill="x")

        # Nickname + button side by side
        nick_row = ctk.CTkFrame(profile_main, fg_color="transparent")
        nick_row.pack(fill="x", padx=18, pady=(0, 16))
        nick_row.grid_columnconfigure(0, weight=1)
        self.nickname_change = ctk.CTkEntry(
            nick_row, placeholder_text="Change Nickname", height=38
        )
        self.nickname_change.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(
            nick_row, text="Update", width=120, height=38,
            command=self.update_nickname
        ).grid(row=0, column=1)

        # ── Budget Settings ───────────────────────────────────────
        budget_card = ctk.CTkFrame(page, corner_radius=20)
        budget_card.pack(fill="x", padx=_CARD_PAD, pady=(0, 12))

        ctk.CTkLabel(
            budget_card, text="Budget Settings", font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        budget_row = ctk.CTkFrame(budget_card, fg_color="transparent")
        budget_row.pack(fill="x", padx=18, pady=(0, 8))
        budget_row.grid_columnconfigure(0, weight=1)
        budget_row.grid_columnconfigure(1, weight=1)

        self.limit_entry = ctk.CTkEntry(
            budget_row, placeholder_text="Budget Amount", height=38
        )
        if self.current_budget_limit:
            self.limit_entry.insert(0, str(self.current_budget_limit))
        self.limit_entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        budget_type_labels = {
            "daily": "Daily", "weekly": "Weekly",
            "monthly": "Monthly", "yearly": "Yearly"
        }
        self.settings_budget_type_var = ctk.StringVar(
            value=budget_type_labels.get(self.current_budget_type or "weekly", "Weekly")
        )
        ctk.CTkOptionMenu(
            budget_row,
            values=["Daily", "Weekly", "Monthly", "Yearly"],
            variable=self.settings_budget_type_var,
            height=38
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        ctk.CTkButton(
            budget_card, text="Apply Budget Limit",
            width=180, height=36,
            command=self.set_budget_limit
        ).pack(anchor="w", padx=18, pady=(0, 16))

        # ── Notifications ─────────────────────────────────────────
        notify_card = ctk.CTkFrame(page, corner_radius=20)
        notify_card.pack(fill="x", padx=_CARD_PAD, pady=(0, 12))

        ctk.CTkLabel(
            notify_card, text="Notifications", font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        self.settings_notifications_var = ctk.IntVar(
            value=self.current_notifications_enabled
        )
        ctk.CTkCheckBox(
            notify_card,
            text="Enable daily expense notifications",
            variable=self.settings_notifications_var,
            onvalue=1, offvalue=0,
            command=self.settings_toggle_notifications
        ).pack(anchor="w", padx=18, pady=(0, 16))

        # ── Application ───────────────────────────────────────────
        app_card = ctk.CTkFrame(page, corner_radius=20)
        app_card.pack(fill="x", padx=_CARD_PAD, pady=(0, 12))

        ctk.CTkLabel(
            app_card, text="Application", font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        app_btn_row = ctk.CTkFrame(app_card, fg_color="transparent")
        app_btn_row.pack(anchor="w", padx=18, pady=(0, 16))

        ctk.CTkButton(
            app_btn_row, text="Delete Latest Transaction",
            fg_color="#EF4444", hover_color="#DC2626",
            height=36, width=210,
            command=self.delete_latest_transaction
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            app_btn_row, text="Export Report",
            height=36, width=160,
            command=self.export_report
        ).pack(side="left")

        # ── Theme ─────────────────────────────────────────────────
        theme_card = ctk.CTkFrame(page, corner_radius=20)
        theme_card.pack(fill="x", padx=_CARD_PAD, pady=(0, 20))

        ctk.CTkLabel(
            theme_card, text="Theme", font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        theme_row = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_row.pack(anchor="w", padx=18, pady=(0, 16))

        for label in ["Light", "Dark", "System"]:
            ctk.CTkButton(
                theme_row, text=label, width=80, height=36,
                command=lambda m=label: self.change_theme(m)
            ).pack(side="left", padx=(0, 8))

        return page

    def settings_toggle_notifications(self):
        new_val = self.settings_notifications_var.get()
        self.current_notifications_enabled = new_val
        if self.current_user and self.current_user.get_user_id() is not None:
            self.db.update_user_notifications(self.current_user.get_user_id(), new_val)

    # =====================
    # CATEGORIES PAGE
    # =====================

    def create_categories_page(self):
        page = ctk.CTkScrollableFrame(self.container, fg_color="transparent")

        ctk.CTkLabel(
            page, text="Categories", font=("Segoe UI", 28, "bold")
        ).pack(anchor="w", padx=_CARD_PAD, pady=(20, 4))

        ctk.CTkLabel(
            page,
            text="View and manage your personal categories.",
            font=("Segoe UI", 14),
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=_CARD_PAD, pady=(0, 10))

        self.categories_list_container = ctk.CTkFrame(page, corner_radius=18)
        self.categories_list_container.pack(
            fill="x", padx=_CARD_PAD, pady=(0, 10)
        )

        self.categories_listbox = ctk.CTkScrollableFrame(
            self.categories_list_container, height=200, corner_radius=14
        )
        self.categories_listbox.pack(fill="x", padx=12, pady=12)

        panels_row = ctk.CTkFrame(page, fg_color="transparent")
        panels_row.pack(fill="x", padx=_CARD_PAD, pady=(0, 20))
        panels_row.grid_columnconfigure(0, weight=1, uniform="cat_panels")
        panels_row.grid_columnconfigure(1, weight=1, uniform="cat_panels")

        add_frame = ctk.CTkFrame(panels_row, corner_radius=18)
        add_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            add_frame, text="Add Category", font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 6))

        self.new_category_entry = ctk.CTkEntry(
            add_frame, placeholder_text="Category Name", height=36
        )
        self.new_category_entry.pack(fill="x", padx=14, pady=(0, 4))

        self.category_status = ctk.CTkLabel(
            add_frame, text="", font=("Segoe UI", 11)
        )
        self.category_status.pack(anchor="w", padx=14)

        ctk.CTkButton(
            add_frame, text="Add Category", height=34,
            command=self.add_new_category
        ).pack(fill="x", padx=14, pady=(4, 12))

        delete_frame = ctk.CTkFrame(panels_row, corner_radius=18)
        delete_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(
            delete_frame, text="Delete Category", font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 6))

        self.delete_category_entry = ctk.CTkEntry(
            delete_frame, placeholder_text="Category to delete", height=36
        )
        self.delete_category_entry.pack(fill="x", padx=14, pady=(0, 4))

        self.delete_category_status = ctk.CTkLabel(
            delete_frame, text="", font=("Segoe UI", 11)
        )
        self.delete_category_status.pack(anchor="w", padx=14)

        ctk.CTkButton(
            delete_frame, text="Delete Category", height=34,
            fg_color="#EF4444", hover_color="#DC2626",
            command=self.delete_category_action
        ).pack(fill="x", padx=14, pady=(4, 12))

        return page

    def load_categories_ui(self):
        if not hasattr(self, "categories_listbox") or not self.current_user \
                or self.current_user.get_user_id() is None:
            return

        self.categories = self.db.get_categories_for_user(self.current_user.get_user_id())
        for w in self.categories_listbox.winfo_children():
            w.destroy()

        default_cats = [
            "Food", "Housing", "Transport", "Shopping",
            "Entertainment", "Bills", "Savings"
        ]
        for cat in self.categories:
            card = ctk.CTkFrame(self.categories_listbox, corner_radius=12, height=46)
            card.pack(fill="x", padx=6, pady=3)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card, text="●", font=("Segoe UI", 16)
            ).pack(side="left", padx=(10, 6))

            name_text = cat + ("  (default)" if cat in default_cats else "")
            ctk.CTkLabel(
                card, text=name_text, font=("Segoe UI", 13, "bold")
            ).pack(side="left")

    def add_new_category(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return
        name = self.new_category_entry.get().strip()
        if not name:
            self.category_status.configure(
                text="Name cannot be empty.", text_color="#EF4444"
            )
            return

        success = self.db.add_user_category(self.current_user.get_user_id(), name)
        if not success:
            self.category_status.configure(
                text="Already exists or failed.", text_color="#EF4444"
            )
            return

        self.category_status.configure(
            text="Added successfully.", text_color="#22C55E"
        )
        self.new_category_entry.delete(0, "end")
        self.categories = self.db.get_categories_for_user(self.current_user.get_user_id())
        self.load_categories_ui()

        if "Summary" in self.pages:
            self.pages["Summary"].destroy()
            self.pages["Summary"] = self.create_summary_page()
            self.pages["Summary"].grid_forget()

        self.refresh_everything()

    def delete_category_action(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return
        name = self.delete_category_entry.get().strip()
        if not name:
            self.delete_category_status.configure(
                text="Name cannot be empty.", text_color="#EF4444"
            )
            return
        success, msg = self.db.delete_user_category(self.current_user.get_user_id(), name)
        self.delete_category_status.configure(
            text=msg, text_color="#22C55E" if success else "#EF4444"
        )
        if success:
            self.delete_category_entry.delete(0, "end")
            self.load_categories_ui()
            self.refresh_everything()

    # =====================
    # PROFILE PICTURE
    # =====================

    def render_profile_picture(self):
        """Render the profile picture cropped to a circle."""
        if not getattr(self, "profile_image_source", None):
            return
        size = int(getattr(self, "profile_image_size", 110))
        circular = crop_to_circle(self.profile_image_source.copy(), size)
        profile_image = ctk.CTkImage(
            light_image=circular, dark_image=circular, size=(size, size)
        )
        # Make the frame and label transparent so only the circular image shows
        if hasattr(self, "profile_frame"):
            self.profile_frame.configure(fg_color="transparent")
        self.profile_label.configure(
            text="", image=profile_image, fg_color="transparent"
        )
        self.profile_label._image = profile_image
        self.profile_label.image = profile_image

    def resize_profile_picture(self, value):
        self.profile_image_size = int(float(value))
        self.render_profile_picture()

    def upload_profile_picture(self):
        import os, shutil
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return
        try:
            if not self.current_user:
                return
            user_id = self.current_user.get_user_id()
            os.makedirs("profile_pics", exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            saved_path = os.path.join("profile_pics", f"user_{user_id}{ext}")
            shutil.copy(file_path, saved_path)
            self.db.update_user_profile_picture(user_id, saved_path)
            self.profile_image_source = Image.open(saved_path)
            self.render_profile_picture()
        except Exception as e:
            print("Profile Picture Error:", e)

    def load_profile_picture(self):
        import os
        try:
            if not self.current_user:
                return
            user_id = self.current_user.get_user_id()
            image_path = self.db.get_user_profile_picture(user_id)
            if not image_path or not os.path.exists(image_path):
                return
            self.profile_image_source = Image.open(image_path)
            self.render_profile_picture()
        except Exception as e:
            print("Load Profile Picture Error:", e)

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode.lower())

    # =====================
    # UPDATE NICKNAME / USERNAME / PASSWORD
    # =====================

    def update_nickname(self):
        new_name = self.nickname_change.get().strip()
        if not new_name or not self.current_user or self.current_user.get_user_id() is None:
            return
        self.db.update_user_nickname(self.current_user.get_user_id(), new_name)
        self.current_user.set_nickname(new_name)
        if hasattr(self, "nickname_display"):
            self.nickname_display.configure(text=new_name)

    def update_username_with_password(self):
        import hashlib
        new_username = self.username_change_entry.get().strip()
        current_password = self.username_current_password_entry.get().strip()
        if not new_username or not current_password:
            return
        hashed = hashlib.sha256(current_password.encode()).hexdigest()
        user = self.db.validate_user(self.current_user.get_username(), hashed)
        if not user:
            print("Incorrect current password.")
            return
        success = self.db.update_user_username(self.current_user.get_user_id(), new_username)
        if success:
            self.current_user.set_username(new_username)
            self.username_change_entry.delete(0, "end")
            self.username_current_password_entry.delete(0, "end")

    def update_password_with_verification(self):
        import hashlib
        new_password = self.new_password_entry.get().strip()
        current_password = self.current_password_for_change_entry.get().strip()
        if not new_password or not current_password:
            return
        hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
        user = self.db.validate_user(self.current_user.get_username(), hashed_current)
        if not user:
            print("Incorrect current password.")
            return
        hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
        success = self.db.update_user_password(self.current_user.get_user_id(), hashed_new)
        if success:
            self.new_password_entry.delete(0, "end")
            self.current_password_for_change_entry.delete(0, "end")