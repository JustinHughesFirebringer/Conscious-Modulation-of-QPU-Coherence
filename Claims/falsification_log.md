# Falsification Log

This document records the systematic falsification of claims in the Quantum Meditation QPU experiment.

## Overview

All claims of meditation-aligned quantum effects have been falsified through rigorous adversarial review. Each apparent signal was traced to a specific, reproducible cause unrelated to consciousness.

## Falsified Claims

### Claim 1: 9-9 Brisbane Meditation Effect

**Original Claim:** Inner register coherence and interference changes aligned with meditation window.

**Falsification Evidence:**

- Qubit settling began 45 minutes before meditation started
- Settling completed 13 minutes before meditation began
- Four settled control jobs existed in the gap before meditation
- Per-bit decomposition showed transition occurred in pre-meditation period
- Variance inside meditation window was statistically identical to pre-meditation settled period

**Root Cause:** Hardware artifact (qubit settling), not meditation effect

**Status:** FALSIFIED

**Reference:** 9-9 temporal analysis, per-bit decomposition

---

### Claim 2: 9-23 Meditation Effect

**Original Claim:** Inner register showed meditation-aligned changes with strengthening effect.

**Falsification Evidence:**

- Flat inner register across all phases
- Window-permutation test: p = 0.18 (not significant)
- Trend test: p = 0.14 (not significant)
- Control block was first five jobs (early-session settling pattern)
- Correlations positive in every phase

**Root Cause:** No significant effect exists

**Status:** FALSIFIED

**Reference:** 9-23 temporal analysis, permutation testing

---

### Claim 3: 7-11 Large Coherence/Entanglement Changes

**Original Claim:** Large coherence/entanglement changes (0.911 → -0.602) indicated meditation effect.

**Falsification Evidence:**

- Pipeline bug: analyzed compressed bytes instead of quantum data
- Corrected pipeline shows flat results (p = 0.20)
- No significant changepoint in corrected data
- Entanglement averages ≈ 0.00055 (at analytic noise floor of mutual-information estimator)

**Root Cause:** Decompression bug in analysis pipeline

**Status:** FALSIFIED

**Reference:** Pipeline validation, corrected 7-11 analysis

---

### Claim 4: 5-25 Meditation Effect

**Original Claim:** Session showed meditation effects.

**Falsification Evidence:**

- 17 jobs executed in 2-minute burst
- Execution occurred 4 hours late (queue delay)
- No time axis exists for temporal analysis
- Alignment with meditation undefined

**Root Cause:** Experimental design failure (queue collapse)

**Status:** FALSIFIED

**Reference:** 5-25 session timing analysis

---

### Claim 5: 4-20 Pilot Session Effects

**Original Claim:** Pilot session showed meditation effects.

**Falsification Evidence:**

- Used different circuit structure (no pentagon layers)
- Incomparable to other sessions
- Different data structure prevents unified analysis

**Root Cause:** Incomparable experimental design

**Status:** FALSIFIED

**Reference:** Circuit structure comparison

---

### Claim 6: >10% Changes Indicate Meditation Effects

**Original Claim:** Percentage changes >10% between phases indicate meditation effects.

**Falsification Evidence:**

- >10% changes occur 69% of time when splitting identical conditions
- Permutation testing: zero tests survive FDR correction
- Exactly one raw p < 0.05 against ~1.7 expected by chance
- Dataset contains exactly the amount of "signal" that noise produces

**Root Cause:** Statistical threshold detects noise, not signal

**Status:** FALSIFIED

**Reference:** Permutation testing, statistical analysis

---

## Pipeline Issues Discovered

### Decompression Bug

**Issue:** Analysis pipeline skipped zlib.decompression step, analyzing compressed bytes instead of quantum data.

**Impact:** All 2026 analyses computed statistics on compressed byte streams, not quantum measurements.

**Evidence:**

- Shot counts varied (8,732-8,761 for pentagons, 11,768-12,016 for central) instead of constant 8,192
- Numbers matched bit-length of compressed data divided by num_bits
- Simulation reproduced exact values using compressed-byte analysis
- Ground truth with biased qubit: coherence 0.073, interference 0.52 (correct) vs 0.001, 0.18 (buggy)

**Fix:** Added zlib.decompress and np.load steps, shot-count validation (8,192 assertion)

**Status:** FIXED

---

### Missing Data Issue

**Issue:** 19 jobs missing from 9-9 Brisbane extraction (55 of 74 jobs present).

**Impact:** Missing jobs spanned entire biased/telegraph regime (21:27-23:22).

**Evidence:**

- Present jobs: mean bit1 = 0.52
- Missing jobs: mean bit1 = 0.32 (biased regime)
- Precisely the anomalous jobs were absent

**Status:** DOCUMENTED (requires investigation of RAW folder)

---

## Statistical Issues Discovered

### Noise Floor Problem

**Issue:** Metrics at or below noise floor of estimators given sample sizes.

**Evidence:**

- 7-11 entanglement ≈ 0.00055 (analytic noise floor ≈ 0.00057 at 8,192 shots)
- Small sample sizes (4-16 jobs per phase) make averages unreliable
- High variance relative to mean values

**Impact:** Statistical power insufficient to detect real effects

---

### Multiple Comparison Problem

**Issue:** Many metrics, registers, and phases tested without correction.

**Evidence:**

- 36 session × register × metric combinations tested
- No FDR correction in original analyses
- Apparent effects likely due to multiple comparisons

**Fix:** Applied FDR correction in permutation testing

**Status:** ADDRESSED

---

## Backend Comparison Findings

### Significant Backend Differences

**Finding:** Backend choice significantly impacts quantum metrics.

**Evidence:**

- Inner register coherence: Torino 5-20x higher than Brisbane (p < 0.001)
- Inner register interference: Torino 2x higher than Brisbane (p < 0.001)
- Outer register entanglement: Torino 8x higher than Brisbane (p < 0.001)

**Implication:** Cross-backend comparisons unreliable without normalization

**Status:** DOCUMENTED

---

## Final Conclusion

**All claims of meditation-aligned quantum effects have been falsified.**

The dataset contains:
- One hardware artifact (9-9 Brisbane)
- One broken decoder (all 2026 analyses)
- One queue-collapsed session (5-25)
- One incomparable pilot (4-20)
- Three synchronized sessions that are statistically flat (7-11, 9-9, 9-23)

This is a complete, coherent, and publishable negative result.

---

## Lessons Learned

### Methodological

1. **Pipeline validation is critical**: Decompression bug would have been caught by shot-count assertion
2. **Statistical rigor matters**: Simple percentage thresholds are unreliable; permutation testing is essential
3. **Backend consistency required**: Different backends have fundamentally different baseline characteristics
4. **Sample size planning**: 4-16 jobs per phase is insufficient for reliable statistical inference

### Experimental Design

1. **Pre-registration essential**: Phase boundaries and analysis methods must be specified in advance
2. **Sham controls needed**: Interleaved non-meditation sessions on same backends
3. **Hardware monitoring**: Real-time qubit stability tracking to distinguish hardware from experimental effects
4. **Single frozen pipeline**: One validated analysis pipeline with built-in quality checks

---

## Acknowledgments

This falsification process demonstrates the value of adversarial review and rigorous null testing. Every apparent signal was traced to a specific, reproducible cause, strengthening the scientific method.
