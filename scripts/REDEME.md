# Skrypty do analizy danych

Ten katalog zawiera skrypty użyte do opracowania danych pomiarowych z doświadczenia **L10 — Efekt fotoakustyczny w gazach i cieczach**.

Celem skryptów jest odtworzenie analizy przedstawionej w raporcie: dopasowanie krzywych rezonansowych do danych pomiarowych, wyznaczenie częstości rezonansowych, parametrów szerokości rezonansu, tła pomiarowego oraz przygotowanie wykresów i tabel wynikowych.

W doświadczeniu badano sygnał fotoakustyczny powstający w ośrodku oświetlanym modulowaną wiązką lasera. Mierzono amplitudę sygnału fotoakustycznego w funkcji częstotliwości modulacji. W pobliżu częstości rezonansowych układu obserwowano wzrost amplitudy. Do opisu tych maksimów wykorzystano model krzywej rezonansowej odpowiadający oscylatorowi tłumionemu z wymuszeniem periodycznym.

Skrypty zostały uporządkowane tak, aby dane pomiarowe nie były wpisane bezpośrednio w kodzie. Dane znajdują się w katalogu `data/raw/`, natomiast skrypty wczytują je z plików CSV, wykonują analizę i zapisują wyniki do katalogów `data/processed/` oraz `plots/`.

---

## Zawartość katalogu

W katalogu `scripts/` znajdują się trzy główne pliki:

```text
scripts/
├── resonance_model.py
├── analyze_harmonics.py
└── analyze_concentration.py
```

Każdy z nich pełni inną funkcję:

* `resonance_model.py` zawiera wspólne funkcje matematyczne używane w analizie,
* `analyze_harmonics.py` analizuje serie pomiarowe z kolejnymi rezonansami,
* `analyze_concentration.py` analizuje wpływ stężenia rodaminy na sygnał fotoakustyczny.

Taki podział pozwala uniknąć powtarzania tych samych funkcji w kilku plikach. W pierwotnych wersjach kodów funkcja krzywej rezonansowej i funkcja dopasowania pojawiały się osobno w każdym skrypcie. W repozytorium zostały one przeniesione do jednego wspólnego pliku `resonance_model.py`.

---

# 1. Plik `resonance_model.py`

Plik `resonance_model.py` zawiera funkcje wspólne dla wszystkich analiz. Nie jest to skrypt przeznaczony do samodzielnego uruchamiania. Jego zadaniem jest dostarczenie funkcji używanych przez pozostałe programy.

W tym pliku znajduje się definicja krzywej rezonansowej oraz funkcje pomocnicze związane z dopasowaniem danych.

---

## Funkcja `resonance_curve`

Najważniejszą funkcją w tym pliku jest:

```python
resonance_curve(f, A0, f0, G, T)
```

Funkcja ta opisuje zależność amplitudy sygnału fotoakustycznego od częstotliwości modulacji lasera. Ma postać:

```text
A(f) = A0 * (G^2 * 4π^2 * f^2) /
       [((2πf)^2 - (2πf0)^2)^2 + G^2 * 4π^2 * f^2] + T
```

Parametry funkcji mają następujące znaczenie:

* `f` — częstotliwość modulacji lasera,
* `A0` — parametr skali amplitudy,
* `f0` — częstotliwość rezonansowa,
* `G` — parametr związany z szerokością rezonansu i tłumieniem,
* `T` — tło pomiarowe.

Funkcja ta jest używana do dopasowania modelu do danych pomiarowych. Dla każdej serii danych szukane są takie wartości parametrów `A0`, `f0`, `G` i `T`, aby krzywa możliwie dobrze przechodziła przez punkty pomiarowe.

Najważniejszym parametrem z punktu widzenia interpretacji fizycznej jest `f0`, ponieważ określa położenie maksimum rezonansowego. Parametr `G` informuje o szerokości rezonansu, a więc pośrednio o tłumieniu odpowiedzi układu. Parametr `T` opisuje tło, czyli wartość amplitudy niezwiązaną bezpośrednio z samym maksimum rezonansowym.

---

## Funkcja `fit_resonance_data`

Druga ważna funkcja to:

```python
fit_resonance_data(x, y)
```

Funkcja ta dopasowuje krzywą rezonansową do danych pomiarowych.

Argumenty:

* `x` — tablica częstotliwości pomiarowych,
* `y` — tablica zmierzonych amplitud.

