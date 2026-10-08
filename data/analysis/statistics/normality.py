import pandas as pd
from scipy.stats import shapiro


def calculate_shapiro_test(df: pd.DataFrame, metrics: list[str], mode_column: str = "mode") -> pd.DataFrame:

    results = []

    for metric in metrics:

        for mode in ["base", "adaptive"]:

            values = (
                df.loc[df[mode_column] == mode, metric]
                .dropna()
            )

            n = len(values)

            if n < 3:
                results.append({
                    "metric": metric,
                    "mode": mode,
                    "n": n,
                    "shapiro_statistic": None,
                    "shapiro_p_value": None,
                    "normal": None,
                })
                continue

            statistic, p_value = shapiro(values)

            results.append({
                "metric": metric,
                "mode": mode,
                "n": n,
                "shapiro_statistic": statistic,
                "shapiro_p_value": p_value,
                "normal": p_value >= 0.05,
            })

    return pd.DataFrame(results)