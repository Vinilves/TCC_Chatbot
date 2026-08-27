import re
import unicodedata


def normalize(text: str) -> str:

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


def normalize_for_comparison(text: str) -> str:

    text = normalize(text)

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )

    return text


def remove_trailing_punctuation(text: str) -> str:

    return re.sub(
        r"[!?.,;:]+$",
        "",
        text
    ).strip()