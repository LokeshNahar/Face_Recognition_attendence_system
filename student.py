from ast import Pass
from logging import exception
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import cv2
import mysql.connector
import cv2 as cv
import os




class Student:
    def __init__(self,root):
        self.root=root
        self.root.geometry("1260x750+0+0")
        self.root.title("Student")


        list =["Dep","Course","Year","Sem","Sid","Sname","Gender","Email","Phonenumber","DoB"]

        # ## Variables
        # for name in list:
        #     setattr(self,"var_"+name,StringVar)
        self.var_Dep=StringVar()
        self.var_Course=StringVar()
        self.var_Year=StringVar()
        self.var_Sem=StringVar()
        self.var_Sid=StringVar()
        self.var_Sname=StringVar()
        self.var_Gender=StringVar()
        self.var_Email=StringVar()
        self.var_Phonenumber=StringVar()
        self.var_DoB=StringVar()

        #background image
        imgbg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/Bgimg.webp")
        imgbg=imgbg.resize((1260,750),Image.ANTIALIAS)
        self.photoimgbg =ImageTk.PhotoImage(imgbg)
     
        f_lbl=Label(self.root,image=self.photoimgbg)
        f_lbl.place(x=0,y=0,width=1260,height=750)

        #label text
        title_lbl = Label(self.root,text="STUDENT Management System",font=("chalkboard",30,"bold"),bg="pink",fg="purple")
        title_lbl.place(x=0,y=0,width=1260,height=50)


        #Main Frame
        main_frame=Frame(self.root,bd=2)
        main_frame.place(x=10,y=50,width=1260,height=700)
