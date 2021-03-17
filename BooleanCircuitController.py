from LeafVertex import LeafVertex
from InnerVertex import InnerVertex
from RootVertex import RootVertex
import Auxiliar as aux


class BooleanCircuitController:
    def __init__(self, name):
        self.controller_name = name
        self.list_of_leafs_objs = []
        self.list_of_inner_nodes_objs = []
        self.root = None
        self.dict_level = {}

    def add_leaf(self, node, edge_cords):
        leaf = LeafVertex(node, edge_cords)
        if leaf not in self.list_of_leafs_objs:
            self.list_of_leafs_objs.append(leaf)
            return "leaf added succesfully"
        else:
            del leaf
            return "leaf already exists"

    def add_leaf_out_edge(self, leaf_node_obj, inner_node_id):
        leaf_node_obj.add_out_edge(inner_node_id)
        return True

    def set_leaf_value(self, leaf_id, value):
        target_leaf = self.get_leaf_by_id(leaf_id)
        target_leaf.set_value(value)
        return "value for leaf " + str(leaf_id) + " set to " + str(value) + " succesfully"

    def set_leaf_value_top_bottom_case(self, leaf_id, value):
        target_leaf = self.get_leaf_by_id(leaf_id)
        target_leaf.set_value(value)

    def update_leaf_id(self, old_leaf_id, new_leaf_id):
        leaf_obj = self.get_leaf_by_id(old_leaf_id)
        leaf_obj.set_name(new_leaf_id)
        for inode in self.list_of_inner_nodes_objs:
            if old_leaf_id in inode.get_in_connections():
                inode.update_in_edges_dict(old_leaf_id, new_leaf_id)
        if self.root is not None:
            if old_leaf_id in self.root.get_in_connections():
                self.root.update_in_edges_dict(old_leaf_id, new_leaf_id)
        return True

    def get_leafs_ids(self):
        list_of_id = []
        for leaf in self.list_of_leafs_objs:
            list_of_id.append(leaf.get_id())
        return list_of_id

    def get_leaf_by_id(self, my_id):
        for leaf in self.list_of_leafs_objs:
            if leaf.id == my_id:
                return leaf

    def get_leafs_values(self):
        leafs_values = []
        for leaf in self.list_of_leafs_objs:
            leafs_values.append(leaf.get_value())
        return leafs_values

    def get_leaf_out_edges(self, leaf_id):
        leaf = self.get_leaf_by_id(leaf_id)
        return leaf.out_edges

    def remove_leaf(self, leaf_id):
        leaf_obj = self.get_leaf_by_id(leaf_id)
        for out_con in leaf_obj.out_edges:
            if self.node_is_inode(out_con):
                ret = self.delete_in_edge_for_inner_node(out_con, leaf_id)
                if not ret:
                    print("LEAF:Problem at removing edge in controller")
            else:
                self.delete_in_edge_for_root(leaf_id)
        if leaf_obj:
            self.list_of_leafs_objs.remove(leaf_obj)
            return "leaf " + str(leaf_obj.id) + " removed succesfully"
        return "leaf " + str(leaf_obj.id) + " doesn't exists"

    def delete_leaf_out_edge (self, leaf_obj, con_to_remove):
        return leaf_obj.delete_out_edge(con_to_remove)

    def add_inner_node(self, bool_operator, node, top_cords, bottom_cords):
        inner_node = InnerVertex(node, bool_operator, top_cords, bottom_cords)
        if inner_node not in self.list_of_inner_nodes_objs:
            self.list_of_inner_nodes_objs.append(inner_node)
            return "node added succesfully"
        else:
            return "Node " + str(inner_node.id) + " already exists"

    def add_in_edge_for_inner_node(self, *nodes_ids):

        target_node = self.get_inner_node_by_id(nodes_ids[0])
        # check how many connections does the node has
        nr_of_free_connections = target_node.get_nr_of_in_connections()
        # if node has 0 free connections then return False
        if nr_of_free_connections == 0:
            return "target node " + nodes_ids[0] + " already has 2 connections. exiting"

        if nr_of_free_connections >= 1:
            # check if i already have connection with the same node
            existing_connections = target_node.get_in_connections()
            if nodes_ids[1] in existing_connections:
                return "Connection of " + str(nodes_ids[1] + " to " + str(nodes_ids[0] + " already exists"))
            else:  # all good
                # add in connection to receiver node
                target_node.add_in_edge(nodes_ids[1])
                # add out connection to giver node:
                # check if giver node is a leaf
                if self.get_leaf_by_id(nodes_ids[1]):
                    leaf_node = self.get_leaf_by_id(nodes_ids[1])
                    self.add_leaf_out_edge(leaf_node, nodes_ids[0])
                else:
                    inner_node = self.get_inner_node_by_id(nodes_ids[1])
                    self.add_out_edge_for_inner_node(inner_node, nodes_ids[0])
                return "connection from " + str(nodes_ids[1]) + " to " + str(nodes_ids[0]) + " added succesfully"

    def add_out_edge_for_inner_node(self, target_node, to_node_id):
        # called from add_in_edges.. functions, no need to check params
        idx = self.list_of_inner_nodes_objs.index(target_node)
        return self.list_of_inner_nodes_objs[idx].add_out_edge(to_node_id)

    def get_inner_nodes_ids(self):
        list_of_id = []
        for inner_node in self.list_of_inner_nodes_objs:
            list_of_id.append(inner_node.id)
        return list_of_id

    def get_inner_node_by_id(self, my_id):
        for node in self.list_of_inner_nodes_objs:
            if my_id == node.id:
                return node

    def remove_inner_node(self, node_id):
        inner_node_obj = self.get_inner_node_by_id(node_id)
        # remove out edges for nodes with which this node has in conections:
        in_cons = self.get_inner_node_in_connections(node_id)
        for in_con in in_cons:
            if self.node_is_inode(in_con):
                ret = self.delete_out_edge_for_inner_node(in_con, node_id)
                if not ret:
                    print("INODE:Problem at removing edge in controller")
            else:
                leaf_obj = self.get_leaf_by_id(in_con)
                ret = self.delete_leaf_out_edge(leaf_obj, node_id)
                if not ret:
                    print("INODE:Problem at removing edge in controller")
        del in_cons
        # remove in edges for nodes with which this node has out cons:
        out_cons = self.get_inner_node_out_connections(node_id)
        for out_con in out_cons:
            if self.node_is_inode(out_con):
                ret = self.delete_in_edge_for_inner_node(out_con, node_id)
                if not ret:
                    print("INODE:Problem at removing edge in controller")
            else:
                ret = self.delete_in_edge_for_root(node_id)
                if not ret:
                    print("INODE:Problem at removing edge in controller")
        if inner_node_obj in self.list_of_inner_nodes_objs:
            self.list_of_inner_nodes_objs.remove(inner_node_obj)
            return "node " + str(inner_node_obj.id) + " removed succesfully"
        return "node " + str(inner_node_obj.id) + " you want to remove doesnt exists"

    def get_inner_node_out_connections(self, node_id):
        node_obj = self.get_inner_node_by_id(node_id)
        return list(node_obj.get_out_connections())

    def set_inner_node_level(self, node_id, level):
        node_obj = self.get_inner_node_by_id(node_id)
        node_obj.set_level(level)

    def set_inner_node_value(self, node_id, value):
        node_obj = self.get_inner_node_by_id(node_id)
        node_obj.set_value(value)

    def get_inner_node_in_connections(self, node_id):
        node_obj = self.get_inner_node_by_id(node_id)
        return list(node_obj.get_in_connections())

    def delete_in_edge_for_inner_node(self, node_id, node_id_to_delete):
        inner_node = self.get_inner_node_by_id(node_id)
        succes = inner_node.delete_in_edge(node_id_to_delete)
        return succes

    def delete_out_edge_for_inner_node(self, node_id, node_id_to_delete):
        inner_node = self.get_inner_node_by_id(node_id)
        return inner_node.delete_out_edge(node_id_to_delete)

    def get_inner_node_level(self, node_id):
        node_obj = self.get_inner_node_by_id(node_id)
        return node_obj.get_level()

    def update_inode_id(self, oid, nid):
        inode_obj = self.get_inner_node_by_id(oid)
        inode_obj.set_id(nid)
        for leaf in self.list_of_leafs_objs:
            if oid in leaf.out_edges:
                leaf.delete_out_edge(oid)
                leaf.add_out_edge(nid)
        for inod in self.list_of_inner_nodes_objs:
            if oid in inod.out_edges:
                inod.update_in_edges_dict(oid, nid)
            if oid in inod.get_in_connections():
                inod.delete_in_edge(oid)
                inod.add_in_edge(nid)
        if self.root is not None:
            if oid in self.root.get_in_connections():
                self.root.update_in_edges_dict(oid, nid)

    def change_inner_node_operator(self, node_id, op):
        n_obj = self.get_inner_node_by_id(node_id)
        n_obj.change_operator(op)

    def set_root(self, node, bool_operator, bott_cords):
        r = RootVertex(node, bool_operator, bott_cords)
        self.root = r
        return "Root set with succes"

    def add_in_edge_for_root(self, node_id):
        # first check if root support one more connection:
        nr_of_free_connections = self.root.get_nr_of_in_connections()
        if nr_of_free_connections > 0:  # ok, root supports connections. dont know how many
            # check if i already connection with node_id, if so exit
            existing_connections = self.root.get_in_connections()
            if node_id in existing_connections:
                return "Root in connection to " + str(node_id) + " already exists"
            else:  # continuing with execution
                # check if inner node exists
                inner_node = self.get_inner_node_by_id(node_id)
                if not inner_node:  # it's not a inner node
                    # it's a leaf
                    leaf = self.get_leaf_by_id(node_id)
                    # add in connection to receiver node
                    self.root.add_in_edge(node_id)
                    # add out connection to giver node:
                    self.add_leaf_out_edge(leaf, self.root.id)
                    return "connection from leaf node " + str(node_id) + " to root  added succesfully"

                else:  # it' a inner node inner node
                    self.root.add_in_edge(node_id)
                    self.add_out_edge_for_inner_node(inner_node, self.root.id)
                    return "connection from inner node " + str(node_id) + " to root  added succesfully"
        else:
            return "Root connections full"

    def change_root_operator(self, new_operator):
        if self.root.change_operator(new_operator) is True:
            return " new operator for root changed with succes"

    def get_root(self):
        return self.root

    def get_root_operator(self):
        return self.root.operator

    def get_root_in_edges(self):
        return list(self.root.get_in_connections())

    def remove_root(self):
        in_cons = self.get_root_in_edges()
        for in_con in in_cons:
            if self.node_is_inode(in_con):
                ret = self.delete_out_edge_for_inner_node(in_con, self.root.id)
                if not ret:
                    print("ROOT:Problem at removing edge in controller")
            else:
                leaf_obj = self.get_leaf_by_id(in_con)
                ret = self.delete_leaf_out_edge(leaf_obj, self.root.id)
                if not ret:
                    print("ROOT:Problem at removing edge in controller")
        del self.root
        self.root = None

    def root_send_info_below(self):
        in_cons = list(self.root.get_in_connections())

        if self.root.operator == 'or':
            for in_con in in_cons:
                self.inner_node_send_info_below(in_con, self.root.value)
        else:
            x1 = aux.get_random_in_range(0, self.root.prime_number - 1)
            x2 = abs(self.root.value - x1)
            self.inner_node_send_info_below(in_cons[0], x1)
            self.inner_node_send_info_below(in_cons[1], x2)

    def delete_in_edge_for_root(self, in_edge_to_remove):
        return self.root.delete_in_edge(in_edge_to_remove)

    def inner_nodes_send_info_below(self, sender_objs):
        for sender_obj in sender_objs:
            sender_in_cons = list(sender_obj.get_in_connections())
            if sender_obj.operator == 'or':
                for in_con in sender_in_cons:
                    self.inner_node_send_info_below(in_con, sender_obj.value)
            elif sender_obj.operator == 'and':
                x1 = aux.get_random_in_range(0, self.root.prime_number - 1)
                x2 = abs(sender_obj.value - x1)  # modulo p
                self.inner_node_send_info_below(sender_in_cons[0], x1)
                self.inner_node_send_info_below(sender_in_cons[1], x2)

    def inner_node_send_info_below(self, recv_node_id, value):  # function used by inner_nodes
        if self.node_is_leaf(recv_node_id):
            self.set_leaf_value_top_bottom_case(recv_node_id, value)
        else:
            self.set_inner_node_value(recv_node_id, value)

    def update_root_id(self, oid, nid):
        self.root.set_id(nid)
        for leaf in self.list_of_leafs_objs:
            if oid in leaf.out_edges:
                leaf.delete_out_edge(oid)
                leaf.add_out_edge(nid)
        for inod in self.list_of_inner_nodes_objs:
            if oid in inod.out_edges:
                inod.delete_out_edge(oid)
                inod.add_out_edge(nid)
            if oid in inod.get_in_connections():
                inod.update_in_edges_dict(oid, nid)

    def node_exists(self, node_id):
        list_of_leafs_objs_ids = self.get_leafs_ids()
        list_of_inner_nodes_objs_ids = self.get_inner_nodes_ids()
        if node_id in list_of_leafs_objs_ids or node_id in list_of_inner_nodes_objs_ids:
            return True
        return False

    def node_is_leaf(self, node_id):
        if not self.get_leaf_by_id(node_id):
            return False
        else:
            return True

    def node_is_inode(self, node_id):
        if not self.get_inner_node_by_id(node_id):
            return False
        else:
            return True

    def create_level_dictionary(self):  # create a dictionary with key=level, values= object nodes on that level
        # add root to dictionary

        # add leafs to dictionary
        self.dict_level['0'] = self.list_of_leafs_objs
        # add inner nodes now:
        for node in self.list_of_inner_nodes_objs:
            if str(node.level) not in self.dict_level.keys():
                self.dict_level[str(node.level)] = []
                self.dict_level[str(node.level)].append(node)
            else:
                self.dict_level[str(node.level)].append(node)
        self.dict_level[str(self.root.level)] = self.root

    def get_top_cords_for_inodes_and_leafs(self, node_id, node_type):
        if node_type == 'leaf':
            n_obj = self.get_leaf_by_id(node_id)
            if n_obj:
                return n_obj.get_top_cords()
            else:
                return False
        elif node_type == 'inode':
            n_obj = self.get_inner_node_by_id(node_id)
            if n_obj:
                return n_obj.get_top_cords()
            else:
                return False
        return False

    def get_bottom_cords_for_inodes_and_root(self, node_id, node_type):
        if node_type == "inode":
            n_obj = self.get_inner_node_by_id(node_id)
            return n_obj.get_bottom_cords()
        else:
            return self.root.get_bottom_cords()


