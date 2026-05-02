////hi

import random
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn


POP_SIZE   = 40
GENE_COUNT = 10   
NUM_GENS   = 20
CR         = 0.8  
MR         = 0.2  
T_SIZE     = 3    
ELIT       = 2

DATA_PATH = "./data"



class OneProduct(BaseModel):
    product_id: int
    category: str
    price: float
    score: float
    rating: float

class ResponseBody(BaseModel):
    user_id: int
    user_location: str
    recommendations: List[OneProduct]



def load_all_data(path):
    try:
        u = pd.read_excel(f"{path}/users.xlsx")
        p = pd.read_excel(f"{path}/products.xlsx")
        b = pd.read_excel(f"{path}/behavior.xlsx")
        r = pd.read_excel(f"{path}/ratings.xlsx")
        
        for df in [u, p, b, r]:
            df.columns = [str(c).strip() for c in df.columns]
        return u, p, b, r
    except Exception as err:
        raise RuntimeError(f"data load error: {err}")

users_df, products_df, behavior_df, ratings_df = load_all_data(DATA_PATH)


avg_rat = ratings_df.groupby("product_id")["rating"].mean().to_dict()


def get_user_by_id(uid):
    res = users_df[users_df["user_id"] == uid]
    if res.empty:
        return None
    return res.iloc[0]



def build_scores(uid):
    scores = {}

    beh = behavior_df[behavior_df["user_id"] == uid]
    for _, row in beh.iterrows():
        pid = int(row["product_id"])
        val = (
            int(row.get("viewed",    0)) * 0.2
            + int(row.get("clicked",   0)) * 0.5
            + int(row.get("purchased", 0)) * 1.0
        )
        scores[pid] = scores.get(pid, 0.0) + val

    rat = ratings_df[ratings_df["user_id"] == uid]
    for _, row in rat.iterrows():
        pid = int(row["product_id"])
        r_val = (float(row.get("rating", 0)) / 5.0) * 1.5
        scores[pid] = scores.get(pid, 0.0) + r_val

    return scores



def fitness(chrom, score_map):
    if len(chrom) == 0:
        return 0.0
    total = 0.0
    for pid in chrom:
        total += score_map.get(pid, 0.0)
    
    return total / (len(chrom) * 3.2)



def tournament(pop, fits):
    idxs = random.sample(range(len(pop)), T_SIZE)
    best = max(idxs, key=lambda i: fits[i])
    return pop[best][:]



def crossover(p1, p2):
    if random.random() >= CR or len(p1) <= 1:
        return p1[:]
    pt = random.randint(1, len(p1) - 1)
    child = list(dict.fromkeys(p1[:pt] + p2[pt:]))
    all_pids = products_df["product_id"].tolist()
    
    while len(child) < len(p1):
        pick = random.choice(all_pids)
        if pick not in child:
            child.append(pick)
    return child[:len(p1)]



def mutate(chrom):
    if random.random() >= MR or len(chrom) < 2:
        return chrom
    c = chrom[:]
    i, j = random.sample(range(len(c)), 2)
    c[i], c[j] = c[j], c[i]
    return c



def run_ga(uid):
    score_map = build_scores(uid)

    all_products = products_df["product_id"].unique().tolist()
    gsize = min(len(all_products), GENE_COUNT)
    if gsize == 0:
        return []

    
    pop = [random.sample(all_products, gsize) for _ in range(POP_SIZE)]

    for gen in range(NUM_GENS):
        fits = [fitness(ind, score_map) for ind in pop]
        sorted_idx = sorted(range(POP_SIZE), key=lambda i: fits[i], reverse=True)

        new_pop = [pop[sorted_idx[i]][:] for i in range(ELIT)]

        while len(new_pop) < POP_SIZE:
            p1 = tournament(pop, fits)
            p2 = tournament(pop, fits)
            kid = crossover(p1, p2)
            kid = mutate(kid)
            new_pop.append(kid)

        pop = new_pop

    final_fits = [fitness(ind, score_map) for ind in pop]
    best_i = max(range(POP_SIZE), key=lambda i: final_fits[i])
    best_chrom = pop[best_i]

    return [(pid, score_map.get(pid, 0.0)) for pid in best_chrom]



app = FastAPI(title="BIA601 Recommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/recommend", response_model=ResponseBody)
def recommend(user_id: int):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"user {user_id} not found")

    results = run_ga(user_id)
    if not results:
        raise HTTPException(status_code=404, detail="no data for this user")

    recs = []
    for pid, raw_sc in results:
        prow = products_df[products_df["product_id"] == pid]
        if prow.empty:
            continue
        p = prow.iloc[0]
        norm = round(min(raw_sc / 3.2, 1.0), 2)
        recs.append(OneProduct(
            product_id = int(pid),
            category   = str(p["category"]),
            price      = float(p["price"]),
            score      = norm,
            rating     = round(float(avg_rat.get(pid, 0.0)), 1)
        ))

    return ResponseBody(
        user_id         = int(user["user_id"]),
        user_location   = str(user.get("location", "Unknown")),
        recommendations = recs
    )


@app.get("/users")
def get_users():
    data = users_df.head(20)[["user_id", "location", "age"]].to_dict(orient="records")
    return {"users": data}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

