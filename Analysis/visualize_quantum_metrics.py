#!/usr/bin/env python3
"""
Visualize quantum metrics with meditation phase annotations
Create temporal evolution plots for coherence, entanglement, and interference
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Phase definitions for each experiment
phase_definitions = {
    '7-11_QPU': {
        'Control': '2025-07-12 03:14:00',
        'Progressive Relaxation': '2025-07-12 03:17:00', 
        'Phase 1': '2025-07-12 03:22:00',
        'Phase 2': '2025-07-12 03:38:00',
        'Return': '2025-07-12 03:42:00',
        'Post Meditation': '2025-07-12 04:20:00'
    },
    '9-23_QPU': {
        'Control': '2025-09-23 22:00:00',
        'Progressive Relaxation': '2025-09-23 22:04:00',
        'Phase 1': '2025-09-23 22:11:00', 
        'Phase 2': '2025-09-23 22:26:00',
        'Return': '2025-09-23 22:30:00',
        'Post Meditation': '2025-09-23 22:55:00'
    },
    '9-9_QPU': {
        'Control': '2025-09-09 23:32:00',
        'Progressive Relaxation': '2025-09-09 23:33:00',
        'Phase 1': '2025-09-09 23:42:00',
        'Phase 2': '2025-09-09 23:51:00',
        'Phase 3': '2025-09-10 00:03:00',
        'Phase 4': '2025-09-10 00:12:00',
        'Phase 5': '2025-09-10 00:21:00',
        'Phase 6': '2025-09-10 00:33:00',
        'Phase 7': '2025-09-10 00:42:00',
        'Return': '2025-09-10 00:51:00',
        'Post Meditation': '2025-09-10 00:52:00'
    }
}

def classify_state(phase):
    """Classify phases into 3 states: Control, Meditation, Post-Meditation"""
    if phase == 'Control':
        return 'Control'
    elif phase == 'Post Meditation':
        return 'Post-Meditation'
    else:
        return 'Meditation'

def assign_phase(timestamp, phase_defs):
    """Assign phase based on timestamp"""
    phase_times = {name: datetime.fromisoformat(time) for name, time in phase_defs.items()}
    sorted_phases = sorted(phase_times.items(), key=lambda x: x[1])
    
    for phase_name, phase_time in sorted_phases:
        if timestamp < phase_time:
            return phase_name
    return sorted_phases[-1][0]

def load_quantum_metrics(metrics_dir, phase_defs, raw_dir):
    """Load quantum metrics and add phase information"""
    metrics_dir = Path(metrics_dir)
    raw_dir = Path(raw_dir)
    data = []
    
    # Load each metrics file
    metrics_files = list(metrics_dir.glob('job-*-metrics.json'))
    if not metrics_files:
        metrics_files = list(metrics_dir.glob('*-metrics.json'))
    if not metrics_files:
        metrics_files = list(metrics_dir.glob('*.json'))
        metrics_files = [f for f in metrics_files if 'summary' not in f.name]
    
    for metrics_file in metrics_files:
        with open(metrics_file, 'r') as f:
            job_metrics = json.load(f)
        
        job_id = job_metrics['job_id']
        
        # Get actual job timestamp from info file
        info_file = raw_dir / f'job-{job_id}-info.json'
        if info_file.exists():
            with open(info_file, 'r') as f:
                info_data = json.load(f)
            timestamp = datetime.fromisoformat(info_data['created'].replace('Z', '+00:00'))
            timestamp = timestamp.replace(tzinfo=None)
        else:
            continue
        
        # Assign phase if phase definitions available
        if phase_defs:
            phase = assign_phase(timestamp, phase_defs)
            state = classify_state(phase)
        else:
            phase = 'Unknown'
            state = 'Unknown'
        
        # Extract metrics for each layer
        for layer_name, layer_metrics in job_metrics['layers'].items():
            row = {
                'job_id': job_id,
                'timestamp': timestamp,
                'phase': phase,
                'state': state,
                'layer': layer_name,
                'coherence': layer_metrics['coherence'],
                'entanglement': layer_metrics['entanglement'],
                'interference': layer_metrics['interference'],
                'num_shots': layer_metrics['num_shots']
            }
            data.append(row)
    
    return pd.DataFrame(data)

def export_job_csvs(df, output_dir):
    """Export CSV for each job isolating measurements per register"""
    output_dir = Path(output_dir)
    csv_dir = output_dir / 'job_csvs'
    csv_dir.mkdir(exist_ok=True)
    
    for job_id in df['job_id'].unique():
        job_data = df[df['job_id'] == job_id].copy()
        
        # Pivot to have registers as columns
        job_pivot = job_data.pivot(index='job_id', columns='layer', 
                                  values=['coherence', 'entanglement', 'interference', 'num_shots'])
        
        # Flatten column names
        job_pivot.columns = [f'{metric}_{layer}' for metric, layer in job_pivot.columns]
        job_pivot = job_pivot.reset_index()
        
        # Add timestamp
        job_pivot['timestamp'] = job_data['timestamp'].iloc[0]
        job_pivot['phase'] = job_data['phase'].iloc[0]
        job_pivot['state'] = job_data['state'].iloc[0]
        
        # Save CSV
        csv_path = csv_dir / f'{job_id}_quantum_metrics.csv'
        job_pivot.to_csv(csv_path, index=False)
    
    print(f"Exported {len(df['job_id'].unique())} job CSVs to {csv_dir}")

def plot_metric_evolution(df, experiment_name, phase_defs, output_dir):
    """Create temporal evolution plots for quantum metrics"""
    # Try to get 'inner' layer, fall back to 'central' or first available layer
    if 'inner' in df['layer'].values:
        layer_data = df[df['layer'] == 'inner'].copy()
    elif 'central' in df['layer'].values:
        layer_data = df[df['layer'] == 'central'].copy()
    else:
        layer_data = df[df['layer'] == df['layer'].values[0]].copy()
    
    layer_data = layer_data.sort_values('timestamp')
    
    # Use job index for even spacing, but keep timestamps for labels
    layer_data['job_index'] = range(len(layer_data))
    
    metrics = ['coherence', 'entanglement', 'interference']
    colors = {'coherence': 'blue', 'entanglement': 'green', 'interference': 'red'}
    layer_name = layer_data['layer'].iloc[0]
    
    # Check if we have pentagon layer data (central, inner, middle, outer)
    has_pentagon_layers = all(layer in df['layer'].values for layer in ['central', 'inner', 'middle', 'outer'])
    
    # Individual metric plots
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle(f'{experiment_name} - Quantum Metrics Evolution ({layer_name.capitalize()} Register)', fontsize=14, fontweight='bold')
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        
        # Plot metric over time using job index for even spacing
        ax.plot(layer_data['job_index'], layer_data[metric], 
                'o-', color=colors[metric], markersize=6, linewidth=2, label=metric)
        
        # Add phase boundaries if available
        if phase_defs:
            phase_times = {name: datetime.fromisoformat(time) for name, time in phase_defs.items()}
            sorted_phases = sorted(phase_times.items(), key=lambda x: x[1])
            
            for phase_name, phase_time in sorted_phases:
                if phase_time > layer_data['timestamp'].min() and phase_time < layer_data['timestamp'].max():
                    # Find the job index closest to this phase time
                    phase_idx = layer_data['timestamp'].searchsorted(phase_time, side='left')
                    if phase_idx < len(layer_data):
                        ax.axvline(phase_idx, color='gray', linestyle='--', alpha=0.5)
                        ax.text(phase_idx, ax.get_ylim()[1]*0.9, phase_name, 
                               rotation=90, verticalalignment='top', fontsize=8, alpha=0.7)
        
        # Color points by state
        if phase_defs:
            for state in ['Control', 'Meditation', 'Post-Meditation']:
                state_data = layer_data[layer_data['state'] == state]
                ax.scatter(state_data['job_index'], state_data[metric], 
                          s=80, alpha=0.6, edgecolors='black', linewidth=1, label=f'{state} state')
        
        ax.set_ylabel(metric.capitalize(), fontsize=11)
        ax.set_xlabel('Job Sequence', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        # Set x-tick labels to show timestamps
        tick_indices = range(0, len(layer_data), max(1, len(layer_data)//10))
        ax.set_xticks(tick_indices)
        ax.set_xticklabels([layer_data['timestamp'].iloc[i].strftime('%H:%M') for i in tick_indices], rotation=45)
    
    plt.tight_layout()
    output_path = Path(output_dir) / f'{experiment_name}_quantum_metrics_evolution.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")
    
    # Combined metrics plot
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle(f'{experiment_name} - Combined Quantum Metrics ({layer_name.capitalize()} Register)', fontsize=14, fontweight='bold')
    
    # Normalize metrics for comparison
    for metric in metrics:
        values = layer_data[metric].values
        normalized = (values - values.min()) / (values.max() - values.min() + 1e-10)
        ax.plot(layer_data['job_index'], normalized, 
                'o-', color=colors[metric], markersize=6, linewidth=2, label=metric)
    
    # Add phase boundaries
    if phase_defs:
        phase_times = {name: datetime.fromisoformat(time) for name, time in phase_defs.items()}
        sorted_phases = sorted(phase_times.items(), key=lambda x: x[1])
        
        for phase_name, phase_time in sorted_phases:
            if phase_time > layer_data['timestamp'].min() and phase_time < layer_data['timestamp'].max():
                # Find the job index closest to this phase time
                phase_idx = layer_data['timestamp'].searchsorted(phase_time, side='left')
                if phase_idx < len(layer_data):
                    ax.axvline(phase_idx, color='gray', linestyle='--', alpha=0.5)
                    ax.text(phase_idx, ax.get_ylim()[1]*0.9, phase_name, 
                           rotation=90, verticalalignment='top', fontsize=8, alpha=0.7)
    
    ax.set_ylabel('Normalized Value', fontsize=11)
    ax.set_xlabel('Job Sequence', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=11)
    
    # Set x-tick labels to show timestamps
    tick_indices = range(0, len(layer_data), max(1, len(layer_data)//10))
    ax.set_xticks(tick_indices)
    ax.set_xticklabels([layer_data['timestamp'].iloc[i].strftime('%H:%M') for i in tick_indices], rotation=45)
    
    plt.tight_layout()
    output_path = Path(output_dir) / f'{experiment_name}_quantum_metrics_combined.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")
    
    # 2x2 grid plot for all registers (only if pentagon layers available)
    if has_pentagon_layers:
        layers = ['central', 'inner', 'middle', 'outer']
        
        for metric in metrics:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'{experiment_name} - {metric.capitalize()} Across All Registers', fontsize=14, fontweight='bold')
            
            for layer_idx, layer in enumerate(layers):
                ax = axes[layer_idx // 2, layer_idx % 2]
                layer_df = df[df['layer'] == layer].copy()
                layer_df = layer_df.sort_values('timestamp')
                layer_df['job_index'] = range(len(layer_df))
                
                # Plot metric
                ax.plot(layer_df['job_index'], layer_df[metric], 
                        'o-', color=colors[metric], markersize=6, linewidth=2, label=metric)
                
                # Add phase boundaries if available
                if phase_defs:
                    phase_times = {name: datetime.fromisoformat(time) for name, time in phase_defs.items()}
                    sorted_phases = sorted(phase_times.items(), key=lambda x: x[1])
                    
                    for phase_name, phase_time in sorted_phases:
                        if phase_time > layer_df['timestamp'].min() and phase_time < layer_df['timestamp'].max():
                            # Find the job index closest to this phase time
                            phase_idx = layer_df['timestamp'].searchsorted(phase_time, side='left')
                            if phase_idx < len(layer_df):
                                ax.axvline(phase_idx, color='gray', linestyle='--', alpha=0.5)
                                ax.text(phase_idx, ax.get_ylim()[1]*0.9, phase_name, 
                                       rotation=90, verticalalignment='top', fontsize=8, alpha=0.7)
                
                # Color points by state
                if phase_defs:
                    for state in ['Control', 'Meditation', 'Post-Meditation']:
                        state_data = layer_df[layer_df['state'] == state]
                        ax.scatter(state_data['job_index'], state_data[metric], 
                                  s=80, alpha=0.6, edgecolors='black', linewidth=1, label=f'{state} state')
                
                ax.set_ylabel(metric.capitalize(), fontsize=11)
                ax.set_xlabel('Job Sequence', fontsize=11)
                ax.set_title(f'{layer.capitalize()} Register', fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(loc='best', fontsize=8)
                
                # Set x-tick labels to show timestamps
                tick_indices = range(0, len(layer_df), max(1, len(layer_df)//10))
                ax.set_xticks(tick_indices)
                ax.set_xticklabels([layer_df['timestamp'].iloc[i].strftime('%H:%M') for i in tick_indices], rotation=45)
            
            plt.tight_layout()
            output_path = Path(output_dir) / f'{experiment_name}_{metric}_all_registers.png'
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"Saved: {output_path}")
    
    # State comparison plot
    if phase_defs:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f'{experiment_name} - Quantum Metrics by State ({layer_name.capitalize()} Register)', fontsize=14, fontweight='bold')
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            state_data = []
            for state in ['Control', 'Meditation', 'Post-Meditation']:
                data = layer_data[layer_data['state'] == state][metric]
                state_data.append(data)
            
            bp = ax.boxplot(state_data, tick_labels=['Control', 'Meditation', 'Post'], 
                           patch_artist=True, widths=0.6)
            
            for patch, color in zip(bp['boxes'], [colors[metric]]*3):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            
            ax.set_ylabel(metric.capitalize(), fontsize=11)
            ax.set_title(f'{metric.capitalize()} Distribution', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = Path(output_dir) / f'{experiment_name}_quantum_metrics_by_state.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_path}")

print("="*80)
print("QUANTUM METRICS VISUALIZATION")
print("="*80)

experiments = {
    '4-20_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\4_20_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\4-20_QPU'),
        'phase_defs': None
    },
    '5-25_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\5_25_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\5-25_QPU'),
        'phase_defs': None
    },
    '7-11_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\7_11_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\7-11_QPU'),
        'phase_defs': phase_definitions['7-11_QPU']
    },
    '9-23_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\9_23_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\9-23_QPU'),
        'phase_defs': phase_definitions['9-23_QPU']
    },
    '9-9_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\9_9_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\9-9_QPU'),
        'phase_defs': phase_definitions['9-9_QPU']
    }
}

output_dir = Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\Quantum_Metrics_Visualizations_FIXED')
output_dir.mkdir(exist_ok=True)

for exp_name, exp_config in experiments.items():
    print(f"\nProcessing {exp_name}...")
    
    df = load_quantum_metrics(exp_config['metrics_dir'], exp_config['phase_defs'], exp_config['raw_dir'])
    
    if len(df) == 0:
        print(f"No data loaded for {exp_name}, skipping...")
        continue
    
    # Export job CSVs
    export_job_csvs(df, output_dir)
    
    # Create visualizations
    plot_metric_evolution(df, exp_name, exp_config['phase_defs'], output_dir)

print(f"\n{'='*80}")
print("Visualization complete!")
print(f"Output directory: {output_dir}")
print(f"{'='*80}")
