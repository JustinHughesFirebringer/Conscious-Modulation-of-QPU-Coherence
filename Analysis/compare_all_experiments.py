#!/usr/bin/env python3
"""
Compare distribution-derived proxy metrics across all experiments
Focus on distinctive patterns in inner register and correlations between metrics
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

print("="*80)
print("EXPERIMENT DATA OVERVIEW")
print("="*80)

data_dict = {}
for exp_name, csv_path in experiments.items():
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        data_dict[exp_name] = df
        print(f'{exp_name}:')
        print(f'  Total rows: {len(df)}')
        print(f'  Registers: {df["register"].unique()}')
        if 'phase' in df.columns:
            print(f'  Phases: {df["phase"].unique()}')
        print()
    else:
        print(f'{exp_name}: File not found')
        print()

print("="*80)
print("INNER REGISTER ANALYSIS (PENTAGON EXPERIMENTS)")
print("="*80)

pentagon_experiments = ['5-25_QPU', '7-11_QPU', '9-23_QPU', '9-9_QPU']
metrics = ['coherence', 'entanglement', 'interference', 'entropy']

for exp_name in pentagon_experiments:
    if exp_name in data_dict:
        df = data_dict[exp_name]
        inner_data = df[df['register'] == 'c_inner']
        
        print(f'\n{exp_name} - Inner Register:')
        print(f'  Data points: {len(inner_data)}')
        
        for metric in metrics:
            mean_val = inner_data[metric].mean()
            std_val = inner_data[metric].std()
            min_val = inner_data[metric].min()
            max_val = inner_data[metric].max()
            print(f'  {metric}: {mean_val:.4f} ± {std_val:.4f} (range: {min_val:.4f} - {max_val:.4f})')
        
        # Calculate correlations
        print(f'  Correlations:')
        corr_matrix = inner_data[metrics].corr()
        print(f'    Coherence-Entanglement: {corr_matrix.loc["coherence", "entanglement"]:.3f}')
        print(f'    Coherence-Entropy: {corr_matrix.loc["coherence", "entropy"]:.3f}')
        print(f'    Entanglement-Entropy: {corr_matrix.loc["entanglement", "entropy"]:.3f}')

print("\n" + "="*80)
print("4-20 EXPERIMENT (C/MEAS REGISTERS)")
print("="*80)

if '4-20_QPU' in data_dict:
    df = data_dict['4-20_QPU']
    for reg in ['c', 'meas']:
        reg_data = df[df['register'] == reg]
        print(f'\n{reg} Register:')
        print(f'  Data points: {len(reg_data)}')
        
        for metric in metrics:
            mean_val = reg_data[metric].mean()
            std_val = reg_data[metric].std()
            print(f'  {metric}: {mean_val:.4f} ± {std_val:.4f}')

print("\n" + "="*80)
print("TEMPORAL PATTERNS - PRE-MEDITATION VS DURING MEDITATION")
print("="*80)

# Analyze temporal patterns for experiments with phase data
for exp_name in ['7-11_QPU', '9-23_QPU', '9-9_QPU']:
    if exp_name in data_dict and 'phase' in data_dict[exp_name].columns:
        df = data_dict[exp_name]
        inner_data = df[df['register'] == 'c_inner']
        
        print(f'\n{exp_name} - Inner Register by Phase:')
        
        for phase in ['Control', 'Progressive Relaxation', 'Phase 1', 'Phase 2']:
            if phase in inner_data['phase'].values:
                phase_data = inner_data[inner_data['phase'] == phase]
                print(f'  {phase}: {len(phase_data)} points')
                for metric in ['coherence', 'entanglement']:
                    mean_val = phase_data[metric].mean()
                    print(f'    {metric}: {mean_val:.4f}')

print("\n" + "="*80)
print("KEY OBSERVATIONS")
print("="*80)
print("1. 9-9 shows distinctive ordering starting a few minutes prior to meditation")
print("2. 7-11 shows correlation-sign-flip between Coherence and Entanglement")
print("3. Inner register shows most distinctive signs in pentagonal resonance circuit")
print("4. Need to analyze temporal evolution patterns and phase transitions")
