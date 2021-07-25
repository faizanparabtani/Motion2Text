import time
import os
import io
import hashlib
from google.cloud import vision
from google.cloud.vision_v1 import types
import pandas as pd
import numpy as np
import cv2
from collections import deque
import binascii
# Evernote SDK for Python3
import evernote
from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes
import evernote.edam.error.ttypes as Errors

# Create a sandbox account
# Your developer token from https://sandbox.evernote.com/api/DeveloperToken.action
developer_token = "paste here"


def activity():
    choice = int(input("1 - List notes\n2 - Add Note\n"))
    if choice == 1:
        listNotes(client)
        activity()
    elif choice == 2:
        title = input("Enter note title: ")
        doodle(title)
    else:
        print("Choice invalid")
        activity()


def initializeClient():
    # Set up the NoteStore client
    client = EvernoteClient(token=developer_token)
    return client


def welcomeUser(client):
    # Gets User and Note Store
    userStore = client.get_user_store()
    note_store = client.get_note_store()
    user = userStore.getUser()
    print("Welcome " + user.username + " to Air Doodling App")

    return note_store


def listNotes(client):
    note_store = client.get_note_store()

    # Make API calls
    notebooks = note_store.listNotebooks()
    for notebook in notebooks:
        print("Notebook: ", notebook.name)


# Type is included to indicate the type of note: text - 0, drawing - 1
def makeNote(authToken, noteStore, noteTitle, noteBody, type, resources=[], parentNotebook=None):
    ourNote = ttypes.Note()
    ourNote.title = noteTitle
    # Check for type
    if type == 0:
        # No resources attached
        nBody = '<?xml version="1.0" encoding="UTF-8"?>'
        nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        nBody += '<en-note>%s</en-note>' % noteBody
    else:
        # Attaching Resources
        nBody = '<?xml version="1.0" encoding="UTF-8"?>'
        nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        nBody += "<en-note>%s" % noteBody
        if resources:
            nBody += "<br />" * 2
            ourNote.resources = resources
            for resource in resources:
                # MD5 hash in hexadecimal
                hexhash = resource.data.bodyHash
                nBody += "Attachment with hash %s: <br /><en-media type=\"image/jpg\" hash=\"%s\" /><br />" % \
                    (hexhash, hexhash)
        nBody += "</en-note>"
    # Create note object
    ourNote.content = nBody

    # parentNotebook is optional; if omitted, default notebook is used
    if parentNotebook and hasattr(parentNotebook, 'guid'):
        ourNote.notebookGuid = parentNotebook.guid

    # Attempt to create note in Evernote account
    try:
        note = noteStore.createNote(authToken, ourNote)
    except (Errors.EDAMUserException, edue):
        # Something was wrong with the note data
        # See EDAMErrorCode enumeration for error code explanation
        # http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        print("EDAMUserException:", edue)
        return None
    except (Errors.EDAMNotFoundException, ednfe):
        # Parent Notebook GUID doesn't correspond to an actual notebook
        print("EDAMNotFoundException: Invalid parent notebook GUID")
        return None

    # Return created note object
    return note


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def setValues(x):
    print("")


