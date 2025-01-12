from ogdf_python import ogdf


class Graph:
    def __init__(self) -> None:
        self._graph = {}

    def __str__(self) -> str:
        return str(self._graph)

    def add_vertex(self, vertex: str) -> None:
        if vertex not in self._graph:
            self._graph[vertex] = {}

    def remove_vertex(self, vertex: str) -> None:
        if vertex in self._graph:
            del self._graph[vertex]
            
        for _, edges in self._graph.items():
            if vertex in edges:
                del edges[vertex]

    def add_edge(self, vertex1: str, vertex2: str, properties: dict={}) -> None:
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)

        self._graph[vertex1][vertex2] = properties
        self._graph[vertex2][vertex1] = properties
            

    def remove_edge(self, vertex1: str, vertex2: str) -> None:
        if vertex1 in self._graph and vertex2 in self._graph[vertex1]:
            del self._graph[vertex1][vertex2]
        
        if vertex2 in self._graph and vertex1 in self._graph[vertex2]:
            del self._graph[vertex2][vertex1]

    def edge_exists(self, vertex1: str, vertex2: str) -> bool:
        return vertex1 in self._graph and vertex2 in self._graph[vertex1]

    def update_edge(self, vertex1: str, vertex2: str, update):
        if vertex1 in self._graph and vertex2 in self._graph[vertex1]:
            new_properties = update(self._graph[vertex1][vertex2])
            self._graph[vertex1][vertex2] = new_properties

        if vertex2 in self._graph and vertex1 in self._graph[vertex2]:
            new_properties = update(self._graph[vertex2][vertex1])
            self._graph[vertex2][vertex1] = new_properties
    
    def get_vertices(self):
        return list(self._graph.keys())
    
    def get_vertices_number(self):
        return len(self._graph)

    def get_edges(self):
        edges = []
        for vertex, neighbours in self._graph.items():
            for neighbour in neighbours:
                if vertex <= neighbour:
                    edges.append((vertex, neighbour))
        return edges
    
    def get_edges_number(self):
        return len(self.get_edges())
    
    def get_neighbours(self, vertex):
        if vertex in self._graph:
            return list(self._graph[vertex].keys())
        else:
            return []
    
    def get_edge_properties(self, vertex1, vertex2):
        if vertex1 in self._graph and vertex2 in self._graph[vertex1]:
            return self._graph[vertex1][vertex2]
        return None
        
    def get_degree(self, vertex):
        return len(self.get_neighbours(vertex))
    
    def get_degrees(self):
        return [self.get_degree(vertex) for vertex in self.get_vertices()]

    @staticmethod
    def connected_components(graph) -> list:
        visited = set()
        vertex_components = {}
        components_count = 0
        
        def dfs(vertex: str):
            visited.add(vertex)
            vertex_components[vertex] = components_count
            for neighbour in graph.get_neighbours(vertex):
                if neighbour not in visited:
                    dfs(neighbour)

        for vertex in graph.get_vertices():
            if vertex not in visited:
                components_count += 1
                dfs(vertex)
                
        connected_components = [Graph() for _ in range(components_count)]
        for edge in graph.get_edges():
            vertex1, vertex2 = edge
            connected_components[vertex_components[vertex1] - 1].add_edge(vertex1, vertex2, graph.get_edge_properties(vertex1, vertex2))
        
        
        return connected_components
    
    @staticmethod
    def merge_graphs(graphs: list):
        merged_graph = Graph()
        for graph in graphs:
            for edge in graph.get_edges():
                vertex1, vertex2 = edge
                properties = graph.get_edge_properties(vertex1, vertex2)
                merged_graph.add_edge(vertex1, vertex2, properties)

        return merged_graph
    
    @staticmethod
    def copy(graph):
        copied_graph = Graph()
        for edge in graph.get_edges():
            vertex1, vertex2 = edge
            properties = graph.get_edge_properties(vertex1, vertex2)
            copied_graph.add_edge(vertex1, vertex2, properties)

        return copied_graph
    
    @staticmethod
    def to_ogdf_graph(graph):
        cpp_graph = ogdf.Graph()
        vertices_mapping = {vertex: cpp_graph.newNode() for vertex in graph.get_vertices()}

        for edge in graph.get_edges():
            vertex1, vertex2 = edge
            if not cpp_graph.searchEdge(vertices_mapping[vertex1], vertices_mapping[vertex2]):
                cpp_graph.newEdge(vertices_mapping[vertex1], vertices_mapping[vertex2])

        return cpp_graph, vertices_mapping
    
    @staticmethod
    def from_ogdf_graph(cpp_graph, vertices_mapping):
        reversed_vertices_mapping = {node: vertex for vertex, node in vertices_mapping.items()}
        graph = Graph()

        for edge in cpp_graph.edges:
            vertex1 = reversed_vertices_mapping[edge.source()]
            vertex2 = reversed_vertices_mapping[edge.target()]
            graph.add_edge(vertex1, vertex2)

        return graph