Funkcja korzysta z procedury `curve_fit` z biblioteki `scipy.optimize`. Dopasowanie odbywa się metodą najmniejszych kwadratów, czyli program szuka takich parametrów modelu, aby suma kwadratów różnic między wartościami zmierzonymi a wartościami obliczonymi z modelu była jak najmniejsza.

Przybliżenia początkowe parametrów są wybierane automatycznie:

* jako początkowe `f0` przyjmowana jest częstotliwość, dla której zmierzono największą amplitudę,
* jako początkowe `A0` przyjmowana jest różnica między największą i najmniejszą amplitudą,
* jako początkowe `G` przyjmowana jest część szerokości badanego zakresu częstotliwości,
* jako początkowe `T` przyjmowana jest najmniejsza zmierzona amplituda.

Dzięki temu skrypt można stosować do różnych serii pomiarowych bez ręcznego ustawiania parametrów startowych.

Funkcja zwraca:

* dopasowane parametry,
* niepewności parametrów wynikające z macierzy kowariancji,
* informację o jakości dopasowania.

---

## Funkcja `calculate_r_squared`

W pliku znajduje się także funkcja obliczająca współczynnik determinacji:

```python
calculate_r_squared(y, y_fit)
```

Współczynnik `R²` służy do oceny jakości dopasowania. Im bliżej wartości `1`, tym lepiej krzywa modelowa opisuje dane pomiarowe.

W analizie doświadczenia `R²` jest traktowane jako pomocnicza miara jakości dopasowania. Wysoka wartość `R²` oznacza, że funkcja rezonansowa dobrze odtwarza kształt danych, ale nie oznacza automatycznie, że model idealnie opisuje cały rzeczywisty układ fizyczny. Układ doświadczalny może być zaburzony przez szumy akustyczne, niedoskonałe warunki brzegowe, niestabilność mocy lasera lub geometrię ustawienia wiązki.

---

# 2. Plik `analyze_harmonics.py`

Plik `analyze_harmonics.py` służy do analizy danych, w których badano zależność amplitudy sygnału fotoakustycznego od częstotliwości modulacji dla kilku kolejnych rezonansów.

Ten skrypt odpowiada za analizę trzech głównych serii pomiarowych:

```text
data/raw/powietrze_helmholtz.csv
data/raw/tlenki_azotu_ozon_helmholtz.csv
data/raw/rodamina_metanol.csv
```

Są to odpowiednio:

1. pomiary dla powietrza w komorze Helmholtza,
2. pomiary dla mieszaniny zawierającej tlenki azotu i ozon w komorze Helmholtza,
3. pomiary dla roztworu rodaminy w metanolu w szklanej rurce.

W każdym z tych przypadków dane zawierają kilka obserwowanych maksimów rezonansowych. W plikach CSV kolejne maksima oznaczone są numerem w kolumnie `harmoniczna`. Nazwa tej kolumny została zachowana ze względów technicznych, ale fizycznie wartości te należy interpretować ostrożnie jako kolejne obserwowane rezonanse lub mody układu, a niekoniecznie jako idealne harmoniczne.

---

## Format danych wejściowych

Skrypt oczekuje pliku CSV o następującej strukturze:

```csv
harmoniczna,czestotliwosc_Hz,amplituda
1,1500,0.49
1,1550,0.96
1,1600,1.02
2,3500,0.866
2,3550,0.992
3,5000,0.64
```

Znaczenie kolumn:

* `harmoniczna` — numer obserwowanego rezonansu,
* `czestotliwosc_Hz` — częstotliwość modulacji lasera w hercach,
* `amplituda` — zmierzona amplituda sygnału fotoakustycznego.

Dane dla różnych rezonansów znajdują się w jednym pliku, a skrypt sam dzieli je na grupy według kolumny `harmoniczna`.

---

## Co robi skrypt krok po kroku?

Skrypt wykonuje następujące operacje:

1. Wczytuje dane z pliku CSV podanego jako argument.
2. Sprawdza, jakie numery rezonansów znajdują się w kolumnie `harmoniczna`.
3. Dzieli dane na osobne serie pomiarowe.
4. Dla każdej serii dopasowuje krzywą rezonansową.
5. Wyznacza parametry `A0`, `f0`, `G`, `T`.
6. Oblicza niepewności parametrów dopasowania.
7. Oblicza współczynnik `R²`.
8. Tworzy tabelę z wynikami.
9. Zapisuje tabelę wyników do katalogu `data/processed/`.
10. Rysuje zbiorczy wykres punktów pomiarowych i dopasowanych krzywych.
11. Zapisuje wykres do katalogu `plots/`.
12. Oblicza stosunki częstości rezonansowych względem pierwszego rezonansu.
13. Zapisuje te stosunki do osobnego pliku CSV.

