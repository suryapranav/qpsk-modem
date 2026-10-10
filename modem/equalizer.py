"""RLS adaptive equalizer.

STATUS: STUB -- you implement this (Stage 3).  THIS IS THE CENTREPIECE.

WHY THIS PROJECT EXISTS
-----------------------
You have already implemented RLS for acoustic noise cancellation on the PYNQ.
The algorithm here is the SAME RECURSION.  What changes is what the filter is
asked to do: instead of subtracting a correlated noise reference, it inverts
a multipath channel so that the cascade (channel * equalizer) is close to a
delta function.  Being able to say that sentence, and mean it, is the point.

THE RECURSION (complex-valued, exponentially weighted)

    pi      = P[n-1] @ u[n]
    k[n]    = pi / (lam + u[n]^H @ pi)          # gain vector
    xi      = d[n] - w[n-1]^H @ u[n]            # a priori error
    w[n]    = w[n-1] + k[n] * conj(xi)
    P[n]    = (P[n-1] - k[n] @ u[n]^H @ P[n-1]) / lam

    u[n] = vector of the last N received samples (the tap delay line)
    d[n] = desired symbol (training sequence, then decision-directed)
    lam  = forgetting factor, typically 0.99-0.999
    P    = inverse correlation matrix, initialised delta^-1 * I

NUMERICAL WARNING, AND WHY IT MATTERS FOR PHASE 2
    P must stay Hermitian positive-definite.  In floating point it drifts and
    can diverge; in Q15 fixed point it WILL, much sooner.  Symmetrising each
    iteration (P = (P + P^H)/2) is the cheap fix.  Note where this bites --
    the divergence behaviour is exactly the kind of fixed-point finding that
    makes Phase 2 worth writing up.

WHAT TO IMPLEMENT
    RLSEqualizer(n_taps, lam, delta)
        .train(rx, ref)       # training-sequence mode
        .equalize(rx)         # decision-directed after training
        .weights               # converged taps, for plotting against the
                               #   inverse channel response

ACCEPTANCE (tests/test_stage3_equalizer.py)
    - on a known 3-tap multipath channel, MSE drops below 1e-3 within
      500 training symbols
    - BER with the equalizer is within 1 dB of the AWGN-only curve, versus
      the badly degraded unequalized BER (measure both -- the delta IS the
      result you put on your resume)
    - P stays Hermitian to within 1e-9 over the whole run
"""

import numpy as np


class RLSEqualizer:
    def __init__(self, n_taps, lam=0.999, delta=0.01):
        raise NotImplementedError("Stage 3: initialise w and P")

    def train(self, rx, ref):
        raise NotImplementedError("Stage 3: RLS recursion, training mode")

    def equalize(self, rx):
        raise NotImplementedError("Stage 3: decision-directed mode")
