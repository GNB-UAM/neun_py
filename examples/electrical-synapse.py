#!/usr/bin/env python3
"""
Python version of synapsis.cpp - Two coupled Hodgkin-Huxley neurons with electrical synapse

This example demonstrates:
- Creating two Hodgkin-Huxley neurons with identical parameters
- Connecting them with an electrical synapse
- Setting different initial conditions
- Adding external current inputs
- Running a coupled simulation
- Monitoring both neurons and the synaptic current

Usage:
    python3 synapsis.py                           # Print to stdout
    python3 synapsis.py --output file.dat         # Save data to file.dat
    python3 synapsis.py --plot file.pdf           # Save plot to file.pdf
    python3 synapsis.py --output data.dat --plot sim.pdf  # Both options
    python3 synapsis.py --help                    # Show help
"""

import sys
import os
import argparse
import neun_py, numpy
import matplotlib.pyplot as plt

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Two coupled Hodgkin-Huxley neurons with electrical synapse',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 synapsis.py                           # Print to stdout
  python3 synapsis.py --output data.dat         # Save data to file
  python3 synapsis.py --plot simulation.pdf     # Save plot to PDF
  python3 synapsis.py --output data.dat --plot sim.pdf  # Both options
        """)
    
    parser.add_argument('--plot', metavar='file.pdf', 
                       help='Plot simulation results to PDF file')
    parser.add_argument('--output', metavar='file.dat',
                       help='Save voltage data to file (columns: Time V1 V2 SynapticCurrent)')
    
    args = parser.parse_args()
    
    # Create constructor arguments for the neurons
    neuron_args = neun_py.HHDoubleConstructorArgs()
    
    # Create two Hodgkin-Huxley neurons with double precision and RungeKutta4 integrator
    h1 = neun_py.HHDoubleRK4(neuron_args)
    h2 = neun_py.HHDoubleRK4(neuron_args)
    
    # Set the parameter values for both neurons (same as C++ version)
    for neuron in [h1, h2]:
        neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
        neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
        neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
        neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
        neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
        neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
        neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
    
    # Set initial value of V in neuron h1 (h2 keeps default)
    h1.set(neun_py.HHDoubleVariable.v, -75)
    
    # Create electrical synapse between the neurons
    # Parameters: neuron1, variable1, neuron2, variable2, conductance1, conductance2
    s1 = neun_py.ESynHHHHDoubleRK4(
        h1, neun_py.HHDoubleVariable.v,
        h2, neun_py.HHDoubleVariable.v,
        -0.002, -0.002
    )
    
    # Simulation parameters
    step = 0.001  # Integration step
    simulation_time = 100  # Total simulation time (reduced for consistency with basic.py)
    
    # Storage for results
    times = []
    v1_values = []
    v2_values = []
    synaptic_currents = []
    
    # Open output file if specified
    output_file = None
    if args.output:
        try:
            output_file = open(args.output, 'w')
            output_file.write("# Time(ms) V1(mV) V2(mV) SynapticCurrent\n")
            print(f"Saving voltage data to: {args.output}")
        except IOError as e:
            print(f"Error: Could not open output file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)
    
    # Perform the simulation
    time = 0.0
    while time < simulation_time:
        # Step the synapse first (if available)
        s1.step(step)
        
        # Add external current input to h1
        h1.add_synaptic_input(0.1)
        
        # Step both neurons
        h1.step(step)
        h2.step(step)
        
        # Get voltage values
        v1 = h1.get(neun_py.HHDoubleVariable.v)
        v2 = h2.get(neun_py.HHDoubleVariable.v)
        
        # Store results
        times.append(time)
        v1_values.append(v1)
        v2_values.append(v2)
        
        # Get synaptic current (if available)
        synaptic_current = s1.get(neun_py.ESynDoubleVariable.i1)
        synaptic_currents.append(synaptic_current)
        
        # Output data
        output_line = f"{time:.6f} {v1:.6f} {v2:.6f} {synaptic_current:.6f}"
        
        if output_file:
            # Write to file
            output_file.write(output_line + "\n")
        else:
            # Print to stdout (default behavior)
            print(output_line)
        
        time += step
    
    # Close output file
    if output_file:
        output_file.close()
        print(f"Data successfully written to: {args.output}")
    
    # Generate plot if requested
    if args.plot:
        if plt is None:
            print("Error: matplotlib not available for plotting")
            print("Install with: pip install neun-py[plotting]")
            sys.exit(1)
        
        try:
            # Create plots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot membrane potentials
            ax1.plot(times, v1_values, label='Neuron 1', linewidth=1.5, color='blue')
            ax1.plot(times, v2_values, label='Neuron 2', linewidth=1.5, color='red')
            ax1.set_ylabel('Membrane Potential (mV)')
            ax1.set_title('Coupled Hodgkin-Huxley Neurons via Electrical Synapse')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot synaptic current
            ax2.plot(times, synaptic_currents, linewidth=1.5, color='purple')
            ax2.set_ylabel('Synaptic Current')
            ax2.set_title('Electrical Synaptic Current')
            ax2.set_xlabel('Time (ms)')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save to PDF
            plt.savefig(args.plot, format='pdf', dpi=300, bbox_inches='tight')
            print(f"Plot successfully saved to: {args.plot}")
            
            # Don't show interactive plot when saving to file
            plt.close()
            
        except Exception as e:
            print(f"Error: Could not save plot to '{args.plot}': {e}", file=sys.stderr)
            sys.exit(1)
    
    # Show summary
    if args.output or args.plot:
        print(f"Simulation completed:")
        print(f"  - Duration: {simulation_time} ms")
        print(f"  - Time step: {step} ms")
        print(f"  - Data points: {len(times)}")

if __name__ == "__main__":
    main()