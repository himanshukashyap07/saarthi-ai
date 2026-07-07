from app.db.models import Goal


def goal_to_dict(goal: Goal) -> dict:
    funded_pct = 0.0 if goal.target_amount <= 0 else min(goal.current_amount / goal.target_amount * 100, 100)

    expected_pct = 0.0
    if goal.target_years > 0:
        expected_pct = min(goal.years_elapsed / goal.target_years, 1.0) * 100
    # within 10 percentage points of the time-linear expectation counts as "on track"
    on_track = funded_pct >= expected_pct - 10

    return {
        "id": goal.id,
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_years": goal.target_years,
        "years_elapsed": goal.years_elapsed,
        "monthly_contribution": goal.monthly_contribution,
        "funded_pct": round(funded_pct, 1),
        "on_track": on_track,
    }
