"""
Text features that HumanDetect looks at.

Nothing fancy in here. Every function takes plain text and gives back a
number that the detector can weigh later. I kept them separate so I can
test each one on its own without dragging the whole scorer along.
"""

import re
import statistics

# Splitting on sentence enders. Not perfect (abbreviations will fool it)
# but good enough for now.
SENTENCE_SPLIT = re.compile(r"[.!?]+\s+")
WORD_PATTERN = re.compile(r"[A-Za-z']+")

# Phrases I kept seeing over and over when I pasted model output into a
# scratch file. Feel free to grow this list.
STOCK_PHRASES = [
    "it is important to note",
    "it's important to note",
    "in conclusion",
    "delve into",
    "navigate the complexities",
    "in today's fast paced world",
    "as an ai language model",
    "furthermore",
    "moreover",
    "additionally",
    "a testament to",
    "plays a crucial role",
    "when it comes to",
    "on the other hand",
    "not only that",
    "in the realm of",
]

# Short forms that people type without thinking and models tend to skip.
CONTRACTIONS = [
    "don't", "can't", "won't", "i'm", "it's", "that's", "didn't",
    "isn't", "you're", "we're", "they're", "i've", "wasn't", "there's",
]


def sentences(text):
    """Break the text into sentences and throw away the empty pieces."""
    parts = SENTENCE_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def words(text):
    """Lowercased word list. Apostrophes stay so contractions survive."""
    return [w.lower() for w in WORD_PATTERN.findall(text)]


def burstiness(text):
    """
    How much sentence length jumps around.

    People write a long winding sentence and then a short one. Models tend
    to hold a steady rhythm, so a low number here is suspicious.
    Returned as the standard deviation divided by the mean, which keeps it
    comparable across short and long samples.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.pstdev(lengths) / mean


def vocabulary_richness(text):
    """
    Unique words over total words, also called the type token ratio.

    Longer texts always score lower here because words repeat, so I clamp
    the sample to the first 400 words to stop that drift.
    """
    tokens = words(text)[:400]
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def stock_phrase_rate(text):
    """Hits from STOCK_PHRASES per 100 words."""
    lowered = text.lower()
    hits = sum(lowered.count(phrase) for phrase in STOCK_PHRASES)
    total = len(words(text))
    if total == 0:
        return 0.0
    return hits / total * 100


def contraction_rate(text):
    """Contractions per 100 words. Casual human writing usually has some."""
    lowered = text.lower()
    hits = sum(lowered.count(c) for c in CONTRACTIONS)
    total = len(words(text))
    if total == 0:
        return 0.0
    return hits / total * 100


def punctuation_flair(text):
    """
    Count the marks that models love and most people rarely type: the long
    dash, the curly quote and the ellipsis character. Per 100 words again.
    """
    marks = ["—", "–", "’", "“", "”", "…"]
    hits = sum(text.count(m) for m in marks)
    total = len(words(text))
    if total == 0:
        return 0.0
    return hits / total * 100


def repeated_openers(text):
    """
    Share of sentences that begin with a word already used to open another
    sentence. Model output loves starting three paragraphs in a row the
    same way.
    """
    openers = []
    for s in sentences(text):
        first = words(s)
        if first:
            openers.append(first[0])
    if len(openers) < 2:
        return 0.0
    unique = len(set(openers))
    return 1 - (unique / len(openers))


def extract(text):
    """Run every feature and hand back a plain dict."""
    return {
        "burstiness": burstiness(text),
        "vocabulary_richness": vocabulary_richness(text),
        "stock_phrase_rate": stock_phrase_rate(text),
        "contraction_rate": contraction_rate(text),
        "punctuation_flair": punctuation_flair(text),
        "repeated_openers": repeated_openers(text),
    }
