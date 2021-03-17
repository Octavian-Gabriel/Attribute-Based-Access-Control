class LeafVertex():
    def __init__(self, node, edge_cord):
        self.id = node
        self.value = None
        self.bool_value = None
        self.out_edges = []
        self.level = 0
        self.top_cords = edge_cord  # list of 2 x,y pair [x,y]

    def set_name(self, new_id):
        self.id = new_id

    def set_value(self, value):
        self.value = value

    def set_b_value(self, value):
        self.bool_value = value

    def get_top_cords(self):
        return self.top_cords

    def get_value(self):
        return self.value

    def get_b_value(self):
        return self.bool_value

    def get_id(self):
        return self.id

    def get_out_edges(self):
        return self.out_edges

    def add_out_edge(self, node_id):
        self.out_edges.append(node_id)
        return True

    def delete_out_edge(self, node):
        if node in self.out_edges:
            self.out_edges.remove(node)
            return True
        return False
