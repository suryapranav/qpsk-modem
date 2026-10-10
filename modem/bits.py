"""Bit generation and Gray-coded QPSK mapping/demapping.

Constellation (Gray-coded, unit average symbol energy):

        Q
    01  |  00
   -----+-----  I
    11  |  10

Bit pair (b0, b1) -> symbol s = (1-2*b0 + j*(1-2*b1)) / sqrt(2)

Gray coding means adjacent constellation points differ in exactly one bit,
so a symbol error at reasonable SNR almost always costs exactly one bit
error. That is what makes BER = Q(sqrt(2*Eb/N0)) hold for QPSK.
"""

import numpy as np

# Each QPSK symbol carries 2 bits.
BITS_PER_SYMBOL = 2


def random_bits(n_bits, rng):
    """Generate n_bits uniform random bits as a uint8 array of 0s and 1s."""
    return rng.integers(0, 2, size=n_bits, dtype=np.uint8)


def qpsk_map(bits):
    """Map a bit array to unit-energy complex QPSK symbols.

    Args:
        bits: 1-D array of 0/1, length must be even.

    Returns:
        Complex128 array of length len(bits)//2 with E[|s|^2] == 1.
    """
    bits = np.asarray(bits)
    if bits.size % BITS_PER_SYMBOL != 0:
        raise ValueError(
            f"bit count {bits.size} is not a multiple of {BITS_PER_SYMBOL}"
        )

    b0 = bits[0::2]  # in-phase bit
    b1 = bits[1::2]  # quadrature bit

    # 0 -> +1, 1 -> -1 on each axis; /sqrt(2) gives unit symbol energy.
    i = 1.0 - 2.0 * b0
    q = 1.0 - 2.0 * b1
    return (i + 1j * q) / np.sqrt(2.0)


def qpsk_demap(symbols):
    """Hard-decision demap complex symbols back to bits.

    Decision regions are simply the sign of each axis, which is optimal for
    QPSK in AWGN because the I and Q channels are independent BPSK channels.
    """
    symbols = np.asarray(symbols)
    b0 = (symbols.real < 0).astype(np.uint8)
    b1 = (symbols.imag < 0).astype(np.uint8)

    bits = np.empty(symbols.size * BITS_PER_SYMBOL, dtype=np.uint8)
    bits[0::2] = b0
    bits[1::2] = b1
    return bits
