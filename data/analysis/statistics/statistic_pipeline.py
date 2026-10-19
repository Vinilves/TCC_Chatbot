import numpy as np
import pandas as pd

from data.analysis.statistics.comparison import compare_paired_groups
from data.analysis.statistics.descriptive import calculate_descriptive_statistics
from data.analysis.statistics.effect_size import (calculate_paired_cohens_dz, calculate_paired_rank_biserial)
from data.analysis.statistics.multiple_comparisons import apply_holm_correction
from data.analysis.statistics.normality import calculate_paired_normality


METRICS = [
    "bertscore_f1",
    "ttr",
    "distinct_2",
    "distinct_3",
    "embedding_cosine",
]

VALID_MODES = {"base", "adaptive"}
VALID_STATUS = "completed"


def prepare_paired_data(interactions_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    required_columns = {
        "participant_id",
        "session_id",
        "mode",
        "status",
        *METRICS,
    }

    missing_columns = required_columns - set(interactions_df.columns)

    if missing_columns:
        raise ValueError(
            "O Parquet não contém todas as colunas necessárias: "
            f"{sorted(missing_columns)}. "
            "Verifique se participant_id e status foram incorporados "
            "aos dados processados."
        )

    if interactions_df.empty:
        raise ValueError(
            "O Parquet não contém registros para análise."
        )

    df = interactions_df.copy()


    for column in ["participant_id", "session_id", "mode", "status"]:
        df[column] = df[column].astype("string").str.strip()

    valid_ids = (
        df["participant_id"].notna()
        & df["session_id"].notna()
        & df["participant_id"].ne("")
        & df["session_id"].ne("")
    )

    metadata_columns = [
        "participant_id",
        "mode",
        "status",
    ]

    session_metadata_counts = (
        df.groupby("session_id", dropna=False)[metadata_columns]
        .nunique(dropna=False)
    )

    inconsistent_sessions = session_metadata_counts.index[
        session_metadata_counts.gt(1).any(axis=1)
    ]

    if len(inconsistent_sessions) > 0:
        examples = list(inconsistent_sessions[:10])

        raise ValueError(
            "Foram encontradas sessões com metadados inconsistentes. "
            "Cada session_id deve estar associado a um único "
            "participant_id, mode e status. "
            f"Exemplos: {examples}"
        )

    eligible_mask = (
        valid_ids
        & df["status"].eq(VALID_STATUS)
        & df["mode"].isin(VALID_MODES)
    )

    eligible_df = df.loc[eligible_mask].copy()

    if eligible_df.empty:
        raise ValueError(
            "Nenhuma sessão elegível foi encontrada. "
            "Verifique os valores de status, mode e os identificadores."
        )

    for metric in METRICS:
        eligible_df[metric] = pd.to_numeric(
            eligible_df[metric],
            errors="coerce",
        )

        eligible_df[metric] = eligible_df[metric].replace(
            [np.inf, -np.inf],
            np.nan,
        )

    session_metrics = (
        eligible_df.groupby(
            ["participant_id", "session_id", "mode"],
            as_index=False,
        )[METRICS]
        .mean()
    )

    session_counts = (
        session_metrics.groupby(
            ["participant_id", "mode"]
        )["session_id"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=["base", "adaptive"], fill_value=0)
    )

    complete_participants = session_counts.index[
        session_counts["base"].eq(1)
        & session_counts["adaptive"].eq(1)
    ]

    excluded_participants = session_counts.index[
        ~(
            session_counts["base"].eq(1)
            & session_counts["adaptive"].eq(1)
        )
    ]

    paired_sessions = session_metrics[
        session_metrics["participant_id"].isin(
            complete_participants
        )
    ].copy()

    if paired_sessions.empty:
        raise ValueError(
            "Nenhum participante possui exatamente uma sessão concluída no modo base e uma no modo adaptive. Verifique os metadados do Parquet."
        )

    paired_df = paired_sessions.pivot(
        index="participant_id",
        columns="mode",
        values=METRICS,
    )

    paired_df.columns = [
        f"{metric}_{mode}"
        for metric, mode in paired_df.columns
    ]

    paired_df = paired_df.reset_index()

    diagnostics = pd.DataFrame(
        [
            {
                "item": "registros_originais",
                "count": len(df),
            },
            {
                "item": "registros_elegiveis",
                "count": len(eligible_df),
            },
            {
                "item": "sessoes_elegiveis",
                "count": len(session_metrics),
            },
            {
                "item": "participantes_com_pareamento_valido",
                "count": len(complete_participants),
            },
            {
                "item": "participantes_excluidos_por_pareamento",
                "count": len(excluded_participants),
            },
            {
                "item": "sessoes_excluidas_por_status_modo_ou_id",
                "count": int((~eligible_mask).sum()),
            },
        ]
    )

    return session_metrics, paired_df, diagnostics


def run_statistical_analysis(interactions_df: pd.DataFrame, alpha: float = 0.05) -> dict[str, pd.DataFrame]:

    session_metrics, paired_df, diagnostics = prepare_paired_data(
        interactions_df
    )

    descriptive = calculate_descriptive_statistics(
        paired_df,
        METRICS,
    )

    normality = calculate_paired_normality(
        paired_df,
        METRICS,
    )

    normality_lookup = normality.set_index("metric")

    comparison_results = []

    for metric in METRICS:
        base_column = f"{metric}_base"
        adaptive_column = f"{metric}_adaptive"

        valid_pairs = paired_df[
            [base_column, adaptive_column]
        ].dropna()

        base_values = valid_pairs[base_column].to_numpy(dtype=float)
        adaptive_values = valid_pairs[adaptive_column].to_numpy(
            dtype=float
        )

        n_pairs = len(valid_pairs)

        result = {
            "metric": metric,
            "n_pairs": n_pairs,
            "base_mean": (
                float(np.mean(base_values))
                if n_pairs > 0
                else np.nan
            ),
            "adaptive_mean": (
                float(np.mean(adaptive_values))
                if n_pairs > 0
                else np.nan
            ),
            "mean_difference_adaptive_minus_base": (
                float(np.mean(adaptive_values - base_values))
                if n_pairs > 0
                else np.nan
            ),
            "test": None,
            "statistic": np.nan,
            "p_value": np.nan,
            "effect_size": np.nan,
            "effect_size_type": None,
            "normal_differences": None,
            "test_status": None,
        }

        if n_pairs < 3:
            result["test_status"] = (
                "Não testado: menos de três pares completos."
            )
            comparison_results.append(result)
            continue

        normal_row = normality_lookup.loc[metric]
        differences_normal = normal_row["normal"]

        if pd.isna(differences_normal):
            result["test_status"] = (
                "Não testado: normalidade das diferenças "
                "não pôde ser avaliada."
            )
            comparison_results.append(result)
            continue

        result["normal_differences"] = bool(differences_normal)

        test_result = compare_paired_groups(
            base_values,
            adaptive_values,
            differences_normal=bool(differences_normal),
        )

        result["test"] = test_result["test"]
        result["statistic"] = test_result["statistic"]
        result["p_value"] = test_result["p_value"]

        if test_result["test"] == "Paired t-test":
            result["effect_size"] = calculate_paired_cohens_dz(
                base_values,
                adaptive_values,
            )
            result["effect_size_type"] = "Cohen's dz"

        elif test_result["test"] == "Wilcoxon signed-rank":
            result["effect_size"] = calculate_paired_rank_biserial(
                base_values,
                adaptive_values,
            )
            result["effect_size_type"] = (
                "Rank-biserial correlation"
            )

        result["test_status"] = "Testado"

        comparison_results.append(result)

    comparison = pd.DataFrame(comparison_results)

    comparison = apply_holm_correction(
        comparison,
        alpha=alpha,
    )

    return {
        "session_metrics": session_metrics,
        "paired_data": paired_df,
        "diagnostics": diagnostics,
        "descriptive": descriptive,
        "normality": normality,
        "comparison": comparison,
    }


def evaluate_h1(comparison: pd.DataFrame, better_directions: dict[str, str] | None = None) -> dict:

    if better_directions is None:
        better_directions = {}

    required_columns = {
        "metric",
        "p_value_adjusted",
        "base_mean",
        "adaptive_mean",
    }

    missing = required_columns - set(comparison.columns)

    if missing:
        raise ValueError(
            f"Colunas ausentes para avaliar H1: {sorted(missing)}"
        )

    evaluable = comparison.dropna(
        subset=[
            "p_value_adjusted",
            "base_mean",
            "adaptive_mean",
        ]
    ).copy()

    if evaluable.empty:
        return {
            "conclusion": "inconclusive",
            "message": (
                "Não foi possível avaliar H1: "
                "não há comparações inferenciais válidas."
            ),
            "supporting_metrics": [],
        }

    supporting_metrics = []

    for _, row in evaluable.iterrows():
        metric = row["metric"]
        direction = better_directions.get(metric)

        if direction not in {"higher", "lower"}:
            continue

        if row["p_value_adjusted"] >= 0.05:
            continue

        if direction == "higher":
            favorable = (
                row["adaptive_mean"] > row["base_mean"]
            )
        else:
            favorable = (
                row["adaptive_mean"] < row["base_mean"]
            )

        if favorable:
            supporting_metrics.append(metric)

    if supporting_metrics:
        return {
            "conclusion": "supported",
            "message": (
                "Há evidência estatística favorável a H1 "
                "em pelo menos uma métrica com direção definida."
            ),
            "supporting_metrics": supporting_metrics,
        }

    return {
        "conclusion": "not_supported",
        "message": (
            "Não foi identificada evidência estatística favorável "
            "a H1 entre as métricas avaliáveis com direção definida. "
            "Isso não demonstra, por si só, que os modos sejam equivalentes."
        ),
        "supporting_metrics": [],
    }