import pandas as pd


PATH = "data/analysis/processed/interactions_metrics.parquet"

METRIC_COLUMNS = [
    "bertscore_f1",
    "ttr",
    "distinct_2",
    "distinct_3",
    "embedding_cosine",
]


def main() -> None:
    df = pd.read_parquet(PATH)

    print("\n=== COLUNAS ===")
    print(df.columns.tolist())

    required_columns = {
        "session_id",
        "participant_id",
        "mode",
        "status",
        "question",
        "answer",
        "sentiment",
        *METRIC_COLUMNS,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Colunas esperadas ausentes no arquivo de métricas: "
            f"{sorted(missing_columns)}. "
            "Verifique preparation.py e execute run_analysis.py novamente."
        )

    print("\n=== AMOSTRA DAS INTERAÇÕES E MÉTRICAS ===")

    display_columns = [
        "participant_id",
        "session_id",
        "mode",
        "status",
        "question",
        "answer",
        *METRIC_COLUMNS,
    ]

    print(
        df[display_columns]
        .head(20)
        .to_string(index=False)
    )

    print("\n=== QUANTIDADE DE INTERAÇÕES POR MODO ===")

    print(
        df.groupby("mode", dropna=False)
        .size()
        .rename("interactions")
        .to_string()
    )

    print("\n=== QUANTIDADE DE SESSÕES POR MODO E STATUS ===")

    sessions = df[
        ["session_id", "participant_id", "mode", "status"]
    ].drop_duplicates()

    print(
        sessions.groupby(
            ["mode", "status"],
            dropna=False,
        )
        .agg(
            sessions=("session_id", "nunique"),
            participants=("participant_id", "nunique"),
        )
        .to_string()
    )

    print("\n=== MÉDIAS DAS MÉTRICAS POR MODO ===")

    print(
        df.groupby("mode", dropna=False)[METRIC_COLUMNS]
        .mean()
        .round(4)
        .to_string()
    )

    print("\n=== DISTRIBUIÇÃO DE VALÊNCIA EMOCIONAL NO MODO ADAPTATIVO ===")

    adaptive_sentiments = df.loc[
        df["mode"].eq("adaptive"),
        "sentiment",
    ]

    if adaptive_sentiments.empty:
        print("Nenhuma interação encontrada no modo adaptativo.")

    else:
        adaptive_sentiment = (
            adaptive_sentiments
            .fillna("não identificado")
            .value_counts()
            .rename_axis("Valência emocional")
            .rename("Quantidade de interações")
            .to_frame()
        )

        adaptive_sentiment["Percentual (%)"] = (
            adaptive_sentiment["Quantidade de interações"]
            / adaptive_sentiment["Quantidade de interações"].sum()
            * 100
        ).round(2)

        print(adaptive_sentiment.to_string())

    print(
        "\n=== PARTICIPANTES COM SESSÕES CONCLUÍDAS "
        "NOS DOIS MODOS ==="
    )

    completed_sessions = sessions.loc[
        sessions["status"].eq("completed")
        & sessions["participant_id"].notna()
        & sessions["mode"].isin(["base", "adaptive"])
    ]

    session_counts = (
        completed_sessions
        .groupby(["participant_id", "mode"])["session_id"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=["base", "adaptive"], fill_value=0)
    )

    valid_participants = session_counts.loc[
        session_counts["base"].eq(1)
        & session_counts["adaptive"].eq(1)
    ]

    print(
        f"Participantes com exatamente uma sessão concluída "
        f"em cada modo: {len(valid_participants)}"
    )

    print(
        "\nParticipantes sem o par completo ou com sessões "
        "duplicadas por modo:"
    )

    invalid_participants = session_counts.loc[
        ~(
            session_counts["base"].eq(1)
            & session_counts["adaptive"].eq(1)
        )
    ]

    print(invalid_participants.to_string())


if __name__ == "__main__":
    main()