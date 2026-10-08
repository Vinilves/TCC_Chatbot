from typing import Literal


Sentiment = Literal[
    "negative",
    "neutral",
    "positive"
]


NEGATIVE_PREFIX = (
    "Tudo bem ter dúvidas durante o aprendizado. Vamos entender isso com calma, passo a passo."
)

POSITIVE_PREFIX = (
    "Muito bem! Você está avançando na compreensão do assunto."
)


def adapt_answer(answer: str, sentiment: Sentiment) -> str:

    if sentiment == "negative":
        return f"{NEGATIVE_PREFIX} {answer}"

    if sentiment == "positive":
        return f"{POSITIVE_PREFIX} {answer}"

    return answer