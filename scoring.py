from database import db

def build_user_scores(uid):
    scores = {}
    # حساب درجة السلوك (Viewed, Clicked, Purchased)
    beh = db.behavior_df[db.behavior_df["user_id"] == uid]
    for _, row in beh.iterrows():
        pid = int(row["product_id"])
        val = (int(row.get("viewed", 0)) * 0.2 + 
               int(row.get("clicked", 0)) * 0.5 + 
               int(row.get("purchased", 0)) * 1.0)
        scores[pid] = scores.get(pid, 0.0) + val

    # إضافة درجات التقييم (Ratings)
    rat = db.ratings_df[db.ratings_df["user_id"] == uid]
    for _, row in rat.iterrows():
        pid = int(row["product_id"])
        r_val = (float(row.get("rating", 0)) / 5.0) * 1.5
        scores[pid] = scores.get(pid, 0.0) + r_val
    return scores

def calculate_fitness(chrom, score_map):
    if not chrom: return 0.0
    total = sum(score_map.get(pid, 0.0) for pid in chrom)
    return total / (len(chrom) * 3.2)