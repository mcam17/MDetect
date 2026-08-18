"""HumanDetect: a small heuristic checker for machine written text."""

from .detector import Detector, Result, analyze

__version__ = "0.1.0"

__all__ = ["Detector", "Result", "analyze", "__version__"]
