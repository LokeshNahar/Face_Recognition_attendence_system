from tkinter import *
from tkinter import ttk
import tkinter
from tkinter import messagebox
from PIL import Image,ImageTk
import os
from time import strftime
from datetime import datetime
from student import Student
from train import Train
from face_recognition import Face_recognition
from attendence import Attendence
from developer import Developer



class Face__Recognition_System:
    def __init__(self,root):
        self.root=root
        self.root.geometry("1260x750+0+0")
        self.root.title("Face Recognition Attendence Management")


        #background image
        imgbg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/Bgimg.webp")
        imgbg=imgbg.resize((1260,750),Image.ANTIALIAS)
        self.photoimgbg =ImageTk.PhotoImage(imgbg)
     
        f_lbl=Label(self.root,image=self.photoimgbg)
        f_lbl.place(x=0,y=0,width=1260,height=750)


        #labelimage
        imglabel=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/labelbg.jpg")
        imglabel=imglabel.resize((311,146),Image.ANTIALIAS)
        self.photoimglbl =ImageTk.PhotoImage(imglabel)
      
        f_lbl1=Label(self.root,image=self.photoimglbl)
        f_lbl1.place(x=-1,y=0,width=311,height=146)
 

        #label text
        title_lbl = Label(self.root,text="~~ Lokesh Nahar, IIT Guwahati",font=("chalkboard",25,"bold"),bg="pink",fg="purple")
        title_lbl.place(x=810,y=675,width=450,height=75)
        


        #student button
        imgstudent=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/student.jpg")
        imgstudent=imgstudent.resize((150,150),Image.ANTIALIAS)
        self.photoimgstudent =ImageTk.PhotoImage(imgstudent)
        
        button_s = Button(self.root,image= self.photoimgstudent,command=self.student_details,cursor="hand2")
        button_s.place(x=200,y=200,width=150,height=150)
        
        button_s_s=Button(self.root,text="Student Details",command=self.student_details,cursor="hand2",font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_s_s.place(x=200,y=350,width=150,height=40)


        #Detect Face Button
        imgdetect=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/detect.jpg")
        imgdetect=imgdetect.resize((150,150),Image.ANTIALIAS)
        self.photoimgdetect =ImageTk.PhotoImage(imgdetect)
        
        button_f = Button(self.root,image= self.photoimgdetect,cursor="hand2",command=self.face_data)
        button_f.place(x=400,y=200,width=150,height=150)
        
        button_f_f=Button(self.root,text="Face Detector",cursor="hand2",command=self.face_data,font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_f_f.place(x=400,y=350,width=150,height=40)


        #attendence button
        imgattendence=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/attendence.jpg")
        imgattendence=imgattendence.resize((150,150),Image.ANTIALIAS)
        self.photoimgattendence =ImageTk.PhotoImage(imgattendence)
        
        button_a = Button(self.root,image= self.photoimgattendence,cursor="hand2",command=self.attendence)
        button_a.place(x=600,y=200,width=150,height=150)
        
        button_a_a=Button(self.root,text="Attendence",cursor="hand2",command=self.attendence,font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_a_a.place(x=600,y=350,width=150,height=40)



        #train face button
        imgtrainface=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/trainface.jpg")
        imgtrainface=imgtrainface.resize((150,150),Image.ANTIALIAS)
        self.photoimgtrainface =ImageTk.PhotoImage(imgtrainface)
        
        button_t = Button(self.root,image= self.photoimgtrainface,cursor="hand2",command=self.training_data)
        button_t.place(x=800,y=200,width=150,height=150)
        
        button_t_t=Button(self.root,text="Trainface",cursor="hand2",command=self.training_data,font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_t_t.place(x=800,y=350,width=150,height=40)


        #Photos button
        imgphotos=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/attendence.jpg")
        imgphotos=imgphotos.resize((150,150),Image.ANTIALIAS)
        self.photoimgphotos =ImageTk.PhotoImage(imgphotos)
        
        button_p = Button(self.root,image= self.photoimgphotos,cursor="hand2",command=self.open_img)
        button_p.place(x=200,y=460,width=150,height=150)
        
        button_p_p=Button(self.root,text="Photos",cursor="hand2",command=self.open_img,font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_p_p.place(x=200,y=600,width=150,height=40)


        #Developer button
        imgDeveloper=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/developer.jpg")
        imgDeveloper=imgDeveloper.resize((150,150),Image.ANTIALIAS)
        self.photoimgDeveloper =ImageTk.PhotoImage(imgDeveloper)
        
        button_d = Button(self.root,image= self.photoimgDeveloper,cursor="hand2",command=self.developer)
        button_d.place(x=400,y=460,width=150,height=150)
        
        button_d_d=Button(self.root,text="Developer",cursor="hand2",command=self.developer,font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_d_d.place(x=400,y=600,width=150,height=40)


        #Exit button
        imgExit=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/exit.jpg")
        imgExit=imgExit.resize((150,150),Image.ANTIALIAS)
        self.photoimgExit =ImageTk.PhotoImage(imgExit)
        
        button_e = Button(self.root,image= self.photoimgExit,cursor="hand2",command=self.iexit)
        button_e.place(x=600,y=460,width=150,height=150)
        
        button_e_e=Button(self.root,text="Exit",cursor="hand2",command=self.iexit,font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_e_e.place(x=600,y=600,width=150,height=40)



        #Contactus button
        imgContactUs=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/contactus.jpg")
        imgContactUs=imgContactUs.resize((150,150),Image.ANTIALIAS)
        self.photoimgContactUs =ImageTk.PhotoImage(imgContactUs)
        
        button_c = Button(self.root,image= self.photoimgContactUs,cursor="hand2")
        button_c.place(x=800,y=460,width=150,height=150)
        
        button_c_c=Button(self.root,text="ContactUs",cursor="hand2",font=("times new roman",15,"bold"),bg="blue",fg="blue")
        button_c_c.place(x=800,y=600,width=150,height=40)





    def open_img(self):
        pass


    def iexit(self):
        self.iexit=messagebox.askyesno("Exit","Thank you for using this Project::Are you Sure you wanna exit",parent=self.root)
        if self.iexit>0:
            self.root.destroy()
        else:
            return
############################################################
##                        Functions                       ##
    def student_details(self):
        self.new_window=Toplevel(self.root)
        self.app=Student(self.new_window)

    def training_data(self):
        self.new_window=Toplevel(self.root)
        self.app=Train(self.new_window)  

    def face_data(self):
        self.new_window=Toplevel(self.root)
        self.app=Face_recognition(self.new_window)        

    def attendence(self):
        self.new_window=Toplevel(self.root)
        self.app=Attendence(self.new_window) 

    def developer(self):
        self.new_window=Toplevel(self.root)
        self.app=Developer(self.new_window)    







if __name__ == "__main__":
    root = Tk()
    obj = Face__Recognition_System(root)
    root.mainloop()