import Auxiliar as aux
import json as js


class BooleanCircuitRunner:
    def __init__(self, name, bc_controller_obj, user_att):
        self.name = name
        self.bcc_obj = bc_controller_obj
        self.user_attributes = user_att

    def leafs_send_data(self, leafs_list_obj):  # list of leafs as objects
        for leaf_obj in leafs_list_obj:  # leaf is the object
            destinations_ids = leaf_obj.get_out_edges()  # list of ids
            for destination_id in destinations_ids:  # destination=id
                # need to get the object with the id
                # first check it's not the root
                if self.bcc_obj.node_is_inode(destination_id):
                    # print(leaf_obj.id,destination_id)
                    # for sure it's a inner node
                    # obtaining the inner node object
                    destination_obj = self.bcc_obj.get_inner_node_by_id(destination_id)
                    destination_obj.add_value_to_one_in_edge(leaf_obj.id, leaf_obj.value)
                    destination_obj.add_value_to_one_boolean_in_edge(leaf_obj.id, leaf_obj.bool_value)
                    # print(destination_obj.fill_parameter)
                else:  # it's the root
                    destination_obj = self.bcc_obj.root
                    destination_obj.add_value_to_one_in_edge(leaf_obj.id, leaf_obj.value)
                    destination_obj.add_value_to_one_boolean_in_edge(leaf_obj.id, leaf_obj.bool_value)
        return True

    def found_full_inner_nodes(self, inner_nodes_obj_list):
        # after leafs send data at least one node needs to be full
        full_nodes_list = []
        for inner_node_obj in inner_nodes_obj_list:
            if inner_node_obj.fill_parameter == inner_node_obj.max_fill_parameter:
                full_nodes_list.append(inner_node_obj)
        return full_nodes_list

    def run_boolean_circuit_bottom_up(self, s):  # main function
        flag = self.assign_values_to_leafs_after_top_bootom_run(self.user_attributes)
        if flag == 0:
            return False
        else:
            run_leafs = self.leafs_send_data(self.bcc_obj.list_of_leafs_objs)
            if run_leafs:
                print("Leafs send data with succes")

                levels = list(self.bcc_obj.dict_level.keys())
                levels.sort()
                levels.pop(0)
                levels.pop(len(levels) - 1)
                for level in levels:
                    nodes = list(self.bcc_obj.dict_level[level])
                    for inner_node in nodes:
                        inner_node.compute_value(s)
                        inner_node.compute_boolean_value()
                        destination_id = inner_node.get_out_edges()
                        destination_id = destination_id[0]
                        if self.bcc_obj.node_is_inode(destination_id):
                            # destination_id=aux.sanitize_id(destination_id)
                            destination_obj = self.bcc_obj.get_inner_node_by_id(destination_id)
                            if destination_obj:
                                destination_obj.add_value_to_one_in_edge(inner_node.id,
                                                                                  inner_node.value_bottom_up)
                                destination_obj.add_value_to_one_boolean_in_edge(inner_node.id,
                                                                                          inner_node.boolean_value)
                            else:
                                print("Problem at obtaining object in runner function", destination_id)
                        else:  # it's the root
                            destination_obj = self.bcc_obj.root
                            destination_obj.add_value_to_one_in_edge(inner_node.id, inner_node.value_bottom_up)
                            destination_obj.add_value_to_one_boolean_in_edge(inner_node.id,
                                                                                      inner_node.boolean_value)

            root_result = self.bcc_obj.root.compute_value(s)
            self.bcc_obj.root.compute_boolean_value()
            if root_result:
                print("Value top-bottom ", self.bcc_obj.root.value)
                print("Value bootom-up: ", self.bcc_obj.root.value_bottom_up)
                print("Boolean value from the root", self.bcc_obj.root.boolean_value)
                return self.bcc_obj.root.boolean_value
            elif not root_result:
                print("Root edges aren't fulfilled. Cannot compute value!")

    def run_boolean_circuit_top_bottom(self):  # send info from the root way down to the leafs


        self.bcc_obj.root_send_info_below()
        levels = list(self.bcc_obj.dict_level.keys())
        levels.sort(reverse=True)
        levels.pop(0)
        levels.pop(len(levels) - 1)
        for level in levels:
            self.bcc_obj.inner_nodes_send_info_below(self.bcc_obj.dict_level[level])
        # parcurg nivel cu nivel de sub radacina pana deasupra frunzelor, deci de la nivel radacina -1 pana la nivelul 1
        # for level in range (self.bcc_obj.root.level - 1, 0, -1):
        #     pass

    def multiply_leafs_with_s(self, s):
        for leaf in self.bcc_obj.list_of_leafs_objs:
            leaf.set_value(int(leaf.value * s) % self.bcc_obj.root.prime_number)

    def full_run_boolean_circuit(self, p,y,s):
        self.bcc_obj.root.set_prime_value(p)
        self.bcc_obj.root.set_value(y)
        self.run_boolean_circuit_top_bottom()
        self.multiply_leafs_with_s(s)
        bool_value = self.run_boolean_circuit_bottom_up(s)
        return bool_value

    def assign_values_to_leafs_after_top_bootom_run(self, user_leafs):  # user_leafs= list of ids
        # method that goes through all leafs from the bc and for each one:
        # if is in user_leafs list : bool_value=1
        # else bool_value=0
        if user_leafs!='-1':
            for leaf_idx in user_leafs:
                try:
                    leaf_obj = self.bcc_obj.list_of_leafs_objs[leaf_idx - 1]
                except Exception as e:
                    print("leaf index is out of range-> access denied")
                    print(e)
                    return 0
                leaf_obj.set_b_value(1)

            for leaf in self.bcc_obj.list_of_leafs_objs:
                if leaf.bool_value is None:
                    leaf.set_b_value(0)
                    leaf.set_value(aux.bottom)
            return 1
        else: #calculate y*s
            for leaf in self.bcc_obj.list_of_leafs_objs:
                if leaf.bool_value is None:
                    leaf.set_b_value(1)
            return 1
    def save_bc_to_json(self, structure_name):
        sorted_d = a = dict(sorted(self.bcc_obj.dict_level.items(), key=lambda x: x[0]))
        final_d = {}
        leafs = list(sorted_d['0'])
        final_d['0'] = []
        for leaf in leafs:
            leaf_dict = {'name': leaf.id, 'out': leaf.out_edges}
            final_d['0'].append(leaf_dict)
        sorted_d.pop('0')
        for level in range(1, len(sorted_d.keys())):
            inodes_objs = list(sorted_d[str(level)])
            final_d[str(level)] = []

            for iobj in inodes_objs:
                i_dict = {'name': iobj.id, 'operator': iobj.operator, 'in': list(iobj.get_in_connections()),
                          'out': iobj.out_edges}
                final_d[str(level)].append(i_dict)
        final_d[self.bcc_obj.root.level] = [{'name': self.bcc_obj.root.id, 'operator': self.bcc_obj.root.operator,
                                             'in': list(self.bcc_obj.root.get_in_connections())}]
        json_object = js.dumps(final_d)
        with open(structure_name + ".json", "w") as outfile:
            outfile.write(json_object)
            outfile.close()


def run_circuit(bc):
    bcr = BooleanCircuitRunner("boolean_circuit_runner", bc, ["dummy"])
    bcr.full_run_boolean_circuit(8)  # length in bits of the prime number