def build_bc_from_json(file):
    f = open(file, "r")
    bc = aux.load(f)
    bcc = BooleanCircuitController("bcc")
    # leafs first
    for leaf in bc["0"]:
        bcc.add_leaf(leaf['name'], [0, 0])
        # # print(leaf['out'][0])
        # self.add_leaf_out_edge(leaf['name'],leaf['out'][0])
    nr_of_keys = len(bc.keys())
    # then inner nodes
    for index in range(1, nr_of_keys - 1):

        for node in bc[str(index)]:
            bcc.add_inner_node(node['operator'], node['name'], [0, 0], [0, 0])
            bcc.set_inner_node_level(node['name'], index)
            bcc.add_in_edge_for_inner_node(node['name'], node['in'][0])
            bcc.add_in_edge_for_inner_node(node['name'], node['in'][1])

    # and finally the root
    root_level = nr_of_keys - 1
    # print(bc[str(root_level)][0]['in'][1])
    bcc.set_root(bc[str(root_level)][0]['name'], bc[str(root_level)][0]['operator'], [0, 0])
    bcc.root.set_level(root_level)
    bcc.add_in_edge_for_root(bc[str(root_level)][0]['in'][0])
    bcc.add_in_edge_for_root(bc[str(root_level)][0]['in'][1])

    # create level dictionary
    bcc.create_level_dictionary()
    # print(self.dict_level)
    return bcc
