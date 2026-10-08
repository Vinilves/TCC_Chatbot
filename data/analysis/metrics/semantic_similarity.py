from bert_score import score


def calculate_bertscore(candidates: list[str], references: list[str], batch_size: int = 16) -> list[float]:

    if len(candidates) != len(references):
        raise ValueError(
            "A quantidade de candidatos deve ser igual à quantidade de referências."
        )

    if not candidates:
        return []

    _, _, f1 = score(
        candidates,
        references,
        lang="pt",
        verbose=False,
        batch_size=batch_size,
    )

    return f1.cpu().tolist()