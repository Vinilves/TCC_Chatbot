import re

from src.preprocessing.normalizer import (normalize_for_comparison, remove_trailing_punctuation)


GREETING_MESSAGE = (
    "Olá estudante! Seja bem-vindo(a)."
    "Sou um chatbot voltado ao ensino de programação em Python e posso ajudá-lo com dúvidas sobre conceitos, instruções, funções, estruturas de dados e outros conteúdos da linguagem. "
    "Como posso ajudá-lo hoje?"
)

FAREWELL_MESSAGE = (
    "Foi um prazer ajudar. Bons estudos em Python!"
)

MODERATION_MESSAGE = (
    "Peço que mantenhamos uma comunicação respeitosa para que eu possa ajudá-lo."
)

EMPTY_MESSAGE = (
    "Digite uma pergunta relacionada à programação em Python para que eu possa ajudá-lo."
)


GREETINGS = {
    "oi",
    "ola",
    "bom dia",
    "boa tarde",
    "boa noite",
    "e ai",
    "eae",
    "eai",
    "ei",
    "opa",
    "hello",
    "hi",
}


FAREWELLS = {
    "tchau",
    "ate logo",
    "ate mais",
    "ate breve",
    "falou",
    "flw",
}


ACKNOWLEDGMENTS = {
    "obrigado",
    "obrigada",
    "valeu",
    "muito obrigado",
    "muito obrigada",
}


OFFENSIVE_WORDS = {
    "idiota",
    "burro",
    "imbecil",
    "otario",
    "babaca",
    "estupido",
    "ignorante",
    "inutil",
    "ridiculo",
    "palhaco",
    "retardado",

    "merda",
    "bosta",
    "porra",
    "caralho",
    "cacete",
    "droga",

    "fdp",
    "arrombado",
    "desgracado",
    "corno",
}


def is_isolated_message(message: str, word_set: set[str]) -> bool:

    message = remove_trailing_punctuation(message)

    return message in word_set


def contains_offensive_word(message: str) -> bool:

    words = re.findall(
        r"\w+",
        message
    )

    return any(
        word in OFFENSIVE_WORDS
        for word in words
    )


def is_greeting(message: str) -> bool:

    message = remove_trailing_punctuation(message)

    message = re.sub(
        r"[^\w\s]",
        " ",
        message
    )

    message = re.sub(
        r"\s+",
        " ",
        message
    ).strip()

    if message in GREETINGS:
        return True

    for greeting in GREETINGS:

        if message.startswith(greeting + " "):

            remaining = message[
                len(greeting):
            ].strip()

            remaining_words = set(
                remaining.split()
            )

            if remaining_words and remaining_words.issubset(
                {
                    "tudo",
                    "bem",
                    "como",
                    "vai",
                    "esta",
                    "voce",
                    "chatbot",
                    "amigo",
                }
            ):
                return True

    return False


def check_rules(text: str) -> tuple[bool, str | None]:

    message = normalize_for_comparison(text)

    if not message:
        return True, EMPTY_MESSAGE

    if contains_offensive_word(message):
        return True, MODERATION_MESSAGE

    if is_greeting(message):
        return True, GREETING_MESSAGE

    if is_isolated_message(message, GREETINGS):
        return True, GREETING_MESSAGE

    if is_isolated_message(message, FAREWELLS):
        return True, FAREWELL_MESSAGE

    if is_isolated_message(message, ACKNOWLEDGMENTS):
        return True, FAREWELL_MESSAGE

    return False, None