# HumanDetect

A small, dependency free Python library that guesses whether a chunk of text was
written by a person or by a language model. It does this with plain statistics
over the text itself, so there is no model to download and no API key to set up.
The whole thing runs on the standard library.

HumanDetect is meant to be a hint, not a verdict. It gives you a score, a label and
the raw numbers behind both so you can decide for yourself.

## How it works

The text is broken into sentences and words, then six features are measured:

| feature | what it looks at |
| --- | --- |
| burstiness | how much sentence length varies. People swing, models stay level. |
| vocabulary richness | unique words over total words in the first 400 words. |
| stock phrase rate | how often filler phrases like "it is important to note" show up. |
| contraction rate | casual short forms such as "don't" and "it's". |
| punctuation flair | long dashes, curly quotes and ellipsis characters per 100 words. |
| repeated openers | how many sentences start with a word another sentence already used. |

Each feature is mapped to a suspicion value between 0 and 1, then combined with
a weighted average into a single score. The weights live at the top of
`humandetect/detector.py` and are easy to change.

Score bands:

* 0.65 and above: likely AI
* 0.40 to 0.65: unclear
* below 0.40: likely human

Samples under 40 words get marked as unreliable, because at that size the
numbers bounce around too much to mean anything.

## Install

Clone the repo and use it in place. There is nothing to install.

```bash
git clone https://github.com/mcam17/HumanDetect.git
cd HumanDetect
```

## Usage

As a library:

```python
from humandetect import analyze

result = analyze(open("essay.txt").read())
print(result.label)      # "likely AI"
print(result.score)      # 0.71
print(result.stats)      # every raw feature value
```

From the command line:

```bash
python -m humandetect essay.txt
```

```bash
python -m humandetect essay.txt --verbose
```

Or get the whole result as json, which is easier to pipe somewhere else:

```bash
python -m humandetect essay.txt --json
```

You can also pipe text in:

```bash
echo "some text to check" | python -m humandetect
```

If you want different weights, build the detector yourself:

```python
from humandetect import Detector

d = Detector(weights={"burstiness": 0.5, "stock_phrase_rate": 0.5})
print(d.analyze(text).summary())
```

## Tests

```bash
python -m unittest discover tests
```

## Limits

Worth being upfront about these:

* Short text is basically noise. Under 40 words the score means very little.
* Edited AI output can slip through easily, and so can heavily formal human
  writing such as legal or academic text.
* The stock phrase list is English only and hand written, so it will go stale.
* Never use this to accuse anyone of anything. It is a rough signal.

## Roadmap

Things I want to add next:

* A larger and smarter stock phrase list, maybe loaded from a data file.
* Paragraph level scoring so you can see which section looks generated.
* A proper `pyproject.toml` so it can be installed with pip.
* More test samples, ideally a small labelled corpus to tune the weights on.

## License

MIT. See LICENSE.
