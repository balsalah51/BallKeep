"""BK Value curve. One formula for every desk and the Discord bot.

Rank 1 is 12,000. The exponential used to be 0.0165, which crushed names
in the 40-80 band (a rank-80 starter was 12% of the 1.01). Halving that
rate and softening the rank-power keeps a real 1.01 premium while leaving
mid-board starters with trade juice.
"""
from __future__ import annotations

import math

BK_VALUE_PEAK = 12000
BK_VALUE_EXP = 0.0085
BK_VALUE_POW = 0.13
QB_1QB_MULT = 0.38

FORMULA = (
    f"value = round({BK_VALUE_PEAK} * exp(-{BK_VALUE_EXP} * (rank-1)) "
    f"/ rank**{BK_VALUE_POW})"
)
ALGORITHM = (
    f"{FORMULA}. 1QB multiplies QB value by {QB_1QB_MULT}. "
    "Picks map to equivalent ranks on that curve."
)


def bk_value(rank, qb_mult: float = 1.0) -> int:
    """Turn a 1-indexed list rank into Ball Keep trade value.

    Rank 1 is 12,000. Value falls on an exponential curve with a mild
    rank-power so the cliff from 1.01 to 1.02 is real, a late first sits
    near half the 1.01, and ranks 40-80 stay in the 5,300-3,500 band.
    """
    if not rank or rank < 1:
        return 0
    raw = BK_VALUE_PEAK * math.exp(-BK_VALUE_EXP * (rank - 1)) / (rank ** BK_VALUE_POW)
    return max(1, int(round(raw * qb_mult)))
