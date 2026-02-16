from fastapi import FastAPI
from app.similarity import recommend_posts

app = FastAPI()

# -------------------- Home Route --------------------
@app.get("/")
def home():
    return {"message": "Social Feed Recommendation API is running"}

# -------------------- Recommendation Route --------------------
@app.get("/feed/{user_id}")
def get_feed(user_id: int):
    try:
        recommended = recommend_posts(user_id)

        return {
            "status": "success",
            "user_id": user_id,
            "recommended_posts": recommended
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }