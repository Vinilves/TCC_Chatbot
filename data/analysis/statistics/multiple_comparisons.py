import pandas as pd
from statsmodels.stats.multitest import multipletests


def apply_holm_correction(comparison: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:

    comparison = comparison.copy()

    if comparison.empty:
        return comparison

    if "p_value" not in comparison.columns:
        raise ValueError(
            "A tabela de comparação precisa conter p_value."
        )

    valid_p_values = (
        comparison["p_value"].notna()
        & comparison["p_value"].between(0, 1)
    )

    comparison["p_value_adjusted"] = float("nan")
    comparison["significant_adjusted"] = pd.Series(
        pd.NA,
        index=comparison.index,
        dtype="boolean",
    )

    if not valid_p_values.any():
        return comparison

    reject, adjusted_p_values, _, _ = multipletests(
        comparison.loc[valid_p_values, "p_value"],
        alpha=alpha,
        method="holm",
    )

    comparison.loc[
        valid_p_values,
        "p_value_adjusted",
    ] = adjusted_p_values

    comparison.loc[
        valid_p_values,
        "significant_adjusted",
    ] = reject

    return comparison