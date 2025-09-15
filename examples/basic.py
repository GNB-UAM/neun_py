#!/usr/bin/env python3
"""
Python version of basic.cpp - Single Hodgkin-Huxley neuron simulation

This example demonstrates:
- Creating a Hodgkin-Huxley neuron with specific parameters
- Setting initial conditions for variables
- Running a simulation loop
- Accessing neuron state variables

Usage:
    python3 basic.py                           # Print to stdout
    python3 basic.py --output file.dat         # Save data to file.dat
    python3 basic.py --plot file.pdf           # Save plot to file.pdf
    python3 basic.py --output data.dat --plot sim.pdf  # Both options
    python3 basic.py --help                    # Show help
"""
import neun_py
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Single Hodgkin-Huxley neuron simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 basic.py                           # Print to stdout
  python3 basic.py --output data.dat         # Save data to file
  python3 basic.py --plot sim.pdf            # Save plot to PDF
  python3 basic.py --output data.dat --plot sim.pdf  # Both options
        """)
    
    parser.add_argument('--plot', metavar='file.pdf', 
                       help='Plot simulation results to PDF file')
    parser.add_argument('--output', metavar='file.dat',
                       help='Save voltage data to file')
    
    args = parser.parse_args()
    
    # Create constructor arguments for the neuron
    neuron_args = neun_py.HHDoubleConstructorArgs()
    
    # Create a Hodgkin-Huxley neuron with double precision and RungeKutta4 integrator
    neuron = neun_py.HHDoubleRK4(neuron_args)
    
    # Set the parameter values (equivalent to C++ version)
    neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
    neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
    neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
    
    # Set initial conditions for the neuron variables
    neuron.set_var(neun_py.HHDoubleVariable.v, -80)
    neuron.set_var(neun_py.HHDoubleVariable.m, 0.1)
    neuron.set_var(neun_py.HHDoubleVariable.n, 0.7)
    neuron.set_var(neun_py.HHDoubleVariable.h, 0.01)
    
    # Simulation parameters
    step = 0.001  # Integration step
    simulation_time = 100  # Total simulation time
    
    # Storage for results
    times = []
    voltages = []
    
    # Open output file if specified
    output_file = None
    if args.output:
        try:
            output_file = open(args.output, 'w')
            output_file.write("# Time(ms) Voltage(mV)\n")
            print(f"Saving voltage data to: {args.output}")
        except IOError as e:
            print(f"Error: Could not open output file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)
    
    # Perform the simulation
    time = 0.0
    while time < simulation_time:
        # Step the neuron forward
        neuron.add_synaptic_input(0.1)
        neuron.step(step)
        
        # Get current voltage
        voltage = neuron.get(neun_py.HHDoubleVariable.v)
        
        # Store results for plotting
        times.append(time)
        voltages.append(voltage)
        
        # Output data
        output_line = f"{time:.6f} {voltage:.6f}"
        
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
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(times, voltages, linewidth=1.5, color='blue')
            plt.xlabel('Time (ms)')
            plt.ylabel('Membrane Potential (mV)')
            plt.title('Hodgkin-Huxley Neuron - Basic Simulation')
            plt.grid(True, alpha=0.3)
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