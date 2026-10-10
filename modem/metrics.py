"""BER measurement and the theoretical reference curve.

The theory curve is the whole point of Phase 1.  Every stage you add to the
chain gets judged against it: either it sits on the curve, or it moves off
by an amount you can explain.  "It looks about right" is not a result.
"""

import numpy as np
from scipy.special import erfc


def q_function(x):
    """Gaussian tail probability Q(x) = P(X > x) for X ~ N(0, 1).

    Expressed via erfc for numerical stability far out in the tail, where
    a naive 1 - Phi(x) loses all its significant digits.
    """
    return 0.5 * erfc(np.asarray(x, dtype=float) / np.sqrt(2.0))


def qpsk_ber_theory(ebn0_db):
    """Theoretical BER for Gray-coded QPSK in AWGN: Q(sqrt(2*Eb/N0)).

    Note this is identical to BPSK.  QPSK gets twice the spectral efficiency
    for free in AWGN because the I and Q channels are orthogonal -- a result
    worth being able to state in an interview.
    """
    ebn0_lin = 10.0 ** (np.asarray(ebn0_db, dtype=float) / 10.0)
    return q_function(np.sqrt(2.0 * ebn0_lin))


def bit_error_rate(tx_bits, rx_bits):
    """Fraction of bits that differ. Both arrays must be the same length."""
    tx_bits = np.asarray(tx_bits)
    rx_bits = np.asarray(rx_bits)
    if tx_bits.shape != rx_bits.shape:
        raise ValueError(
            f"length mismatch: tx {tx_bits.shape} vs rx {rx_bits.shape} -- "
            "check for an off-by-one from filter delay or decimation offset"
        )
    return float(np.count_nonzero(tx_bits != rx_bits)) / tx_bits.size


def bits_needed_for_ber(target_ber, min_errors=100):
    """How many bits to simulate to resolve a given BER.

    Rule of thumb: you need ~100 bit errors for a BER estimate to be stable
    to within a few percent.  At BER = 1e-5 that means ~1e7 bits.  This is
    why high-Eb/N0 points are slow, and why you should never report a BER
    point that was measured with 3 errors.
    """
    return int(np.ceil(min_errors / max(target_ber, 1e-12)))


def implementation_loss_db(ebn0_db, measured_ber, search_range=(-5.0, 25.0)):
    """dB penalty of a measured BER point relative to theory.

    Finds the Eb/N0 at which theory would give `measured_ber`, and returns
    how much further right of the theory curve the measured point sits.
    Positive means worse than theory, which is the normal direction.

    This is the single number that summarises Phase 2 (fixed-point) loss,
    so it is worth having in the harness from the start.
    """
    lo, hi = search_range
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if qpsk_ber_theory(mid) > measured_ber:
            lo = mid
        else:
            hi = mid
    return float(ebn0_db - 0.5 * (lo + hi))