Dzięki temu po jednym uruchomieniu otrzymuje się zarówno wykres, jak i tabelę parametrów potrzebną do raportu.

---

## Przykład uruchomienia

Z głównego katalogu repozytorium można uruchomić analizę powietrza w komorze Helmholtza:

```bash
python scripts/analyze_harmonics.py data/raw/powietrze_helmholtz.csv powietrze_helmholtz
```

Pierwszy argument to ścieżka do pliku z danymi, a drugi argument to nazwa serii pomiarowej. Ta nazwa jest używana przy zapisie wyników.

Po uruchomieniu powstaną pliki:

```text
data/processed/powietrze_helmholtz_fit_results.csv
data/processed/powietrze_helmholtz_frequency_ratios.csv
plots/powietrze_helmholtz_harmonics.png
```

Analogicznie można uruchomić analizę dla pozostałych danych:

```bash
python scripts/analyze_harmonics.py data/raw/tlenki_azotu_ozon_helmholtz.csv tlenki_azotu_ozon_helmholtz

python scripts/analyze_harmonics.py data/raw/rodamina_metanol.csv rodamina_metanol
```

---

## Plik wynikowy z parametrami dopasowania

Skrypt zapisuje tabelę wynikową w katalogu `data/processed/`.

Przykładowe kolumny w pliku wynikowym:

```csv
harmoniczna,A0,A0_err,f0_Hz,f0_err_Hz,G_Hz,G_err_Hz,T,T_err,R2,Q
```

Znaczenie kolumn:

* `harmoniczna` — numer analizowanego rezonansu,
* `A0` — dopasowany parametr skali amplitudy,
* `A0_err` — niepewność parametru `A0`,
* `f0_Hz` — dopasowana częstotliwość rezonansowa,
* `f0_err_Hz` — niepewność częstotliwości rezonansowej,
* `G_Hz` — dopasowany parametr szerokości rezonansu,
* `G_err_Hz` — niepewność parametru `G`,
* `T` — tło pomiarowe,
* `T_err` — niepewność tła,
* `R2` — współczynnik determinacji,
* `Q` — oszacowana dobroć rezonansu, liczona jako `Q = f0 / G`.

Wartość `Q` należy traktować jako parametr modelowy. Jest użyteczna do porównywania szerokości rezonansów, ale nie powinna być interpretowana jako bardzo dokładna dobroć idealnego rezonatora, ponieważ układ doświadczalny nie jest idealny.

---

## Plik ze stosunkami częstotliwości

Dodatkowo skrypt zapisuje plik:

```text
data/processed/<nazwa_serii>_frequency_ratios.csv
```

W tym pliku znajdują się stosunki częstotliwości kolejnych rezonansów względem pierwszego rezonansu, na przykład:

```csv
harmoniczna,f0_Hz,ratio_to_first
1,1927.08,1.000
2,4057.47,2.106
3,5561.85,2.886
```

Takie zestawienie pozwala sprawdzić, czy obserwowane rezonanse są bliskie idealnym stosunkom `1:2:3` albo `1:2:3:4`.

W rzeczywistym układzie nie należy oczekiwać idealnej zgodności. Odchylenia mogą wynikać z geometrii komory, warunków brzegowych, sprzężenia mikrofonu z układem, położenia wiązki oraz tłumienia.

---

## Wykres generowany przez skrypt

Skrypt tworzy wykres zbiorczy, na którym znajdują się:

* punkty pomiarowe dla każdego rezonansu,
* dopasowane krzywe rezonansowe,
* oznaczenia częstości rezonansowych `f0`.

Wykres jest zapisywany w katalogu `plots/`.

Przykładowy plik:

```text
plots/powietrze_helmholtz_harmonics.png
```

Wykres pozwala szybko ocenić, czy dopasowanie jest sensowne i czy krzywe dobrze opisują dane pomiarowe.

---

# 3. Plik `analyze_concentration.py`

Plik `analyze_concentration.py` służy do analizy danych z części doświadczenia, w której badano wpływ stężenia rodaminy na amplitudę sygnału fotoakustycznego.

W tej części doświadczenia roztwór rodaminy w metanolu był kolejno rozcieńczany. Dla każdego stężenia mierzono zależność amplitudy sygnału fotoakustycznego od częstotliwości modulacji w pobliżu pierwszego rezonansu.

Skrypt analizuje plik:

