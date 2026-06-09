import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.cm import get_cmap

def resonance_curve(f, A0, f0, G, T):
    """
    Krzywa rezonansowa zgodnie z podanym wzorem
    """
    omega = 2 * np.pi * f
    omega0 = 2 * np.pi * f0

    numerator = A0 * (G**2 * 4 * np.pi**2 * f**2)
    denominator = ((omega**2 - omega0**2)**2 + G**2 * 4 * np.pi**2 * f**2)

    return numerator / denominator + T

def fit_resonance_data(x, y, initial_guess=None):
    """Dopasowuje krzywą rezonansową do danych"""
    if initial_guess is None:
        A0_guess = np.max(y) - np.min(y)
        f0_guess = x[np.argmax(y)]
        G_guess = (np.max(x) - np.min(x)) / 10
        T_guess = np.min(y)
        initial_guess = [A0_guess, f0_guess, G_guess, T_guess]

    try:
        popt, pcov = curve_fit(resonance_curve, x, y, p0=initial_guess, maxfev=5000)
        perr = np.sqrt(np.diag(pcov))
        return popt, perr
    except Exception as e:
        print(f"Błąd podczas dopasowania: {e}")
        return None, None

def plot_concentration_series(concentration_data):
    """Rysuje serie krzywych dla różnych stężeń"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    # Kolorowa mapa dla stężeń
    colors = get_cmap('viridis')(np.linspace(0, 1, len(concentration_data)))

    # Wykres 1: Wszystkie krzywe na jednym wykresie
    ax1 = axes[0]
    for i, (label, data) in enumerate(concentration_data.items()):
        x, y = data['x'], data['y']
        popt = data['popt']

        # Punkty pomiarowe
        ax1.scatter(x, y, color=colors[i], alpha=0.6, s=40, label=label)

        # Krzywa dopasowana
        x_fit = np.linspace(min(x), max(x), 500)
        y_fit = resonance_curve(x_fit, *popt)
        ax1.plot(x_fit, y_fit, color=colors[i], linewidth=2, alpha=0.8)

    ax1.set_xlabel('Częstotliwość [Hz]', fontsize=12)
    ax1.set_ylabel('Amplituda', fontsize=12)
    ax1.set_title('Krzywe rezonansowe dla różnych stężeń barwnika', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10, loc='upper right')
    ax1.set_ylim(bottom=0)

    # Wykres 2: Maksymalna amplituda vs stężenie
    ax2 = axes[1]
    concentrations = []
    max_amplitudes = []
    f0_values = []
    A0_values = []

    for label, data in concentration_data.items():
        popt = data['popt']
        concentrations.append(data['concentration_value'])
        max_amplitudes.append(np.max(data['y']))
        f0_values.append(popt[1])
        A0_values.append(popt[0])

    # Sortowanie według stężenia
    sort_idx = np.argsort(concentrations)
    concentrations = np.array(concentrations)[sort_idx]
    max_amplitudes = np.array(max_amplitudes)[sort_idx]
    f0_values = np.array(f0_values)[sort_idx]
    A0_values = np.array(A0_values)[sort_idx]

    ax2.plot(concentrations, max_amplitudes, 'o', linewidth=2, markersize=8,
             color='darkred', label='Maksymalna amplituda')
    ax2.set_xlabel('Stężenie (względne)', fontsize=12)
    ax2.set_ylabel('Maksymalna amplituda', fontsize=12)
    ax2.set_title('Zależność maksymalnej amplitudy od stężenia', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.legend()

    # Wykres 3: Częstotliwość rezonansowa vs stężenie
    ax3 = axes[2]
    ax3.plot(concentrations, f0_values, 's', linewidth=2, markersize=8,
             color='darkblue', label='Częstotliwość rezonansowa (f₀)')
    ax3.set_xlabel('Stężenie (względne)', fontsize=12)
    ax3.set_ylabel('Częstotliwość rezonansowa [Hz]', fontsize=12)
    ax3.set_title('Zależność częstotliwości rezonansowej od stężenia', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    ax3.legend()

    # Wykres 4: Parametr A₀ vs stężenie
    ax4 = axes[3]
    ax4.plot(concentrations, A0_values, '^', linewidth=2, markersize=8,
             color='darkgreen', label='Parametr A₀ z dopasowania')
    ax4.set_xlabel('Stężenie (względne)', fontsize=12)
    ax4.set_ylabel('Parametr A₀', fontsize=12)
    ax4.set_title('Zależność parametru A₀ od stężenia', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.set_xscale('log')
    ax4.legend()

    plt.tight_layout()
    plt.show()

    return {
        'concentrations': concentrations,
        'max_amplitudes': max_amplitudes,
        'f0_values': f0_values,
        'A0_values': A0_values
    }

def plot_summary_statistics(results):
    """Rysuje podsumowanie statystyk"""
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))

    concentrations = results['concentrations']
    max_amps = results['max_amplitudes']
    f0_vals = results['f0_values']
    A0_vals = results['A0_values']

    # Normalizacja do najwyższej wartości
    norm_max_amps = max_amps / np.max(max_amps)
    norm_A0_vals = A0_vals / np.max(A0_vals)

    # Wykres znormalizowany
    ax[0].plot(concentrations, norm_max_amps, 'o', label='Maks. amplituda (znormalizowana)',
               linewidth=2, markersize=8)
    ax[0].plot(concentrations, norm_A0_vals, 's', label='A₀ (znormalizowany)',
               linewidth=2, markersize=8)
    ax[0].set_xlabel('Stężenie (względne)', fontsize=12)
    ax[0].set_ylabel('Wartość znormalizowana', fontsize=12)
    ax[0].set_title('Znormalizowane parametry vs stężenie', fontsize=14, fontweight='bold')
    ax[0].grid(True, alpha=0.3)
    ax[0].set_xscale('log')
    ax[0].legend()

    # Wykres stosunku A₀ do maksymalnej amplitudy
    ax[1].plot(concentrations, A0_vals / max_amps, '^', color='purple',
               linewidth=2, markersize=8)
    ax[1].set_xlabel('Stężenie (względne)', fontsize=12)
    ax[1].set_ylabel('Stosunek A₀ / Amax', fontsize=12)
    ax[1].set_title('Stosunek parametru A₀ do maksymalnej amplitudy', fontsize=14, fontweight='bold')
    ax[1].grid(True, alpha=0.3)
    ax[1].set_xscale('log')

    # Wykres przesunięcia częstotliwości
    f0_shift = f0_vals - f0_vals[0]  # przesunięcie względem najwyższego stężenia
    ax[2].plot(concentrations, f0_shift, 'D', color='orange',
               linewidth=2, markersize=8)
    ax[2].set_xlabel('Stężenie (względne)', fontsize=12)
    ax[2].set_ylabel('Δf₀ [Hz]', fontsize=12)
    ax[2].set_title('Przesunięcie częstotliwości rezonansowej', fontsize=14, fontweight='bold')
    ax[2].grid(True, alpha=0.3)
    ax[2].set_xscale('log')

    plt.tight_layout()
    plt.show()

# Dane dla różnych stężeń
concentration_data = {
    'D': {
        'x': np.array([2200, 2210, 2220, 2230, 2240, 2250, 2260, 2270, 2280, 2290, 2300,
                       2310, 2320, 2330, 2340, 2350, 2360, 2370, 2380, 2390, 2400]),
        'y': np.array([4.8, 5.63, 6.16, 6.68, 7.36, 8.21, 9.32, 10.72, 12.57, 14.98, 17.67,
                       20.31, 21.25, 19.18, 16.84, 13.72, 11.3, 9.47, 8.09, 6.98, 6.18]),
        'concentration_value': 1.0  # D
    },
    'D/2': {
        'x': np.array([2270, 2280, 2290, 2300, 2310, 2320, 2330, 2340, 2350, 2360, 2370,
                       2380, 2390, 2400, 2410, 2420, 2430, 2440, 2450, 2460, 2470, 2480, 2490, 2500]),
        'y': np.array([2.824, 2.972, 3.184, 3.464, 3.732, 4.088, 4.54, 5.052, 5.736, 6.624, 7.812,
                       9.484, 11.92, 15.656, 19.612, 17.536, 13.616, 8.44, 7.08, 5.992, 5.236, 4.592, 4.044, 3.736]),
        'concentration_value': 0.5  # D/2
    },
    'D/4': {
        'x': np.array([2200, 2210, 2220, 2230, 2240, 2250, 2260, 2270, 2280, 2290, 2300,
                       2310, 2320, 2330, 2340, 2350, 2360, 2370, 2380, 2390, 2400,
                       2410, 2420, 2430, 2440]),
        'y': np.array([4.17, 4.46, 4.75, 5.15, 5.57, 6.43, 6.73, 7.5, 8.49, 9.77, 11.25,
                       13.23, 15.47, 17.69, 18.67, 17.1, 15.41, 12.6, 10.9, 9.09, 7.76,
                       6.75, 5.86, 5.28, 4.31]),
        'concentration_value': 0.25  # D/4
    },
    'D/8': {
        'x': np.array([2200, 2280, 2290, 2300, 2310, 2320, 2330, 2340, 2350, 2360, 2400, 2500]),
        'y': np.array([4.37, 12.14, 14.04, 16.0, 16.98, 16.26, 12.02, 12.47, 10.73, 9.16, 7.13, 2.75]),
        'concentration_value': 0.125  # D/8
    },
    'D/16': {
        'x': np.array([2200, 2210, 2220, 2230, 2240, 2250, 2260, 2270, 2280,
                       2290, 2300, 2310, 2320, 2330, 2340, 2350, 2360, 2370, 2380, 2390,
                       2400, 2450, 2500]),
        'y': np.array([4.58, 4.92, 5.37, 5.98, 6.51, 7.32, 8.33, 9.56, 11.14,
                       13.04, 15.00, 15.98, 15.26, 11.02, 11.47, 9.73, 8.16, 6.96, 6.04,
                       5.26, 4.68, 1.58, 0.76]),
        'concentration_value': 0.0625  # D/16
    },
    'D/32': {
        'x': np.array([2200, 2210, 2220, 2230, 2240, 2250, 2260, 2270, 2280,
                       2290, 2300, 2310, 2320, 2330, 2340, 2350, 2400, 2500]),
        'y': np.array([3.15, 3.41, 3.79, 4.22, 4.83, 5.49, 7.82, 9.73, 11.84,
                       13.25, 12.26, 9.85, 7.75, 6.19, 5.01, 4.25, 2.8, 1.22]),
        'concentration_value': 0.03125  # D/32
    }
}

print("Analiza wpływu stężenia barwnika na pierwszą harmoniczną")
print("=" * 60)

# Dopasowanie krzywych dla każdego stężenia
for label, data in concentration_data.items():
    print(f"\nAnaliza dla stężenia: {label}")
    x, y = data['x'], data['y']
    popt, perr = fit_resonance_data(x, y)

    if popt is not None:
        data['popt'] = popt
        data['perr'] = perr
        print(f"  f₀ = {popt[1]:.1f} ± {perr[1]:.1f} Hz")
        print(f"  A₀ = {popt[0]:.2f} ± {perr[0]:.2f}")
        print(f"  Amax (zmierzony) = {np.max(y):.2f}")
    else:
        print(f"  Błąd dopasowania dla {label}")

# Generowanie wykresów
results = plot_concentration_series(concentration_data)

# Dodatkowe analizy
print("\n" + "=" * 60)
print("Podsumowanie zależności od stężenia")
print("=" * 60)

concentrations = results['concentrations']
max_amplitudes = results['max_amplitudes']
f0_values = results['f0_values']
A0_values = results['A0_values']

# Wydrukowanie tabeli
print("\nTabela wyników:")
print(f"{'Stężenie':<10} {'C (wzgl.)':<10} {'Amax':<10} {'f₀ [Hz]':<12} {'A₀':<10}")
print("-" * 60)

for label, data in concentration_data.items():
    if 'popt' in data:
        print(f"{label:<10} {data['concentration_value']:<10.5f} "
              f"{np.max(data['y']):<10.2f} {data['popt'][1]:<12.1f} {data['popt'][0]:<10.2f}")

# Korelacje
print(f"\nKorelacja stężenie - Amax: {np.corrcoef(np.log(concentrations), max_amplitudes)[0,1]:.3f}")
print(f"Korelacja stężenie - f₀: {np.corrcoef(np.log(concentrations), f0_values)[0,1]:.3f}")
print(f"Korelacja stężenie - A₀: {np.corrcoef(np.log(concentrations), A0_values)[0,1]:.3f}")

# Generowanie dodatkowych wykresów podsumowujących
plot_summary_statistics(results)