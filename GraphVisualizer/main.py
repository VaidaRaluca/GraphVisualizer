import tkinter as tk
from tkinter import ttk
from gui import GraphGUI
from graph import Graph

if __name__ == '__main__':
    graph = Graph(directed=False)
    gui = GraphGUI(graph)
    gui.run()
