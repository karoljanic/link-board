from ogdf_python import ogdf, cppinclude
from graph import Graph

cppinclude("ogdf/basic/simple_graph_alg.h")
cppinclude("ogdf/basic/extended_graph_alg.h")
cppinclude("ogdf/planarity/PlanarSubgraphCactus.h")
cppinclude("ogdf/planarity/PlanarizationLayout.h")
cppinclude("ogdf/orthogonal/OrthoLayout.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")


class Planarity:    
    def is_planar(graph: Graph) -> bool:
        ogdf_graph, _ = Graph.to_ogdf_graph(graph)
        return ogdf.isPlanar(ogdf_graph)
    
    def max_planar_subgraph_of_connected_graph(graph: Graph) -> tuple[Graph, Graph]:
        ogdf_graph, mapping = Graph.to_ogdf_graph(graph)
        reversed_mapping = {node: vertex for vertex, node in mapping.items()}

        psc = ogdf.PlanarSubgraphCactus['float']()
        costs = ogdf.EdgeArray['float'](ogdf_graph)
        for edge in ogdf_graph.edges:
            costs[edge] = edge.source().degree() * edge.target().degree()    

        del_edges = ogdf.List[ogdf.edge]()
        preferred_edges = ogdf.List[ogdf.edge]()

        psc.call(ogdf_graph, costs, preferred_edges, del_edges, False)

        graph_copy = Graph.copy(graph)
        remaining_graph = Graph()
        for edge in del_edges:
            ogdf_graph.delEdge(edge)
            graph_copy.remove_edge(reversed_mapping[edge.source()], reversed_mapping[edge.target()])
            remaining_graph.add_edge(reversed_mapping[edge.source()], reversed_mapping[edge.target()])

        max_edges = 3 * graph_copy.get_edges_number() - 6
        sorted_del_edges = [(edge.source(), edge.target()) for edge in 
                            sorted(del_edges, key=lambda e: costs[e], reverse=True)]
        
        for edge in sorted_del_edges:
            ne = ogdf_graph.newEdge(edge[0], edge[1])
            if not ogdf.isPlanar(ogdf_graph):
                ogdf_graph.delEdge(ne)
            else:
                graph_copy.add_edge(reversed_mapping[edge[0]], reversed_mapping[edge[1]])
                remaining_graph.remove_edge(reversed_mapping[edge[0]], reversed_mapping[edge[1]])

                if graph_copy.get_edges_number() > max_edges:
                    break

        return graph_copy, remaining_graph
    
    def max_planar_subgraph(graph: Graph) -> tuple[Graph, Graph]:
        connected_components = Graph.connected_components(graph)
        max_planar_subgraph = Graph()
        remaining_graph = Graph()
        for component in connected_components:
            max_planar_subgraph_component, remaining_graph_component = Planarity.max_planar_subgraph_of_connected_graph(component)
            max_planar_subgraph = Graph.merge_graphs([max_planar_subgraph, max_planar_subgraph_component])
            remaining_graph = Graph.merge_graphs([remaining_graph, remaining_graph_component])

        return max_planar_subgraph, remaining_graph

    def max_planar_subgraphs(graph) -> list[Graph]:
        subgraphs = []
        graph_copy = Graph.copy(graph)
        while graph_copy.get_edges_number() > 0:
            max_planar_subgraph, remaining_graph = Planarity.max_planar_subgraph(graph_copy)
            subgraphs.append(max_planar_subgraph)
            graph_copy = remaining_graph

        return sorted(subgraphs, key=lambda x: x.get_edges_number(), reverse=True)
    
    def graph_thickness(graph: Graph) -> int:
        return len(Planarity.max_planar_subgraphs(graph))
    
    def find_layout_of_planar_graph(graph: Graph, node_dimensions: dict, separation: float, drawing_filename: str) -> dict:
        ogdf_graph, mapping = Graph.to_ogdf_graph(graph)
        reversed_mapping = {node: vertex for vertex, node in mapping.items()}

        graph_attributes = ogdf.GraphAttributes(ogdf_graph, ogdf.GraphAttributes.all)
        
        for node in ogdf_graph.nodes:
            graph_attributes.width[node] = node_dimensions[reversed_mapping[node]]['width']
            graph_attributes.height[node] = node_dimensions[reversed_mapping[node]]['height']
            graph_attributes.strokeColor[node] = ogdf.Color.Name.Gold
            graph_attributes.fillColor[node] = ogdf.Color.Name.Gold
            graph_attributes.strokeWidth[node] = 0.2

        for edge in ogdf_graph.edges:
            graph_attributes.strokeColor[edge] = ogdf.Color.Name.Orange
            graph_attributes.strokeWidth[edge] = 0.1
            graph_attributes.arrowType[edge] = getattr(ogdf.EdgeArrow, "None")
        
        layouter = ogdf.OrthoLayout()
        layouter.separation(separation)
        layouter.cOverhang(0.4)
        layouter.__python_owns__ = False

        planarization = ogdf.PlanarizationLayout()
        planarization.setPlanarLayouter(layouter)

        # planarization = ogdf.SugiyamaLayout()

        planarization.call(graph_attributes)

        ogdf.GraphIO.write(graph_attributes, drawing_filename)

        embedding = {}
        for node in ogdf_graph.nodes:
            embedding[reversed_mapping[node]] = {'x': graph_attributes.x[node], 'y': graph_attributes.y[node]}

        return embedding