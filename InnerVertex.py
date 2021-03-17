import Auxiliar as aux


class InnerVertex:
    def __init__(self, node, boolean_operator, top_cords, bottom_cords):
        self.id = node
        self.value = None  # value top_bottom
        self.value_bottom_up = None
        self.boolean_value = None
        self.operator = boolean_operator
        self.fill_parameter = 0
        self.in_edges = {}
        self.boolean_in_edges = {}
        self.out_edges = []  # poate scot lista asta???
        self.max_fill_parameter = 2  # o sa folosesc asta pt operatorul not
        self.level = None
        self.top_edge_cords = top_cords
        self.botton_edge_cords = bottom_cords

    def change_operator(self, new_operator):
        self.operator = new_operator

    def get_top_cords(self):
        return self.top_edge_cords

    def get_bottom_cords(self):
        return self.botton_edge_cords

    def compute_value(self, s):
        in_edges_values_list = list(self.in_edges.values())
        # print(in_edges_values_list[0])
        if self.operator == 'and':
            if in_edges_values_list[0] == aux.bottom or in_edges_values_list[1] == aux.bottom:
                self.value_bottom_up = aux.bottom
            else:
                in_edges_values_list[0] = int(in_edges_values_list[0] / s)
                in_edges_values_list[1] = int(in_edges_values_list[1] / s)
                self.value_bottom_up = ((in_edges_values_list[0] + in_edges_values_list[1]) * s) % aux.root_prime_number
        else:
            if in_edges_values_list[0] == aux.bottom:
                self.value_bottom_up = in_edges_values_list[1]
            if in_edges_values_list[1] == aux.bottom:
                self.value_bottom_up = in_edges_values_list[0]
            if in_edges_values_list[0] != aux.bottom and in_edges_values_list[1] != aux.bottom:
                self.value_bottom_up = in_edges_values_list[0]

    def compute_boolean_value(self):
        in_edges_values_list = list(self.boolean_in_edges.values())
        if self.operator == 'and':
            self.boolean_value = in_edges_values_list[0] and in_edges_values_list[1]
        else:
            self.boolean_value = in_edges_values_list[0] or in_edges_values_list[1]

    def add_in_edge(self, node_id):  # both boolean and prime
        if len(self.in_edges.keys()) < 2:
            self.in_edges[node_id] = None
            self.boolean_in_edges[node_id] = None
            return True
        return False

    def add_out_edge(self, node_id):
        self.out_edges.append(node_id)

    def update_in_edges_dict(self, old_in, new_in):
        self.in_edges[new_in] = self.in_edges.pop(old_in)

    def get_nr_of_in_connections(self):
        return 2 - len(self.in_edges.keys())

    def get_value(self):
        return self.value

    def get_id(self):
        return self.id

    def get_level(self):
        return self.level

    def get_in_connections(self):
        return self.in_edges.keys()

    def get_out_connections(self):
        return self.out_edges

    def get_out_edges(self):
        return self.out_edges

    def node_is_level1(self):
        if self.level == 1:
            return True
        return False

    def set_level(self, level):
        self.level = level

    def set_value(self, value):
        self.value = value

    def delete_in_edge(self, node):
        if node in self.in_edges.keys():
            self.in_edges.pop(node)
            return True
        return False

    def set_id(self, new_id):
        self.id = new_id

    def delete_out_edge(self, node_id):

        self.out_edges.remove(node_id)
        return True

    def add_value_to_one_in_edge(self, in_node, value):
        if in_node in self.in_edges.keys():
            self.in_edges[in_node] = value
            self.fill_parameter += 1
            return True
        return False

    def add_value_to_one_boolean_in_edge(self, in_node, value):
        if in_node in self.in_edges.keys():
            self.boolean_in_edges[in_node] = value
            # self.fill_parameter+=1
            return True
        return False

    def add_value_to_all_in_edges(self, value):
        for key in self.in_edges.keys():
            self.in_edges[key] = value
