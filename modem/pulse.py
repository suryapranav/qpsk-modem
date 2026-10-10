"""Root-raised-cosine pulse shaping and matched filtering.

STATUS: STUB -- you implement this (Stage 1).

WHY RRC AND NOT A RECTANGLE
---------------------------
A rectangular pulse has a sinc spectrum: infinite bandwidth, and in a real
system it would splatter energy into the adjacent channel.  A raised-cosine
pulse is bandlimited and has zero crossings at every symbol instant except
its own (the Nyquist ISI criterion), so neighbouring symbols do not
interfere at the sampling point.

We split it: RRC at the transmitter and RRC again at the receiver.  Cascading
two RRCs gives one full RC, so the Nyquist property holds end to end, AND the
receiver filter is matched to the transmit pulse, which maximises SNR at the
sampling instant.  This is why the BER after matched filtering should land
back on the AWGN theory curve -- if it does not, your filters are not
actually a matched pair, or your normalisation is off.

WHAT TO IMPLEMENT
-----------------
rrc_taps(beta, sps, span_symbols) -> np.ndarray
    Real-valued FIR taps, length sps*span_symbols + 1 (odd, so the peak sits
    on a sample).  Normalise so that sum(h^2) == 1, which keeps symbol energy
    unchanged through the tx filter.

    The closed form has two removable singularities you must special-case:
      t = 0           -> (1/sqrt(T)) * (1 - beta + 4*beta/pi)
      t = +-T/(4beta) -> handle separately; derive it or look it up, but
                         make sure you can say WHY the general formula blows
                         up there (denominator 1 - (4*beta*t/T)^2 goes to 0).

    A NaN or inf in your taps is the classic failure here, and the test below
    catches it.

upsample(symbols, sps)       -> zero-stuffed symbol stream
filter_signal(x, taps)       -> 'full' convolution (keep the transient)

ACCEPTANCE (tests/test_stage1_pulse.py)
    - taps are finite, symmetric, and unit-energy
    - cascaded tx+rx RRC satisfies the Nyquist criterion: sampling the
      combined response at multiples of sps gives ~1 at the centre tap and
      ~0 at every other symbol offset (|value| < 1e-10)
    - end-to-end BER through tx RRC -> AWGN -> rx RRC -> downsample still
      matches theory within 0.3 dB
"""

import numpy as np


def rrc_taps(beta, sps, span_symbols):
    raise NotImplementedError("Stage 1: implement the RRC impulse response")


def upsample(symbols, sps):
    raise NotImplementedError("Stage 1: zero-stuff by sps")


def filter_signal(x, taps):
    raise NotImplementedError("Stage 1: FIR convolution")
