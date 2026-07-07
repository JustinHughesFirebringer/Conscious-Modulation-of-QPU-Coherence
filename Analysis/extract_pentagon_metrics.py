#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract Quantum Metrics from Pentagon Resonance Circuit Results

This script analyzes IBM Quantum job result files from the pentagon resonance circuit
to extract accurate quantum metrics for each pentagon layer:
- Coherence
- Entanglement
- Interference

It processes the raw measurement data directly from the result files.
"""

import os
import json
import argparse
import base64
import numpy as np
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from scipy.fft import fft
from datetime import datetime
import zlib
import io

# Pentagon layer information
PENTAGON_LAYERS = {
    "c_central": {"qubits": 1, "name": "Central Qubit"},
    "c_inner": {"qubits": 5, "name": "Inner Pentagon"},
    "c_middle": {"qubits": 5, "name": "Middle Pentagon"},
    "c_outer": {"qubits": 5, "name": "Outer Pentagon"}
}

def extract_layer_bitstrings(result_file):
    """
    Extract bitstrings for each pentagon layer from an IBM Quantum Runtime V2 job result file
    
    Args:
        result_file: Path to the job result file
        
    Returns:
        Dictionary with layer names as keys and lists of bitstrings as values
    """
    try:
        # Load the result JSON
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        # Extract the field data from the IBM Quantum Runtime V2 format
        if "__type__" in data and data["__type__"] == "PrimitiveResult":
            pub_results = data["__value__"]["pub_results"]
            
            if pub_results and "__type__" in pub_results[0] and pub_results[0]["__type__"] == "SamplerPubResult":
                data_bin = pub_results[0]["__value__"]["data"]
                
                if data_bin["__type__"] == "DataBin":
                    fields = data_bin["__value__"]["fields"]
                    field_names = data_bin["__value__"]["field_names"]
                    
                    print(f"Found registers: {field_names}")
                    
                    # Dictionary to store bitstrings for each layer
                    layer_bitstrings = {}
                    
                    # Process each field (register)
                    for field_name in field_names:
                        if field_name in fields:
                            field_data = fields[field_name]
                            if field_data["__type__"] == "BitArray":
                                # Get the array data from the ndarray value
                                array_data = field_data["__value__"]["array"]["__value__"]
                                num_bits = field_data["__value__"]["num_bits"]
                                
                                # Decode the base64 data
                                decoded_bytes = base64.b64decode(array_data)
                                
                                # Decompress with zlib
                                decompressed_data = zlib.decompress(decoded_bytes)
                                
                                # Load as numpy array (the decompressed data is a serialized .npy file)
                                arr = np.load(io.BytesIO(decompressed_data), allow_pickle=False).reshape(-1)
                                
                                # Convert to bitstrings
                                bitstrings = [format(int(val), f'0{num_bits}b') for val in arr]
                                
                                print(f"Extracted {len(bitstrings)} shots with {num_bits} bits each for {field_name}")
                                
                                # Store in layer_bitstrings dictionary
                                layer_bitstrings[field_name] = bitstrings
                    
                    return layer_bitstrings
                else:
                    print("Error: Could not find DataBin in the result file.")
            else:
                print("Error: Could not find SamplerPubResult in the result file.")
        else:
            print("Error: Invalid result file format. Expected PrimitiveResult type.")
    
    except Exception as e:
        print(f"Error processing {result_file}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return {}

def calculate_coherence(bitstrings):
    """Calculate quantum coherence based on measurement outcomes.
    
    Args:
        bitstrings: List of bitstrings
        
    Returns:
        Coherence value (0-1)
    """
    try:
        # Convert bitstrings to state vectors
        state_vectors = np.array([list(map(int, bs)) for bs in bitstrings])
        
        # Calculate density matrix
        num_qubits = len(bitstrings[0])
        total_shots = len(bitstrings)
        
        # Calculate purity for each qubit
        purities = []
        for i in range(num_qubits):
            # Get probabilities for qubit i
            counts = Counter(state_vectors[:, i].astype(int))
            probabilities = {state: count/total_shots for state, count in counts.items()}
            
            # Calculate purity contribution
            purity = sum(p*p for p in probabilities.values())
            purities.append(purity)
        
        # Calculate average purity
        avg_purity = np.mean(purities)
        
        # Convert to coherence measure (0-1)
        # Purity of 0.5 means completely mixed state (no coherence)
        # Purity of 1.0 means pure state (maximum coherence)
        coherence = 2 * (avg_purity - 0.5) if avg_purity > 0.5 else 0.0
        
        return float(coherence)
    except Exception as e:
        print(f"Error calculating coherence: {e}")
        return 0.0

def calculate_bit_correlations(bitstrings):
    """
    Calculate correlations between bit positions.
    
    Args:
        bitstrings: List of bitstrings
        
    Returns:
        Correlation matrix
    """
    if not bitstrings or len(bitstrings) == 0:
        return np.zeros((0, 0))
    
    # Get the length of bitstrings
    n_bits = len(bitstrings[0])
    
    # Convert bitstrings to binary values (0 or 1)
    binary_data = np.zeros((len(bitstrings), n_bits))
    for i, bitstring in enumerate(bitstrings):
        for j, bit in enumerate(bitstring):
            binary_data[i, j] = int(bit)
    
    # Calculate correlation matrix
    correlation_matrix = np.corrcoef(binary_data.T)
    
    return correlation_matrix

def calculate_entanglement(bitstrings):
    """
    Calculate quantum entanglement based on bit correlations.
    
    Args:
        bitstrings: List of bitstrings
        
    Returns:
        Entanglement value (0-1)
    """
    try:
        # Convert bitstrings to state vectors
        state_vectors = np.array([list(map(int, bs)) for bs in bitstrings])
        
        # Calculate reduced density matrices
        num_qubits = len(bitstrings[0])
        total_shots = len(bitstrings)
        
        # Calculate von Neumann entropy for each qubit
        single_qubit_entropies = []
        for i in range(num_qubits):
            # Calculate reduced density matrix for qubit i
            counts = Counter(state_vectors[:, i].astype(int))
            probabilities = {state: count/total_shots for state, count in counts.items()}
            
            # Calculate von Neumann entropy
            entropy = 0
            for p in probabilities.values():
                if p > 0:
                    entropy -= p * np.log2(p)
            single_qubit_entropies.append(entropy)
        
        # Calculate total system entropy
        state_counts = Counter([''.join(map(str, row)) for row in state_vectors.astype(int)])
        probabilities = {state: count/total_shots for state, count in state_counts.items()}
        total_entropy = 0
        for p in probabilities.values():
            if p > 0:
                total_entropy -= p * np.log2(p)
        
        # Calculate entanglement as difference between sum of individual entropies
        # and total system entropy, normalized to [0,1]
        max_entanglement = num_qubits - 1  # Maximum possible difference
        if max_entanglement > 0:
            entanglement = (sum(single_qubit_entropies) - total_entropy) / max_entanglement
            return float(entanglement)
    except Exception as e:
        print(f"Error calculating entanglement: {e}")
    
    return 0.0

def calculate_interference(bitstrings):
    """
    Calculate quantum interference based on FFT analysis of measurement outcomes.
    
    Args:
        bitstrings: List of bitstrings
        
    Returns:
        Interference value (0-1)
    """
    try:
        # Convert bitstrings to state amplitudes
        num_qubits = len(bitstrings[0])
        hilbert_dim = 2**num_qubits
        
        # Create state vector
        state_counts = Counter(bitstrings)
        total_shots = len(bitstrings)
        
        # Calculate amplitudes
        amplitudes = np.zeros(hilbert_dim, dtype=complex)
        for bitstring, count in state_counts.items():
            try:
                idx = int(bitstring, 2)
                if 0 <= idx < hilbert_dim:
                    amplitudes[idx] = np.sqrt(count / total_shots)
            except ValueError:
                continue
        
        # Calculate FFT of amplitudes
        fft_result = np.abs(fft(amplitudes))
        
        # Calculate interference as ratio of off-diagonal terms
        diagonal_sum = np.sum(fft_result[::hilbert_dim+1])
        total_sum = np.sum(fft_result)
        
        # Normalize to [0,1]
        if total_sum > 0:
            interference = 1 - (diagonal_sum / total_sum)
            return float(interference)
    except Exception as e:
        print(f"Error calculating interference: {e}")
    
    return 0.0

def analyze_job(result_data):
    """Analyze quantum metrics from job result data.
    
    Args:
        result_data: Loaded JSON result data
        
    Returns:
        Dictionary containing metrics for each layer
    """
    try:
        # Get all field data
        fields = result_data['__value__']['pub_results'][0]['__value__']['data']['__value__']['fields']
        
        # Initialize metrics dictionary
        metrics = {'layers': {}}
        
        # Check for pentagon layer naming convention (c_central, c_inner, c_middle, c_outer)
        pentagon_layers = ['c_central', 'c_inner', 'c_middle', 'c_outer']
        has_pentagon_layers = any(layer in fields for layer in pentagon_layers)
        
        if has_pentagon_layers:
            # Process pentagon resonance circuit data
            for layer_name in pentagon_layers:
                if layer_name in fields:
                    # Extract bitstrings
                    field_data = fields[layer_name]['__value__']
                    array_data = field_data['array']['__value__']
                    num_bits = field_data['num_bits']
                    
                    # Decode base64 data
                    decoded_data = base64.b64decode(array_data)
                    
                    # Decompress with zlib (CRITICAL: was missing in original version)
                    decompressed_data = zlib.decompress(decoded_data)
                    
                    # Load as numpy array (the decompressed data is a serialized .npy file)
                    arr = np.load(io.BytesIO(decompressed_data), allow_pickle=False).reshape(-1)
                    
                    # Convert to bitstrings
                    num_bits = field_data['num_bits']
                    bitstrings = [format(int(val), f'0{num_bits}b') for val in arr]
                    
                    # Validate shot count
                    if len(bitstrings) != 8192:
                        print(f"WARNING: Expected 8192 shots, got {len(bitstrings)} for layer {layer_name}")
                    
                    # Calculate metrics
                    layer_metrics = {
                        'num_shots': len(bitstrings),
                        'coherence': calculate_coherence(bitstrings),
                        'entanglement': calculate_entanglement(bitstrings),
                        'interference': calculate_interference(bitstrings)
                    }
                    
                    # Map field names to layer names
                    layer_map = {
                        'c_central': 'central',
                        'c_inner': 'inner',
                        'c_middle': 'middle',
                        'c_outer': 'outer'
                    }
                    metrics['layers'][layer_map[layer_name]] = layer_metrics
        else:
            # Process alternative circuit structure (e.g., 4-20 data with 'c' and 'meas' fields)
            for field_name in fields:
                if field_name in ['c', 'meas']:
                    field_data = fields[field_name]['__value__']
                    array_data = field_data['array']['__value__']
                    num_bits = field_data['num_bits']
                    
                    # Decode base64 data
                    decoded_data = base64.b64decode(array_data)
                    
                    # Decompress with zlib
                    decompressed_data = zlib.decompress(decoded_data)
                    
                    # Load as numpy array
                    arr = np.load(io.BytesIO(decompressed_data), allow_pickle=False).reshape(-1)
                    
                    # Convert to bitstrings
                    bitstrings = [format(int(val), f'0{num_bits}b') for val in arr]
                    
                    # Validate shot count
                    if len(bitstrings) != 8192:
                        print(f"WARNING: Expected 8192 shots, got {len(bitstrings)} for field {field_name}")
                    
                    # Calculate metrics
                    layer_metrics = {
                        'num_shots': len(bitstrings),
                        'coherence': calculate_coherence(bitstrings),
                        'entanglement': calculate_entanglement(bitstrings),
                        'interference': calculate_interference(bitstrings)
                    }
                    
                    # Map field names to layer names
                    layer_map = {
                        'c': 'central',
                        'meas': 'measurement'
                    }
                    metrics['layers'][layer_map[field_name]] = layer_metrics
        
        return metrics
        
    except Exception as e:
        print(f"Error analyzing job: {e}")
        return None

def save_metrics(metrics, metrics_file, summary_file):
    """
    Save metrics to file and create summary.
    
    Args:
        metrics: Dictionary of metrics
        metrics_file: Path to save metrics file
        summary_file: Path to save summary file
    """
    with open(metrics_file, 'w') as f:
        f.write("# Quantum Metrics\n\n")
        
        # Combined metrics table
        f.write("## Combined Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        
        for metric, value in metrics['combined'].items():
            f.write(f"| {metric} | {value:.4f} |\n")
        
        # Layer metrics tables
        for layer_name, layer_metrics in metrics['layers'].items():
            f.write(f"\n## {layer_name} Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            
            for metric, value in layer_metrics.items():
                f.write(f"| {metric} | {value:.4f} |\n")
    
    with open(summary_file, 'w') as f:
        f.write("# Quantum Metrics Summary\n\n")
        
        # Combined metrics table
        f.write("## Combined Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        
        for metric, value in metrics['combined'].items():
            f.write(f"| {metric} | {value:.4f} |\n")
        
        # Layer metrics tables
        for layer_name, layer_metrics in metrics['layers'].items():
            f.write(f"\n## {layer_name} Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            
            for metric, value in layer_metrics.items():
                f.write(f"| {metric} | {value:.4f} |\n")
    
    print(f"Metrics saved to {metrics_file}")
    print(f"Summary saved to {summary_file}")
    
    return metrics

def process_directory(directory_path, output_dir=None):
    """Process all result files in a directory and save metrics.
    
    Args:
        directory_path: Path to directory containing result files
        output_dir: Directory to save metrics files (default: directory_path/metrics)
    """
    from pathlib import Path
    
    directory_path = Path(directory_path)
    if output_dir is None:
        output_dir = directory_path / 'metrics'
    else:
        output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all result files
    result_files = list(directory_path.glob('job-*-result.json'))
    print(f"Found {len(result_files)} result files")
    
    # Process each result file
    all_metrics = []
    for result_file in result_files:
        print(f"\nProcessing {result_file.name}...")
        try:
            # Extract job ID from filename
            job_id = result_file.stem.split('-')[1]
            
            # Get actual job timestamp from info.json file
            info_file = directory_path / f"job-{job_id}-info.json"
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info_data = json.load(f)
                    # Handle Z suffix for UTC timezone
                    created_str = info_data['created']
                    if created_str.endswith('Z'):
                        created_str = created_str[:-1]
                    timestamp = datetime.fromisoformat(created_str)
                    print(f"  Using timestamp from info.json: {timestamp}")
            else:
                # Fallback to file modification time if info.json doesn't exist
                timestamp = datetime.fromtimestamp(result_file.stat().st_mtime)
                print(f"  Using file modification time: {timestamp}")
            
            # Load result data
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            
            # Extract metrics for each layer
            metrics = analyze_job(result_data)
            
            # Add metadata
            metrics['job_id'] = job_id
            metrics['timestamp'] = timestamp.isoformat()
            
            # Save metrics to file
            metrics_file = output_dir / f"job-{job_id}-metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"Saved metrics to {metrics_file}")
            
            all_metrics.append(metrics)
        except Exception as e:
            print(f"Error processing {result_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create comparative summary if we have results
    if all_metrics:
        summary_file = output_dir / 'summary.json'
        # Use the earliest job timestamp as the summary timestamp instead of current time
        if all_metrics:
            job_timestamps = [job['timestamp'] for job in all_metrics if 'timestamp' in job]
            if job_timestamps:
                summary_timestamp = min(job_timestamps)
            else:
                summary_timestamp = datetime.now().isoformat()
        else:
            summary_timestamp = datetime.now().isoformat()
        
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': summary_timestamp,
                'num_jobs': len(all_metrics),
                'jobs': all_metrics
            }, f, indent=2)
        print(f"\nSummary saved to {summary_file}")
        print(f"Summary contains {len(all_metrics)} jobs with timestamps from info.json files")
        print(f"Summary timestamp: {summary_timestamp}")
    else:
        print("\nNo valid results found")
    
    return all_metrics

def create_comparative_summary(all_metrics, output_dir):
    """
    Create a comparative summary of metrics across all jobs.
    
    Args:
        all_metrics: List of job metrics dictionaries
        output_dir: Directory to save summary
    """
    # Create summary file
    summary_file = os.path.join(output_dir, "comparative_metrics_summary.md")
    with open(summary_file, 'w') as f:
        f.write("# Comparative Quantum Metrics Summary\n\n")
        
        # Combined metrics table (average across all layers)
        f.write("## Combined Metrics (Average Across All Layers)\n\n")
        f.write("| Job ID | Coherence | Entanglement | Interference |\n")
        f.write("|--------|-----------|--------------|-------------|\n")
        
        for metrics in all_metrics:
            job_id = metrics["job_id"]
            if "layers" in metrics and metrics["layers"]:
                # Calculate averages across all layers
                coherences = [layer["coherence"] for layer in metrics["layers"].values()]
                entanglements = [layer["entanglement"] for layer in metrics["layers"].values()]
                interferences = [layer["interference"] for layer in metrics["layers"].values()]
                
                avg_coherence = np.mean(coherences)
                avg_entanglement = np.mean(entanglements)
                avg_interference = np.mean(interferences)
                
                f.write(f"| {job_id} | {avg_coherence:.6f} | {avg_entanglement:.6f} | {avg_interference:.4f} |\n")
            else:
                f.write(f"| {job_id} | N/A | N/A | N/A |\n")
        
        # Layer metrics tables
        layer_mapping = {
            'c_central': 'central',
            'c_inner': 'inner', 
            'c_middle': 'middle',
            'c_outer': 'outer'
        }
        
        for layer_key, layer_short in layer_mapping.items():
            display_name = PENTAGON_LAYERS[layer_key]["name"]
            f.write(f"\n## {display_name} Metrics\n\n")
            f.write("| Job ID | Coherence | Entanglement | Interference |\n")
            f.write("|--------|-----------|--------------|-------------|\n")
            
            for metrics in all_metrics:
                job_id = metrics["job_id"]
                if "layers" in metrics and layer_short in metrics["layers"]:
                    layer_metrics = metrics["layers"][layer_short]
                    coherence = layer_metrics["coherence"]
                    entanglement = layer_metrics["entanglement"]
                    interference = layer_metrics["interference"]
                    
                    f.write(f"| {job_id} | {coherence:.6f} | {entanglement:.6f} | {interference:.4f} |\n")
                else:
                    f.write(f"| {job_id} | N/A | N/A | N/A |\n")
    
    print(f"Comparative summary saved to {summary_file}")

def main():
    parser = argparse.ArgumentParser(description='Extract quantum metrics from pentagon resonance circuit results')
    parser.add_argument('--directory', required=True, help='Directory containing result files')
    parser.add_argument('--output', help='Output directory for metrics files')
    args = parser.parse_args()
    
    directory_path = Path(args.directory)
    output_dir = Path(args.output) if args.output else directory_path / 'metrics'
    
    print(f'Processing results from: {directory_path}')
    print(f'Saving metrics to: {output_dir}')
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all result files
    all_metrics = process_directory(directory_path, output_dir)
    
    # Create comparative summary
    if all_metrics:
        create_comparative_summary(all_metrics, output_dir)
        print(f'\nResults have been saved to {output_dir}')
    else:
        print('\nNo valid result files found')

if __name__ == "__main__":
    main()
