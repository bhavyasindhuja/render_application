import pandas as pd

def recommend_posts(user_id, top_n=10):
    user_id = str(user_id)

    # Load datasets INSIDE function (very important)
    users = pd.read_csv("data/users.csv")
    posts = pd.read_csv("data/posts.csv")
    interactions = pd.read_csv("data/interactions.csv")

    users["user_id"] = users["user_id"].astype(str)
    interactions["user_id"] = interactions["user_id"].astype(str)
    posts["post_id"] = posts["post_id"].astype(str)


    # Engagement Score
    interactions["engagement_score"] = (
        interactions["like_flag"] * 3 +
        interactions["comment_flag"] * 4 +
        interactions["share_flag"] * 5 +
        interactions["save_flag"] * 4 +
        interactions["watch_time"] * 0.1
    )

    # ------------------ NEW USER ------------------
    if user_id not in interactions["user_id"].values:
        top_posts = (
            interactions.groupby("post_id")["engagement_score"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        recommended_posts = posts[posts["post_id"].isin(top_posts)]
        return recommended_posts[["post_id", "topic", "content_type"]].to_dict("records")

    # ------------------ EXISTING USER ------------------
    user_data = interactions[interactions["user_id"] == user_id]

    user_interests = users[users["user_id"] == user_id]["interests"].values[0]
    interest_list = [i.strip() for i in user_interests.split(",")]

    merged = posts.merge(user_data, on="post_id", how="left")

    merged["topic_score"] = merged["topic"].apply(
        lambda x: 5 if x in interest_list else 0
    )

    merged["engagement_score"] = merged["engagement_score"].fillna(0)
    merged["final_score"] = merged["topic_score"] + merged["engagement_score"]

    seen_posts = user_data["post_id"].values
    merged = merged[~merged["post_id"].isin(seen_posts)]

    recommendations = merged.sort_values(
        by="final_score", ascending=False
    ).head(top_n)

    return recommendations[["post_id", "topic", "content_type"]].to_dict("records")