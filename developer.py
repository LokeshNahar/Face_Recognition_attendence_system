from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import mysql.connector
import cv2 as cv
import os
import csv
from tkinter import filedialog



class Developer:
    def __init__(self,root):
        self.root=root
        self.root.geometry("1260x750+0+0")
        self.root.title("Introduction")

        #background image
        imgbg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/Bgimg.webp")
        imgbg=imgbg.resize((1260,750),Image.ANTIALIAS)
        self.photoimgbg =ImageTk.PhotoImage(imgbg)
     
        f_lbl=Label(self.root,image=self.photoimgbg)
        f_lbl.place(x=0,y=0,width=1260,height=750)

        #label text
        title_lbl = Label(self.root,text="Introduction",font=("chalkboard",30,"bold"),bg="red",fg="black")
        title_lbl.place(x=0,y=0,width=1260,height=50)


        #Main Frame
        main_frame=Frame(self.root,bd=2,relief=RIDGE,bg="skyblue")
        main_frame.place(x=800,y=75,width=400,height=600)

        imgstudent=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/intro.jpg")
        imgstudent=imgstudent.resize((700,700),Image.ANTIALIAS)
        self.photoimgstudent =ImageTk.PhotoImage(imgstudent)
        f_lbl1=Label(self.root,image=self.photoimgstudent)
        f_lbl1.place(x=50,y=50,width=700,height=700)

        a_lbl = Label(main_frame,text="Python",font=("chalkboard",30,"bold"),bg="yellow",fg="orange")
        a_lbl.place(x=10,y=100,width=200,height=50)

        a_lbl = Label(main_frame,text="MySQl",font=("chalkboard",25,"bold"),bg="skyblue",fg="blue")
        a_lbl.place(x=200,y=160,width=200,height=50)

        a_lbl = Label(main_frame,text="Open CV in Python",font=("chalkboard",20,"bold"),bg="pink",fg="purple")
        a_lbl.place(x=10,y=220,width=200,height=50)

        a_lbl = Label(main_frame,text="used tkinter",font=("chalkboard",25,"bold"),bg="lightgreen",fg="green")
        a_lbl.place(x=200,y=280,width=200,height=50)

        # iitg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/iitg.png")
        # iitg=iitg.resize((150,150),Image.ANTIALIAS)
        # self.photoiitg =ImageTk.PhotoImage(iitg)
        # f_lbl2=Label(self.root,image=self.photoiitg)
        # f_lbl2.place(x=800,y=75,width=400,height=75)
##




if __name__ == "__main__":
    root = Tk()
    obj = Developer(root)
    root.mainloop()