import customtkinter as ctk
from PIL import Image
from tkinter import filedialog

from mixin_base import AppMixin

class SettingsMixin(AppMixin):

    def create_settings_page(self):
        page = ctk.CTkScrollableFrame(self.container, fg_color="transparent")

        ctk.CTkLabel(
            page, text="Settings", font=("Segoe UI", 32, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # ── Profile ───────────────────────────────────────────────
        profile_main = ctk.CTkFrame(page, corner_radius=24)
        profile_main.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            profile_main, text="Profile", font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        def _pw_row(parent, entry_attr, placeholder):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=(0, 6))
            row.grid_columnconfigure(0, weight=1)
            entry = ctk.CTkEntry(row, placeholder_text=placeholder, height=40, show="*")
            entry.grid(row=0, column=0, sticky="ew")
            visible = ctk.BooleanVar(value=False)
            btn = ctk.CTkButton(
                row, text="Show", width=50, height=40,
                fg_color="transparent", hover_color="#374151",
                command=lambda: None
            )
            btn.grid(row=0, column=1, padx=(4, 0))
            def toggle(e=entry, v=visible, b=btn):
                v.set(not v.get())
                e.configure(show="" if v.get() else "*")
                b.configure(text="Hide" if v.get() else "Show")
            btn.configure(command=toggle)
            setattr(self, entry_attr, entry)

        # Username section — compact
        self.username_change_entry = ctk.CTkEntry(
            profile_main, placeholder_text="New Username", height=40
        )
        self.username_change_entry.pack(fill="x", padx=20, pady=(0, 6))

        _pw_row(profile_main, "username_current_password_entry",
                "Current Password (for username change)")

        ctk.CTkButton(
            profile_main, text="Update Username",
            width=220, height=38,
            command=self.update_username_with_password
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Password section
        _pw_row(profile_main, "new_password_entry", "New Password")
        _pw_row(profile_main, "current_password_for_change_entry",
                "Current Password (for password change)")

        ctk.CTkButton(
            profile_main, text="Update Password",
            width=220, height=38,
            command=self.update_password_with_verification
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Profile picture
        ctk.CTkButton(
            profile_main, text="Upload Profile Picture",
            width=220, height=38,
            command=self.upload_profile_picture
        ).pack(anchor="w", padx=20, pady=(0, 8))

        self.profile_image_size_var = ctk.IntVar(
            value=getattr(self, "profile_image_size", 110)
        )
        ctk.CTkLabel(
            profile_main, text="Profile Picture Size",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 2))

        ctk.CTkSlider(
            profile_main, from_=60, to=120, number_of_steps=6,
            variable=self.profile_image_size_var,
            command=self.resize_profile_picture
        ).pack(fill="x", padx=20, pady=(0, 10))

        # Nickname
        self.nickname_change = ctk.CTkEntry(
            profile_main, placeholder_text="Change Nickname", height=40
        )
        self.nickname_change.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkButton(
            profile_main, text="Update Nickname",
            width=220, height=38,
            command=self.update_nickname
        ).pack(anchor="w", padx=20, pady=(0, 18))

        # ── Budget Settings ───────────────────────────────────────
        budget_card = ctk.CTkFrame(page, corner_radius=24)
        budget_card.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            budget_card, text="Budget Settings", font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        self.limit_entry = ctk.CTkEntry(
            budget_card, placeholder_text="Set Budget Limit", height=40
        )
        if self.current_budget_limit:
            self.limit_entry.insert(0, str(self.current_budget_limit))
        self.limit_entry.pack(fill="x", padx=20, pady=(0, 8))

        budget_type_labels = {
            "daily": "Daily", "weekly": "Weekly",
            "monthly": "Monthly", "yearly": "Yearly"
        }
        self.settings_budget_type_var = ctk.StringVar(
            value=budget_type_labels.get(self.current_budget_type or "weekly", "Weekly")
        )
        ctk.CTkOptionMenu(
            budget_card,
            values=["Daily", "Weekly", "Monthly", "Yearly"],
            variable=self.settings_budget_type_var,
            height=40, width=200
        ).pack(anchor="w", padx=20, pady=(0, 8))

        ctk.CTkButton(
            budget_card, text="Apply Budget Limit",
            width=220, height=38,
            command=self.set_budget_limit
        ).pack(anchor="w", padx=20, pady=(0, 18))

        # ── Notifications ─────────────────────────────────────────
        notify_card = ctk.CTkFrame(page, corner_radius=24)
        notify_card.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            notify_card, text="Notifications", font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        self.settings_notifications_var = ctk.IntVar(
            value=self.current_notifications_enabled
        )
        ctk.CTkCheckBox(
            notify_card,
            text="Enable daily expense notifications",
            variable=self.settings_notifications_var,
            onvalue=1, offvalue=0,
            command=self.settings_toggle_notifications
        ).pack(anchor="w", padx=20, pady=(0, 18))

        # ── Application ───────────────────────────────────────────
        app_card = ctk.CTkFrame(page, corner_radius=24)
        app_card.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            app_card, text="Application", font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        btn_row = ctk.CTkFrame(app_card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=20, pady=(0, 18))

        ctk.CTkButton(
            btn_row, text="Delete Latest Transaction",
            fg_color="#EF4444", height=38, width=220,
            command=self.delete_latest_transaction
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="Export Financial Report",
            height=38, width=200,
            command=self.export_report
        ).pack(side="left")

        # ── Theme ─────────────────────────────────────────────────
        theme_card = ctk.CTkFrame(page, corner_radius=24)
        theme_card.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            theme_card, text="Theme", font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        theme_buttons_frame = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_buttons_frame.pack(anchor="w", padx=20, pady=(0, 18))

        for label, mode in [("Light", "Light"), ("Dark", "Dark"), ("System", "System")]:
            ctk.CTkButton(
                theme_buttons_frame, text=label, width=90, height=38,
                command=lambda m=mode: self.change_theme(m)
            ).pack(side="left", padx=(0, 8))

        return page

    def settings_toggle_notifications(self):
        new_val = self.settings_notifications_var.get()
        self.current_notifications_enabled = new_val
        if self.current_user and self.current_user.get_user_id() is not None:
            self.db.update_user_notifications(self.current_user.get_user_id(), new_val)

    # =====================
    # CATEGORIES PAGE — side-by-side add/delete panels
    # =====================

    def create_categories_page(self):
        page = ctk.CTkScrollableFrame(self.container, fg_color="transparent")

        ctk.CTkLabel(
            page, text="Categories", font=("Segoe UI", 30, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            page,
            text="View and manage your personal categories.",
            font=("Segoe UI", 15),
            text_color="#9CA3AF"
        ).pack(anchor="w", padx=20, pady=(0, 10))

        # Categories list
        self.categories_list_container = ctk.CTkFrame(page, corner_radius=20)
        self.categories_list_container.pack(
            fill="both", expand=True, padx=20, pady=(0, 10)
        )

        self.categories_listbox = ctk.CTkScrollableFrame(
            self.categories_list_container, height=220, corner_radius=16
        )
        self.categories_listbox.pack(fill="both", expand=True, padx=12, pady=12)

        # ── Add & Delete side by side ──────────────────────────────
        panels_row = ctk.CTkFrame(page, fg_color="transparent")
        panels_row.pack(fill="x", padx=20, pady=(0, 20))
        panels_row.grid_columnconfigure(0, weight=1, uniform="cat_panels")
        panels_row.grid_columnconfigure(1, weight=1, uniform="cat_panels")

        # Add panel
        add_frame = ctk.CTkFrame(panels_row, corner_radius=20)
        add_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(
            add_frame, text="Add Category", font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.new_category_entry = ctk.CTkEntry(
            add_frame, placeholder_text="Category Name", height=38
        )
        self.new_category_entry.pack(fill="x", padx=16, pady=(0, 6))

        self.category_status = ctk.CTkLabel(
            add_frame, text="", font=("Segoe UI", 12)
        )
        self.category_status.pack(anchor="w", padx=16, pady=(0, 4))

        ctk.CTkButton(
            add_frame, text="Add Category",
            height=36, command=self.add_new_category
        ).pack(fill="x", padx=16, pady=(0, 14))

        # Delete panel
        delete_frame = ctk.CTkFrame(panels_row, corner_radius=20)
        delete_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(
            delete_frame, text="Delete Category", font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.delete_category_entry = ctk.CTkEntry(
            delete_frame, placeholder_text="Category Name to delete", height=38
        )
        self.delete_category_entry.pack(fill="x", padx=16, pady=(0, 6))

        self.delete_category_status = ctk.CTkLabel(
            delete_frame, text="", font=("Segoe UI", 12)
        )
        self.delete_category_status.pack(anchor="w", padx=16, pady=(0, 4))

        ctk.CTkButton(
            delete_frame, text="Delete Category",
            height=36, fg_color="#EF4444", hover_color="#DC2626",
            command=self.delete_category_action
        ).pack(fill="x", padx=16, pady=(0, 14))

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
            card = ctk.CTkFrame(self.categories_listbox, corner_radius=14, height=50)
            card.pack(fill="x", padx=8, pady=4)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card, text="●", font=("Segoe UI", 18)
            ).pack(side="left", padx=(10, 6))

            name_text = cat + ("  (default)" if cat in default_cats else "")
            ctk.CTkLabel(
                card, text=name_text, font=("Segoe UI", 14, "bold")
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
    # PROFILE PICTURE / THEME
    # =====================

    def render_profile_picture(self):
        if not getattr(self, "profile_image_source", None):
            return
        size = int(getattr(self, "profile_image_size", 110))
        image = self.profile_image_source.copy().resize((size, size))
        profile_image = ctk.CTkImage(
            light_image=image, dark_image=image, size=(size, size)
        )
        self.profile_label.configure(text="", image=profile_image)
        self.profile_label._image = profile_image
        self.profile_label.image = profile_image

    def resize_profile_picture(self, value):
        self.profile_image_size = int(float(value))
        self.render_profile_picture()

    def upload_profile_picture(self):
        import os
        import shutil
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
            file_extension = os.path.splitext(file_path)[1]
            saved_path = os.path.join("profile_pics", f"user_{user_id}{file_extension}")
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
            print("Username updated successfully.")
        else:
            print("Failed to update username.")

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
            print("Password updated successfully.")
        else:
            print("Failed to update password.")