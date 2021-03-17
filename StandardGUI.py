from os import chdir,startfile
from tkinter import *
from tkinter import messagebox
from BooleanCircuitController import build_bc_from_json
from BooleanCircuitRunner import BooleanCircuitRunner
import sqlite3
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class StandardGui:
    def __init__(self):
        self.root = Tk()
        self.root.geometry('650x500+350+100')
        self.root.title("Access Controlled Files")
        self.connection = sqlite3.connect("AccessControl.db")
        self.cursor = self.connection.cursor()

    def run(self):
        chdir("AccessStructures")
        self.display_files()
        self.root.mainloop()
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
    def display_files(self):
        self.remove_widget_children(self.root)
        self.cursor.execute("SELECT * from Files where protected !=-1")
        files = self.cursor.fetchall()
        f_box_list = []
        f_bts_list = []
        f_view_dict = {}
        if len(files) == 0:
            Label(self.root, text="There are no files to display").pack(pady=10)
        else:

            for file in files:
                f_box_list.append(LabelFrame(self.root))
                f_box_list[-1].pack(fill='both', pady=10, padx=10)
                Label(f_box_list[-1], text="Name: " + file[1], width=20).pack(side=LEFT, padx=10, pady=10)

                f_bts_list.append(Button(f_box_list[-1], text="Open", width=10))
                f_bts_list[-1].pack(side=LEFT, padx=10, ipadx=10)
                f_view_dict[f_bts_list[-1]] = file[3]
                f_bts_list[-1].bind("<Button-1>", lambda x: self.open_file(x, f_view_dict, files))

    def open_file(self, event, f_dict, files):
        btn = event.widget
        # print(f_dict)
        acs=""
        for key in f_dict.keys():
            if str(btn) == str(key):
                # print("cheie",str(key))
                # print("valoare",f_dict[key])#asta ma intereseaza
                # print(pf_params)
                acs=f_dict[key]
                break
        target_file=None
        for file in files:
            if acs == file[3]:
                target_file=file
                break
        request_code_window = Toplevel()
        request_code_window.geometry("300x300+420+120")
        Label(request_code_window, text="Please introduce the access code below").pack()
        code_entry = Entry(request_code_window, show="*")
        code_entry.pack()
        print(target_file)
        Button(request_code_window, text="Enter",
               command=lambda: self.check_access(code_entry.get(), target_file,
                                                 request_code_window)).pack()


    def decrypt_file(self,file_name,file_extension,key_base):
        self.directory_manager('fv')
        print('cheia decriptare',key_base)
        hash_meth = SHA256.new()
        hash_meth.update(key_base.encode())
        key = hash_meth.digest()
        iv = "licenta FII 2021".encode()
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        with open(file_name, "rb") as f:
            crypt_txt = f.read()
        f.close()
        plain_txt = decryptor.decrypt(crypt_txt)
        self.directory_manager('as')
        with open(file_name+'.'+file_extension, "wb") as f:
            f.write(plain_txt.rstrip(b'0'))
        # f.close()

    def check_access(self, user_leafs, pf_params, window):
        self.directory_manager('as')
        user_leafs_list = []
        flag = 1
        if len(user_leafs.strip(' ')) == 0:
            messagebox.showerror("Error", "Empty access code!")
            flag=0
        else:
            for digit in user_leafs:
                if digit.isdigit():
                    user_leafs_list.append(int(digit))
                else:
                    messagebox.showerror("Access denied", "You don't have access to this file")
                    flag = 0
                    break
        if flag == 1:
            self.cursor.execute('SELECT p,y,s from Prime_numbers where file_alias=?', (pf_params[1],))
            primes_list=self.cursor.fetchone()
            bcc = build_bc_from_json(str(pf_params[3]) + ".json")
            bcr = BooleanCircuitRunner("bcr", bcc, user_leafs_list)
            access = bcr.full_run_boolean_circuit(primes_list[0],primes_list[1],primes_list[2])
            if access == 1:
                dec_key=str(primes_list[1])+str(primes_list[2])+str(bcc.root.value_bottom_up)
                self.decrypt_file(pf_params[1],pf_params[4],dec_key)
                window.destroy()
                succes=0
                try:
                    startfile(pf_params[1]+'.'+pf_params[4])
                    succes = 1
                except:
                    messagebox.showerror("Access denied", "You don't have access to this file")
                if succes == 1:
                    messagebox.showinfo("Info", "Access granted. Opening file")
                self.display_files()
            else:
                messagebox.showinfo("Info", "Access denied")

    def remove_widget_children(self, widget):
        for child in widget.winfo_children():
            child.destroy()
