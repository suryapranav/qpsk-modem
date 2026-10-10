"""Stage 0: QPSK over AWGN, no pulse shaping.

This is the foundation every later stage is measured against. If this does
not sit on the theory curve, nothing downstream can be trusted.
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modem.bits import qpsk_demap, qpsk_map, random_bits
from modem.channel import awgn, ebn0_db_to_noise_sigma, measured_esn0_db
from modem.metrics import bit_error_rate, qpsk_ber_theory


class TestMapping(unittest.TestCase):
    def test_roundtrip_is_lossless_without_noise(self):
        rng = np.random.default_rng(0)
        bits = random_bits(10_000, rng)
        self.assertEqual(bit_error_rate(bits, qpsk_demap(qpsk_map(bits))), 0.0)

    def test_unit_average_symbol_energy(self):
        rng = np.random.default_rng(1)
        syms = qpsk_map(random_bits(100_000, rng))
        self.assertAlmostEqual(float(np.mean(np.abs(syms) ** 2)), 1.0, places=9)

    def test_gray_coding_adjacent_symbols_differ_by_one_bit(self):
        # All four symbols, in order 00, 01, 10, 11.
        syms = qpsk_map(np.array([0, 0, 0, 1, 1, 0, 1, 1], dtype=np.uint8))
        # Nearest neighbours on each axis must differ in exactly one bit.
        for a, b in [(0, 1), (0, 2), (1, 3), (2, 3)]:
            dist = abs(syms[a] - syms[b])
            self.assertAlmostEqual(dist, np.sqrt(2.0), places=9)


class TestChannelCalibration(unittest.TestCase):
    """The 3 dB trap. These two tests are the ones that save you a weekend."""

    def test_sigma_matches_hand_derivation(self):
        # At Eb/N0 = 0 dB with Es = 1 and 2 bits/symbol:
        #   Es/N0 = 2  ->  N0 = 0.5  ->  sigma_per_axis = sqrt(0.25) = 0.5
        self.assertAlmostEqual(ebn0_db_to_noise_sigma(0.0), 0.5, places=12)

    def test_measured_esn0_matches_requested(self):
        rng = np.random.default_rng(2)
        syms = qpsk_map(random_bits(2_000_000, rng))
        for ebn0_db in [0.0, 4.0, 8.0]:
            noisy = awgn(syms, ebn0_db, rng)
            # Es/N0 should be Eb/N0 + 10*log10(2) = Eb/N0 + 3.01 dB
            expected = ebn0_db + 10.0 * np.log10(2.0)
            self.assertAlmostEqual(measured_esn0_db(syms, noisy), expected, places=1)


class TestBERAgainstTheory(unittest.TestCase):
    def test_ber_tracks_theory_across_sweep(self):
        rng = np.random.default_rng(3)
        for ebn0_db in [0.0, 2.0, 4.0, 6.0, 8.0]:
            theory = qpsk_ber_theory(ebn0_db)
            # Simulate enough bits for ~400 errors so the estimate is stable.
            n_bits = int(max(400 / theory, 20_000))
            n_bits += n_bits % 2
            bits = random_bits(n_bits, rng)
            rx = qpsk_demap(awgn(qpsk_map(bits), ebn0_db, rng))
            measured = bit_error_rate(bits, rx)
            rel_err = abs(measured - theory) / theory
            self.assertLess(
                rel_err,
                0.15,
                f"Eb/N0={ebn0_db} dB: measured {measured:.3e} vs "
                f"theory {theory:.3e} ({rel_err:.1%} off)",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
