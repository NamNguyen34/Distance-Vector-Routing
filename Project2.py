#Name: Nam Nguyen
#UTA ID: 1001823561

#Import modules for functions in this project
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import time

#Set infinity as 16 as specified in the project
INFINITY = 16  

#Node class
class Node:
    #Initialize the node with its ID and a reference to the GUI class
    def __init__(self, id, gui):
        self.id = id
        self.gui = gui
        self.dv_table = {}
        self.edges = {}

    #Initialize the distance vector table with its initial provided distance
    def init_dv(self, init_dist):
        self.dv_table = init_dist.copy()
        self.dv_table[self.id] = 0  

    #Update the distance vectore table with a new received distance
    def update_dv(self, received_dv, src_node):
        updated = False
        for dest, received_cost in received_dv.items():

            if dest in self.dv_table:
                #Calculate the new cost to the destination node from the received dv
                new_cost = self.edges[src_node] + received_cost

                #If the new cost is lower, update the distance vector
                if new_cost < self.dv_table.get(dest, INFINITY):
                    self.dv_table[dest] = new_cost
                    updated = True
        return updated

    #Receive a distance vectore from a source node and and update the table
    def receive_dv(self, received_dv, src_node):
        updated = self.update_dv(received_dv, src_node)

        #If the updated flag is True, then send the distance vector to the neighbor nodes
        if updated:
            self.send_dv_to_neighbors()

    #Iterate through the neighbor nodes and send the current node's distance vector to the neighbor if the neighbore node exists
    def send_dv_to_neighbors(self):
        for neighbor_id in self.edges:
            neighbor_node = self.gui.dv_tables.get(neighbor_id)

            if neighbor_node is not None:
                neighbor_node.receive_dv(self.dv_table, self.id)

    #Add an edge to the neighbor node with a specified cost
    def add_edge(self, neighbor_id, cost):
        self.edges[neighbor_id] = cost

        #Also add the edge to the gui's DV dictionary
        self.gui.DV[self.id][neighbor_id] = cost

    #Update the link cost to the neighbor node specified in the argument
    def update_link_cost(self, neighbor_id, new_cost):
        self.edges[neighbor_id] = new_cost

        #Notify the gui to update its DV dictionary
        self.gui.update_DV_link_cost(self.id, neighbor_id, new_cost)

        #Re-run the DV algorithm on this node to reflect changes
        self.gui.run_dv_algorithm_for_node(self.id)

