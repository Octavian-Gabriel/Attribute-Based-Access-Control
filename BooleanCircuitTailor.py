'''
This is a class that does the cleaning and fan out solving. More exact:
0. check inner nodes and root are valid
1. runs leafs garbage cleaner
2.runs inner nodes garbage cleaner
3. runs leafs fan out solving
4.runs level 1 inner nodes fan out solving
5.completes the level parameter
6.runs the level >1 < root inner nodes fan out solving
'''
import Auxiliar as aux


class BooleanCircuitTailor():
    def __init__(self, bc):
        self.bcc_obj = bc

    def found_blocker_inner_nodes(self):  # found nodes with in_edge complete but out_edge empty
        blocker_inner_nodes_list = []
        for innner_node in self.bcc_obj.list_of_inner_nodes_objs:
            if len(innner_node.get_out_edges()) == 0 and innner_node.fill_parameter >= 0:
                blocker_inner_nodes_list.append(innner_node)
        return blocker_inner_nodes_list

    def run_garbage_cleaner(self):
        # clean garbage out of inner nodes list

        garbage_list = self.found_blocker_inner_nodes()
        all_garbage_nodes = []
        while len(garbage_list) > 0:
            for garbage in garbage_list:
                all_garbage_nodes.append(garbage.id)
                # cut connections from node below to node above(above is blocker)
                conns_to_cut = garbage.in_edges.keys()
                for con in conns_to_cut:
                    if self.bcc_obj.node_is_inode(con):
                        self.bcc_obj.delete_out_edge_for_inner_node(garbage.id, con)
                    else:
                        l_obj = self.bcc_obj.get_leaf_by_id(con)
                        self.bcc_obj.delete_leaf_out_edge(l_obj, garbage.id)
                # remove node from inner nodes list
                self.bcc_obj.list_of_inner_nodes_objs.remove(garbage)
                print("removed node " + str(garbage.id))
            garbage_list = self.found_blocker_inner_nodes()

        return all_garbage_nodes

    def run_null_leafs_cleaner(self):
        # remove leafs with no out con
        leafs = []
        all_leafs_list = self.bcc_obj.list_of_leafs_objs.copy()
        # create a copy of the object list because after removing an element the for doesn't iterate again. don't know why...
        for leaf in all_leafs_list:
            if len(leaf.get_out_edges()) == 0:
                leafs.append(leaf.id)
                self.bcc_obj.list_of_leafs_objs.remove(leaf)
        return leafs

    def inner_nodes_are_valid(self):  # function that checks that there are no nodes with the following conditions:
        # binar operator and one in edge

        for node in self.bcc_obj.list_of_inner_nodes_objs:
            if node.max_fill_parameter == 2:  # need 2 in connections
                if len(node.in_edges.keys()) == 1:  # problem node
                    return False
                else:
                    pass
        return True

    def root_is_valid(self):  # check root has enough in connections based on operator
        if len(self.bcc_obj.root.get_in_connections()) == 2:
            return True
        else:
            return False

    def find_fan_out_leafs(self):
        problem_leaf = []
        for leaf in self.bcc_obj.list_of_leafs_objs:
            if len(leaf.out_edges) > 1:
                problem_leaf.append(leaf)
        return problem_leaf

    def find_fan_out_innner_nodes(self):
        # method that return inner_nodes with problem fan out
        # method is executed after level 1 fan out nodes clean up
        problem_nodes = []
        for inner_node in self.bcc_obj.list_of_inner_nodes_objs:
            if len(inner_node.out_edges) > 1 and inner_node not in problem_nodes:
                problem_nodes.append(inner_node)
        return problem_nodes

    def find_level1_fan_out_inner_nodes(self):  # find nodes just above leafs that have fan-out>1  -> more out edges
        fanout_2_inner_nodes_above_leafs = []
        for inode in self.bcc_obj.list_of_inner_nodes_objs:
            if len(inode.out_edges) > 1:
                in_cons = list(inode.get_in_connections())
                if self.bcc_obj.node_is_leaf(in_cons[0]) == True and self.bcc_obj.node_is_leaf(in_cons[1]) == True:
                    fanout_2_inner_nodes_above_leafs.append(inode)
                    inode.set_level(1)

        return fanout_2_inner_nodes_above_leafs

    def solve_level1_fan_out_binar_nodes(self):  # only for case with leafs with 1 fan out edge
        # and 2 fan out node just above leafs

        fan_out_nodes = self.find_level1_fan_out_inner_nodes()  # list with objects
        for fan2_node in fan_out_nodes:
            in_edge = list(fan2_node.get_in_connections())
            first_leaf_to_get_value_from = self.bcc_obj.get_leaf_by_id(in_edge[0])
            second_leaf_to_get_value_from = self.bcc_obj.get_leaf_by_id(in_edge[1])
            out_edges = fan2_node.get_out_edges().copy()
            out_edges.pop(0)  # removing first element from out edges as it is ok
            # case when fan-out can be anything larger >2
            # go trough list of out edges
            for out_edge in out_edges:
                # sanitize : example from ('i1') to i1 
                # node_to_reconnect_id=aux.sanitize_id(out_edge)
                if fan2_node.delete_out_edge(out_edge):
                    print("deleted one fan out connection from inner node ", fan2_node.id)
                first_new_leaf_id = aux.create_leaf_id()
                second_new_leaf_id = aux.create_leaf_id()
                self.bcc_obj.add_leaf(first_new_leaf_id, [0, 0])
                self.bcc_obj.add_leaf(second_new_leaf_id, [0, 0])
                new_node_id = aux.create_inner_node_id()
                self.bcc_obj.add_inner_node(fan2_node.operator, new_node_id, [0, 0], [0, 0])
                self.bcc_obj.add_in_edge_for_inner_node(new_node_id, first_new_leaf_id)
                self.bcc_obj.add_in_edge_for_inner_node(new_node_id, second_new_leaf_id)
                self.bcc_obj.delete_in_edge_for_inner_node(out_edge, fan2_node.id)
                self.bcc_obj.add_in_edge_for_inner_node(out_edge, new_node_id)
        print("Leafs after l1 binar nodes fan out solving: ", self.bcc_obj.get_leafs_ids())
        print(" L1 binar Inner nodes after fan out solving", self.bcc_obj.get_inner_nodes_ids())

    def solve_fan_out_leafs(self):
        problem_leafs = self.find_fan_out_leafs()  # list of leaf objects
        for problem_leaf in problem_leafs:
            leaf_out_edges = problem_leaf.get_out_edges().copy()
            leaf_out_edges.pop(0)
            for conn in leaf_out_edges:
                new_leaf_id = aux.create_leaf_id()
                self.bcc_obj.add_leaf(new_leaf_id, [0, 0])
                if self.bcc_obj.node_is_inode(conn):
                    inner_node = self.bcc_obj.get_inner_node_by_id(conn)
                    self.bcc_obj.delete_in_edge_for_inner_node(inner_node.id, problem_leaf.id)
                    self.bcc_obj.add_in_edge_for_inner_node(inner_node.id, new_leaf_id)
                else:
                    self.bcc_obj.delete_in_edge_for_root(problem_leaf.id)
                    self.bcc_obj.add_in_edge_for_root(new_leaf_id)
                self.bcc_obj.delete_leaf_out_edge(problem_leaf, conn)

    def pre_run_checkings(self):
        if not self.inner_nodes_are_valid() or not self.root_is_valid():
            return False
        else:
            return True

    def solve_fan_out_for_leafs_and_l1_nodes(self):
        self.solve_fan_out_leafs()
        self.solve_level1_fan_out_binar_nodes()

    def solve_fan_out_inner_nodes(self):  # fan out for nodes with l>1 and l<root level
        problem_nodes = self.find_fan_out_innner_nodes()
        problem_nodes.sort(key=lambda x: x.level)
        for node in problem_nodes:
            out_edges = node.get_out_edges().copy()
            out_edges.pop(0)
            for out_edge in out_edges:
                # remove connection to node above
                node.delete_out_edge(out_edge)

                if out_edge != self.bcc_obj.root.id:
                    remove_con = self.bcc_obj.delete_in_edge_for_inner_node(out_edge, node.id)
                    self.dfs_cloning(node.id, out_edge, out_edge)
                else:
                    remove_con = self.bcc_obj.root.delete_in_edge(node.id)
                    self.dfs_cloning(node.id, out_edge, out_edge)

    def dfs_cloning(self, start_node_id, node_above_start_id, cloned_node_above_id, visited=None):
        leafs_reached = False
        if visited == None:
            visited = []
        if node_above_start_id != self.bcc_obj.root.id:
            node_above_start_obj = self.bcc_obj.get_inner_node_by_id(node_above_start_id)
            if start_node_id not in visited:
                if node_above_start_obj.node_is_level1() == False:  # start node is not leaf
                    # pot avea cazul cand nodul sa fie conecat cu o frunza care este cu x nivele mai jos
                    if self.bcc_obj.node_is_leaf(start_node_id):
                        new_node_id = aux.create_leaf_id()
                        self.bcc_obj.add_leaf(new_node_id, [0, 0])
                        self.bcc_obj.add_in_edge_for_inner_node(cloned_node_above_id, new_node_id)
                        leafs_reached = True
                    else:
                        new_node_id = aux.create_inner_node_id()
                        start_node_obj = self.bcc_obj.get_inner_node_by_id(start_node_id)
                        self.bcc_obj.add_inner_node(start_node_obj.operator, new_node_id, [0, 0], [0, 0])
                        self.bcc_obj.add_in_edge_for_inner_node(cloned_node_above_id, new_node_id)
                        self.bcc_obj.set_inner_node_level(new_node_id, start_node_obj.get_level())
                else:  # start node id is leaf
                    new_node_id = aux.create_leaf_id()
                    self.bcc_obj.add_leaf(new_node_id, [0, 0])
                    self.bcc_obj.add_in_edge_for_inner_node(cloned_node_above_id, new_node_id)
                    leafs_reached = True
                visited.append(start_node_id)
                if leafs_reached == False:
                    if start_node_obj:
                        for child in start_node_obj.get_in_connections():
                            self.dfs_cloning(child, start_node_id, new_node_id, visited)
            else:
                pass
        else:
            new_node_id = aux.create_inner_node_id()
            start_node_obj = start_node_obj = self.bcc_obj.get_inner_node_by_id(start_node_id)
            self.bcc_obj.add_inner_node(start_node_obj.operator, new_node_id, [0, 0], [0, 0])
            self.bcc_obj.add_in_edge_for_root(new_node_id)
            self.bcc_obj.set_inner_node_level(new_node_id, start_node_obj.get_level())
            visited.append(start_node_id)
            for child in start_node_obj.get_in_connections():
                self.dfs_cloning(child, start_node_id, new_node_id, visited)

    def find_inner_nodes_without_level(self):
        nodes_without_level = []
        for node in self.bcc_obj.list_of_inner_nodes_objs:
            if node.get_level() == None:
                nodes_without_level.append(node)
        return nodes_without_level

    def set_inner_nodes_levels(self):
        nodes_without_level = self.find_inner_nodes_without_level()  # list of objects

        while len(nodes_without_level) > 0:
            for node in nodes_without_level:
                in_cons = list(node.get_in_connections())
                if self.bcc_obj.node_is_leaf(in_cons[0]) and self.bcc_obj.node_is_leaf(in_cons[1]):  # 2 leafs
                    node.set_level(1)
                    nodes_without_level.remove(node)
                elif self.bcc_obj.node_is_leaf(in_cons[0]) or self.bcc_obj.node_is_leaf(
                        in_cons[1]):  # at least one leaf. dont know which node is leaf
                    level_1 = level_2 = 0
                    if self.bcc_obj.node_is_leaf(in_cons[0]):
                        level_2 = self.bcc_obj.get_inner_node_level(in_cons[1])
                    if self.bcc_obj.node_is_leaf(in_cons[1]):
                        level_1 = self.bcc_obj.get_inner_node_level(in_cons[0])
                    # one of l1 or l2 might be None, need to check
                    if level_1 != None and level_2 != None:
                        node.set_level(max(level_1, level_2) + 1)
                        nodes_without_level.remove(node)
                    else:  # node rght below doesnt have a level
                        pass
                else:  # no leaf right below
                    level_1 = self.bcc_obj.get_inner_node_level(in_cons[0])
                    level_2 = self.bcc_obj.get_inner_node_level(in_cons[1])
                    if level_1 != None and level_2 != None:
                        node.set_level(max(level_1, level_2) + 1)
                        nodes_without_level.remove(node)

            nodes_without_level = self.find_inner_nodes_without_level()

    def set_root_level(self):
        root_in_cons = list(self.bcc_obj.root.get_in_connections())
        if self.bcc_obj.node_is_inode(root_in_cons[0]) and self.bcc_obj.node_is_inode(root_in_cons[1]):
            level1 = self.bcc_obj.get_inner_node_level(root_in_cons[0])
            level2 = self.bcc_obj.get_inner_node_level(root_in_cons[1])
            self.bcc_obj.root.set_level(max(level1, level2) + 1)
        elif self.bcc_obj.node_is_leaf(root_in_cons[0]) and self.bcc_obj.node_is_leaf(root_in_cons[1]):
            self.bcc_obj.root.set_level(1)
        else:
            if self.bcc_obj.node_is_inode(root_in_cons[0]) == False:
                level = self.bcc_obj.get_inner_node_level(root_in_cons[1])
                self.bcc_obj.root.set_level(level + 1)
            else:
                level = self.bcc_obj.get_inner_node_level(root_in_cons[0])
                self.bcc_obj.root.set_level(level + 1)

    def boolean_circuit_tailoring(self):
        if not self.pre_run_checkings():
            print(
                "Error!!!  Some of the inner nodes don't have enough input edges!!!  Or root doesn't have enough edges. Aborting execution ")
        else:
            self.run_garbage_cleaner()
            self.solve_fan_out_for_leafs_and_l1_nodes()
            self.set_inner_nodes_levels()
            self.set_root_level()
            self.solve_fan_out_inner_nodes()
            self.bcc_obj.create_level_dictionary()
            print("Boolean circuit is valid.Running")
