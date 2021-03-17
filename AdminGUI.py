from tkinter import *
from os import chdir, getcwd, startfile, listdir, remove
from CreateBooleanCircuitGUI import CreateBooleanCircuitGUI, show_graph_from_json
from tkinter import filedialog
from tkinter import messagebox
import sqlite3
import Auxiliar as aux
from  Crypto.Cipher import AES
from Crypto.Hash import SHA256
from BooleanCircuitController import build_bc_from_json
from BooleanCircuitRunner import BooleanCircuitRunner
class AdminGui:
    def __init__(self):
        self.root = Tk()
        self.root.geometry('650x500+350+100')
        self.root.title("Access Control")
        self.admin_frame = LabelFrame(self.root)
        self.admin_frame.pack(expand=True, fill='both')

        self.top_buttons_frame = LabelFrame(self.admin_frame)
        self.top_buttons_frame.pack(fill='x')
        self.top_buttons_frame.columnconfigure([0, 1, 2], weight=1)

        self.display_frame = LabelFrame(self.admin_frame, bd=8)
        self.display_frame.pack(fill='both', pady=10, expand=True)
        self.connection = sqlite3.connect("AccessControl.db")
        self.cursor = self.connection.cursor()
        self.prime_bit_length = 8

    def directory_manager(self, path):
        if path == "as":
            try:
                chdir("AccessStructures")
            except:
                chdir("..")
                chdir("AccessStructures")
        if path == 'fv':
            try:
                chdir("FilesVault")
            except:
                chdir('..')
                chdir("FilesVault")

    def run(self):
        # self.complete_prime_numbers()
        self.fill_welcome_frame()
        self.create_top_panel_widgets()
        self.root.mainloop()

    def complete_prime_numbers(self):
        self.cursor.execute('SELECT * FROM Prime_numbers')
        primes_list = self.cursor.fetchall()
        self.p = primes_list[1]
        self.y = primes_list[2]
        self.s = primes_list[3]
        del primes_list

    def fill_welcome_frame(self):
        Label(self.display_frame, text="Welcome to the access control application!").pack(pady=15)
    def create_top_panel_widgets(self):
        Button(self.top_buttons_frame, text="Access Control Panel",
               command=self.access_control_panel_with_buttons).grid(row=0, column=0, sticky="NSWE")
        Button(self.top_buttons_frame, text="Files Control Panel",
               command=self.files_control_panel).grid(row=0, column=1, sticky="NSWE")
        Button(self.top_buttons_frame, text="Access Structures Control Panel",
               command=self.acc_control_panel).grid(row=0, column=2, sticky="NSWE")

    def files_control_panel(self):
        self.remove_widget_children(self.display_frame)
        self.display_frame.destroy()  # destroy to remove text
        self.display_frame = LabelFrame(self.admin_frame, bd=8, text="   Files Control Panel    ")
        self.display_frame.pack(fill='both', pady=10, expand=True)

        add_button = Button(self.display_frame, text="Add a new File", command=self.add_file_widgets)
        refresh_button = Button(self.display_frame, text="Refresh", command=self.files_control_panel)

        add_button.pack(padx=20, pady=10)
        refresh_button.pack()

        f_box_list = []
        f_bts_list = []
        f_view_dict = {}
        f_acs_dict = {}
        f_remove_dict = {}

        self.cursor.execute('SELECT * from Files')
        files = self.cursor.fetchall()
        # print (files)
        for file in files:
            # name = file.split('.')
            f_box_list.append(LabelFrame(self.display_frame))
            f_box_list[-1].pack(fill='both', pady=10, padx=10)
            name_label = Label(f_box_list[-1], text="Name: " + file[1], width=20).pack(side=LEFT, padx=10, pady=10)

            f_bts_list.append(Button(f_box_list[-1], text="Open", width=10))
            f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
            f_view_dict[f_bts_list[-1]] = file
            f_bts_list[-1].bind("<Button-1>", lambda x: self.open_file(x, f_view_dict))

            f_bts_list.append(Button(f_box_list[-1], text="File info", width=10))
            f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
            f_acs_dict[f_bts_list[-1]] = file
            f_bts_list[-1].bind("<Button-1>", lambda x: self.view_file_info(x, f_acs_dict))

            f_bts_list.append(Button(f_box_list[-1], text="Remove file", width=10))
            f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
            f_remove_dict[f_bts_list[-1]] = file
            f_bts_list[-1].bind("<Button-1>", lambda x: self.remove_file(x, f_remove_dict, f_bts_list[-1]))

    def add_file_widgets(self):
        file_chosen = filedialog.askopenfilenames(
            parent=self.display_frame,
            initialdir='/',
            filetypes=[
                ("All files", "*")])
        # print(rep)
        try:
            if file_chosen != "":
                # os.startfile(rep[0])
                new_window = Toplevel()
                new_window.geometry("400x200+450+290")
                label1 = Label(new_window, text="You have selected the file " + file_chosen[0].split("/")[-1]).pack(
                    pady=20)
                label2 = Label(new_window, text="Please provide an alias for the file(or keep the file's name):").pack()
                alias_entry = Entry(new_window, width=25)
                alias_entry.pack(pady=10)
                add_btn = Button(new_window, text="Add file",
                                 command=lambda: [self.add_file(file_chosen[0], alias_entry.get()),
                                                  new_window.destroy()],
                                 width=20).pack(pady=10)

        except IndexError:
            print("No file selected")

    def add_file(self, file_path, file_alias):
        try:
            # self.directory_manager('fv')

            self.cursor.execute("INSERT INTO Files(alias, path, extension) VALUES(?, ?,?)", (file_alias, file_path, file_path.split('/')[-1].split('.')[1]))

            self.connection.commit()
            messagebox.showinfo("Info", "File added sucessfully. Please refresh")
        except Exception as e:
            messagebox.showerror("Error", e)

    def encrypt_file(self,file_alias,file_path,key_base):
        hash_meth=SHA256.new()
        print("cheia criptare ", key_base)
        hash_meth.update(key_base.encode())
        key = hash_meth.digest()
        iv="licenta FII 2021".encode()
        encryptor=AES.new(key,AES.MODE_CBC,iv)
        with open(file_path,"rb") as f:
            plain_txt=f.read()
        while len(plain_txt) % 16 !=0:
            plain_txt=plain_txt+b'0'
        f.close()
        cipher_text=encryptor.encrypt(plain_txt)
        with open(file_alias,"wb") as f :
            f.write(cipher_text)
        f.close()

    def open_file(self, event, file_dict):
        btn = event.widget
        for key in file_dict.keys():
            if str(btn) in str(key):
                print("Opening file :", file_dict[key])
                self.cursor.execute("SELECT path from Files where alias=?", (file_dict[key][1],))
                path = self.cursor.fetchone()
                startfile(path[0])

    def remove_file(self, event, file_dict, button):
        btn = event.widget
        for key in file_dict.keys():
            if str(btn) in str(key):
                print("Removing file", file_dict[key])
                self.cursor.execute("SELECT * from Files where alias=?", (file_dict[key][1],))
                params = self.cursor.fetchone()
                if params[3] == '-1':
                    try:
                        self.directory_manager('fv')
                        remove(file_dict[key][1])
                        button.config(state=DISABLED)
                        self.cursor.execute("DELETE from Files where alias=?", (file_dict[key][1],))
                        self.cursor.execute("DELETE from Prime_numbers where file_alias=?", (file_dict[key][1],))
                        self.connection.commit()
                        messagebox.showinfo("Info", "File removed successfully. Please refresh")
                    except Exception as e:
                        messagebox.showerror("Error", e)
                else:
                    messagebox.showerror("Error",
                                         "This file can't be deleted because is protected. Remove protection first")
                    return 'break'

    def view_file_acs(self, event, f_acs_dict):
        btn = event.widget
        for key in f_acs_dict.keys():
            if str(btn) in str(key):
                try:
                    self.cursor.execute('SELECT protected from Files where alias=?', (f_acs_dict[key][1],))
                    params = self.cursor.fetchone()
                    # print((params))
                    if params[0] == '-1':
                        messagebox.showinfo("Info", "This file is not protected")
                        return 'break'
                    else:
                        messagebox.showinfo("Info", "This file is protected by " + params[0] + " access structure")
                        return 'break'
                except Exception as e:
                    messagebox.showerror("Error", e)

    def acc_control_panel(self):
        self.directory_manager('as')
        self.remove_widget_children(self.display_frame)
        self.display_frame.destroy()  # destroy to remove text
        self.display_frame = LabelFrame(self.admin_frame, bd=8, text="   Access Structures Control Panel    ")
        self.display_frame.pack(fill='both', pady=10, expand=True)
        add_button = Button(self.display_frame, text="Add a new Access Control Structure", command=self.add_acs)
        refresh_button = Button(self.display_frame, text="Refresh", command=self.acc_control_panel)

        add_button.pack(padx=20, pady=10)
        refresh_button.pack()

        ac_box_list = []
        ac_bts_list = []
        ac_view_dict = {}
        ac_files_dict = {}
        ac_remove_dict = {}

        for file in listdir(getcwd()):
            name = file.split('.')
            ac_box_list.append(LabelFrame(self.display_frame))
            ac_box_list[-1].pack(fill='both', pady=10, padx=10)
            name_label = Label(ac_box_list[-1], text="Name: " + name[0], width=20).pack(side=LEFT, padx=10, pady=10)

            ac_bts_list.append(Button(ac_box_list[-1], text="Files", width=10))
            ac_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
            ac_files_dict[ac_bts_list[-1]] = file
            ac_bts_list[-1].bind("<Button-1>", lambda x: self.ac_view_files(x, ac_files_dict))

            ac_bts_list.append(Button(ac_box_list[-1], text="View", width=10))
            ac_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
            ac_view_dict[ac_bts_list[-1]] = file
            ac_bts_list[-1].bind("<Button-1>", lambda x: self.ac_view_structure(x, ac_view_dict))

            ac_bts_list.append(Button(ac_box_list[-1], text="Remove", width=10))
            ac_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
            ac_remove_dict[ac_bts_list[-1]] = file
            ac_bts_list[-1].bind("<Button-1>", lambda x: self.ac_remove(x, ac_remove_dict))

    def access_control_panel_with_buttons(self):
        self.remove_widget_children(self.display_frame)
        self.display_frame.destroy()  # destroy to remove text
        self.display_frame = LabelFrame(self.admin_frame, bd=8, text="   Access Control Panel    ")
        self.display_frame.pack(fill='both', pady=10, expand=True)
        v = StringVar()
        rb_frame = LabelFrame(self.display_frame)
        labels_frame = LabelFrame(self.display_frame)

        r1 = Button(self.display_frame, text="Protected files",
                    command=lambda: self.show_protected_files(r1, r2, labels_frame))

        r2 = Button(self.display_frame, text="Unprotected files",
                    command=lambda: self.show_unprotectd_files(r2, r1, labels_frame))
        r1.pack(anchor=N, side=TOP, fill='x')
        r2.pack(anchor=N, side=TOP, fill='x')
        labels_frame.pack(fill='x', anchor=N, side=TOP)

    def show_protected_files(self, button1, button2, labels_frame):
        button1.config(relief=SUNKEN, background='white')
        button2.config(relief=RAISED, background="SystemButtonFace")
        f_box_list = []
        f_bts_list = []
        f_view_dict = {}
        f_remove_dict = {}

        self.remove_widget_children(labels_frame)
        self.cursor.execute("SELECT * from Files where protected !=-1")
        files = self.cursor.fetchall()
        if len(files) == 0:
            Label(labels_frame, text="There are no protected files").pack(fill='x', pady=10)
        else:
            for file in files:
                f_box_list.append(LabelFrame(labels_frame))
                f_box_list[-1].pack(fill='x')
                name_label = Label(f_box_list[-1], text="File alias: " + file[1], width=15).pack(side=LEFT, padx=10,
                                                                                                 pady=10)
                p_label = Label(f_box_list[-1], text="Protected by: " + file[3], width=25).pack(side=LEFT)
                f_bts_list.append(Button(f_box_list[-1], text="File info", width=10))
                f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                f_view_dict[f_bts_list[-1]] = file
                f_bts_list[-1].bind("<Button-1>", lambda x: self.view_file_info(x, f_view_dict))

                f_bts_list.append(Button(f_box_list[-1], text="Remove protection", width=15))
                f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                f_remove_dict[f_bts_list[-1]] = file
                f_bts_list[-1].bind("<Button-1>", lambda x: [self.remove_file_protection(x, f_remove_dict),
                                                             f_bts_list[-1].config(state=DISABLED)])

    def show_unprotectd_files(self, button1, button2, labels_frame):
        button1.config(relief=SUNKEN, background='white')
        button2.config(relief=RAISED, background="SystemButtonFace")

        f_box_list = []
        f_bts_list = []
        f_view_dict = {}
        f_add_pro_dict = {}
        self.remove_widget_children(labels_frame)
        self.cursor.execute("SELECT * from Files where protected =-1")
        files = self.cursor.fetchall()
        if len(files) == 0:
            Label(labels_frame, text="There are no unprotected files").pack(fill='x', pady=10)
        else:
            for file in files:
                f_box_list.append(LabelFrame(labels_frame))
                f_box_list[-1].pack(fill='x')
                name_label = Label(f_box_list[-1], text="File alias: " + file[1], width=20).pack(side=LEFT, padx=30,
                                                                                                 pady=10)

                f_bts_list.append(Button(f_box_list[-1], text="Add protection", width=15))
                f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                f_add_pro_dict[f_bts_list[-1]] = file
                f_bts_list[-1].bind("<Button-1>", lambda x: [self.add_file_protection_widgets(x, f_add_pro_dict),
                                                             f_bts_list[-1].config(state=DISABLED)])

    def view_file_info(self, event, file_dict):
        btn = event.widget
        for key in file_dict.keys():
            if str(btn) in str(key):
                print("View file info for  ", file_dict[key])
                self.cursor.execute("SELECT path from Files where alias=?", (file_dict[key][1],))
                path = self.cursor.fetchone()
                messagebox.showinfo("Info",
                                    "The real file is located at the address: " + path[0])
                return "break"

    def add_file_protection_widgets(self, event, file_dict):
        btn = event.widget
        for key in file_dict.keys():
            if str(btn) in str(key):
                self.directory_manager('as')
                print("Add protection to file " + file_dict[key][1])
                file_name_to_be_send=file_dict[key][1]
                new_window = Toplevel()
                new_window.geometry("600x500+450+100")
                new_window.title("Add protection to file " + file_dict[key][1])
                l = Label(new_window, text="Please choose an access structure:").pack(pady=10)
                ac_box_list = []
                ac_bts_list = []
                ac_view_dict = {}
                ac_files_dict = {}
                ac_remove_dict = {}
                for file in listdir(getcwd()):
                    name = file.split('.')
                    ac_box_list.append(LabelFrame(new_window))
                    ac_box_list[-1].pack(fill='both', pady=10, padx=10)
                    name_label = Label(ac_box_list[-1], text="Name: " + name[0], width=20).pack(side=LEFT, padx=10,
                                                                                                pady=10)

                    ac_bts_list.append(Button(ac_box_list[-1], text="Files", width=10))
                    ac_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                    ac_files_dict[ac_bts_list[-1]] = file
                    ac_bts_list[-1].bind("<Button-1>", lambda x: self.ac_view_files(x, ac_files_dict))

                    ac_bts_list.append(Button(ac_box_list[-1], text="View", width=10))
                    ac_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                    ac_view_dict[ac_bts_list[-1]] = file
                    ac_bts_list[-1].bind("<Button-1>", lambda x: self.ac_view_structure(x, ac_view_dict))

                    ac_bts_list.append(Button(ac_box_list[-1], text="Choose", width=10))
                    ac_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                    ac_remove_dict[ac_bts_list[-1]] = file
                    ac_bts_list[-1].bind("<Button-1>",
                                         lambda x: self.add_file_protection(x, ac_remove_dict, file_name_to_be_send,
                                                                            new_window))
                break

    def add_file_protection(self, event, acs_dict, file_name, parent_widget):
        btn = event.widget
        for key in acs_dict.keys():
            if str(btn) == str(key):
                try:
                    name_of_acs=acs_dict[key].split('.')[0]
                    self.cursor.execute('UPDATE  Files SET protected=? where alias=?',
                                        (name_of_acs, file_name))
                    self.connection.commit()
                    p = aux.get_prime_number(self.prime_bit_length)
                    y = aux.get_random_in_range(0, p - 1)
                    s = aux.get_random_in_range(0, p - 1)
                    self.cursor.execute('INSERT INTO Prime_numbers(file_alias,p,y,s) VALUES(?,?,?,?)',
                                        (file_name, p, y, s,))
                    self.connection.commit()
                    self.cursor.execute('SELECT path from Files where alias=?',(file_name,))
                    path= self.cursor.fetchone()
                    bcc = build_bc_from_json(name_of_acs+ ".json")
                    bcr = BooleanCircuitRunner("bcr", bcc, "-1")
                    access = bcr.full_run_boolean_circuit(p, y, s)
                    enc_key=str(y)+str(s)+str(bcc.root.value_bottom_up)
                    self.directory_manager('fv')
                    self.encrypt_file(file_name,path[0],enc_key)
                    messagebox.showinfo("Info", "Protection added successfully")
                    parent_widget.destroy()

                except Exception as e:
                    messagebox.showerror("Error", e)
                    return "break"
                break

    def remove_file_protection(self, event, file_dict):
        btn = event.widget
        for key in file_dict.keys():
            if str(btn) in str(key):
                print("remove file protection for ", file_dict[key])
                try:
                    self.cursor.execute('UPDATE Files SET protected=? where alias=?', ('-1', file_dict[key][1]))
                    self.connection.commit()
                    self.cursor.execute("DELETE  FROM Prime_numbers WHERE file_alias=?",(file_dict[key][1],))
                    self.connection.commit()
                    messagebox.showinfo("Info", "File protection removed successfully. Please refresh")
                    self.directory_manager('fv')
                    remove(file_dict[key][1])
                except Exception as e:
                    messagebox.showerror("Error", e)
        return "break "

    def add_acs(self):
        create_gui = CreateBooleanCircuitGUI()

    def ac_view_files(self, event, ac_dict):
        btn = event.widget
        files_protected_by_acs = []
        for key in ac_dict.keys():
            if str(btn) in str(key):
                my_access_structure = ac_dict[key].split('.')[0]
                print(my_access_structure)
                self.cursor.execute("SELECT alias from Files where protected=?", (my_access_structure,))
                files_protected_by_acs = self.cursor.fetchall()
                break
        if len(files_protected_by_acs) == 0:
            messagebox.showinfo("Info", "This access structure doesn't protect any file")
            return "break"  # used to raise the button after it was pressed
        else:
            msg = str(files_protected_by_acs[0][0])
            files_protected_by_acs.pop(0)
            for file in files_protected_by_acs:
                msg = msg + ", " + str(file[0])
            messagebox.showinfo("Info", "This access structure is used to protect the following file(s): " + msg)
            return "break"
            # show_graph_from_json(self.root,ac_dict[key])

    def ac_view_structure(self, event, ac_dict):
        btn = event.widget
        new_win = Toplevel()
        new_win.geometry('700x500')
        canvas = Canvas(new_win, bg='white')
        canvas.pack(expand=True, fill='both')
        canvas.update()
        for key in ac_dict.keys():
            if str(btn) in str(key):
                show_graph_from_json(canvas, ac_dict[key])
                new_win.title("Boolean circuit of the " + ac_dict[key].split(".")[0] + " access structure ")
                canvas.bind("<Configure>", lambda x: show_graph_from_json(canvas, ac_dict[key]))
                break

    def ac_remove(self, event, ac_dict):
        btn = event.widget

        for key in ac_dict.keys():
            if str(btn) in str(key):
                print("removing access structure", ac_dict[key])
                self.cursor.execute("SELECT alias from Files where protected=?", (ac_dict[key].split('.')[0],))
                files_protected_by_acs = self.cursor.fetchall()
                if len(files_protected_by_acs) > 0:
                    msg = str(files_protected_by_acs[0][0])
                    files_protected_by_acs.pop(0)
                    for file in files_protected_by_acs:
                        msg = msg + ", " + str(file[0])
                    messagebox.showerror("Error",
                                         "This access structure is used to protect the following file(s): "
                                         + msg + ". Please remove protection before deleting this access structure")
                    return "break"

                else:
                    btn.configure(state=DISABLED)
                    remove(ac_dict[key])
                    messagebox.showinfo("Info", "Access structure removed successfully. Please refresh")
                    return "break"



    def remove_widget_children(self, widget):
        for child in widget.winfo_children():
            child.destroy()
