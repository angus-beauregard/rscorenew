# utils/course_data.py

import pandas as pd
import os

def load_course_credits(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame(columns=["course_name", "credits"])
    df = pd.read_csv(path)
    # normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    return df
