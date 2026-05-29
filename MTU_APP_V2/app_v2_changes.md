`reports_mixin.py` - added grid lines on the bar graph and changed the background theme. added an amount total indicator for each bar and slices. pie chart now uses a legend at the bottom instead of inline labels to prevent text overlap. pie chart figure size increased for better readability. bar graph total banner added above chart. pie chart autopct now shows ₱ amount and percentage per slice. graph colors adapt to light/dark theme.

`dashboard_mixin.py` - made the page longer, avoiding the lower boxes being cut-off. replaced the "Budget Status" textbox card on the overview page with a "Goal Status" card that shows each savings goal's name, saved/target amounts, percentage, and a mini progress bar. displays "No goals yet. Set one now →" if no goals exist.

`budget_mixin.py` - added the goal feature so that the user can enter amount of savings and also withdraw some from it, saving it all in a history. goals support: create goal, add savings, withdraw savings, view history, delete goal. streak display label updated to show "Current streak: X | Best: X" format. load_streak_history now also syncs the streak display label so the header and history box always match.

`navigation_mixin.py` - fixed refresh_everything to check for streak_history_box instead of the old goal_box attribute, so the Goals & Streaks page streak display and history now update correctly on every refresh.

`database.py` - profile picture path is saved to the database per user, so it persists across logout/login sessions. custom user categories are stored in user_categories table and are included in all graph and report queries.

`settings_mixin.py` - Add Category and Delete Category panels are now side by side in a two-column layout for a more compact categories page. Delete Category button is now styled red to distinguish it from Add. profile picture size slider added in settings.

`auth_mixin.py` - returning users who log in are no longer shown the budget setup popup, since they already configured it. the budget setup window now only appears for newly registered accounts (detected by the absence of a saved budget_type). the daily reminder prompt still appears for all users on login.

`mixin_base.py` - added class-level type annotations for all shared state attributes (total_limit, current_budget_limit, current_budget_type, current_streak_current, current_streak_best, current_streak_last_success, etc.) so Pylance resolves them correctly across all mixin subclasses. removed __getattr__ override which was causing false "attribute is unknown" errors in Pylance.

`settings_mixin.py` - profile picture is now saved to disk under profile_pics/ and the path is stored in the database, so the image is restored automatically when the user logs back in after signing out.

`settings_mixin.py / database.py` - when the user adds a custom category, it is stored in the user_categories table and is immediately reflected in the Reports graphs and Summary progress bars, not just the category dropdown.