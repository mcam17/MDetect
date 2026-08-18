"""
Command line front end.

Usage looks like this:

    python -m humandetect notes.txt
    echo "some text" | python -m humandetect

Kept the argument handling manual since there are only two options and
argparse felt like overkill for that.
"""

import sys

from .detector import analyze

HELP = """HumanDetect: quick check for machine written text

  python -m humandetect FILE      read a file
  python -m humandetect           read from standard input

options:
  --verbose   also print every feature and signal
  --help      show this text
"""


def run(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--help" in argv or "-h" in argv:
        print(HELP)
        return 0

    verbose = "--verbose" in argv
    if verbose:
        argv.remove("--verbose")

    if argv:
        path = argv[0]
        try:
            with open(path, "r", encoding="utf8") as handle:
                text = handle.read()
        except OSError as err:
            print("could not read {}: {}".format(path, err), file=sys.stderr)
            return 1
    else:
        # No file given, so assume the text is being piped in.
        text = sys.stdin.read()

    if not text.strip():
        print("nothing to analyze", file=sys.stderr)
        return 1

    result = analyze(text)
    print(result.summary())

    if verbose:
        print("\nfeatures:")
        for name, value in result.stats.items():
            print("  {:<22} {:.3f}".format(name, value))
        print("\nsignals:")
        for name, value in result.signals.items():
            print("  {:<22} {:.3f}".format(name, value))

    return 0


if __name__ == "__main__":
    sys.exit(run())
