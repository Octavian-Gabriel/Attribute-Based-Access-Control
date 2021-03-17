from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from BooleanCircuitController import BooleanCircuitController
from BooleanCircuitRunner import BooleanCircuitRunner
from BooleanCircuitTailor import BooleanCircuitTailor
import json
import os


class CreateBooleanCircuitGUI():
    def __init__(self):
        self.bcc = BooleanCircuitController("boolean_circuit")
        self.bcr = BooleanCircuitRunner("bcr", self.bcc, ['dummy'])
        self.bct = BooleanCircuitTailor(self.bcc)
        self.root = None
        # given_root.wait_window()
        self.graph_frame = None
        self.canvas = None
        self.actions_frame = None
        self.vertex_combo_menu = None
        self.elements_combo_menu_for_adding = None
        self.elements_combo_menu_for_editing = None
        self.elements_combo_menu_for_removing = None
        # dictonary  of leafs: key=leaf name from the user as string value=circle object and text object and for inodes and root :operator text object
        self.leafs_dict = {}
        self.inodes_dict = {}
        self.root_dict = {}
        # list with nodes and texts that were added but the mouse wasnt activated
        self.elements_added_but_not_drawn_list = []
        # list containing node type in [0-leaf,1-inode,2-root], node name,operator if has any and event from bind at button-1
        self.curr_obj_created = [-1] * 4
        self.list_of_all_nodes_names = []
        # key=line object from canvas value=[start node,end node]
        self.edges_dict = {}
        # list in which i put elements i want to delete so i don't pass them as param in functions
        self.temporary_elements = []
        self.run_circuit_button = None
        self.circuit_name_entry = None
        self.return_value = None
        self.gui_power_up()
        self.root.mainloop()

    def root_power_up(self):
        self.root = Tk()
        self.root.title("Acces control")
        self.root.geometry('1200x650+70+20')  # + is position on screen
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        # self.root.resizable(0,0)

    def actions_frame_power_up(self):
        self.actions_frame = LabelFrame(
            self.root, text="   Actions   ", padx=5, pady=5)
        self.actions_frame.grid(row=0, column=0, sticky=W + E, padx=10, pady=10)
        name_label = Label(self.actions_frame, text="Name of the circuit: ")
        name_label.grid(row=0, column=0, padx=10, pady=5)
        self.circuit_name_entry = Entry(self.actions_frame)
        self.circuit_name_entry.grid(row=0, column=1)
        self.display_actions()

    def graph_frame_power_up(self):
        self.graph_frame = LabelFrame(self.root, text="Graph image", padx=5)
        self.graph_frame.grid(
            row=1, column=0, columnspan=3, padx=10, sticky=E + W + N + S)
        self.graph_frame.rowconfigure(0, weight=1)
        self.graph_frame.columnconfigure(0, weight=1)
        self.canvas_power_up()

    def canvas_power_up(self):
        self.canvas = Canvas(self.graph_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky=E + W + N + S)
        self.canvas.bind("<Configure>", self.canvas_size_monitor)

    def canvas_size_monitor(self, event):
        # print(event)
        # print(self.canvas.winfo_height())
        pass

    def display_vertex_combo_menu(self, row, column):
        self.vertex_combo_menu = ttk.Combobox(self.actions_frame, values=[
            'Leaf', 'Inner Node', 'Root'], state='readonly', width=17)
        self.vertex_combo_menu.grid(row=row, column=column, padx=3, pady=3)
        self.vertex_combo_menu.set("Choose vertex type")

    def display_elements_combo_menu(self, row, column, mode):
        if mode == 'add':
            self.elements_combo_menu_for_adding = ttk.Combobox(
                self.actions_frame, values=['Vertex', 'Edge'], state='readonly', width=15)
            self.elements_combo_menu_for_adding.grid(
                row=row, column=column, padx=3, pady=3)
            self.elements_combo_menu_for_adding.set("Choose element")
        elif mode == 'remove':
            self.elements_combo_menu_for_removing = ttk.Combobox(
                self.actions_frame, values=['Vertex', 'Edge'], state='readonly', width=15)
            self.elements_combo_menu_for_removing.grid(
                row=row, column=column, padx=3, pady=3)
            self.elements_combo_menu_for_removing.set("Choose element")
        else:
            self.elements_combo_menu_for_editing = ttk.Combobox(
                self.actions_frame, values=['Vertex', 'Edge'], state='readonly', width=15)
            self.elements_combo_menu_for_editing.grid(
                row=row, column=column, padx=3, pady=3)
            self.elements_combo_menu_for_editing.set("Choose element")

    def display_actions(self):
        add_elements_label = Label(self.actions_frame, text="Add ")
        add_elements_label.grid(row=1, column=0)
        self.display_elements_combo_menu(1, 1, 'add')
        self.elements_combo_menu_for_adding.bind(
            "<<ComboboxSelected>>", self.add_elements_controller)

        edit_elements_label = Label(self.actions_frame, text='Edit ')
        edit_elements_label.grid(row=2, column=0)
        self.display_elements_combo_menu(2, 1, 'editing')
        self.elements_combo_menu_for_editing.bind(
            "<<ComboboxSelected>>", self.edit_elements_controller)

        remove_label = Label(self.actions_frame, text="Remove ")
        remove_label.grid(row=3, column=0)
        self.display_elements_combo_menu(3, 1, 'remove')
        self.elements_combo_menu_for_removing.bind(
            "<<ComboboxSelected>>", self.remove_elements_controller)

        self.run_circuit_button = Button(
            self.actions_frame, text="Add circuit", command=self.check_circuit_integrity)
        self.run_circuit_button.grid(row=4, column=0, padx=10)

    def gui_power_up(self):
        self.root_power_up()
        self.actions_frame_power_up()
        self.graph_frame_power_up()

    # def runner(self):
    #     pass

    def run_gui(self):
        self.gui_power_up()
        self.root.mainloop()

    # functions for buttons

    def empty_elements_added_but_not_drawn_list(self):
        for element in self.elements_added_but_not_drawn_list:
            self.canvas.delete(element)
        self.elements_added_but_not_drawn_list = []

    def gather_leaf_info(self):
        self.temporary_elements[0].destroy()
        self.temporary_elements.clear()
        name_label = Label(self.actions_frame, text="Leaf name: ")
        name_label.grid(row=1, column=3)

        name_input = Entry(self.actions_frame, width=10)
        name_input.grid(row=1, column=4)

        go_button = Button(self.actions_frame, text="Add leaf", command=lambda: [
            self.empty_elements_added_but_not_drawn_list(),
            self.check_leaf_info(name_input.get(), 'add', name_input, "dummy_parameter", 'dummy_parameter')])
        go_button.grid(row=1, column=5, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel action",
                               command=lambda: [self.empty_elements_added_but_not_drawn_list(),
                                                self.canvas.unbind('<ButtonRelease-1>'), self.canvas.unbind(
                                       '<Motion>'), self.canvas.unbind('<Button-1>'), cancel_button.destroy(),
                                                go_button.destroy(), name_input.destroy(), name_label.destroy(),
                                                self.vertex_combo_menu.destroy(),
                                                self.display_vertex_combo_menu_when_adding()])
        cancel_button.grid(row=1, column=6, padx=20)

    def check_leaf_info(self, leaf_name, mode, input_box, old_leaf_name, objs_to_delete):
        if leaf_name.replace(" ", "") == '':  # display warning message
            messagebox.showwarning("Warning", "Leaf name is empty.")
        elif leaf_name != '':
            if mode == 'add':
                # draw leaf and add to the bc object
                # need further development
                if leaf_name not in self.leafs_dict.keys() and leaf_name not in self.list_of_all_nodes_names:
                    self.create_leaf_on_gui_side(leaf_name, input_box)
                else:
                    messagebox.showerror(
                        "Error", "Leaf already exists or other node has this name.")

            elif mode == 'remove':
                self.remove_node_on_gui_side(leaf_name, 'leaf')
                self.remove_node_edges_on_gui_side(leaf_name)
                self.remove_node_on_bcc_side(leaf_name, 'leaf')
                for obj in objs_to_delete:
                    obj.destroy()
                self.display_leafs_removal_panel()
            else:
                ret = self.edit_node_on_gui_side(
                    old_leaf_name, leaf_name, "nothing", "nothing", 'leaf', objs_to_delete)
                if ret:
                    self.edit_node_on_bcc_side(
                        old_leaf_name, leaf_name, 'nada', 'leaf')
                    if ret:
                        print("Leaf edited succesfully")

    def move_node_when_adding(self, event, circle, circle_text, circle_operator, node_type):

        if node_type == 'leaf':
            self.canvas.coords(circle, event.x - 40,
                               event.y - 40, event.x, event.y)
            self.canvas.coords(circle_text, event.x + 22, event.y - 32)
        else:
            self.canvas.coords(circle, event.x - 40,
                               event.y - 40, event.x, event.y)
            self.canvas.coords(circle_text, event.x + 22, event.y - 32)
            self.canvas.coords(circle_operator, event.x - 20, event.y - 20)

    def draw_node(self, event, node_text, node_type, input_box):
        input_box.delete(0, 'end')
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Button-1>')
        circle_size = 40
        self.list_of_all_nodes_names.append(node_text)
        if node_type == 'leaf':
            self.leafs_dict[node_text] = [self.canvas.create_oval(
                event.x - circle_size, event.y - circle_size, event.x, event.y, tag=node_text)]
            self.empty_elements_added_but_not_drawn_list()
        elif node_type == 'inode':
            self.inodes_dict[node_text] = [self.canvas.create_oval(
                event.x - circle_size, event.y - circle_size, event.x, event.y, tag=node_text)]
            self.empty_elements_added_but_not_drawn_list()
        elif node_type == 'root':
            self.root_dict[node_text] = [self.canvas.create_oval(
                event.x - circle_size, event.y - circle_size, event.x, event.y, tag=node_text)]
            self.empty_elements_added_but_not_drawn_list()

    def write_text(self, event, text, operator, node_type, text_obj_to_remove):
        self.canvas.delete(text_obj_to_remove)
        size_x = 22
        size_y = 32
        operator_param = 20
        if node_type == 'leaf':
            self.curr_obj_created[2] = 'empty'
            self.leafs_dict[text].append(
                self.canvas.create_text(event.x + size_x, event.y - size_y, text=text))
        elif node_type == 'inode':
            self.inodes_dict[text].append(
                self.canvas.create_text(event.x + size_x, event.y - size_y, text=text))
            self.inodes_dict[text].append(self.canvas.create_text(
                event.x - operator_param, event.y - operator_param, text=operator, font='bold'))
            self.curr_obj_created[2] = operator
        else:  # root
            self.root_dict[text].append(self.canvas.create_text(
                event.x + size_x, event.y - size_y, text=text))
            self.root_dict[text].append(self.canvas.create_text(
                event.x - operator_param, event.y - operator_param, text=operator, font='bold'))
            self.curr_obj_created[2] = operator
        self.canvas.unbind('<ButtonRelease-1>')
        self.curr_obj_created[1] = text

        self.curr_obj_created[3] = event
        self.create_node_on_bcc_side()

    def create_leaf_on_gui_side(self, leaf_name, input_box):
        circle = self.canvas.create_oval(0, 0, 0, 0)
        leaf_text = self.canvas.create_text(0, 0, text=leaf_name)
        self.elements_added_but_not_drawn_list.append(circle)
        self.elements_added_but_not_drawn_list.append(leaf_text)
        self.canvas.bind('<Motion>', lambda event, param1=circle, param2=leaf_text, param3='empty',
                                            param4='leaf': self.move_node_when_adding(event, param1, param2, param3,
                                                                                      param4))
        self.canvas.bind('<Button-1>', lambda event, param2=leaf_name, param3='leaf',
                                              param4=input_box: self.draw_node(event, param2, param3, param4))
        self.canvas.bind('<ButtonRelease-1>', lambda event, param1=leaf_name,
                                                     param2='empty', param3='leaf', param4=leaf_text: self.write_text(
            event, param1, param2, param3, param4))
        self.curr_obj_created[0] = 0

    def gather_inode_info(self):
        self.temporary_elements[0].destroy()
        self.temporary_elements.clear()
        name_label = Label(self.actions_frame, text="Name: ")
        name_label.grid(row=1, column=3)

        name_input = Entry(self.actions_frame, width=15)
        name_input.grid(row=1, column=4)

        operator_label = Label(self.actions_frame, text="Operator: ")
        operator_label.grid(row=1, column=5)

        operator_combo = ttk.Combobox(self.actions_frame, values=[
            'and', 'or'], state='readonly', width=4)
        operator_combo.grid(row=1, column=6)

        go_button = Button(self.actions_frame, text="Add inner node",
                           command=lambda: [self.empty_elements_added_but_not_drawn_list(
                           ), self.check_inode_info_when_adding_and_editing(name_input.get(), operator_combo.get(),
                                                                            'add', name_input, 'empty', 'empty',
                                                                            'empty')])
        go_button.grid(row=1, column=7, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel action",
                               command=lambda: [self.empty_elements_added_but_not_drawn_list(),
                                                self.canvas.unbind('<ButtonRelease-1>'), self.canvas.unbind('<Motion>'),
                                                self.canvas.unbind(
                                                    '<Button-1>'), self.vertex_combo_menu.destroy(),
                                                cancel_button.destroy(), go_button.destroy(), name_input.destroy(),
                                                name_label.destroy(), operator_combo.destroy(),
                                                operator_label.destroy(), self.display_vertex_combo_menu_when_adding()])
        cancel_button.grid(row=1, column=8, padx=20)

    def check_inode_info_when_adding_and_editing(self, inode_name, inode_operator, mode, in_box, old_n, old_o,
                                                 objs_to_delete):
        if inode_name.replace(" ", "") == '' and inode_operator == '':
            messagebox.showwarning(
                "Warning", "Inner node name and operator are empty.")
        elif inode_name.replace(" ", "") == '':
            messagebox.showwarning("Warning", "Inner node name is empty.")
        elif inode_operator == '':
            messagebox.showwarning("warning", "Inner node operator is empty.")
        else:
            if mode == 'add':
                if inode_name in self.inodes_dict.keys() or inode_name in self.list_of_all_nodes_names:
                    messagebox.showerror(
                        "Error", "Inner node already exists or other node has this name")
                else:
                    self.create_inode_on_gui_side(
                        inode_name, inode_operator, in_box)
            else:
                ret = self.edit_node_on_gui_side(
                    old_n, inode_name, old_o, inode_operator, 'inode', objs_to_delete)
                if ret == True:
                    self.edit_node_on_bcc_side(
                        old_n, inode_name, inode_operator, 'inode')

    def create_inode_on_gui_side(self, inode_name, inode_operator, in_box):
        circle = self.canvas.create_oval(0, 0, 0, 0)
        inode_text = self.canvas.create_text(0, 0, text=inode_name)
        inode_operator_text = self.canvas.create_text(
            0, 0, text=inode_operator)
        self.elements_added_but_not_drawn_list.append(circle)
        self.elements_added_but_not_drawn_list.append(inode_operator_text)
        self.canvas.bind('<Motion>', lambda event, param1=circle, param2=inode_text, param3=inode_operator_text,
                                            param4='inode': self.move_node_when_adding(event, param1, param2, param3,
                                                                                       param4))
        self.canvas.bind('<Button-1>', lambda event, param2=inode_name, param3='inode',
                                              param4=in_box: self.draw_node(event, param2, param3, param4))
        self.canvas.bind('<ButtonRelease-1>', lambda event, param1=inode_name,
                                                     param2=inode_operator, param3='inode',
                                                     param4=inode_text: self.write_text(event, param1, param2, param3,
                                                                                        param4))
        self.curr_obj_created[0] = 1

    def gather_root_info(self):
        self.temporary_elements[0].destroy()
        self.temporary_elements.clear()
        name_label = Label(self.actions_frame, text="Name: ")
        name_label.grid(row=1, column=3)

        name_input = Entry(self.actions_frame, width=15)
        name_input.grid(row=1, column=4)

        operator_label = Label(self.actions_frame, text="Operator: ")
        operator_label.grid(row=1, column=5)

        operator_combo = ttk.Combobox(self.actions_frame, values=[
            'and', 'or'], state='readonly', width=4)
        operator_combo.grid(row=1, column=6)

        go_button = Button(self.actions_frame, text="Add root node",
                           command=lambda: self.check_root_info_when_adding_and_editing(
                               name_input.get(), operator_combo.get(), 'nada', 'nada', 'add', name_input, 'nada'))
        go_button.grid(row=1, column=7, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel action",
                               command=lambda: [self.vertex_combo_menu.destroy(), cancel_button.destroy(
                               ), go_button.destroy(), name_input.destroy(), name_label.destroy(),
                                                operator_combo.destroy(), operator_label.destroy(),
                                                self.display_actions()])
        cancel_button.grid(row=1, column=8, padx=20)

    def check_root_info_when_adding_and_editing(self, root_name, root_operator, oid, oop, mode, in_box, objs_to_delete):
        if root_name.replace(" ", "") == '' and root_operator == '':
            messagebox.showwarning(
                "Warning", "Root node name and operator are empty.")
        elif root_name.replace(" ", "") == '':
            messagebox.showwarning("Warning", "Root node name is empty.")
        elif root_operator == '':
            messagebox.showwarning("warning", "Root node operator is empty.")
        else:
            if mode == 'add':
                if root_name not in self.list_of_all_nodes_names:
                    if len(self.root_dict.keys()) == 0:
                        self.create_root_on_gui_side(
                            root_name, root_operator, in_box)
                    else:
                        messagebox.showerror(
                            "Error", "Root is created. Only one root is accepted")
                else:
                    pass
                    # messagebox.showerror("Error",'This name is taken')
            else:
                ret = self.edit_node_on_gui_side(
                    oid, root_name, oop, root_operator, 'root', objs_to_delete)
                if ret:
                    self.edit_node_on_bcc_side(
                        oid, root_name, root_operator, 'root')

    def create_root_on_gui_side(self, r_name, r_op, in_box):
        circle = self.canvas.create_oval(0, 0, 0, 0)
        r_text = self.canvas.create_text(0, 0, text=r_name)
        r_op_text = self.canvas.create_text(0, 0, text=r_op)
        self.elements_added_but_not_drawn_list.append(circle)
        self.elements_added_but_not_drawn_list.append(r_text)
        self.elements_added_but_not_drawn_list.append(r_op_text)
        self.canvas.bind('<Motion>', lambda event, param1=circle, param2=r_text, param3=r_op_text,
                                            param4='root': self.move_node_when_adding(event, param1, param2, param3,
                                                                                      param4))
        self.canvas.bind('<Button-1>', lambda event, param2=r_name, param3='root',
                                              param4=in_box: self.draw_node(event, param2, param3, param4))
        self.canvas.bind('<ButtonRelease-1>', lambda event, param1=r_name, param2=r_op,
                                                     param3='root', param4=r_text: self.write_text(event, param1,
                                                                                                   param2, param3,
                                                                                                   param4))
        self.curr_obj_created[0] = 2

    def edit_elements_controller(self, event):
        self.elements_combo_menu_for_removing['state'] = 'disabled'
        self.elements_combo_menu_for_adding['state'] = 'disabled'
        self.elements_combo_menu_for_editing['state'] = 'disabled'
        if self.elements_combo_menu_for_editing.get() == "Vertex":
            self.display_vertex_combo_menu_when_editing()
        else:
            self.choose_edge_to_edit_panel()

    def choose_edge_to_edit_panel(self):
        from_label = Label(self.actions_frame, text="Edge to edit")
        from_label.grid(row=2, column=2)

        edges_list = list(self.edges_dict.values())

        edges_combo = ttk.Combobox(
            self.actions_frame, values=edges_list, state='readonly', width=18)
        edges_combo.grid(row=2, column=3)
        edges_combo.set("Choose edge")
        cancel_button = Button(self.actions_frame, text="Cancel action", command=lambda: [
            cancel_button.destroy(), from_label.destroy(), edges_combo.destroy(), self.display_actions()])
        cancel_button.grid(row=2, column=4, padx=20)
        param1 = 'empty'
        param2 = edges_combo
        param3 = from_label
        param4 = cancel_button
        edges_combo.bind("<<ComboboxSelected>>", lambda x: self.edit_edge_panel(
            x, param1, param2, param3, param4))

    def edit_edge_panel(self, event, edge, edges_combo, label, clc_button):
        edge = edges_combo.get()
        print(edge)
        nodes = edge.split(' ')
        clc_button.destroy()

        from_label = Label(self.actions_frame, text=" From node")
        from_label.grid(row=2, column=4)

        start_node = ttk.Combobox(
            self.actions_frame, values=nodes[0], state='readonly')
        start_node.grid(row=2, column=5)

        to_label = Label(self.actions_frame, text=" to node ")
        to_label.grid(row=2, column=6)

        list_of_nodes_inner_nodes_and_root = []
        for node in self.list_of_all_nodes_names:
            if node not in self.leafs_dict.keys():
                list_of_nodes_inner_nodes_and_root.append(node)
        try:
            list_of_nodes_inner_nodes_and_root.remove(nodes[1])
            list_of_nodes_inner_nodes_and_root.remove(nodes[0])
        except Exception as e:
            pass
        end_node = ttk.Combobox(
            self.actions_frame, values=list_of_nodes_inner_nodes_and_root, state='readonly')
        end_node.grid(row=2, column=7)

        go_button = Button(self.actions_frame, text="Edit edge",
                           command=lambda: self.edge_check_info_when_adding_editing_removing(
                               nodes[0], end_node.get(), 'edit', nodes[1]))
        go_button.grid(row=2, column=8, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel action",
                               command=lambda: [cancel_button.destroy(), go_button.destroy(
                               ), to_label.destroy(), start_node.destroy(), edges_combo.destroy(), label.destroy(),
                                                from_label.destroy(), end_node.destroy(),
                                                self.choose_edge_to_edit_panel()])
        cancel_button.grid(row=2, column=9, padx=20)

    def display_vertex_combo_menu_when_editing(self):
        self.display_vertex_combo_menu(2, 2)  # row and column to display on
        self.vertex_combo_menu.bind(
            "<<ComboboxSelected>>", self.edit_vertex_controller)

    def edit_vertex_controller(self, event):
        option = self.vertex_combo_menu.get()
        self.vertex_combo_menu['state'] = 'disabled'
        self.elements_combo_menu_for_editing['state'] = 'disabled'
        if option == "Leaf":
            self.display_leafs_editing_panel()
        elif option == "Inner Node":
            self.display_inodes_editing_panel()
        else:
            self.display_root_editing_panel()

    def display_root_editing_panel(self):
        root_name = list(self.root_dict.keys())
        root_name = root_name[0]
        operators = ['and', 'or']

        root_label = Label(self.actions_frame, text="Root name: ")
        root_label.grid(row=2, column=4)

        name_entry = Entry(self.actions_frame, text=root_name, )
        name_entry.grid(row=2, column=5)
        name_entry.insert(0, root_name)
        operator_label = Label(self.actions_frame, text=" and operator ")
        operator_label.grid(row=2, column=6)

        operator_selection = ttk.Combobox(
            self.actions_frame, values=operators, state='readonly', width=5)
        operator_selection.grid(row=2, column=7)

        op_text_obj = self.root_dict[root_name][2]
        op = self.canvas.itemcget(op_text_obj, "text")

        go_button = Button(self.actions_frame, text="Edit root",
                           command=lambda: self.check_root_info_when_adding_and_editing(
                               name_entry.get(), operator_selection.get(), root_name, op, 'edit', 'nada',
                               objs_to_delete))
        go_button.grid(row=2, column=9, padx=10)

        new_cancel_button = Button(self.actions_frame, text="Cancel",
                                   command=lambda: [operator_selection.destroy(), root_label.destroy(),
                                                    operator_label.destroy(
                                                    ), name_entry.destroy(), go_button.destroy(),
                                                    new_cancel_button.destroy(), self.vertex_combo_menu.destroy(),
                                                    self.display_actions()])
        new_cancel_button.grid(row=2, column=10)

        objs_to_delete = [root_label, name_entry, operator_label,
                          operator_selection, go_button, new_cancel_button]

    def display_inodes_editing_panel(self):
        inode_list = list(self.inodes_dict.keys())

        edit_label = Label(self.actions_frame, text="Edit ")
        edit_label.grid(row=2, column=3)

        inodes_combo_menu = ttk.Combobox(
            self.actions_frame, values=inode_list, state='readonly', width=10)
        inodes_combo_menu.grid(row=2, column=4)

        cancel_button = Button(self.actions_frame, text="Cancel", command=lambda: [self.vertex_combo_menu.destroy(
        ), edit_label.destroy(), inodes_combo_menu.destroy(), cancel_button.destroy(), self.display_actions()])
        cancel_button.grid(row=2, column=7, padx=10)

        inodes_combo_menu.bind("<<ComboboxSelected>>", lambda x: self.display_edit_inode_panel(
            'dummy parameter', cancel_button, edit_label, inodes_combo_menu, inodes_combo_menu.get()))

    def display_edit_inode_panel(self, event, cancel_button, previus_label, inodes_combo_menu, inode_name):
        cancel_button.destroy()
        operators = ['and', 'or']
        inodes_combo_menu['state'] = 'disabled'

        my_label = Label(self.actions_frame, text=" Name ")
        my_label.grid(row=2, column=5)

        name_input = Entry(self.actions_frame, width=10)
        name_input.insert(0, inode_name)
        name_input.grid(row=2, column=6)

        my_second_label = Label(self.actions_frame, text=" Operator ")
        my_second_label.grid(row=2, column=7)

        operator_selection = ttk.Combobox(
            self.actions_frame, values=operators, state='readonly', width=5)
        operator_selection.grid(row=2, column=8)
        op_text_obj = self.inodes_dict[inode_name][2]
        op = self.canvas.itemcget(op_text_obj, "text")
        go_button = Button(self.actions_frame, text="Edit",
                           command=lambda: self.check_inode_info_when_adding_and_editing(
                               name_input.get(), operator_selection.get(), 'edit', 'empty', inode_name, op,
                               objs_to_destroy))
        go_button.grid(row=2, column=9, padx=10)

        new_cancel_button = Button(self.actions_frame, text="Cancel",
                                   command=lambda: [operator_selection.destroy(), my_second_label.destroy(),
                                                    my_label.destroy(), name_input.destroy(
                                       ), go_button.destroy(), new_cancel_button.destroy(),
                                                    self.vertex_combo_menu.destroy(), previus_label.destroy(),
                                                    inodes_combo_menu.destroy(), cancel_button.destroy(),
                                                    self.display_actions()])
        new_cancel_button.grid(row=2, column=10)

        objs_to_destroy = [previus_label, my_second_label, inodes_combo_menu, my_label,
                           name_input, my_label, operator_selection, go_button, new_cancel_button]

    def display_leafs_editing_panel(self):
        leafs_list = list(self.leafs_dict.keys())

        edit_label = Label(self.actions_frame, text="Edit leaf ")
        edit_label.grid(row=2, column=3)

        leafs_combo_menu = ttk.Combobox(
            self.actions_frame, values=leafs_list, state='readonly', width=10)
        leafs_combo_menu.grid(row=2, column=4)

        cancel_button = Button(self.actions_frame, text="Cancel", command=lambda: [self.vertex_combo_menu.destroy(
        ), edit_label.destroy(), leafs_combo_menu.destroy(), cancel_button.destroy(), self.display_actions()])
        cancel_button.grid(row=2, column=7, padx=10)

        leafs_combo_menu.bind("<<ComboboxSelected>>", lambda x: self.display_edit_leaf_panel(
            'dummy parameter', cancel_button, edit_label, leafs_combo_menu, leafs_combo_menu.get()))

    def display_edit_leaf_panel(self, event, cancel_button, previus_label, leafs_combo_menu, leaf_name):
        cancel_button.destroy()
        name_input = Entry(self.actions_frame, width=10)
        leafs_combo_menu['state'] = 'disabled'

        my_label = Label(self.actions_frame, text=" Name ")
        my_label.grid(row=2, column=5)

        # name_input=Entry(self.actions_frame,width=10)
        name_input.insert(0, leaf_name)
        name_input.grid(row=2, column=6)

        go_button = Button(self.actions_frame, text="Edit leaf",
                           command=lambda: self.check_leaf_info(name_input.get(), 'edit', name_input, leaf_name,
                                                                objs_to_delete))
        go_button.grid(row=2, column=7, padx=10)

        new_cancel_button = Button(self.actions_frame, text="Cancel",
                                   command=lambda: [my_label.destroy(), name_input.destroy(), go_button.destroy(
                                   ), new_cancel_button.destroy(), self.vertex_combo_menu.destroy(),
                                                    previus_label.destroy(), leafs_combo_menu.destroy(),
                                                    cancel_button.destroy(), self.display_actions()])
        new_cancel_button.grid(row=2, column=8)

        objs_to_delete = [name_input, my_label, go_button,
                          new_cancel_button, previus_label, leafs_combo_menu]

    def edit_node_on_gui_side(self, old_n_name, new_n_name, old_op, new_op, n_type, obj_to_delete_list):
        if old_n_name == new_n_name and old_op == new_op:
            messagebox.showwarning(
                "Warning", "New info and old info are the same.")
        elif old_n_name == new_n_name and old_op != new_op:
            if n_type == 'leaf':
                messagebox.showwarning(
                    "Warning", "New info and old info are the same.")
                for obj in obj_to_delete_list:
                    obj.destroy()
                self.display_leafs_editing_panel()
            elif n_type == 'inode':
                op_obj = self.inodes_dict[new_n_name][2]
                self.canvas.itemconfigure(op_obj, text=new_op)
                for obj in obj_to_delete_list:
                    obj.destroy()
                self.display_inodes_editing_panel()
                print("Node edited succesfully")
            else:
                op_obj = self.root_dict[new_n_name][2]
                self.canvas.itemconfigure(op_obj, text=new_op)
                for obj in obj_to_delete_list:
                    obj.destroy()
                self.display_root_editing_panel()
                print("Node edited succesfully")
            if self.node_has_edges(old_n_name):
                self.update_edges_on_node_changes(old_n_name, new_n_name)
            return True
        elif new_n_name != old_n_name and old_op == new_op:
            if new_n_name not in self.list_of_all_nodes_names:
                self.list_of_all_nodes_names.remove(old_n_name)
                self.list_of_all_nodes_names.append(new_n_name)
                if n_type == 'leaf':
                    self.leafs_dict[new_n_name] = self.leafs_dict.pop(
                        old_n_name)
                    text_obj = self.leafs_dict[new_n_name][1]
                    self.canvas.itemconfigure(text_obj, text=new_n_name)
                    for obj in obj_to_delete_list:
                        obj.destroy()
                    self.display_leafs_editing_panel()
                    print("Node edited succesfully")
                elif n_type == 'inode':
                    self.inodes_dict[new_n_name] = self.inodes_dict.pop(
                        old_n_name)
                    text_obj = self.inodes_dict[new_n_name][1]
                    self.canvas.itemconfigure(text_obj, text=new_n_name)
                    for obj in obj_to_delete_list:
                        obj.destroy()
                    self.display_inodes_editing_panel()
                    print("Node edited succesfully")
                else:
                    self.root_dict[new_n_name] = self.root_dict.pop(old_n_name)
                    text_obj = self.root_dict[new_n_name][1]
                    self.canvas.itemconfigure(text_obj, text=new_n_name)
                    for obj in obj_to_delete_list:
                        obj.destroy()
                    self.display_root_editing_panel()
                    print("Node edited succesfully")

                if self.node_has_edges(old_n_name):
                    self.update_edges_on_node_changes(old_n_name, new_n_name)
                return True

            else:
                messagebox.showerror("Error", "This name is already taken")
                return False
        elif new_n_name != old_n_name and old_op != new_op:
            if new_n_name not in self.list_of_all_nodes_names:
                self.list_of_all_nodes_names.remove(old_n_name)
                self.list_of_all_nodes_names.append(new_n_name)
                if n_type == 'leaf':
                    self.leafs_dict[new_n_name] = self.leafs_dict.pop(
                        old_n_name)
                    text_obj = self.leafs_dict[new_n_name][1]
                    self.canvas.itemconfigure(text_obj, text=new_n_name)
                    for obj in obj_to_delete_list:
                        obj.destroy()
                    self.display_leafs_editing_panel()
                    print("Node edited succesfully")
                elif n_type == 'inode':
                    self.inodes_dict[new_n_name] = self.inodes_dict.pop(
                        old_n_name)
                    text_obj = self.inodes_dict[new_n_name][1]
                    self.canvas.itemconfigure(text_obj, text=new_n_name)
                    op_obj = self.inodes_dict[new_n_name][2]
                    self.canvas.itemconfigure(op_obj, text=new_op)
                    for obj in obj_to_delete_list:
                        obj.destroy()
                    self.display_inodes_editing_panel()
                    print("Node edited succesfully")
                else:
                    self.root_dict[new_n_name] = self.root_dict.pop(old_n_name)
                    text_obj = self.root_dict[new_n_name][1]
                    self.canvas.itemconfigure(text_obj, text=new_n_name)
                    op_obj = self.root_dict[new_n_name][2]
                    self.canvas.itemconfigure(op_obj, text=new_op)
                    for obj in obj_to_delete_list:
                        obj.destroy()
                    self.display_root_editing_panel()
                    print("Node edited succesfully")

                if self.node_has_edges(old_n_name):
                    self.update_edges_on_node_changes(old_n_name, new_n_name)
                return True
            else:
                messagebox.showerror("Error", "This name is already taken")
                return False

    def edit_node_on_bcc_side(self, oid, nid, nop, ntype):
        if ntype == 'leaf':
            self.bcc.update_leaf_id(oid, nid)
        elif ntype == 'inode':
            self.bcc.update_inode_id(oid, nid)
            self.bcc.change_inner_node_operator(nid, nop)
        else:
            self.bcc.update_root_id(oid, nid)

    def update_edges_on_node_changes(self, old_n_name, new_n_name):
        for edge in list(self.edges_dict.keys()):
            if old_n_name in self.edges_dict[edge][0]:
                self.edges_dict[edge] = [new_n_name, self.edges_dict[edge][1]]
            elif old_n_name in self.edges_dict[edge][1]:
                self.edges_dict[edge] = [self.edges_dict[edge][0], new_n_name]
            else:
                pass

    def remove_elements_controller(self, event):
        self.elements_combo_menu_for_removing['state'] = 'disabled'
        self.elements_combo_menu_for_adding['state'] = 'disabled'
        self.elements_combo_menu_for_editing['state'] = 'disabled'
        if self.elements_combo_menu_for_removing.get() == "Vertex":
            self.display_vertex_combo_menu_when_removing()
        else:
            self.remove_edge_diplay_panel()

    def remove_edge_diplay_panel(self):
        from_label = Label(self.actions_frame, text="Remove edge: ")
        from_label.grid(row=3, column=2)

        edges_list = list(self.edges_dict.values())

        edges_combo = ttk.Combobox(
            self.actions_frame, values=edges_list, state='readonly', width=18)
        edges_combo.grid(row=3, column=3)
        edges_combo.set("Choose edge")

        go_button = Button(self.actions_frame, text="Remove edge",
                           command=lambda: [self.edge_check_info_when_adding_editing_removing(
                               edges_combo.get(), edges_combo.get(), 'remove', 'empty'), from_label.destroy(),
                               edges_combo.destroy(), go_button.destroy(), cancel_button.destroy()])
        go_button.grid(row=3, column=6, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel action", command=lambda: [cancel_button.destroy(
        ), go_button.destroy(), edges_combo.destroy(), from_label.destroy(), self.display_actions()])
        cancel_button.grid(row=3, column=7, padx=20)

    def add_elements_controller(self, event):
        self.elements_combo_menu_for_removing['state'] = 'disabled'
        self.elements_combo_menu_for_adding['state'] = 'disabled'
        self.elements_combo_menu_for_editing['state'] = 'disabled'
        if self.elements_combo_menu_for_adding.get() == "Vertex":

            self.display_vertex_combo_menu_when_adding()
        else:
            self.add_edge_display_panel()

    def add_edge_display_panel(self):
        from_label = Label(self.actions_frame, text="Add edge from node ")
        from_label.grid(row=1, column=2)
        list_of_nodes_without_root = self.list_of_all_nodes_names.copy()
        if self.bcc.root is not None:
            list_of_nodes_without_root.remove(self.bcc.root.id)
        start_nodes_combo = ttk.Combobox(
            self.actions_frame, values=list_of_nodes_without_root
            , state='readonly', width=18)
        start_nodes_combo.grid(row=1, column=3)
        start_nodes_combo.set("Choose node")

        to_label = Label(self.actions_frame, text=" to node ")
        to_label.grid(row=1, column=4)
        list_of_nodes_without_leafs = []
        for node in self.list_of_all_nodes_names:
            if node not in self.leafs_dict.keys():
                list_of_nodes_without_leafs.append(node)
        end_nodes_combo = ttk.Combobox(
            self.actions_frame, values=list_of_nodes_without_leafs, state='readonly', width=18)
        end_nodes_combo.grid(row=1, column=5)
        end_nodes_combo.set("Choose node")

        go_button = Button(self.actions_frame, text="Add edge",
                           command=lambda: self.edge_check_info_when_adding_editing_removing(
                               start_nodes_combo.get(), end_nodes_combo.get(), 'add', 'empty'))
        go_button.grid(row=1, column=6, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel action",
                               command=lambda: [cancel_button.destroy(), go_button.destroy(
                               ), end_nodes_combo.destroy(), to_label.destroy(), start_nodes_combo.destroy(),
                                                from_label.destroy(), self.display_actions()])
        cancel_button.grid(row=1, column=7, padx=20)

    def edge_check_info_when_adding_editing_removing(self, start_node, end_node, mode, old_en):
        if mode == 'add':
            if end_node == 'Choose node' or start_node == 'Choose node':
                messagebox.showwarning("Warning", "Choose nodes")
            elif end_node == start_node and end_node != 'Choose node':
                messagebox.showwarning("Warning", "Nodes are the same")
            else:  # good to go
                self.create_edge_on_gui_side(start_node, end_node)
        elif mode == 'edit':
            if end_node == 'Choose node' or start_node == 'Choose node':
                messagebox.showwarning("Warning", "Choose nodes")
            else:
                self.remove_edge_on_gui_side(start_node, old_en)
                self.remove_edge_on_bcc_side(start_node, old_en)
                self.create_edge_on_gui_side(start_node, end_node)
        else:
            nodes = start_node.split(' ')
            self.remove_edge_on_gui_side(nodes[0], nodes[1])
            self.remove_edge_on_bcc_side(nodes[0], nodes[1])
            self.remove_edge_diplay_panel()

    def remove_edge_on_gui_side(self, sn, en):
        val_list = list(self.edges_dict.values())
        key_list = list(self.edges_dict.keys())
        key_pos = val_list.index([sn, en])
        self.canvas.delete(key_list[key_pos])
        self.edges_dict.pop(key_list[key_pos])

    def remove_edge_on_bcc_side(self, sn, en):
        if sn in self.leafs_dict.keys():
            if en in self.inodes_dict.keys():
                self.bcc.delete_in_edge_for_inner_node(en, sn)
            else:
                self.bcc.delete_in_edge_for_root(sn)
            l_obj = self.bcc.get_leaf_by_id(sn)
            self.bcc.delete_leaf_out_edge(l_obj, en)
        else:
            if en in self.inodes_dict.keys():
                self.bcc.delete_in_edge_for_inner_node(en, sn)
            else:
                self.bcc.delete_in_edge_for_root(sn)
            self.bcc.delete_out_edge_for_inner_node(sn, en)

    def create_edge_on_gui_side(self, start_node, end_node):
        start_node_cords = None
        end_node_cords = None
        if end_node in self.leafs_dict.keys():
            messagebox.showwarning(
                "Warning", "Please create edges only in bottom up manner")
        else:

            if start_node in self.leafs_dict.keys():
                start_node_cords = self.bcc.get_top_cords_for_inodes_and_leafs(
                    start_node, 'leaf')
            else:
                start_node_cords = self.bcc.get_top_cords_for_inodes_and_leafs(
                    start_node, 'inode')
            if start_node_cords is None:
                messagebox.showwarning(
                    "Warning", "Please create edges only in bottom up manner")
            else:
                if end_node in self.root_dict.keys():
                    end_node_cords = self.bcc.get_bottom_cords_for_inodes_and_root(
                        end_node, 'root')
                else:
                    end_node_cords = self.bcc.get_bottom_cords_for_inodes_and_root(
                        end_node, 'inode')
                if start_node_cords is None or end_node_cords is None:
                    messagebox.showwarning(
                        "Warning", "Please create edges only in bottom up manner")
                else:
                    ret = self.create_edge_on_bcc_side(start_node, end_node)
                    if ret:  # on this point i'm sure the edge is ok to add
                        line_obj = self.canvas.create_line(
                            start_node_cords[0], start_node_cords[1], end_node_cords[0], end_node_cords[1])
                        edge_ends = [start_node, end_node]
                        self.edges_dict[line_obj] = edge_ends
                        del edge_ends
        # self.canvas.create_line()

    def display_vertex_combo_menu_when_adding(self):
        if len(self.temporary_elements) > 0:
            self.temporary_elements[0].destroy()
            self.temporary_elements.clear()
        cancel_button = Button(self.actions_frame, text='Cancel', command=lambda: [cancel_button.destroy(),
                                                                                   self.vertex_combo_menu.destroy(),
                                                                                   self.display_actions()])
        cancel_button.grid(row=1, column=3, padx=5)
        self.temporary_elements.append(cancel_button)
        self.display_vertex_combo_menu(1, 2)  # row and column to display on
        self.vertex_combo_menu.bind(
            "<<ComboboxSelected>>", self.add_vertex_controller)

    def add_vertex_controller(self, event):
        option = self.vertex_combo_menu.get()
        self.vertex_combo_menu['state'] = 'disabled'
        self.elements_combo_menu_for_adding['state'] = 'disabled'
        if option == "Leaf":
            self.gather_leaf_info()
        elif option == "Inner Node":
            self.gather_inode_info()
        else:
            self.gather_root_info()

    def display_vertex_combo_menu_when_removing(self):
        self.display_vertex_combo_menu(3, 2)  # row and column to display on
        self.vertex_combo_menu.bind(
            "<<ComboboxSelected>>", self.remove_vertex_controller)

    def remove_vertex_controller(self, event):
        option = self.vertex_combo_menu.get()
        self.vertex_combo_menu['state'] = 'disabled'
        self.elements_combo_menu_for_removing['state'] = 'disabled'
        if option == "Leaf":
            self.display_leafs_removal_panel()
        elif option == "Inner Node":
            self.display_inodes_removal_panel()
        else:
            self.display_root_removal_panel()

    def display_leafs_removal_panel(self):
        leafs_list = list(self.leafs_dict.keys())

        remove = Label(self.actions_frame, text="Choose a leaf to remove ")
        remove.grid(row=3, column=3)

        leafs_combo_menu = ttk.Combobox(
            self.actions_frame, values=leafs_list, state='readonly', width=10)
        leafs_combo_menu.grid(row=3, column=4)

        go_button = Button(self.actions_frame, text="Remove leaf",
                           command=lambda: self.check_leaf_info(leafs_combo_menu.get(), 'remove', 'empty_parameter',
                                                                'empty_parameter', obj_to_destroy))
        go_button.grid(row=3, column=5, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel", command=lambda: [self.vertex_combo_menu.destroy(
        ), leafs_combo_menu.destroy(), go_button.destroy(), remove.destroy(), cancel_button.destroy(),
            self.display_actions()])
        cancel_button.grid(row=3, column=6, padx=10)

        obj_to_destroy = [remove, leafs_combo_menu, go_button, cancel_button]

    def remove_node_on_gui_side(self, node_name, n_type):
        if n_type == 'leaf':
            self.canvas.delete(self.leafs_dict[node_name][0])  # remove circle
            # remove text name
            self.canvas.delete(self.leafs_dict[node_name][1])
            self.leafs_dict.pop(node_name)
            print("leaf " + node_name + " removed succesfully")
        elif n_type == 'inode':
            self.canvas.delete(self.inodes_dict[node_name][0])  # remove circle
            # remove text name
            self.canvas.delete(self.inodes_dict[node_name][1])
            # remove operator text
            self.canvas.delete(self.inodes_dict[node_name][2])
            self.inodes_dict.pop(node_name)
            print("inode " + node_name + " removed succesfully")
        else:  # root
            self.canvas.delete(self.root_dict[node_name][0])  # remove circle
            # remove text name
            self.canvas.delete(self.root_dict[node_name][1])
            # remove operator text
            self.canvas.delete(self.root_dict[node_name][2])
            self.root_dict.pop(node_name)
        self.list_of_all_nodes_names.remove(node_name)

    def remove_node_on_bcc_side(self, n_name, n_type):
        if n_type == 'leaf':

            ret = self.bcc.remove_leaf(n_name)
            print(ret)
        elif n_type == 'inode':
            self.bcc.remove_inner_node(n_name)
        else:  # root
            self.bcc.remove_root()

    def display_inodes_removal_panel(self):
        inode_list = list(self.inodes_dict.keys())
        remove = Label(self.actions_frame,
                       text="Choose an inner node to remove ")
        remove.grid(row=3, column=3)

        inodes_combo_menu = ttk.Combobox(
            self.actions_frame, values=inode_list, state='readonly', width=10)
        inodes_combo_menu.grid(row=3, column=4)

        go_button = Button(self.actions_frame, text="Remove inner node",
                           command=lambda: [self.check_inode_info_when_removing(inodes_combo_menu.get()),
                                            remove.destroy(), inodes_combo_menu.destroy(), go_button.destroy(),
                                            cancel_button.destroy()])
        go_button.grid(row=3, column=5, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel", command=lambda: [self.vertex_combo_menu.destroy(
        ), inodes_combo_menu.destroy(), go_button.destroy(), remove.destroy(), cancel_button.destroy(),
            self.display_actions()])
        cancel_button.grid(row=3, column=6, padx=10)

    def check_inode_info_when_removing(self, inode_name):
        if inode_name == '':
            messagebox.showwarning("Warning", "Inner node name is empty")
        elif inode_name not in self.list_of_all_nodes_names:
            messagebox.showerror('Error', "Node is already removed")
        else:
            self.remove_node_on_gui_side(inode_name, 'inode')
            self.remove_node_edges_on_gui_side(inode_name)
            self.remove_node_on_bcc_side(inode_name, 'inode')
            self.display_inodes_removal_panel()

    def display_root_removal_panel(self):
        root = list(self.root_dict.keys())
        remove = Label(self.actions_frame, text="Root is ")
        remove.grid(row=3, column=3)

        root_combo_menu = ttk.Combobox(
            self.actions_frame, values=root, state='readonly', width=10)
        root_combo_menu.grid(row=3, column=4)
        root_combo_menu.current(0)

        go_button = Button(self.actions_frame, text="Remove root node",
                           command=lambda: self.check_root_info_when_removing(root_combo_menu.get(), objs_to_destroy))
        go_button.grid(row=3, column=5, padx=10)

        cancel_button = Button(self.actions_frame, text="Cancel", command=lambda: [self.vertex_combo_menu.destroy(
        ), root_combo_menu.destroy(), go_button.destroy(), remove.destroy(), cancel_button.destroy(),
            self.display_actions()])
        cancel_button.grid(row=3, column=6, padx=10)

        objs_to_destroy = [remove, root_combo_menu, go_button, cancel_button]

    def check_root_info_when_removing(self, root_name, objs_to_destroy):
        if root_name == '':
            messagebox.showwarning("Warning", "Root node name is empty")

        else:
            self.remove_node_on_gui_side(root_name, 'root')
            self.remove_node_edges_on_gui_side(root_name)
            self.remove_node_on_bcc_side(root_name, 'root')
            for obj in objs_to_destroy:
                obj.destroy()
            self.vertex_combo_menu.destroy()
            self.display_actions()

    def remove_root(self):
        pass

    def calculate_top_end_point(self, event):  # applicable for leafs and inodes
        cord = ['x', 'y']
        cord[0] = event.x - 20
        cord[1] = event.y - 38
        return cord

    # applicable for root and inodes
    def calculate_bottom_end_point(self, event):
        cord = ['x', 'y']
        cord[0] = event.x - 20
        cord[1] = event.y
        return cord

    def create_node_on_bcc_side(self):
        if self.curr_obj_created[0] == 0:
            self.create_leaf_on_bcc_side()
        elif self.curr_obj_created[0] == 1:
            self.create_inode_on_bcc_side()
        else:
            self.create_root_on_bcc_side()

    def create_leaf_on_bcc_side(self):
        cords = self.calculate_top_end_point(self.curr_obj_created[3])
        ret = self.bcc.add_leaf(self.curr_obj_created[1], cords)
        if "succes" in ret:
            print(ret)
            self.curr_obj_created.clear()
            self.curr_obj_created = [-1] * 4
        else:
            print(ret)

    def create_inode_on_bcc_side(self):
        top_cords = self.calculate_top_end_point(self.curr_obj_created[3])
        bottom_cords = self.calculate_bottom_end_point(
            self.curr_obj_created[3])
        ret = self.bcc.add_inner_node(
            self.curr_obj_created[2], self.curr_obj_created[1], top_cords, bottom_cords)
        if 'succes' in ret:
            print(ret)
            self.curr_obj_created.clear()
            self.curr_obj_created = [-1] * 4
        else:
            print(ret)

    def create_root_on_bcc_side(self):
        bottom_cords = self.calculate_bottom_end_point(
            self.curr_obj_created[3])
        ret = self.bcc.set_root(
            self.curr_obj_created[1], self.curr_obj_created[2], bottom_cords)
        if 'succes' in ret:
            print(ret)
            self.curr_obj_created.clear()
            self.curr_obj_created = [-1] * 4
        else:
            print(ret)

    def create_edge_on_bcc_side(self, start_n, end_n):
        if start_n in self.leafs_dict.keys() and end_n in self.leafs_dict.keys():
            messagebox.showerror("Error", "Can't draw edge between two leafs")
            return False
        elif start_n == end_n:
            messagebox.showerror("Error", "Can't draw edge to the same node")
            return False
        else:
            if end_n in self.root_dict.keys():
                ret = self.bcc.add_in_edge_for_root(start_n)
            else:
                ret = self.bcc.add_in_edge_for_inner_node(end_n, start_n)
            if 'succes' in ret:
                print(ret)
                return True
            else:
                messagebox.showerror("Error", ret)
                return False

    def node_has_edges(self, n_name):
        edges = self.edges_dict.values()
        for edge in edges:
            if n_name in edge:
                return True
        return False

    def remove_node_edges_on_gui_side(self, n_name):
        edges_list = self.edges_dict.values()
        node_edges_list = []
        for edge in edges_list:
            if n_name == edge[0]:
                # self.remove_edge_on_gui_side(n_name,edge[1]) #this creates a run time error
                node_edges_list.append([n_name, edge[1]])
            elif n_name == edge[1]:
                # self.remove_edge_on_gui_side(edge[0],n_name)
                node_edges_list.append([edge[0], n_name])
            else:
                pass
        for n_edge in node_edges_list:
            self.remove_edge_on_gui_side(n_edge[0], n_edge[1])

    def clear_board(self):  # method used to block any other updates of the bc
        self.elements_combo_menu_for_adding['state'] = 'disabled'
        self.elements_combo_menu_for_editing['state'] = 'disabled'
        self.elements_combo_menu_for_removing['state'] = 'disabled'
        # self.run_circuit_button.destroy()
        self.run_circuit_button['state'] = DISABLED

    def check_circuit_integrity(self):
        ok = 1
        given_name = self.circuit_name_entry.get()
        if given_name.strip(' ') == "":
            messagebox.showerror("Error", "Please provide a name for this circuit")
        else:
            for root, dirs, files in os.walk('AccesStructures'):
                for name in files:
                    if given_name == name.split('.')[0]:
                        ok = 0
                        break
            if ok == 0:
                messagebox.showwarning("Warning", "This name is taken. Please choose other name")
            else:

                if len(self.root_dict.keys()) == 0 or len(self.leafs_dict.keys()) == 0:
                    messagebox.showerror("Error", "A boolean circuit needs to have at leas 2 leafs and a root.")

                elif self.bct.pre_run_checkings() == False:
                    messagebox.showerror("Error",
                                         "Some of the inner nodes or the root don't have enough input edges!!! ")
                else:
                    self.clear_board()
                    inodes_removed = self.bct.run_garbage_cleaner()
                    if inodes_removed != []:  # remove inodes from the gui side  and their edges as well
                        mess = ""
                        for inode in inodes_removed:
                            val_list = list(self.edges_dict.values())
                            mess = mess + inode + ", "
                            for edge in val_list:
                                if inode == edge[1]:
                                    self.remove_edge_on_gui_side(edge[0], inode)
                            self.remove_node_on_gui_side(inode, 'inode')
                        messagebox.showinfo(
                            'Info',
                            "Because they weren't connected from above, we removed the following inner node(s): " + mess[
                                                                                                                    :-2])
                    leafs_removed = self.bct.run_null_leafs_cleaner()
                    mess = ""
                    if leafs_removed != []:
                        # remove leafs from gui side and prompt a message to the user
                        for lr in leafs_removed:
                            self.remove_node_on_gui_side(lr, 'leaf')
                            mess = mess + lr + ", "
                        messagebox.showinfo("Info",
                                            "We removed the following leaf/s "
                                            "because it/they wasn't/weren't used: " + mess[:-2])  # remove last
                        # comma and space
                        del mess
                    self.bct.solve_fan_out_leafs()
                    self.bct.solve_level1_fan_out_binar_nodes()
                    self.bct.set_inner_nodes_levels()
                    self.bct.set_root_level()
                    self.bct.solve_fan_out_inner_nodes()
                    self.bcc.create_level_dictionary()
                    # self.bcr.full_run_boolean_circuit(16)
                    self.bcr.save_bc_to_json(given_name)
                    messagebox.showinfo("Info", "Structure Access added successfully. Please Refresh ")

                    self.root.destroy()
                    del self
                    # return self.return_value

                    # self.show_graph_from_json(self.canvas.winfo_width(),self.canvas.winfo_height())


