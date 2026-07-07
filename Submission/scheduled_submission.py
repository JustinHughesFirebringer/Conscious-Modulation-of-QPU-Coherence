#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scheduled Submissions for Pentagonal Resonance Circuit

This script schedules multiple submissions of the pentagonal resonance circuit
at regular intervals during a specified time window.
"""

import os
import sys
import time
import datetime
import subprocess
import argparse
from dotenv import load_dotenv

# Load environment variables from project .env (one level above this folder)
# This ensures authentication (e.g., IBM Cloud keys) comes from .env instead of CLI args
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

def parse_time(time_str):
    """Parse time string in format HH:MM:SS or HH:MM and return time object."""
    try:
        # Try HH:MM:SS format
        dt = datetime.datetime.strptime(time_str, "%H:%M:%S")
        return dt.time()
    except ValueError:
        try:
            # Try HH:MM format
            dt = datetime.datetime.strptime(time_str, "%H:%M")
            return dt.time()
        except ValueError:
            pass
    
    raise ValueError(f"Time string '{time_str}' does not match expected formats (HH:MM:SS or HH:MM)")

def wait_until(target_time):
    """Wait until the specified time."""
    now = datetime.datetime.now()
    current_time = now.time()
    target_datetime = datetime.datetime.combine(now.date(), target_time)
    
    # If target time is earlier today, it must be for tomorrow
    if current_time >= target_time:
        print(f"Target time {target_time.strftime('%H:%M:%S')} is in the past for today")
        print("Please specify a future time")
        return False
    
    time_to_wait = (target_datetime - now).total_seconds()
    if time_to_wait > 0:
        print(f"Waiting {time_to_wait:.1f} seconds until {target_time.strftime('%H:%M:%S')}...")
        time.sleep(time_to_wait)
        print(f"Time reached: {target_time.strftime('%H:%M:%S')}")
    
    return True

def submit_circuit(script_path, full_circuit=False, backend=None, concept=None):
    """
    Submit the pentagonal resonance circuit using the specified script.
    
    Args:
        script_path: Path to the pentagonal_resonance_circuit.py script
        full_circuit: Whether to use the full circuit (True) or reduced circuit (False)
        backend: IBM Quantum backend name (e.g., ibm_fez)
        concept: Semantic concept to encode in the circuit
    """
    cmd = [sys.executable, script_path, '--submit']
    
    if full_circuit:
        cmd.append('--full-circuit')
    if backend:
        cmd.extend(['--backend', backend])
    if concept:
        cmd.extend(['--concept', concept])
    
    print(f"Executing: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Print output in real-time
    for line in process.stdout:
        print(line.strip())
    
    process.wait()
    
    if process.returncode != 0:
        print("Error executing command:")
        for line in process.stderr:
            print(line.strip())
        return False
    
    return True

def schedule_submissions(script_path, start_time_str, end_time_str, interval_minutes, api_key=None, crn=None, full_circuit=False, backend=None, concepts=None):
    """
    Schedule multiple submissions at regular intervals within a time window.
    
    Args:
        script_path: Path to the pentagonal_resonance_circuit.py script
        start_time_str: Start time in format HH:MM:SS
        end_time_str: End time in format HH:MM:SS
        interval_minutes: Interval between submissions in minutes
        api_key: Optional IBM Cloud API key for authentication
        crn: Optional IBM Cloud CRN for instance selection
        full_circuit: Whether to use the full circuit (True) or reduced circuit (False)
        backend: IBM Quantum backend name (e.g., ibm_fez)
        concepts: List of semantic concepts to submit at each interval
    """
    # Parse start and end times as time objects
    start_time = parse_time(start_time_str)
    end_time = parse_time(end_time_str)
    
    # Convert to datetime objects for today
    today = datetime.datetime.now().date()
    start_dt = datetime.datetime.combine(today, start_time)
    end_dt = datetime.datetime.combine(today, end_time)
    
    if start_dt >= end_dt:
        print("Error: Start time must be before end time")
        return None, None
    
    # Calculate submission times
    current_dt = start_dt
    submission_times = []
    
    while current_dt <= end_dt:
        submission_times.append(current_dt.time())
        current_dt += datetime.timedelta(minutes=interval_minutes)
    
    # Build base command with credentials if provided
    # Use Python from the virtual environment
    venv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'quantum-venv')
    python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
    
    if not os.path.isfile(python_exe):
        print(f"Error: Virtual environment Python not found at {python_exe}")
        print("Please ensure the virtual environment is properly set up")
        return None, None
        
    base_cmd = [python_exe, script_path, "--submit"]
    # Authentication now relies on environment variables loaded from .env
    # Keep CLI compatibility but do not forward --api-key/--crn to child process
    if full_circuit:
        base_cmd.append("--full-circuit")
    if backend:
        base_cmd.extend(["--backend", backend])
    
    # Display schedule
    print(f"Scheduled {len(submission_times)} submissions:")
    for i, t in enumerate(submission_times, 1):
        print(f"  {i}. {t.strftime('%H:%M:%S')}")
        
    return base_cmd, submission_times
    
    # Wait for start time
    wait_until(start_time)
    
    # Execute submissions at scheduled times
    for i, submission_time in enumerate(submission_times, 1):
        print(f"\n=== Submission {i}/{len(submission_times)} at {submission_time.strftime('%H:%M:%S')} ===")
        
        # Wait until the exact submission time
        wait_until(submission_time)
        
        # Submit the circuit
        success = submit_circuit(script_path, full_circuit)
        
        if success:
            print(f"Submission {i}/{len(submission_times)} completed successfully")
        else:
            print(f"Submission {i}/{len(submission_times)} failed")
        
        # If this is not the last submission, wait for the next interval
        if i < len(submission_times):
            next_time = submission_times[i]
            print(f"Next submission scheduled for {next_time.strftime('%H:%M:%S')}")
    
    print("\nAll scheduled submissions completed!")

def main():
    """
    Main function to parse arguments and schedule submissions.
    """
    parser = argparse.ArgumentParser(description='Schedule multiple submissions of the pentagonal resonance circuit')
    parser.add_argument("--start", required=True, help="Start time in format HH:MM:SS")
    parser.add_argument("--end", required=True, help="End time in format HH:MM:SS")
    parser.add_argument("--interval", type=int, default=5, help="Interval between submissions in minutes")
    parser.add_argument("--script", default="pentagonal_resonance_circuit.py", help="Path to submission script")
    parser.add_argument("--full-circuit", action="store_true", help="Use full circuit instead of reduced version")
    parser.add_argument("--api-key", help="IBM Cloud API key for authentication")
    parser.add_argument("--crn", help="IBM Cloud CRN for instance selection")
    parser.add_argument("--backend", type=str, default="ibm_torino", help="IBM Quantum backend to use (e.g., ibm_torino, ibm_fez)")
    parser.add_argument("--concept", type=str, nargs="+", help="Semantic concept(s) to encode in the circuit (e.g., Remembrance Transmutation)")
    
    args = parser.parse_args()
    
    # Parse times and convert to datetime objects for today
    now = datetime.datetime.now()
    today = now.date()
    
    start_time = parse_time(args.start)
    end_time = parse_time(args.end)
    
    start_dt = datetime.datetime.combine(today, start_time)
    end_dt = datetime.datetime.combine(today, end_time)
    
    # Verify times are in the future
    if start_dt <= now:
        print(f"Error: Start time {args.start} is in the past")
        print("Please specify a future start time")
        sys.exit(1)
    
    if end_dt <= start_dt:
        print(f"Error: End time {args.end} must be after start time {args.start}")
        sys.exit(1)
    
    # Verify script exists
    script_path = args.script
    if not os.path.isfile(script_path):
        # Try relative to this script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, args.script)
        if not os.path.isfile(script_path):
            print(f"Error: Script not found at {args.script} or {script_path}")
            sys.exit(1)
    
    base_cmd, submission_times = schedule_submissions(
        script_path,
        args.start,
        args.end,
        args.interval,
        api_key=args.api_key,
        crn=args.crn,
        full_circuit=args.full_circuit,
        backend=args.backend,
        concepts=args.concept
    )
    
    if base_cmd is None:
        print("Error: Failed to create submission schedule")
        sys.exit(1)
    
    concepts = args.concept if args.concept else [None]
    
    print(f"\nBackend: {args.backend}")
    if args.concept:
        print(f"Semantic concepts: {', '.join(args.concept)}")
        print(f"Total submissions per time slot: {len(concepts)}")
        total = len(submission_times) * len(concepts)
        print(f"Total submissions: {total}")
    
    print("\nBase command that will be executed:")
    print(" ".join(base_cmd))
    
    print("\nPress Enter to start submissions or Ctrl+C to cancel...")
    input()
    
    try:
        # Wait for start time and execute submissions
        for t in submission_times:
            if not wait_until(t):
                print("Error: Invalid submission time, stopping schedule")
                break
            for concept in concepts:
                concept_label = concept if concept else "default"
                print(f"\nExecuting submission at {t.strftime('%H:%M:%S')} [concept: {concept_label}]...")
                cmd = list(base_cmd)
                if concept:
                    cmd.extend(["--concept", concept])
                subprocess.run(cmd, check=True)
                print(f"Submission complete [concept: {concept_label}]")
        
        print("\nAll scheduled submissions completed successfully!")
    except KeyboardInterrupt:
        print("\nSchedule interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during submissions: {str(e)}")
        sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
