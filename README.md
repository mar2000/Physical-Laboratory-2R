# L10 — Efekt fotoakustyczny w gazach i cieczach

Repozytorium zawiera dane pomiarowe, skrypty analityczne, instrukcję oraz raport z doświadczenia dotyczącego efektu fotoakustycznego. W doświadczeniu badano zależność amplitudy sygnału fotoakustycznego od częstotliwości modulacji wiązki lasera oraz od właściwości badanego ośrodka.

## Zawartość repozytorium

```text
L10_efekt_fotoakustyczny_repo/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── powietrze_helmholtz.csv
│   │   ├── tlenki_azotu_ozon_helmholtz.csv
│   │   ├── rodamina_metanol.csv
│   │   └── rodamina_stezenia.csv
│   └── processed/
├── scripts/
│   ├── resonance_model.py
│   ├── analyze_harmonics.py
│   ├── analyze_concentration.py
│   ├── analyze_concentration_original.py
│   └── run_all.py
├── plots/
├── docs/
│   └── L10_instrukcja.pdf
└── report/
    └── Pracownia2R.pdf
```

## Dane pomiarowe

Pliki w `data/raw/` zawierają surowe dane pomiarowe przepisane do formatu CSV.

| Plik | Zawartość |
|---|---|
| `powietrze_helmholtz.csv` | Rezonanse w komorze Helmholtza wypełnionej powietrzem. |
| `tlenki_azotu_ozon_helmholtz.csv` | Rezonanse w komorze Helmholtza po wprowadzeniu mieszaniny zawierającej tlenki azotu i ozon. |
| `rodamina_metanol.csv` | Rezonanse w rurce wypełnionej roztworem rodaminy w metanolu. |
| `rodamina_stezenia.csv` | Pomiary pierwszego rezonansu dla kolejnych rozcieńczeń rodaminy. |

Dane dla serii rezonansowych mają kolumny:

```text
seria, opis_serii, harmoniczna, czestotliwosc_Hz, amplituda
```

Dane dla stężeń mają kolumny:

```text
stezenie_label, stezenie_wzgledne, czestotliwosc_Hz, amplituda
```

## Model dopasowania

Do analizy maksimów rezonansowych użyto funkcji

```text
A(f) = A0 * (G^2 * 4π^2 * f^2) / (((2πf)^2 - (2πf0)^2)^2 + G^2 * 4π^2 * f^2) + T
```

gdzie `A0` jest parametrem skali amplitudy, `f0` częstotliwością rezonansową, `G` parametrem związanym z tłumieniem i szerokością rezonansu, a `T` tłem pomiarowym.

## Uruchomienie analizy

1. Utwórz środowisko i zainstaluj zależności:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

2. Uruchom całą analizę:

```bash
python scripts/run_all.py
```

Wyniki zostaną zapisane do:

```text
data/processed/
plots/
```

Można też uruchamiać pojedyncze analizy:

```bash
python scripts/analyze_harmonics.py data/raw/powietrze_helmholtz.csv powietrze_helmholtz
python scripts/analyze_harmonics.py data/raw/tlenki_azotu_ozon_helmholtz.csv tlenki_azotu_ozon_helmholtz
python scripts/analyze_harmonics.py data/raw/rodamina_metanol.csv rodamina_metanol
python scripts/analyze_concentration.py data/raw/rodamina_stezenia.csv rodamina_stezenia
```

## Wyniki generowane przez skrypty

Dla serii harmonicznych skrypt zapisuje:

```text
data/processed/<nazwa>_fit_results.csv
data/processed/<nazwa>_frequency_ratios.txt
plots/<nazwa>_harmoniczne.png
```

Dla serii stężeń skrypt zapisuje:

```text
data/processed/rodamina_stezenia_fit_results.csv
data/processed/rodamina_stezenia_correlations.txt
plots/rodamina_stezenia_krzywe.png
plots/rodamina_stezenia_amax_vs_stezenie.png
plots/rodamina_stezenia_f0_vs_stezenie.png
plots/rodamina_stezenia_A0_vs_stezenie.png
```

## Dokumenty

- `docs/L10_instrukcja.pdf` — instrukcja do ćwiczenia.
- `report/Pracownia2R.pdf` — raport końcowy.

## Uwagi

Nazwy plików są opisowe, a nie tylko numerowane, żeby repozytorium było czytelne po czasie. W raporcie serie odpowiadają kolejno: powietrzu w komorze Helmholtza, mieszaninie zawierającej tlenki azotu i ozon, roztworowi rodaminy w metanolu oraz rozcieńczeniom rodaminy.
