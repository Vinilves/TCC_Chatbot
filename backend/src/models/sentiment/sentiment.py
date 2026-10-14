from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "template_models" / "sentiment"


device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


print("Carregando modelo de sentimento...")
print("Diretório:", MODEL_PATH)


tokenizer = AutoTokenizer.from_pretrained(
    str(MODEL_PATH),
    local_files_only=True
)

model = AutoModelForSequenceClassification.from_pretrained(
    str(MODEL_PATH),
    local_files_only=True
).to(device)

model.eval()


def analyze_sentiment(text: str) -> dict:

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(device)

    with torch.inference_mode():

        outputs = model(**inputs)

    probabilities = torch.softmax(
        outputs.logits,
        dim=-1
    )

    confidence, prediction = torch.max(
        probabilities,
        dim=-1
    )

    label = model.config.id2label[
        prediction.item()
    ]

    return {
        "sentiment": label.lower(),
        "confidence": confidence.item()
    }