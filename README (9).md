# Quantum Meditation QPU Review Packet

## Purpose

This repository is an adversarial-review packet for a series of synchronized meditation experiments run against IBM Quantum backends.

The goal is narrow:

> Do synchronized meditation windows coincide with register-specific changes in distribution-derived QPU proxy metrics after accounting for timing, backend, calibration, queue delay, circuit layout, run order, and analysis artifacts?

This repository does not ask the reviewer to accept Quantum Consciousness Field Theory, consciousness-QPU coupling, or any broad interpretation of the mechanism.

It asks a smaller question:

> Is there a statistically interesting, reproducible, register-specific temporal structure in the QPU output distributions that deserves further controlled testing?

The desired review is skeptical. The most useful contribution is to identify the strongest null explanation or the analysis/design flaw that makes the apparent effect disappear.

---

## Reviewer Task

If you are reviewing this repository, please focus on the following:

1. Identify the strongest non-consciousness explanation for the observed patterns.  
2. Test whether the apparent effects survive appropriate null models.  
3. Check whether the metrics are validly defined and consistently applied.  
4. Look for post-selection, phase-labeling, timing, backend, queue, calibration, or circuit-layout artifacts.  
5. Determine whether the inner-register effects are distinguishable from ordinary temporal drift.  
6. Recommend the cleanest next experiment that would falsify or strengthen the observation.

The central review question is:

> Are the observed register-specific changes more consistent with synchronized experimental timing, or with mundane QPU/runtime artifacts?

---

## Important Terminology Note

This repository uses metric names such as:

- coherence  
- interference  
- entanglement  
- entropy

These are **distribution-derived proxy metrics** computed from measured output bitstrings.

They are not tomography-based physical measurements of quantum coherence or entanglement.

For technical review, the correct phrase is:

> register-level output-distribution proxy metrics

The metric names are retained for continuity with earlier analysis files, but reviewers should evaluate the exact metric definitions in the analysis code rather than relying on the labels.

---

## Experimental Summary

The original protocol used synchronized human meditation sessions with binaural beats and/or isochronic tones while quantum circuits were submitted repeatedly to IBM Quantum hardware.

The intended structure was:

- pre-meditation control window  
- synchronized meditation window  
- post-meditation recovery window  
- repeated QPU circuit submissions throughout the session  
- later extraction of register-level proxy metrics from measured bitstring distributions

The original protocol describes circuit submissions before, during, and after meditation, with later blind processing and phase labeling. See `protocol/` for the original and updated protocol documentation.

Actual execution varied across sessions, intentionally and operationally, to avoid dependence on a single backend, calibration window, queue condition, or local-time artifact.

---

## Actual Run-Condition Variation

Across sessions, the experiment included the following variation:

| Variable | Observed Range |  
|---|---|  
| IBM backends | Fez, Torino, Marrakesh |  
| Control duration | 20–90 minutes |  
| Circuit submission frequency | Every 1–3 minutes |  
| Start times | Late morning through overnight, including 1–2 AM local time |  
| Synchronization quality | Some sessions were successfully synchronized; others were disrupted by queue or runtime delays |

These variables should be treated as covariates, not ignored.

A serious analysis should model or stratify by:

- backend  
- calibration age  
- queue delay  
- actual job execution time  
- intended submission time  
- circuit hash  
- transpilation/layout  
- shot count  
- register mapping  
- session phase  
- local time  
- run order

---

## Primary Exploratory Observation

The strongest observed pattern is not a simple global increase or decrease in a single metric.

The strongest pattern is **register-specific temporal reorganization**, especially in the inner register.

In the strongest session examples:

- the inner register appears to show increased organization/ordering during or around the meditation window  
- the middle register often remains comparatively stable  
- the outer register sometimes moves differently from the inner register  
- post-meditation recovery behavior appears in successfully synchronized sessions  
- delayed or asynchronous sessions do not show the same clean return-to-baseline pattern

The current working hypothesis for review is:

> Synchronized sessions may produce register-specific changes in QPU output-distribution proxy metrics, with the inner register acting as the primary candidate signal channel and the middle register serving as a possible internal comparison register.

This is an exploratory observation, not a demonstrated causal claim.

---

## Failure-Mode Observation

One of the most important observations is from sessions where queue delays or other execution delays prevented the intended pre-meditation or during-meditation synchronization.

In those sessions:

- inner-register outputs remained more random/unordered once jobs completed  
- the return-to-baseline pattern seen in successfully synchronized QPU jobs was not clearly evident  
- the apparent temporal structure was weaker or absent

This should be treated as a natural negative-control class.

Reviewer-facing interpretation:

> If the apparent effect depends on temporal synchronization, delayed/asynchronous sessions should reduce or eliminate the register-level structure seen in synchronized runs.

This failure mode is one of the main reasons the dataset is being submitted for adversarial review.

---

## Cross-Metric Observation

