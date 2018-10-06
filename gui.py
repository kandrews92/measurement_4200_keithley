from Tkinter import *
root1 = tk.Tk()
label = tk.Label(root1, text="ourlabel")
entry = tk.Entry(root1)
label.pack(side=tk.TOP)
entry.pack()
root1.mainloop()