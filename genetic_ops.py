import random
from database import db

def tournament_selection(pop, fits, t_size=3):
    idxs = random.sample(range(len(pop)), t_size)
    best = max(idxs, key=lambda i: fits[i])
    return pop[best][:]

def crossover_op(p1, p2, cr=0.8):
    if random.random() >= cr or len(p1) <= 1:
        return p1[:]
    pt = random.randint(1, len(p1) - 1)
    child = list(dict.fromkeys(p1[:pt] + p2[pt:]))
    all_pids = db.products_df["product_id"].tolist()
    while len(child) < len(p1):
        pick = random.choice(all_pids)
        if pick not in child: child.append(pick)
    return child[:len(p1)]

def mutate_op(chrom, mr=0.2):
    if random.random() >= mr or len(chrom) < 2:
        return chrom
    c = chrom[:]
    i, j = random.sample(range(len(c)), 2)
    c[i], c[j] = c[j], c[i]
    return c