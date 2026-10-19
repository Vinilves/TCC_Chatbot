import numpy as np
from scipy.stats import rankdata


def calculate_paired_cohens_dz(base_values, adaptive_values) -> float:

    base_values = np.asarray(base_values, dtype=float)
    adaptive_values = np.asarray(adaptive_values, dtype=float)

    differences = adaptive_values - base_values

    if len(differences) < 2:
        return np.nan

    std_difference = np.std(
        differences,
        ddof=1,
    )

    if np.isclose(std_difference, 0):
        return np.nan

    return float(
        np.mean(differences) / std_difference
    )


def calculate_paired_rank_biserial(base_values, adaptive_values) -> float:

    base_values = np.asarray(base_values, dtype=float)
    adaptive_values = np.asarray(adaptive_values, dtype=float)

    differences = adaptive_values - base_values

    differences = differences[
        ~np.isclose(differences, 0)
    ]

    if len(differences) == 0:
        return np.nan

    ranks = rankdata(
        np.abs(differences),
        method="average",
    )

    positive_rank_sum = ranks[
        differences > 0
    ].sum()

    negative_rank_sum = ranks[
        differences < 0
    ].sum()

    total_rank_sum = (
        positive_rank_sum + negative_rank_sum
    )

    if total_rank_sum == 0:
        return np.nan

    return float(
        (positive_rank_sum - negative_rank_sum) / total_rank_sum
    )