############################################################################################
        #Left Frame
        Left_frame=LabelFrame(master=main_frame,bd=2,relief=RIDGE,text="Student Details",font=("chalkduster",12,"bold"),bg="yellow",fg="purple")
        Left_frame.place(x=10,y=10,width=600,height=650)
        
        #current course Frame
        CurrentCourse_frame=LabelFrame(master=Left_frame,bd=2,relief=RIDGE,text="Current Course Details",font=("chalkduster",12,"bold"),bg="skyblue",fg="purple")
        CurrentCourse_frame.place(x=2,y=10,width=600,height=150)


        #Department combobox
        dep_label=Label(CurrentCourse_frame,text="Department",font=("chalkduster",12,"bold"),bg="White")
        dep_label.grid(row=0,column=0,padx=10)

        dep_combo=ttk.Combobox(CurrentCourse_frame,textvariable=self.var_Dep,font=("chalkduster",12,"bold"),width=15,state="read only")
        dep_combo["values"]=("Select Department:","CS","EE","CL","ME")
        dep_combo.current(0)
        dep_combo.grid(row=0,column=1,padx=2,pady=10)
        

        #Course combobox
        course_label=Label(CurrentCourse_frame,text="Course",font=("chalkduster",12,"bold"),bg="White")
        course_label.grid(row=0,column=2,padx=10)

        course_combo=ttk.Combobox(CurrentCourse_frame,textvariable=self.var_Course,font=("chalkduster",12,"bold"),width=15,state="read only")
        course_combo["values"]=("Select Course:","B-Tech","M-Tech","Phd")
        course_combo.current(0)
        course_combo.grid(row=0,column=3,padx=2,pady=10)


        #Year combobox
        year_label=Label(CurrentCourse_frame,text="Year",font=("chalkduster",12,"bold"),bg="White")
        year_label.grid(row=1,column=0,padx=10)

        year_combo=ttk.Combobox(CurrentCourse_frame,textvariable=self.var_Year,font=("chalkduster",12,"bold"),width=15,state="read only")
        year_combo["values"]=("Select Year:","2020-21","2021-22","2022-23","2023-24")
        year_combo.current(0)
        year_combo.grid(row=1,column=1,padx=2,pady=10)


        #Semester combobox
        sem_label=Label(CurrentCourse_frame,text="Semester",font=("chalkduster",12,"bold"),bg="White")
        sem_label.grid(row=1,column=2,padx=10)

        sem_combo=ttk.Combobox(CurrentCourse_frame,textvariable=self.var_Sem,font=("chalkduster",12,"bold"),width=15,state="read only")
        sem_combo["values"]=("Select Semester:","Monsoon Sem","Summer Sem")
        sem_combo.current(0)
        sem_combo.grid(row=1,column=3,padx=2,pady=10)
        


        #######################
        #Class Student Information Frame
        classstudent_frame=LabelFrame(master=Left_frame,bd=2,relief=RIDGE,text="Class Student Information",font=("chalkduster",12,"bold"),bg="skyblue",fg="purple")
        classstudent_frame.place(x=2,y=170,width=600,height=400)
        
        #Student Id
        studentid_label=Label(classstudent_frame,text="Student ID",font=("chalkduster",12,"bold"),bg="white")
        studentid_label.grid(row=0,column=0,padx=10,pady=5,sticky=W)
        studentid_entry = ttk.Entry(classstudent_frame,textvariable=self.var_Sid,width=15,font=("chalkduster",12,"bold"))
        studentid_entry.grid(row=0,column=1,padx=2,pady=5,sticky=W)

        #Student name
        studentname_label=Label(classstudent_frame,text="Name",font=("chalkduster",12,"bold"),bg="white")
        studentname_label.grid(row=0,column=2,padx=10,pady=5,sticky=W)
        studentname_entry = ttk.Entry(classstudent_frame,textvariable=self.var_Sname,width=15,font=("chalkduster",12,"bold"))
        studentname_entry.grid(row=0,column=3,padx=2,pady=5,sticky=W)

        #Student Gender
        Gender_label=Label(classstudent_frame,text="Gender",font=("chalkduster",12,"bold"),bg="white")
        Gender_label.grid(row=1,column=0,padx=10,pady=5,sticky=W)

        gender_combo=ttk.Combobox(classstudent_frame,textvariable=self.var_Gender,font=("chalkduster",12,"bold"),width=15,state="read only")
        gender_combo["values"]=("select Gender:","Male","Female","others")
        gender_combo.current(0)
        gender_combo.grid(row=1,column=1,padx=2,pady=10)

        #Student email
        email_label=Label(classstudent_frame,text="E-mail",font=("chalkduster",12,"bold"),bg="white")
        email_label.grid(row=1,column=2,padx=10,pady=5,sticky=W)
        email_entry = ttk.Entry(classstudent_frame,textvariable=self.var_Email,width=15,font=("chalkduster",12,"bold"))
        email_entry.grid(row=1,column=3,padx=2,pady=5,sticky=W)

        #Student phone number
        phoneno_label=Label(classstudent_frame,text="Phone Number",font=("chalkduster",12,"bold"),bg="white")
        phoneno_label.grid(row=2,column=0,padx=10,pady=5,sticky=W)
        phoneno_entry = ttk.Entry(classstudent_frame,textvariable=self.var_Phonenumber,width=15,font=("chalkduster",12,"bold"))
        phoneno_entry.grid(row=2,column=1,padx=2,pady=5,sticky=W)
        
        #Date-of-Birth
        dob_label=Label(classstudent_frame,text="Date-of-Birth",font=("chalkduster",12,"bold"),bg="white")
        dob_label.grid(row=2,column=2,padx=10,pady=5,sticky=W)
        dob_entry = ttk.Entry(classstudent_frame,textvariable=self.var_DoB,width=15,font=("chalkduster",12,"bold"))
        dob_entry.grid(row=2,column=3,padx=2,pady=5,sticky=W)

        #Radiobuttons
        self.var_radio1=StringVar()
        radiobutton1= ttk.Radiobutton(classstudent_frame,variable=self.var_radio1,text="Take Photo Sample",value="Yes")
        radiobutton1.grid(row=3,column=0,padx=2,pady=5)
        
        radiobutton2= ttk.Radiobutton(classstudent_frame,variable=self.var_radio1,text="NO Photo Sample",value="No")
        radiobutton2.grid(row=3,column=1,padx=2,pady=5)


        # Buttons Frame
        btn_frame = Frame(classstudent_frame,bd=2,relief=RIDGE,bg="light green")
        btn_frame.place(x=0,y=160,width=600,height=200)

        save_btn=Button(btn_frame,text="Save",command=self.add_data,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        save_btn.grid(row=0,column=0)

        update_btn=Button(btn_frame,text="Update",command=self.update_data,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        update_btn.grid(row=0,column=1)

        delete_btn=Button(btn_frame,text="Delete",command=self.delete_data,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        delete_btn.grid(row=0,column=2)

        Reset_btn=Button(btn_frame,text="Reset",command=self.reset_data,width=16,height=2 ,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        Reset_btn.grid(row=0,column=3)

        Take_photo_btn=Button(btn_frame,text="Take Photo Sample",command=self.generate_dataset,width=16,height=3,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        Take_photo_btn.grid(row=1,column=1)

        Update_photo_btn=Button(btn_frame,text="Update Photo Sample",width=16,height=3,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        Update_photo_btn.grid(row=1,column=2)





############################################################
        #Right Frame
        Right_frame=LabelFrame(main_frame,bd=2,relief=RIDGE,text="Student Details",font=("chalkduster",12,"bold"),bg="pink",fg="purple")
        Right_frame.place(x=610,y=10,width=600,height=650)

        #search frame
        search_frame=LabelFrame(Right_frame,bd=2,relief=RIDGE,text="Search System",font=("chalkduster",12,"bold"),bg="yellow",fg="purple")
        search_frame.place(x=2,y=10,width=580,height=75)

        search_label=Label(search_frame,text="Search by:",font=("chalkduster",12,"bold"),bg="white")
        search_label.grid(row=0,column=0,padx=2,pady=5,sticky=W)

        search_combo=ttk.Combobox(search_frame,font=("chalkduster",12,"bold"),width=10,state="read only")
        search_combo["values"]=("select :","Student ID","Phone_no")
        search_combo.current(0)
        search_combo.grid(row=0,column=1,padx=2,pady=10)

        search_entry = ttk.Entry(search_frame,width=15,font=("chalkduster",12,"bold"))
        search_entry.grid(row=0,column=2,padx=2,pady=5,sticky=W)

        search_btn=Button(search_frame,text="Search",width=10,height=3,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        search_btn.grid(row=0,column=3,padx=4)

        showall_btn=Button(search_frame,text="Showall",width=10,height=3,font=("chalkduster",12,"bold"),bg="skyblue",fg="green",cursor="hand")
        showall_btn.grid(row=0,column=4,padx=4)



        #table frame
        table_frame=Frame(Right_frame,bd=2,relief=RIDGE,bg="lightgreen")
        table_frame.place(x=2,y=100,width=580,height=250)

        scroll_x=ttk.Scrollbar(table_frame,orient=HORIZONTAL)
        scroll_y=ttk.Scrollbar(table_frame,orient=VERTICAL)

        self.student_table=ttk.Treeview(table_frame,column=("Dep","Course","Year","Sem","Sid","Sname","Gender","Email","Phonenumber","DoB","Photo"),xscrollcommand=scroll_x.set,yscrollcommand=scroll_y.set)

        scroll_x.pack(side=BOTTOM,fill=X)
        scroll_y.pack(side=RIGHT,fill=Y)
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        for j in list:
            self.student_table.heading(j,text=j)
        self.student_table.heading("Photo",text="Photo")
        self.student_table["show"]="headings"

        self.student_table.pack(fill=BOTH,expand=1)
        for j in list:
            self.student_table.column(j,width=100)
        self.student_table.column("Photo",width=150)

        self.student_table.bind("<ButtonRelease>",self.get_cursor)
        self.fetch_data()

################################################################
##     functions    ##

    def add_data(self):
        if self.var_Dep.get()=="Select Department:" or self.var_Sid.get()=="" or self.var_Email.get()=="":
            messagebox.showerror("Error", "All fields are required",parent=self.root) 
        else:
            try:
                conn=mysql.connector.connect(host="localhost",username="root",password="allaboutenergy&practise",database="face_recognixer")
                my_cursor=conn.cursor()
                my_cursor.execute("insert into student values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                                                            self.var_Dep.get(),
                                                            self.var_Course.get(),
                                                            self.var_Year.get(),
                                                            self.var_Sem.get(),
                                                            self.var_Sid.get(),
                                                            self.var_Sname.get(),
                                                            self.var_Gender.get(),
                                                            self.var_Email.get(),
                                                            self.var_Phonenumber.get(),
                                                            self.var_DoB.get(),
                                                            self.var_radio1.get()
                                                        ))
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Success","Student added",parent=self.root)
            except Exception as es:
                messagebox.showerror("Error",f"Due to :{str(es)} ",parent=self.root)



    def fetch_data(self):
        conn=mysql.connector.connect(host="localhost",username="root",password="allaboutenergy&practise",database="face_recognixer")
        my_cursor=conn.cursor()
        my_cursor.execute("select * from student")
        data=my_cursor.fetchall()

        if len(data)!=0:
            self.student_table.delete(*self.student_table.get_children())
            for i in data:
                self.student_table.insert("",END,values=i)
            conn.commit()
        conn.close()


    def get_cursor(self,event=""):
        cursor_focus=self.student_table.focus()
        content=self.student_table.item(cursor_focus)
        data = content["values"]

        self.var_Dep.set(data[0]),
        self.var_Course.set(data[1]),
        self.var_Year.set(data[2]),
        self.var_Sem.set(data[3]),
        self.var_Sid.set(data[4]),
        self.var_Sname.set(data[5]),
        self.var_Gender.set(data[6]),
        self.var_Email.set(data[7]),
        self.var_Phonenumber.set(data[8]),
        self.var_DoB.set(data[9]),
        self.var_radio1.set(data[10])


    def update_data(self):
        if self.var_Dep.get()=="Select Department:":
            messagebox.showerror("Error", "All fields are required",parent=self.root) 
        else:
            try:
                update=messagebox.askyesno("Update","Do you wanna update",parent=self.root)
                if  update>0:
                    conn=mysql.connector.connect(host="localhost",username="root",password="allaboutenergy&practise",database="face_recognixer")
                    my_cursor=conn.cursor()
                    my_cursor.execute("update student set Dep=%s,Course=%s,Year=%s,Semester=%s,Sname=%s,Gender=%s,Email=%s,Phonenumber=%s,DoB=%s,Photosample=%s where Sid=%s",(
                                                            self.var_Dep.get(),
                                                            self.var_Course.get(),
                                                            self.var_Year.get(),
                                                            self.var_Sem.get(),
                                                            self.var_Sname.get(),
                                                            self.var_Gender.get(),
                                                            self.var_Email.get(),
                                                            self.var_Phonenumber.get(),
                                                            self.var_DoB.get(),
                                                            self.var_radio1.get(),
                                                            self.var_Sid.get()           

                                                     ))
                else:
                    if not update:
                        return
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Success","Update complete",parent = self.root)     
                
            except exception as es:
                messagebox.showerror("Error",f"Due to: {str(es)}",parent=self.root)
                


    def delete_data(self):
        if self.var_Sid.get()=="":
            messagebox.showerror("Error","Sid required!",parent=self.root)
        else:
            try:
                delete=messagebox.askyesno("Delete page","Do you want to delete",parent=self.root)
                if delete>0:
                    conn=mysql.connector.connect(host="localhost",username="root",password="allaboutenergy&practise",database="face_recognixer")
                    my_cursor=conn.cursor()
                    val=(self.var_Sid.get(),)
                    my_cursor.execute("delete from student where Sid=%s",val)
                else:
                    if not delete:
                        return
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("delete","deleted sucessfully", parent=self.root)
            except exception as es:
                messagebox.showerror("Error",f"Due to {str(es)}", parent=self.root)


    def reset_data(self):
        self.var_Dep.set("Select Department:"),
        self.var_Course.set("Select Course"),
        self.var_Year.set("Select Year"),
        self.var_Sem.set("Select Semester"),
        self.var_Sid.set(""),
        self.var_Sname.set(""),
        self.var_Gender.set("select Gender"),
        self.var_Email.set(""),
        self.var_Phonenumber.set(""),
        self.var_DoB.set(""),
        self.var_radio1.set("")


    def generate_dataset(self):
            try:
                conn=mysql.connector.connect(host="localhost",username="root",password="allaboutenergy&practise",database="face_recognixer")
                my_cursor=conn.cursor()
                my_cursor.execute("select * from student")
                myresult=my_cursor.fetchall()
                id=0
                for x in myresult:
                    id+=1
                    my_cursor.execute("update student set Dep=%s,Course=%s,Year=%s,Semester=%s,Sname=%s,Gender=%s,Email=%s,Phonenumber=%s,DoB=%s,Photosample=%s where Sid=%s",(
                                                            self.var_Dep.get(),
                                                            self.var_Course.get(),
                                                            self.var_Year.get(),
                                                            self.var_Sem.get(),
                                                            self.var_Sname.get(),
                                                            self.var_Gender.get(),
                                                            self.var_Email.get(),
                                                            self.var_Phonenumber.get(),
                                                            self.var_DoB.get(),
                                                            self.var_radio1.get(),
                                                            self.var_Sid.get() ==id+1           

                                                        ))  

                conn.commit()  
                self.fetch_data()
                self.reset_data()
                conn.close()    


                face_classifier=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                
                def face_cropped(img):
                    gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
                    faces=face_classifier.detectMultiScale(gray,1.3,5)

                    for (x,y,w,h) in faces:
                        face_cropped=img[y:y+h,x:x+w]
                        return face_cropped

                capture=cv.VideoCapture(0)
                image_id=0
                while True:
                    ret, my_frame=capture.read()
                    if face_cropped(my_frame) is not None:
                        image_id+=1
                        face=cv.resize(face_cropped(my_frame),(450,450))
                        face=cv.cvtColor(face,cv.COLOR_BGR2GRAY)
                        File_path="/Users/lokeshnahar/Desktop/Engage/Image_data/user."+str(id)+"."+str(image_id)+".jpg"
                        cv.imwrite(File_path,face)
                        cv.putText(face,str(image_id),(50,50),cv.FONT_HERSHEY_COMPLEX,2,(0,255,0),2)
                        cv.imshow("Cropped Face",face)
                         
                    if cv.waitKey(1)==13 or int(image_id)==100:
                        break
                capture.release()
                cv.destroyAllWindows()
                messagebox.showinfo("Result","Generating Dataset Competed!",parent=self.root)    
            
            
            
            
            except exception as es:
                messagebox.showerror("Error",f"Due to:{es}",parent=self.root)



if __name__ == "__main__":
    root = Tk()
    obj = Student(root)
    root.mainloop()