import cv2 as cv



img = cv.imread('try.cpp/Images/DnC.jpg') 
cv.imshow('Dn', img)


#greying,decolour
decolour = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# cv.imshow('decolor',decolour)

#bblurring
blur = cv.bilateralFilter(decolour,50,45,45)
# cv.imshow('blur',blur)
blur1 = cv.GaussianBlur(decolour, (5,7), cv.BORDER_DEFAULT)

canny = cv.Canny(blur,125,175)
canny1 = cv.Canny(blur1,125,175)

cv.imshow('Canny_Edges', canny)
cv.imshow('Canny_Edges1', canny1)

# dilate = cv.dilate(canny, (3,3), iterations=2)
# cv.imshow('dilate', dilate)


cv.waitKey(0) 