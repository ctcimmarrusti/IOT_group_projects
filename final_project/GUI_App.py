#for ubuntu:
#sudo apt-get install python3-tk
import tkinter as tk
from tkinter import scrolledtext

class GUI_App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Welcome to DC2")
        self.geometry('850x400')


        self.frame_main = tk.Frame(self)
        self.frame_main.pack(fill=tk.BOTH, expand=True)

        self.output_txt = scrolledtext.ScrolledText(self.frame_main, width=40, height=15)
        self.output_txt.pack(fill=tk.BOTH, expand=True)
        self.output_txt.insert(tk.INSERT, 'Welcome!!\n')
        self.output_txt.configure(state = tk.DISABLED)



        self.frame_bottom = tk.Frame(self)
        self.frame_bottom.pack()

        self.ip_label = tk.Label(self.frame_bottom, text="IP Address:")
        self.ip_label.grid(column=0, row=0, sticky=tk.E, pady=10)
        
        self.ip_entry_var = tk.StringVar()
        self.ip_entry = tk.Entry(self.frame_bottom, textvariable=self.ip_entry_var, width=40)
        self.ip_entry.grid(column=1, row=0, sticky=tk.W)



        self.message_label = tk.Label(self.frame_bottom, text="Message:")
        self.message_label.grid(column=0, row=1, sticky=tk.E)

        self.message_entry_var = tk.StringVar()
        self.message_entry = tk.Text(self.frame_bottom, width=30, height=3)
        self.message_entry.grid(column=1, row=1, sticky=tk.W)
        #self.message_entry = tk.Entry(self.frame_bottom, textvariable=self.message_entry_var, width=40)
        #self.message_entry.grid(column=1, row=1)
        


        self.send_button = tk.Button(self.frame_bottom, text="Send", bg="green", fg="white")
        self.send_button.grid(column=0, row=2, columnspan=2, pady=10)
    
    def append_output(self, message_string):
        self.output_txt.configure(state = tk.NORMAL)
        self.output_txt.insert(tk.INSERT, "\n{0}\n".format(message_string))
        self.output_txt.configure(state = tk.DISABLED)
        

#def main():
#	gui = GUI_App()
#	gui.mainloop()
#if __name__ == '__main__':
#	main()
