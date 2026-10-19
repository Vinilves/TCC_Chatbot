from pathlib import Path

import pandas as pd

from data.analysis.statistics.statistic_pipeline import run_statistical_analysis


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INTERACTIONS_PATH = PROJECT_ROOT / "data" / "analysis" / "processed" / "interactions_metrics.parquet"

OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis" / "statistics" / "results"

ALPHA = 0.05


def main() -> None:
    
    if not INTERACTIONS_PATH.exists():
        raise FileNotFoundError(
            "Arquivo Parquet não encontrado: "
            f"{INTERACTIONS_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    interactions_df = pd.read_parquet(
        INTERACTIONS_PATH
    )

    print(
        f"Registros carregados: {len(interactions_df):,}"
    )

    results = run_statistical_analysis(
        interactions_df=interactions_df,
        alpha=ALPHA,
    )

    output_files = {
        "session_metrics": "session_metrics.csv",
        "paired_data": "paired_data.csv",
        "diagnostics": "diagnostics.csv",
        "descriptive": "descriptive.csv",
        "normality": "normality.csv",
        "comparison": "comparison.csv",
    }

    for result_key, filename in output_files.items():
        output_path = OUTPUT_DIR / filename

        results[result_key].to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"Arquivo salvo: {output_path}")

    print("\n=== Diagnóstico da amostra ===")
    print(
        results["diagnostics"].to_string(index=False)
    )

    print("\n=== Estatísticas descritivas ===")
    print(
        results["descriptive"].to_string(index=False)
    )

    print("\n=== Testes de normalidade ===")
    print(
        results["normality"].to_string(index=False)
    )

    print("\n=== Comparação entre os modos ===")
    print(
        results["comparison"].to_string(index=False)
    )

    print("\nAnálise estatística concluída.")


if __name__ == "__main__":
    main()