def show_graph_from_json(canvas, file):
    canvas.delete("all")
    f = open(file, 'r')
    bc = json.load(f)
    sorted_bc = dict(sorted(bc.items(), key=lambda x: x[0], reverse=True))
    del bc
    height = canvas.winfo_height()
    width = canvas.winfo_width()
    # print(height,width)
    nr_of_keys = len(sorted_bc.keys())
    layer_height = int(height) / int(nr_of_keys)
    current_height = layer_height
    nodes_dict = {}
    # sorted_bc=sort_based_on_in_edges(sorted_bc.copy())

    # draw circle,name,and operator
    for i in range(nr_of_keys - 1, 0, -1):  # -1 because of index from 0 on dict keys
        layer_center_line = current_height - (layer_height / 2)
        # canvas.create_line(0,layer_center_line,width,layer_center_line,dash=(5,2))
        # canvas.create_line(0,current_height,width,current_height)
        current_height = current_height + layer_height
        nr_of_nodes_in_layer = len(sorted_bc[str(i)])
        width_ratio = width / (nr_of_nodes_in_layer + 1)
        circle_x = 0
        circle_y = layer_center_line
        # print(nr_of_nodes_in_layer)
        for j in range(0, nr_of_nodes_in_layer):
            circle_x += width_ratio
            circle_dim = 20
            canvas.create_oval(circle_x - circle_dim, circle_y - circle_dim, circle_x + circle_dim,
                               circle_y + circle_dim)
            node = sorted_bc[str(i)][j]
            canvas.create_text(circle_x + circle_dim * 2, circle_y - circle_dim, text=node['name'])
            nodes_dict[node['name']] = [circle_x, circle_y]
            try:
                canvas.create_text(circle_x, circle_y, text=node['operator'])
            except Exception as e:
                print(e)
    nr_of_nodes_in_layer = len(sorted_bc['0'])
    width_ratio = width / (nr_of_nodes_in_layer + 1)
    layer_center_line = current_height - (layer_height / 2)
    # current_height=current_height+layer_height
    circle_x = 0
    circle_y = layer_center_line
    for j in range(0, nr_of_nodes_in_layer):
        circle_x += width_ratio
        circle_dim = 20
        canvas.create_oval(circle_x - circle_dim, circle_y - circle_dim, circle_x + circle_dim,
                           circle_y + circle_dim)
        node = sorted_bc['0'][j]
        canvas.create_text(circle_x, circle_y + circle_dim * 1.5, text=node['name'])
        nodes_dict[node['name']] = [circle_x, circle_y]
        try:
            canvas.create_text(circle_x, circle_y, text=node['operator'])
        except Exception as e:
            print(e)

    # draw edges
    for i in range(0, nr_of_keys - 1):
        nr_of_nodes_in_layer = len(sorted_bc[str(i)])
        for j in range(0, nr_of_nodes_in_layer):
            node = sorted_bc[str(i)][j]
            start_point = nodes_dict[node['name']]
            start_x_offset = 0
            start_y_offset = -20
            end_x_offset = 0
            end_y_offset = 20
            try:
                out = node['out']
                out = out[0]
                end_point = nodes_dict[out]
                canvas.create_line(start_point[0] + start_x_offset, start_point[1] + start_y_offset,
                                   end_point[0] + end_x_offset, end_point[1] + end_y_offset)
            except Exception as e:
                print(e)
