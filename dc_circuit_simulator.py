import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np


# ---------------- Circuit Components ---------------- #

class CircuitComponent:

    # Base class for all circuit components
    # Every component must define its nodes, how it "stamps" into the system,
    # and how to calculate its current after solving
    def nodes(self):
        raise NotImplementedError

    def stamp(self, G, I, B, C_row, node_map, vs_index=None):
        raise NotImplementedError
 
    def current(self, voltages, currents_source=None, vs_index=None):
        raise NotImplementedError


class Resistor(CircuitComponent):

    # Resistor defined by two nodes and its resistance value
    def __init__(self, node1, node2, resistance):
        self.node1 = node1
        self.node2 = node2
        self.resistance = resistance

    def nodes(self):
        return (self.node1, self.node2)

    def stamp(self, G, I, B, C_row, node_map, vs_index=None):
        # Stamp resistor into conductance matrix G
        n1 = node_map.get(self.node1, None)
        n2 = node_map.get(self.node2, None)
        g = 1 / self.resistance  # Convert resistance to conductance
        if n1 is not None:
            G[n1, n1] += g
        if n2 is not None:
            G[n2, n2] += g
        if n1 is not None and n2 is not None:
            G[n1, n2] -= g
            G[n2, n1] -= g

    def current(self, voltages, currents_source=None, vs_index=None):
        # Calculate resistor current using Ohm's law: I = (V1 - V2) / R
        v1 = voltages.get(self.node1, 0)
        v2 = voltages.get(self.node2, 0)
        return (v1 - v2) / self.resistance


class VoltageSource(CircuitComponent):

    # Independent voltage source between two nodes
    def __init__(self, node_pos, node_neg, voltage):
        self.node_pos = node_pos
        self.node_neg = node_neg
        self.voltage = voltage

    def nodes(self):
        return (self.node_pos, self.node_neg)

    def stamp(self, G, I, B, C_row, node_map, vs_index):
        # Add voltage source equations into matrix
        # A voltage source introduces an extra equation and unknown (its current)
        n_pos = node_map.get(self.node_pos, None)
        n_neg = node_map.get(self.node_neg, None)

        # Positive terminal: +1
        if n_pos is not None:
            G[n_pos, C_row] += 1
            G[C_row, n_pos] += 1

        # Negative terminal: -1
        if n_neg is not None:
            G[n_neg, C_row] -= 1
            G[C_row, n_neg] -= 1

        # Voltage value goes into RHS vector
        I[C_row] += self.voltage

    def current(self, voltages, currents_source=None, vs_index=None):
        # Current through source comes from solution vector
        # Negative sign makes positive current = delivering power
        if currents_source is None or vs_index is None:
            return None
        return -currents_source[vs_index]


class Circuit:

    # Represents the entire circuit and handles solving
    def __init__(self):
        self.components = []   # Stores all components
        self.nodes_set = set() # Tracks all unique node numbers
        self.vsources = []     # Stores all voltage sources separately

    def add_component(self, comp):
        # Add a component and update node list
        self.components.append(comp)
        self.nodes_set.update(comp.nodes())
        if isinstance(comp, VoltageSource):
            self.vsources.append(comp)

    def solve(self):
        # Solve circuit using Modified Nodal Analysis (MNA)

        # Ignore ground (node 0), only map non-ground nodes
        non_ground_nodes = sorted(n for n in self.nodes_set if n != 0)
        node_map = {node: idx for idx, node in enumerate(non_ground_nodes)}

        N = len(non_ground_nodes)   # Number of node voltages to find
        M = len(self.vsources)      # Number of voltage sources (extra equations)

        # Build empty system of equations
        size = N + M                # Total equations = nodes + sources
        G = np.zeros((size, size))  # Conductance matrix
        I = np.zeros(size)          # RHS current/voltage vector
        B = np.zeros((N, M))        # Not used here, placeholder

        # Stamp each component into the system
        for comp in self.components:
            if isinstance(comp, VoltageSource):
                vs_index = self.vsources.index(comp)
                comp.stamp(G, I, B, N + vs_index, node_map, vs_index)
            else:
                comp.stamp(G, I, B, None, node_map)

        # Solve the linear system [G][x] = [I]
        x = np.linalg.solve(G, I)

        # Extract node voltages
        voltages = {0: 0.0}  # Ground node always 0 V
        for node, idx in node_map.items():
            voltages[node] = x[idx]

        # Extract source currents (appear after voltages in x)
        currents_source = x[N:] if M > 0 else []

        return voltages, currents_source

    def print_results(self, voltages, currents_source):
        # Format results into a readable string
        output = []
        output.append("Node Voltages:")
        for node in sorted(voltages.keys()):
            output.append(f"Node {node}: {voltages[node]:.4f} V")

        output.append("\nComponent Currents:")
        for idx, comp in enumerate(self.components):
            if isinstance(comp, VoltageSource):
                current_val = comp.current(voltages, currents_source, self.vsources.index(comp))
                output.append(f"Voltage Source {idx + 1} (Node {comp.node_pos} to Node {comp.node_neg}): {current_val:.6f} A")
            elif isinstance(comp, Resistor):
                current_val = comp.current(voltages)
                output.append(f"Resistor {idx + 1} (Node {comp.node1} to Node {comp.node2}): {current_val:.6f} A")

        return "\n".join(output)