#GUI class
class GUI:
    #Initalize the GUI window with a title
    def __init__(self, master):
        self.master = master
        self.master.title("Distance Vector Routing Simulator")

        #Create a file selection button
        self.file_button = tk.Button(self.master, text="Select Input File", command=self.select_input_file)
        self.file_button.pack()

        #Create text box to display logs
        self.log_text = tk.Text(self.master, wrap="word", height=10)
        self.log_text.pack()

        #Create a single step execution button
        self.single_step_button = tk.Button(self.master, text="Run Single Step", command=self.run_single_step)
        self.single_step_button.pack()

        #Create a full algorithm execution button
        self.run_full_button = tk.Button(self.master, text="Run Full Algorithm", command=self.run_full_algorithm)
        self.run_full_button.pack()

        #Create an entry to allow link cost change
        self.change_cost_label = tk.Label(self.master, text="Change Link Cost:")
        self.change_cost_label.pack()

        self.change_cost_entry = tk.Entry(self.master)
        self.change_cost_entry.pack()

        self.change_cost_button = tk.Button(self.master, text="Apply Link Cost", command=self.apply_link_cost)
        self.change_cost_button.pack()

        #Initialize DV and DV tables
        self.DV = {}
        self.dv_tables = {}
        self.original_link_costs = {}
        self.input_file = None

        #Create a frame for displaying DV tables
        self.dv_table_frame = tk.Frame(self.master)
        self.dv_table_frame.pack()

    #Initalize a file dialog to select an input file
    def select_input_file(self):
        file_path = filedialog.askopenfilename(title="Select DV File")
        if file_path:
            self.input_file = file_path
            self.log_text.insert(tk.END, f"Selected input file: {file_path}\n")
            self.setup_initial_DV()
            self.display_dv_tables()

    #Initialize a function to read the selected input file and set up initial distance vector tables
    def setup_initial_DV(self):
        with open(self.input_file, 'r') as file:
            nodes = set()
            for line in file:
                node1, node2, cost = map(int, line.strip().split())
                nodes.add(node1)
                nodes.add(node2)

                #Initialize distance vector table dictionary
                if node1 not in self.DV:
                    self.DV[node1] = {}
                if node2 not in self.DV:
                    self.DV[node2] = {}

                #Update the distance vector dictionary with the cost from the file
                self.DV[node1][node2] = cost
                self.DV[node2][node1] = cost

                #Store original link costs
                self.original_link_costs[(node1, node2)] = cost
                self.original_link_costs[(node2, node1)] = cost

                #Initialize node instances and add edges
                if node1 not in self.dv_tables:
                    self.dv_tables[node1] = Node(node1, self)
                if node2 not in self.dv_tables:
                    self.dv_tables[node2] = Node(node2, self)

                self.dv_tables[node1].add_edge(node2, cost)
                self.dv_tables[node2].add_edge(node1, cost)

            #Initialize distance vector tables in each node
            for node in nodes:
                self.dv_tables[node].init_dv({n: INFINITY for n in nodes})
                self.dv_tables[node].dv_table[node] = 0
                #Initialize distance vector table with direct neighbors' costs
                for neighbor in self.DV[node]:
                    self.dv_tables[node].dv_table[neighbor] = self.DV[node][neighbor]
        
        self.log_text.insert(tk.END, "Initial DV and DV tables set up.\n")

    #Initialize function to display distance vector tables
    def display_dv_tables(self):
        #Clear existing widgets in the DV table frame
        for widget in self.dv_table_frame.winfo_children():
            widget.destroy()

        #Create a grid to display DV tables
        row = 0
        for id, node in self.dv_tables.items():
            #Ensure `node` is an instance of `Node` class
            if isinstance(node, Node):
                #Create a row for each node
                node_label = tk.Label(self.dv_table_frame, text=f"Node {node.id}")
                node_label.grid(row=row, column=0, padx=10, pady=5)

                #Display destinations and costs in the columns
                col = 1
                for destination, cost in node.dv_table.items():
                    destination_label = tk.Label(self.dv_table_frame, text=f"To {destination}: {cost}")
                    destination_label.grid(row=row, column=col, padx=10)
                    col += 1
            
                row += 1
        
        #Log the successful display to the GUI
        self.log_text.insert(tk.END, "DV tables displayed in the GUI.\n")

    #Initialize the function for a simulation of a single step execution of the distance vector algorithm
    def run_single_step(self):
        stable = True
        for id, node in self.dv_tables.items():
            for neighbor_id in node.edges:
                neighbor = self.dv_tables[neighbor_id]
                if neighbor is None:
                    continue
                
                for destination, cost in neighbor.dv_table.items():
                    new_cost = node.edges[neighbor_id] + cost
                    if destination not in node.dv_table or new_cost < node.dv_table[destination]:
                        node.dv_table[destination] = new_cost
                        stable = False

        self.log_text.insert(tk.END, "Ran one step of the algorithm.\n")

        #Check if the status is stable, if it is stable then display the distance vector tables
        if stable:
            self.log_text.insert(tk.END, "DV is in a stable state.\n")
            self.display_dv_tables()  
            return
        
        #Update and display the distance vector tables after running one step
        self.display_dv_tables()

    #Initialize the function for a simulation of a full execution of the distance vector algorithm
    def run_full_algorithm(self):
        #Initalize the time function to measure the time
        start_time = time.time()

        #Initalize a loop to run the algorithm repeatedly until the status is stable or no more link cost change can be made
        while True:
            stable = True
            for id, node in self.dv_tables.items():
                for neighbor_id in node.edges:
                    neighbor = self.dv_tables[neighbor_id]
                    if neighbor is None:
                        continue
                    
                    for destination, cost in neighbor.dv_table.items():
                        new_cost = node.edges[neighbor_id] + cost
                        if destination not in node.dv_table or new_cost < node.dv_table[destination]:
                            node.dv_table[destination] = new_cost
                            stable = False
            #If the status is stable, break
            if stable:
                break
        
        #Calculate the time it took for the algorithm to be fully executed
        end_time = time.time()
        self.log_text.insert(tk.END, f"Algorithm executed in {end_time - start_time:.2f} seconds.\n")
        self.log_text.insert(tk.END, "DV is in a stable state.\n")

        #Update and display the DV tables after running the full algorithm
        self.display_dv_tables()

    #Initialize the function to apply link cost changes and simulate a line failure when the cost is set to 16
    def apply_link_cost(self):
        entry_text = self.change_cost_entry.get()
        try:
            #Parse the input
            node1, node2, new_cost = entry_text.split()
            node1, node2, new_cost = int(node1), int(node2), int(new_cost) 

            #If the new cost is set to 16 (as infinity is set to 16 in this project)
            if new_cost == INFINITY:
                #Log the simulation of a line failure and display the new values to the GUI
                self.log_text.insert(tk.END, f"Simulated line failure: {node1}-{node2} set to {new_cost}\n")
                self.display_dv_tables()

            #If the nodes exist, update the link cost
            elif node1 in self.dv_tables and node2 in self.dv_tables:
                node1_instance = self.dv_tables[node1]
                node2_instance = self.dv_tables[node2]

                #Update the link cost in node instances
                if node2 in node1_instance.edges:
                    node1_instance.update_link_cost(node2, new_cost)
                if node1 in node2_instance.edges:
                    node2_instance.update_link_cost(node1, new_cost)
                

                self.log_text.insert(tk.END, f"Link cost updated: {node1}-{node2} to {new_cost}\n")
                self.display_dv_tables()
            else:
                #Display the error in a separate message box if the link specified is invalid
                messagebox.showerror("Error", "Invalid link specified. The nodes or link may not exist in the DV.")
        except ValueError:
            #Display the error in a separate message box if the input format is invalid
            messagebox.showerror("Error", "Invalid input format. Please enter in the format: node1 node2 cost.")

    #Initialize a function to run distance vector algorithm on a single node to reflect links changes and notify the node to send its distance vector table to neighbors
    def run_dv_algorithm_for_node(self, id):
        node = self.dv_tables[id]
        node.send_dv_to_neighbors()

    #Initialize a function to update link cost in the specified nodes
    def update_DV_link_cost(self, node1, node2, new_cost):
        self.DV[node1][node2] = new_cost
        self.DV[node2][node1] = new_cost

#Main function of the script
if __name__ == "__main__":
    #Create the main GUI and initialize the GUI class
    root = tk.Tk()
    app = GUI(root)
    #Start the main loop to run the GUI
    root.mainloop()