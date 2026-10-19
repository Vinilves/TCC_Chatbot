import numpy as np
from scipy.stats import ttest_rel, wilcoxon


def _validate_paired_values(base_values, adaptive_values) -> tuple[np.ndarray, np.ndarray]:
    
    base_values = np.asarray(
        base_values,
        dtype=float,
    )

    adaptive_values = np.asarray(
        adaptive_values,
        dtype=float,
    )

    if len(base_values) != len(adaptive_values):
        raise ValueError(
            "Os grupos devem conter o mesmo número de observações."
        )

    if len(base_values) < 2:
        raise ValueError(
            "São necessários pelo menos dois pares."
        )

    if not np.all(np.isfinite(base_values)):
        raise ValueError(
            "O grupo base contém valores ausentes ou não finitos."
        )

    if not np.all(np.isfinite(adaptive_values)):
        raise ValueError(
            "O grupo adaptive contém valores ausentes ou não finitos."
        )

    return base_values, adaptive_values


def calculate_paired_t_test(base_values, adaptive_values) -> dict:
    
    base_values, adaptive_values = _validate_paired_values(
        base_values,
        adaptive_values,
    )

    differences = adaptive_values - base_values

    if np.allclose(differences, 0):
        return {
            "test": "Paired t-test",
            "statistic": 0.0,
            "p_value": 1.0,
        }

    statistic, p_value = ttest_rel(
        adaptive_values,
        base_values,
        alternative="two-sided",
    )

    return {
        "test": "Paired t-test",
        "statistic": float(statistic),
        "p_value": float(p_value),
    }


def calculate_wilcoxon_test(base_values, adaptive_values) -> dict:
    
    base_values, adaptive_values = _validate_paired_values(
        base_values,
        adaptive_values,
    )

    differences = adaptive_values - base_values

    if np.allclose(differences, 0):
        return {
            "test": "Wilcoxon signed-rank",
            "statistic": 0.0,
            "p_value": 1.0,
        }

    result = wilcoxon(
        differences,
        alternative="two-sided",
        zero_method="wilcox",
        method="auto",
    )

    return {
        "test": "Wilcoxon signed-rank",
        "statistic": float(result.statistic),
        "p_value": float(result.pvalue),
    }


def compare_paired_groups(base_values, adaptive_values, differences_normal: bool) -> dict:
    
    if differences_normal:
        return calculate_paired_t_test(
            base_values,
            adaptive_values,
        )

    return calculate_wilcoxon_test(
        base_values,
        adaptive_values,
    )