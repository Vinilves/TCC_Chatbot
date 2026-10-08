import nltk
import unicodedata

from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)


def normalize_stopword(word: str) -> str:
    
    word = word.lower().strip()

    word = unicodedata.normalize("NFD", word)

    word = "".join(
        character
        for character in word
        if unicodedata.category(character) != "Mn"
    )

    return word


STOPWORDS_PT = {
    normalize_stopword(word)
    for word in stopwords.words("portuguese")
}