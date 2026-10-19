import warnings

import numpy as np
import pandas as pd
from scipy.stats import shapiro


def calculate_paired_normality(paired_df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:

    results = []

    for metric in metrics:
        base_column = f"{metric}_base"
        adaptive_column = f"{metric}_adaptive"

        missing_columns = {
            base_column,
            adaptive_column,
        } - set(paired_df.columns)

        if missing_columns:
            raise ValueError(
                f"Colunas ausentes para {metric}: "
                f"{sorted(missing_columns)}"
            )

        valid_pairs = paired_df[
            [base_column, adaptive_column]
        ].copy()

        valid_pairs = valid_pairs.replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        differences = (
            valid_pairs[adaptive_column]
            - valid_pairs[base_column]
        ).to_numpy(dtype=float)

        n = len(differences)

        result = {
            "metric": metric,
            "n_pairs": n,
            "statistic": np.nan,
            "p_value": np.nan,
            "normal": None,
            "status": None,
        }

        if n < 3:
            result["status"] = (
                "Não avaliado: menos de três pares."
            )
            results.append(result)
            continue

        if not np.all(np.isfinite(differences)):
            result["status"] = (
                "Não avaliado: diferenças não finitas."
            )
            results.append(result)
            continue

        if np.allclose(differences, differences[0]):
            result["status"] = (
                "Não avaliado: diferenças constantes."
            )
            results.append(result)
            continue

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                statistic, p_value = shapiro(
                    differences
                )

            result["statistic"] = float(statistic)
            result["p_value"] = float(p_value)
            result["normal"] = bool(p_value >= 0.05)
            result["status"] = "Avaliado"

        except (ValueError, FloatingPointError) as exc:
            result["status"] = (
                f"Erro no teste de normalidade: {exc}"
            )

        results.append(result)

    return pd.DataFrame(results)