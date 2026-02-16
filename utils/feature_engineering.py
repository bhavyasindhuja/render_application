import pandas as pd
import numpy as np
from datetime import datetime

def calculate_engagement_score(df):
    df["engagement_score"] = (
        df["like_flag"] * 2 +
        df["comment_flag"] * 3 +
        df["share_flag"] * 4 +
        df["save_flag"] * 5 +
        df["watch_time"] * 0.05
    )
    return df


def add_recency_score(posts_df):
    now = datetime.now()
    posts_df["publish_time"] = pd.to_datetime(posts_df["publish_time"])
    hours_diff = (now - posts_df["publish_time"]).dt.total_seconds() / 3600
    posts_df["recency_score"] = np.exp(-0.1 * hours_diff)
    return posts_df
