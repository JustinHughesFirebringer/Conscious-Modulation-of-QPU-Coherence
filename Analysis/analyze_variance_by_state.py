#!/usr/bin/env python3
"""
Analyze variance between control, meditation, and post-meditation states
across all experiments, focusing on inner register patterns
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from all experiments
experiments = {
    '4-20_QPU': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\4_20_QPU_Proxy_Output\temporal_data_proxy_long.csv'),
    '5-25_QPU': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\5_25_QPU_Proxy_Output\temporal_data_proxy_long.csv'),
    '7-11_QPU': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\7_11_QPU_Proxy_Output\temporal_data_proxy_long.csv'),
    '9-23_QPU': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\9_23_QPU_Proxy_Output\temporal_data_proxy_long.csv'),
    '9-9_QPU': Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis\9_9_QPU_Proxy_Output\temporal_data_proxy_long_brisbane_with_phases.csv')
}

def classify_state(phase):
    """Classify phases into 3 states: Control, Meditation, Post-Meditation"""
    if phase == 'Control':
        return 'Control'
    elif phase == 'Post Meditation':
        return 'Post-Meditation'
    else:
        return 'Meditation'

print("="*80)
print("VARIANCE ANALYSIS BY STATE (CONTROL vs MEDITATION vs POST-MEDITATION)")
print("="*80)

metrics = ['coherence', 'entanglement', 'interference', 'entropy']
pentagon_experiments = ['5-25_QPU', '7-11_QPU', '9-23_QPU', '9-9_QPU']

# Store variance data for comparison
variance_results = {}

for exp_name in pentagon_experiments:
    csv_path = experiments[exp_name]
    if not csv_path.exists():
        continue
    
    df = pd.read_csv(csv_path)
    
    # Focus on inner register
    inner_data = df[df['register'] == 'c_inner'].copy()
    
    if 'phase' not in inner_data.columns:
        print(f"\n{exp_name}: No phase data available")
        continue
    
    # Classify into 3 states
    inner_data['state'] = inner_data['phase'].apply(classify_state)
    
    print(f"\n{'='*80}")
    print(f"{exp_name} - INNER REGISTER VARIANCE BY STATE")
    print(f"{'='*80}")
    
    exp_variance = {}
    
    for state in ['Control', 'Meditation', 'Post-Meditation']:
        state_data = inner_data[inner_data['state'] == state]
        
        if len(state_data) == 0:
            print(f"\n{state}: No data")
            continue
        
        print(f"\n{state} ({len(state_data)} points):")
        
        state_variance = {}
        for metric in metrics:
            mean_val = state_data[metric].mean()
            std_val = state_data[metric].std()
            variance_val = state_data[metric].var()
            cv = (std_val / mean_val * 100) if mean_val != 0 else 0  # Coefficient of variation
            
            print(f"  {metric}:")
            print(f"    Mean: {mean_val:.6f}")
            print(f"    Std: {std_val:.6f}")
            print(f"    Variance: {variance_val:.8f}")
            print(f"    CV (%): {cv:.2f}")
            
            state_variance[metric] = {
                'mean': mean_val,
                'std': std_val,
                'variance': variance_val,
                'cv': cv
            }
        
        exp_variance[state] = state_variance
    
    variance_results[exp_name] = exp_variance
    
    # Calculate between-state variance
    print(f"\nBETWEEN-STATE VARIANCE:")
    for metric in metrics:
        state_means = [exp_variance[state][metric]['mean'] 
                      for state in ['Control', 'Meditation', 'Post-Meditation']
                      if state in exp_variance]
        if len(state_means) >= 2:
            between_state_var = np.var(state_means)
            print(f"  {metric}: {between_state_var:.8f}")

# 4-20 experiment (different register structure)
print(f"\n{'='*80}")
print("4-20_QPU - MEAS REGISTER VARIANCE BY STATE")
print(f"{'='*80}")

csv_path = experiments['4-20_QPU']
if csv_path.exists():
    df = pd.read_csv(csv_path)
    meas_data = df[df['register'] == 'meas'].copy()
    
    if 'phase' in meas_data.columns:
        meas_data['state'] = meas_data['phase'].apply(classify_state)
        
        for state in ['Control', 'Meditation', 'Post-Meditation']:
            state_data = meas_data[meas_data['state'] == state]
            
            if len(state_data) == 0:
                print(f"\n{state}: No data")
                continue
            
            print(f"\n{state} ({len(state_data)} points):")
            for metric in metrics:
                mean_val = state_data[metric].mean()
                std_val = state_data[metric].std()
                cv = (std_val / mean_val * 100) if mean_val != 0 else 0
                
                print(f"  {metric}: {mean_val:.6f} ± {std_val:.6f} (CV: {cv:.2f}%)")

print(f"\n{'='*80}")
print("VARIANCE RATIO ANALYSIS (Meditation/Control, Post-Meditation/Control)")
print(f"{'='*80}")

for exp_name in pentagon_experiments:
    if exp_name not in variance_results:
        continue
    
    exp_data = variance_results[exp_name]
    
    if 'Control' not in exp_data or 'Meditation' not in exp_data:
        continue
    
    print(f"\n{exp_name}:")
    
    for metric in metrics:
        control_var = exp_data['Control'][metric]['variance']
        meditation_var = exp_data['Meditation'][metric]['variance']
        
        if 'Post-Meditation' in exp_data:
            post_var = exp_data['Post-Meditation'][metric]['variance']
            post_ratio = post_var / control_var if control_var > 0 else 0
        else:
            post_ratio = None
        
        med_ratio = meditation_var / control_var if control_var > 0 else 0
        
        print(f"  {metric}:")
        print(f"    Meditation/Control variance ratio: {med_ratio:.3f}")
        if post_ratio is not None:
            print(f"    Post-Meditation/Control variance ratio: {post_ratio:.3f}")

print(f"\n{'='*80}")
print("KEY INSIGHTS")
print(f"{'='*80}")
print("1. Compare variance ratios to identify which states show most/least stability")
print("2. Look for experiments where meditation reduces variance (potential effect)")
print("3. Identify metrics that are most sensitive to state changes")
print("4. Note any distinctive patterns in 9-9 vs other experiments")
