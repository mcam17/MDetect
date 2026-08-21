"""
A small desktop window for people who would rather not open a terminal.

Tkinter ships with Python, so this keeps the no dependency promise. Paste
text in the box or open a file, hit Check, and the score plus every raw
feature shows up underneath.

    python -m humandetect --gui
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .detector import Detector

# Colours for the three bands. Muted on purpose, the label already says it.
BAND_COLOURS = {
    "likely AI": "#b3261e",
    "unclear": "#8a6d00",
    "likely human": "#1c6b3c",
}

PLACEHOLDER = "Paste some text here, or use Open file, then press Check."


class App:
    """The whole window. One class is plenty at this size."""

    def __init__(self, root, detector=None):
        self.root = root
        self.detector = detector or Detector()

        root.title("HumanDetect")
        root.minsize(560, 520)

        outer = ttk.Frame(root, padding=12)
        outer.pack(fill="both", expand=True)

        # Top row: the buttons.
        buttons = ttk.Frame(outer)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Open file", command=self.open_file).pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left", padx=(6, 0))
        ttk.Button(buttons, text="Check", command=self.check).pack(side="right")

        # Middle: the text box with a scrollbar.
        box = ttk.Frame(outer)
        box.pack(fill="both", expand=True, pady=(10, 10))

        self.text = tk.Text(box, wrap="word", height=14, undo=True)
        self.text.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(box, orient="vertical", command=self.text.yview)
        scroll.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=scroll.set)

        # Bottom: the verdict and the numbers behind it.
        self.verdict = tk.Label(outer, text=PLACEHOLDER, font=("TkDefaultFont", 13, "bold"))
        self.verdict.pack(anchor="w")

        self.note = ttk.Label(outer, text="")
        self.note.pack(anchor="w", pady=(2, 8))

        self.table = ttk.Treeview(
            outer, columns=("value", "signal"), show="tree headings", height=6
        )
        self.table.heading("#0", text="feature")
        self.table.heading("value", text="raw")
        self.table.heading("signal", text="suspicion")
        self.table.column("#0", width=200, anchor="w")
        self.table.column("value", width=90, anchor="e")
        self.table.column("signal", width=90, anchor="e")
        self.table.pack(fill="both", expand=False)

        # Ctrl+Enter runs the check without reaching for the mouse.
        self.text.bind("<Control-Return>", self._on_shortcut)
        self.text.focus_set()

    def _on_shortcut(self, event):
        self.check()
        return "break"  # stop tkinter inserting a newline too

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open a text file",
            filetypes=[("Text files", "*.txt *.md"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf8", errors="replace") as handle:
                content = handle.read()
        except OSError as err:
            messagebox.showerror("Could not open file", str(err))
            return

        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.check()

    def clear(self):
        self.text.delete("1.0", "end")
        self.verdict.configure(text=PLACEHOLDER, fg="black")
        self.note.configure(text="")
        self.table.delete(*self.table.get_children())
        self.text.focus_set()

    def check(self):
        content = self.text.get("1.0", "end")
        if not content.strip():
            messagebox.showinfo("Nothing to check", "The box is empty.")
            return

        result = self.detector.analyze(content)

        self.verdict.configure(
            text="{} at {:.0f} percent".format(result.label, result.score * 100),
            fg=BAND_COLOURS.get(result.label, "black"),
        )
        self.note.configure(
            text=""
            if result.reliable
            else "Sample is short, so this number is not worth much."
        )

        self.table.delete(*self.table.get_children())
        for name, value in result.stats.items():
            signal = result.signals.get(name)
            self.table.insert(
                "",
                "end",
                text=name.replace("_", " "),
                values=(
                    "{:.3f}".format(value),
                    "-" if signal is None else "{:.3f}".format(signal),
                ),
            )


def run(text=None):
    """Open the window. Optional text is pre-filled and checked right away."""
    root = tk.Tk()
    app = App(root)
    if text and text.strip():
        app.text.insert("1.0", text)
        app.check()
    root.mainloop()
    return 0
