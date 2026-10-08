import pandas as pd

from data.analysis.statistics.statistic_pipeline import (run_statistical_analysis, evaluate_h1)


PATH = "data/analysis/processed/interactions_metrics.parquet"


def main() -> None:

    df = pd.read_parquet(PATH)

    results = run_statistical_analysis(df)

    print("\n=== ESTATÍSTICA DESCRITIVA ===")
    print(results["descriptive"].to_string(index=False))

    print("\n=== TESTE DE NORMALIDADE ===")
    print(results["normality"].to_string(index=False))

    print("\n=== COMPARAÇÃO ENTRE OS GRUPOS ===")
    print(results["comparison"].to_string(index=False))

    h1_supported = evaluate_h1(results["comparison"])

    print("\n=== AVALIAÇÃO DA H1 ===")

    if h1_supported:
        print(
            "H1: apoiada pelos resultados - o modo adaptativo apresentou desempenho "
            "significativamente superior ao modo base "
            "em pelo menos uma métrica após a correção de Holm."
        )
    else:
        print(
            "H1: não apoiada pelos resultados - não foi identificada diferença estatisticamente "
            "significativa favorável ao modo adaptativo "
            "em nenhuma métrica após a correção de Holm."
        )


if __name__ == "__main__":
    main()