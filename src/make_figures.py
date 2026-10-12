"""Step 6b: charts and tables from data/processed/results/ (made by src/analyze.py).

Writes PNG charts to figures/ and CSV tables to data/processed/results/tables/. Colors are the
dataviz reference palette's first three categorical slots (checked for colorblind safety, Oct 12)
plus gray. Every chart has a legend or labels, and every number is also in a table.
"""

import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import PROCESSED, ROOT  # noqa: E402

RESULTS = PROCESSED / "results"
TABLES = RESULTS / "tables"
FIGURES = ROOT / "figures"

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SLOT = ["#2a78d6", "#eb6834", "#1baf7a"]
GRAY = "#a9a8a2"
NAMES = {"qwen3-8b-nothink": "Qwen3 8B", "qwen3-14b-nothink": "Qwen3 14B",
         "qwen3-8b-think": "Qwen3 8B, thinking on", "gpt-oss-20b-low": "gpt-oss 20B (low reasoning)"}
PAIR_SETUPS = ["qwen3-8b-nothink", "qwen3-14b-nothink", "gpt-oss-20b-low"]
LIST_SETUPS = ["qwen3-8b-nothink", "qwen3-14b-nothink", "qwen3-8b-think", "gpt-oss-20b-low"]
BANDS = ["1", "2", "3-5", "6-10", "11-25", "26+"]
LENGTHS = [5, 10, 20]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "legend.frameon": False,
})


def load():
    out = {}
    for setup in LIST_SETUPS:
        path = RESULTS / f"{setup}.json"
        if path.exists():
            out[setup] = json.loads(path.read_text(encoding="utf-8"))
    return out


def write_table(name, header, rows):
    TABLES.mkdir(parents=True, exist_ok=True)
    with (TABLES / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def err(value, ci):
    if ci is None or value is None:
        return [[0], [0]]
    return [[max(0, value - ci[0])], [max(0, ci[1] - value)]]


def fig_date_resolution(res):
    setups = [s for s in PAIR_SETUPS if s in res and "pairs" in res[s]]
    if not setups:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True)
    rows = []
    for panel, (kind, title, ref) in enumerate([("stable-right", "Right both ways", 0.95),
                                                 ("flip", "Answer flips when the order is swapped", 0.05)]):
        ax = axes[panel]
        for k, s in enumerate(setups):
            table = res[s]["pairs"]["by_gap_band"]
            vals = [table[b][kind]["share"] for b in BANDS]
            lo = [table[b][kind]["share"] - table[b][kind]["ci95"][0] for b in BANDS]
            hi = [table[b][kind]["ci95"][1] - table[b][kind]["share"] for b in BANDS]
            x = list(range(len(BANDS)))
            # No end-of-line labels: lines often meet near 1.0 and the labels would collide.
            # The legend and pairs_by_gap.csv identify every line.
            ax.errorbar(x, vals, yerr=[lo, hi], color=SLOT[k], lw=2, marker="o", ms=6, capsize=0,
                        elinewidth=1, mec=SURFACE, mew=2, label=NAMES[s])
            if panel == 0:
                for b in BANDS:
                    rows.append([s, b, table[b]["pairs"], table[b]["stable-right"]["share"],
                                 *table[b]["stable-right"]["ci95"], table[b]["flip"]["share"],
                                 *table[b]["flip"]["ci95"], table[b]["stable-wrong"]["share"]])
        ax.axhline(ref, color=MUTED, lw=1)
        ax.set_title(title, loc="left")
        ax.set_xticks(range(len(BANDS)), BANDS)
        ax.set_xlabel("Years between the two events")
        ax.set_ylim(0, 1)
        ax.set_xlim(-0.3, len(BANDS) - 0.7)
    axes[0].set_ylabel("Share of pairs")
    axes[0].legend(loc="lower right", fontsize=8)
    fig.suptitle("Date resolution: how far apart events must be before answers are right and consistent",
                 x=0.01, ha="left", fontsize=11)
    fig.text(0.01, -0.02, "Lines at 95% (left) and 5% (right) are the date-resolution thresholds. "
             "Bars: 95% ranges from redrawing events.", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig1_date_resolution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    write_table("pairs_by_gap.csv", ["setup", "gap_band", "pairs", "stable_right", "sr_lo", "sr_hi", "flip",
                                     "flip_lo", "flip_hi", "stable_wrong"], rows)


def fig_list_mistakes(res):
    setups = [s for s in LIST_SETUPS if s in res and "lists" in res[s]]
    if not setups:
        return
    kinds = [("C", "List-only (right on the pair alone)", SLOT[0]),
             ("B", "Wrong on the pair alone too", SLOT[1]),
             ("U", "Unsure on the pair alone (flips)", SLOT[2]),
             ("X", "Pair answer unreadable", GRAY)]
    fig, axes = plt.subplots(1, len(setups), figsize=(3.2 * len(setups), 4.2), sharey=True, squeeze=False)
    rows = []
    for ax, s in zip(axes[0], setups):
        by = res[s]["lists"]["by_length"]
        bottom = [0.0] * len(LENGTHS)
        for kind, label, color in kinds:
            vals = [(by[str(l)] if str(l) in by else by.get(l, {})).get("type_share", {}).get(kind, {}).get("value") or 0
                    for l in LENGTHS]
            ax.bar([str(l) for l in LENGTHS], vals, bottom=bottom, color=color, width=0.55,
                   edgecolor=SURFACE, linewidth=2, label=label)
            bottom = [b + v for b, v in zip(bottom, vals)]
        for l in LENGTHS:
            d = by.get(str(l), by.get(l))
            if d:
                rows.append([s, l, d["lists"], d["valid_share"], d["wrong_neighbor_pairs"],
                             *[d["type_share"][k]["value"] for k in "BUCX"], d["misdated_share"]])
                ax.annotate(f"n={d['wrong_neighbor_pairs']}", (LENGTHS.index(l), 1.01), ha="center",
                            fontsize=7, color=MUTED, annotation_clip=False)
        ax.set_title(NAMES[s], loc="left", fontsize=9)
        ax.set_xlabel("Events in the list")
        ax.set_ylim(0, 1.06)
    axes[0][0].set_ylabel("Share of wrong neighbor pairs")
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Where list mistakes come from: would the model also get that pair wrong on its own?",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig2_list_mistakes.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    write_table("list_mistakes_by_length.csv", ["setup", "length", "lists", "valid_share", "wrong_neighbor_pairs",
                                               "B", "U", "C", "X", "misdated_share"], rows)


