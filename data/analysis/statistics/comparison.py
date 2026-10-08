from scipy.stats import ttest_ind, mannwhitneyu


def calculate_welch_t_test(base_values, adaptive_values) -> dict:

    statistic, p_value = ttest_ind(base_values, adaptive_values, equal_var=False, alternative="two-sided")

    return {
        "test": "Welch t-test",
        "statistic": statistic,
        "p_value": p_value,
    }

def calculate_mann_whitney_test(base_values, adaptive_values) -> dict:

    statistic, p_value = mannwhitneyu(base_values, adaptive_values, alternative="two-sided")

    return {
        "test": "Mann-Whitney U",
        "statistic": statistic,
        "p_value": p_value,
    }

def compare_groups(base_values, adaptive_values, normal_base: bool, normal_adaptive: bool) -> dict:

    if normal_base and normal_adaptive:

        result = calculate_welch_t_test(base_values, adaptive_values)

    else:

        result = calculate_mann_whitney_test(base_values, adaptive_values)

    return result