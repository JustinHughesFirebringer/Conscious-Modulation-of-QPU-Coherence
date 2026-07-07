"""
Analyze quantum metrics by meditation phase (Control, Meditation, Post-Meditation)
for 7-11, 9-9, and 9-23 sessions to identify any impact on measurements per register.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from scipy import stats

# Phase definitions based on actual experiment data provided by user
# User provided times in Central timezone, converted to UTC (Central = UTC-5)
phase_definitions = {
    '7-11_QPU': {
        'Control': '2025-07-12T03:00:00',
        'Meditation': '2025-07-12T03:14:00',  # 10:14PM Central = 03:14 UTC
        'Post-Meditation': '2025-07-12T03:36:00'  # 10:36PM Central = 03:36 UTC
    },
    '9-23_QPU': {
        'Control': '2025-09-23T21:50:00',
        'Meditation': '2025-09-23T22:00:00',  # 5:00PM Central = 22:00 UTC
        'Post-Meditation': '2025-09-23T22:30:00'  # 5:30PM Central = 22:30 UTC
    },
    '9-9_QPU': {
        'Control': '2025-09-09T21:30:00',
        'Meditation': '2025-09-09T23:33:00',  # 6:33PM Central = 23:33 UTC
        'Post-Meditation': '2025-09-10T00:55:00'  # 7:55PM Central = 00:55 UTC next day
    }
}

def classify_state(timestamp, phase_defs):
    """Classify job state based on timestamp and phase definitions"""
    if phase_defs is None:
        return 'Unknown'
    
    control_time = datetime.fromisoformat(phase_defs['Control'])
    meditation_time = datetime.fromisoformat(phase_defs['Meditation'])
    post_meditation_time = datetime.fromisoformat(phase_defs['Post-Meditation'])
    
    if timestamp < meditation_time:
        return 'Control'
    elif timestamp < post_meditation_time:
        return 'Meditation'
    else:
        return 'Post-Meditation'

def auto_determine_phases(timestamps):
    """Automatically determine phase boundaries based on timestamp distribution"""
    if len(timestamps) < 3:
        return None
    
    sorted_times = sorted(timestamps)
    n = len(sorted_times)
    
    # Simple approach: divide into thirds
    control_end = sorted_times[n // 3]
    meditation_end = sorted_times[2 * n // 3]
    
    return {
        'Control': control_end.isoformat(),
        'Meditation': meditation_end.isoformat(),
        'Post-Meditation': sorted_times[-1].isoformat()
    }

def load_and_analyze_session(session_name, summary_file, phase_defs):
    """Load summary.json and analyze metrics by phase"""
    with open(summary_file, 'r') as f:
        data = json.load(f)
    
    # Extract all timestamps first
    all_timestamps = [datetime.fromisoformat(job['timestamp']) for job in data['jobs']]
    
    # Auto-determine phases if not provided or if they don't match data
    if phase_defs is None:
        phase_defs = auto_determine_phases(all_timestamps)
        print(f"Auto-determined phases for {session_name}: {phase_defs}")
    else:
        # Check if provided phases make sense for the data
        control_time = datetime.fromisoformat(phase_defs['Control'])
        meditation_time = datetime.fromisoformat(phase_defs['Meditation'])
        post_time = datetime.fromisoformat(phase_defs['Post-Meditation'])
        
        if control_time > all_timestamps[-1] or meditation_time > all_timestamps[-1]:
            print(f"Provided phases don't match data timestamps, auto-determining...")
            phase_defs = auto_determine_phases(all_timestamps)
            print(f"Auto-determined phases for {session_name}: {phase_defs}")
    
    # Extract job data with phase classification
    jobs_data = []
    for job in data['jobs']:
        timestamp = datetime.fromisoformat(job['timestamp'])
        state = classify_state(timestamp, phase_defs)
        
        for layer, metrics in job['layers'].items():
            jobs_data.append({
                'job_id': job['job_id'],
                'timestamp': timestamp,
                'state': state,
                'layer': layer,
                'coherence': metrics['coherence'],
                'entanglement': metrics['entanglement'],
                'interference': metrics['interference']
            })
    
    df = pd.DataFrame(jobs_data)
    
    # Count unique jobs by state (not rows, since each job has multiple layers)
    job_counts = df.groupby('state')['job_id'].nunique()
    
    # Calculate statistics by state and layer
    results = {}
    layers = ['central', 'inner', 'middle', 'outer']
    metrics = ['coherence', 'entanglement', 'interference']
    states = ['Control', 'Meditation', 'Post-Meditation']
    
    for layer in layers:
        if layer not in df['layer'].values:
            continue
            
        layer_data = df[df['layer'] == layer]
        results[layer] = {}
        
        for metric in metrics:
            results[layer][metric] = {}
            
            for state in states:
                state_data = layer_data[layer_data['state'] == state]
                if len(state_data) > 0:
                    results[layer][metric][state] = {
                        'mean': state_data[metric].mean(),
                        'std': state_data[metric].std(),
                        'min': state_data[metric].min(),
                        'max': state_data[metric].max(),
                        'count': len(state_data)
                    }
                else:
                    results[layer][metric][state] = None
    
    return df, results, job_counts

def print_session_analysis(session_name, df, results, job_counts):
    """Print analysis results for a session"""
    print(f"\n{'='*80}")
    print(f"{session_name} - Phase Impact Analysis")
    print(f"{'='*80}")
    
    layers = ['central', 'inner', 'middle', 'outer']
    metrics = ['coherence', 'entanglement', 'interference']
    states = ['Control', 'Meditation', 'Post-Meditation']
    
    # Print job counts by state
    print(f"\nJob counts by state:")
    for state in states:
        count = job_counts.get(state, 0)
        print(f"  {state}: {count} jobs")
    
    # Print metrics by layer and state
    for layer in layers:
        if layer not in results:
            continue
            
        print(f"\n{layer.upper()} REGISTER:")
        print(f"{'-'*80}")
        
        for metric in metrics:
            print(f"\n{metric.capitalize()}:")
            
            # Get values for each state
            control_val = results[layer][metric]['Control']
            meditation_val = results[layer][metric]['Meditation']
            post_val = results[layer][metric]['Post-Meditation']
            
            if control_val and meditation_val and post_val:
                control_mean = control_val['mean']
                meditation_mean = meditation_val['mean']
                post_mean = post_val['mean']
                
                # Calculate changes
                control_to_meditation = ((meditation_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
                meditation_to_post = ((post_mean - meditation_mean) / meditation_mean * 100) if meditation_mean != 0 else 0
                control_to_post = ((post_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
                
                print(f"  Control:       {control_mean:.6f} ± {control_val['std']:.6f} (n={control_val['count']})")
                print(f"  Meditation:    {meditation_mean:.6f} ± {meditation_val['std']:.6f} (n={meditation_val['count']})")
                print(f"  Post-Meditation: {post_mean:.6f} ± {post_val['std']:.6f} (n={post_val['count']})")
                print(f"  Control→Meditation: {control_to_meditation:+.2f}%")
                print(f"  Meditation→Post: {meditation_to_post:+.2f}%")
                print(f"  Control→Post: {control_to_post:+.2f}%")
                
                # Perform statistical tests
                control_data = df[(df['layer'] == layer) & (df['state'] == 'Control')][metric].values
                meditation_data = df[(df['layer'] == layer) & (df['state'] == 'Meditation')][metric].values
                post_data = df[(df['layer'] == layer) & (df['state'] == 'Post-Meditation')][metric].values
                
                print(f"\n  Statistical Tests:")
                
                # T-tests for pairwise comparisons
                try:
                    t_stat, p_val = stats.ttest_ind(control_data, meditation_data)
                    print(f"    T-test (Control vs Meditation): t={t_stat:.3f}, p={p_val:.4f} {'***' if p_val < 0.05 else ''}")
                except:
                    print(f"    T-test (Control vs Meditation): Unable to compute")
                
                try:
                    t_stat, p_val = stats.ttest_ind(meditation_data, post_data)
                    print(f"    T-test (Meditation vs Post): t={t_stat:.3f}, p={p_val:.4f} {'***' if p_val < 0.05 else ''}")
                except:
                    print(f"    T-test (Meditation vs Post): Unable to compute")
                
                try:
                    t_stat, p_val = stats.ttest_ind(control_data, post_data)
                    print(f"    T-test (Control vs Post): t={t_stat:.3f}, p={p_val:.4f} {'***' if p_val < 0.05 else ''}")
                except:
                    print(f"    T-test (Control vs Post): Unable to compute")
                
                # ANOVA for overall phase effect
                try:
                    f_stat, p_val = stats.f_oneway(control_data, meditation_data, post_data)
                    print(f"    ANOVA (overall phase effect): F={f_stat:.3f}, p={p_val:.4f} {'***' if p_val < 0.05 else ''}")
                except:
                    print(f"    ANOVA (overall phase effect): Unable to compute")
                
                # Highlight significant changes (>10%)
                if abs(control_to_meditation) > 10:
                    print(f"  *** SIGNIFICANT CHANGE: Control→Meditation ({control_to_meditation:+.2f}%) ***")
                if abs(meditation_to_post) > 10:
                    print(f"  *** SIGNIFICANT CHANGE: Meditation→Post ({meditation_to_post:+.2f}%) ***")
            else:
                print(f"  Insufficient data for comparison")

def main():
    base_dir = Path(r'C:\Users\bigre\CascadeProjects\QuantumConsciousnessAI\quantum_intelligence_interface\Clean_Repo\Analysis')
    
    # Use actual provided phase boundaries from experiment metadata
    # 4-20_QPU excluded due to different data structure (no pentagon layers)
    # 5-25_QPU excluded due to no phase definitions available
    sessions = [
        ('7-11_QPU', base_dir / '7_11_QPU_Quantum_Metrics_FIXED' / '7-11 summary.json', phase_definitions['7-11_QPU']),
        ('9-9_QPU', base_dir / '9_9_QPU_Quantum_Metrics_FIXED' / '9-9 summary.json', phase_definitions['9-9_QPU']),
        ('9-23_QPU', base_dir / '9_23_QPU_Quantum_Metrics_FIXED' / '9-23 summary.json', phase_definitions['9-23_QPU'])
    ]
    
    all_results = {}
    
    for session_name, summary_file, phase_defs in sessions:
        if summary_file.exists():
            df, results, job_counts = load_and_analyze_session(session_name, summary_file, phase_defs)
            print_session_analysis(session_name, df, results, job_counts)
            all_results[session_name] = {'df': df, 'results': results}
        else:
            print(f"Summary file not found: {summary_file}")
    
    # Generate summary of significant findings
    print(f"\n{'='*80}")
    print("SUMMARY OF SIGNIFICANT FINDINGS")
    print(f"{'='*80}")
    print("Note: Using actual provided phase boundaries from experiment metadata")
    print("Note: 4-20_QPU excluded due to different data structure (no pentagon layers)")
    print("Note: 5-25_QPU excluded due to no phase definitions available")
    
    for session_name, data in all_results.items():
        results = data['results']
        print(f"\n{session_name}:")
        
        layers = ['central', 'inner', 'middle', 'outer']
        metrics = ['coherence', 'entanglement', 'interference']
        
        for layer in layers:
            if layer not in results:
                continue
                
            for metric in metrics:
                control_val = results[layer][metric]['Control']
                meditation_val = results[layer][metric]['Meditation']
                post_val = results[layer][metric]['Post-Meditation']
                
                if control_val and meditation_val and post_val:
                    control_mean = control_val['mean']
                    meditation_mean = meditation_val['mean']
                    post_mean = post_val['mean']
                    
                    control_to_meditation = ((meditation_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
                    meditation_to_post = ((post_mean - meditation_mean) / meditation_mean * 100) if meditation_mean != 0 else 0
                    
                    if abs(control_to_meditation) > 10 or abs(meditation_to_post) > 10:
                        print(f"  {layer} {metric}:")
                        if abs(control_to_meditation) > 10:
                            print(f"    Control→Meditation: {control_to_meditation:+.2f}%")
                        if abs(meditation_to_post) > 10:
                            print(f"    Meditation→Post: {meditation_to_post:+.2f}%")

if __name__ == '__main__':
    main()
