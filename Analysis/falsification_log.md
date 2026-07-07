# Falsification Log

This log documents critical errors discovered during analysis review that invalidate specific results.

## 2026-07-06: Quantum Metrics Decoder Bug

### Issue
The `extract_pentagon_metrics.py` script contained a critical decoding bug in the `analyze_job()` function that caused it to analyze compressed data bytes instead of actual quantum measurement results.

### Root Cause
**File**: `extract_pentagon_metrics.py`
**Function**: `analyze_job()` (lines 297-311)
**Bug**: Missing zlib decompression step

**Incorrect decoding path** (buggy):
```python
decoded_data = base64.b64decode(array_data)
bits = np.unpackbits(np.frombuffer(decoded_data, dtype=np.uint8))  # MISSING decompression
```

**Correct decoding path** (used in `extract_layer_bitstrings()`):
```python
decoded_bytes = base64.b64decode(array_data)
decompressed_data = zlib.decompress(decoded_bytes)  # CRITICAL STEP
arr = np.load(io.BytesIO(decompressed_data), allow_pickle=False).reshape(-1)
bitstrings = [format(int(val), f'0{num_bits}b') for val in arr]
```

### Evidence of Bug
1. **Incorrect shot counts**: All IBM Quantum jobs use exactly 8,192 shots. The buggy extraction reported varying shot counts:
   - Pentagon layers: 8,732–8,761 shots (varies with compression ratio)
   - Central register: 11,768–12,016 shots (varies with compression ratio)
   
2. **Matched compression artifacts**: The reported shot counts matched the formula `bit_length_of_compressed_data / num_bits`, confirming the data source was compressed bytes, not quantum measurements.

3. **Noise-like metrics**: The buggy pipeline produced metrics indistinguishable from uniform random noise, even when fed perfectly deterministic quantum states (e.g., all-zeros state).

4. **Magnitude mismatch**: Correctly decoded data produces coherence values ~0.01-0.05. Buggy data produced coherence values ~0.0001-0.0006 (100x smaller), consistent with analyzing noise.

### Invalidated Results
All quantum metrics analysis from the 2026 re-extraction using the buggy decoder:

**Retired Directories**:
- `7_11_QPU_Quantum_Metrics/` (buggy)
- `9_23_QPU_Quantum_Metrics/` (buggy)
- `9_9_QPU_Quantum_Metrics/` (buggy)
- `5_25_QPU_Quantum_Metrics/` (buggy)

**Retired Analyses**:
- All correlation sign-flip tables showing:
  - 7-11: Coherence ↔ Entanglement: 0.911 → -0.602 (sign flip)
  - 9-9: Coherence ↔ Entanglement: -0.293 → 0.009 (sign flip)
- All variance analysis tables showing interference variance shifts
- All quantum metrics visualizations in `Quantum_Metrics_Visualizations/`
- All summaries claiming quantum metrics were "more sensitive to meditation effects"

**Reason**: These analyzed compressed-file byte statistics, not quantum measurement data. The correlation sign flips, variance patterns, and all other findings are artifacts of analyzing noise, not evidence of meditation effects.

### Fix Applied
**File**: `extract_pentagon_metrics.py`
**Change**: Added zlib decompression and np.load to `analyze_job()` function (lines 297-313)
**Validation**: Added assertion check for exactly 8,192 shots per layer

### Corrected Results
**New Directories** (with proper decoding):
- `7_11_QPU_Quantum_Metrics_FIXED/` (all layers show exactly 8,192 shots)
- `9_23_QPU_Quantum_Metrics_FIXED/` (all layers show exactly 8,192 shots)
- `9_9_QPU_Quantum_Metrics_FIXED/` (all layers show exactly 8,192 shots)

**Metric Magnitudes** (corrected):
- Coherence: ~0.01-0.05 (vs 0.0001-0.0006 buggy)
- Entanglement: ~0.0003-0.0006 (vs 0.0005-0.0010 buggy)
- Interference: ~0.19-0.28 (vs 0.11-0.18 buggy)

### Lessons Learned
1. **Validation is critical**: Simple assertions (e.g., `num_shots == 8192`) would have caught this bug immediately.
2. **Code review matters**: The correct decoding path existed in the same file (`extract_layer_bitstrings()`) but wasn't used in `analyze_job()`.
3. **Adversarial testing**: Checking results against known ground truth (e.g., deterministic states) reveals pipeline bugs.
4. **Data provenance**: Varying shot counts should have been investigated immediately as a red flag.

### Next Steps
1. Use the corrected quantum metrics for any future analysis
2. Re-run the distribution-derived metrics analysis (2025 method) on all datasets uniformly
3. Test 7-11 data with correct decoding to determine if any meditation effects exist
4. Apply changepoint analysis to 7-11 to determine if any transitions align with meditation window or hardware artifacts

---

## Summary

**Total Invalidated Analyses**: 1 critical bug affecting all 2026 quantum metrics re-extractions
**Status**: Bug fixed, corrected data available for re-analysis
**Confidence**: High - bug is definitively proven by shot count evidence and ground truth testing
