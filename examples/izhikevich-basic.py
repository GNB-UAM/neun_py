#!/usr/bin/env python3
"""
izhikevich-basic.py

Basic Izhikevich neuron example using neun_py, adapted from examples/basic.py.

Usage:
    python3 izhikevich-basic.py
    python3 izhikevich-basic.py --output data.dat
    python3 izhikevich-basic.py --plot sim.pdf
"""
import neun_py
import argparse
import sys
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(
        description='Single Izhikevich neuron simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 izhikevich-basic.py
  python3 izhikevich-basic.py --output data.dat --plot sim.pdf
""")
    parser.add_argument('--plot', metavar='file.pdf', help='Plot simulation results to PDF file')
    parser.add_argument('--output', metavar='file.dat', help='Save voltage data to file')
    args = parser.parse_args()

    # Constructor args (if the binding requires them)
    neuron_args = neun_py.IzDoubleConstructorArgs()

    # Create an Iz neuron (Euler integrator is common for this model)
    neuron = neun_py.IzDoubleRK4(neuron_args)

    # Typical Iz regular-spiking parameters
    neuron.set_param(neun_py.IzDoubleParameter.a, 0.02)
    neuron.set_param(neun_py.IzDoubleParameter.b, 0.2)
    neuron.set_param(neun_py.IzDoubleParameter.c, -65.0)
    neuron.set_param(neun_py.IzDoubleParameter.d, 8.0)

    print(f"a: {neuron.get_param(neun_py.IzDoubleParameter.a)}")
    print(f"b: {neuron.get_param(neun_py.IzDoubleParameter.b)}")
    print(f"c: {neuron.get_param(neun_py.IzDoubleParameter.c)}")
    print(f"d: {neuron.get_param(neun_py.IzDoubleParameter.d)}")

    # Initial conditions: membrane potential v and recovery variable u
    neuron.set(neun_py.IzDoubleVariable.v, -65.0)
    # u initialized to b * v (common choice)
    b = neuron.get_param(neun_py.IzDoubleParameter.b)
    neuron.set(neun_py.IzDoubleVariable.u, b * -65.0)

    # Simulation parameters
    step = 0.1            # ms, integration step
    simulation_time = 300.0  # ms

    # Stimulus: DC current injected between 0 ms and 300 ms
    def stimulus(t_ms):
        return 20.0 if 0 <= t_ms <= 300.0 else 0.0

    times = []
    voltages = []

    output_file = None
    if args.output:
        try:
            output_file = open(args.output, 'w')
            output_file.write("# Time(ms) Voltage(mV)\n")
            print(f"Saving voltage data to: {args.output}")
        except IOError as e:
            print(f"Error: Could not open output file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)

    t = 0.0
    while t < simulation_time:
        I_ext = stimulus(t)

        # Provide input to the neuron; API may be add_current or set_input_current depending on binding
        # Try to use a generic name expected in neun_py
        try:
            neuron.add_current(I_ext)
        except AttributeError:
            try:
                neuron.set_input_current(I_ext)
            except AttributeError:
                # Fallback: some bindings expect add_synaptic_input
                neuron.add_synaptic_input(I_ext)

        neuron.step(step)

        v = neuron.get(neun_py.IzDoubleVariable.v)

        times.append(t)
        voltages.append(v)

        line = f"{t:.6f} {v:.6f}"
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
            plt.figure(figsize=(10, 4))
            plt.plot(times, voltages, color='blue', linewidth=1)
            plt.xlabel('Time (ms)')
            plt.ylabel('Membrane potential (mV)')
            plt.title('Izhikevich neuron - Basic simulation')
            plt.grid(True, alpha=0.3)
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