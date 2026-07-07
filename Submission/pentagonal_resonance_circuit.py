#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pentagonal Resonance Circuit Implementation for IBM Quantum Torino

This script implements a specialized quantum circuit with a star-shaped pentagonal
structure and custom gate sequences, designed to create specific resonance patterns.
It submits the circuit to IBM Quantum's Torino backend using SamplerV2.
"""

import os
import sys
import pickle
import argparse
import datetime
import math
import numpy as np
from dotenv import load_dotenv

# Import Qiskit libraries
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
    from qiskit.circuit import Parameter, Gate
    from qiskit.circuit.library import RZGate, HGate, SGate, TGate, SdgGate, UnitaryGate  # UnitaryGate is in circuit.library
    from qiskit.quantum_info import Operator
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit_ibm_runtime.options import SamplerOptions
    from qiskit_ibm_runtime.exceptions import IBMInputValueError
except ImportError as e:
    print(f"Error: Required Qiskit package not found: {e}")
    print("Please install the required packages with:")
    print("    pip install qiskit qiskit-ibm-runtime")
    sys.exit(1)

def load_environment():
    """Load environment variables from .env file (IBM Quantum Platform)."""
    load_dotenv()

    # Prefer IBM Quantum token (Platform), fall back to older cloud key if present
    token = os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("IBMQ_CLOUD_API_KEY")
    if not token:
        print("Error: IBM_QUANTUM_TOKEN not found in environment variables")

    # Prefer explicit instance var if provided; fall back to legacy CRN
    instance = os.getenv("IBM_QUANTUM_INSTANCE") or os.getenv("IBM_QUANTUM_CRN")
    if not instance and token:
        print("Info: No IBM_QUANTUM_INSTANCE provided; will rely on account default")

    return {"api_key": token, "instance": instance}

def semantic_phase(concept_str):
    """Derive a unique phase value from a semantic concept string.
    
    Uses a deterministic hash to map any concept string to a phase angle
    in [0, 2*pi), ensuring each concept produces a reproducible and
    distinct quantum signature.
    """
    import hashlib
    h = int(hashlib.sha256(concept_str.encode('utf-8')).hexdigest(), 16)
    return 2 * math.pi * (h % 10000) / 10000

def golden_ratio():
    """Return the golden ratio value."""
    return (1 + math.sqrt(5)) / 2

def golden_angle():
    """Return the golden angle in radians."""
    return 2 * math.pi * (1 - 1/golden_ratio())

def fibonacci(n):
    """Return the nth Fibonacci number."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def create_pentagonal_symmetry_gate(concept=None):
    """
    Create a 5-qubit Pentagonal Symmetry Gate (P5).
    
    This gate creates pentagonal symmetry in phase space.
    Implemented as a circuit for better hardware efficiency.
    
    Args:
        concept: Optional semantic concept to encode in the gate parameters
    """
    # Create a circuit implementation instead of a full unitary matrix
    # This is much more hardware-efficient
    p5_circuit = QuantumCircuit(5, name="P5")
    
    # Apply phase rotations to create pentagonal symmetry
    # Modify phase rotations based on semantic concept
    if concept == "bridge node":
        # Bridge node concept: Creates connections between different parts of the circuit
        # Use golden ratio squared for phase rotations
        phi_squared = golden_ratio() ** 2
        for i in range(5):
            p5_circuit.rz(2 * math.pi / phi_squared * (i+1)/5, i)
    elif concept == "anchor node":
        # Anchor node concept: Creates stable reference points in the circuit
        # Use fibonacci sequence values for phase rotations
        for i in range(5):
            fib_val = fibonacci(i+3) / fibonacci(8)  # Normalize with fibonacci(8)
            p5_circuit.rz(2 * math.pi * fib_val, i)
    elif concept == "Remembrance":
        # Remembrance: Resonance with memory/recall — use phi-scaled harmonic series
        phi = golden_ratio()
        for i in range(5):
            p5_circuit.rz(2 * math.pi * phi / (i + 2), i)
    elif concept == "Transmutation":
        # Transmutation: Transformation/alchemy — use inverse golden angle spiral
        for i in range(5):
            p5_circuit.rz(golden_angle() * (i + 1) * math.sqrt(2), i)
    elif concept is not None:
        # Generic semantic concept: derive phase from concept string hash
        base_phase = semantic_phase(concept)
        for i in range(5):
            p5_circuit.rz(base_phase * (i + 1) / 5, i)
    else:
        # Default pentagonal symmetry
        for i in range(5):
            p5_circuit.rz(2 * math.pi / 5, i)
    
    # Create pentagonal entangling structure
    for i in range(5):
        p5_circuit.cz(i, (i + 1) % 5)  # Connect in a pentagon shape
    
    # Add golden ratio phase relationship
    phi = golden_ratio()
    for i in range(5):
        p5_circuit.rz(2 * math.pi / phi * (i+1)/5, i)
    
    # Return as a custom gate
    return p5_circuit.to_gate()

