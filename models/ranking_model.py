import pandas as pd
import numpy as np
from utils.feature_engineering import calculate_engagement_score, add_recency_score
from app.similarity import user_user_similarity


class FeedRankingModel:

    def __init__(self, interactions, posts):

        self.interactions = calculate_engagement_score(interactions)
        self.posts = add_recency_score(posts)

        self.similarity_df, self.user_post_matrix = user_user_similarity(self.interactions)


    def recommend_posts(self, user_id, top_n=5):

        if user_id not in self.user_post_matrix.index:
            return []

        # Similar users
        similar_users = self.similarity_df[user_id]

        # Weighted sum of engagement from similar users
        weighted_scores = np.dot(
            similar_users.values,
            self.user_post_matrix.values
        )

        scores_series = pd.Series(
            weighted_scores,
            index=self.user_post_matrix.columns
        )

        # Remove posts already interacted by user
        interacted_posts = self.interactions[
            self.interactions["user_id"] == user_id
        ]["post_id"]

        scores_series = scores_series.drop(interacted_posts, errors="ignore")

        # Add recency boost
        scores_series = scores_series.reset_index()
        scores_series.columns = ["post_id", "cf_score"]

        scores_series = scores_series.merge(
            self.posts[["post_id", "recency_score"]],
            on="post_id",
            how="left"
        )

        scores_series["final_score"] = (
            0.7 * scores_series["cf_score"] +
            0.3 * scores_series["recency_score"]
        )

        scores_series = scores_series.sort_values(
            by="final_score",
            ascending=False
        )

        return scores_series["post_id"].head(top_n).tolist()


