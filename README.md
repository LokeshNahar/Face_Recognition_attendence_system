# Face_Recognition_attendence_system
Project under Microsoft Engage 2022 
------------------------------------------------------------------------------------------------------------------------------------------------
Face Recognition "Tracking Attendence"

Upon running the main.py with attendence.py,classifier.xml,developer.py,face_recognition.py,haarcascade_frontalface_default.xml,student.py,and train.py along with the folder Images and Image_data in the same folder with changing the path of the images in main.py and other
a Window will be opened ,
that includes eight button,
1.) Student details~
    clicking this button redirects to a new window in which we can manually save a data of Student with his/her Photo sample ,
    alongwith these functinality you can also update,and delete the data,and reset the entrie filled in the respective area
    note:- Photo sample is being recorded by the Student ID (about 100 photos is captured for the data training) In this face is detected using a face classifier ,by cascading 'haarcascade_frontalface_default classifier' also a cropped black n white image of face will be previewed

2.)Train Face~
    Upon clicking on this button a window with another button is redirected that is used to train the face photo sample taken in the previous window
    The trained data of the Faces is stored in the file 'classifier.xml' by using LBPH algorithm that uses four parameters;Radius (a circular binary pattern is made around the central pixel),Neighbors i.e.  the number of sample points to build the circular local binary pattern. the next parameters are grid x and grid y that are the number of cells in the horizontal and the vertical direction respectively.
    the algorithm will use Student ID to recognize an input image and give you an output
    then LBP operations are handled along with the extracting of the Histograms. the more details of this algorithm can be read by this article: "https://towardsdatascience.com/face-recognition-how-lbph-works-90ec258c3d6b"

3.)Face Detector~
    This button also contains a button, which on clicking recognises the face by mentioning his/her details in the green
    if the person is not recognised/trained to the model a red box along with unknown tag is mentioned
    as soon as one is recognised his/her attendence is saved with the date and time in the attendence.csv file

4.) Attendence~
    in this button we can import the csv file to display the attendence in which we can update the attendence data by updating in the spaces provided, and export it to another csv file.

5.) Developer~
    My details are mentioned here:)

6.) Photos~
    This button is not functional yet but was meant to direct to the Image_data folder where the sample data is being taken

7.) Contact us~
    contact details of the developer can be accessed here

8.)Exit~
    Pressing this button will destroy all windows. so you exit to the Project
------------------------------------------------------------------------------------------------------------------------------------------------

note:- You need to enter the password and other host details of your mysql server  also it will throw an error so the path of the images should bet accordingly
------------------------------------------------------------------------------------------------------------------------------------------------
The Language used is Python , with queries of mySQL for the database access ,GUI is tkinter, the requirements.txt ile contains the requirements of the modules to be imported for this project
