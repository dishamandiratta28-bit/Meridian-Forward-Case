"""Meridian Forward Session 5 calculation.

P-number references point to the original case. Q5.02-Q5.08 are teaching inputs
used for the four-week pilot calculation, not figures for the full workforce.
"""
import math

ROLES = [
    "Engineering",
    "Analytics",
    "Operations",
    "Data preparation",
    "Quality assurance",
    "Legacy experts",
]
PEOPLE = [20, 12, 8, 6, 6, 8]
LEGACY_H = [96, 80, 96, 96, 96, 112]
VOLUME = [120, 80, 60, 60, 80, 40]
H_UNIT = [4, 4, 3, 4, 3, 4]
COORD = {
    1: [160, 96, 64, 64, 48, 64],  # Retained approvals
    2: [80, 48, 32, 32, 24, 32],   # Bounded delegation
}
PRICE = [1000, 900, 600, 550, 800, 1000]
PRODUCTIVE = 160 * 0.8             # 128 usable hours per person (Q5.02)
VENDOR_EFF = PRODUCTIVE * 0.8      # 102.4 effective hours per vendor (Q5.07)
BUDGET = 600_000
MAX_VENDORS = 8


def run(workflow=2, include_duplicate=False, buy_legacy=False):
    """Return role-by-role demand, capacity, gap and vendor-cost estimates.

    Args:
        workflow: 1 for retained approvals, 2 for bounded delegation.
        include_duplicate: count the duplicate 60-pack data-preparation task.
        buy_legacy: permit a vendor for the legacy-expert gap as a fallback.
    """
    if workflow not in COORD:
        raise ValueError("workflow must be 1 (retained approvals) or 2 (bounded delegation)")

    rows = []
    for i, role in enumerate(ROLES):
        task_hours = VOLUME[i] * H_UNIT[i]
        if role == "Data preparation" and include_duplicate:
            task_hours += 60 * 4

        demand = task_hours + COORD[workflow][i]
        usable_supply = PEOPLE[i] * (PRODUCTIVE - LEGACY_H[i])
        assigned = min(demand, usable_supply)
        gap = max(0, demand - assigned)
        workers_needed = math.ceil(gap / VENDOR_EFF - 1e-9) if gap else 0
        workers = workers_needed if (role != "Legacy experts" or buy_legacy) else 0
        cost = workers * 160 * PRICE[i]
        positions = math.ceil((PEOPLE[i] * LEGACY_H[i] + demand) / PRODUCTIVE - 1e-9)
        unfilled = max(0, gap - workers * VENDOR_EFF)

        rows.append({
            "Role": role,
            "Demand": demand,
            "Usable": usable_supply,
            "Assigned": assigned,
            "Gap": gap,
            "Positions": positions,
            "Pool": PEOPLE[i],
            "Workers": workers,
            "Cost": cost,
            "Unfilled": unfilled,
        })
    return rows
