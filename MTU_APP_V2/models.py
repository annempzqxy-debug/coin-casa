from abc import ABC, abstractmethod

class User:
    def __init__(self, user_id, username, nickname,
                 budget_limit=0, budget_type=None,
                 notifications_enabled=0,
                 streak_current=0,
                 streak_best=0):

        self.__user_id = user_id
        self.__username = username
        self.__nickname = nickname
        self.__budget_limit = budget_limit
        self.__budget_type = budget_type
        self.__notifications_enabled = notifications_enabled
        self.__streak_current = streak_current
        self.__streak_best = streak_best

    def get_user_id(self):
        return self.__user_id

    def get_username(self):
        return self.__username

    def get_nickname(self):
        return self.__nickname

    def get_budget_limit(self):
        return self.__budget_limit

    def get_budget_type(self):
        return self.__budget_type

    def get_notifications(self):
        return self.__notifications_enabled

    def get_streak(self):
        return self.__streak_current

    def get_best_streak(self):
        return self.__streak_best

    def set_nickname(self, nickname):
        self.__nickname = nickname

    def set_budget_limit(self, amount):
        self.__budget_limit = amount

    def set_budget_type(self, budget_type):
        self.__budget_type = budget_type

    def set_notifications(self, value):
        self.__notifications_enabled = value

    def set_streak(self, streak):
        self.__streak_current = streak

class Transaction(ABC):
    def __init__(self, amount, category, description, date):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date

    @abstractmethod
    def transaction_type(self):
        pass

class Expense(Transaction):
    def transaction_type(self):
        return "Expense"

class Income(Transaction):
    def transaction_type(self):
        return "Income"