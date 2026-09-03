import re

from src.preprocessing.normalizer import normalize_for_comparison
from src.preprocessing.scope import extract_python_terms


GREETING_MESSAGE = (
    "Olá estudante! Seja bem-vindo(a). "
    "Sou um chatbot voltado ao ensino de programação em Python e posso ajudá-lo com dúvidas sobre conceitos, instruções, funções, estruturas de dados e outros conteúdos da linguagem. "
    "Como posso ajudá-lo hoje?"
)

FAREWELL_MESSAGE = (
    "Foi um prazer ajudar. Bons estudos em Python!"
)

MODERATION_MESSAGE = (
    "Peço que mantenhamos uma comunicação respeitosa para que eu possa ajudá-lo."
)

ACKNOWLEDGMENT_MESSAGE = (
    "Por nada! Estou à disposição para ajudar com suas dúvidas de Python."
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
    "sair",
    "encerrar",
    "finalizar",
}


ACKNOWLEDGMENT_TERMS = {
    "obrigado",
    "obrigada",
    "agradeco",
    "agradecer",
    "valeu",
    "brigado",
    "brigada",
}

ACKNOWLEDGMENT_EXPRESSIONS = {
    "muito obrigado",
    "muito obrigada",
    "pela ajuda",
    "pela explicacao",
    "pela resposta",
    "pela informacao",
    "pelo apoio",
    "pelo suporte",
    "pela assistencia",
    "pela orientacao",
}


CONVERSATIONAL_WORDS = {
    "tudo",
    "bem",
    "como",
    "vai",
    "esta",
    "voce",
    "chatbot",
    "amigo",
    "assistente",
    "por",
    "favor",
    "ajuda",
    "ajudar",
    "muito",
    "mesmo",
    "bastante",
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


def clean_message(message: str) -> str:

    message = normalize_for_comparison(message)

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

    return message


def tokenize(message: str) -> list[str]:

    return re.findall(
        r"\w+",
        message
    )


def contains_related_term(message: str, terms: set[str]) -> bool:

    words = set(tokenize(message))

    return bool(
        words.intersection(terms)
    )


def contains_expression(message: str, expressions: set[str]) -> bool:

    return any(
        expression in message
        for expression in expressions
    )


def is_isolated_message(message: str, word_set: set[str]) -> bool:

    message = clean_message(message)

    return message in word_set


def contains_offensive_word(message: str) -> bool:

    words = tokenize(message)

    return any(
        word in OFFENSIVE_WORDS
        for word in words
    )


def is_greeting(message: str) -> bool:

    message = clean_message(message)

    if not message:
        return False

    if message in GREETINGS:
        return True

    for greeting in GREETINGS:

        if message.startswith(greeting + " "):

            remaining = message[
                len(greeting):
            ].strip()

            if not remaining:
                return True

            remaining_words = set(
                remaining.split()
            )

            if remaining_words.issubset(
                CONVERSATIONAL_WORDS):
                return True

    return False


def is_farewell(message: str) -> bool:

    message = clean_message(message)

    if not message:
        return False

    if message in FAREWELLS:
        return True

    words = set(
        message.split()
    )

    for farewell in FAREWELLS:

        farewell_words = set(
            farewell.split()
        )

        if farewell_words.issubset(words):

            remaining_words = (words - farewell_words)

            if remaining_words.issubset(CONVERSATIONAL_WORDS):
                return True

    return False


def is_acknowledgment(message: str) -> bool:

    message = clean_message(message)

    if not message:
        return False

    if not contains_related_term(message, ACKNOWLEDGMENT_TERMS):
        return False

    python_terms = extract_python_terms(message)

    if python_terms:
        return False

    words = set(
        message.split()
    )

    acknowledgment_words = (words.intersection(ACKNOWLEDGMENT_TERMS))

    remaining_words = (words - acknowledgment_words)

    if remaining_words.issubset(CONVERSATIONAL_WORDS):
        return True

    if contains_expression(message, ACKNOWLEDGMENT_EXPRESSIONS):
        return True

    return False


def check_rules(text: str) -> tuple[bool, str | None]:

    message = clean_message(text)

    if not message:
        return True, EMPTY_MESSAGE

    if contains_offensive_word(message):
        return True, MODERATION_MESSAGE

    if is_farewell(message):
        return True, FAREWELL_MESSAGE

    if is_acknowledgment(message):
        return True, ACKNOWLEDGMENT_MESSAGE

    if is_greeting(message):
        return True, GREETING_MESSAGE

    return False, None