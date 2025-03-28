# Graph Visualizer

This **Graph Visualizer** is a Python application that allows users to create, visualize, and interact with graphs. It supports both directed and undirected graphs and includes several graph algorithms for visualization, such as **BFS**, **DFS**, **Connected Components**, **Strongly Connected Components**, **Topological Sort**, and more. The underlying graph structure is implemented using a custom `Graph` class, which provides various methods for graph manipulation, traversal, and analysis.

### Graph Class Overview

The **Graph** class provides a comprehensive set of methods to manage graph data and perform various algorithms. Here are some of the key features:

#### Graph Structure
- **Nodes**: Nodes are stored in a set, ensuring each node is unique.
- **Adjacency List**: An adjacency list is used to store the graph’s edges. It is a dictionary where each key represents a node, and its corresponding value is a list of nodes it is connected to.

#### Core Methods

1. **add_node(node_id)**:
   - Adds a node to the graph if it doesn’t already exist.

2. **add_edge(start_node, end_node)**:
   - Adds an edge between two nodes. For undirected graphs, the edge is added in both directions.
   
3. **delete_node(node_id)**:
   - Removes a node and all edges connected to it from the graph.

4. **delete_edge(start_node, end_node)**:
   - Removes an edge between two nodes.

#### Graph Algorithms

1. **Breadth-First Search (BFS)**:
   - `bfs(start_node)` performs a BFS starting from the given node. The algorithm explores all nodes at the present depth level before moving on to nodes at the next depth level.

2. **Depth-First Search (DFS)**:
   - `dfs(start_node)` explores as far down a branch as possible before backtracking. This method uses an explicit stack to manage the nodes to be explored.
   
3. **Recursive DFS**:
   - `recursive_dfs(node)` is a recursive version of DFS. It explores all nodes starting from the given node using recursion.

4. **Connected Components**:
   - `find_connected_components()` identifies and returns all connected components in the graph using DFS. Each connected component is a subgraph where every node is reachable from every other node within the same component.

5. **Strongly Connected Components (SCC)**:
   - `kosaraju()` finds all strongly connected components (SCCs) in a directed graph using **Kosaraju's Algorithm**. It involves two main steps: 
     1. Perform DFS to store nodes based on finishing times.
     2. Transpose the graph (reverse all edges), and perform DFS on the transposed graph.
   - SCCs are subgraphs where every node is reachable from every other node within the subgraph, specifically for directed graphs.

6. **Topological Sort**:
   - `topological_sort()` orders the nodes of a Directed Acyclic Graph (DAG) in such a way that for every directed edge `u -> v`, node `u` comes before node `v`. It uses a DFS-based approach to achieve this.

7. **Cycle Detection**:
   - `is_cycle()` detects whether the graph contains a cycle using modified DFS. It tracks recursion stacks during the DFS traversal to detect back edges, which indicate a cycle.

8. **Tree Check**:
   - `is_tree()` checks whether the graph is a tree. A tree is a connected graph without cycles, and it must have exactly `n - 1` edges for `n` nodes.

9. **Find Tree Center**:
   - `find_tree_center()` identifies the center of a tree. The center is the node(s) that are closest to all other nodes in terms of graph distance. The method works by iteratively removing leaf nodes (nodes with only one connection) until only 1 or 2 nodes remain, which are the center of the tree.
     
     ---
