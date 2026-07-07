# Combined 9-9 Analysis: Brisbane vs Torino

## Overview
This analysis combines quantum metrics from the 9-9 meditation session run on two different IBM Quantum backends:
- **Brisbane**: 55 jobs (2025-09-09 23:15-00:55 UTC)
- **Torino**: 15 jobs (2025-09-09 21:27-22:58 UTC)

## Key Findings

### 1. Significant Backend Differences
The two backends show **substantial and statistically significant differences** in quantum metrics, particularly in the inner register:

**Inner Register Coherence:**
- Brisbane: ~0.002-0.003 across phases
- Torino: ~0.015-0.059 across phases (5-20x higher)
- **All phase comparisons: p < 0.001 ***

**Inner Register Interference:**
- Brisbane: ~0.21-0.23 across phases
- Torino: ~0.36-0.50 across phases (2x higher)
- **All phase comparisons: p < 0.001 ***

**Outer Register Entanglement:**
- Brisbane: ~0.0006-0.0007 across phases
- Torino: ~0.0048-0.0055 across phases (8x higher)
- **All phase comparisons: p < 0.001 ***

### 2. Phase Classification Results

**Brisbane (55 jobs):**
- Pre-Control: 10 jobs
- Control: 6 jobs
- Meditation: 27 jobs
- Post-Meditation: 12 jobs

**Torino (15 jobs):**
- Control: 2 jobs
- Meditation: 12 jobs
- Post-Meditation: 1 job

### 3. Statistical Significance Tests

**Backend Differences (t-tests):**
- **Inner register**: All metrics show highly significant differences (p < 0.001)
- **Outer register**: Coherence and entanglement highly significant (p < 0.001)
- **Central register**: No significant differences between backends
- **Middle register**: Mixed results, some significant differences

### 4. Interpretation

The large and systematic differences between Brisbane and Torino backends indicate:

1. **Hardware Variability**: Different quantum processors have distinct noise characteristics, calibration, and performance profiles
2. **Backend-Specific Baselines**: Each backend has its own baseline for quantum metrics, making cross-backend comparisons challenging
3. **Torino Higher Metrics**: Torino consistently shows higher coherence, entanglement, and interference values, suggesting different hardware characteristics

### 5. Implications for Meditation Research

These findings have important implications for quantum consciousness research:

1. **Backend Consistency Required**: Comparisons across sessions must use the same backend to avoid hardware-induced variability
2. **Baseline Normalization**: May need backend-specific baselines or normalization procedures
3. **Sample Size Considerations**: Torino's smaller sample size (15 vs 55 jobs) limits statistical power for phase analysis

### 6. Visualizations

The analysis includes comprehensive visualizations:
- Time series plots for each register showing temporal evolution
- Box plots comparing backend performance by phase
- Correlation heatmaps for each backend

## Conclusion

The combined analysis reveals that **backend choice significantly impacts quantum metrics**, with Torino showing systematically higher values than Brisbane across most registers and metrics. This underscores the importance of backend consistency in quantum consciousness research and suggests that cross-backend comparisons require careful normalization or should be avoided altogether.

The phase analysis within each backend shows similar patterns to previous analyses, with no clear meditation-aligned effects emerging after proper statistical testing.

## Files Generated

- `combined_summary.json`: Overall summary statistics
- `*_timeseries.png`: Time series plots for each register
- `*_boxplot.png`: Box plots comparing backends by phase
- `*_correlations.png`: Correlation heatmaps by backend
- `combined_analysis_summary.md`: This summary document
