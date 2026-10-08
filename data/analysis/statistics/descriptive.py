import pandas as pd


def calculate_descriptive_statistics(df: pd.DataFrame, metrics: list[str], mode_column: str = "mode") -> pd.DataFrame:

    required_columns = [mode_column, *metrics]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas ausentes no DataFrame: {missing_columns}"
        )

    results = []

    for metric in metrics:

        for mode in ["base", "adaptive"]:

            values = (
                df.loc[df[mode_column] == mode, metric]
                .dropna()
            )

            results.append({
                "metric": metric,
                "mode": mode,
                "n": len(values),
                "mean": values.mean(),
                "std": values.std(),
                "median": values.median(),
                "min": values.min(),
                "max": values.max(),
            })

    return pd.DataFrame(results)