import pandas as pd

from data.analysis.statistics.descriptive import calculate_descriptive_statistics
from data.analysis.statistics.multiple_comparisons import apply_holm_correction
from data.analysis.statistics.normality import calculate_shapiro_test
from data.analysis.statistics.comparison import compare_groups
from data.analysis.statistics.effect_size import (calculate_cohens_d, calculate_rank_biserial)


METRICS = [
    "bertscore_f1",
    "ttr",
    "distinct_2",
    "distinct_3",
    "embedding_cosine",
]


def run_statistical_analysis(df: pd.DataFrame, alpha: float = 0.05) -> dict:

    required_columns = [
        "session_id",
        "mode",
        *METRICS,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas ausentes: {missing_columns}"
        )

    session_modes = (
        df.groupby("session_id")["mode"]
        .nunique()
    )

    if (session_modes > 1).any():
        raise ValueError(
            "Foi encontrada pelo menos uma sessão associada a mais de um modo experimental."
        )

    df = (
        df
        .groupby(
            ["session_id", "mode"],
            as_index=False,
        )[METRICS]
        .mean()
    )

    descriptive = calculate_descriptive_statistics(
        df=df,
        metrics=METRICS,
    )

    normality = calculate_shapiro_test(
        df=df,
        metrics=METRICS,
    )

    comparison_results = []

    for metric in METRICS:

        base_values = (
            df.loc[
                df["mode"] == "base",
                metric,
            ]
            .dropna()
            .to_numpy()
        )

        adaptive_values = (
            df.loc[
                df["mode"] == "adaptive",
                metric,
            ]
            .dropna()
            .to_numpy()
        )

        if (len(base_values) < 3 or len(adaptive_values) < 3):
            continue

        normal_base = normality.loc[
            (normality["metric"] == metric)
            & (normality["mode"] == "base"),
            "normal",
        ].iloc[0]

        normal_adaptive = normality.loc[
            (normality["metric"] == metric)
            & (normality["mode"] == "adaptive"),
            "normal",
        ].iloc[0]

        if (pd.isna(normal_base) or pd.isna(normal_adaptive)):
            continue

        result = compare_groups(
            base_values=base_values,
            adaptive_values=adaptive_values,
            normal_base=normal_base,
            normal_adaptive=normal_adaptive,
        )

        if result["test"] == "Welch t-test":

            effect_size = calculate_cohens_d(
                base_values,
                adaptive_values,
            )

            effect_name = "cohens_d"

        else:

            effect_size = calculate_rank_biserial(
                base_values,
                adaptive_values,
            )

            effect_name = "rank_biserial"

        comparison_results.append({
            "metric": metric,
            "test": result["test"],
            "statistic": result["statistic"],
            "p_value": result["p_value"],
            "significant_uncorrected": (
                result["p_value"] < alpha
            ),
            "effect_size": effect_size,
            "effect_size_type": effect_name,
            "base_mean": base_values.mean(),
            "adaptive_mean": adaptive_values.mean(),
            "base_median": pd.Series(
                base_values
            ).median(),
            "adaptive_median": pd.Series(
                adaptive_values
            ).median(),
        })

    comparison = pd.DataFrame(
        comparison_results
    )

    comparison = apply_holm_correction(
        comparison=comparison,
        alpha=alpha,
    )

    return {
        "descriptive": descriptive,
        "normality": normality,
        "comparison": comparison,
    }


def evaluate_h1(comparison: pd.DataFrame) -> bool:

    if comparison.empty:
        return False

    evidence = comparison[
        (comparison["significant_adjusted"])
        & (
            comparison["adaptive_mean"]
            > comparison["base_mean"]
        )
    ]

    return not evidence.empty