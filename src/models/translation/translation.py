import re
import torch

from transformers import MarianTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "Helsinki-NLP/opus-mt-en-ROMANCE"

device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


print("Carregando modelo de tradução...")
print("Modelo:", MODEL_NAME)


tokenizer = MarianTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
).to(device)

model.eval()


def separate_code(text: str):

    if not isinstance(text, str):
        return [("text", text)]

    parts = []

    pattern = (
        r"(```[\s\S]*?```|`[^`\n]+`)"
    )

    last_end = 0

    for match in re.finditer(pattern, text):
        start = match.start()
        end = match.end()

        if start > last_end:
            parts.append(
                (
                    "text",
                    text[last_end:start]
                )
            )

        parts.append(
            (
                "code",
                match.group(0)
            )
        )

        last_end = end

    if last_end < len(text):
        parts.append(
            (
                "text",
                text[last_end:]
            )
        )

    return parts


def translate_batch(texts, batch_size=16):
    results = []

    for start in range(
        0,
        len(texts),
        batch_size
    ):
        end = min(
            start + batch_size,
            len(texts)
        )

        batch = texts[start:end]

        batch = [
            ">>pt_BR<< " + text
            for text in batch
        ]

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(device)

        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_length=512
            )

        translations = tokenizer.batch_decode(
            outputs,
            skip_special_tokens=True
        )

        results.extend(translations)

    return results


def translate_response(text: str) -> str:

    if not isinstance(text, str):
        return text

    if not text.strip():
        return text

    parts = separate_code(text)

    texts = []
    indices = []

    result = [None] * len(parts)

    for i, (part_type, content) in enumerate(parts):

        if part_type == "text":
            if content.strip():
                texts.append(content)
                indices.append(i)
            else:
                result[i] = content

        else:
            result[i] = content

    if texts:
        translations = translate_batch(texts)

        for index, translation in zip(indices, translations):
            result[index] = translation

    return "".join(
        part
        for part in result
        if part is not None
    )