def fig_penalty_and_integrity(res):
    setups = [s for s in LIST_SETUPS if s in res and "lists" in res[s]]
    if not setups:
        return
    fig, axes = plt.subplots(2, len(setups), figsize=(3.2 * len(setups), 6), sharey="row", squeeze=False)
    rows = []
    for col, s in enumerate(setups):
        by = res[s]["lists"]["by_length"]
        pen, valid = [], []
        for l in LENGTHS:
            d = by.get(str(l), by.get(l))
            pen.append(d["penalty_mean"] if d else {"value": None, "ci95": None})
            valid.append(d["valid_share"] if d else None)
            if d:
                rows.append([s, l, d["valid_share"], d["didnt_stop_share"], d["exact_share_of_all"],
                             d["mean_tau_valid"], d["penalty_mean"]["value"],
                             *(d["penalty_mean"]["ci95"] or [None, None])])
        ax = axes[0][col]
        for k, (l, p) in enumerate(zip(LENGTHS, pen)):
            if p["value"] is not None:
                ax.errorbar([k], [p["value"]], yerr=err(p["value"], p["ci95"]), color=SLOT[0], marker="o", ms=7,
                            mec=SURFACE, mew=2, lw=2, elinewidth=1)
        ax.axhline(0, color=MUTED, lw=1)
        ax.set_xticks(range(3), [str(l) for l in LENGTHS])
        ax.set_title(NAMES[s], loc="left", fontsize=9)
        ax = axes[1][col]
        ax.bar([str(l) for l in LENGTHS], [v or 0 for v in valid], color=SLOT[0], width=0.55)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Events in the list")
    axes[0][0].set_ylabel("List penalty\n(observed minus predicted\nwrong neighbor pairs)")
    axes[1][0].set_ylabel("Share of lists with every\nevent exactly once")
    fig.suptitle("Top: extra mistakes beyond what the model's own pair answers predict.  "
                 "Bottom: list integrity.", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig3_penalty_and_integrity.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    write_table("lists_by_length.csv", ["setup", "length", "valid_share", "didnt_stop_share", "exact_share_of_all",
                                       "mean_tau_valid", "penalty", "penalty_lo", "penalty_hi"], rows)


def table_cycles(res):
    rows = []
    for s in PAIR_SETUPS:
        c = res.get(s, {}).get("cycles")
        if c:
            rows.append([s, c["all_stable_triples"], c["observed_circular"], c["shuffle_mean"],
                         *c["shuffle_ci95"], c["p_two_sided"]])
    if rows:
        write_table("cycles.csv", ["setup", "all_stable_triples", "observed_circular", "shuffle_mean",
                                   "shuffle_lo", "shuffle_hi", "p_two_sided"], rows)


def main():
    FIGURES.mkdir(exist_ok=True)
    res = load()
    fig_date_resolution(res)
    fig_list_mistakes(res)
    fig_penalty_and_integrity(res)
    table_cycles(res)
    print(f"Charts in {FIGURES}, tables in {TABLES}")


if __name__ == "__main__":
    main()