```text
data/raw/rodamina_stezenia.csv
```

---

## Format danych wejściowych

Plik z danymi powinien mieć strukturę:

```csv
stezenie_label,stezenie_wzgledne,czestotliwosc_Hz,amplituda
D,1.0,2200,4.8
D,1.0,2210,5.63
D/2,0.5,2270,2.824
D/2,0.5,2280,2.972
D/4,0.25,2200,4.17
```

Znaczenie kolumn:

* `stezenie_label` — oznaczenie stężenia, np. `D`, `D/2`, `D/4`,
* `stezenie_wzgledne` — względna wartość stężenia, np. `1.0`, `0.5`, `0.25`,
* `czestotliwosc_Hz` — częstotliwość modulacji lasera w hercach,
* `amplituda` — zmierzona amplituda sygnału fotoakustycznego.

Stężenie `D` oznacza stężenie początkowe, natomiast `D/2`, `D/4`, `D/8`, `D/16` i `D/32` oznaczają kolejne rozcieńczenia.

---

## Co robi skrypt krok po kroku?

Skrypt wykonuje następujące kroki:

1. Wczytuje dane z pliku `data/raw/rodamina_stezenia.csv`.
2. Dzieli dane na grupy według kolumny `stezenie_label`.
3. Dla każdego stężenia dopasowuje krzywą rezonansową.
4. Wyznacza parametry `A0`, `f0`, `G`, `T`.
5. Oblicza niepewności parametrów.
6. Oblicza współczynnik `R²`.
7. Wyznacza maksymalną zmierzoną amplitudę `Amax`.
8. Tworzy tabelę wynikową.
9. Zapisuje tabelę do katalogu `data/processed/`.
10. Rysuje krzywe rezonansowe dla wszystkich stężeń.
11. Rysuje wykresy podsumowujące zależności od stężenia.
12. Zapisuje wykresy do katalogu `plots/`.

---

## Przykład uruchomienia

Z głównego katalogu repozytorium należy uruchomić:

```bash
python scripts/analyze_concentration.py
```

Skrypt domyślnie wczytuje dane z pliku:

```text
data/raw/rodamina_stezenia.csv
```

Po uruchomieniu powstaną wyniki:

```text
data/processed/rodamina_stezenia_fit_results.csv
plots/rodamina_stezenia_resonance_curves.png
plots/rodamina_stezenia_summary.png
```

---

## Plik wynikowy z analizy stężeń

Tabela wynikowa zawiera parametry dopasowania dla każdego stężenia.

Przykładowe kolumny:

```csv
stezenie_label,stezenie_wzgledne,Amax,A0,A0_err,f0_Hz,f0_err_Hz,G_Hz,G_err_Hz,T,T_err,R2
```

Znaczenie kolumn:

* `stezenie_label` — oznaczenie stężenia,
* `stezenie_wzgledne` — względne stężenie rodaminy,
* `Amax` — największa zmierzona amplituda w danej serii,
* `A0` — parametr amplitudy z dopasowania,
* `A0_err` — niepewność parametru `A0`,
* `f0_Hz` — częstotliwość rezonansowa,
* `f0_err_Hz` — niepewność częstotliwości rezonansowej,
* `G_Hz` — parametr szerokości rezonansu,
* `G_err_Hz` — niepewność parametru `G`,
* `T` — tło pomiarowe,
* `T_err` — niepewność tła,
* `R2` — współczynnik determinacji.

W tej części analizy szczególnie ważne są `Amax`, `A0` oraz `f0_Hz`.

---

## Wykres krzywych rezonansowych

Pierwszy wykres generowany przez skrypt przedstawia krzywe rezonansowe dla wszystkich stężeń rodaminy.

Na wykresie znajdują się:

* punkty pomiarowe dla każdego rozcieńczenia,
* dopasowane krzywe rezonansowe,
* legenda z oznaczeniami stężeń.

Ten wykres pozwala porównać kształt i wysokość maksimów dla kolejnych rozcieńczeń. W idealnym przypadku zmniejszenie stężenia absorbenta powinno prowadzić do zmniejszenia amplitudy sygnału fotoakustycznego, ponieważ mniej energii promieniowania jest pochłaniane przez próbkę.

W praktyce zależność może nie być idealnie liniowa. Na amplitudę wpływają również ustawienie wiązki, położenie źródła ciepła względem modu akustycznego, sprzężenie z mikrofonem, tło akustyczne oraz stabilność mocy lasera.

---

## Wykresy podsumowujące

Drugi plik graficzny zawiera wykresy podsumowujące, na przykład:

