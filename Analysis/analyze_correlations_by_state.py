#!/usr/bin/env python3
"""
Analyze correlations between metrics across jobs per date, separated by state
Focus on how metric relationships change between Control, Meditation, and Post-Meditation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt

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
print("CORRELATION ANALYSIS BY STATE (CONTROL vs MEDITATION vs POST-MEDITATION)")
print("="*80)

metrics = ['coherence', 'entanglement', 'interference', 'entropy']
pentagon_experiments = ['7-11_QPU', '9-23_QPU', '9-9_QPU']

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
    print(f"{exp_name} - INNER REGISTER CORRELATIONS BY STATE")
    print(f"{'='*80}")
    
    for state in ['Control', 'Meditation', 'Post-Meditation']:
        state_data = inner_data[inner_data['state'] == state]
        
        if len(state_data) < 2:
            print(f"\n{state}: Insufficient data ({len(state_data)} points)")
            continue
        
        print(f"\n{state} ({len(state_data)} points):")
        
        # Calculate correlation matrix
        corr_matrix = state_data[metrics].corr()
        
        print("Correlation Matrix:")
        print(corr_matrix.round(3))
        
        # Highlight key correlations
        print("\nKey Correlations:")
        print(f"  Coherence ↔ Entanglement: {corr_matrix.loc['coherence', 'entanglement']:.3f}")
        print(f"  Coherence ↔ Entropy: {corr_matrix.loc['coherence', 'entropy']:.3f}")
        print(f"  Coherence ↔ Interference: {corr_matrix.loc['coherence', 'interference']:.3f}")
        print(f"  Entanglement ↔ Entropy: {corr_matrix.loc['entanglement', 'entropy']:.3f}")
        print(f"  Entanglement ↔ Interference: {corr_matrix.loc['entanglement', 'interference']:.3f}")
        print(f"  Interference ↔ Entropy: {corr_matrix.loc['interference', 'entropy']:.3f}")

# 4-20 experiment (different register structure)
print(f"\n{'='*80}")
print("4-20_QPU - MEAS REGISTER CORRELATIONS BY STATE")
print(f"{'='*80}")

csv_path = experiments['4-20_QPU']
if csv_path.exists():
    df = pd.read_csv(csv_path)
    meas_data = df[df['register'] == 'meas'].copy()
    
    if 'phase' in meas_data.columns:
        meas_data['state'] = meas_data['phase'].apply(classify_state)
        
        for state in ['Control', 'Meditation', 'Post-Meditation']:
            state_data = meas_data[meas_data['state'] == state]
            
            if len(state_data) < 2:
                print(f"\n{state}: Insufficient data ({len(state_data)} points)")
                continue
            
            print(f"\n{state} ({len(state_data)} points):")
            corr_matrix = state_data[metrics].corr()
            print("Correlation Matrix:")
            print(corr_matrix.round(3))

print(f"\n{'='*80}")
print("CORRELATION CHANGES BETWEEN STATES")
print(f"{'='*80}")

for exp_name in pentagon_experiments:
    csv_path = experiments[exp_name]
    if not csv_path.exists():
        continue
    
    df = pd.read_csv(csv_path)
    inner_data = df[df['register'] == 'c_inner'].copy()
    
    if 'phase' not in inner_data.columns:
        continue
    
    inner_data['state'] = inner_data['phase'].apply(classify_state)
    
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
        for metric1 in metrics:
            for metric2 in metrics:
                if metric1 < metric2:  # Avoid duplicates
                    control_corr = state_correlations['Control'].loc[metric1, metric2]
                    med_corr = state_correlations['Meditation'].loc[metric1, metric2]
                    change = med_corr - control_corr
                    print(f"    {metric1} ↔ {metric2}: {control_corr:.3f} → {med_corr:.3f} (Δ{change:+.3f})")
    
    if 'Meditation' in state_correlations and 'Post-Meditation' in state_correlations:
        print(f"\n  Meditation → Post-Meditation changes:")
        for metric1 in metrics:
            for metric2 in metrics:
                if metric1 < metric2:
                    med_corr = state_correlations['Meditation'].loc[metric1, metric2]
                    post_corr = state_correlations['Post-Meditation'].loc[metric1, metric2]
                    change = post_corr - med_corr
                    print(f"    {metric1} ↔ {metric2}: {med_corr:.3f} → {post_corr:.3f} (Δ{change:+.3f})")

print(f"\n{'='*80}")
print("KEY INSIGHTS")
print(f"{'='*80}")
print("1. Look for correlation sign changes between states (indicates different dynamics)")
print("2. Identify which metric relationships are most stable vs most variable")
print("3. Note if 9-9 shows distinctive correlation patterns compared to other experiments")
print("4. Check if meditation strengthens or weakens specific metric relationships")