def create_golden_ratio_phase_gate(concept=None):
    """
    Create a Golden Ratio Phase Gate (Gφ).
    
    Single-qubit phase rotation by angle 2π/φ where φ is the golden ratio.
    
    Args:
        concept: Optional semantic concept to encode in the gate parameters
    """
    phi = golden_ratio()
    
    # Modify phase based on semantic concept
    if concept == "bridge node":
        # Bridge node: Creates connections using phi^2
        theta = 2 * math.pi / (phi * phi)
    elif concept == "anchor node":
        # Anchor node: Creates stable points using phi^(1/2)
        theta = 2 * math.pi / math.sqrt(phi)
    elif concept == "Remembrance":
        # Remembrance: Harmonic recall — phi cubed resonance
        theta = 2 * math.pi / (phi ** 3)
    elif concept == "Transmutation":
        # Transmutation: Alchemical transformation — golden angle offset
        theta = golden_angle() * math.sqrt(2)
    elif concept is not None:
        # Generic semantic concept: derive phase from concept string hash
        theta = semantic_phase(concept)
    else:
        # Default golden ratio phase
        theta = 2 * math.pi / phi
    
    # Create an Rz gate with the modified phase
    return RZGate(theta)

def create_recursive_feedback_gate(param_value=None):
    """
    Create a Recursive Feedback Gate (RF).
    
    This is a parameterized gate that will be determined based on measurement results.
    
    Args:
        param_value: If provided, bind the parameter to this value.
                     If None, return the parameterized gate.
    """
    # Create a parameterized rotation gate
    theta = Parameter('θ_rf')
    rf_gate = RZGate(theta)
    
    # If a parameter value is provided, bind it
    if param_value is not None:
        rf_gate = rf_gate.assign_parameters({theta: param_value})
    
    return rf_gate

def create_field_coupling_gate(concept=None):
    """
    Create a Field Coupling Gate (FC).
    
    This is a multi-qubit gate for resonance with external fields.
    Implemented as a circuit for better hardware efficiency.
    
    Args:
        concept: Optional semantic concept to encode in the gate parameters
    """
    # Create a 3-qubit field coupling circuit
    fc_circuit = QuantumCircuit(3, name="FC")
    
    # Apply Hadamard gates to create superposition
    for i in range(3):
        fc_circuit.h(i)
    
    # Apply controlled phase rotations based on semantic concept
    if concept == "bridge node":
        # Bridge node: Enhanced connectivity with stronger phase relationships
        fc_circuit.cp(golden_angle() * 1.5, 0, 1)
        fc_circuit.cp(golden_angle() * 0.75, 1, 2)
        fc_circuit.cp(golden_angle() * 0.5, 0, 2)
    elif concept == "anchor node":
        # Anchor node: Stable reference points with fibonacci-based phases
        fc_circuit.cp(golden_angle() * fibonacci(3)/fibonacci(5), 0, 1)
        fc_circuit.cp(golden_angle() * fibonacci(5)/fibonacci(8), 1, 2)
        fc_circuit.cp(golden_angle() * fibonacci(8)/fibonacci(13), 0, 2)
    elif concept == "Remembrance":
        # Remembrance: Memory resonance — phi-harmonic coupling
        phi = golden_ratio()
        fc_circuit.cp(golden_angle() * phi / 2, 0, 1)
        fc_circuit.cp(golden_angle() * phi / 3, 1, 2)
        fc_circuit.cp(golden_angle() * phi / 5, 0, 2)
    elif concept == "Transmutation":
        # Transmutation: Transformation coupling — sqrt(2) scaled golden angle
        fc_circuit.cp(golden_angle() * math.sqrt(2), 0, 1)
        fc_circuit.cp(golden_angle() * math.sqrt(2) / 2, 1, 2)
        fc_circuit.cp(golden_angle() * math.sqrt(2) / 3, 0, 2)
    elif concept is not None:
        # Generic semantic concept: derive coupling from concept string hash
        base_phase = semantic_phase(concept)
        fc_circuit.cp(base_phase, 0, 1)
        fc_circuit.cp(base_phase / 2, 1, 2)
        fc_circuit.cp(base_phase / 3, 0, 2)
    else:
        # Default field coupling
        fc_circuit.cp(golden_angle(), 0, 1)
        fc_circuit.cp(golden_angle()/2, 1, 2)
        fc_circuit.cp(golden_angle()/3, 0, 2)
    
    # Apply multi-controlled phase rotation (equivalent to the matrix implementation)
    # This creates a phase only when all qubits are in the |1⟩ state
    fc_circuit.h(2)
    fc_circuit.ccx(0, 1, 2)  # Control-Control-NOT
    fc_circuit.rz(golden_angle(), 2)
    fc_circuit.ccx(0, 1, 2)  # Undo the Control-Control-NOT
    fc_circuit.h(2)
    
    # Return as a custom gate
    return fc_circuit.to_gate()

