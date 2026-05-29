# MoneyTracker split layout

Run the app from this folder:

```bash
python3 main.py
```

- `app_before_mixin_split.py` is the file that contains the main gui before the split. THIS HOLDS THE OLDER VERSION OF THE GUI AS I EDITED THE MIXIN FILES.

Files:

- `main.py` starts the application.
- `app.py` contains the CustomTkinter UI.
- `database.py` contains database setup, queries, budget checks, and streak logic.
- `models.py` contains `User`, `Transaction`, `Expense`, and `Income`.
- `date_utils.py` contains date helper functions.
- `config.py` contains app theme setup and shared constants.

Files separated by pages:

- `mixin_base.py` the base code to run all 7 mixin files.
- `auth_mixin.py` focused on the sign in/up page.
- `budget_mixin.py` holds the budget page.
- `dashboard_mixin.py` focuses on. the overview page.
- `navigation_mixin.py` navigation has the page settings and side bar slider.
- `reports_mixin.py` all the graphs and analytics.
- `settings_mixin.py` have all the user editing settings.
- `transactions_mixin.py` handles the transaction inputs and appends it to the data file.