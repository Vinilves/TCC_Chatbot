from bert_score import score


def calculate_bertscore(candidates: list[str], references: list[str], batch_size: int = 16) -> list[float]:

    if len(candidates) != len(references):
        raise ValueError(
            "A quantidade de candidatos deve ser igual à quantidade de referências."
        )

    if not candidates:
        return []

    for index, (candidate, reference) in enumerate(
        zip(candidates, references)):
        if not isinstance(candidate, str):
            raise TypeError(
                f"O candidato da posição {index} "
                "não é uma string."
            )

        if not isinstance(reference, str):
            raise TypeError(
                f"A referência da posição {index} "
                "não é uma string."
            )

        if not candidate.strip():
            raise ValueError(
                f"O candidato da posição {index} está vazio."
            )

        if not reference.strip():
            raise ValueError(
                f"A referência da posição {index} está vazia."
            )

    _, _, f1 = score(
        candidates,
        references,
        lang="pt",
        verbose=False,
        batch_size=batch_size,
    )

    return f1.cpu().tolist()