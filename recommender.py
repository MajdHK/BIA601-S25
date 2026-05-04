import random
from database import db
from scoring import build_user_scores, calculate_fitness
from genetic_ops import tournament_selection, crossover_op, mutate_op

# إعدادات ثابتة
POP_SIZE, GENE_COUNT, NUM_GENS, ELIT = 40, 10, 20, 2

def run_recommender_ga(uid):
    score_map = build_user_scores(uid)
    all_products = db.products_df["product_id"].unique().tolist()
    gsize = min(len(all_products), GENE_COUNT)
    if gsize == 0: return []

    pop = [random.sample(all_products, gsize) for _ in range(POP_SIZE)]

    for _ in range(NUM_GENS):
        fits = [calculate_fitness(ind, score_map) for ind in pop]
        sorted_idx = sorted(range(POP_SIZE), key=lambda i: fits[i], reverse=True)
        new_pop = [pop[sorted_idx[i]][:] for i in range(ELIT)]

        while len(new_pop) < POP_SIZE:
            p1 = tournament_selection(pop, fits)
            p2 = tournament_selection(pop, fits)
            kid = crossover_op(p1, p2)
            new_pop.append(mutate_op(kid))
        pop = new_pop

    final_fits = [calculate_fitness(ind, score_map) for ind in pop]
    best_chrom = pop[max(range(POP_SIZE), key=lambda i: final_fits[i])]
    return [(pid, score_map.get(pid, 0.0)) for pid in best_chrom]