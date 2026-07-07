# QPU Proxy Metrics Analysis Workflow

## Overview
This workflow provides a consistent methodology for analyzing quantum processing unit (QPU) experiment data using distribution-derived proxy metrics. These metrics are computed from measured output bitstrings rather than quantum mechanical measurements.

## Key Formulas

### Distribution-Derived Metrics (from Excel methodology)

1. **Shannon Entropy**
   ```
   entropy = -Σ(p_i * log2(p_i))
   ```
   Where p_i is the probability of each bitstring outcome.

2. **Coherence**
   ```
   coherence = max(p_i)
   ```
   The probability of the single most frequent bitstring.

3. **Entanglement**
   ```
   entanglement = entropy / num_bits
   ```
   Normalized entropy by number of qubits.

4. **Interference**
   ```
   interference = 1 - (p_max - p_min)
   ```
   Where p_max is the most frequent outcome probability and p_min is the least frequent.

5. **Bit-Balance**
   ```
   balance = 1 - (|count_1 - count_0| / total_shots)
   ```
   Calculated per qubit, where 1 = perfect balance, 0 = complete imbalance.

## Workflow Steps

### 1. Data Processing
- Decode base64-encoded bitarray data from Qiskit Runtime V2 format
- Extract bitstrings for each register (c_central, c_inner, c_middle, c_outer)
- Calculate distribution-derived metrics for each register

### 2. Time Calculation
- Extract timestamps from job info files
- Convert to datetime objects
- Calculate time_minutes from session start
- **Important**: Recalculate time_minutes from actual timestamps to avoid scaling errors

### 3. Job Filtering (Optional)
- Filter by job ID range if needed
- Remove test jobs if present
- Ensure chronological ordering

### 4. Phase Assignment (Optional)
- Define meditation phase boundaries in UTC
- Assign phases based on timestamp ranges
- Typical phases: Control, Progressive Relaxation, Phase 1-7, Return, Post Meditation

### 5. CSV Output
- Save data in long format (one row per register per job)
- Include columns: job_id, timestamp, register, metrics, phase
- Include time_minutes for temporal analysis

### 6. Visualization
- Generate temporal evolution plots for each metric
- Use vertical stack layout (4 rows for 4 registers)
- Add phase markers as vertical lines
- Use consistent color scheme across registers
- Connect points with lines in chronological order

## Configuration Template

Use `analyze_qpu_proxy_metrics_template.py` as a starting point for new experiments:

```python
# Configuration
EXPERIMENT_NAME = "EXPERIMENT_NAME"
RAW_DIR = Path(r"PATH_TO_RAW_DATA")
OUTPUT_DIR = Path(r"PATH_TO_OUTPUT")

# Optional job filtering
JOB_ID_START = None  # e.g., "d30au7qiggks73ctos7g"
JOB_ID_END = None    # e.g., "d30d8p5otchc73baaagg"

# Optional phase definitions (UTC times)
PHASE_DEFINITIONS = {
    'Control': '2025-09-09 23:32:00',
    'Progressive Relaxation': '2025-09-09 23:33:00',
    # ... additional phases
}
```

## Common Issues and Solutions

### Time Scaling Errors
- **Problem**: time_minutes column shows incorrect values (e.g., 78-527 minutes instead of 0-159)
- **Solution**: Always recalculate time_minutes from actual timestamps: `df['time_minutes'] = (df['timestamp_dt'] - df['timestamp_dt'].min()).dt.total_seconds() / 60`

### Phase Boundary Alignment
- **Problem**: Phase boundaries outside data range
- **Solution**: Ensure phase times are in UTC and match the data's timezone. Convert Central Time to UTC by adding 5 hours (DST).

### Visual Clarity
- **Problem**: Overcrowded plots with confusing lines
- **Solution**: Use vertical stack layout (4x1 instead of 2x2), increase figure size, add phase markers

### Data Ordering
- **Problem**: Points not in chronological order
- **Solution**: Always sort by time_minutes before plotting: `reg_data = reg_data.sort_values('time_minutes')`

## File Structure

```
Clean_Repo/
├── Data/
│   ├── RAW/
│   │   ├── EXPERIMENT_NAME/
│   │   │   ├── job-*-result.json
│   │   │   └── job-*-info.json
│   └── Processed/
└── Analysis/
    ├── analyze_qpu_proxy_metrics_template.py
    ├── EXPERIMENT_NAME_Proxy_Output/
    │   ├── temporal_data_proxy_long.csv
    │   └── temporal_evolution_*.png
```

## Validation Checklist

- [ ] Verify time_minutes calculation from actual timestamps
- [ ] Check phase boundaries align with data range
- [ ] Ensure chronological ordering in plots
- [ ] Confirm metric formulas match Excel methodology
- [ ] Validate bit-balance inversion (1 = perfect balance)
- [ ] Test with known job IDs for expected results
- [ ] Check CSV output includes all required columns
- [ ] Verify visualizations show proper temporal progression

## Example Usage

For the 9-9 Brisbane experiment:
```python
EXPERIMENT_NAME = "9-9_QPU_Brisbane"
RAW_DIR = Path(r"C:\...\Data\RAW\9-9_QPU_Brisbane")
OUTPUT_DIR = Path(r"C:\...\Analysis\9_9_QPU_Brisbane_Proxy_Output")
JOB_ID_START = "d30au7qiggks73ctos7g"
JOB_ID_END = "d30d8p5otchc73baaagg"
PHASE_DEFINITIONS = {
    'Control': '2025-09-09 23:32:00',
    'Progressive Relaxation': '2025-09-09 23:33:00',
    # ... etc
}
```

## Notes

- These are proxy metrics, not true quantum mechanical measurements
- The interference formula `1-(p_max-p_min)` matches Excel for 1-bit registers but may differ for multi-qubit registers
- Phase definitions are optional and experiment-specific
- All timestamps should be in UTC for consistency
