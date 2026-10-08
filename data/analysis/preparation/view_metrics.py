import pandas as pd


PATH = "data/analysis/processed/interactions_metrics.parquet"


def main() -> None:
    df = pd.read_parquet(PATH)

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    print("\n=== MÉTRICAS ===")
    print(
        df[
            [
                "mode",
                "question",
                "answer",
                "bertscore_f1",
                "ttr",
                "distinct_2",
                "distinct_3",
                "embedding_cosine",
            ]
        ].to_string(index=False)
    )

    print("\n=== MÉDIAS POR MODO ===")
    print(
        df.groupby("mode")[
            [
                "bertscore_f1",
                "ttr",
                "distinct_2",
                "distinct_3",
                "embedding_cosine",
            ]
        ]
        .mean()
        .round(4)
    )


if __name__ == "__main__":
    main()