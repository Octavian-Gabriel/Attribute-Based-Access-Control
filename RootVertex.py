import Auxiliar as aux


class RootVertex():
    def __init__(self, node, boolean_operator, bottom_cords):
        self.id = node
        self.value = None
        self.value_bottom_up = None
        self.boolean_value = None
        self.operator = boolean_operator
        self.in_edges = {}
        self.boolean_in_edges = {}
        self.level = None
        self.prime_number = None
        self.bottom_cords = bottom_cords

    def set_id(self, nid):
        self.id = nid

    def get_bottom_cords(self):
        return self.bottom_cords

    def get_value(self):
        return self.value

    def get_nr_of_in_connections(self):
        return 2 - len(self.in_edges.keys())

    def get_in_connections(self):
        return self.in_edges.keys()

    def check_operator(self, boolean_operator):
        if boolean_operator not in ['and', 'And,', 'AND', 'or', 'Or', 'OR', 'not', 'Not', 'NOT']:
            return False
        return True

    def change_operator(self, new_operator):
        self.operator = new_operator
        return True

    def check_if_root_is_full(self):
        if len(self.in_edges.values()) == 2:
            return True
        return False

    def compute_value(self, s):
        root_is_full = self.check_if_root_is_full()
        if root_is_full == True:
            in_edges_values_list = list(self.in_edges.values())
            if self.operator in ['and', 'And,', 'AND']:
                if in_edges_values_list[0] == aux.bottom or in_edges_values_list[1] == aux.bottom:
                    self.value_bottom_up = aux.bottom
                else:
                    in_edges_values_list[0] = int(in_edges_values_list[0] / s)
                    in_edges_values_list[1] = int(in_edges_values_list[1] / s)
                    self.value_bottom_up = (in_edges_values_list[0] + in_edges_values_list[1]) * s
                return True
            if self.operator in ['or', 'Or', 'OR']:
                if in_edges_values_list[0] == aux.bottom:
                    self.value_bottom_up = in_edges_values_list[1]
                if in_edges_values_list[1] == aux.bottom:
                    self.value_bottom_up = in_edges_values_list[0]
                if in_edges_values_list[0] != aux.bottom and in_edges_values_list[1] != aux.bottom:
                    self.value_bottom_up = in_edges_values_list[0]
                return True
            if self.operator in ['not', 'Not', 'NOT']:
                self.value_bottom_up = in_edges_values_list[0]
                return True

        else:
            return False

    def compute_boolean_value(self):
        in_edges_values_list = list(self.boolean_in_edges.values())
        if self.operator == 'and':
            self.boolean_value = in_edges_values_list[0] and in_edges_values_list[1]
        else:
            self.boolean_value = in_edges_values_list[0] or in_edges_values_list[1]

    def add_in_edge(self, node):
        if len(self.in_edges.keys()) < 2:
            self.in_edges[node] = None
            self.boolean_in_edges[node] = None
            return True

        return False

    def set_level(self, level):
        self.level = level

    def set_value(self, value):
        self.value = value
        aux.root_prime_number=value

    def set_prime_value(self, value):
        self.prime_number = value
        aux.set_root_prime_number(value)

    def delete_in_edge(self, node):
        if node in self.in_edges.keys():
            self.in_edges.pop(node)
            return True
        return False

    def update_in_edges_dict(self, old_in, new_in):
        self.in_edges[new_in] = self.in_edges.pop(old_in)

    def add_value_to_one_in_edge(self, in_node, value):
        if in_node in self.in_edges.keys():
            self.in_edges[in_node] = value
            return True
        return False

    def add_value_to_one_boolean_in_edge(self, in_node, value):
        if in_node in self.in_edges.keys():
            self.boolean_in_edges[in_node] = value
            return True
        return False

    def add_value_to_all_in_edges(self, value):
        for key in self.in_edges.keys():
            self.in_edges[key] = value
