"""BER vs Eb/N0 sweep: simulation against theory.

Usage:
    python3 scripts/ber_sweep.py [--min-errors 200] [--max-bits 20000000]

Writes results/ber_awgn.png and results/ber_awgn.csv.

As you add stages, add curves to this same plot. A single figure showing
AWGN theory / unequalized multipath / RLS-equalized is the one image that
explains the whole project.
"""

import argparse
import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modem.bits import qpsk_demap, qpsk_map, random_bits
from modem.channel import awgn
from modem.metrics import bit_error_rate, implementation_loss_db, qpsk_ber_theory

RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results"
)


def simulate_point(ebn0_db, rng, min_errors, max_bits, chunk_bits=400_000):
    """Accumulate bits until min_errors errors or max_bits budget is spent."""
    errors = 0
    total = 0
    while errors < min_errors and total < max_bits:
        bits = random_bits(chunk_bits, rng)
        rx = qpsk_demap(awgn(qpsk_map(bits), ebn0_db, rng))
        errors += int(np.count_nonzero(bits != rx))
        total += chunk_bits
    return (errors / total if total else float("nan")), errors, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-errors", type=int, default=200)
    ap.add_argument("--max-bits", type=int, default=20_000_000)
    ap.add_argument("--seed", type=int, default=20261011)
    args = ap.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    ebn0_grid = np.arange(0.0, 11.0, 1.0)

    rows = []
    print(f"{'Eb/N0':>6} {'measured':>11} {'theory':>11} {'errors':>8} "
          f"{'bits':>11} {'loss dB':>8}")
    for ebn0_db in ebn0_grid:
        ber, errors, total = simulate_point(
            ebn0_db, rng, args.min_errors, args.max_bits
        )
        theory = float(qpsk_ber_theory(ebn0_db))
        loss = implementation_loss_db(ebn0_db, ber) if ber > 0 else float("nan")
        rows.append((ebn0_db, ber, theory, errors, total, loss))
        flag = "" if errors >= args.min_errors else "  (few errors)"
        print(f"{ebn0_db:6.1f} {ber:11.3e} {theory:11.3e} {errors:8d} "
              f"{total:11d} {loss:8.2f}{flag}")

    csv_path = os.path.join(RESULTS_DIR, "ber_awgn.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ebn0_db", "ber_measured", "ber_theory", "errors",
                    "bits", "implementation_loss_db"])
        w.writerows(rows)

    fine = np.linspace(0.0, 10.0, 400)
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.semilogy(fine, qpsk_ber_theory(fine), "-", lw=1.8,
                label="Theory: $Q(\\sqrt{2E_b/N_0})$")
    measured = [r[1] for r in rows]
    ax.semilogy(ebn0_grid, measured, "o", ms=6, mfc="none", mew=1.6,
                label="Simulated (Stage 0: AWGN)")
    ax.set_xlabel("$E_b/N_0$ (dB)")
    ax.set_ylabel("Bit error rate")
    ax.set_title("Gray-coded QPSK over AWGN")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-7, 1e0)
    ax.legend()
    fig.tight_layout()
    png_path = os.path.join(RESULTS_DIR, "ber_awgn.png")
    fig.savefig(png_path, dpi=150)
    print(f"\nwrote {png_path}\nwrote {csv_path}")


if __name__ == "__main__":
    main()
