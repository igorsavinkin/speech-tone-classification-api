from dataclasses import dataclass

from app.schemas import Label


@dataclass
class ModelResult:
    label: Label
    confidence: float


class SimpleSentimentModel:
    POSITIVE_WORDS = {"good", "great", "excellent", "love", "amazing"}
    NEGATIVE_WORDS = {"bad", "terrible", "awful", "hate", "poor"}

    def predict(self, text: str) -> ModelResult:
        tokens = {token.strip(".,!?").lower() for token in text.split()}
        positive_hits = len(tokens & self.POSITIVE_WORDS)
        negative_hits = len(tokens & self.NEGATIVE_WORDS)
        score = positive_hits - negative_hits

        if score >= 2:
            return ModelResult(label=Label.positive, confidence=0.95)
        if score <= -2:
            return ModelResult(label=Label.negative, confidence=0.95)
        if score > 0:
            return ModelResult(label=Label.positive, confidence=0.6)
        if score < 0:
            return ModelResult(label=Label.negative, confidence=0.6)
        return ModelResult(label=Label.neutral, confidence=0.55)