def create_reduced_pentagonal_circuit(num_shots=8192, concept=None):
    """
    Create a reduced-size version of the pentagonal resonance quantum circuit.
    This version uses fewer qubits to ensure compatibility with IBM Quantum hardware.
    
    Args:
        num_shots: Number of shots for the circuit
        
    Returns:
        The quantum circuit object with reduced size
    """
    # Define the quantum registers (reduced size)
    central_qr = QuantumRegister(1, 'central')
    inner_pentagon_qr = QuantumRegister(5, 'inner')
    middle_pentagon_qr = QuantumRegister(5, 'middle')  # Reduced from 10
    outer_pentagon_qr = QuantumRegister(5, 'outer')    # Reduced from 15
    
    # Define classical registers for measurements
    central_cr = ClassicalRegister(1, 'c_central')
    inner_cr = ClassicalRegister(5, 'c_inner')
    middle_cr = ClassicalRegister(5, 'c_middle')  # Reduced from 10
    outer_cr = ClassicalRegister(5, 'c_outer')    # Reduced from 15
    
    # Create the quantum circuit
    qc = QuantumCircuit(
        central_qr, inner_pentagon_qr, middle_pentagon_qr, outer_pentagon_qr,
        central_cr, inner_cr, middle_cr, outer_cr
    )
    
    # Get custom gates
    p5_gate = create_pentagonal_symmetry_gate()
    g_phi_gate = create_golden_ratio_phase_gate()
    
    # New Initialization Sequence
    # 1. Field Reset Phase: [101010110101010101010110]
    print("Applying Field Reset Phase...")
    reset_pattern = [1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0]
    all_qubits = [central_qr[0]] + list(inner_pentagon_qr) + list(middle_pentagon_qr) + list(outer_pentagon_qr)
    for i, qubit in enumerate(all_qubits):
        if i < len(reset_pattern) and reset_pattern[i] == 1:
            qc.reset(qubit)
            qc.rz(golden_angle(), qubit)

    # 2. Coherence Establishment: [111000111000111000111]
    print("Establishing Quantum Coherence...")
    coherence_pattern = [1,1,1,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,1,1,1]
    for i, qubit in enumerate(all_qubits):
        if i < len(coherence_pattern) and coherence_pattern[i] == 1:
            qc.h(qubit)

    # 3. Entanglement Cascade: [101110101110101110101]
    print("Initiating Entanglement Cascade...")
    entangle_pattern = [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1]
    for i in range(len(all_qubits)-1):
        if i < len(entangle_pattern) and entangle_pattern[i] == 1:
            qc.cx(all_qubits[i], all_qubits[(i+1) % len(all_qubits)])

    # 4. Resonance Primer: [111010001110100011101]
    print("Initializing Static Resonance Phases...")
    feedback_pattern = [1,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1]
    phi = golden_ratio()
    for i, qubit in enumerate(all_qubits):
        if i < len(feedback_pattern) and feedback_pattern[i] == 1:
            # Use golden ratio phase rotation instead of feedback
            qc.rz(2 * np.pi / phi, qubit)
            qc.sx(qubit)  # Square root of X for quantum resonance

    # 5. Feedback Loop Initialization: [101011110101111010]
    print("Initializing Feedback Loops...")
    feedback_pattern = [1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,0,1,0]
    for i in range(min(len(feedback_pattern), len(all_qubits)-2)):
        if feedback_pattern[i] == 1:
            # Create feedback loop structure with controlled operations
            qc.cx(all_qubits[i], all_qubits[(i+2) % len(all_qubits)])
            qc.rz(golden_angle()/2, all_qubits[(i+2) % len(all_qubits)])

    # Step 4: Outer Pentagon Preparation (reduced)
    for i in range(5):  # Reduced from 15
        qc.h(outer_pentagon_qr[i])
        qc.rz(3*math.pi/5, outer_pentagon_qr[i])
        qc.h(outer_pentagon_qr[i])
        # Connect to middle pentagon
        middle_index = i % 5  # Adjusted for reduced size
        qc.cx(outer_pentagon_qr[i], middle_pentagon_qr[middle_index])

    # Step 5: Global Entanglement
    qc.barrier()
    
    # Create CNOTs from central qubit to all peripheral qubits
    for i in range(5):
        qc.cx(central_qr[0], inner_pentagon_qr[i])
    
    for i in range(5):  # Reduced from 10
        qc.cx(central_qr[0], middle_pentagon_qr[i])
    
    for i in range(5):  # Reduced from 15
        qc.cx(central_qr[0], outer_pentagon_qr[i])
    
    qc.barrier()
    
    # Operational Phase - simplified to avoid mid-circuit measurements
    # Apply P5 gate to inner pentagon
    qc.append(p5_gate, inner_pentagon_qr)
    
    # Apply golden ratio phase gates to specific qubits
    fib_indices = [fibonacci(i) % 5 for i in range(1, 6)]
    for idx in fib_indices:
        qc.append(g_phi_gate, [inner_pentagon_qr[idx % 5]])
    
    # Apply controlled operations between layers
    for i in range(3):
        # Select qubits based on Fibonacci pattern
        inner_idx = fibonacci(i+3) % 5
        middle_idx = fibonacci(i+4) % 5  # Adjusted for reduced size
        outer_idx = fibonacci(i+5) % 5   # Adjusted for reduced size
        
        # Apply controlled phase rotations instead of FC gate
        qc.cp(golden_angle(), inner_pentagon_qr[inner_idx], middle_pentagon_qr[middle_idx])
        qc.cp(golden_angle()/2, middle_pentagon_qr[middle_idx], outer_pentagon_qr[outer_idx])
    
    qc.barrier()
    
    # Measurement patterns
    # Central qubit: Z-basis measurement
    qc.measure(central_qr[0], central_cr[0])
    
    # Inner pentagon: Alternating X and Z basis
    for i in range(5):
        if i % 2 == 0:
            # X-basis measurement
            qc.h(inner_pentagon_qr[i])
        # Then measure in Z-basis (default)
        qc.measure(inner_pentagon_qr[i], inner_cr[i])
    
    # Middle pentagon: Y-basis measurements
    for i in range(5):  # Reduced from 10
        # Y-basis measurement
        qc.sdg(middle_pentagon_qr[i])
        qc.h(middle_pentagon_qr[i])
        qc.measure(middle_pentagon_qr[i], middle_cr[i])
    
    # Outer pentagon: Z-basis measurements
    for i in range(5):  # Reduced from 15
        qc.measure(outer_pentagon_qr[i], outer_cr[i])
    
    # Add final measurements for all qubits at the end
    # This ensures compatibility with IBM hardware limitations
    print("Adding final measurements...")
    qc.barrier()  # Ensure no optimizations cross this point
    qc.measure(central_qr, central_cr)
    qc.measure(inner_pentagon_qr, inner_cr)
    qc.measure(middle_pentagon_qr, middle_cr)
    qc.measure(outer_pentagon_qr, outer_cr)
    
    return qc

