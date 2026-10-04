import cv2 , time


#create an object . Zero for extrenal camera 
video = cv2.VideoCapture(0)

#taking a as variable 
a = 0

while True:
    a = a + 1


    #create a frame object 
    check, frame = video.read()

    print(check)
    print(frame)   #replesenting the image 

    #converting greyscale 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #show the frame 
    cv2.imshow("capturing", gray)

    #for press any key to close the window(in milliseconds)
    #cv2.waitKey(0)

    #for Playing
    key = cv2.waitKey(1)
    
    if key == ord('q'):
        break
    print(a)

#shutdown the camera 
video.release()

cv2.destroyAllWindows