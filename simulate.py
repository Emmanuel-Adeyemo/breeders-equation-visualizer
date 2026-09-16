# houses the maths logic
from scipy import stats
import numpy as np


def _validate_proportion(p):
    if 0 < p > 1:
        raise ValueError('Proportion selected must be between 0 and 1.')


def calc_truncation_point(mu, sd_p, p):
    # pheno value above which inds are selected
    # mu is pop mean, sd_p is the pheno standard dev, p is the proportion selected

    _validate_proportion(p)
    z_score = stats.norm.ppf(1.0 - p)
    trunc_point = mu + (sd_p * z_score)

    return trunc_point


def selection_intensity(p):
    # standardized selection differential, i = z_score / p
    # p is proportion selected
    # i = pdf(z)/p
    _validate_proportion(p)
    z_score = stats.norm.ppf(1.0 - p)
    i = stats.norm.pdf(z_score)/p

    return i

def selection_differential(sd_p, p):
    # S in original phenotypic units
    i = selection_intensity(p)
    return i * sd_p

def calculate_response(h2, sd_p, p):
    # breeders equation
    # h2 is narrow sense heritability, sd_p is phenotypic standard deviation, p is proportion selected
    i = selection_intensity(p)
    response = i * h2 * sd_p

    return response

def get_curve_params(mu_orig, sd_p, R, n_pts=500):
    # mu_orig is the mean of original pop, sd_p is the phenotypic standard deviation
    # R is response to selection, n_pts is num of point for plot rendering - def = 500
    # response = calculate_response(h2, sd_p, p)
    mu_child = mu_orig + R

    x_min = min(mu_orig, mu_child) - 4 * sd_p
    x_max = max(mu_orig, mu_child) + 4*sd_p
    x = np.linspace(x_min, x_max, n_pts)

    # height of curve
    y_orig = stats.norm.pdf(x, loc=mu_orig, scale=sd_p)
    y_child = stats.norm.pdf(x, loc=mu_child, scale=sd_p)

    res = {
        'x': x,
        'y_orig': y_orig,
        'y_child': y_child,
        'mu_child': mu_child
    }

    return res

def run_generations(mu0, sd_p0, h2, p, n_gen, shrink_variance=False, shrink_factor=0.98, shrink_mode='fixed'):
    """
    Iterate breeders equation across generations
    :param mu0: starting pop mean
    :param sd_p0: starting phenotypic standard deviation
    :param h2: narrow sense (constant across gens).
    :param p: prop selected in each gens (constant across gens)
    :param n_gen: num of gens to simulate
    :param shrink_variance: if True, sd_p is multiplied by shrink_factor for each gen.
    idea is just to show loss of Vg under sustained selection (not a formal model)
    :return: dict of lists [gens], [mus], [sd_ps], [Ss], [Rs]
    """
    mu = mu0
    sd_p = sd_p0
    i_val = selection_intensity(p)

    generations = [0]
    mus = [mu]
    sds = [sd_p]
    S_list = [np.nan]
    R_list = [np.nan]

    for gen in range(1, n_gen + 1):
        S = selection_differential(sd_p, p)
        R = calculate_response(h2, sd_p, p)

        mu = mu + R
        if shrink_variance:
            if shrink_variance:
                if shrink_mode == "intensity":
                    decay = max(0.0, 1.0 - shrink_factor * i_val)
                    sd_p = sd_p * decay
                else:
                    sd_p = sd_p * shrink_factor
                sd_p = max(sd_p, 1e-6)  # guard against collapsing to zero/negative

        generations.append(gen)
        mus.append(mu)
        sds.append(sd_p)
        S_list.append(S)
        R_list.append(R)

    return {
        'generation': generations,
        'mu': mus,
        'sd': sds,
        'S': S_list,
        'R': R_list
    }


# for realized heritability
def simulate_realized_heritability(true_h2, sd_p, p, n_offspring, n_reps=1, rng=None):
    """
    Simulate single gen selection experiment for realized h2 estimation ie realized h2 = R_hat/S_hat.
    models sampling noise breeders would face given finite nos of elected parents and offspring so S and R would be estimated from
    finite samples rather than that known exactly.
    :param true_h2: true population level h2 used to generate data
    :param sd_p: standard deviation of base pop
    :param p: proportion selected
    :param n_offspring: no of offspring phenos measured in the sim experiment - this drives how noisy R estimate will be
    eg small no of offsprings = noisier R_hat
    :param n_reps: no of times to repeat the experiment
    :param rng: seed
    :return: dict with S_true, T_true (ie from breeders eq), S_hat, R_hat, h2_hat (len = n_reps)
    """

    if rng is None:
        rng = np.random.default_rng()

    if not (0 <= true_h2 <= 1):
        raise ValueError('Heritability must be between 0 and 1.')
    if n_offspring < 2:
        raise ValueError('Offspring must be at least 2 to estimate mean')

    mu0 = 0.0 # deviation
    trunc = calc_truncation_point(mu0, sd_p, p)
    S_true = selection_differential(sd_p, p)
    R_true = calculate_response(true_h2, sd_p, p)

    sd_offspring = sd_p # assumed same as parental

    S_hat = np.empty(n_reps)
    R_hat = np.empty(n_reps)
    h2_hat = np.empty(n_reps)

    for rep in range(n_reps):

        selected = []

        max_draws = max(20 * n_offspring, 2000)
        draws = 0
        while len(selected) < n_offspring and draws < max_draws:
            batch = rng.normal(mu0, sd_p, size=n_offspring *4)
            selected.extend(batch[batch >= trunc].tolist())
            draws += len(batch)
        selected = np.array(selected[:n_offspring])
        if len(selected) < 2:
            # extreme p with bad luck, fall back to trunc mean
            selected = np.array([trunc, trunc])
        S_hat[rep] = selected.mean() - mu0

        offspring_sample = rng.normal(mu0 + R_true, sd_offspring, size=n_offspring)
        R_hat[rep] = offspring_sample.mean() - mu0

        h2_hat[rep] = R_hat[rep] / S_hat[rep] if S_hat[rep] != 0 else np.nan

    return {
        'S_true': S_true,
        'R_true': R_true,
        'S_hat': S_hat,
        'R_hat': R_hat,
        'h2_hat': h2_hat
    }






# print(get_curve_params(100, 0.5, 15, 0.1))

# print(calc_truncation_point(100, 15, 0.01))