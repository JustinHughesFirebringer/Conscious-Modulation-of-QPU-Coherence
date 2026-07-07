#!/usr/bin/env python3
"""
Temporal evolution analysis for ALL registers with accurate 2.5-hour timeline
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime
import seaborn as sns

# Directories
RESULTS_DIR = Path(r"C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\decoding\results\Samhain 2025")
METRICS_DIR = RESULTS_DIR / "metrics"
OUTPUT_DIR = RESULTS_DIR / "all_registers_timeline"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load all job metrics
print("Loading job metrics for all registers...")
jobs_data = []

for metrics_file in sorted(METRICS_DIR.glob("job-*-metrics.json")):
    with open(metrics_file, 'r') as f:
        data = json.load(f)
        job_id = metrics_file.stem.replace("-metrics", "")
        
        job_entry = {
            'job_id': job_id,
            'job_number': len(jobs_data) + 1,
            'timestamp': data.get('timestamp', 'unknown')
        }
        
        # Extract metrics for each register
        for register in ['central', 'inner', 'middle', 'outer']:
            reg_data = data['layers'].get(register, {})
            job_entry[f'{register}_coherence'] = reg_data.get('coherence', 0)
            job_entry[f'{register}_interference'] = reg_data.get('interference', 0)
            job_entry[f'{register}_entanglement'] = reg_data.get('entanglement', 0)
        
        jobs_data.append(job_entry)

df = pd.DataFrame(jobs_data)

# Calculate actual time intervals (48 jobs over ~2.5 hours)
minutes_per_job = 150 / 48
time_minutes = [i * minutes_per_job for i in range(len(df))]
df['time_minutes'] = time_minutes

print(f"\nLoaded {len(df)} jobs")
print(f"Time span: 0 to {time_minutes[-1]:.1f} minutes (~{time_minutes[-1]/60:.2f} hours)")

# Print summary statistics for each register
registers = ['central', 'inner', 'middle', 'outer']
for register in registers:
    print(f"\n{register.upper()} Register:")
    for metric in ['coherence', 'interference', 'entanglement']:
        col = f'{register}_{metric}'
        print(f"  {metric:12s}: {df[col].mean():.6f} ± {df[col].std():.6f}")

# Meditation session timing (ACTUAL from job timestamps)
# Jobs #13 to #23 (inclusive)
# Start: 21:11:10 (36 min from start), End: 21:41:10 (66 min from start)
MEDITATION_START = 36  # minutes (Job #13)
MEDITATION_END = 66    # minutes (Job #23)

# =============================================================================
# PLOT 1: All registers, all metrics in one comprehensive view
# =============================================================================
print("\nGenerating comprehensive temporal evolution plot...")

fig, axes = plt.subplots(4, 3, figsize=(22, 16))
fig.suptitle('Pentagonal Resonance Circuit - All Registers Temporal Evolution\nSamhain 2025 - 48 Jobs over 2.5 Hours', 
             fontsize=18, fontweight='bold', y=0.995)

metrics = ['coherence', 'interference', 'entanglement']
colors = {'central': '#e74c3c', 'inner': '#3498db', 'middle': '#2ecc71', 'outer': '#f39c12'}
register_names = {'central': 'Central (1 qubit)', 'inner': 'Inner Pentagon (5 qubits)', 
                 'middle': 'Middle Pentagon (5 qubits)', 'outer': 'Outer Pentagon (5 qubits)'}

for row, register in enumerate(registers):
    for col, metric in enumerate(metrics):
        ax = axes[row, col]
        col_name = f'{register}_{metric}'
        
        # Plot the metric
        ax.plot(df['time_minutes'], df[col_name], 
               marker='o', linewidth=2, markersize=3, 
               color=colors[register], alpha=0.7)
        
        # Add meditation window
        ax.axvspan(MEDITATION_START, MEDITATION_END, 
                  alpha=0.15, color='gold', zorder=0)
        
        # Styling
        if col == 0:
            ax.set_ylabel(register_names[register], fontsize=11, fontweight='bold')
        if row == 0:
            ax.set_title(metric.title(), fontsize=12, fontweight='bold')
        if row == 3:
            ax.set_xlabel('Time (minutes)', fontsize=10)
        
        ax.grid(True, alpha=0.3, linewidth=0.5)
        
        # Add mean line
        mean_val = df[col_name].mean()
        ax.axhline(y=mean_val, color=colors[register], linestyle='--', alpha=0.3, linewidth=1)
        
        # Add stats text
        std_val = df[col_name].std()
        stats_text = f'μ={mean_val:.4f}\nσ={std_val:.5f}'
        ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
               fontsize=7, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, pad=0.3))

plt.tight_layout()
output_file = OUTPUT_DIR / "all_registers_comprehensive_timeline.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_file}")
plt.close()

# =============================================================================
# PLOT 2: Per-metric comparison (all registers on same plot)
# =============================================================================
print("Generating per-metric comparison plots...")

fig, axes = plt.subplots(3, 1, figsize=(18, 14))
fig.suptitle('Quantum Metrics Comparison Across All Registers\nSamhain 2025 - 2.5 Hour Timeline', 
             fontsize=16, fontweight='bold')

for idx, metric in enumerate(metrics):
    ax = axes[idx]
    
    for register in registers:
        col_name = f'{register}_{metric}'
        ax.plot(df['time_minutes'], df[col_name], 
               marker='o', linewidth=2, markersize=3, 
               color=colors[register], alpha=0.7, 
               label=register_names[register])
    
    # Add meditation window
    ax.axvspan(MEDITATION_START, MEDITATION_END, 
              alpha=0.2, color='gold', label='Meditation (30 min)', zorder=0)
    
    ax.set_ylabel(metric.title(), fontsize=12, fontweight='bold')
    ax.set_title(f'{metric.title()} - All Registers', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=10)

axes[-1].set_xlabel('Time (minutes)', fontsize=12, fontweight='bold')

plt.tight_layout()
output_file = OUTPUT_DIR / "per_metric_comparison.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_file}")
plt.close()

# =============================================================================
# PLOT 3: Interference focus (most interesting metric)
# =============================================================================
print("Generating interference-focused analysis...")

fig, ax = plt.subplots(figsize=(20, 8))

for register in registers:
    col_name = f'{register}_interference'
    ax.plot(df['time_minutes'], df[col_name], 
           marker='o', linewidth=2.5, markersize=5, 
           color=colors[register], alpha=0.8, 
           label=register_names[register])

# Meditation window
ax.axvspan(MEDITATION_START, MEDITATION_END, 
          alpha=0.25, color='gold', label='Meditation Session (30 min)', zorder=0)

ax.set_xlabel('Time (minutes)', fontsize=14, fontweight='bold')
ax.set_ylabel('Interference', fontsize=14, fontweight='bold')
ax.set_title('Quantum Interference Temporal Evolution - All Registers\n2.5 Hour Timeline with Meditation Window', 
            fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='best', fontsize=12)

# Calculate changes for each register
analysis_text = "Interference Changes by Register:\n\n"
for register in registers:
    col_name = f'{register}_interference'
    pre = df[df['time_minutes'] < MEDITATION_START][col_name].mean()
    during = df[(df['time_minutes'] >= MEDITATION_START) & (df['time_minutes'] <= MEDITATION_END)][col_name].mean()
    post = df[df['time_minutes'] > MEDITATION_END][col_name].mean()
    
    delta_during = during - pre
    delta_post = post - pre
    pct_during = (delta_during / pre) * 100 if pre != 0 else 0
    pct_post = (delta_post / pre) * 100 if pre != 0 else 0
    
    analysis_text += f"{register.upper():7s}: Pre={pre:.4f}, During={during:.4f} ({pct_during:+.1f}%), Post={post:.4f} ({pct_post:+.1f}%)\n"

ax.text(0.02, 0.98, analysis_text.strip(), transform=ax.transAxes,
       fontsize=9, verticalalignment='top', family='monospace',
       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

plt.tight_layout()
output_file = OUTPUT_DIR / "interference_all_registers_focused.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_file}")
plt.close()

# =============================================================================
# PLOT 4: Heatmap view (register x time for each metric)
# =============================================================================
print("Generating heatmap visualizations...")

fig, axes = plt.subplots(1, 3, figsize=(22, 6))
fig.suptitle('Quantum Metrics Heatmaps - Registers × Time', fontsize=16, fontweight='bold')

for idx, metric in enumerate(metrics):
    ax = axes[idx]
    
    # Create data matrix: registers x time
    data_matrix = []
    for register in registers:
        col_name = f'{register}_{metric}'
        data_matrix.append(df[col_name].values)
    
    data_matrix = np.array(data_matrix)
    
    # Plot heatmap
    im = ax.imshow(data_matrix, aspect='auto', cmap='viridis', interpolation='nearest')
    ax.set_title(metric.title(), fontsize=13, fontweight='bold')
    ax.set_xlabel('Job Sequence', fontsize=11)
    ax.set_ylabel('Register', fontsize=11)
    ax.set_yticks(range(len(registers)))
    ax.set_yticklabels([r.title() for r in registers])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(metric.title(), fontsize=10)
    
    # Add meditation window overlay
    med_start_job = int(MEDITATION_START / minutes_per_job)
    med_end_job = int(MEDITATION_END / minutes_per_job)
    ax.axvline(x=med_start_job, color='gold', linestyle='--', linewidth=2, alpha=0.7)
    ax.axvline(x=med_end_job, color='gold', linestyle='--', linewidth=2, alpha=0.7)

plt.tight_layout()
output_file = OUTPUT_DIR / "heatmap_all_metrics.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_file}")
plt.close()

# Save comprehensive data
csv_file = OUTPUT_DIR / "all_registers_timeline_data.csv"
df.to_csv(csv_file, index=False)
print(f"✓ Saved: {csv_file}")

# Generate summary statistics report
summary_file = OUTPUT_DIR / "temporal_analysis_summary.txt"
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("SAMHAIN 2025 - TEMPORAL ANALYSIS SUMMARY\n")
    f.write("All Registers - 48 Jobs over 2.5 Hours\n")
    f.write("="*80 + "\n\n")
    
    for register in registers:
        f.write(f"\n{register.upper()} REGISTER ({register_names[register]})\n")
        f.write("-"*60 + "\n")
        for metric in metrics:
            col_name = f'{register}_{metric}'
            f.write(f"{metric.title():15s}: {df[col_name].mean():.8f} ± {df[col_name].std():.8f}\n")
            f.write(f"                 Range: [{df[col_name].min():.8f}, {df[col_name].max():.8f}]\n")
    
    f.write("\n" + "="*80 + "\n")
    f.write("MEDITATION WINDOW ANALYSIS (Estimated: 60-90 minutes)\n")
    f.write("="*80 + "\n\n")
    
    for metric in metrics:
        f.write(f"\n{metric.upper()}:\n")
        f.write("-"*60 + "\n")
        for register in registers:
            col_name = f'{register}_{metric}'
            pre = df[df['time_minutes'] < MEDITATION_START][col_name].mean()
            during = df[(df['time_minutes'] >= MEDITATION_START) & (df['time_minutes'] <= MEDITATION_END)][col_name].mean()
            post = df[df['time_minutes'] > MEDITATION_END][col_name].mean()
            
            delta_during = during - pre
            pct_during = (delta_during / pre) * 100 if pre != 0 else 0
            
            f.write(f"{register.upper():8s}: Pre={pre:.6f}, During={during:.6f} (Δ={delta_during:+.6f}, {pct_during:+.2f}%), Post={post:.6f}\n")

print(f"✓ Saved: {summary_file}")

print(f"\n{'='*80}")
print("TEMPORAL ANALYSIS COMPLETE")
print(f"{'='*80}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"\nGenerated files:")
print(f"  • all_registers_comprehensive_timeline.png (4x3 grid)")
print(f"  • per_metric_comparison.png (3 plots)")
print(f"  • interference_all_registers_focused.png")
print(f"  • heatmap_all_metrics.png")
print(f"  • all_registers_timeline_data.csv")
print(f"  • temporal_analysis_summary.txt")
print(f"\nNOTE: Meditation timing (60-90 min) is estimated.")
print("      Adjust MEDITATION_START and MEDITATION_END as needed.")