In many of the stronger runs, the relationship between the entanglement proxy and interference proxy appears to change by phase.

Preliminary observation:

| Phase | Observed Relationship |  
|---|---|  
| Control window | Positive correlation between entanglement proxy and interference proxy |  
| Meditation window | Negative correlation in many successful runs |

This may be more informative than a single-metric rise or fall because it describes a relationship between metrics rather than amplitude movement in one metric.

Reviewer task:

> Test whether the sign change survives phase-label permutation, time-block permutation, backend stratification, and correction for autocorrelation.

---

## Lead/Lag Observation

Later sessions showed two exploratory timing effects:

1. ordering sometimes appeared slightly before the scheduled meditation start  
2. return-to-baseline sometimes became slower than in earlier sessions

These observations require formal lead-lag analysis.

Possible tests:

- cross-correlation by register and phase  
- lead/lag permutation tests  
- comparison against non-meditation runs from similar backend windows  
- analysis using actual QPU execution timestamps rather than intended submission timestamps

No theoretical interpretation should be built on this until the timing survives null testing.

---

## Recommended Null Tests

The most important work in this repository is null testing.

Suggested nulls:

### 1. Time/Order Drift Null

Test whether the observed structure can be explained by ordinary temporal drift across the session.

Methods:

- compare against same-duration non-meditation QPU windows  
- shuffle meditation labels while preserving time blocks  
- use rolling baseline models  
- test autocorrelation explicitly

### 2. Backend/Calibration Null

Test whether the effect is backend-specific or calibration-window-specific.

Methods:

- stratify by backend: Fez, Torino, Marrakesh  
- include calibration age as a covariate where available  
- compare against nearby public or private backend runs when possible

### 3. Queue/Execution-Time Null

Test intended timing against actual execution timing.

Methods:

- use actual QPU job execution timestamps  
- separate submitted-time analysis from completed-time analysis  
- compare synchronized sessions against delayed/asynchronous sessions

### 4. Circuit/Layout Null

Test whether the effect is created by circuit structure, transpilation, qubit layout, or register mapping.

Methods:

- verify circuit hashes  
- compare transpiled layouts  
- test whether register effects track physical qubit placement  
- rerun with randomized logical-to-physical register assignment

### 5. Phase-Label Permutation Null

Test whether meditation phase labels explain more variance than random phase labels.

Methods:

- preserve temporal block lengths  
- randomly rotate or permute phase labels  
- compare observed register shifts to null distribution

### 6. Register Negative-Control Null

Test whether the inner register behaves differently from comparison registers.

Methods:

- compare inner vs middle register  
- use middle register as an internal stability reference where justified  
- test whether all registers shift together under backend drift

### 7. Metric-Definition Null

Test whether the observed effect depends on one custom metric definition.

Methods:

- recalculate using standard distributional measures  
- compare Shannon entropy, KL divergence, Jensen-Shannon divergence, Hellinger distance, total variation distance, and autocorrelation  
- avoid relying on the names “coherence,” “interference,” or “entanglement” unless the metric definition is explicitly justified

---

## Suggested Primary Endpoint for Review

For the current review packet, the cleanest primary endpoint is:

> Inner-register distributional change from control to meditation/post-meditation windows, compared against the middle register and against delayed/asynchronous sessions.

Suggested secondary endpoints:

- entanglement-proxy/interference-proxy correlation sign change  
- return-to-baseline timing  
- lead/lag structure  
- backend-stratified replication  
- register-specific divergence from baseline

---

## Proposed Repository Structure

```text  
/  
├── README.md  
├── protocol/  
│   ├── original_protocol.md  
│   ├── updated_protocol.md  
│   └── session_execution_notes.md  
│  
├── data/  
│   ├── raw/  
│   │   ├── session_YYYY_MM_DD/  
│   │   └── ...  
│   ├── processed/  
│   └── metadata/  
│       ├── backend_log.csv  
│       ├── job_timestamps.csv  
│       ├── calibration_metadata.csv  
│       └── session_phase_labels.csv  
│  
├── analysis/  
│   ├── metric_definitions.md  
│   ├── extraction_scripts/  
│   ├── temporal_analysis/  
│   └── register_analysis/  
│  
├── null_tests/  
│   ├── phase_label_permutation/  
│   ├── backend_calibration_tests/  
│   ├── queue_delay_tests/  
│   ├── register_negative_controls/  
│   └── metric_robustness/  
│  
├── figures/  
│   ├── cleaned_temporal_evolution_coherence.png  
│   ├── cleaned_temporal_evolution_entanglement.png  
│   ├── cleaned_temporal_evolution_entropy.png  
│   └── cleaned_temporal_evolution_interference.png  
│  
├── claims/  
│   ├── current_claims.md  
│   ├── retired_claims.md  
│   └── falsification_log.md  
│  
└── theory/  
    └── qcft_interpretation.md
```
