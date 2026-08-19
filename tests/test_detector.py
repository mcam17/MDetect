"""
Basic checks. Run them with:

    python -m unittest discover tests
"""

import json
import unittest

from humandetect import analyze
from humandetect import Detector
from humandetect import features

# Written by me, on purpose messy, with uneven sentence lengths.
HUMAN_SAMPLE = """
So I tried the new build last night and honestly it was a mess. Crashed twice.
The second crash took my save file with it, which stung, because I had just
finished the long mission that everyone complains about. Anyway I filed a bug
report and went to bed. This morning it worked fine? No idea what changed.
I didn't reinstall anything. Weird.
"""

# Deliberately flat and formal, the way generated filler tends to read.
MACHINE_SAMPLE = """
It is important to note that modern software development involves many
different considerations. Furthermore, teams must carefully evaluate the
tools that they choose to adopt. Additionally, the process of integration
requires significant planning and coordination. In conclusion, organizations
that plan carefully will achieve better outcomes over the long term.
Moreover, continuous improvement plays a crucial role in this process.
"""


class TestFeatures(unittest.TestCase):
    def test_sentences_are_split(self):
        self.assertEqual(len(features.sentences("One. Two! Three?")), 3)

    def test_empty_text_does_not_explode(self):
        stats = features.extract("")
        for value in stats.values():
            self.assertEqual(value, 0.0)

    def test_quotes_are_stripped_from_words(self):
        # Used to come back as "'hello'" and count as its own word.
        self.assertEqual(features.words("he said 'hello' twice")[2], "hello")

    def test_quoted_word_is_not_a_new_word(self):
        self.assertEqual(features.vocabulary_richness("'a' 'a' a a"), 0.25)

    def test_contractions_are_counted(self):
        rate = features.contraction_rate("I don't think that's right at all")
        self.assertGreater(rate, 0)


class TestDetector(unittest.TestCase):
    def test_score_stays_in_range(self):
        for sample in (HUMAN_SAMPLE, MACHINE_SAMPLE):
            result = analyze(sample)
            self.assertGreaterEqual(result.score, 0.0)
            self.assertLessEqual(result.score, 1.0)

    def test_machine_sample_scores_higher(self):
        human = analyze(HUMAN_SAMPLE).score
        machine = analyze(MACHINE_SAMPLE).score
        self.assertGreater(machine, human)

    def test_short_text_is_flagged_unreliable(self):
        self.assertFalse(analyze("Hi there.").reliable)

    def test_unknown_weight_name_is_rejected(self):
        with self.assertRaises(ValueError):
            Detector(weights={"burstiness": 1.0, "not_a_feature": 0.5})

    def test_bad_input_type(self):
        with self.assertRaises(TypeError):
            analyze(1234)

    def test_as_dict_round_trips_through_json(self):
        payload = json.dumps(analyze(HUMAN_SAMPLE).as_dict())
        loaded = json.loads(payload)
        self.assertEqual(loaded["label"], "likely human")
        self.assertIn("burstiness", loaded["stats"])


if __name__ == "__main__":
    unittest.main()
