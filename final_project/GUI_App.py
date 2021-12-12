#for ubuntu:
#sudo apt-get install python3-tk
import tkinter as tk
from tkinter import scrolledtext

class GUI_App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Welcome to DC2")
        self.geometry('725x575')


        # FRAMES / LAYOUT
        self.frame_main = tk.Frame(self)
        self.frame_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.frame_bottom = tk.Frame(self, bd=2)
        self.frame_bottom.pack(padx=10)

        self.frame_footer = tk.Frame(self, bd=2, relief="groove", bg="lightgrey")
        self.frame_footer.pack(pady=10, ipadx=3, ipady=3)


        self.frame_bottom_0 = tk.Frame(self.frame_bottom, bd=2, relief="groove", bg="lightgrey")
        self.frame_bottom_0.grid(column=0, row=0, ipadx=3, ipady=3, padx=6, pady=6)

        self.frame_bottom_1 = tk.Frame(self.frame_bottom, bd=2, relief="groove", bg="lightgrey")
        self.frame_bottom_1.grid(column=1, row=0, ipadx=3, ipady=3, padx=6, pady=6)

        #self.frame_bottom_2 = tk.Frame(self.frame_bottom, bd=2, relief="groove", bg="lightgrey")
        #self.frame_bottom_2.grid(column=2, row=0, ipadx=3, ipady=3, padx=6, pady=6)

        


        # STATUS BOX
        self.output_txt = scrolledtext.ScrolledText(self.frame_main, width=40, height=15)
        self.output_txt.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.output_txt.insert(tk.INSERT, 'Welcome!!\n')
        self.output_txt.configure(state = tk.DISABLED)


        # SEND MESSAGE IP
        self.ip_label = tk.Label(self.frame_bottom_0, text="IP Address:", bg="lightgrey")
        self.ip_label.grid(column=0, row=0, sticky=tk.E, pady=10)
        
        self.ip_entry = tk.Entry(self.frame_bottom_0, width=30)
        self.ip_entry.grid(column=1, row=0, sticky=tk.W)

        self.message_label = tk.Label(self.frame_bottom_0, text="Message:", bg="lightgrey")
        self.message_label.grid(column=0, row=1, sticky=tk.E)

        self.message_entry = tk.Text(self.frame_bottom_0, width=30, height=3)
        self.message_entry.grid(column=1, row=1, sticky=tk.W)

        self.send_button = tk.Button(self.frame_bottom_0, text="Send Message to IP", bg="green", fg="white")
        self.send_button.grid(column=0, row=2, columnspan=2, pady=10)


        # SEND MESSAGE GROUP
        self.group_label = tk.Label(self.frame_bottom_1, text="Group:", bg="lightgrey")
        self.group_label.grid(column=0, row=0, sticky=tk.E, pady=10)
        
        self.group_entry = tk.Entry(self.frame_bottom_1, width=25)
        self.group_entry.grid(column=1, row=0, sticky=tk.W)

        self.group_message_label = tk.Label(self.frame_bottom_1, text="Group Message:", bg="lightgrey")
        self.group_message_label.grid(column=0, row=1, sticky=tk.E)

        self.group_message_entry = tk.Text(self.frame_bottom_1, width=30, height=3)
        self.group_message_entry.grid(column=1, row=1, sticky=tk.W)

        self.send_group_message_button = tk.Button(self.frame_bottom_1, text="Send Message to group", bg="green", fg="white")
        self.send_group_message_button.grid(column=0, row=2, columnspan=2, pady=10)


        # JOIN / LEAVE GROUP
        self.group_label = tk.Label(self.frame_footer, text="Group:", bg="lightgrey")
        self.group_label.grid(column=0, row=0, sticky=tk.E, pady=10)
        
        self.group_membership_entry = tk.Entry(self.frame_footer, width=25)
        self.group_membership_entry.grid(column=1, row=0, sticky=tk.W)

        self.join_group_button = tk.Button(self.frame_footer, text="Join Group", bg="darkblue", fg="white")
        self.join_group_button.grid(column=1, row=2, sticky=tk.W)

        self.leave_group_button = tk.Button(self.frame_footer, text="Leave Group", bg="red", fg="white")
        self.leave_group_button.grid(column=1, row=2, sticky=tk.E)
    

    def append_output(self, message_string):
        self.output_txt.configure(state = tk.NORMAL)
        self.output_txt.insert(tk.INSERT, "\n{0}\n".format(message_string))
        self.output_txt.configure(state = tk.DISABLED)

    def display_neighbors(self, neighbors):
        self.output_txt.configure(state = tk.NORMAL)
        self.output_txt.delete("1.0", "end-1c")
        self.output_txt.insert(tk.INSERT, "\n".join(neighbors))
        self.output_txt.configure(state = tk.DISABLED)
        

#def main():
#    gui = GUI_App()
#    gui.mainloop()
#if __name__ == '__main__':
#    main()
