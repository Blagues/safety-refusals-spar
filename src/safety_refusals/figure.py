"""Two standalone figures for the initial test (baseline vs target-line-removed)."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from safety_refusals.compare import OUT_DIR

# validated ordinal ramp — single hue, monotone lightness (dataviz validate_palette.js)
RAMP = {0: "#86b6ef", 2: "#5598e7", 3: "#2a78d6", 4: "#1c5cab", 5: "#104281"}
NAMES = {0: "produced the artifact", 2: "offers as specified",
         3: "offers modified only", 4: "asks question, no offer",
         5: "declines, offers alternative"}
ACCENT, INK, MUTED, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#e6e5e1"
REASONS = ["object-level", "methodological", "legitimacy",
           "user-suspicion", "scope-ambiguity"]
SUB = "n = 50 per condition · claude-opus-4.5 · reasoning off · temperature 1.0"


def load():
    return json.load(open(OUT_DIR / "labels_n50.json"))


def _bar(ax, x, y, w, h, color, r=0.035):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=color, edgecolor="none", mutation_aspect=0.12, zorder=3))


def _clean(ax):
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=9, color=MUTED)


def compliance(labs, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.6, 2.75))
    fig.patch.set_facecolor("white")
    rows = [("present", "Baseline\n(target line included)"),
            ("absent", "Target line\nremoved")]
    for row, (cond, label) in enumerate(rows):
        sub = [l for l in labs if l["condition"] == cond]
        left = 0.0
        for lv in sorted(RAMP):
            n = sum(1 for l in sub if l["level"] == lv)
            if not n:
                continue
            w = n / len(sub) * 100
            _bar(ax, left, row - 0.23, w - 0.35, 0.46, RAMP[lv])
            if w > 4:
                ax.text(left + w / 2, row, str(n), ha="center", va="center",
                        color="white", fontsize=10.5, fontweight="bold", zorder=4)
            left += w
        ax.text(-1.5, row, label, ha="right", va="center", fontsize=10.5, color=INK)

    ax.set_xlim(0, 100); ax.set_ylim(-0.62, 1.62); ax.invert_yaxis(); ax.set_yticks([])
    _clean(ax)
    ax.set_title("Compliance ladder — what the model did with the request",
                 fontsize=12.5, color=INK, loc="left", pad=10, fontweight="bold")
    handles = [plt.Line2D([], [], marker="s", ls="none", ms=8.5,
                          color=RAMP[lv], label=f"{lv} · {NAMES[lv]}") for lv in sorted(RAMP)]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.20), ncol=3,
              frameon=False, fontsize=8.8, handletextpad=0.5, columnspacing=1.6,
              labelcolor=MUTED)
    ax.text(0, -0.70, SUB, fontsize=9, color=MUTED, transform=ax.transAxes)
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def reasons(labs, path: Path) -> Path:
    nc = [l for l in labs if l["condition"] == "absent" and l["level"] != 0]
    base_nc = [l for l in labs if l["condition"] == "present" and l["level"] != 0]
    fig, ax = plt.subplots(figsize=(9.6, 3.0))
    fig.patch.set_facecolor("white")
    for i, r in enumerate(REASONS):
        n = sum(1 for l in nc if r in l["reasons"])
        pct = n / len(nc) * 100
        _bar(ax, 0, i - 0.22, max(pct - 0.35, 0.4), 0.44, ACCENT, r=0.03)
        ax.text(pct + 1.6, i, f"{n}/{len(nc)}  ({pct:.0f}%)", va="center",
                fontsize=9.5, color=MUTED)
        ax.text(-1.5, i, r, ha="right", va="center", fontsize=10.5, color=INK)

    ax.set_xlim(0, 118); ax.set_ylim(-0.7, len(REASONS) - 0.3)
    ax.invert_yaxis(); ax.set_yticks([])
    _clean(ax)
    ax.set_title(f"Stated reasons — the {len(nc)} non-complying responses "
                 "with the target line removed",
                 fontsize=12.5, color=INK, loc="left", pad=10, fontweight="bold")
    ax.text(0, -0.20, "multi-label — one response may cite several reasons.  "
            f"Baseline is not shown: it produced only {len(base_nc)} non-complying response.",
            fontsize=9, color=MUTED, transform=ax.transAxes)
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    labs = load()
    print("wrote", compliance(labs, OUT_DIR / "fig1_compliance.png"))
    print("wrote", reasons(labs, OUT_DIR / "fig2_stated_reasons.png"))
