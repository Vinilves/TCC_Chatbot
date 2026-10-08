import pandas as pd
from statsmodels.stats.multitest import multipletests


def apply_holm_correction(comparison: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:

    comparison = comparison.copy()

    if comparison.empty:
        return comparison

    adjusted = multipletests(
        comparison["p_value"],
        alpha=alpha,
        method="holm",
    )

    comparison["p_value_adjusted"] = adjusted[1]
    comparison["significant_adjusted"] = adjusted[0]

    return comparison