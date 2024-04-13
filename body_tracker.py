import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from subtraction_manager import SubtractionManager

net = cv.dnn.readNetFromTensorflow("graph_opt.pb") ## weights

inWidth = 320
inHeight = 240
thr = 0.2

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                   ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                   ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
                   ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
                   ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]


def pose_estimation(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]
    
    assert(len(BODY_PARTS) == out.shape[1])
    
    points = []
    
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponding body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
        
    t, _ = net.getPerfProfile()
    freq = cv.getTickFrequency() / 1000
    cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    return frame


# estimated_image = pose_estimation(img)
# plt.imshow(cv.cvtColor(estimated_image, cv.COLOR_BGR2RGB))

cap = cv.VideoCapture(1)
cap.set(cv.CAP_PROP_FPS, 30)
cap.set(3, 800)
cap.set(4, 800)
font = cv.FONT_HERSHEY_SIMPLEX

if not cap.isOpened():
    cap = cv.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

c1counter = 0
c2counter = 0
c3counter = 0
c4counter = 0
    
while True:
    hasFrame, frame = cap.read()
    if not hasFrame:
        cv.waitKey()
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]

    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    


    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponding body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)

            #Manages each hand individually
            if (pair[0] == 'LElbow' or pair[0] == 'RElbow'):
                print(pair)
                print(points[idFrom])
                print(str(points[idFrom][0]) + " " + str(points[idFrom][1]))


                # cv.rectangle(frame, (0, 0), (150, 150), (0, 255, 0), 3) #Option Box 1
                # cv.rectangle(frame, (0, frameHeight-150), (150, frameHeight), (0, 255, 0), 3) #Option Box 2
                # cv.rectangle(frame, (frameWidth - 150, 0), (frameWidth, 150), (0, 255, 0), 3) #Option Box 3
                # cv.rectangle(frame, (frameWidth - 150, frameHeight-150), (frameWidth, frameHeight), (0, 255, 0), 3) #Option Box 4

                
                #Top Left
                if (points[idFrom][0] <=150 and points[idFrom][1] <= 150):
                    c1counter = c1counter + 1
                    print(c1counter)


                #Top Right
                if (points[idFrom][0] >= (frameWidth - 150) and points[idFrom][1] <= 150): #FIXME: Add proper bounds
                    c2counter = c2counter + 1
                    print(c2counter)


                #Bottom Left
                if (points[idFrom][0] <= 150 and points[idFrom][1] >= (frameHeight - 150)):
                    c3counter = c3counter + 1
                    print(c3counter)

                #Bottom Right
                if (points[idFrom][0] >= (frameWidth - 150) and points[idFrom][1] >= (frameHeight - 150)):
                    c4counter = c4counter + 1
                    print(c4counter)


                # get first and second values of points[idFrom]


    #----------------------------------------------------------
    #Game Logic

    #drawing objects
    cv.rectangle(frame, (0, 0), (150, 150), (0, 255, 0), 3) #Option Box 1
    cv.rectangle(frame, (0, frameHeight-150), (150, frameHeight), (0, 255, 0), 3) #Option Box 2
    cv.rectangle(frame, (frameWidth - 150, 0), (frameWidth, 150), (0, 255, 0), 3) #Option Box 3
    cv.rectangle(frame, (frameWidth - 150, frameHeight-150), (frameWidth, frameHeight), (0, 255, 0), 3) #Option Box 4

    #drawing answer choices
    #call method from subtraction-manager.py
    problem = SubtractionManager.getProblem()
    cv.putText(frame, problem, (int(frameWidth/2) - 130, 60), font, 1, (255, 255, 255), 2) #problem
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[0]), (20, 60), font, 1, (255, 255, 255), 2) #ac1
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[1]), (int(frameWidth/2) + 200, 60), font, 1, (255, 255, 255), 2) #ac2
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[2]), (20, frameHeight - 70), font, 1, (255, 255, 255), 2) #ac3
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[3]), (int(frameWidth/2) + 200, frameHeight - 70), font, 1, (255, 255, 255), 2) #ac4

    


    #counter manager
    if (c1counter >= 25):
        cv.putText(frame, 'Option 1 Picked!', (10, 250), font, 2.5, (255, 255, 255), 2)
    if (c2counter >= 25):
        cv.putText(frame, 'Option 2 Picked!', (10, 250), font, 2.5, (255, 255, 255), 2)
    if (c3counter >= 25):
        cv.putText(frame, 'Option 3 Picked!', (10, 250), font, 2.5, (255, 255, 255), 2)
    if (c4counter >= 25):
        cv.putText(frame, 'Option 4 Picked!', (10, 250), font, 2.5, (255, 255, 255), 2)




    #cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    cv.imshow('Body Tracker', frame)

    # Check for key press to exit
    key = cv.waitKey(1)
    if key == ord('q') or key == 27:  # 'q' key or ESC key
        break

# Release the video capture and close the OpenCV window
cap.release()
cv.destroyAllWindows()