import cv2 as cv

#read images 
 
img = cv.imread('try.cpp/Images/DnC.jpg')    #img is an instance of that jpg file whose path is directed
cv.imshow('Dn', img)


cv.waitKey(0)       #waits till a key is pressed












#play videos
capture = cv.VideoCapture('try.cpp/Images/Panadaas.webm') #or 0 for webcam instead of address

while True:      #reading frame by frame
    isTrue, frame = capture.read()
    cv.imshow('vid', frame)

    if cv.waitKey(20) & 0xFF == ord ('d'):    #pressing key 'd' will break the loop
        break

capture.release() 
cv.destroyAllWindows()


