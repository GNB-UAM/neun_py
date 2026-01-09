#!/usr/bin/env python3
"""
Python example of diffusion synapse - Two coupled Hodgkin-Huxley neurons

This example demonstrates:
- Creating two Hodgkin-Huxley neurons with identical parameters
- Connecting them with a diffusion synapse (Destexhe et al. 1994)
- Setting different initial conditions
- Adding external current inputs
- Running a coupled simulation with chemical synaptic transmission
- Monitoring both neurons and the synaptic variables

The diffusion synapse implements neurotransmitter-mediated chemical synaptic
transmission with:
- Neurotransmitter release triggered by presynaptic threshold crossing
- Exponential rise and decay dynamics of neurotransmitter concentration
- Postsynaptic current proportional to neurotransmitter and driving force

Usage:
    python3 diffusion-synapse.py                           # Print to stdout
    python3 diffusion-synapse.py --output file.dat         # Save data to file.dat
    python3 diffusion-synapse.py --plot file.pdf           # Save plot to file.pdf
    python3 diffusion-synapse.py --output data.dat --plot sim.pdf  # Both options
    python3 diffusion-synapse.py --help                    # Show help
"""

import sys
import os
import argparse
import neun_py

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Two coupled Hodgkin-Huxley neurons with diffusion synapse (Destexhe et al. 1994)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 diffusion-synapse.py                           # Print to stdout
  python3 diffusion-synapse.py --output data.dat         # Save data to file
  python3 diffusion-synapse.py --plot simulation.pdf     # Save plot to PDF
  python3 diffusion-synapse.py --output data.dat --plot sim.pdf  # Both options
        """)
    
    parser.add_argument('--plot', metavar='file.pdf', 
                       help='Plot simulation results to PDF file')
    parser.add_argument('--output', metavar='file.dat',
                       help='Save data to file (columns: Time V1 V2 SynapticCurrent NeurotransmitterConc)')
    
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
    
    # Set initial values for both neurons to avoid NaN
    # Default HH resting state
    h1.set(neun_py.HHDoubleVariable.v, -65.0)
    h1.set(neun_py.HHDoubleVariable.h, 0.6)
    h1.set(neun_py.HHDoubleVariable.m, 0.05)
    h1.set(neun_py.HHDoubleVariable.n, 0.32)
    
    h2.set(neun_py.HHDoubleVariable.v, -65.0)
    h2.set(neun_py.HHDoubleVariable.h, 0.6)
    h2.set(neun_py.HHDoubleVariable.m, 0.05)
    h2.set(neun_py.HHDoubleVariable.n, 0.32)
    
    # Create diffusion synapse between the neurons
    # Following Destexhe et al. 1994 parameters for GABAergic synapse
    
    # Create constructor args for the synapse
    synapse_args = neun_py.DSynDoubleConstructorArgs()
    
    # Set synapse parameters (GABAergic inhibitory synapse)
    # Based on Destexhe et al. 1994: "Synthesis of models for excitable membranes..."
    synapse_args.set_param(neun_py.DSynDoubleParameter.alpha, 5.0)          # Rise rate (1/ms)
    synapse_args.set_param(neun_py.DSynDoubleParameter.beta, 0.18)          # Decay rate (1/ms)
    synapse_args.set_param(neun_py.DSynDoubleParameter.threshold, -20.0)    # Threshold (mV)
    synapse_args.set_param(neun_py.DSynDoubleParameter.esyn, -75.0)         # Reversal potential (mV)
    synapse_args.set_param(neun_py.DSynDoubleParameter.gsyn, 0.015)         # Max conductance
    synapse_args.set_param(neun_py.DSynDoubleParameter.T, 1.0)              # Transmitter conc at release
    synapse_args.set_param(neun_py.DSynDoubleParameter.max_release_time, 1.0)  # Release duration (ms)
    
    # Create the diffusion synapse
    # Parameters: neuron1, variable1, neuron2, variable2, constructor_args, integration_steps
    s1 = neun_py.DSynHHHHDoubleRK4(
        h1, neun_py.HHDoubleVariable.v,
        h2, neun_py.HHDoubleVariable.v,
        synapse_args,
        1  # integration steps per synapse step
    )
    
    print("=" * 70)
    print("Diffusion Synapse Example - Destexhe et al. 1994")
    print("=" * 70)
    print("\nSynapse parameters (GABAergic inhibitory):")
    print(f"  alpha (rise rate):        {synapse_args.get_param(neun_py.DSynDoubleParameter.alpha):.3f} 1/ms")
    print(f"  beta (decay rate):        {synapse_args.get_param(neun_py.DSynDoubleParameter.beta):.3f} 1/ms")
    print(f"  threshold:                {synapse_args.get_param(neun_py.DSynDoubleParameter.threshold):.1f} mV")
    print(f"  esyn (reversal):          {synapse_args.get_param(neun_py.DSynDoubleParameter.esyn):.1f} mV")
    print(f"  gsyn (max conductance):   {synapse_args.get_param(neun_py.DSynDoubleParameter.gsyn):.3f}")
    print(f"  T (transmitter):          {synapse_args.get_param(neun_py.DSynDoubleParameter.T):.1f}")
    print(f"  max_release_time:         {synapse_args.get_param(neun_py.DSynDoubleParameter.max_release_time):.1f} ms")
    print("=" * 70)
    print()
    
    # Simulation parameters
    step = 0.01  # Integration step (ms)
    simulation_time = 100  # Total simulation time (ms)
    
    # Storage for results
    times = []
    v1_values = []
    v2_values = []
    synaptic_currents = []
    neurotransmitter_concs = []
    
    # Open output file if specified
    output_file = None
    if args.output:
        try:
            output_file = open(args.output, 'w')
            output_file.write("# Time(ms) V1(mV) V2(mV) SynapticCurrent NeurotransmitterConc\n")
            print(f"Saving data to: {args.output}")
        except IOError as e:
            print(f"Error: Could not open output file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)
    
    # Perform the simulation
    print("Running simulation with diffusion synapse...\n")
    time = 0.0
    while time < simulation_time:
        # Step the synapse first
        s1.step(step)
        
        # Add external current input to h1 to trigger spiking
        h1.add_synaptic_input(0.5)
        
        # Step both neurons
        h1.step(step)
        h2.step(step)
        
        # Get voltage values
        v1 = h1.get(neun_py.HHDoubleVariable.v)
        v2 = h2.get(neun_py.HHDoubleVariable.v)
        
        # Get synaptic variables
        synaptic_current = s1.get(neun_py.DSynDoubleVariable.i)
        neurotransmitter = s1.get(neun_py.DSynDoubleVariable.r)
        
        # Store results
        times.append(time)
        v1_values.append(v1)
        v2_values.append(v2)
        synaptic_currents.append(synaptic_current)
        neurotransmitter_concs.append(neurotransmitter)
        
        # Output data
        output_line = f"{time:.6f} {v1:.6f} {v2:.6f} {synaptic_current:.6f} {neurotransmitter:.6f}"
        
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
        print(f"\nData successfully written to: {args.output}")
    
    # Generate plot if requested
    if args.plot:
        if plt is None:
            print("Error: matplotlib not available for plotting")
            print("Install with: pip install matplotlib")
            sys.exit(1)
        
        try:
            # Create plots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
            
            # Plot membrane potentials
            ax1.plot(times, v1_values, label='Presynaptic Neuron (h1)', linewidth=1.5, color='blue')
            ax1.plot(times, v2_values, label='Postsynaptic Neuron (h2)', linewidth=1.5, color='red')
            ax1.set_ylabel('Membrane Potential (mV)')
            ax1.set_title('Coupled Hodgkin-Huxley Neurons via Diffusion Synapse')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot neurotransmitter concentration
            ax2.plot(times, neurotransmitter_concs, linewidth=1.5, color='green')
            ax2.set_ylabel('Neurotransmitter Conc. (r)')
            ax2.set_title('Neurotransmitter Release Dynamics')
            ax2.grid(True, alpha=0.3)
            
            # Plot synaptic current
            ax3.plot(times, synaptic_currents, linewidth=1.5, color='purple')
            ax3.set_ylabel('Synaptic Current (i)')
            ax3.set_xlabel('Time (ms)')
            ax3.set_title('Postsynaptic Current')
            ax3.grid(True, alpha=0.3)
            
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
        print(f"\nSimulation completed:")
        print(f"  - Duration: {simulation_time} ms")
        print(f"  - Time step: {step} ms")
        print(f"  - Data points: {len(times)}")
        print(f"\nSynaptic activity:")
        print(f"  - Mean neurotransmitter: {sum(neurotransmitter_concs)/len(neurotransmitter_concs):.6f}")
        print(f"  - Mean synaptic current: {sum(synaptic_currents)/len(synaptic_currents):.6f}")

if __name__ == "__main__":
    main()
