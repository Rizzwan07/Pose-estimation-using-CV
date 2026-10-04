#recording and saving video 
import cv2

camera =cv2.VideoCapture(0)

if (camera.isOpened()):
    print("The camera is successfully opened")
else:
    print("Couldn't open the camera")

#checking the frame height , width and frame rate 
frameWidth=int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight=int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
frameRate=int(camera.get(cv2.CAP_PROP_FPS))

print(frameWidth,"x",frameHeight)
print(frameRate)

#capturing and saving 

fourccCode=cv2.VideoWriter_fourcc(*'MJPG')

videoFileName='recordedVideo.mp4'
videoDimenssion=(frameWidth,frameHeight)
recordedVideo=cv2.VideoWriter(videoFileName,fourccCode,frameRate,videoDimenssion)

while True:
    success,frame=camera.read()
    if not success:
        print("Not able to read the frame. End.")
        break
    
    cv2.imshow('Camera Video',frame)

    recordedVideo.write(frame)
    if cv2.waitKey(1) == ord('q'):
        break

recordedVideo.release()
camera.release()
cv2.destroyAllWindows()