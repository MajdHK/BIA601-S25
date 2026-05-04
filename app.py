from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse   # ✅ أضف هذا
from pydantic import BaseModel
from typing import List
import uvicorn

from database import db
from recommender import run_recommender_ga

# نماذج البيانات
class OneProduct(BaseModel):
    product_id: int; category: str; price: float; score: float; rating: float

class ResponseBody(BaseModel):
    user_id: int; user_location: str; recommendations: List[OneProduct]

app = FastAPI(title="BIA601 Integrated System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/recommend", response_model=ResponseBody)
def recommend(user_id: int):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    results = run_recommender_ga(user_id)
    recs = []
    for pid, raw_sc in results:
        p = db.products_df[db.products_df["product_id"] == pid].iloc[0]
        recs.append(OneProduct(
            product_id=int(pid),
            category=str(p["category"]),
            price=float(p["price"]),
            score=round(min(raw_sc / 3.2, 1.0), 2),
            rating=round(float(db.avg_ratings.get(pid, 0.0)), 1)
        ))

    return ResponseBody(
        user_id=int(user["user_id"]),
        user_location=str(user.get("location", "Unknown")),
        recommendations=recs
    )


@app.get("/users")
def get_users():
    return {
        "users": db.users_df.head(20)[["user_id", "location", "age"]].to_dict(orient="records")
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
