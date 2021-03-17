from tkinter import *

root = Tk()
top = Toplevel()
top.withdraw()
var1 = StringVar(root)
var1.set("top")
var2 = StringVar(root)
var2.set("none")
var4 = StringVar(root)
var4.set("center")
var3 = BooleanVar(root)

def command(top, var1, var3, var2):
    top.destroy()
    top = Toplevel()
    top.geometry("500x500")
    Label(top, text="Welcome home").pack()
    Button(top, text="Button1").pack(side=var1.get(), fill=var2.get(), expand=var3.get(), anchor=var4.get())
    Button(top, text="Button2").pack(side=var1.get(), fill=var2.get(), expand=var3.get(), anchor=var4.get())
    Button(top, text="Button3").pack(side=var1.get(), fill=var2.get(), expand=var3.get(), anchor=var4.get())
    Button(top, text="Button4").pack(side=var1.get(), fill=var2.get(), expand=var3.get(), anchor=var4.get())

option1 = OptionMenu(root, var1, "top", "left", "bottom", "right")
check1 = Checkbutton(root, variable=var3, text="Expand?")
option2 = OptionMenu(root, var2, "none", "x", "y", "both")
option3 = OptionMenu(root, var4, "center", "n", "ne", "e", "se", "s", "sw", "w", "nw")
button1 = Button(root, text="Render", command=lambda:command(top, var1, var3, var2))

option1.pack()
check1.pack()
option2.pack()
option3.pack()
button1.pack()

root.mainloop()