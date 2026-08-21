"""
Command line front end.

Usage looks like this:

    python -m humandetect notes.txt
    echo "some text" | python -m humandetect
    python -m humandetect --gui

Kept the argument handling manual since there are only a handful of flags
and argparse felt like overkill for that.
"""

import json
import sys

from .detector import analyze

HELP = """HumanDetect: quick check for machine written text

  python -m humandetect FILE      read a file
  python -m humandetect           read from standard input

options:
  --gui       open the desktop window instead of printing
  --verbose   also print every feature and signal
  --json      print the whole result as json, good for piping
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

    as_json = "--json" in argv
    if as_json:
        argv.remove("--json")

    use_gui = "--gui" in argv
    if use_gui:
        argv.remove("--gui")

    if argv:
        path = argv[0]
        try:
            with open(path, "r", encoding="utf8") as handle:
                text = handle.read()
        except OSError as err:
            print("could not read {}: {}".format(path, err), file=sys.stderr)
            return 1
    elif use_gui:
        # The window is its own way of getting text in, so do not sit on
        # stdin waiting for something that is never coming.
        text = ""
    else:
        # No file given, so assume the text is being piped in.
        text = sys.stdin.read()

    if use_gui:
        try:
            from .gui import run as run_gui
        except ImportError as err:
            # Some builds of Python ship without tkinter.
            print("the gui needs tkinter, which is missing: {}".format(err), file=sys.stderr)
            return 1
        return run_gui(text)

    if not text.strip():
        print("nothing to analyze", file=sys.stderr)
        return 1

    result = analyze(text)

    # json mode is all or nothing, so verbose does not apply to it. The
    # dict already carries the features and signals anyway.
    if as_json:
        print(json.dumps(result.as_dict(), indent=2))
        return 0

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
