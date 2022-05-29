import cv2 as cv


img = cv.imread('ab.jpg')
cv.imshow("person",img)



classi=cv.CascadeClassifier("haarcascade_frontalface_default.xml")
face = classi.detectMultiScale(img,1.5,3)

for (x,y,w,h) in face:
    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),thickness=2)

cv.imshow("dete",img)
print(f"no. faces{len(face)}")
cv.waitKey(0) 