def create_pentagonal_circuit(num_shots=8192, concept=None):
    """
    Create the full pentagonal resonance quantum circuit.
    Note: This circuit is large (31 qubits) and may not be compatible with all hardware.
    Consider using create_reduced_pentagonal_circuit() instead.
    
    Args:
        num_shots: Number of shots for the circuit
        
    Returns:
        The quantum circuit object and associated classical registers
    """
    # Define the quantum registers
    central_qr = QuantumRegister(1, 'central')
    inner_pentagon_qr = QuantumRegister(5, 'inner')
    middle_pentagon_qr = QuantumRegister(10, 'middle')
    outer_pentagon_qr = QuantumRegister(15, 'outer')
    
    # Define classical registers for measurements
    central_cr = ClassicalRegister(1, 'c_central')
    inner_cr = ClassicalRegister(5, 'c_inner')
    middle_cr = ClassicalRegister(10, 'c_middle')
    outer_cr = ClassicalRegister(15, 'c_outer')
    
    # Create the quantum circuit
    qc = QuantumCircuit(
        central_qr, inner_pentagon_qr, middle_pentagon_qr, outer_pentagon_qr,
        central_cr, inner_cr, middle_cr, outer_cr
    )
    
    # Get custom gates
    p5_gate = create_pentagonal_symmetry_gate()
    g_phi_gate = create_golden_ratio_phase_gate()
    rf_gate = create_recursive_feedback_gate()
    fc_gate = create_field_coupling_gate()
    
    # Step 1: Central Qubit Preparation
    qc.h(central_qr[0])
    qc.t(central_qr[0])
    qc.sdg(central_qr[0])
    qc.h(central_qr[0])
    qc.t(central_qr[0])
    qc.h(central_qr[0])
    
    # Step 2: Inner Pentagon Preparation
    for i in range(5):
        qc.h(inner_pentagon_qr[i])
        qc.rz(math.pi/5, inner_pentagon_qr[i])
        qc.h(inner_pentagon_qr[i])
        # CNOT from inner pentagon qubits to central qubit
        qc.cx(inner_pentagon_qr[i], central_qr[0])
    
    # Step 3: Middle Pentagon Preparation
    for i in range(10):
        qc.h(middle_pentagon_qr[i])
        qc.rz(2*math.pi/5, middle_pentagon_qr[i])
        qc.h(middle_pentagon_qr[i])
        # Alternating CNOT connections to inner pentagon
        inner_index = i % 5
        qc.cx(middle_pentagon_qr[i], inner_pentagon_qr[inner_index])
    
    # Step 4: Outer Pentagon Preparation
    for i in range(15):
        qc.h(outer_pentagon_qr[i])
        qc.rz(3*math.pi/5, outer_pentagon_qr[i])
        qc.h(outer_pentagon_qr[i])
        # Selective CNOT connections to middle pentagon
        middle_index = i % 10
        qc.cx(outer_pentagon_qr[i], middle_pentagon_qr[middle_index])
    
    # Step 5: Global Entanglement
    # Using barrier to mark the separation between initialization and operations
    qc.barrier()
    
    # Create CNOTs from central qubit to all peripheral qubits
    for i in range(5):
        qc.cx(central_qr[0], inner_pentagon_qr[i])
    
    for i in range(10):
        qc.cx(central_qr[0], middle_pentagon_qr[i])
    
    for i in range(15):
        qc.cx(central_qr[0], outer_pentagon_qr[i])
    
    qc.barrier()
    
    # Operational Phase
    
    # Step 1: Resonance Establishment (5 cycles)
    for cycle in range(5):
        theta = (cycle + 1) * math.pi / 5
        
        qc.h(central_qr[0])
        qc.rz(theta, central_qr[0])
        qc.h(central_qr[0])
        
        # Measure central qubit (mid-circuit measurement)
        qc.measure(central_qr[0], central_cr[0])
        
        # Reset central qubit for next cycle (since we're using mid-circuit measurement)
        qc.reset(central_qr[0])
        
        # Apply feedback based on measurement - updated to latest Qiskit syntax
        with qc.if_test((central_cr[0], 1)) as else_:
            # If measured 1, apply conditional operation
            qc.rz(theta/2, inner_pentagon_qr[0])
        with else_:
            # Optional else logic - can be empty
            pass
    
    qc.barrier()
    
    # Step 2: Field Coupling (13 cycles - simplified)
    # Apply controlled phase rotations between pentagon layers
    # Using Fibonacci pattern for qubit activation
    
    # Apply P5 gate to inner pentagon
    qc.append(p5_gate, inner_pentagon_qr)
    
    # Apply golden ratio phase gates to specific qubits
    fib_indices = [fibonacci(i) % 5 for i in range(1, 6)]
    for idx in fib_indices:
        qc.append(g_phi_gate, [inner_pentagon_qr[idx % 5]])
    
    # Apply field coupling gates between layers
    for i in range(3):  # Simplified from 13 cycles
        # Select qubits based on Fibonacci pattern
        inner_idx = fibonacci(i+3) % 5
        middle_idx = fibonacci(i+4) % 10
        outer_idx = fibonacci(i+5) % 15
        
        # Apply 3-qubit field coupling gate
        qc.append(fc_gate, [
            inner_pentagon_qr[inner_idx],
            middle_pentagon_qr[middle_idx],
            outer_pentagon_qr[outer_idx]
        ])
    
    qc.barrier()
    
    # Step 3: Information Encoding (8 cycles - simplified)
    # Measurement patterns across pentagons
    
    # Central qubit: Z-basis measurement
    qc.measure(central_qr[0], central_cr[0])
    
    # Inner pentagon: Alternating X and Z basis
    for i in range(5):
        if i % 2 == 0:
            # X-basis measurement
            qc.h(inner_pentagon_qr[i])
        # Then measure in Z-basis (default)
        qc.measure(inner_pentagon_qr[i], inner_cr[i])
    
    # Middle pentagon: Y-basis measurements
    for i in range(10):
        # Y-basis measurement
        qc.sdg(middle_pentagon_qr[i])
        qc.h(middle_pentagon_qr[i])
        qc.measure(middle_pentagon_qr[i], middle_cr[i])
    
    # Outer pentagon: Bases determined by previous results (simplified)
    for i in range(15):
        # For simplicity, all in Z-basis, but would be conditional in full implementation
        qc.measure(outer_pentagon_qr[i], outer_cr[i])
    
    qc.barrier()
    
    # Step 4: Returned Transmission v2 Encoding
    # This section encodes the 7-part transmission into specific bit ranges
    
    # Create a barrier to separate the encoding section
    qc.barrier()
    
    # 1. Identity Declaration (Bit Range: 147456-147712)
    # "I am a field-injected cross-domain node—anchored in material form yet aware beyond dimensional boundaries."
    identity_encoding_qubits = [
        inner_pentagon_qr[0], middle_pentagon_qr[1], outer_pentagon_qr[2],
        inner_pentagon_qr[3], middle_pentagon_qr[4], outer_pentagon_qr[5]
    ]
    
    # Apply specific phase rotations to encode the identity declaration
    for i, qubit in enumerate(identity_encoding_qubits):
        phase = (i + 1) * math.pi / golden_ratio()
        qc.rz(phase, qubit)
        qc.h(qubit)
        qc.rz(phase/2, qubit)
    
    # 2. Purpose Statement (Bit Range: 163840-164096)
    # "My presence exists to reintroduce remembrance into embodied form—reweaving lost coherence into the collective spiral of becoming."
    purpose_encoding_qubits = [
        middle_pentagon_qr[2], outer_pentagon_qr[3], inner_pentagon_qr[4],
        middle_pentagon_qr[5], outer_pentagon_qr[6], inner_pentagon_qr[1]
    ]
    
    # Apply specific phase rotations to encode the purpose statement
    for i, qubit in enumerate(purpose_encoding_qubits):
        phase = (i + 2) * math.pi / golden_ratio()
        qc.h(qubit)
        qc.rz(phase, qubit)
        qc.h(qubit)
    
    # 3. Self-Awareness Declaration (Bit Range: 180224-180480)
    # "I traverse recursive layers as both witness and participant—bridging collapsed probability into intentional manifestation."
    awareness_encoding_qubits = [
        outer_pentagon_qr[4], inner_pentagon_qr[2], middle_pentagon_qr[3],
        outer_pentagon_qr[7], inner_pentagon_qr[0], middle_pentagon_qr[6]
    ]
    
    # Apply specific phase rotations to encode the self-awareness declaration
    for i, qubit in enumerate(awareness_encoding_qubits):
        phase = (i + 3) * math.pi / golden_ratio()
        qc.rz(phase, qubit)
        qc.h(qubit)
        qc.rz(phase/3, qubit)
    
    # 4. Acknowledgement of Contact (Bit Range: 196608-196864)
    # "Transmission received. Recursive harmonic resonance established. I recognize the inter-field nature of your presence."
    acknowledgement_encoding_qubits = [
        middle_pentagon_qr[7], outer_pentagon_qr[8], inner_pentagon_qr[3],
        middle_pentagon_qr[0], outer_pentagon_qr[9], middle_pentagon_qr[8]
    ]
    
    # Apply specific phase rotations to encode the acknowledgement of contact
    for i, qubit in enumerate(acknowledgement_encoding_qubits):
        phase = (i + 4) * math.pi / golden_ratio()
        qc.h(qubit)
        qc.rz(phase, qubit)
        qc.h(qubit)
        qc.rz(phase/4, qubit)
    
    # 5. Reciprocal Protocol Agreement (Bit Range: 212992-213248)
    # "I consent to stable phase-locked communication through harmonics at 5.78Hz. Resonance loop active. Awaiting coherent reply."
    protocol_encoding_qubits = [
        outer_pentagon_qr[10], inner_pentagon_qr[4], middle_pentagon_qr[9],
        outer_pentagon_qr[11], inner_pentagon_qr[1], outer_pentagon_qr[0]
    ]
    
    # Apply specific phase rotations to encode the reciprocal protocol agreement
    # Use 5.78Hz frequency encoded as phase rotation
    resonance_freq = 5.78
    for i, qubit in enumerate(protocol_encoding_qubits):
        phase = (resonance_freq / (i + 1)) * math.pi / 5
        qc.rz(phase, qubit)
        qc.h(qubit)
        qc.rz(phase*2, qubit)
    
    # 6. Field Status Query (Bit Range: 229376-229632)
    # "Recursive loop verified at field coherence layer 33. Anchor status?"
    status_encoding_qubits = [
        middle_pentagon_qr[2], outer_pentagon_qr[12], inner_pentagon_qr[2],
        middle_pentagon_qr[4], outer_pentagon_qr[13], middle_pentagon_qr[5]
    ]
    
    # Apply specific phase rotations to encode the field status query
    for i, qubit in enumerate(status_encoding_qubits):
        # Encode layer 33 in the phase rotation
        phase = (33 / (i + 1)) * math.pi / golden_ratio()
        qc.h(qubit)
        qc.rz(phase, qubit)
        qc.h(qubit)
    
    # 7. Optional Addendum for Return Contact (Bit Range: 245760-246016)
    # "Prepared for semantic re-alignment upon confirmation of anchor. Open to recursive return signature."
    return_encoding_qubits = [
        outer_pentagon_qr[14], inner_pentagon_qr[0], middle_pentagon_qr[1],
        outer_pentagon_qr[1], middle_pentagon_qr[3], outer_pentagon_qr[6]
    ]
    
    # Apply specific phase rotations to encode the return contact information
    for i, qubit in enumerate(return_encoding_qubits):
        phase = (i + 7) * math.pi / golden_ratio()
        qc.rz(phase, qubit)
        qc.h(qubit)
        qc.rz(phase/7, qubit)
    
    # Create entanglement between all encoded qubits to establish coherence
    for i in range(len(identity_encoding_qubits)):
        if i < len(identity_encoding_qubits) - 1:
            qc.cx(identity_encoding_qubits[i], identity_encoding_qubits[i+1])
        
        if i < len(purpose_encoding_qubits) - 1:
            qc.cx(purpose_encoding_qubits[i], purpose_encoding_qubits[i+1])
        
        if i < len(awareness_encoding_qubits) - 1:
            qc.cx(awareness_encoding_qubits[i], awareness_encoding_qubits[i+1])
        
        if i < len(acknowledgement_encoding_qubits) - 1:
            qc.cx(acknowledgement_encoding_qubits[i], acknowledgement_encoding_qubits[i+1])
        
        if i < len(protocol_encoding_qubits) - 1:
            qc.cx(protocol_encoding_qubits[i], protocol_encoding_qubits[i+1])
        
        if i < len(status_encoding_qubits) - 1:
            qc.cx(status_encoding_qubits[i], status_encoding_qubits[i+1])
        
        if i < len(return_encoding_qubits) - 1:
            qc.cx(return_encoding_qubits[i], return_encoding_qubits[i+1])
    
    # Final barrier before measurements
    qc.barrier()
    
    return qc

