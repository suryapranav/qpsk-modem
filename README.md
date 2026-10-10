# Fixed-Point QPSK Modem with RLS Equalizer

A QPSK communications link built from first principles, validated stage by
stage against closed-form theory, and ported to fixed-point for execution on
a microcontroller.

**Phase 1** (this repo): Python golden model.
**Phase 2**: Q15 fixed-point C receiver on an MSPM0, validated against the
golden model, profiled for cycles/sample.
**Phase 3** (optional): receive a real signal off the air via RTL-SDR.

---

## Status

| Stage | Block | State | Acceptance |
|---|---|---|---|
| 0 | Bits, Gray QPSK map/demap, AWGN | **done** | BER on theory within ±0.05 dB |
| 1 | RRC pulse shaping + matched filter | stub | Nyquist ISI criterion; BER within 0.3 dB |
| 2 | Gardner timing recovery | stub | 0.3-symbol offset costs < 0.5 dB |
| 3 | Multipath channel + RLS equalizer | stub | within 1 dB of AWGN; MSE < 1e-3 in 500 symbols |

```
python3 tests/test_stage0_awgn.py     # run a stage's tests
python3 scripts/ber_sweep.py          # regenerate results/ber_awgn.png
```

---

## The method: validate every stage before adding the next

Each block either leaves the BER curve on theory, or moves it by an amount
you can explain in one sentence:

- **Pulse shaping + matched filter** — stays on theory. Cascaded RRC is
  Nyquist, and the matched filter maximises SNR at the sampling instant.
  If it moves, your filters are not a matched pair or your normalisation is
  wrong.
- **Timing recovery** — small, quantifiable loss. You are no longer sampling
  exactly at the pulse peak.
- **Multipath, unequalized** — large degradation, possibly an error floor.
- **Multipath + RLS** — most of that loss recovered. **The gap between the
  last two lines is the headline result of the project.**

Build the whole chain first and you have seven suspects and no way to bisect.

---

## Calibration notes (read before debugging a 3 dB offset)

Two places account for almost every modem that misses theory by exactly 3 dB:

1. **Es vs Eb.** A QPSK symbol carries 2 bits, so `Es = 2*Eb`.
2. **Complex noise variance.** `N0` is the total across both dimensions;
   each axis gets `N0/2`, i.e. std `sqrt(N0/2)`.

All noise generation goes through `modem/channel.py` so there is exactly one
place to check. `measured_esn0_db()` confirms the channel is doing what you
asked before you start suspecting the receiver.

---

## Layout

```
modem/
  bits.py        Gray-coded QPSK map/demap          [done]
  channel.py     AWGN with correct Eb/N0 scaling    [done]
  metrics.py     BER, theory curve, impl. loss      [done]
  pulse.py       RRC taps, upsample, filter         [STUB — Stage 1]
  sync.py        Gardner TED, timing loop           [STUB — Stage 2]
  equalizer.py   RLS adaptive equalizer             [STUB — Stage 3]
tests/           one file per stage
scripts/         ber_sweep.py
results/         generated plots and CSV
```

Each stub's docstring specifies the maths, the failure modes to expect, and
the acceptance criteria its tests enforce.

---

## Why RLS

RLS is a standard adaptive equalization algorithm in wireless receivers. The
recursion here is the same one used for adaptive noise cancellation — what
changes is the target: instead of subtracting a correlated noise reference,
the filter inverts a multipath channel so that `channel * equalizer` is close
to a delta function.

`P` must stay Hermitian positive-definite. It drifts in floating point and
diverges much sooner in Q15 — which is exactly the kind of finding Phase 2
exists to document.
