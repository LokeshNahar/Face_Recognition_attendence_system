from hmac import new
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import mysql.connector
import cv2 as cv
import os
import csv
from tkinter import filedialog


Mydata=[]
class Attendence:
    def __init__(self,root):
        self.root=root
        self.root.geometry("1260x750+0+0")
        self.root.title("Attendence")


        self.var_atten_id = StringVar()
        self.var_atten_name = StringVar()
        self.var_atten_email = StringVar()
        self.var_atten_dep = StringVar()
        self.var_atten_time = StringVar()
        self.var_atten_date = StringVar()
        self.var_atten_attendance =StringVar()


         #background image
        imgbg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/Bgimg.webp")
        imgbg=imgbg.resize((1260,750),Image.ANTIALIAS)
        self.photoimgbg =ImageTk.PhotoImage(imgbg)
     
        f_lbl=Label(self.root,image=self.photoimgbg)
        f_lbl.place(x=0,y=0,width=1260,height=750)

        #label text
        title_lbl = Label(self.root,text="Attendence Matters!",font=("chalkduster",30,"bold"),bg="pink",fg="purple")
        title_lbl.place(x=0,y=0,width=1260,height=50)

        #Main Frame
        main_frame=Frame(self.root,bd=2)
        main_frame.place(x=10,y=50,width=1260,height=700)

        #Left Frame
        Left_frame=LabelFrame(master=main_frame,bd=2,relief=RIDGE,text="attendence Attendence Details",font=("chalkduster",12,"bold"),bg="yellow",fg="purple")
        Left_frame.place(x=10,y=10,width=600,height=650)


        #attendence Id
        attendenceid_label=Label(Left_frame,text="attendence ID",font=("chalkduster",12,"bold"),bg="white")
        attendenceid_label.grid(row=0,column=0,padx=10,pady=5,sticky=W)
        attendenceid_entry = ttk.Entry(Left_frame,textvariable=self.var_atten_id,width=15,font=("chalkduster",12,"bold"))
        attendenceid_entry.grid(row=0,column=1,padx=2,pady=5,sticky=W)

        #attendence name
        attendencename_label=Label(Left_frame,text="Name",font=("chalkduster",12,"bold"),bg="white")
        attendencename_label.grid(row=0,column=2,padx=10,pady=5,sticky=W)
        attendencename_entry = ttk.Entry(Left_frame,textvariable=self.var_atten_name,width=15,font=("chalkduster",12,"bold"))
        attendencename_entry.grid(row=0,column=3,padx=2,pady=5,sticky=W)

        #attendence Department
        Dep_label=Label(Left_frame,text="Department :",font=("chalkduster",12,"bold"),bg="white")
        Dep_label.grid(row=1,column=0,padx=10,pady=5,sticky=W)

        Dep_combo=ttk.Combobox(Left_frame,textvariable=self.var_atten_dep,font=("chalkduster",12,"bold"),width=15,state="read only")
        Dep_combo["values"]=("select Department:","CS","ME","CL","EE")
        Dep_combo.current(0)
        Dep_combo.grid(row=1,column=1,padx=2,pady=10)

        #attendence email
        email_label=Label(Left_frame,text="E-mail",font=("chalkduster",12,"bold"),bg="white")
        email_label.grid(row=1,column=2,padx=10,pady=5,sticky=W)
        email_entry = ttk.Entry(Left_frame,textvariable=self.var_atten_email,width=15,font=("chalkduster",12,"bold"))
        email_entry.grid(row=1,column=3,padx=2,pady=5,sticky=W)

        #Time
        Time_label=Label(Left_frame,text="Time",font=("chalkduster",12,"bold"),bg="white")
        Time_label.grid(row=2,column=0,padx=10,pady=5,sticky=W)
        Time_entry = ttk.Entry(Left_frame,textvariable=self.var_atten_time,width=15,font=("chalkduster",12,"bold"))
        Time_entry.grid(row=2,column=1,padx=2,pady=5,sticky=W)
        
        #Date
        Date_label=Label(Left_frame,text="Date",font=("chalkduster",12,"bold"),bg="white")
        Date_label.grid(row=2,column=2,padx=10,pady=5,sticky=W)
        Date_entry = ttk.Entry(Left_frame,textvariable=self.var_atten_date,width=15,font=("chalkduster",12,"bold"))
        Date_entry.grid(row=2,column=3,padx=2,pady=5,sticky=W)

        #Attendence
        attendence_label=Label(Left_frame,text="Attendence",font=("chalkduster",12,"bold"),bg="white")
        attendence_label.grid(row=3,column=1,padx=10,pady=5,sticky=W)
        attendence_entry = ttk.Entry(Left_frame,textvariable=self.var_atten_attendance,width=15,font=("chalkduster",12,"bold"))
        attendence_entry.grid(row=3,column=2,padx=2,pady=5,sticky=W)



        #Buttons
        # Buttons Frame
        btn_frame = Frame(Left_frame,bd=2,relief=RIDGE,bg="light green")
        btn_frame.place(x=0,y=160,width=600,height=60)

        import_btn=Button(btn_frame,text="Import CSV",command=self.import_csv,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        import_btn.grid(row=0,column=0)

        export_btn=Button(btn_frame,text="Export CSV",command=self.export_csv,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        export_btn.grid(row=0,column=1)

        update_btn=Button(btn_frame,text="Update",width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        update_btn.grid(row=0,column=2)

        Reset_btn=Button(btn_frame,text="Reset",command=self.reset_data,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        Reset_btn.grid(row=0,column=3)

       




        #Right Frame
        Right_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Attendence Details",font=("chalkduster",12,"bold"),bg="pink",fg="purple")
        Right_frame.place(x=610,y=10,width=600,height=650)



        #table frame
        table_frame=Frame(Right_frame,bd=2,relief=RIDGE,bg="lightgreen")
        table_frame.place(x=2,y=10,width=580,height=250)

        scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)

        self.attendence_table=ttk.Treeview(table_frame,column=("Sid","Sname","Department","Email","Time","Date","Attendence"),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)
        scroll_x.config(command=self.attendence_table.xview)
        scroll_y.config(command=self.attendence_table.yview)

        list=["Sid","Sname","Email","Department","Time","Date","Attendence"]

        for j in list:
            self.attendence_table.heading(j,text=j)
        self.attendence_table["show"]="headings"

        self.attendence_table.pack(fill=BOTH,expand=1)
        for j in list:
            self.attendence_table.column(j,width=100)

        self.attendence_table.bind("<ButtonRelease>",self.get_cursor)
        # self.fetch_data()


    def fetch_data(self,rows):
        self.attendence_table.delete(*self.attendence_table.get_children())
        for i in rows:
            self.attendence_table.insert("",END,values=i)

    def import_csv(self):
        global Mydata
        filename=filedialog.askopenfilename(initialdir=os.getcwd(),title="Open CSV",filetypes=(("CSV File","*.csv"),("ALL File","*.*")),parent=self.root)
        with open(filename) as myfile:
            csvread=csv.reader(myfile,delimiter=",")
            for i in csvread:
                Mydata.append(i)
            self.fetch_data(Mydata)


    def export_csv(self):
        try:
            if len(Mydata)<1:
                messagebox.showerror("no error","No Data Available",parent=self.root)
                return False
            filename=filedialog.asksaveasfilename(initialdir=os.getcwd(),title="Open CSV",filetypes=(("CSV File","*.csv"),("ALL File","*.*")),parent=self.root)
            with open(filename,"w",newline="") as myfile:
                exp_write=csv.writer(myfile,delimiter=",")
                for i in Mydata:
                    exp_write.writerow(i)
                messagebox.showinfo("success","Your data exported to "+os.path.basename(filename)+" successfully",parent=self.root)
        except Exception as es:
            messagebox.showerror("Error",f"Due to: {str(es)}",parent=self.root)

    
    def get_cursor(self,event=""):
        cursor_focus=self.attendence_table.focus()
        content=self.attendence_table.item(cursor_focus)
        rows = content["values"]

        self.var_atten_id.set(rows[0])
        self.var_atten_name.set(rows[1])
        self.var_atten_email.set(rows[2])
        self.var_atten_dep.set(rows[3])
        self.var_atten_time.set(rows[4])
        self.var_atten_date.set(rows[5])
        self.var_atten_attendance.set(rows[6])


    def reset_data(self):
        self.var_atten_id.set("")
        self.var_atten_name.set("")
        self.var_atten_email.set("")
        self.var_atten_dep.set("Select Department:")
        self.var_atten_time.set("")
        self.var_atten_date.set("")
        self.var_atten_attendance.set("")


if __name__ == "__main__":
    root = Tk()
    obj = Attendence(root)
    root.mainloop()