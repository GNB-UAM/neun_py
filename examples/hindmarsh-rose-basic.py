#!/usr/bin/env python3
"""
hindmarsh-rose-basic.py

Basic Hindmarsh-Rose neuron example using neun_py, adapted from examples/basic.py.

The Hindmarsh-Rose model is a simplified model of neuronal activity that exhibits
bursting and chaotic behavior. It consists of three variables:
- x: membrane potential variable
- y: recovery variable  
- z: slow adaptation variable

Usage:
    python3 hindmarsh-rose-basic.py
    python3 hindmarsh-rose-basic.py --output data.dat
    python3 hindmarsh-rose-basic.py --plot sim.pdf
"""
import neun_py
import argparse
import sys
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(
        description='Single Hindmarsh-Rose neuron simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 hindmarsh-rose-basic.py
  python3 hindmarsh-rose-basic.py --output data.dat --plot sim.pdf
""")
    parser.add_argument('--plot', metavar='file.pdf', help='Plot simulation results to PDF file')
    parser.add_argument('--output', metavar='file.dat', help='Save voltage data to file')
    args = parser.parse_args()

    # Constructor args
    neuron_args = neun_py.HRDoubleConstructorArgs()

    # Create a Hindmarsh-Rose neuron with double precision and RungeKutta4 integrator
    neuron = neun_py.HRDoubleRK4(neuron_args)

    # Set typical Hindmarsh-Rose parameters for bursting behavior
    # These are the standard parameters from Hindmarsh & Rose (1984)
    neuron.set_param(neun_py.HRDoubleParameter.a, 1.0)
    neuron.set_param(neun_py.HRDoubleParameter.b, 3.0)
    neuron.set_param(neun_py.HRDoubleParameter.c, 1.0)
    neuron.set_param(neun_py.HRDoubleParameter.d, 5.0)
    neuron.set_param(neun_py.HRDoubleParameter.e, 3.281)
    neuron.set_param(neun_py.HRDoubleParameter.mu, 0.0029)
    neuron.set_param(neun_py.HRDoubleParameter.S, 4.0)
    neuron.set_param(neun_py.HRDoubleParameter.xr, -1.6)
    neuron.set_param(neun_py.HRDoubleParameter.vh, 1.0)

    print(f"Hindmarsh-Rose model parameters:")
    print(f"  a:  {neuron.get_param(neun_py.HRDoubleParameter.a)}")
    print(f"  b:  {neuron.get_param(neun_py.HRDoubleParameter.b)}")
    print(f"  c:  {neuron.get_param(neun_py.HRDoubleParameter.c)}")
    print(f"  d:  {neuron.get_param(neun_py.HRDoubleParameter.d)}")
    print(f"  e:  {neuron.get_param(neun_py.HRDoubleParameter.e)}")
    print(f"  mu: {neuron.get_param(neun_py.HRDoubleParameter.mu)}")
    print(f"  S:  {neuron.get_param(neun_py.HRDoubleParameter.S)}")
    print(f"  xr: {neuron.get_param(neun_py.HRDoubleParameter.xr)}")
    print(f"  vh: {neuron.get_param(neun_py.HRDoubleParameter.vh)}")

    # Initial conditions
    neuron.set(neun_py.HRDoubleVariable.x, -1.5)
    neuron.set(neun_py.HRDoubleVariable.y, -10.0)
    neuron.set(neun_py.HRDoubleVariable.z, 0.0)

    # Simulation parameters
    step = 0.01            # ms, integration step
    simulation_time = 1000.0  # ms

    # No external stimulus - the model exhibits intrinsic bursting
    times = []
    x_values = []  # membrane potential
    y_values = []  # recovery variable
    z_values = []  # slow adaptation

    output_file = None
    if args.output:
        try:
            output_file = open(args.output, 'w')
            output_file.write("# Time(ms) x y z\n")
            print(f"Saving data to: {args.output}")
        except IOError as e:
            print(f"Error: Could not open output file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)

    t = 0.0
    while t < simulation_time:
        # Add a small constant input (like a DC current)
        neuron.add_synaptic_input(0.0)
        
        neuron.step(step)

        x = neuron.get(neun_py.HRDoubleVariable.x)
        y = neuron.get(neun_py.HRDoubleVariable.y)
        z = neuron.get(neun_py.HRDoubleVariable.z)

        times.append(t)
        x_values.append(x)
        y_values.append(y)
        z_values.append(z)

        line = f"{t:.6f} {x:.6f} {y:.6f} {z:.6f}"
        if output_file:
            output_file.write(line + "\n")
        else:
            print(line)

        t += step

    if output_file:
        output_file.close()
        print(f"Data successfully written to: {args.output}")

    if args.plot:
        try:
            fig, axes = plt.subplots(3, 1, figsize=(12, 9))
            
            # Plot x (membrane potential)
            axes[0].plot(times, x_values, color='blue', linewidth=0.8)
            axes[0].set_ylabel('x (Membrane potential)')
            axes[0].set_title('Hindmarsh-Rose Neuron - Bursting Behavior')
            axes[0].grid(True, alpha=0.3)
            
            # Plot y (recovery variable)
            axes[1].plot(times, y_values, color='red', linewidth=0.8)
            axes[1].set_ylabel('y (Recovery)')
            axes[1].grid(True, alpha=0.3)
            
            # Plot z (slow adaptation)
            axes[2].plot(times, z_values, color='green', linewidth=0.8)
            axes[2].set_xlabel('Time (ms)')
            axes[2].set_ylabel('z (Slow adaptation)')
            axes[2].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(args.plot, format='pdf', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Plot successfully saved to: {args.plot}")
        except Exception as e:
            print(f"Error: Could not save plot to '{args.plot}': {e}", file=sys.stderr)
            sys.exit(1)

    if args.output or args.plot:
        print("Simulation completed:")
        print(f"  - Duration: {simulation_time} ms")
        print(f"  - Time step: {step} ms")
        print(f"  - Data points: {len(times)}")

if __name__ == "__main__":
    main()
