import customtkinter as ctk

from auth_mixin import AuthMixin
from budget_mixin import BudgetMixin
from dashboard_mixin import DashboardMixin
from database import DatabaseManager
from navigation_mixin import NavigationMixin
from reports_mixin import ReportsMixin
from settings_mixin import SettingsMixin
from transactions_mixin import TransactionsMixin


class COINSCASA(
    AuthMixin,
    NavigationMixin,
    DashboardMixin,
    TransactionsMixin,
    BudgetMixin,
    ReportsMixin,
    SettingsMixin,
    ctk.CTk,
):

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()

        self.title("COINSCASA")
        self.geometry("1500x900")
        self.minsize(1100, 700)
        self.after(0, lambda: self.state("zoomed"))  # open maximized

        self.categories = []
        self.active_button = None
        self.total_limit = 0
        self.period = "weekly"
        self.category_totals = {}
        self.profile_image = None

        self.current_user = None
        self.current_budget_limit = 0
        self.current_budget_type = None
        self.current_notifications_enabled = 0
        self.current_streak_current = 0
        self.current_streak_best = 0
        self.current_streak_last_success = None
        self.current_streak_last_checked = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_auth_page()

