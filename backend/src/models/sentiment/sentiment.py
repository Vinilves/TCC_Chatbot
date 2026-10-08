import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


print("Carregando modelo de sentimento...")
print("Modelo:", MODEL_NAME)


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)

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