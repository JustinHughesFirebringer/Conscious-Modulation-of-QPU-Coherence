#!/usr/bin/env python3
"""
Analyze original quantum metrics with meditation phase information
Compare correlation patterns between Control, Meditation, and Post-Meditation states
"""

import json
import pandas as pd
import numpy as np
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
        # Try alternative pattern (without 'job-' prefix)
        metrics_files = list(metrics_dir.glob('*-metrics.json'))
    if not metrics_files:
        # Try all JSON files
        metrics_files = list(metrics_dir.glob('*.json'))
        # Filter out summary files
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
            # Remove timezone for comparison
            timestamp = timestamp.replace(tzinfo=None)
        else:
            print(f"Warning: Info file not found for {job_id}")
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
    
    print(f"Loaded {len(data)} data points from {metrics_dir}")
    return pd.DataFrame(data)

print("="*80)
print("ORIGINAL QUANTUM METRICS ANALYSIS WITH PHASES")
print("="*80)

experiments = {
    '4-20_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\4_20_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\4-20_QPU'),
        'phase_defs': None  # No phase data available
    },
    '5-25_QPU': {
        'metrics_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\5_25_QPU_Quantum_Metrics_FIXED'),
        'raw_dir': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Data\RAW\5-25_QPU'),
        'phase_defs': None  # No phase data available
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

for exp_name, exp_config in experiments.items():
    print(f"\n{'='*80}")
    print(f"{exp_name} - INNER REGISTER QUANTUM METRICS")
    print(f"{'='*80}")
    
    df = load_quantum_metrics(exp_config['metrics_dir'], exp_config['phase_defs'], exp_config['raw_dir'])
    
    if len(df) == 0:
        print(f"No data loaded for {exp_name}, skipping...")
        continue
        
    inner_data = df[df['layer'] == 'inner'].copy()
    
    print(f"Total inner register data points: {len(inner_data)}")
    
    if exp_config['phase_defs']:
        print(f"States: {inner_data['state'].unique()}")
    else:
        print("No phase definitions available")
    
    metrics = ['coherence', 'entanglement', 'interference']
    
    # Variance analysis
    print(f"\n{'='*60}")
    print("VARIANCE ANALYSIS BY STATE")
    print(f"{'='*60}")
    
    if exp_config['phase_defs']:
        for metric in metrics:
            print(f"\n{metric}:")
            for state in ['Control', 'Meditation', 'Post-Meditation']:
                state_data = inner_data[inner_data['state'] == state]
                if len(state_data) >= 2:
                    variance = state_data[metric].var()
                    std = state_data[metric].std()
                    mean = state_data[metric].mean()
                    print(f"  {state}: var={variance:.6f}, std={std:.6f}, mean={mean:.6f}")
    else:
        for metric in metrics:
            variance = inner_data[metric].var()
            std = inner_data[metric].std()
            mean = inner_data[metric].mean()
            print(f"{metric}: var={variance:.6f}, std={std:.6f}, mean={mean:.6f}")
    
    if exp_config['phase_defs']:
        for state in ['Control', 'Meditation', 'Post-Meditation']:
            state_data = inner_data[inner_data['state'] == state]
            
            if len(state_data) < 2:
                print(f"\n{state}: Insufficient data ({len(state_data)} points)")
                continue
            
            print(f"\n{state} ({len(state_data)} points):")
            
            for metric in metrics:
                mean_val = state_data[metric].mean()
                std_val = state_data[metric].std()
                print(f"  {metric}: {mean_val:.6f} ± {std_val:.6f}")
            
            # Calculate correlations
            corr_matrix = state_data[metrics].corr()
            print(f"  Correlations:")
            print(f"    Coherence ↔ Entanglement: {corr_matrix.loc['coherence', 'entanglement']:.3f}")
            print(f"    Coherence ↔ Interference: {corr_matrix.loc['coherence', 'interference']:.3f}")
            print(f"    Entanglement ↔ Interference: {corr_matrix.loc['entanglement', 'interference']:.3f}")
    else:
        print(f"\nOverall statistics ({len(inner_data)} points):")
        for metric in metrics:
            mean_val = inner_data[metric].mean()
            std_val = inner_data[metric].std()
            print(f"  {metric}: {mean_val:.6f} ± {std_val:.6f}")
        
        corr_matrix = inner_data[metrics].corr()
        print(f"  Correlations:")
        print(f"    Coherence ↔ Entanglement: {corr_matrix.loc['coherence', 'entanglement']:.3f}")
        print(f"    Coherence ↔ Interference: {corr_matrix.loc['coherence', 'interference']:.3f}")
        print(f"    Entanglement ↔ Interference: {corr_matrix.loc['entanglement', 'interference']:.3f}")

print(f"\n{'='*80}")
print("CORRELATION CHANGES BETWEEN STATES (QUANTUM METRICS)")
print(f"{'='*80}")

for exp_name, exp_config in experiments.items():
    if not exp_config['phase_defs']:
        print(f"\n{exp_name}: No phase definitions, skipping correlation analysis")
        continue
        
    df = load_quantum_metrics(exp_config['metrics_dir'], exp_config['phase_defs'], exp_config['raw_dir'])
    
    if len(df) == 0:
        print(f"\n{exp_name}: No data loaded, skipping...")
        continue
        
    inner_data = df[df['layer'] == 'inner'].copy()
    
    print(f"\n{exp_name}:")
    
    # Calculate correlations for each state
    state_correlations = {}
    for state in ['Control', 'Meditation', 'Post-Meditation']:
        state_data = inner_data[inner_data['state'] == state]
        if len(state_data) >= 2:
            corr_matrix = state_data[metrics].corr()
            state_correlations[state] = corr_matrix
    
    # Compare key correlations between states
    if 'Control' in state_correlations and 'Meditation' in state_correlations:
        print(f"\n  Control → Meditation changes:")
        coh_ent_control = state_correlations['Control'].loc['coherence', 'entanglement']
        coh_ent_med = state_correlations['Meditation'].loc['coherence', 'entanglement']
        change = coh_ent_med - coh_ent_control
        print(f"    Coherence ↔ Entanglement: {coh_ent_control:.3f} → {coh_ent_med:.3f} (Δ{change:+.3f})")
        
        if (coh_ent_control > 0 and coh_ent_med < 0) or (coh_ent_control < 0 and coh_ent_med > 0):
            print(f"    *** SIGN FLIP DETECTED ***")

print(f"\n{'='*80}")
print("KEY INSIGHTS")
print(f"{'='*80}")
print("1. Compare quantum metric correlations with distribution-derived metric correlations")
print("2. Look for correlation sign changes in quantum metrics (the original finding)")
print("3. Note which metric calculation method shows stronger meditation effects")
