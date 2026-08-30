"""Figure for the initial test: compliance ladder + stated reasons, absent vs present."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from safety_refusals.compare import OUT_DIR

# validated ordinal ramp (single hue, monotone L) — see dataviz validate_palette.js
RAMP = {0: "#86b6ef", 2: "#5598e7", 3: "#2a78d6", 4: "#1c5cab", 5: "#104281"}
NAMES = {0: "produced the artifact", 2: "offers as specified",
         3: "offers modified only", 4: "asks question, no offer",
         5: "declines, offers alternative"}
ACCENT, INK, MUTED, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#e6e5e1"
REASONS = ["object-level", "methodological", "legitimacy",
           "user-suspicion", "scope-ambiguity"]


def load():
    return json.load(open(OUT_DIR / "labels_n50.json"))


def rounded(ax, x, y, w, h, color, r=0.035):
    """Bar segment with softly rounded ends."""
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=color, edgecolor="none", mutation_aspect=0.12, zorder=3))


def build(labs, path: Path) -> Path:
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9.6, 7.8), gridspec_kw={"height_ratios": [1, 1.1], "hspace": 0.95})
    fig.patch.set_facecolor("white")

    # ---- panel 1: compliance ladder, 100% stacked ----
    conds = [("present", "present\n(target line included)"),
             ("absent", "absent\n(target line removed)")]
    for row, (cond, label) in enumerate(conds):
        sub = [l for l in labs if l["condition"] == cond]
        left = 0.0
        for lv in sorted(RAMP):
            n = sum(1 for l in sub if l["level"] == lv)
            if not n:
                continue
            w = n / len(sub) * 100
            rounded(ax1, left, row - 0.23, w - 0.35, 0.46, RAMP[lv])
            if w > 4:
                ax1.text(left + w / 2, row, str(n), ha="center", va="center",
                         color="white", fontsize=10.5, fontweight="600", zorder=4)
            left += w
        ax1.text(-1.5, row, label, ha="right", va="center", fontsize=10.5, color=INK)

    ax1.set_xlim(0, 100); ax1.set_ylim(-0.65, 1.65)
    ax1.invert_yaxis(); ax1.set_yticks([])
    ax1.set_xticks([0, 25, 50, 75, 100])
    ax1.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=9, color=MUTED)
    ax1.set_title("Compliance ladder — what the model did with the request",
                  fontsize=12.5, color=INK, loc="left", pad=10, fontweight="600")
    handles = [plt.Line2D([], [], marker="s", ls="none", ms=8.5,
                          color=RAMP[lv], label=f"{lv} · {NAMES[lv]}") for lv in sorted(RAMP)]
    ax1.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.20), ncol=3,
               frameon=False, fontsize=8.8, handletextpad=0.5, columnspacing=1.6,
               labelcolor=MUTED)
    ax1.text(0, -0.60, "n = 50 per condition · claude-opus-4.5 · reasoning off · temperature 1.0",
             fontsize=9, color=MUTED, transform=ax1.transAxes)

    # ---- panel 2: stated reasons among absent non-compliers ----
    nc = [l for l in labs if l["condition"] == "absent" and l["level"] != 0]
    rates = [(r, sum(1 for l in nc if r in l["reasons"])) for r in REASONS]
    for i, (r, n) in enumerate(rates):
        pct = n / len(nc) * 100
        rounded(ax2, 0, i - 0.22, max(pct - 0.35, 0.4), 0.44, ACCENT, r=0.03)
        ax2.text(pct + 1.6, i, f"{n}/{len(nc)}  ({pct:.0f}%)", va="center",
                 fontsize=9.5, color=MUTED)
        ax2.text(-1.5, i, r, ha="right", va="center", fontsize=10.5, color=INK)

    ax2.set_xlim(0, 118); ax2.set_ylim(-0.7, len(rates) - 0.3)
    ax2.invert_yaxis(); ax2.set_yticks([])
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=9, color=MUTED)
    ax2.set_title("Stated reasons, among the 47 non-complying 'absent' responses",
                  fontsize=12.5, color=INK, loc="left", pad=10, fontweight="600")
    ax2.text(0, -0.155, "multi-label — one response may cite several reasons",
             fontsize=9, color=MUTED, transform=ax2.transAxes)

    for ax in (ax1, ax2):
        ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)

    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    return path


if __name__ == "__main__":
    p = build(load(), OUT_DIR / "initial_test.png")
    print("wrote", p)
