"""Symbol timing recovery.

STATUS: STUB -- you implement this (Stage 2).

THE PROBLEM
-----------
The receiver does not know where symbol boundaries are.  Sampling the matched
filter output at the wrong instant costs you SNR (you are off the peak of the
Nyquist pulse) and reintroduces ISI (you are no longer at the zero crossings
of the neighbours).  A half-sample timing error can cost several dB.

SUGGESTED APPROACH: Gardner timing error detector
    e[n] = Re{ (y[n] - y[n-1]) * conj(y[n - 1/2]) }

Gardner is a good choice here because it is decision-directed-free (works
before you know the symbols) and needs only 2 samples per symbol.  Feed e[n]
through a loop filter (proportional + integral) into an interpolator.

Start with a fixed fractional-delay interpolator and a known timing offset to
prove the interpolator alone works, THEN close the loop.  Debugging an
interpolator and a control loop simultaneously is miserable.

ACCEPTANCE (tests/test_stage2_sync.py)
    - with a deliberately injected fractional timing offset of 0.3 symbols,
      the recovered BER is within 0.5 dB of the perfect-timing BER
    - the timing error estimate converges and stays bounded over 10k symbols
"""

import numpy as np


def gardner_ted(y_half_rate):
    raise NotImplementedError("Stage 2: Gardner timing error detector")


def timing_recovery(samples, sps, loop_bw=0.01):
    raise NotImplementedError("Stage 2: closed-loop timing recovery")
