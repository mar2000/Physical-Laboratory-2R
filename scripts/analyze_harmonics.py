"""Analiza danych rezonansowych dla serii z kolejnymi harmonicznymi.

Przykład:
    python scripts/analyze_harmonics.py data/raw/powietrze_helmholtz.csv powietrze_helmholtz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from resonance_model import fit_resonance_data, resonance_curve, r_squared


def analyze_harmonics(input_csv: Path, output_name: str, plots_dir: Path, processed_dir: Path):
    df = pd.read_csv(input_csv)
    required = {"harmoniczna", "czestotliwosc_Hz", "amplituda"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Brak wymaganych kolumn w {input_csv}: {sorted(missing)}")

    plots_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    results = []
    plt.figure(figsize=(12, 7))

    for harmonic, group in df.groupby("harmoniczna"):
        group = group.sort_values("czestotliwosc_Hz")
        x = group["czestotliwosc_Hz"].to_numpy(float)
        y = group["amplituda"].to_numpy(float)

        try:
            popt, perr, _ = fit_resonance_data(x, y)
        except Exception as exc:
            print(f"Nie udało się dopasować harmonicznej {harmonic}: {exc}")
            continue

        y_pred = resonance_curve(x, *popt)
        r2 = r_squared(y, y_pred)
        q_factor = popt[1] / popt[2] if popt[2] != 0 else np.nan

        results.append({
            "harmoniczna": int(harmonic),
            "A0": popt[0],
            "A0_err": perr[0],
            "f0_Hz": popt[1],
            "f0_err_Hz": perr[1],
            "G_Hz": popt[2],
            "G_err_Hz": perr[2],
            "T": popt[3],
            "T_err": perr[3],
            "Q_f0_over_G": q_factor,
            "R2": r2,
            "Amax_pomiar": float(np.max(y)),
            "f_Amax_pomiar_Hz": float(x[np.argmax(y)]),
        })

        plt.scatter(x, y, s=28, alpha=0.75, label=f"{int(harmonic)}. harm. — dane")
        x_fit = np.linspace(np.min(x), np.max(x), 1000)
        y_fit = resonance_curve(x_fit, *popt)
        plt.plot(x_fit, y_fit, linewidth=1.8, label=f"{int(harmonic)}. harm. — dopasowanie")
        plt.axvline(popt[1], linestyle="--", linewidth=1, alpha=0.55)

    if not results:
        raise RuntimeError(f"Nie uzyskano żadnego poprawnego dopasowania dla {input_csv}")

    results_df = pd.DataFrame(results).sort_values("harmoniczna")
    first_f0 = results_df.iloc[0]["f0_Hz"]
    results_df["stosunek_f0_do_pierwszej"] = results_df["f0_Hz"] / first_f0
    results_path = processed_dir / f"{output_name}_fit_results.csv"
    results_df.to_csv(results_path, index=False)

    plt.xlabel("Częstotliwość [Hz]")
    plt.ylabel("Amplituda")
    plt.title(f"Krzywe rezonansowe — {output_name}")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plot_path = plots_dir / f"{output_name}_harmoniczne.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()

    ratios_path = processed_dir / f"{output_name}_frequency_ratios.txt"
    with ratios_path.open("w", encoding="utf-8") as f:
        f.write(f"Stosunki częstotliwości rezonansowych dla {output_name}\n")
        f.write("================================================\n")
        for _, row in results_df.iterrows():
            f.write(
                f"h={int(row['harmoniczna'])}: f0 = {row['f0_Hz']:.2f} Hz, "
                f"f0/f1 = {row['stosunek_f0_do_pierwszej']:.3f}\n"
            )

    print(f"Zapisano: {results_path}")
    print(f"Zapisano: {plot_path}")
    print(f"Zapisano: {ratios_path}")
    return results_df


def main():
    parser = argparse.ArgumentParser(description="Dopasowanie krzywych rezonansowych do danych harmonicznych.")
    parser.add_argument("input_csv", type=Path, help="Plik CSV z kolumnami: harmoniczna, czestotliwosc_Hz, amplituda")
    parser.add_argument("output_name", help="Nazwa używana w plikach wynikowych")
    parser.add_argument("--plots-dir", type=Path, default=Path("plots"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    analyze_harmonics(args.input_csv, args.output_name, args.plots_dir, args.processed_dir)


if __name__ == "__main__":
    main()
