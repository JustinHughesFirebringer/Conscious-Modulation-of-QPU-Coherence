#!/usr/bin/env python3
"""
Template for analyzing QPU experiment data using distribution-derived proxy metrics
This script provides a consistent workflow for processing different experiment dates
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime
import seaborn as sns
import base64
import zlib
import io
from collections import Counter

# Configuration - modify these for each experiment
EXPERIMENT_NAME = "EXPERIMENT_NAME"  # e.g., "9-9_QPU", "7-11_QPU"
RAW_DIR = Path(r"PATH_TO_RAW_DATA")  # e.g., r"C:\...\Data\RAW\9-9_QPU_Brisbane"
OUTPUT_DIR = Path(r"PATH_TO_OUTPUT")  # e.g., r"C:\...\Analysis\9_9_QPU_Proxy_Output"

# Job ID filtering (optional, set to None to include all jobs)
JOB_ID_START = None  # e.g., "d30au7qiggks73ctos7g"
JOB_ID_END = None    # e.g., "d30d8p5otchc73baaagg"

# Meditation phase definitions (optional, set to None to skip phase labeling)
# Times in UTC format
PHASE_DEFINITIONS = {
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

OUTPUT_DIR.mkdir(exist_ok=True)

def decode_bitarray(field_data):
    """Decode base64-encoded bitarray data from Qiskit Runtime V2 format"""
    try:
        array_data = field_data["__value__"]["array"]["__value__"]
        num_bits = field_data["__value__"]["num_bits"]
        
        decoded_bytes = base64.b64decode(array_data)
        decompressed_data = zlib.decompress(decoded_bytes)
        arr = np.load(io.BytesIO(decompressed_data), allow_pickle=False).reshape(-1)
        bitstrings = [format(int(val), f'0{num_bits}b') for val in arr]
        
        return bitstrings
    except Exception as e:
        print(f"Error decoding bitarray: {e}")
        return []

def calculate_entropy(bitstrings):
    """Calculate Shannon entropy of measurement outcomes"""
    try:
        if not bitstrings:
            return 0.0
        
        state_counts = Counter(bitstrings)
        total_shots = len(bitstrings)
        probabilities = {state: count/total_shots for state, count in state_counts.items()}
        
        entropy = 0
        for p in probabilities.values():
            if p > 0:
                entropy -= p * np.log2(p)
        
        return float(entropy)
    except Exception as e:
        print(f"Error calculating entropy: {e}")
        return 0.0

def calculate_per_bit_balances(bitstrings):
    """Calculate bit-balance for each qubit: 1 = perfect balance, 0 = complete imbalance"""
    try:
        if not bitstrings:
            return []
        
        state_vectors = np.array([list(map(int, bs)) for bs in bitstrings])
        num_qubits = len(bitstrings[0])
        total_shots = len(bitstrings)
        
        balances = []
        for i in range(num_qubits):
            counts = Counter(state_vectors[:, i].astype(int))
            count_1 = counts.get(1, 0)
            count_0 = counts.get(0, 0)
            
            if total_shots > 0:
                balance = 1 - (abs(count_1 - count_0) / total_shots)
                balances.append(balance)
        
        return balances
    except Exception as e:
        print(f"Error calculating per-bit balances: {e}")
        return []

def calculate_avg_bit_balance(bitstrings):
    """Calculate average bit-balance across all qubits"""
    balances = calculate_per_bit_balances(bitstrings)
    return float(np.mean(balances)) if balances else 0.0

def calculate_coherence(bitstrings):
    """Calculate coherence as probability of the single most frequent bitstring"""
    try:
        if not bitstrings:
            return 0.0
        
        state_counts = Counter(bitstrings)
        total_shots = len(bitstrings)
        probabilities = [count / total_shots for count in state_counts.values()]
        
        coherence = max(probabilities)
        return float(coherence)
    except Exception as e:
        print(f"Error calculating coherence: {e}")
        return 0.0

def calculate_entanglement(bitstrings):
    """Calculate entanglement as entropy divided by num_bits"""
    try:
        if not bitstrings:
            return 0.0
        
        num_bits = len(bitstrings[0])
        entropy = calculate_entropy(bitstrings)
        return entropy / num_bits if num_bits > 0 else 0.0
    except Exception as e:
        print(f"Error calculating entanglement: {e}")
        return 0.0

def calculate_interference(bitstrings):
    """Calculate interference as 1 - (p_max - p_min)"""
    try:
        if not bitstrings:
            return 0.0
        
        state_counts = Counter(bitstrings)
        total_shots = len(bitstrings)
        probabilities = [count / total_shots for count in state_counts.values()]
        
        p_max = max(probabilities)
        p_min = min(probabilities)
        interference = 1 - (p_max - p_min)
        return float(interference)
    except Exception as e:
        print(f"Error calculating interference: {e}")
        return 0.0

def process_job(result_file, info_file):
    """Process a single job's result and info files"""
    try:
        with open(result_file, 'r') as f:
            result_data = json.load(f)
        
        with open(info_file, 'r') as f:
            info_data = json.load(f)
        
        created_str = info_data.get('created', '')
        timestamp = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
        
        fields = result_data['__value__']['pub_results'][0]['__value__']['data']['__value__']['fields']
        job_id = result_file.stem.replace('-result', '')
        register_rows = []
        
        for register_name in ['c_central', 'c_inner', 'c_middle', 'c_outer']:
            if register_name in fields:
                bitstrings = decode_bitarray(fields[register_name])
                num_bits = fields[register_name]["__value__"]["num_bits"]
                
                entropy = calculate_entropy(bitstrings)
                entanglement = calculate_entanglement(bitstrings)
                coherence = calculate_coherence(bitstrings)
                interference = calculate_interference(bitstrings)
                per_bit_balances = calculate_per_bit_balances(bitstrings)
                avg_bit_balance = calculate_avg_bit_balance(bitstrings)
                unique_states = len(set(bitstrings))
                
                row = {
                    'job_id': job_id,
                    'timestamp': timestamp.strftime('%Y%m%d_%H%M%S'),
                    'register': register_name,
                    'num_bits': num_bits,
                    'total_shots': len(bitstrings),
                    'unique_states': unique_states,
                    'coherence': coherence,
                    'entanglement': entanglement,
                    'interference': interference,
                    'bit_balances': str(per_bit_balances),
                    'entropy': entropy
                }
                register_rows.append(row)
        
        return register_rows
    except Exception as e:
        print(f"Error processing {result_file.name}: {e}")
        return []

