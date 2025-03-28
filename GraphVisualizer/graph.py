from collections import deque


class Graph:
    def __init__(self, directed=False):
        self.adjacency_list = {}
        self.nodes = set()
        self.directed = directed

    def add_node(self, node_id):
        if node_id not in self.adjacency_list:
            self.nodes.add(node_id)
            self.adjacency_list[node_id] = []

    def add_edge(self, start_node, end_node):
        if start_node not in self.adjacency_list or end_node not in self.adjacency_list:
            return
        if end_node not in self.adjacency_list[start_node]:
            self.adjacency_list[start_node].append(end_node)
        if not self.directed and start_node not in self.adjacency_list[end_node]:
            self.adjacency_list[end_node].append(start_node)

    def bfs(self, start_node):
        visited = set()
        queue = deque([start_node])
        traversal_order = []
        while queue:
            current = queue.popleft()
            if current not in visited:
                visited.add(current)
                traversal_order.append(current)
                for neighbor in self.adjacency_list.get(current, []):
                    if neighbor not in visited:
                        queue.append(neighbor)
        return traversal_order

    def dfs(self, start_node):
        visited = set()
        stack = [start_node]
        traversal_order = []
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                traversal_order.append(current)
                for neighbor in reversed(self.adjacency_list.get(current, [])):  # Reverse for consistent order
                    if neighbor not in visited:
                        stack.append(neighbor)
        return traversal_order

    def recursive_dfs(self, node, visited=None, traversal_order=None):
        if visited is None:
            visited = set()
        if traversal_order is None:
            traversal_order = []
        if node not in self.adjacency_list:
            return traversal_order
        visited.add(node)
        traversal_order.append(node)
        for neighbor in self.adjacency_list.get(node, []):
            if neighbor not in visited:
                self.recursive_dfs(neighbor, visited, traversal_order)
        return traversal_order

    def delete_node(self, node_id):
        """Delete a node and all edges connected to it (including incoming edges)."""
        if node_id not in self.adjacency_list:
            return  # Node doesn't exist, nothing to delete
        for neighbors in self.adjacency_list.values():
            if node_id in neighbors:
                neighbors.remove(node_id)
        del self.adjacency_list[node_id]
        self.nodes.remove(node_id)

    def delete_edge(self, start_node, end_node):
        """Delete an edge between two nodes."""
        if start_node not in self.adjacency_list or end_node not in self.adjacency_list:
            return  # One or both nodes do not exist in the graph
        if self.directed:
            if end_node in self.adjacency_list[start_node]:
                self.adjacency_list[start_node].remove(end_node)
        else:
            if end_node in self.adjacency_list[start_node]:
                self.adjacency_list[start_node].remove(end_node)
            if start_node in self.adjacency_list[end_node]:
                self.adjacency_list[end_node].remove(start_node)

    def dfs_helper(self, node, visited, component):
        """Perform DFS to explore all nodes in the connected component."""
        visited.add(node)
        component.append(node)
        # Iterate over the neighbors of the current node using the get() method
        for neighbor in self.adjacency_list.get(node, []):  # Using get to handle missing nodes gracefully
            if neighbor not in visited:
                # Recursively call dfs_helper for unvisited neighbors
                self.dfs_helper(neighbor, visited, component)

    def find_connected_components(self):
        visited = set()  # Keep track of visited nodes
        components = []  # List to store all connected components
        # Explore each node in the graph
        for node in self.adjacency_list:
            if node not in visited:
                # Start a new component
                component = []
                # Perform DFS to find all nodes in this component
                self.dfs_helper(node, visited, component)
                # Add the component to the list of components
                components.append(component)
                print(f"Found component: {component}")
        return components

    def dfs_scc(self, start_node, visited, stack):
        """Helper DFS function to fill the stack with nodes in finishing order"""
        visited.add(start_node)
        for neighbor in self.adjacency_list.get(start_node, []):
            if neighbor not in visited:
                self.dfs_scc(neighbor, visited, stack)
        stack.append(start_node)

    def transpose(self):
        """Create the transposed (reversed) graph"""
        transposed = Graph(directed=self.directed)
        for node in self.adjacency_list:
            transposed.add_node(node)
        for node, neighbors in self.adjacency_list.items():
            for neighbor in neighbors:
                transposed.add_edge(neighbor, node)  # Reverse the edge direction
        return transposed

    def dfs_util(self, node, visited, component, transposed_graph):
        """Perform DFS on the transposed graph and collect the SCC"""
        visited.add(node)
        component.append(node)
        for neighbor in transposed_graph.adjacency_list.get(node, []):
            if neighbor not in visited:
                self.dfs_util(neighbor, visited, component, transposed_graph)

    def kosaraju(self):
        # Step 1: Perform DFS and store the nodes in the stack based on finishing times
        visited = set()
        stack = deque()  # Stack to store the nodes in the order of finishing times
        for node in self.adjacency_list:
            if node not in visited:
                self.dfs_scc(node, visited, stack)

        # Step 2: Transpose the graph (reverse all edges)
        transposed_graph = self.transpose()

        # Step 3: Perform DFS on the transposed graph in the order of the stack
        visited.clear()  # Reset visited for the second DFS
        strong_components = []  # List to store all SCCs
        while stack:
            node = stack.pop()
            if node not in visited:
                component = []
                self.dfs_util(node, visited, component, transposed_graph)
                strong_components.append(component)

        print(f"All strongly connected components: {strong_components}")
        return strong_components

    def topological_sort(self):
        visited = set()
        stack = []
        for node in self.adjacency_list:
            if node not in visited:
                self.dfs_scc(node,visited,stack)
        return stack[::-1]

    def dfs_cycle_util(self, start_node, visited, recursion_stack, parent=None):
        visited.add(start_node)
        recursion_stack.add(start_node)  # Add to recursion stack

        # Explore neighbors
        for neighbor in self.adjacency_list.get(start_node, []):
            # Skip the edge back to the parent node
            if neighbor == parent:
                continue
            if neighbor not in visited:  # If neighbor hasn't been visited, continue DFS
                if self.dfs_cycle_util(neighbor, visited, recursion_stack, parent=start_node):
                    return True
            elif neighbor in recursion_stack:  # If neighbor is in recursion stack, a cycle is detected
                return True

        recursion_stack.remove(start_node)  # Remove from recursion stack after DFS completes for this node
        return False

    def is_cycle(self):
        """Detect if the graph contains a cycle using modified DFS."""
        visited = set()
        for node in self.adjacency_list:
            if node not in visited:  # If the node hasn't been visited yet
                recursion_stack = set()
                if self.dfs_cycle_util(node, visited, recursion_stack, parent=None):  # Start DFS from that node
                    return True  # Cycle found
        return False  # No cycle detected

    # HELP
    def is_tree(self):
        if not self.adjacency_list:
            return False
        print(f"Adjacency List: {self.adjacency_list}")
        edge_count = sum(len(neighbors) for neighbors in self.adjacency_list.values()) // 2 # For undirected graph, divide by 2
        print(f"Edge Count: {edge_count}")
        expected_edge_count = len(self.adjacency_list) - 1
        print(f"Expected Edge Count: {expected_edge_count}")
        if edge_count != expected_edge_count or self.is_cycle():
            return False
        else:
            return True

    def find_tree_center(self):
        if not self.adjacency_list:
            return []

        degrees = {node: len(neighbours) for node, neighbours in self.adjacency_list.items()}
        leaves = deque([node for node, degree in degrees.items() if degree == 1])
        print(f"Initial leaves: {list(leaves)}")
        remaining_nodes = len(self.adjacency_list)
        processed = set()  # Track processed nodes to avoid re-processing
        while remaining_nodes > 2:
            num_leaves = len(leaves)
            remaining_nodes -= num_leaves
            print(f"Processing {num_leaves} leaves: {list(leaves)}")
            for _ in range(num_leaves):
                leaf = leaves.popleft()
                processed.add(leaf)
                for neighbour in self.adjacency_list[leaf]:
                    if neighbour not in processed:
                        degrees[neighbour] -= 1
                        if degrees[neighbour] == 1:
                            leaves.append(neighbour)
            print(f"Remaining nodes: {remaining_nodes}, Current leaves: {list(leaves)}")
        return list(leaves)
