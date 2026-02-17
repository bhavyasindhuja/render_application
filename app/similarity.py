import streamlit as st
import pandas as pd

# =================================================
# RECOMMENDATION LOGIC (from similarity.py)
# =================================================
def recommend_posts(user_id, top_n=10):
    user_id = str(user_id)

    # Load datasets
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

    # -------- NEW USER --------
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

    # -------- EXISTING USER --------
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


# =================================================
# STREAMLIT UI (from streamlit_app.py)
# =================================================
st.set_page_config(page_title="Personalized Feed", layout="centered")

# ----------------- Custom CSS -----------------
st.markdown("""
<style>
.stContainer {
    background: #ffffff90;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 10px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
}
h1 {
    color: #4B0082;
    text-align: center;
}
.stButton>button {
    background: linear-gradient(to right, #ff7e5f, #feb47b);
    color: white;
    font-weight: bold;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------- App Title -----------------
st.title("📱 Personalized Feed Recommendation System")

# ----------------- User Input -----------------
user_id = st.text_input("Enter User ID")

# ----------------- Get Recommendations -----------------
if st.button("Get Recommendations"):
    results = recommend_posts(user_id)

    if results:
        st.success(f"Showing Top {len(results)} Recommendations for {user_id}")

        for post in results:
            with st.container():
                st.markdown(f"""
                <div class="stContainer">
                    <h3>📌 Post ID: {post['post_id']}</h3>
                    <p>🏷 <b>Topic:</b> {post['topic']}</p>
                    <p>🎬 <b>Content Type:</b> {post['content_type']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.divider()
    else:
        st.error("No recommendations found.")