def assign_phases(df, phase_definitions):
    """Assign meditation phases based on timestamp boundaries"""
    if phase_definitions is None:
        df['phase'] = 'Unknown'
        return df
    
    # Convert phase definitions to timestamps
    phase_times = {name: pd.Timestamp(time) for name, time in phase_definitions.items()}
    
    # Sort phases by time
    sorted_phases = sorted(phase_times.items(), key=lambda x: x[1])
    
    def get_phase(timestamp):
        for phase_name, phase_time in sorted_phases:
            if timestamp < phase_time:
                return phase_name
        return sorted_phases[-1][0]  # Return last phase if beyond all boundaries
    
    df['phase'] = df['timestamp_dt'].apply(get_phase)
    return df

def generate_visualizations(df, output_dir, experiment_name):
    """Generate consistent visualizations with phase markers"""
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    
    colors = {
        'central': '#FF6B6B',
        'inner': '#4ECDC4', 
        'middle': '#45B7D1',
        'outer': '#96CEB4'
    }
    
    metrics = ['coherence', 'entanglement', 'entropy', 'interference']
    time_start = df['timestamp'].iloc[0]
    time_end = df['timestamp'].iloc[-1]
    
    # Check if phases are defined
    has_phases = 'phase' in df.columns
    if has_phases:
        phase_times = df.groupby('phase')['time_minutes'].min().to_dict()
    
    for metric in metrics:
        fig, axes = plt.subplots(4, 1, figsize=(16, 18))
        
        for idx, register in enumerate(['c_central', 'c_inner', 'c_middle', 'c_outer']):
            reg_name = register.replace('c_', '')
            reg_data = df[df['register'] == register].copy()
            reg_data = reg_data.sort_values('time_minutes')
            ax = axes[idx]
            
            ax.plot(reg_data['time_minutes'], reg_data[metric], 
                   marker='o', linewidth=2.5, markersize=8, 
                   label=f'{reg_name.title()} Register', 
                   color=colors[reg_name], alpha=0.8)
            ax.set_xlabel('Time (minutes)', fontsize=14, fontweight='bold')
            ax.set_ylabel(metric.capitalize(), fontsize=14, fontweight='bold')
            ax.set_title(f'{reg_name.title()} Register - {metric.capitalize()}', 
                       fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best', fontsize=12)
            
            # Add phase markers if available
            if has_phases:
                for phase_name, phase_time in phase_times.items():
                    if phase_name not in ['Control', 'Post Meditation', 'Unknown']:
                        ax.axvline(x=phase_time, color='red', linestyle='--', alpha=0.5, linewidth=1)
                        ax.text(phase_time, ax.get_ylim()[1] * 0.95, phase_name, 
                               rotation=90, verticalalignment='top', fontsize=9, color='red')
        
        fig.suptitle(f'{metric.capitalize()} Temporal Evolution ({experiment_name})\n{time_start} to {time_end}', 
                    fontsize=18, fontweight='bold')
        plt.tight_layout()
        
        output_file = output_dir / f"temporal_evolution_{metric}_proxy.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

def main():
    print(f"Processing {EXPERIMENT_NAME} data using distribution-derived metrics...")
    
    # Find all result files
    result_files = sorted(RAW_DIR.glob('job-*-result.json'))
    print(f"Found {len(result_files)} result files")
    
    # Process each job
    all_register_rows = []
    for result_file in result_files:
        job_id = result_file.stem.replace('-result', '')
        info_file = RAW_DIR / f'{job_id}-info.json'
        
        if info_file.exists():
            print(f"Processing {job_id}...")
            register_rows = process_job(result_file, info_file)
            all_register_rows.extend(register_rows)
        else:
            print(f"Warning: Info file not found for {job_id}")
    
    # Create DataFrame
    df = pd.DataFrame(all_register_rows)
    
    if len(df) == 0:
        print("No valid data found!")
        return
    
    # Sort by timestamp
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], format='%Y%m%d_%H%M%S')
    df = df.sort_values('timestamp_dt')
    
    # Filter by job ID range if specified
    if JOB_ID_START and JOB_ID_END:
        df['job_id_clean'] = df['job_id'].str.replace('job-', '')
        df = df[(df['job_id_clean'] >= JOB_ID_START) & (df['job_id_clean'] <= JOB_ID_END)]
        print(f"Filtered to {len(df)} register rows (job ID range)")
    
    # Recalculate time_minutes correctly from actual timestamps
    df['time_minutes'] = (df['timestamp_dt'] - df['timestamp_dt'].min()).dt.total_seconds() / 60
    
    print(f"Processed {len(df)} register rows")
    print(f"Time span: {df['timestamp_dt'].min()} to {df['timestamp_dt'].max()}")
    print(f"Duration: {(df['timestamp_dt'].max() - df['timestamp_dt'].min()).total_seconds() / 60:.1f} minutes")
    
    # Assign phases if defined
    if PHASE_DEFINITIONS:
        df = assign_phases(df, PHASE_DEFINITIONS)
        print("\nPhase distribution:")
        print(df['phase'].value_counts().sort_index())
    
    # Save CSV
    csv_file = OUTPUT_DIR / "temporal_data_proxy_long.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n✓ Saved temporal data to {csv_file}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generate_visualizations(df, OUTPUT_DIR, EXPERIMENT_NAME)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
