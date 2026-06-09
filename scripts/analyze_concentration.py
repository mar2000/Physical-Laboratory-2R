"""Analiza zależności sygnału fotoakustycznego od stężenia rodaminy.

Przykład:
    python scripts/analyze_concentration.py data/raw/rodamina_stezenia.csv rodamina_stezenia
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


def analyze_concentration(input_csv: Path, output_name: str, plots_dir: Path, processed_dir: Path):
    df = pd.read_csv(input_csv)
    required = {"stezenie_label", "stezenie_wzgledne", "czestotliwosc_Hz", "amplituda"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Brak wymaganych kolumn w {input_csv}: {sorted(missing)}")

    plots_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    results = []
    plt.figure(figsize=(12, 7))

    for label, group in df.groupby("stezenie_label", sort=False):
        group = group.sort_values("czestotliwosc_Hz")
        x = group["czestotliwosc_Hz"].to_numpy(float)
        y = group["amplituda"].to_numpy(float)
        c = float(group["stezenie_wzgledne"].iloc[0])

        try:
            popt, perr, _ = fit_resonance_data(x, y)
        except Exception as exc:
            print(f"Nie udało się dopasować stężenia {label}: {exc}")
            continue

        y_pred = resonance_curve(x, *popt)
        r2 = r_squared(y, y_pred)
        results.append({
            "stezenie_label": label,
            "stezenie_wzgledne": c,
            "A0": popt[0],
            "A0_err": perr[0],
            "f0_Hz": popt[1],
            "f0_err_Hz": perr[1],
            "G_Hz": popt[2],
            "G_err_Hz": perr[2],
            "T": popt[3],
            "T_err": perr[3],
            "Q_f0_over_G": popt[1] / popt[2] if popt[2] != 0 else np.nan,
            "R2": r2,
            "Amax_pomiar": float(np.max(y)),
            "f_Amax_pomiar_Hz": float(x[np.argmax(y)]),
        })

        plt.scatter(x, y, s=28, alpha=0.75, label=f"{label} — dane")
        x_fit = np.linspace(np.min(x), np.max(x), 800)
        y_fit = resonance_curve(x_fit, *popt)
        plt.plot(x_fit, y_fit, linewidth=1.8, label=f"{label} — dopasowanie")

    if not results:
        raise RuntimeError(f"Nie uzyskano żadnego poprawnego dopasowania dla {input_csv}")

    results_df = pd.DataFrame(results).sort_values("stezenie_wzgledne")
    results_path = processed_dir / f"{output_name}_fit_results.csv"
    results_df.to_csv(results_path, index=False)

    plt.xlabel("Częstotliwość [Hz]")
    plt.ylabel("Amplituda")
    plt.title("Krzywe rezonansowe dla różnych stężeń rodaminy")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    curves_path = plots_dir / f"{output_name}_krzywe.png"
    plt.savefig(curves_path, dpi=200)
    plt.close()

    # Wykresy podsumowujące.
    for column, ylabel, suffix in [
        ("Amax_pomiar", "Maksymalna amplituda", "amax_vs_stezenie"),
        ("f0_Hz", "Częstotliwość rezonansowa f0 [Hz]", "f0_vs_stezenie"),
        ("A0", "Parametr A0", "A0_vs_stezenie"),
    ]:
        plt.figure(figsize=(7, 5))
        plt.plot(results_df["stezenie_wzgledne"], results_df[column], marker="o", linewidth=1.8)
        plt.xscale("log")
        plt.xlabel("Stężenie względne")
        plt.ylabel(ylabel)
        plt.title(ylabel + " od stężenia")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        path = plots_dir / f"{output_name}_{suffix}.png"
        plt.savefig(path, dpi=200)
        plt.close()
        print(f"Zapisano: {path}")

    summary_path = processed_dir / f"{output_name}_correlations.txt"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(f"Podsumowanie zależności od stężenia dla {output_name}\n")
        f.write("================================================\n")
        log_c = np.log(results_df["stezenie_wzgledne"].to_numpy(float))
        for column in ["Amax_pomiar", "f0_Hz", "A0"]:
            corr = np.corrcoef(log_c, results_df[column].to_numpy(float))[0, 1]
            f.write(f"Korelacja log(stężenia) — {column}: {corr:.4f}\n")

    print(f"Zapisano: {results_path}")
    print(f"Zapisano: {curves_path}")
    print(f"Zapisano: {summary_path}")
    return results_df


def main():
    parser = argparse.ArgumentParser(description="Analiza zależności sygnału od stężenia rodaminy.")
    parser.add_argument("input_csv", type=Path, help="Plik CSV z danymi stężeń")
    parser.add_argument("output_name", help="Nazwa używana w plikach wynikowych")
    parser.add_argument("--plots-dir", type=Path, default=Path("plots"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    analyze_concentration(args.input_csv, args.output_name, args.plots_dir, args.processed_dir)


if __name__ == "__main__":
    main()
