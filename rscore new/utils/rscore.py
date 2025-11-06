# utils/rscore.py

import pandas as pd

def compute_rscore(mark, group_avg, group_sd, idg=5, isg=5, c=5):
    if group_sd == 0:
        z = 0
    else:
        z = (mark - group_avg) / group_sd
    r = ((z * idg) + isg + c) * 5
    return round(r, 2)

def compute_overall_rscore(df: pd.DataFrame):
    """Weighted by credits."""
    if df.empty:
        return 0.0
    df = df.copy()
    if "credits" not in df.columns:
        df["credits"] = 1.0
    total_credits = df["credits"].sum()
    if total_credits == 0:
        return 0.0
    weighted = (df["rscore"] * df["credits"]).sum() / total_credits
    return round(weighted, 2)
