from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from tkinter import messagebox
import cv2
import mysql.connector
import cv2 as cv
import os
import numpy as np




class Train:
    def __init__(self,root):
        self.root=root
        self.root.geometry("1260x750+0+0")
        self.root.title("Train")


        #background image
        imgbg=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/Bgimg.webp")
        imgbg=imgbg.resize((1260,750),Image.ANTIALIAS)
        self.photoimgbg =ImageTk.PhotoImage(imgbg)
     
        f_lbl=Label(self.root,image=self.photoimgbg)
        f_lbl.place(x=0,y=0,width=1260,height=750)


        #title label
        title_lbl = Label(self.root,text = " TRAIN DATA SET " , font = ( " chalkduster " , 35 , " bold " ) ,bg="white",fg="blue")
        title_lbl.place ( x = 0 , y = 0 , width = 1260 , height = 45 )


        #train button
        imgtrain=Image.open(r"/Users/lokeshnahar/Documents/try_try/try.cpp/Images/train.jpg")
        imgtrain=imgtrain.resize((300,300),Image.ANTIALIAS)
        self.photoimgtrain =ImageTk.PhotoImage(imgtrain)
        
        button_s = Button(self.root,image= self.photoimgtrain,cursor="hand2",command=self.train_classifier)
        button_s.place(x=450,y=200,width=300,height=300)
        
        button_s_s=Button(self.root,text="Train Data",cursor="hand2",command=self.train_classifier,font=("chalkduster",35,"bold"),bg="green",fg="blue")
        button_s_s.place(x=450,y=500,width=300,height=80)




    def train_classifier(self):
        data_dir=("Image_data")
        path=[os.path.join(data_dir,file) for file in os.listdir(data_dir)]

        faces=[]
        ids=[]
        for image in path:
            img=Image.open(image).convert('L')  #Greyscale Image
            imagenp=np.array(img,'uint8')
            id=int(os.path.split(image)[1].split(".")[1])

            faces.append(imagenp)
            ids.append(id)
            cv.imshow("Training",imagenp)
            cv2.waitKey(1)==13# & 0xFF == ord('l')
        ids=np.array(ids)
 
        ##################training Clasifire and save##################
        clf = cv.face.LBPHFaceRecognizer_create()
        clf.train(faces,ids)
        clf.write("classifier.xml") 
        cv.destroyAllWindows()
        messagebox.showinfo("done","Training Completed!!",parent=self.root)

















if __name__ == "__main__":
    root = Tk()
    obj = Train(root)
    root.mainloop()