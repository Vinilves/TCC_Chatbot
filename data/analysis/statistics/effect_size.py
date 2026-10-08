import numpy as np
from scipy.stats import mannwhitneyu


def calculate_cohens_d(base_values, adaptive_values) -> float:

    base_values = np.asarray(base_values, dtype=float)
    adaptive_values = np.asarray(adaptive_values, dtype=float)

    n_base = len(base_values)
    n_adaptive = len(adaptive_values)

    mean_base = np.mean(base_values)
    mean_adaptive = np.mean(adaptive_values)

    std_base = np.std(base_values, ddof=1)
    std_adaptive = np.std(adaptive_values, ddof=1)

    pooled_std = np.sqrt(
        ((n_base - 1) * std_base**2 + (n_adaptive - 1) * std_adaptive**2) / (n_base + n_adaptive - 2)
    )

    if pooled_std == 0:
        return np.nan

    return (mean_adaptive - mean_base) / pooled_std


def calculate_rank_biserial(base_values, adaptive_values) -> float:

    base_values = np.asarray(base_values, dtype=float)
    adaptive_values = np.asarray(adaptive_values, dtype=float)

    n_base = len(base_values)
    n_adaptive = len(adaptive_values)

    u_statistic, _ = mannwhitneyu(
        adaptive_values,
        base_values,
        alternative="two-sided",
    )

    return ((2 * u_statistic) / (n_adaptive * n_base)) - 1