def doodle(title):
    global hashed_image
    resources = []
    notebody = ""
    word_lis = []
    # Have the visionapi.json in the same folder
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'visionapi.json'
    client = vision.ImageAnnotatorClient()

    FOLDER_PATH = r'Enter text folder path'
    FOLDER_PATH1 = r'Enter image folder path'
    # Trackabars to change HSV values of color being tracked
    cv2.namedWindow("color")
    cv2.createTrackbar("Upper Hue", "color", 180, 180, lambda x: x)
    cv2.createTrackbar("Upper Saturation", "color", 255, 255, lambda x: x)
    cv2.createTrackbar("Upper Value", "color", 255, 255, lambda x: x)
    cv2.createTrackbar("Lower Hue", "color", 50, 180, lambda x: x)
    cv2.createTrackbar("Lower Saturation", "color", 110, 255, lambda x: x)
    cv2.createTrackbar("Lower Value", "color", 60, 255, lambda x: x)
    cv2.resizeWindow("color", 500, 500)

    # List to keep the latest action/type of note
    text_drawing = [0]  # Default Text Note

    # Giving different arrays to handle colour points of different colour
    bpoints = [deque(maxlen=1024)]

    # These indexes will be used to mark the points in particular arrays of specific colour
    blue_index = 0

    # The kernel to be used for dilation purpose
    kernel = np.ones((5, 5), np.uint8)
    # RGBY
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0

    # Canvas setup
    paintWindow = np.zeros((471, 636, 3)) + 255
    paintWindow = cv2.rectangle(paintWindow, (40, 1), (140, 65), (0, 0, 0), 2)
    paintWindow = cv2.rectangle(
        paintWindow, (160, 1), (255, 65), colors[0], -1)
    paintWindow = cv2.rectangle(
        paintWindow, (275, 1), (370, 65), colors[2], -1)
    paintWindow = cv2.rectangle(
        paintWindow, (390, 1), (485, 65), colors[1], -1)
    paintWindow = cv2.rectangle(
        paintWindow, (505, 1), (600, 65), colors[1], -1)

    cv2.putText(paintWindow, "CLEAR", (49, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "Text", (185, 33), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "Drawing", (298, 33), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "Save & Exit", (420, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(paintWindow, "Save", (520, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 2, cv2.LINE_AA)
    cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

    # Loading the default webcam of PC.
    cap = cv2.VideoCapture(0)
    # Keep looping
    while True:
        # Reading the frame from the camera
        ret, frame = cap.read()
        # Flipping the frame to see same side of yours
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        u_hue = cv2.getTrackbarPos("Upper Hue", "color")
        u_saturation = cv2.getTrackbarPos("Upper Saturation", "color")
        u_value = cv2.getTrackbarPos("Upper Value", "color")
        l_hue = cv2.getTrackbarPos("Lower Hue", "color")
        l_saturation = cv2.getTrackbarPos("Lower Saturation", "color")
        l_value = cv2.getTrackbarPos("Lower Value", "color")
        Upper_hsv = np.array([u_hue, u_saturation, u_value])
        Lower_hsv = np.array([l_hue, l_saturation, l_value])

        # Adding the colour buttons to the live frame for colour access
        frame = cv2.rectangle(frame, (40, 1), (140, 65), (122, 122, 122), -1)
        frame = cv2.rectangle(frame, (160, 1), (255, 65), colors[0], -1)
        frame = cv2.rectangle(frame, (275, 1), (370, 65), colors[2], -1)
        frame = cv2.rectangle(frame, (390, 1), (485, 65), colors[1], -1)
        frame = cv2.rectangle(frame, (505, 1), (600, 65), colors[1], -1)
        cv2.putText(frame, "CLEAR ALL", (49, 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Text", (185, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Drawing", (298, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Save & Exit", (420, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    0.3, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Save", (520, 33), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (150, 150, 150), 2, cv2.LINE_AA)

        # Identifying the pointer by making its mask
        Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
        Mask = cv2.erode(Mask, kernel, iterations=1)
        Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
        Mask = cv2.dilate(Mask, kernel, iterations=1)

        # Find contours for the pointer after idetifying it
        cnts, _ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
        center = None

        # Ifthe contours are formed
        if len(cnts) > 0:
            # sorting the contours to find biggest
            cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
            # Get the radius of the enclosing circle around the found contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            # Draw the circle around the contour
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            # Calculating the center of the detected contour
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            # Now checking if the user wants to click on any button above the screen
            if center[1] <= 65:
                if 40 <= center[0] <= 140:  # Clear Button
                    bpoints = [deque(maxlen=512)]
                    blue_index = 0
                    paintWindow[67:, :, :] = 255
                elif 160 <= center[0] <= 255:
                    text_drawing.append(0)
                elif 275 <= center[0] <= 370:
                    text_drawing.append(1)
                elif 390 <= center[0] <= 485:
                    if text_drawing[-1] == 0:
                        makeNote(developer_token, note_store,
                                 title, notebody, 0)
                    else:
                        makeNote(developer_token, note_store,
                                 title, notebody, 1, resources)
                    exit()
                elif 505 <= center[0] <= 600:
                    time.sleep(2) # To avoid multiple saves
                    if text_drawing[-1] == 0:
                        IMAGE_FILE = 'text.jpg'
                        FILE_PATH = os.path.join(FOLDER_PATH, IMAGE_FILE)
                        cv2.imwrite(FILE_PATH, paintWindow[67:])

                        # Reading the file in binary
                        with io.open(FILE_PATH, 'rb') as image_file:
                            content = image_file.read()

                        # GCP handwritten text to string
                        image = types.Image(content=content)
                        response = client.document_text_detection(image=image)

                        docText = response.full_text_annotation.text
                        # Checking for repeats
                        if len(word_lis) > 0:
                            if word_lis[-1] == docText:
                                pass
                            else:
                                notebody += " " + docText
                                word_lis.append(docText)
                        else:
                            notebody += " " + docText
                            word_lis.append(docText)
                        print(word_lis, notebody)
                    else:
                        # It is a drawing so upload as a Resource
                        IMAGE_FILE = "doodle.jpg"
                        FILE_PATH = os.path.join(FOLDER_PATH1, IMAGE_FILE)
                        cv2.imwrite(FILE_PATH, paintWindow[67:])
                        # Bodyhash
                        hashed_image = md5(FILE_PATH)
                        with io.open(FILE_PATH, 'rb') as image_file:
                            content = image_file.read()
                        # Data object
                        data_instance = ttypes.Data(bodyHash=hashed_image, size=len(hashed_image), body=content)
                        #Resource Object
                        res = ttypes.Resource(data=data_instance, mime="image/jpg") 
                        # Append to resource list to send to makeNote
                        resources.append(res)
            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
        # Append the next deque when nothing is detected to avoid messing up
        else:
            bpoints.append(deque(maxlen=512))
            blue_index += 1
    # Drawing lines
        points = [bpoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1],
                             points[i][j][k], colors[i], 2)
                    cv2.line(paintWindow, points[i][j]
                             [k - 1], points[i][j][k], colors[i], 2)

        # Show all the windows
        if text_drawing[-1] == 0:
            cv2.putText(frame, "Text", (10, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, "Drawing", (10, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)
        cv2.imshow("mask", Mask)

        # If the 'q' key is pressed then stop the application
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the camera and all resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    client = initializeClient()
    note_store = welcomeUser(client)
    activity()
