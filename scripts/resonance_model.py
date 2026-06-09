"""Wspólne funkcje do analizy krzywych rezonansowych w doświadczeniu L10."""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit


def resonance_curve(f, A0, f0, G, T):
    """
    Krzywa rezonansowa używana w raporcie.

    A(f) = A0 * (G^2 * 4*pi^2*f^2) /
           (((2*pi*f)^2 - (2*pi*f0)^2)^2 + G^2 * 4*pi^2*f^2) + T
    """
    f = np.asarray(f, dtype=float)
    omega = 2 * np.pi * f
    omega0 = 2 * np.pi * f0
    numerator = A0 * (G**2 * 4 * np.pi**2 * f**2)
    denominator = (omega**2 - omega0**2) ** 2 + G**2 * 4 * np.pi**2 * f**2
    return numerator / denominator + T


def initial_guess(x, y):
    """Wyznacza proste wartości startowe dla dopasowania."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return [
        float(np.max(y) - np.min(y)),
        float(x[np.argmax(y)]),
        float((np.max(x) - np.min(x)) / 10),
        float(np.min(y)),
    ]


def fit_resonance_data(x, y, p0=None):
    """Dopasowuje krzywą rezonansową i zwraca popt, perr, pcov."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if p0 is None:
        p0 = initial_guess(x, y)

    # Parametry ograniczamy do fizycznie sensownych zakresów.
    lower = [0, np.min(x), 1e-9, -np.inf]
    upper = [np.inf, np.max(x), np.inf, np.inf]
    popt, pcov = curve_fit(
        resonance_curve,
        x,
        y,
        p0=p0,
        bounds=(lower, upper),
        maxfev=20000,
    )
    perr = np.sqrt(np.diag(pcov))
    return popt, perr, pcov


def r_squared(y_true, y_pred):
    """Współczynnik determinacji R^2."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return np.nan
    return 1 - ss_res / ss_tot