1. maksymalna amplituda w funkcji stężenia,
2. częstotliwość rezonansowa `f0` w funkcji stężenia,
3. parametr `A0` w funkcji stężenia.

Oś stężenia jest zwykle przedstawiona w skali logarytmicznej, ponieważ kolejne stężenia różnią się czynnikami `2`.

Interpretacja tych wykresów powinna być ostrożna. Celem tej części doświadczenia jest głównie jakościowe sprawdzenie, czy zmiana stężenia absorbenta wpływa na sygnał fotoakustyczny. Nie należy traktować otrzymanej zależności jako dokładnego pomiaru współczynnika absorpcji, ponieważ układ nie był kalibrowany w taki sposób.

---

# Wymagane biblioteki

Do uruchomienia skryptów potrzebne są następujące biblioteki Pythona:

```text
numpy
pandas
matplotlib
scipy
```

Są one zapisane w pliku `requirements.txt` w głównym katalogu repozytorium.

Aby zainstalować wymagane pakiety, należy przejść do głównego katalogu repozytorium i uruchomić:

```bash
pip install -r requirements.txt
```

---

# Zalecana kolejność uruchamiania

Po zainstalowaniu bibliotek można odtworzyć analizę w następującej kolejności:

```bash
python scripts/analyze_harmonics.py data/raw/powietrze_helmholtz.csv powietrze_helmholtz

python scripts/analyze_harmonics.py data/raw/tlenki_azotu_ozon_helmholtz.csv tlenki_azotu_ozon_helmholtz

python scripts/analyze_harmonics.py data/raw/rodamina_metanol.csv rodamina_metanol

python scripts/analyze_concentration.py
```

Po wykonaniu tych poleceń powinny zostać utworzone pliki wynikowe w katalogach:

```text
data/processed/
plots/
```

---

# Jak czytać wyniki?

Najważniejsze wyniki znajdują się w plikach CSV w katalogu `data/processed/`.

Dla serii rezonansowych najważniejszy jest parametr:

```text
f0_Hz
```

czyli dopasowana częstotliwość rezonansowa.

Warto też zwrócić uwagę na:

```text
G_Hz
```

czyli parametr szerokości rezonansu, oraz:

```text
R2
```

czyli jakość dopasowania.

Dla analizy stężeń najważniejsze są:

```text
stezenie_wzgledne
Amax
A0
f0_Hz
```

Pozwalają one sprawdzić, jak zmienia się wysokość maksimum oraz położenie rezonansu przy kolejnych rozcieńczeniach roztworu.

---

# Uwagi dotyczące interpretacji

Dopasowana krzywa rezonansowa jest modelem przybliżonym. Dobrze opisuje lokalny kształt obserwowanych maksimów, ale nie uwzględnia wszystkich szczegółów rzeczywistego układu pomiarowego.

Na wyniki mogą wpływać między innymi:

* zakłócenia akustyczne z otoczenia,
* szumy elektryczne,
* niestabilność mocy lasera,
* niedokładność ustawienia wiązki,
* położenie mikrofonu,
* geometria komory lub rurki,
* nieidealne warunki brzegowe,
* zmiana sprzężenia między źródłem ciepła a modem akustycznym.

Dlatego dopasowane częstotliwości rezonansowe i parametry amplitudowe należy interpretować jako charakterystyki rzeczywistego układu doświadczalnego, a nie idealnego rezonatora.

Szczególnie ostrożnie należy interpretować słowo „harmoniczna”. W skryptach kolumna `harmoniczna` oznacza numer kolejnego obserwowanego maksimum. Nie zawsze oznacza to idealną harmoniczną w sensie matematycznym. W raporcie obserwowane maksima są traktowane jako rezonanse rzeczywistego układu, których stosunki częstotliwości mogą odbiegać od idealnych wartości `1:2:3` lub `1:2:3:4`.

---

# Związek skryptów z raportem

Skrypty odpowiadają analizie opisanej w raporcie:

* `analyze_harmonics.py` odtwarza analizę rezonansów w powietrzu, w mieszaninie gazów oraz w roztworze rodaminy,
* `analyze_concentration.py` odtwarza analizę wpływu stężenia rodaminy na sygnał fotoakustyczny,
* `resonance_model.py` zawiera model matematyczny użyty w dopasowaniach.

Wygenerowane przez skrypty tabele i wykresy mogą służyć do sprawdzenia wyników liczbowych oraz do ponownego wykonania analizy w przypadku zmiany danych wejściowych.
