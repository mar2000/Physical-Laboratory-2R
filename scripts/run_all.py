"""Uruchamia całą analizę dla repozytorium L10."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "scripts/analyze_harmonics.py", "data/raw/powietrze_helmholtz.csv", "powietrze_helmholtz"],
    [sys.executable, "scripts/analyze_harmonics.py", "data/raw/tlenki_azotu_ozon_helmholtz.csv", "tlenki_azotu_ozon_helmholtz"],
    [sys.executable, "scripts/analyze_harmonics.py", "data/raw/rodamina_metanol.csv", "rodamina_metanol"],
    [sys.executable, "scripts/analyze_concentration.py", "data/raw/rodamina_stezenia.csv", "rodamina_stezenia"],
]

for command in COMMANDS:
    print("\n$ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)
