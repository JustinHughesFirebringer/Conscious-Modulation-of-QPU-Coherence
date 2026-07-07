#!/usr/bin/env python3
"""
Combined analysis of 9-9 Brisbane and Torino quantum metrics
Compare quantum metrics across both backends with phase classification
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from scipy import stats

# Phase definitions for 9-9 (Central timezone converted to UTC)
# Brisbane session: 2025-09-09 23:15-00:55 UTC
# Torino session: 2025-09-09 21:27-22:58 UTC (assume same meditation timing shifted)
phase_definitions = {
    'brisbane': {
        'Control': '2025-09-09T23:15:00',
        'Meditation': '2025-09-09T23:33:00',
        'Post-Meditation': '2025-09-10T00:55:00'
    },
    'torino': {
        'Control': '2025-09-09T21:27:00',
        'Meditation': '2025-09-09T21:45:00',
        'Post-Meditation': '2025-09-09T22:58:00'
    }
}

def classify_state(timestamp, phase_defs):
    """Classify job state based on timestamp and phase definitions"""
    if phase_defs is None:
        return 'Unknown'
    
    control_time = datetime.fromisoformat(phase_defs['Control'])
    meditation_time = datetime.fromisoformat(phase_defs['Meditation'])
    post_time = datetime.fromisoformat(phase_defs['Post-Meditation'])
    
    if timestamp < control_time:
        return 'Pre-Control'
    elif timestamp < meditation_time:
        return 'Control'
    elif timestamp < post_time:
        return 'Meditation'
    else:
        return 'Post-Meditation'

def load_summary_data(summary_file, backend_name, phase_defs):
    """Load summary data and add phase classification"""
    with open(summary_file, 'r') as f:
        data = json.load(f)
    
    jobs_data = []
    for job in data['jobs']:
        timestamp = datetime.fromisoformat(job['timestamp'])
        state = classify_state(timestamp, phase_defs)
        
        for layer, metrics in job['layers'].items():
            jobs_data.append({
                'backend': backend_name,
                'job_id': job['job_id'],
                'timestamp': timestamp,
                'state': state,
                'layer': layer,
                'coherence': metrics['coherence'],
                'entanglement': metrics['entanglement'],
                'interference': metrics['interference'],
                'num_shots': metrics['num_shots']
            })
    
    return pd.DataFrame(jobs_data)

def main():
    base_dir = Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis')
    
    # Load both datasets
    brisbane_file = base_dir / '9_9_QPU_Quantum_Metrics_FIXED' / '9-9 summary.json'
    torino_file = base_dir / '9_9_Torino_Quantum_Metrics' / 'summary.json'
    
    print("Loading Brisbane data...")
    df_brisbane = load_summary_data(brisbane_file, 'Brisbane', phase_definitions['brisbane'])
    print(f"Brisbane: {len(df_brisbane)} data points from {df_brisbane['job_id'].nunique()} jobs")
    
    print("Loading Torino data...")
    df_torino = load_summary_data(torino_file, 'Torino', phase_definitions['torino'])
    print(f"Torino: {len(df_torino)} data points from {df_torino['job_id'].nunique()} jobs")
    
    # Combine datasets
    df_combined = pd.concat([df_brisbane, df_torino], ignore_index=True)
    print(f"Combined: {len(df_combined)} data points from {df_combined['job_id'].nunique()} jobs")
    
    # State distribution by backend
    print("\n" + "="*80)
    print("STATE DISTRIBUTION BY BACKEND")
    print("="*80)
    for backend in ['Brisbane', 'Torino']:
        backend_data = df_combined[df_combined['backend'] == backend]
        state_counts = backend_data.groupby('state')['job_id'].nunique()
        print(f"\n{backend}:")
        for state, count in state_counts.items():
            print(f"  {state}: {count} jobs")
    
    # Comparative statistics by backend and state
    print("\n" + "="*80)
    print("COMPARATIVE STATISTICS BY BACKEND AND STATE")
    print("="*80)
    
    layers = ['central', 'inner', 'middle', 'outer']
    metrics = ['coherence', 'entanglement', 'interference']
    
    for layer in layers:
        print(f"\n{layer.upper()} REGISTER:")
        print("-" * 80)
        
        for metric in metrics:
            print(f"\n{metric.capitalize()}:")
            
            for backend in ['Brisbane', 'Torino']:
                backend_data = df_combined[(df_combined['backend'] == backend) & (df_combined['layer'] == layer)]
                
                print(f"  {backend}:")
                for state in ['Control', 'Meditation', 'Post-Meditation']:
                    state_data = backend_data[backend_data['state'] == state]
                    if len(state_data) > 0:
                        mean_val = state_data[metric].mean()
                        std_val = state_data[metric].std()
                        count = len(state_data)
                        print(f"    {state}: {mean_val:.6f} ± {std_val:.6f} (n={count})")
                    else:
                        print(f"    {state}: No data")
    
    # Statistical tests comparing backends
    print("\n" + "="*80)
    print("STATISTICAL TESTS: BACKEND COMPARISON")
    print("="*80)
    
    for layer in layers:
        print(f"\n{layer.upper()} REGISTER:")
        print("-" * 80)
        
        for metric in metrics:
            print(f"\n{metric.capitalize()}:")
            
            for state in ['Control', 'Meditation', 'Post-Meditation']:
                brisbane_data = df_combined[(df_combined['backend'] == 'Brisbane') & 
                                          (df_combined['layer'] == layer) & 
                                          (df_combined['state'] == state)][metric].values
                torino_data = df_combined[(df_combined['backend'] == 'Torino') & 
                                        (df_combined['layer'] == layer) & 
                                        (df_combined['state'] == state)][metric].values
                
                if len(brisbane_data) > 0 and len(torino_data) > 0:
                    try:
                        t_stat, p_val = stats.ttest_ind(brisbane_data, torino_data)
                        print(f"  {state}: t={t_stat:.3f}, p={p_val:.4f} {'***' if p_val < 0.05 else ''}")
                    except:
                        print(f"  {state}: Unable to compute")
                else:
                    print(f"  {state}: Insufficient data")
    
    # Create visualizations
    print("\n" + "="*80)
    print("CREATING VISUALIZATIONS")
    print("="*80)
    
    output_dir = base_dir / '9_9_Combined_Analysis'
    output_dir.mkdir(exist_ok=True)
    
    # Set style
    sns.set_style("whitegrid")
    
    # 1. Time series plots by backend
    for layer in layers:
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle(f'{layer.capitalize()} Register - Time Series by Backend', fontsize=14)
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            for backend in ['Brisbane', 'Torino']:
                backend_data = df_combined[(df_combined['backend'] == backend) & 
                                          (df_combined['layer'] == layer)]
                
                # Group by job and plot
                job_means = backend_data.groupby('job_id').agg({
                    'timestamp': 'first',
                    metric: 'mean',
                    'state': 'first'
                }).sort_values('timestamp')
                
                # Color by state
                colors = {'Pre-Control': 'gray', 'Control': 'blue', 'Meditation': 'orange', 'Post-Meditation': 'green'}
                for state in job_means['state'].unique():
                    state_data = job_means[job_means['state'] == state]
                    ax.scatter(state_data['timestamp'], state_data[metric], 
                              label=f'{backend} {state}', color=colors.get(state, 'black'), 
                              alpha=0.7, marker='o' if backend == 'Brisbane' else 's')
            
            ax.set_ylabel(metric.capitalize())
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / f'{layer}_timeseries.png', dpi=150)
        plt.close()
        print(f"Saved {layer}_timeseries.png")
    
    # 2. Box plots comparing backends by state
    for layer in layers:
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(f'{layer.capitalize()} Register - Backend Comparison by State', fontsize=14)
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            
            # Filter data for this layer and metric
            plot_data = df_combined[(df_combined['layer'] == layer)].copy()
            
            # Only plot states with data
            plot_data = plot_data[plot_data['state'].isin(['Control', 'Meditation', 'Post-Meditation'])]
            
            if len(plot_data) > 0:
                sns.boxplot(data=plot_data, x='state', y=metric, hue='backend', ax=ax)
                ax.set_ylabel(metric.capitalize())
                ax.set_xlabel('State')
                ax.legend(title='Backend')
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / f'{layer}_boxplot.png', dpi=150)
        plt.close()
        print(f"Saved {layer}_boxplot.png")
    
    # 3. Correlation heatmap by backend
    for backend in ['Brisbane', 'Torino']:
        backend_data = df_combined[df_combined['backend'] == backend]
        
        # Calculate correlations for inner register
        inner_data = backend_data[backend_data['layer'] == 'inner']
        if len(inner_data) > 0:
            corr_matrix = inner_data[metrics].corr()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                       square=True, ax=ax, vmin=-1, vmax=1)
            ax.set_title(f'{backend} - Inner Register Correlations')
            plt.tight_layout()
            plt.savefig(output_dir / f'{backend.lower()}_correlations.png', dpi=150)
            plt.close()
            print(f"Saved {backend.lower()}_correlations.png")
    
    # Save combined summary with full job data
    summary_file = output_dir / 'combined_summary.json'
    
    # Combine job data from both backends
    combined_jobs = []
    for backend in ['Brisbane', 'Torino']:
        backend_data = df_combined[df_combined['backend'] == backend]
        for job_id in backend_data['job_id'].unique():
            job_data = backend_data[backend_data['job_id'] == job_id].iloc[0]
            job_entry = {
                'backend': backend,
                'job_id': job_id,
                'timestamp': str(job_data['timestamp']),
                'state': job_data['state'],
                'layers': {}
            }
            
            # Add layer metrics
            job_layers = backend_data[backend_data['job_id'] == job_id]
            for _, layer_row in job_layers.iterrows():
                job_entry['layers'][layer_row['layer']] = {
                    'coherence': layer_row['coherence'],
                    'entanglement': layer_row['entanglement'],
                    'interference': layer_row['interference'],
                    'num_shots': layer_row['num_shots']
                }
            
            combined_jobs.append(job_entry)
    
    combined_summary = {
        'timestamp': datetime.now().isoformat(),
        'brisbane_jobs': df_brisbane['job_id'].nunique(),
        'torino_jobs': df_torino['job_id'].nunique(),
        'total_jobs': df_combined['job_id'].nunique(),
        'brisbane_time_range': [str(df_brisbane['timestamp'].min()), str(df_brisbane['timestamp'].max())],
        'torino_time_range': [str(df_torino['timestamp'].min()), str(df_torino['timestamp'].max())],
        'jobs': combined_jobs
    }
    
    with open(summary_file, 'w') as f:
        json.dump(combined_summary, f, indent=2)
    
    print(f"\nCombined analysis saved to {output_dir}")
    print(f"Summary saved to {summary_file}")

if __name__ == '__main__':
    main()
