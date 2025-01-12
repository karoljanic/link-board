import pcbnew

from graph import Graph


class PcbBoard:
    def __init__(self, name: str):
        self._name = name

    def load_from_file(self, filename: str):
        self._board = pcbnew.LoadBoard(filename)
        self._extract_components_pads_nets_connections()
        self._convert_to_graphs()

    def save_to_file(self, filename: str):
        self._board.Save(filename)

    def get_name(self):
        return self._name
    
    def get_components(self):
        return self._components
    
    def get_pads(self):
        return self._pads
    
    def get_aggregated_pads(self):
        return self._aggregated_pads

    def get_nets(self):
        return self._nets
    
    def get_connections(self):
        return self._connections
    
    def get_components_graph(self) -> Graph:
        return self._components_graph
    
    def get_pads_graph(self) -> Graph:
        return self._pads_graph
    
    def get_edge_net_components_lookup(self):
        return self._edge_net_components_lookup
        
    def get_edge_net_pads_lookup(self):
        return self._edge_net_pads_lookup
    
    def get_component_dimensions(self):
        return {component: self._get_component_dimensions(component, 1.0) for component in self._components}
    
    def update_component_positions(self, component_positions: dict):
        for footprint in self._board.Footprints():
            footprint_name = self._get_footprint_name(footprint)
            if footprint_name in component_positions:
                pos = component_positions[footprint_name]
                point = pcbnew.VECTOR2I(int(pos['x'] * 10**6), int(pos['y'] * 10**6))
                footprint.SetPosition(point)

    def _extract_components_pads_nets_connections(self):
        self._components = []
        self._pads = []
        self._aggregated_pads = {}
        self._nets = []
        self._connections = {}

        for footprint in self._board.Footprints():
            footprint_name = self._get_footprint_name(footprint)
            self._components.append(footprint_name)

            for pad in footprint.Pads():
                pad_name = self._get_pad_name(pad)
                pad_pos = pad.GetPosition()
                self._pads.append((pad_name, (pad_pos.x, pad_pos.y)))
                if footprint_name not in self._aggregated_pads:
                    self._aggregated_pads[footprint_name] = []
                self._aggregated_pads[footprint_name].append(pad_name)

            self._nets = [net.GetNetname() for net in self._board.GetNetsByName().values()]

        for net in self._nets:
            self._connections[net] = []

            for footprint in self._board.Footprints():
                for pad in footprint.Pads():
                    if pad.GetNet().GetNetname() == net:
                        self._connections[net].append(self._get_pad_name(pad))

            if len(self._connections[net]) == 0:
                del self._connections[net]

    def _convert_to_graphs(self):
        self._components_graph = Graph()
        self._pads_graph = Graph()

        # Create nodes in the general and detailed graphs for each pad
        for footprint in self._board.Footprints():
            footprint_name = self._get_footprint_name(footprint)
            self._components_graph.add_vertex(footprint_name)

            for pad in footprint.Pads():
                pad_name = self._get_pad_name(pad)
                self._pads_graph.add_vertex(pad_name)

        # Create edges in the general graph between connected components
        for conn in self._connections.values():
            for index in range(1, len(conn)):
                src = conn[index - 1]
                dst = conn[index]

                src_comp = self._extract_component_name(src)
                dst_comp = self._extract_component_name(dst)

                if src_comp == dst_comp:
                    continue
                
                if not self._components_graph.edge_exists(src_comp, dst_comp):
                    self._components_graph.add_edge(src_comp, dst_comp, [(src, dst)])
                else:
                    self._components_graph.update_edge(src_comp, dst_comp, lambda properties: properties + [(src, dst)])

                if not self._pads_graph.edge_exists(src, dst):
                    self._pads_graph.add_edge(src, dst, 1)
                else:
                    self._pads_graph.update_edge(src, dst, lambda x: x + 1)

    def _get_footprint_name(self, footprint: pcbnew.FOOTPRINT) -> str:
        return footprint.GetReference()

    def _get_pad_name(self, pad: pcbnew.PAD) -> str:
        return pad.GetParentAsString() + "@" + pad.GetPadName()
    
    def _extract_component_name(self, pad_name: str) -> str:
        return pad_name.split("@")[0]
    
    def _get_component_dimensions(self, component: str, padding: float):
        component_pads = [pad for pad in self._pads if pad[0].startswith(f"{component}@")]
        pad_x_positions = [pad[1][0] for pad in component_pads]
        pad_y_positions = [pad[1][1] for pad in component_pads]

        min_x = min(pad_x_positions) if len(pad_x_positions) > 0 else 0
        max_x = max(pad_x_positions) if len(pad_x_positions) > 0 else 0
        min_y = min(pad_y_positions) if len(pad_y_positions) > 0 else 0
        max_y = max(pad_y_positions) if len(pad_y_positions) > 0 else 0

        return {
            'width': (max_x - min_x) / 10**6  + 2 * padding,
            'height': (max_y - min_y) / 10**6  + 2 * padding
        }