# ---------------- GUI ---------------- #

class CircuitGUI:
    
    # Graphical user interface for building and solving circuits
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Solver")
        self.circuit = Circuit()  # New empty circuit

        # Notebook with two tabs: Resistor and Voltage Source
        tab_control = ttk.Notebook(root)
        self.res_tab = ttk.Frame(tab_control)
        self.vsrc_tab = ttk.Frame(tab_control)
        tab_control.add(self.res_tab, text="Add Resistor")
        tab_control.add(self.vsrc_tab, text="Add Voltage Source")
        tab_control.pack(expand=1, fill="both")

        # ----- Resistor Tab -----
        ttk.Label(self.res_tab, text="Resistance (Ω):").grid(row=0, column=0)
        self.res_val = ttk.Entry(self.res_tab)
        self.res_val.grid(row=0, column=1)

        ttk.Label(self.res_tab, text="Node 1:").grid(row=1, column=0)
        self.res_n1 = ttk.Entry(self.res_tab)
        self.res_n1.grid(row=1, column=1)

        ttk.Label(self.res_tab, text="Node 2:").grid(row=2, column=0)
        self.res_n2 = ttk.Entry(self.res_tab)
        self.res_n2.grid(row=2, column=1)

        ttk.Button(self.res_tab, text="Add Resistor", command=self.add_resistor).grid(row=3, column=0, columnspan=2)

        # ----- Voltage Source Tab -----
        ttk.Label(self.vsrc_tab, text="Voltage (V):").grid(row=0, column=0)
        self.vsrc_val = ttk.Entry(self.vsrc_tab)
        self.vsrc_val.grid(row=0, column=1)

        ttk.Label(self.vsrc_tab, text="Node +:").grid(row=1, column=0)
        self.vsrc_n1 = ttk.Entry(self.vsrc_tab)
        self.vsrc_n1.grid(row=1, column=1)

        ttk.Label(self.vsrc_tab, text="Node -:").grid(row=2, column=0)
        self.vsrc_n2 = ttk.Entry(self.vsrc_tab)
        self.vsrc_n2.grid(row=2, column=1)

        ttk.Button(self.vsrc_tab, text="Add Voltage Source", command=self.add_vsource).grid(row=3, column=0, columnspan=2)

        # Listbox shows all components currently in circuit
        self.comp_list = tk.Listbox(root, height=8, width=50)
        self.comp_list.pack(pady=5)

        # Buttons for actions: Solve, Clear, Save
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Solve Circuit", command=self.solve_circuit).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Clear Circuit", command=self.clear_circuit).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Save Results", command=self.save_results).grid(row=0, column=2, padx=5)

        # Text box to display results after solving
        self.results_box = tk.Text(root, height=15, width=60)
        self.results_box.pack(pady=5)

    def add_resistor(self):
        # Add resistor from user inputs
        try:
            r = float(self.res_val.get())
            n1 = int(self.res_n1.get())
            n2 = int(self.res_n2.get())
            comp = Resistor(n1, n2, r)
            self.circuit.add_component(comp)
            self.comp_list.insert(tk.END, f"Resistor: {r}Ω between Node {n1} and {n2}")
            # Clear fields for next input
            self.res_val.delete(0, tk.END)
            self.res_n1.delete(0, tk.END)
            self.res_n2.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid input for resistor")

    def add_vsource(self):
        # Add voltage source from user inputs
        try:
            v = float(self.vsrc_val.get())
            n1 = int(self.vsrc_n1.get())
            n2 = int(self.vsrc_n2.get())
            comp = VoltageSource(n1, n2, v)
            self.circuit.add_component(comp)
            self.comp_list.insert(tk.END, f"Voltage Source: {v}V between Node {n1} and {n2}")
            # Clear fields for next input
            self.vsrc_val.delete(0, tk.END)
            self.vsrc_n1.delete(0, tk.END)
            self.vsrc_n2.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid input for voltage source")

    def solve_circuit(self):
        # Try to solve circuit and display results
        try:
            voltages, currents_source = self.circuit.solve()
            results = self.circuit.print_results(voltages, currents_source)
            self.results_box.delete(1.0, tk.END)
            self.results_box.insert(tk.END, results)
        except np.linalg.LinAlgError:
            # Friendly message instead of raw "Singular matrix"
            messagebox.showerror(
                "Invalid Circuit",
                "Circuit cannot be solved.\n\nPossible reasons:\n"
                "- Missing ground reference (node 0)\n"
                "- Conflicting voltage sources\n"
                "- Floating or unconnected nodes"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def clear_circuit(self):
        # Clear all components and results to start a new circuit
        self.circuit = Circuit()
        self.comp_list.delete(0, tk.END)
        self.results_box.delete(1.0, tk.END)

    def save_results(self):
        # Save results to a text file
        results = self.results_box.get(1.0, tk.END).strip()
        if not results:
            messagebox.showwarning("Warning", "No results to save")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(results)
            messagebox.showinfo("Saved", f"Results saved to {file_path}")


# ---------------- Run GUI ---------------- #

if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitGUI(root)
    root.mainloop()
