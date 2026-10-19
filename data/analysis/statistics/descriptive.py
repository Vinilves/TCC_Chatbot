import pandas as pd


def calculate_descriptive_statistics(paired_df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:

    results = []

    for metric in metrics:
        base_column = f"{metric}_base"
        adaptive_column = f"{metric}_adaptive"

        required_columns = {
            base_column,
            adaptive_column,
        }

        missing_columns = (
            required_columns - set(paired_df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"Colunas ausentes para {metric}: "
                f"{sorted(missing_columns)}"
            )

        valid_pairs = paired_df[
            [base_column, adaptive_column]
        ].dropna()

        for mode, column in [
            ("base", base_column),
            ("adaptive", adaptive_column)]:
            values = valid_pairs[column]

            results.append(
                {
                    "metric": metric,
                    "mode": mode,
                    "n": len(values),
                    "mean": (
                        values.mean()
                        if len(values) > 0
                        else float("nan")
                    ),
                    "std": (
                        values.std(ddof=1)
                        if len(values) > 1
                        else float("nan")
                    ),
                    "median": (
                        values.median()
                        if len(values) > 0
                        else float("nan")
                    ),
                    "min": (
                        values.min()
                        if len(values) > 0
                        else float("nan")
                    ),
                    "max": (
                        values.max()
                        if len(values) > 0
                        else float("nan")
                    ),
                }
            )

    return pd.DataFrame(results)