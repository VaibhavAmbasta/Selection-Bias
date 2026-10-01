"""Shared matplotlib styling so every figure reads as one set."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
GRAY = "#8a8985"
INK = "#0b0b0b"
INK_2 = "#52514e"
SURFACE = "#fcfcfb"
GRID = "#e4e3df"


def apply():
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 10.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "font.family": "DejaVu Sans",
        "figure.dpi": 110,
    })


def save(fig, path, note=None):
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color=INK_2, ha="left", va="top", wrap=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def titled(ax, title, subtitle=None):
    """Bold headline plus a plain-English subtitle under it."""
    ax.set_title(title, pad=30 if subtitle else 10)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10, color=INK_2,
                ha="left", va="bottom")


def label_hbars(ax, y, vals, texts, pad, inside_min=None):
    """Write each bar's value just past its end, in ink colour."""
    for yi, v, t in zip(y, vals, texts):
        ax.text(v + (pad if v >= 0 else -pad), yi, t, va="center",
                ha="left" if v >= 0 else "right", fontsize=11, color=INK, fontweight="bold")
