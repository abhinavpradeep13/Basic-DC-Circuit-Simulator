DC Circuit Simulator (OOP & Tkinter)

A Python-based DC Circuit Simulator that allows users to design, analyze, and solve electrical networks consisting of resistors and independent voltage sources. The project leverages Object-Oriented Programming (OOP) principles for its architecture and Modified Nodal Analysis (MNA) for its computational engine.

🚀 Features

OOP-Driven Architecture: Uses inheritance and polymorphism to model components (Resistors, Voltage Sources) through a unified interface.
Modified Nodal Analysis (MNA): Formulates circuit equations into a matrix system ($[G][x] = [I]$) and solves them using the NumPy linear algebra library.
Interactive GUI:Tabbed Interface: Dedicated tabs for adding resistors and voltage sources with specific node assignments.
Real-time Tracking: A listbox displays all currently added components in the circuit.
Result Display: Shows calculated node voltages and individual component currents in a formatted text area.
Data Management: Includes functionality to clear the current workspace or save the analysis results to a .txt file.
Error Handling: Provides user-friendly alerts for invalid inputs or unsolvable circuits (e.g., missing ground reference or conflicting sources).

🛠️ Technical Stack

Language: Python 3.x
GUI Framework: Tkinter / ttk
Numerical Computation: NumPy
Analysis Method: Modified Nodal Analysis (MNA)

📂 Project Structure

The code is organized into modular classes for clear separation of concerns:
CircuitComponent: The base class establishing the interface for all components (stamping and current calculation).
Resistor & VoltageSource: Derived classes that implement specific physical laws (Ohm's Law, conductance stamping).
Circuit: The core engine that manages the collection of components, builds the MNA matrices, and invokes the solver.
CircuitGUI: The interface layer handling user inputs, visual output, and event handling.

⚙️ Installation & Usage

Clone the repository:Bashgit clone https://github.com/your-username/dc-circuit-simulator.git
cd dc-circuit-simulator
Install dependencies:
pip install numpy
Run the application:
python "DC Circuit Simulator.py"

💡 How It Works

The simulator works by converting a visual circuit into a mathematical representation:
Stamping: Each component "stamps" its values into a conductance matrix (G) and a source vector (I).
Matrix Solving: The system solves the equation $[G][x] = [I]$ where $[x]$ contains the unknown node voltages and voltage source currents.
Output: The solver maps the results back to the GUI for the user to read.

💡 Applications & Advantages

This simulator serves as an excellent educational tool for learning circuit theory and demonstrating how OOP can be applied to engineering problems. Its modular design allows for easy scalability, meaning new components like dependent sources or capacitors can be added with minimal changes to the core solver

Developed as part of the Object-Oriented Programming curriculum.
