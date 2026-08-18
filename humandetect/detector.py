"""
The scorer.

Each feature gets turned into a small signal between 0 and 1, where 1 means
"this looks machine written". Then I take a weighted average. The weights
are hand picked from eyeballing a few dozen samples, so treat the output as
a hint and not as proof.
"""

from dataclasses import dataclass, field

from . import features

# How much each signal counts toward the final score. They add up to 1.0.
WEIGHTS = {
    "burstiness": 0.30,
    "vocabulary_richness": 0.15,
    "stock_phrase_rate": 0.20,
    "contraction_rate": 0.15,
    "punctuation_flair": 0.10,
    "repeated_openers": 0.10,
}

# Below this many words the sample is too small to say anything useful.
MIN_WORDS = 40


def _clamp(value):
    """Keep a signal inside the 0 to 1 range."""
    return max(0.0, min(1.0, value))


def _signals(stats):
    """Turn raw feature numbers into 0 to 1 suspicion values."""
    signals = {}

    # Flat rhythm is the strongest tell I found. Around 0.6 is normal for a
    # person, so anything under that starts pushing the score up.
    signals["burstiness"] = _clamp((0.6 - stats["burstiness"]) / 0.6)

    # A very tidy middling vocabulary reads as generated. Very low richness
    # usually just means the text is short and repetitive, so I only punish
    # the band under 0.55.
    signals["vocabulary_richness"] = _clamp((0.55 - stats["vocabulary_richness"]) / 0.25)

    # Two stock phrases per hundred words is already a lot.
    signals["stock_phrase_rate"] = _clamp(stats["stock_phrase_rate"] / 2.0)

    # No contractions at all is a mild flag on its own.
    signals["contraction_rate"] = _clamp((1.5 - stats["contraction_rate"]) / 1.5)

    # Typed by hand this is near zero, pasted from a model it is not.
    signals["punctuation_flair"] = _clamp(stats["punctuation_flair"] / 1.0)

    # Half the sentences opening with a repeat word is plenty.
    signals["repeated_openers"] = _clamp(stats["repeated_openers"] / 0.5)

    return signals


@dataclass
class Result:
    """What the detector gives back."""

    score: float
    label: str
    reliable: bool
    stats: dict = field(default_factory=dict)
    signals: dict = field(default_factory=dict)

    def summary(self):
        """One line version for printing."""
        note = "" if self.reliable else " (sample is short, low confidence)"
        return "{} at {:.0f} percent{}".format(self.label, self.score * 100, note)


class Detector:
    """Wraps the weights so they can be swapped out in tests."""

    def __init__(self, weights=None, min_words=MIN_WORDS):
        self.weights = dict(weights or WEIGHTS)
        self.min_words = min_words

    def label_for(self, score):
        # Three buckets. I avoided a hard yes or no on purpose because the
        # middle band really is a coin flip.
        if score >= 0.65:
            return "likely AI"
        if score >= 0.40:
            return "unclear"
        return "likely human"

    def analyze(self, text):
        if not isinstance(text, str):
            raise TypeError("analyze needs a string")

        stats = features.extract(text)
        signals = _signals(stats)

        total = sum(self.weights.values())
        if total == 0:
            raise ValueError("weights cannot all be zero")

        score = sum(signals[k] * w for k, w in self.weights.items()) / total
        reliable = len(features.words(text)) >= self.min_words

        return Result(
            score=round(score, 3),
            label=self.label_for(score),
            reliable=reliable,
            stats=stats,
            signals=signals,
        )


def analyze(text):
    """Shortcut for people who do not want to build a Detector."""
    return Detector().analyze(text)
