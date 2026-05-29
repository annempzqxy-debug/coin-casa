import calendar
import sqlite3
from datetime import datetime, date, timedelta
from tkinter import filedialog
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import DB


from mixin_base import AppMixin
class ReportsMixin(AppMixin):

    # =====================
    # GRAPH THEME HELPERS
    # =====================

    def _graph_colors(self):
        """Return (bg, axes_bg, text, grid, bar) colours based on current CTk mode."""
        mode = ctk.get_appearance_mode()  # "Dark" or "Light"
        if mode == "Dark":
            return {
                "fig_bg":   "#1a1a2e",   # very dark navy — deeper than the app bg
                "axes_bg":  "#16213e",   # slightly lighter dark box for the plot area
                "text":     "#e2e8f0",   # light grey text / ticks
                "grid":     "#2d3748",   # subtle dark gridlines
                "bar":      "#3B82F6",   # blue bars (unchanged)
            }
        else:
            return {
                "fig_bg":   "#dde3ec",   # slightly off-white frame around the chart
                "axes_bg":  "#ffffff",   # crisp white plot area
                "text":     "#1f2937",   # near-black text / ticks
                "grid":     "#cbd5e1",   # soft light-grey gridlines
                "bar":      "#3B82F6",
            }

    def _style_axes(self, ax, fig, colors):
        """Apply background colours, spine colours and grid to an axes object."""
        fig.patch.set_facecolor(colors["fig_bg"])
        ax.set_facecolor(colors["axes_bg"])
        ax.tick_params(colors=colors["text"], labelcolor=colors["text"])
        for spine in ax.spines.values():
            spine.set_edgecolor(colors["grid"])
        ax.title.set_color(colors["text"])
        ax.xaxis.label.set_color(colors["text"])
        ax.yaxis.label.set_color(colors["text"])

    def create_reports_page(self):
        page = ctk.CTkScrollableFrame(self.container)

        header = ctk.CTkFrame(page)
        header.pack(fill="x", pady=10)

        self.period_button = ctk.CTkButton(
            header,
            text=self.period.title(),
            command=self.change_period
        )
        self.period_button.pack(side="left", padx=10)

        self.report_total = ctk.CTkLabel(
            header,
            text="Total Spending: ₱0.00",
            font=("Segoe UI", 18, "bold")
        )
        self.report_total.pack(side="left", padx=20)

        self.analytics_label = ctk.CTkLabel(
            page,
            text="Summary Analytics",
            font=("Segoe UI", 24, "bold")
        )
        self.analytics_label.pack(pady=10)

        self.chart_frame = ctk.CTkFrame(page)
        self.chart_frame.pack(fill="both", expand=True)

        colors = self._graph_colors()

        self.figure = Figure(figsize=(10, 4.8), dpi=100)
        self.figure.patch.set_facecolor(colors["fig_bg"])
        self.ax = self.figure.add_subplot(111)
        self._style_axes(self.ax, self.figure, colors)

        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.pie_frame = ctk.CTkFrame(page)
        self.pie_frame.pack(fill="both", expand=True, pady=10)

        self.pie_figure = Figure(figsize=(10, 9), dpi=100)
        self.pie_figure.patch.set_facecolor(colors["fig_bg"])
        self.pie_ax = self.pie_figure.add_subplot(111)

        self.pie_canvas = FigureCanvasTkAgg(self.pie_figure, self.pie_frame)
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True)

        return page


    def change_period(self):
        periods = ["today", "daily", "weekly", "monthly", "yearly"]
        if self.period not in periods:
            self.period = "today"
        else:
            self.period = periods[(periods.index(self.period) + 1) % len(periods)]

        self.period_button.configure(text=self.period.title())
        self.update_report_graph()
        self.update_pie_chart()


    def _expense_rows_for_report(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return []

        rows = []
        for row in self.db.get_transactions(self.current_user.get_user_id()):
            if row[2] != "Expense":
                continue
            try:
                d = date.fromisoformat(row[6])
            except Exception:
                continue
            rows.append((d, row))
        return sorted(rows, key=lambda item: item[0])


    def _filtered_report_rows(self):
        today = date.today()
        rows = self._expense_rows_for_report()

        if self.period == "today":
            return [(d, row) for d, row in rows if d == today]
        if self.period == "daily":
            month_start = today.replace(day=1)
            return [(d, row) for d, row in rows if month_start <= d <= today]
        if self.period == "weekly":
            month_start = today.replace(day=1)
            return [(d, row) for d, row in rows if month_start <= d <= today]
        if self.period == "monthly":
            year_start = date(today.year, 1, 1)
            return [(d, row) for d, row in rows if year_start <= d <= today]
        if self.period == "yearly":
            return rows
        return rows


    def _report_series(self):
        rows = self._filtered_report_rows()
        totals = {}

        for d, row in rows:
            amount = row[3]
            if self.period == "today":
                key = row[4] or "Uncategorized"
            elif self.period == "daily":
                key = d.strftime("%b %d")
            elif self.period == "weekly":
                week_start = d - timedelta(days=d.weekday())
                week_end = week_start + timedelta(days=6)
                key = f"{week_start.strftime('%b %d')}-{week_end.strftime('%b %d')}"
            elif self.period == "monthly":
                key = d.strftime("%b %Y")
            else:
                key = d.strftime("%Y")
            totals[key] = totals.get(key, 0.0) + amount

        return list(totals.keys()), list(totals.values()), rows


    def update_report_graph(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return

        labels, values, rows = self._report_series()
        colors = self._graph_colors()
        self.ax.clear()
        self._style_axes(self.ax, self.figure, colors)

        total = sum(row[3] for _, row in rows)

        if values:
            x_positions = list(range(len(labels)))
            bars = self.ax.bar(x_positions, values, color=colors["bar"])
            self.ax.set_xticks(x_positions)
            self.ax.set_xticklabels(labels, rotation=30, ha="right")
            self.ax.set_ylabel("Total Expense (₱)")
            self.ax.set_xlabel({
                "today": "Categories today",
                "daily": "Dates in the current month",
                "weekly": "Weeks in the current month",
                "monthly": "Months in the current year",
                "yearly": "Years",
            }.get(self.period, "Period"))
            # horizontal gridlines behind the bars
            self.ax.yaxis.grid(True, color=colors["grid"], linestyle="--", linewidth=0.8, alpha=0.8)
            self.ax.set_axisbelow(True)
            # ₱ amount label on top of every bar
            for bar, val in zip(bars, values):
                self.ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"₱{val:,.0f}",
                    ha="center", va="bottom",
                    fontsize=9, fontweight="bold",
                    color=colors["text"]
                )
        else:
            self.ax.text(
                0.5, 0.5, "No expenses for this filter",
                ha="center", va="center",
                transform=self.ax.transAxes,
                color=colors["text"]
            )
            self.ax.set_xticks([])

        self.ax.set_title(f"{self.period.title()} Spending", color=colors["text"])

        # Total amount banner above the chart
        self.figure.suptitle(
            f"Total:  ₱{total:,.2f}",
            fontsize=14,
            fontweight="bold",
            color=colors["text"],
            y=0.98
        )

        self.figure.tight_layout(rect=(0, 0, 1, 0.94))
        self.canvas.draw()

        self.report_total.configure(
            text=f"Total Spending: ₱{total:,.2f}"
        )


    def update_pie_chart(self):
        if not hasattr(self, "pie_ax"):
            return

        colors = self._graph_colors()
        self.pie_ax.clear()
        self._style_axes(self.pie_ax, self.pie_figure, colors)

        # Use the same filtered rows as the bar chart — already respects self.period
        filtered_rows = self._filtered_report_rows()
        category_totals = {}
        for _, row in filtered_rows:
            category = row[4] or "Uncategorized"
            category_totals[category] = category_totals.get(category, 0.0) + row[3]

        labels = [cat for cat, amount in category_totals.items() if amount > 0]
        values = [amount for amount in category_totals.values() if amount > 0]
        total = sum(values)

        if values:
            def make_autopct(vals):
                def autopct(pct):
                    absolute = pct / 100.0 * sum(vals)
                    return f"₱{absolute:,.0f}\n({pct:.1f}%)"
                return autopct

            pie_result = self.pie_ax.pie(
                values,
                autopct=make_autopct(values),
                radius=1.0,
                pctdistance=0.75,
                startangle=90,
                textprops={"fontsize": 11, "color": colors["text"]}
            )
            wedges = pie_result[0]
            autotexts = pie_result[2] if len(pie_result) > 2 else []

            # Style the percentage labels inside slices
            for at in autotexts:
                at.set_fontsize(10)
                at.set_color(colors["text"])

            # Put category names in a legend to avoid any overlap
            self.pie_ax.legend(
                wedges,
                labels,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.12),
                ncol=min(len(labels), 4),
                fontsize=11,
                framealpha=0,
                labelcolor=colors["text"]
            )

            self.pie_ax.set_title(
                f"{self.period.title()} Expenses by Category",
                fontsize=14,
                pad=18,
                color=colors["text"]
            )
        else:
            self.pie_ax.text(
                0.5, 0.5, "No category data",
                ha="center", va="center",
                transform=self.pie_ax.transAxes,
                color=colors["text"]
            )

        # Total amount banner above the pie chart
        self.pie_figure.suptitle(
            f"Total:  ₱{total:,.2f}",
            fontsize=14,
            fontweight="bold",
            color=colors["text"],
            y=0.98
        )

        self.pie_figure.tight_layout(rect=(0, 0.08, 1, 0.94))
        self.pie_canvas.draw()

    # =====================
    # DELETE TRANSACTIONS
    # =====================


    def _first_over_budget_date(self, user_id, budget_type, period_key, limit):
        rows = sorted(
            self.db.get_transactions(user_id),
            key=lambda row: row[6] or ""
        )
        total = 0.0
        for row in rows:
            ttype, amount, dstr = row[2], row[3], row[6]
            if ttype != "Expense":
                continue
            try:
                tx_period = self.db.get_period_key(budget_type, dstr)
            except Exception:
                continue
            if tx_period != period_key:
                continue
            total += amount
            if total > limit:
                try:
                    return datetime.strptime(dstr, "%Y-%m-%d").date()
                except Exception:
                    return None
        return None


    def _streak_day_status(self, d, user_id, budget_type, limit):
        if not budget_type or limit <= 0:
            return "neutral", "No budget set"

        today = date.today()
        if d > today:
            return "neutral", "Future date"

        dstr = d.isoformat()
        period_key = self.db.get_period_key(budget_type, dstr)
        period_items = {
            item["period"]: item
            for item in self.db.get_streak_summary_for_user(user_id)["history"]
        }
        item = period_items.get(period_key)
        if not item:
            return "neutral", "No spending recorded"

        if item["status"] == "failed":
            over_date = self._first_over_budget_date(user_id, budget_type, period_key, limit)
            if budget_type == "daily" or d == over_date:
                return "failed_start", f"Streak ended: ₱{item['total']:,.2f} / ₱{limit:,.2f}"
            return "neutral", f"Budget was still under limit before {over_date}"

        current_period = self.db.get_period_key(budget_type, today.isoformat())
        if period_key == current_period:
            return "current", f"Current {budget_type} period: ₱{item['total']:,.2f} / ₱{limit:,.2f}"

        return "success", f"Successful {budget_type} period: ₱{item['total']:,.2f} / ₱{limit:,.2f}"


    def update_streak_calendar(self):
        if not hasattr(self, "calendar_grid") or not self.current_user or self.current_user.get_user_id() is None:
            return

        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        today = date.today()
        user_id = self.current_user.get_user_id()
        budget_type = self.current_budget_type or "weekly"
        budget_limit = float(self.current_budget_limit or self.total_limit or 0)
        visible_year = getattr(self, "calendar_visible_year", today.year)
        visible_month = getattr(self, "calendar_visible_month", today.month)
        month_name = calendar.month_name[visible_month]

        # Build daily expense totals for the visible month
        daily_totals = {}
        for row in self.db.get_transactions(user_id):
            if row[2] != "Expense":
                continue
            try:
                d = date.fromisoformat(row[6])
            except Exception:
                continue
            if d.year == visible_year and d.month == visible_month:
                daily_totals[d.isoformat()] = daily_totals.get(d.isoformat(), 0.0) + row[3]

        # Build a period_key → status map from streak history
        summary = self.db.get_streak_summary_for_user(user_id)
        period_status = {item["period"]: item["status"] for item in summary["history"]}
        current_period_key = self.db.get_period_key(budget_type, today.isoformat())

        self.calendar_month.configure(
            text=f"{month_name} {visible_year} | {budget_type.title()} Budget Streak"
        )

        legend = ctk.CTkFrame(self.calendar_grid, fg_color="transparent")
        legend.grid(row=0, column=0, columnspan=7, sticky="w", pady=(0, 8))
        for label, color in [
            ("Successful completed period", "#F59E0B"),
            ("Current / unfinished period", "#374151"),
            ("Failed / over budget period", "#6B7280"),
        ]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=(0, 14))
            swatch = ctk.CTkFrame(item, width=18, height=18, corner_radius=5, fg_color=color)
            swatch.pack(side="left", padx=(0, 5))
            swatch.pack_propagate(False)
            ctk.CTkLabel(item, text=label, font=("Segoe UI", 12)).pack(side="left")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            lbl = ctk.CTkLabel(
                self.calendar_grid,
                text=day,
                font=("Segoe UI", 18, "bold")
            )
            lbl.grid(row=1, column=col, padx=6, pady=6, sticky="nsew")

        cal = calendar.monthcalendar(visible_year, visible_month)

        # For monthly budget: compute whole-month status once
        month_color: str = "#374151"
        month_marker: str = ""
        if budget_type == "monthly":
            month_key_str = f"{visible_year}-{visible_month:02d}"
            month_status = period_status.get(month_key_str)
            if month_key_str == current_period_key:
                month_color = "#374151"   # current in-progress
                month_marker = ""
            elif month_status == "success":
                month_color = "#F59E0B"
                month_marker = "OK"
            elif month_status == "failed":
                month_color = "#6B7280"
                month_marker = "Ended"
            else:
                month_color = "#374151"
                month_marker = ""
        else:
            month_color = "#374151"
            month_marker = ""

        for row_i, week in enumerate(cal):
            # Default week vars (only used when budget_type == "weekly")
            week_color: str = "#374151"
            week_marker: str = ""

            # For weekly budget: compute this week's period status once per row
            if budget_type == "weekly":
                # Find first real day in this week
                first_day_num = next((d for d in week if d != 0), None)
                if first_day_num is not None:
                    week_d = date(visible_year, visible_month, first_day_num)
                    week_period_key = self.db.get_period_key("weekly", week_d.isoformat())
                    week_status = period_status.get(week_period_key)
                    if week_period_key == current_period_key:
                        week_color = "#374151"   # in-progress week
                        week_marker = ""
                    elif week_status == "success":
                        week_color = "#F59E0B"   # whole week succeeded → amber
                        week_marker = "OK"
                    elif week_status == "failed":
                        week_color = "#6B7280"   # whole week failed → gray
                        week_marker = "Ended"
                    else:
                        week_color = "#374151"
                        week_marker = ""
                else:
                    week_color = "#374151"
                    week_marker = ""

            for col_i, day_num in enumerate(week):
                if day_num == 0:
                    spacer = ctk.CTkFrame(self.calendar_grid, width=150, height=118, fg_color="transparent")
                    spacer.grid(row=row_i + 2, column=col_i, padx=8, pady=8, sticky="nsew")
                    continue

                d = date(visible_year, visible_month, day_num)
                daily_total = daily_totals.get(d.isoformat(), 0.0)

                # Defaults — overwritten by the branch below
                color: str = "#374151"
                marker: str = ""

                # Determine color and marker based on budget_type
                if budget_type == "daily":
                    day_period_key = self.db.get_period_key("daily", d.isoformat())
                    day_status = period_status.get(day_period_key)
                    if d > today:
                        color = "#374151"
                        marker = ""
                    elif day_period_key == current_period_key:
                        color = "#374151"
                        marker = ""
                    elif day_status == "success":
                        color = "#F59E0B"
                        marker = "OK"
                    elif day_status == "failed":
                        color = "#6B7280"
                        marker = "Ended"
                    else:
                        color = "#374151"
                        marker = ""
                elif budget_type == "weekly":
                    color = week_color
                    marker = week_marker
                elif budget_type == "monthly":
                    color = month_color
                    marker = month_marker
                else:
                    # yearly: treat whole year as one period
                    year_key_str = str(visible_year)
                    year_status = period_status.get(year_key_str)
                    if year_key_str == current_period_key:
                        color = "#374151"
                        marker = ""
                    elif year_status == "success":
                        color = "#F59E0B"
                        marker = "OK"
                    elif year_status == "failed":
                        color = "#6B7280"
                        marker = "Ended"
                    else:
                        color = "#374151"
                        marker = ""

                box = ctk.CTkFrame(
                    self.calendar_grid,
                    width=150,
                    height=118,
                    corner_radius=18,
                    fg_color=color
                )
                box.grid(row=row_i + 2, column=col_i, padx=8, pady=8, sticky="nsew")
                box.grid_propagate(False)

                ctk.CTkLabel(
                    box,
                    text=str(day_num),
                    font=("Segoe UI", 22, "bold")
                ).pack(pady=(10, 0))

                total_text = f"₱{daily_total:,.0f}" if daily_total > 0 else ""
                ctk.CTkLabel(
                    box,
                    text=total_text,
                    font=("Segoe UI", 13, "bold"),
                    text_color="white"
                ).pack(pady=(2, 0))

                ctk.CTkLabel(
                    box,
                    text=marker,
                    font=("Segoe UI", 11, "bold"),
                    text_color="white"
                ).pack(pady=(2, 0))

        for col in range(7):
            self.calendar_grid.grid_columnconfigure(col, weight=1, uniform="streak_calendar", minsize=155)
        for row in range(2, 8):
            self.calendar_grid.grid_rowconfigure(row, weight=1, minsize=122)

    # =====================
    # REPORT REFRESH
    # =====================


    def refresh_reports(self):
        self.update_report_graph()
        self.update_pie_chart()

    # =====================
    # GLOBAL REFRESH
    # =====================


    def export_report(self):
        if not self.current_user or self.current_user.get_user_id() is None:
            return
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )

            if not file_path:
                return

            rows = self.db.get_transactions(self.current_user.get_user_id())

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("MoneyTracker Report\n\n")
                for row in rows:
                    f.write(
                        f"{row[6]} | {row[2]} | {row[4]} | ₱{row[3]:,.2f} | {row[5]}\n"
                    )

        except Exception as e:
            print("Export Error:", e)