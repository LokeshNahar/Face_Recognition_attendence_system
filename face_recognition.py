from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import cv2
from cv2 import VideoCapture
import mysql.connector
import cv2 as cv
import os
import numpy as np
from time import strftime
from datetime import datetime




class Face_recognition:
    def __init__(self,root):
        self.root=root
        self.root.geometry("1260x750+0+0")
        self.root.title("Face_Recognition")


        #background image
        imgbg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/Bgimg.webp")
        imgbg=imgbg.resize((1260,750),Image.ANTIALIAS)
        self.photoimgbg =ImageTk.PhotoImage(imgbg)
     
        f_lbl=Label(self.root,image=self.photoimgbg)
        f_lbl.place(x=0,y=0,width=1260,height=750)


        #facerecognition label
        title_lbl = Label(self.root,text = " Face Recognition " , font = ( " chalkduster " , 35 , " bold " ) ,bg="white",fg="blue")
        title_lbl.place ( x = 0 , y = 0 , width = 1260 , height = 45 )


        #facerecognition button
        imgfacerecognition=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/facerecognition.jpg")
        imgfacerecognition=imgfacerecognition.resize((300,300),Image.ANTIALIAS)
        self.photoimgfacerecognition =ImageTk.PhotoImage(imgfacerecognition)
        
        button_s = Button(self.root,image= self.photoimgfacerecognition,cursor="hand2",command=self.face_recog)
        button_s.place(x=450,y=200,width=300,height=300)
###################################################################
    def mark_attendence(self,i,n,e,d):
        with open("attendence.csv","r+",newline="\n") as f:
            myDataList=f.readline()
            namelist=[]
            for line in myDataList:
                entry=line.split(",")
                namelist.append(entry[0])
            if ((i not in namelist)) and ((n not in namelist)) and   ((e not in namelist)) and   ((d not in namelist)):
                now=datetime.now()
                d1=now.strftime("%d/%m/%Y")
                dtstring=now.strftime("%H:%M:%S")
                f.writelines(f"\n{i},{n},{e},{d},{dtstring},{d1},Present")



##################################################################
    def face_recog(self):
        def draw_boundary(img,classifier,scaleFactor,minimumNeighbour,color,text,clf):
            gray_image=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray_image,scaleFactor,minimumNeighbour)

            coord=[]

            for(x,y,w,h) in features:
                cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                id,predict=clf.predict(gray_image[y:y+h,x:x+w])
                confidence=int((100*(1-predict/300)))

                conn=mysql.connector.connect(host="localhost",username="root",password="allaboutenergy&practise",database="face_recognixer")
                my_cursor=conn.cursor()

                my_cursor.execute("select Sname from student where Sid="+str(id))
                n=my_cursor.fetchone()
                n="+".join(n)

                my_cursor.execute("select Email from student where Sid="+str(id))
                e=my_cursor.fetchone()
                e="+".join(e)

                my_cursor.execute("select Dep from student where Sid="+str(id))
                d=my_cursor.fetchone()
                d="+".join(d)

                my_cursor.execute("select Sid from student where Sid="+str(id))
                i=my_cursor.fetchone()
                i="+".join(i)

                if confidence>78:
                    cv.putText(img,f"SID: {i}",(x,y-75),cv.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv.putText(img,f"Email: {e}",(x,y-55),cv.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv.putText(img,f"Name: {n}",(x,y-30),cv.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    cv.putText(img,f"Dep: {d}",(x,y-5),cv.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)
                    self.mark_attendence(i,n,e,d)
                else:
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
                    cv.putText(img,"Unknown",(x,y-5),cv.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)

                coord=[x,y,w,h]
            return coord


        def recognise(img,clf,faceCascade):
            coord=draw_boundary(img,faceCascade,1.1,10,(225,25,255),"Face",clf)
            return img


        faceCascade=cv.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf=cv.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")
        video_cap=cv.VideoCapture(0)

        while True:
            ret,img=video_cap.read()
            img=recognise(img,clf,faceCascade)
            cv.imshow("Smile:)",img)
            
            if cv.waitKey(1)==13:
                break
        video_cap.release()
        cv.destroyAllWindows()

if __name__ == "__main__":
    root = Tk()
    obj = Face_recognition(root)
    root.mainloop()