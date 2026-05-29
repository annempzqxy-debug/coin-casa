import hashlib
import sqlite3
from datetime import datetime, date, timedelta

from config import DB
from date_utils import today_str, week_key, month_key, year_key


class DatabaseManager:
    def __init__(self):
        self.create_tables()
        self.ensure_default_admin()

    def create_tables(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
        """)

        try:
            cur.execute("PRAGMA table_info(transactions)")
            columns = [row[1] for row in cur.fetchall()]
            if "user_id" not in columns:
                cur.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")
        except Exception as e:
            print("Migration error (transactions.user_id):", e)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            budget_limit REAL DEFAULT 0
        )
        """)

        cur.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cur.fetchall()]

        if "profile_picture" not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")

        try:
            cur.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cur.fetchall()]
            if "notifications_enabled" not in columns:
                cur.execute(
                    "ALTER TABLE users ADD COLUMN notifications_enabled INTEGER DEFAULT 0"
                )
        except Exception as e:
            print("Migration error (users.notifications_enabled):", e)

        try:
            cur.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cur.fetchall()]
            if "budget_type" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN budget_type TEXT")
            if "streak_current" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN streak_current INTEGER DEFAULT 0")
            if "streak_best" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN streak_best INTEGER DEFAULT 0")
            if "streak_last_success_period" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN streak_last_success_period TEXT")
            if "streak_last_checked_period" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN streak_last_checked_period TEXT")
        except Exception as e:
            print("Migration error (users budget/streak columns):", e)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS goals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            target REAL,
            saved REAL DEFAULT 0
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            UNIQUE(user_id, name)
        )
        """)

        default_categories = [
            "Food",
            "Housing",
            "Transport",
            "Shopping",
            "Entertainment",
            "Bills",
            "Savings"
        ]
        for cat in default_categories:
            cur.execute("""
            INSERT OR IGNORE INTO categories(name)
            VALUES (?)
            """, (cat,))

        try:
            conn.commit()
        except Exception as e:
            print("Database Error:", e)
            conn.rollback()
        finally:
            conn.close()

    def ensure_default_admin(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            exists = cur.fetchone()[0]
            if not exists:
                default_password = hashlib.sha256("Admin123!".encode()).hexdigest()
                cur.execute("""
                INSERT INTO users (username, password, nickname, budget_limit, notifications_enabled,
                                   budget_type, streak_current, streak_best,
                                   streak_last_success_period, streak_last_checked_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, ("admin", default_password, "Admin", 0, 0,
                      None, 0, 0, None, None))
                conn.commit()
                self.initialize_user_categories(cur.lastrowid)
                conn.commit()
        except Exception as e:
            print("Ensure admin error:", e)
        finally:
            conn.close()

    def initialize_user_categories(self, user_id):
        default_categories = [
            "Food",
            "Housing",
            "Transport",
            "Shopping",
            "Entertainment",
            "Bills",
            "Savings"
        ]
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            for cat in default_categories:
                cur.execute("""
                    INSERT OR IGNORE INTO user_categories(user_id, name)
                    VALUES (?, ?)
                """, (user_id, cat))
            conn.commit()
        except Exception as e:
            print("Init user categories error:", e)
            conn.rollback()
        finally:
            conn.close()

    def create_user(self, username, password_hashed, nickname="", budget_limit=0,
                    notifications_enabled=0):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO users
                (username, password, nickname, budget_limit, notifications_enabled,
                 budget_type, streak_current, streak_best,
                 streak_last_success_period, streak_last_checked_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (username, password_hashed, nickname, budget_limit, notifications_enabled,
                 None, 0, 0, None, None)
            )
            user_id = cur.lastrowid
            conn.commit()
            conn.close()
            self.initialize_user_categories(user_id)
            return True
        except Exception as e:
            print("Signup Error:", e)
            conn.rollback()
            conn.close()
            return False

    def validate_user(self, username, password_hashed):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, username, password, nickname, budget_limit, notifications_enabled,
                   budget_type, streak_current, streak_best,
                   streak_last_success_period, streak_last_checked_period
            FROM users
            WHERE username=? AND password=?
            """,
            (username, password_hashed)
        )
        user = cur.fetchone()
        conn.close()
        return user

    def update_user_nickname(self, user_id, nickname):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET nickname=? WHERE id=?",
                (nickname, user_id)
            )
            conn.commit()
        except Exception as e:
            print("Update nickname error:", e)
        finally:
            conn.close()

    def update_user_budget(self, user_id, budget_type, amount):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE users
                SET budget_type=?,
                    budget_limit=?,
                    streak_current=0,
                    streak_best=0,
                    streak_last_success_period=NULL,
                    streak_last_checked_period=?
                WHERE id=?
            """, (budget_type, amount, self.get_period_key(budget_type), user_id))
            conn.commit()
        except Exception as e:
            print("Update user budget error:", e)
            conn.rollback()
        finally:
            conn.close()

    def update_user_budget_limit_only(self, user_id, amount):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET budget_limit=? WHERE id=?",
                (amount, user_id)
            )
            conn.commit()
        except Exception as e:
            print("Update budget limit error:", e)
            conn.rollback()
        finally:
            conn.close()

    def update_user_notifications(self, user_id, enabled):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET notifications_enabled=? WHERE id=?",
                (1 if enabled else 0, user_id)
            )
            conn.commit()
        except Exception as e:
            print("Update notifications error:", e)
        finally:
            conn.close()

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, username, password, nickname, budget_limit, notifications_enabled,
                   budget_type, streak_current, streak_best,
                   streak_last_success_period, streak_last_checked_period
            FROM users
            WHERE id=?
            """,
            (user_id,)
        )
        user = cur.fetchone()
        conn.close()
        return user

    def update_user_profile_picture(self, user_id, image_path):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "UPDATE users SET profile_picture = ? WHERE id = ?",
            (image_path, user_id)
        )

        conn.commit()
        conn.close()

    def get_user_profile_picture(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute(
            "SELECT profile_picture FROM users WHERE id = ?",
            (user_id,)
        )

        result = cur.fetchone()
        conn.close()

        if result:
            return result[0]

        return None

    def add_transaction(self, user_id, ttype, amount, category, description, custom_date=None):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        if custom_date is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            date_str = custom_date

        cur.execute("""
        INSERT INTO transactions
        (
            user_id,
            type,
            amount,
            category,
            description,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
                    (
                        user_id,
                        ttype,
                        amount,
                        category,
                        description,
                        date_str
                    ))

        conn.commit()
        conn.close()

    def get_transactions(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
        """, (user_id,))

        rows = cur.fetchall()
        conn.close()
        return rows

    def get_income(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        SELECT COALESCE(
            SUM(amount),
            0
        )
        FROM transactions
        WHERE user_id = ? AND type='Income'
        """, (user_id,))

        value = cur.fetchone()[0]
        conn.close()
        return value

    def get_expense(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        SELECT COALESCE(
            SUM(amount),
            0
        )
        FROM transactions
        WHERE user_id = ? AND type='Expense'
        """, (user_id,))

        value = cur.fetchone()[0]
        conn.close()
        return value

    def get_categories_for_user(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM user_categories WHERE user_id=? ORDER BY name ASC",
            (user_id,)
        )
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def add_user_category(self, user_id, name):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO user_categories(user_id, name) VALUES (?, ?)",
                (user_id, name)
            )
            conn.commit()
            return True
        except Exception as e:
            print("Add user category error:", e)
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_user_category(self, user_id, name, default_cats=None):
        if default_cats is None:
            default_cats = [
                "Food",
                "Housing",
                "Transport",
                "Shopping",
                "Entertainment",
                "Bills",
                "Savings"
            ]
        if name in default_cats:
            return False, "Cannot delete a default category."

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM user_categories
                WHERE user_id=? AND name=?
            """, (user_id, name))
            if cur.rowcount == 0:
                conn.commit()
                return False, "Category not found."
            conn.commit()
            return True, f"Category '{name}' deleted."
        except Exception as e:
            print("Delete user category error:", e)
            conn.rollback()
            return False, "Delete failed."
        finally:
            conn.close()

    def get_period_key(self, budget_type, dstr=None):
        if dstr is None:
            dstr = today_str()
        if budget_type == "daily":
            return dstr
        if budget_type == "weekly":
            return week_key(dstr)
        if budget_type == "monthly":
            return month_key(dstr)
        if budget_type == "yearly":
            return year_key(dstr)
        return None

    def get_prev_period_key(self, budget_type, period_key):
        if budget_type == "daily":
            d = date.fromisoformat(period_key)
            return (d - timedelta(days=1)).isoformat()
        if budget_type == "weekly":
            yr, wk = period_key.split("-W")
            monday = date.fromisocalendar(int(yr), int(wk), 1)
            prev = monday - timedelta(weeks=1)
            y, w, _ = prev.isocalendar()
            return f"{y}-W{w:02d}"
        if budget_type == "monthly":
            yr, mo = map(int, period_key.split("-"))
            mo -= 1
            if mo == 0:
                yr -= 1
                mo = 12
            return f"{yr}-{mo:02d}"
        if budget_type == "yearly":
            return str(int(period_key) - 1)
        return None

    def get_period_total(self, user_id, budget_type, period_key=None):
        if period_key is None:
            period_key = self.get_period_key(budget_type)
        rows = self.get_transactions(user_id)
        total = 0.0
        for row in rows:
            ttype, amount, dstr = row[2], row[3], row[6]
            if ttype != "Expense":
                continue
            pk = self.get_period_key(budget_type, dstr)
            if pk == period_key:
                total += amount
        return total


    def get_period_bounds(self, budget_type, period_key):
        if budget_type == "daily":
            d = date.fromisoformat(period_key)
            return d, d
        if budget_type == "weekly":
            yr, wk = period_key.split("-W")
            start = date.fromisocalendar(int(yr), int(wk), 1)
            return start, start + timedelta(days=6)
        if budget_type == "monthly":
            yr, mo = map(int, period_key.split("-"))
            start = date(yr, mo, 1)
            if mo == 12:
                end = date(yr + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(yr, mo + 1, 1) - timedelta(days=1)
            return start, end
        if budget_type == "yearly":
            yr = int(period_key)
            return date(yr, 1, 1), date(yr, 12, 31)
        return None, None

    def get_period_history(self, user_id, budget_type):
        rows = self.get_transactions(user_id)
        periods = {}
        for row in rows:
            ttype, amount, dstr = row[2], row[3], row[6]
            if ttype != "Expense":
                continue
            try:
                d = date.fromisoformat(dstr)
                period_key = self.get_period_key(budget_type, dstr)
            except Exception:
                continue
            if period_key is None:
                continue
            info = periods.setdefault(period_key, {"total": 0.0, "dates": set()})
            info["total"] += amount
            info["dates"].add(d)

        history = []
        for period_key, info in periods.items():
            start, end = self.get_period_bounds(budget_type, period_key)
            history.append({
                "period": period_key,
                "start": start,
                "end": end,
                "total": info["total"],
                "dates": sorted(info["dates"]),
            })
        return sorted(history, key=lambda item: item["start"])

    def get_streak_summary_for_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if not user:
            return {"current": 0, "best": 0, "history": [], "budget_type": None, "limit": 0.0}

        budget_limit = float(user[4] or 0.0)
        budget_type = user[6]
        if not budget_type or budget_limit <= 0:
            return {"current": 0, "best": 0, "history": [], "budget_type": budget_type, "limit": budget_limit}

        current = 0
        best = 0
        history = []
        for item in self.get_period_history(user_id, budget_type):
            success = item["total"] <= budget_limit
            if success:
                current += 1
                best = max(best, current)
                status = "success"
            else:
                best = max(best, current)
                current = 0
                status = "failed"
            history.append({**item, "status": status, "limit": budget_limit, "streak_after": current})

        return {
            "current": current,
            "best": best,
            "history": history,
            "budget_type": budget_type,
            "limit": budget_limit,
        }

    def sync_streak_summary_for_user(self, user_id):
        summary = self.get_streak_summary_for_user(user_id)
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE users
                SET streak_current=?,
                    streak_best=?
                WHERE id=?
            """, (summary["current"], summary["best"], user_id))
            conn.commit()
        except Exception as e:
            print("Sync streak summary error:", e)
            conn.rollback()
        finally:
            conn.close()
        return summary

    def get_budget_status_for_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if not user:
            return 0.0, 0.0, 0.0, False, 0.0, None
        budget_limit = user[4] or 0.0
        budget_type = user[6]
        if not budget_limit or not budget_type:
            return 0.0, 0.0, 0.0, False, 0.0, budget_type

        spent = self.get_period_total(user_id, budget_type)
        limit = float(budget_limit)
        over = spent > limit

        if spent > limit:
            remaining = 0.0
            amount_over = spent - limit
        else:
            remaining = limit - spent
            amount_over = 0.0

        return spent, limit, remaining, over, amount_over, budget_type

    def update_streak_for_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if not user:
            return []

        budget_limit = float(user[4] or 0.0)
        budget_type = user[6]
        if not budget_type or budget_limit <= 0:
            return []

        before_current = user[7] or 0
        summary = self.sync_streak_summary_for_user(user_id)
        notifications = []

        history = summary["history"]
        if history:
            last = history[-1]
            if last["status"] == "failed" and before_current != 0:
                notifications.append({
                    "type": "over_now",
                    "spent": last["total"],
                    "limit": budget_limit,
                    "amount_over": last["total"] - budget_limit,
                    "period": last["period"],
                    "budget_type": budget_type,
                })

        return notifications


