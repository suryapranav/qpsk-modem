"""Channel models: AWGN and (later) multipath.

THE 3 dB TRAP
-------------
Almost every student modem that misses the theoretical BER curve by 3 dB
gets it wrong in one of these two places:

1. Es vs Eb.  A QPSK symbol carries 2 bits, so Es = 2*Eb.  If you set your
   noise level from Eb/N0 as though Es = Eb, you are off by exactly 3 dB.

2. Complex noise variance.  For a complex baseband signal, N0 is the TOTAL
   noise power across both dimensions.  Each of the real and imaginary parts
   gets variance N0/2, i.e. standard deviation sqrt(N0/2).  Generating
   complex noise with std sqrt(N0) per axis doubles your noise power.

The derivation used below, for unit-energy symbols (Es = 1):

    Es/N0 = BITS_PER_SYMBOL * Eb/N0
    N0    = Es / (Es/N0) = 1 / (2 * Eb/N0_linear)
    sigma_per_axis = sqrt(N0 / 2)

Keep this function as the single place noise is ever generated.  If the
BER curve is off by a constant number of dB, this file is the first and
usually only place to look.
"""

import numpy as np

from .bits import BITS_PER_SYMBOL


def ebn0_db_to_noise_sigma(ebn0_db, bits_per_symbol=BITS_PER_SYMBOL, es=1.0):
    """Per-axis noise standard deviation for a target Eb/N0 in dB.

    Args:
        ebn0_db: Target Eb/N0 in decibels.
        bits_per_symbol: 2 for QPSK.
        es: Average symbol energy of the signal being corrupted.

    Returns:
        Standard deviation to apply independently to the real and imaginary
        parts of the complex noise.
    """
    ebn0_lin = 10.0 ** (ebn0_db / 10.0)
    esn0_lin = bits_per_symbol * ebn0_lin
    n0 = es / esn0_lin
    return np.sqrt(n0 / 2.0)


def awgn(symbols, ebn0_db, rng, bits_per_symbol=BITS_PER_SYMBOL, es=1.0):
    """Add complex additive white Gaussian noise at the given Eb/N0."""
    sigma = ebn0_db_to_noise_sigma(ebn0_db, bits_per_symbol, es)
    noise = rng.normal(0.0, sigma, symbols.shape) + 1j * rng.normal(
        0.0, sigma, symbols.shape
    )
    return symbols + noise


def measured_esn0_db(clean, noisy):
    """Estimate Es/N0 in dB from a clean/noisy pair.

    Diagnostic only -- use this to confirm the channel is doing what you
    asked before you go hunting for bugs in the receiver.
    """
    signal_power = np.mean(np.abs(clean) ** 2)
    noise_power = np.mean(np.abs(noisy - clean) ** 2)
    return 10.0 * np.log10(signal_power / noise_power)