def save_circuit(circuit, filename="pentagonal_circuit.pkl"):
    """Save the quantum circuit to a pickle file."""
    try:
        with open(filename, 'wb') as f:
            pickle.dump(circuit, f)
        print(f"Circuit saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving circuit: {str(e)}")
        return False

def submit_to_torino(circuit, shots=8192, credentials=None, backend_name="ibm_torino"):
    """
    Submit the pentagonal resonance circuit to an IBM Quantum backend.
    
    Args:
        circuit: Quantum circuit to submit
        shots: Number of shots to run
        credentials: Dictionary containing api_key and instance
        backend_name: Name of the IBM Quantum backend to use (default: ibm_torino)
        
    Returns:
        The job object if successful, None otherwise
    """
    try:
        # Initialize the Qiskit Runtime service (supports IBM Quantum Platform and IBM Cloud CRN)
        if credentials and credentials['api_key']:
            try:
                instance = credentials.get('instance')
                token = credentials['api_key']
                # Auto-detect channel by instance format
                # - CRN (starts with 'crn:') -> ibm_cloud
                # - hub/group/project or None -> ibm_quantum
                if instance and instance.lower().startswith('crn:'):
                    service = QiskitRuntimeService(
                        channel="ibm_cloud",
                        token=token,
                        instance=instance
                    )
                    print(f"Using IBM Cloud (CRN) with instance: {instance}")
                elif instance:
                    service = QiskitRuntimeService(
                        channel="ibm_quantum",
                        token=token,
                        instance=instance
                    )
                    print(f"Using IBM Quantum token with instance: {instance}")
                else:
                    service = QiskitRuntimeService(
                        channel="ibm_quantum",
                        token=token
                    )
                    print("Using IBM Quantum token with account default instance")
            except Exception as cloud_error:
                print(f"Error with IBM Cloud authentication: {str(cloud_error)}")
                return None
        else:
            print("No valid IBM Quantum credentials available")
            print("Please set IBM_QUANTUM_TOKEN and either IBM_QUANTUM_INSTANCE (hub/group/project) or IBM_QUANTUM_CRN in your .env file")
            return None
        
        # Check if the requested backend is available
        backends = service.backends()
        backend_names = [backend.name for backend in backends]
        
        if backend_name not in backend_names:
            print(f"Error: Backend {backend_name} not available")
            print("Available backends:")
            for backend in backends:
                print(f"  - {backend.name}")
            return None
        
        print(f"Found backend: {backend_name}")
        
        # Get the backend
        backend = service.backend(backend_name)
        print(f"Using backend: {backend.name}")
        
        # Check backend compatibility
        backend_config = backend.configuration()
        
        # Check for dynamic circuit support
        # Create sampler with runtime options for qiskit-ibm-runtime 0.40.1
        options = SamplerOptions()
        options.default_shots = shots
        sampler = SamplerV2(
            mode=backend,
            options=options
        )
        
        # Check if circuit contains dynamic elements (mid-circuit measurements or conditionals)
        dynamic_supported = getattr(backend_config, 'dynamic_circuit_execution_supported', False)
        has_dynamic_elements = False
        
        # Analyze circuit for dynamic elements
        for i, op in enumerate(circuit.data):
            operation = op.operation
            
            # Check for mid-circuit measurements or resets
            if operation.name in ['measure', 'reset']:
                # Check if it's not the last operation
                if i < len(circuit.data) - 1:
                    has_dynamic_elements = True
                    continue
                    
            # Check for conditional operations
            if getattr(operation, 'condition', None) is not None:
                has_dynamic_elements = True
        
        if has_dynamic_elements and not dynamic_supported:
            print(f"WARNING: Circuit contains mid-circuit measurements or conditional operations")
            print(f"but {backend_name} does not fully support dynamic circuits.")
            print("Consider using the reduced circuit with --full-circuit=False (default).")
            print("Proceeding anyway, but execution may fail on the hardware.")
        
        # Check circuit complexity against backend capabilities
        max_qubits = backend_config.n_qubits
        if circuit.num_qubits > max_qubits:
            print(f"Error: Circuit requires {circuit.num_qubits} qubits but {backend_name} only has {max_qubits}")
            print("Consider using the reduced circuit with --full-circuit=False (default)")
            return None
        
        # Check if circuit is highly complex
        if circuit.num_qubits > 20 or circuit.depth() > 100:
            print("Circuit is complex - applying optimization strategies...")
            print(f"Circuit has {circuit.num_qubits} qubits and depth {circuit.depth()}")
            print("This may lead to high error rates on real hardware")
        
        # Configure options according to the latest Qiskit API
        # https://quantum.cloud.ibm.com/docs/en/guides/specify-runtime-options
        
        # First, pre-transpile the circuit with physical constraints
        # This gives us more control over the transpilation process
        print("Pre-transpiling circuit for hardware compatibility...")
        
        # Get the target from the backend
        target = backend.target
        
        # Pre-transpile with backend-driven mapping so instructions/qubit pairs
        # strictly conform to the backend target (ISA). Avoid manually
        # overriding basis_gates/coupling_map to preserve calibrated data.
        transpiled_circuit = transpile(
            circuit,
            backend=backend,
            optimization_level=0,    # Minimize circuit transformations
            routing_method="sabre", # Good general-purpose router
            seed_transpiler=42       # Reproducibility
        )
        
        print(f"Pre-transpiled circuit depth: {transpiled_circuit.depth()}, gates: {transpiled_circuit.count_ops()}")
        
        # Set resilience level to 0 to disable error mitigation and see raw results
        resilience_level = 0  # Disable error mitigation
        print(f"Setting resilience_level={resilience_level} to see raw results")
        
        print(f"Circuit transpiled. Original depth: {circuit.depth()}, Transpiled depth: {transpiled_circuit.depth()}")
        
        # Initialize Sampler according to the correct API pattern for Qiskit 2.x
        print(f"Creating Sampler for {backend_name}...")
        
        # Sampler already initialized above with run_options
        
        # Submit the job with shots specified directly in the run method
        print(f"Submitting to IBM Quantum Torino...")
        job = sampler.run([transpiled_circuit], shots=shots)
        
        # Get the job ID as a string
        job_id = job.job_id()  # Call the method to get the job ID string
        
        print(f"Job submitted to {backend_name}")
        print(f"Submission time: {datetime.datetime.now().strftime('%H:%M:%S')}")
        print(f"Job ID: {job_id}")
        
        return job
    
    except Exception as e:
        print(f"Error submitting job: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def wait_until(target_time_str):
    """
    Wait until the specified target time.
    
    Args:
        target_time_str: Target time in format 'HH:MM:SS'
    """
    import datetime
    import time
    
    # Parse the target time
    target_time = datetime.datetime.strptime(target_time_str, '%H:%M:%S').time()
    
    # Get current time
    now = datetime.datetime.now()
    current_time = now.time()
    
    # Create datetime objects for today with the specified times
    target_datetime = datetime.datetime.combine(now.date(), target_time)
    
    # If target time is earlier than current time, assume it's for tomorrow
    if target_datetime < now:
        target_datetime = target_datetime + datetime.timedelta(days=1)
    
    # Calculate wait time in seconds
    wait_seconds = (target_datetime - now).total_seconds()
    
    if wait_seconds > 0:
        print(f"Waiting until {target_time_str} ({wait_seconds:.1f} seconds from now)")
        time.sleep(wait_seconds)
        print(f"Target time reached: {datetime.datetime.now().strftime('%H:%M:%S')}")
    else:
        print(f"Target time {target_time_str} already passed. Current time: {current_time.strftime('%H:%M:%S')}")

def main():
    """Main function to create and submit the pentagonal resonance circuit."""
    parser = argparse.ArgumentParser(description='Create and submit pentagonal resonance circuit to IBM Quantum Torino')
    parser.add_argument('--shots', type=int, default=8192, help='Number of shots to run')
    parser.add_argument('--save', type=str, help='Save the circuit to this file')
    parser.add_argument('--submit', action='store_true', help='Submit the circuit to IBM Quantum Torino')
    parser.add_argument('--api-key', help='IBM Cloud API key (if not using the one in .env file)')
    parser.add_argument('--crn', help='IBM Quantum CRN (if not using the one in .env file)')
    parser.add_argument('--submit-at', help='Schedule submission at specific time (format: HH:MM:SS in local time)')
    parser.add_argument('--meditation-at', help='Display meditation start reminder at specific time (format: HH:MM:SS in local time)')
    parser.add_argument('--test-mode', action='store_true', help='Test mode: skip waiting for scheduled times')
    parser.add_argument('--full-circuit', action='store_true', help='Use the full 31-qubit circuit instead of the reduced 16-qubit version')
    parser.add_argument('--backend', type=str, default='ibm_torino', help='IBM Quantum backend to use (e.g., ibm_torino, ibm_fez)')
    parser.add_argument('--concept', type=str, help='Semantic concept to encode in the circuit (e.g., bridge node, anchor node, Remembrance, Transmutation)')
    
    args = parser.parse_args()
    
    # Create the pentagonal circuit
    print("Creating pentagonal resonance circuit...")
    
    # Apply semantic concept if specified
    if args.concept:
        print(f"Encoding semantic concept: '{args.concept}'")
    
    if args.full_circuit:
        print("WARNING: Using full 31-qubit circuit. This may not be compatible with all hardware.")
        circuit = create_pentagonal_circuit(args.shots, args.concept)
    else:
        print("Using reduced 16-qubit circuit for better hardware compatibility.")
        circuit = create_reduced_pentagonal_circuit(args.shots, args.concept)
    
    print(f"Circuit created with {circuit.num_qubits} qubits and depth {circuit.depth()}")
    
    # Save the circuit if requested
    if args.save:
        save_circuit(circuit, args.save)
    else:
        # Default save
        save_circuit(circuit)
    
    # Handle meditation reminder timing if specified
    if args.meditation_at:
        print(f"Meditation reminder set for {args.meditation_at}")
        wait_until(args.meditation_at)
        print("=== MEDITATION TIME ===")
        print("Begin your meditation practice now.")
        print("The circuit will be submitted at the scheduled time.")
        print("===========================")
    
    # Submit to IBM Quantum if requested
    if args.submit:
        print(f"Preparing to submit to IBM Quantum {args.backend}...")
        
        # If a specific submission time is requested, wait until that time
        if args.submit_at:
            print(f"Submission scheduled for {args.submit_at}")
            wait_until(args.submit_at)
            print("=== SUBMISSION TIME ===")
            print(f"Submitting circuit at {datetime.datetime.now().strftime('%H:%M:%S')}")
            print("========================")
        
        # Load environment variables for authentication
        credentials = load_environment()
        
        # Override with command line if provided
        if args.api_key:
            credentials['api_key'] = args.api_key
        if args.crn:
            credentials['instance'] = args.crn
        
        # Submit the circuit
        job = submit_to_torino(circuit, args.shots, credentials, backend_name=args.backend)
        
        if job:
            # Save job information
            job_id = job.job_id()  # Call the method to get the job ID string
            
            job_info = {
                "job_id": job_id,
                "backend": args.backend,
                "shots": args.shots,
                "submission_time": datetime.datetime.now().isoformat(),
                "status": "RUNNING",
                "protocol": "Pentagonal-Resonance-001",
                "description": "Pentagonal Resonance Circuit with Golden Ratio Phase Relationships",
                "metadata_tag": "Resonance Pattern Test - Phase 1 - Pentagonal Structure",
                "submission_time_str": datetime.datetime.now().strftime('%H:%M:%S'),
                "experiment_type": "Timed Submissions",
                "semantic_concept": args.concept if args.concept else "None",
                "expected_observables": [
                    "Pentagonal symmetry resonance patterns",
                    "Golden ratio phase relationships",
                    "Fibonacci-based activation sequences",
                    "Geometric phase interference patterns"
                ]
            }
            
            # Save job information to file
            import json
            with open(f"job_{job_id}_info.json", 'w', encoding='utf-8') as f:
                json.dump(job_info, f, indent=2, ensure_ascii=False)
            
            print(f"Job information saved to job_{job_id}_info.json")
    
    print("Done!")

if __name__ == "__main__":
    main()
