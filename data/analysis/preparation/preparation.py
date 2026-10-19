import pandas as pd
import pyarrow.parquet as pq


def load_data_in_batches(interactions_path: str, batch_size: int = 500):
    
    parquet_file = pq.ParquetFile(interactions_path)

    for batch in parquet_file.iter_batches(batch_size=batch_size):
        yield batch.to_pandas()


def load_answers(answers_path: str) -> pd.DataFrame:
    return pd.read_parquet(answers_path)


def load_sessions(sessions_path: str) -> pd.DataFrame:
    return pd.read_parquet(sessions_path)


def normalize_id(series: pd.Series) -> pd.Series:
    
    normalized = series.astype("string").str.strip()

    normalized = normalized.str.replace(
        r"^(-?\d+)\.0+$",
        r"\1",
        regex=True,
    )

    normalized = normalized.replace("", pd.NA)

    return normalized


def prepare_data(interactions: pd.DataFrame, answers: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:

    interactions = interactions.copy()
    answers = answers.copy()
    sessions = sessions.copy()

    required_interaction_columns = {
        "session_id",
        "answer_id",
        "question",
        "answer",
    }

    required_session_columns = {
        "session_id",
        "participant_id",
        "mode",
        "status",
    }

    required_answer_columns = {
        "id",
        "answer",
    }

    missing_interaction_columns = (
        required_interaction_columns - set(interactions.columns)
    )

    missing_session_columns = (
        required_session_columns - set(sessions.columns)
    )

    missing_answer_columns = (
        required_answer_columns - set(answers.columns)
    )

    if missing_interaction_columns:
        raise ValueError(
            "Colunas ausentes na tabela de interações: "
            f"{sorted(missing_interaction_columns)}"
        )

    if missing_session_columns:
        raise ValueError(
            "Colunas ausentes na tabela de sessões: "
            f"{sorted(missing_session_columns)}"
        )

    if missing_answer_columns:
        raise ValueError(
            "Colunas ausentes na tabela de respostas: "
            f"{sorted(missing_answer_columns)}"
        )

    interactions["session_id"] = (
        interactions["session_id"].astype("string").str.strip()
    )

    sessions["session_id"] = (
        sessions["session_id"].astype("string").str.strip()
    )

    interactions["answer_id"] = normalize_id(
        interactions["answer_id"]
    )

    answers["id"] = normalize_id(
        answers["id"]
    )


    if interactions["session_id"].isna().any():
        raise ValueError(
            "Existem interações com session_id ausente."
        )

    if sessions["session_id"].isna().any():
        raise ValueError(
            "Existem sessões com session_id ausente."
        )

    if sessions["session_id"].duplicated().any():
        raise ValueError(
            "A tabela de sessões contém session_id duplicados."
        )

    if answers["id"].isna().any():
        raise ValueError(
            "A tabela de respostas contém IDs ausentes."
        )

    if answers["id"].duplicated().any():
        raise ValueError(
            "A tabela de respostas contém IDs duplicados."
        )

    session_data = sessions[["session_id", "participant_id", "mode", "status"]]

    df = interactions.merge(
        session_data,
        on="session_id",
        how="left",
        validate="many_to_one",
        indicator="_session_merge",
    )

    unmatched_sessions = df["_session_merge"] != "both"

    if unmatched_sessions.any():
        missing_ids = (
            df.loc[unmatched_sessions, "session_id"]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Existem interações sem correspondência na tabela de sessões. "
            f"Quantidade: {int(unmatched_sessions.sum())}. "
            f"Exemplos de session_id: {missing_ids[:5]}"
        )

    df = df.drop(columns="_session_merge")

    reference_data = answers[["id", "answer"]].rename(
        columns={
            "id": "answer_id",
            "answer": "reference_answer",
        }
    )

    df = df.merge(
        reference_data,
        on="answer_id",
        how="left",
        validate="many_to_one",
        indicator="_answer_merge",
    )

    unmatched_answers = (
        df["answer_id"].notna()
        & (df["_answer_merge"] != "both")
    )

    if unmatched_answers.any():
        missing_ids = (
            df.loc[unmatched_answers, "answer_id"]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Existem answer_id preenchidos que não correspondem "
            "a registros da tabela de respostas. "
            f"Quantidade de interações: {int(unmatched_answers.sum())}. "
            f"Exemplos de answer_id: {missing_ids[:10]}"
        )

    df = df.drop(columns="_answer_merge")

    for column in ["question", "answer"]:
        invalid = (
            df[column].isna()
            | ~df[column].map(
                lambda value: isinstance(value, str)
            )
            | df[column].map(
                lambda value: (
                    isinstance(value, str) and not value.strip()
                )
            )
        )

        if invalid.any():
            raise ValueError(
                f"A coluna '{column}' contém "
                f"{int(invalid.sum())} valores nulos, inválidos ou vazios."
            )

    missing_references = int(df["reference_answer"].isna().sum())

    if missing_references:
        print(
            "Aviso: "
            f"{missing_references} interações não possuem resposta "
            "de referência. Elas serão mantidas no DataFrame; "
            "o BERTScore deverá ser calculado apenas para as "
            "interações com referência válida."
        )

    return df