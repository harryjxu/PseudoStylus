'''
Created on Dec 1, 2015
15-112 Term Project

Harry Xu
hjx@andrew.cmu.edu
Section G

The demo code is borrowed from here:
http://www.computervisiononline.com/blog/
tutorial-using-camshift-track-objects-video
'''
# we use globals since the original code did - don't want to break it
# import statements - we will use OpenCV, numpy, and imutils
import numpy as np;
import cv2;
import imutils;

# dictating which mode we are operating and an pause feature
mode = 0x40;
paused = False;
col = (255, 0, 0);

# the variables to operate the tracking feature
FRAME = None;
roiPts = [];
orig = None;
roiHist = None;
roiBox = None;

# the global storage for writing letters
ptHist = [];
mouseHist = [];
letters = [];

letterRef = []; # refernce for the shape of letters
word = '';

def main():
    global FRAME, roiPts, mode, paused;
    width = 1200;
    height = 600;
    termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1);
    key = None;
    currentFrame = None;
    modeTracker = [0];

    # set the frame to all white
    camera = cv2.VideoCapture(0);
    FRAME = np.zeros((height, width, 3), np.uint8); 
    FRAME[:, :] = (255, 255, 255);

    # Window is the window we are showing 
    cv2.namedWindow("Window");
    cv2.setMouseCallback("Window", mouseClick);
    try:
        readme_file = open('menu.txt', 'r+');
    except:
        raise ValueError("menu not found");
    readme = readme_file.read();

    # initialize the letter references
    initLetter();
    initLetterRef();

    # mode dispatcher
    # mode 0 being menu
    # mode 1 being selection
    # mode 2 being drawing
    # mode 3 being writing
    # and mode 4 being the background
    while True:
        if mode == 0xFF: # break condition
            break;
        elif mode & 0xF0 == 0x00:
            mode0(readme, modeTracker);
        elif mode & 0xF0  == 0x10:
            if paused == False:
                (grabbed, currentFrame) = camera.read()
            mode1(currentFrame, termination);
        elif mode & 0xF0 == 0x20:
            (grabbed, currentFrame) = camera.read();
            mode2(currentFrame, termination);
        elif mode & 0xF0 == 0x30:
            (grabbed, currentFrame) = camera.read();
            mode3(currentFrame, termination);
        elif mode & 0xF0== 0x40:
            mode4(); # we added this late, so it is last!

    # we need these two functions otherwise we will not release resources
    camera.release();
    cv2.destroyAllWindows();
    print "Exit";

def mouseClick(event, x, y, flags, param):
    # grab the reference to the current frame, list of ROI
    # points and whether or not it is ROI selection mode
    global FRAME, roiPts, mode, mouseHist;
    # if we are in ROI selection mode, the mouse was clicked,
    # and we do not already have four points, then update the
    # list of ROI points with the (x, y) location of the click
    # and draw the circle

    if mode == 0x11 and event == cv2.EVENT_LBUTTONDOWN and len(roiPts) < 4:
        roiPts.append((x, y))
        cv2.circle(FRAME, (x, y), 4, (0, 255, 0), 2)
        cv2.imshow("Window", FRAME)
    elif mode == 0x31 and event == cv2.EVENT_LBUTTONDOWN: # debugging modes
        mode = 0x32;
    elif mode == 0x32 and event == cv2.EVENT_MOUSEMOVE:
        mouseHist.append((x, y));
    elif mode == 0x32 and event == cv2.EVENT_LBUTTONUP:
        mode = 0x31;
    elif event == cv2.EVENT_LBUTTONDOWN: # if you want to find the coordinates of the window
        print "click", (x, y)

def mode0(msg, modeTracker): # the menu screen
    # font size is 20
    global FRAME, mode

    msg = msg.splitlines();

    # writes the components of menu.txt
    for line in range(0, 3): 
        cv2.putText(FRAME, msg[line], (500, 100 + line*20),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0));

    for line in range(0, 6):
        if modeTracker[0] == line:
            col = (0, 0, 255);
        else:
            col = (0, 0, 0);
        cv2.putText(FRAME, msg[line + 3], (500, 100 + 60 + line*20),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, col);
    for line in range(9, len(msg)):
        cv2.putText(FRAME, msg[line], (500, 100 + line*20),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0));

    cv2.imshow("Window", FRAME); # we show the frame to update the new written message

    key = cv2.waitKey(0); # wait until key movement

    if key == ord('q'): # this is our quit key - reoccuring in nearly every mode
        mode = 0xFF;
        return None;
    elif key == ord('1'): # mode tracker determines what is highlighted
        # no change in mode
        modeTracker[0] = 0;
    elif key == ord('2'):
        modeTracker[0] = 1;
    elif key == ord('3'):
        modeTracker[0] = 2;
    elif key == ord('4'):
        modeTracker[0] = 3;
    elif key == ord('5'):
        modeTracker[0] = 4;
    elif key == ord(' '): # if space is hit, then we move to the next mode
        modeTracker[0] = 0;
        mode = 0x10;

def mode1(frame, termination): # the mode to select the points for comparison
    global mode, FRAME, paused, roiPts, orig, roiHist, roiBox;

    if paused == False: # if we are paused stop reading and updating new frames
        frame = imutils.resize(frame, width = 600);
        frame = cv2.flip(frame, 1); # flip across y axis
        FRAME = np.zeros((600, 1200, 3), np.uint8);
        FRAME[0 + 120:337 + 120,:600] = frame[:,:];
        
    FRAME[:100, :] = (0, 0, 0); # we make the top clear for writing a message
    cv2.putText(FRAME, "Press 'i' to select bounding points."
                +" Press 'i' to finish after.",
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

    key = cv2.waitKey(1) & 0xFF; # wait a key, check if the key is within 0 -> 255
    
    if key == ord('q'): # quit key
        mode = 0xFF;
        return None;
    elif key == ord('i') and mode == 0x10: # pause for selection
        mode = 0x11;
        paused = True;
            
        orig = FRAME.copy();
            
        while len(roiPts) < 4: # selection while we have points to add
            cv2.imshow("Window", FRAME);
            cv2.waitKey(0);

        # determine the top-left and bottom-right points
        roiPts = np.array(roiPts)
        s = roiPts.sum(axis = 1) # summation to find the rectangle
        tl = roiPts[np.argmin(s)] # top left pixel
        br = roiPts[np.argmax(s)] # bottom right pixel

        # grab the ROI for the bounding box and convert it
        # to the HSV color space
        roi = orig[tl[1]:br[1], tl[0]:br[0]]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

        # compute a HSV histogram for the ROI and store the
        # bounding box
        roiHist = cv2.calcHist([roi], [0], None, [16], [0, 180])
        
        roiHist = cv2.normalize(roiHist, roiHist, 0, 255, cv2.NORM_MINMAX)

        for i in range(16): # round the values for ease of use
            roiHist[i] = int(round(roiHist[i]));

        roiBox = (tl[0], tl[1], br[0], br[1]) # create a bounding box

        paused = False;
        mode = 0x12;

    elif mode == 0x12 and key == ord("y"): # we move on if the points are there
        FRAME[:100, :] = (0, 0, 0);
        cv2.putText(FRAME, "D for drawing, W for writing", (525, 75),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

        cv2.imshow("Window", FRAME);

        key = cv2.waitKey(0); # wait until a decision is made

        if key == ord("d"):
            mode = 0x20; # state transition
        elif key == ord("w"):
            mode = 0x30;
    elif mode == 0x12 and key == ord("n"): # reset var to try again
        mode = 0x10;
        roiPts = [];
        orig = None;
        roiHist = None;
        roiBox = None;

    if mode == 0x12 and paused == False:

        # convert the current frame to the HSV color space
        # and perform mean shift

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # create a back projection based on the historgram of HSV values
        backProj = cv2.calcBackProject([hsv], [0], roiHist, [0, 180], 1)
        
        # show the backprojection onto the frame
        newBackProj = np.zeros((337, 600, 3), np.uint8);
        newBackProj[:,:,0] = backProj[:,:];
        newBackProj[:,:,1] = newBackProj[:,:,2] = newBackProj[:,:,0];

        FRAME[0 + 120:337 + 120,600:] = newBackProj[:,:];

        # apply cam shift to the back projection, convert the
        # points to a bounding box, and then draw them
        
        try: # if the selected points are not working, we catch that
            (r, roiBox) = cv2.CamShift(backProj, roiBox, termination)
            pts = np.int0(cv2.cv.BoxPoints(r))
            for pt in pts:
                pt[1] = pt[1] + 120;
            
            cv2.polylines(FRAME, [pts], True, (0, 255, 0), 2)
        except:
            cv2.putText(FRAME, "NOT WORKING!!!", (300, 240),
                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255));

        FRAME[:100, :] = (0, 0, 0);
        cv2.putText(FRAME, "Are you satisfied? Y/N?", (525, 75),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

    cv2.imshow("Window", FRAME);


def mode2(frame, termination): # this mode is for drawing
    global mode, col, FRAME, ptHist, roiPts, orig, roiHist, roiBox;

    FRAME[:100, :] = (0, 0, 0);
    if mode == 0x20:
        cv2.putText(FRAME, "Ready to draw 'd', 's' to stop immediately",
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));
    elif mode == 0x21:
        cv2.putText(FRAME, "Drawing now. 'd' to stop",
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

    frame = imutils.resize(frame, width = 600);
    frame = cv2.flip(frame, 1); # flip across y axis
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # calculate and display backprojection again
    backProj = cv2.calcBackProject([hsv], [0], roiHist, [0, 180], 1)
        
    newBackProj = np.zeros((337, 600, 3), np.uint8);
    newBackProj[:,:,0] = backProj[:,:];
    newBackProj[:,:,1] = newBackProj[:,:,2] = newBackProj[:,:,0];

    FRAME[0 + 120:337 + 120,:600] = newBackProj[:,:];

    # apply cam shift to the back projection, convert the
    # points to a bounding box, and then draw them
    try: # if the selected points are not working, we catch that
        (r, roiBox) = cv2.CamShift(backProj, roiBox, termination)
        pts = np.int0(cv2.cv.BoxPoints(r))
        for pt in pts:
            pt[1] = pt[1] + 120;
            
        cv2.polylines(FRAME, [pts], True, (0, 255, 0), 2)
    except:
        cv2.putText(FRAME, "NOT WORKING!!!", (300, 240),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255));
        cv2.imshow("Window", FRAME);
        cv2.waitKey(0); # this is how we make sure we can reset this thing
        mode = 0x10;
        roiPts = [];
        orig = None;
        roiHist = None;
        roiBox = None;
        return None;
    
    FRAME[0 + 120: 337 + 120, :600] = frame[:, :]

    # calculate the mean of the roiBox points
    meanX = 0;
    meanY = 0;
    for pt in pts:
        meanX += pt[0];
        meanY += pt[1];
    if mode == 0x21:
        ptHist.append((meanX//len(pts) + 600, meanY//len(pts), col));
    cv2.circle(FRAME, (meanX//len(pts), meanY//len(pts)), 4, (255, 0, 0), 2);
            
    cv2.polylines(FRAME, [pts], True, (0, 255, 0), 2)

    FRAME[120: 337+120, 600:] = (255, 255, 255);
    # show the whole ptHistory
    for pt in ptHist: # make circles of all the points
        cv2.circle(FRAME, (pt[0], pt[1]), 4, pt[2], 2);

    # clean up the borders - top and bottom
    FRAME[100:120, :] = (0, 0, 0);
    FRAME[337+120:, :] = (0, 0, 0);

    # color choices - color squares we see
    FRAME[120:120 + 40, 0:0 + 40] = (255, 0, 0);
    FRAME[120:120 + 40, 600 - 40:600] = (0, 255, 0);
    FRAME[120+337 - 40:120+337, 0:0 + 40] = (0, 0, 0);
    FRAME[120+337 - 41:120+337 - 40, 0:0 + 40] = (0, 0, 255);
    FRAME[120+337 - 40:120+337, 40-1:40] = (0, 0, 255);
    FRAME[120+337 - 40:120+337, 600 - 40:600] = (0, 0, 255);
    for pt in pts: # if any of the box points fall within, change the color
        if pt[1] < 120 + 40 and pt[1] > 120:
            if pt[0] < 40 and pt[0] > 0:
                col = (255, 0, 0);
                # print "blue"
            elif pt[0] > 600 - 40 and pt[0] < 600:
                col = (0, 255, 0);
                # print "green"
        elif pt[1] > 120 - 40 + 337 and pt[1] < 120 + 337:
            if pt[0] < 40 and pt[0] > 0:
                col = (0, 0, 0);
                # print "red"
            elif pt[0] > 600 - 40 and pt[0] < 600:
                col = (0, 0, 255);
                # print "black"

    cv2.imshow("Window", FRAME); # update the window with the new graphics

    key = cv2.waitKey(1);

    if key == ord('q'): # quit key
        mode = 0xFF;
        return None;

    if key == ord("d") and mode == 0x20: # begin drawing
        mode = 0x21;
    elif key == ord("d") and mode == 0x21: # new/change mode
        mode = 0x22;
    elif key == ord(" ") and mode == 0x21: # being drawing
        mode = 0x20;
    elif key == ord(" ") and mode == 0x20: # stop drawing
        mode = 0x21;
    elif key == ord("s") and (mode == 0x20 or mode == 0x21): # new/change mode
        mode = 0x22;
    elif mode == 0x22:
        FRAME[:100, :] = (0, 0, 0);
        cv2.putText(FRAME, "'w' to write, or 'n' for new",
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

        letter = np.zeros((600, 600), np.uint8); # format into letter form for storage
        for pt in ptHist:
            x = pt[1]; # adjust for the frame offset
            y = pt[0] - 600; # readjust from the FRAME offset
            letter[x, y] = 1;
            # lets use a box of radius 10
            for oldX in range(5):
                for oldY in range(5):
                    newX = x + oldX;
                    newY = y + oldY;
                    if newX < 600 and newY < 600:
                        letter[newX, newY] = 1;

        ptHist = []; # reset the pointHistory

        letterFrame = np.zeros((600, 600, 3), np.uint8);
        for x in range(600):
            for y in range(600):
                if letter[x, y] == 1:
                    letterFrame[x, y] = (0, 0, 0);
                else:
                    letterFrame[x, y] = (255, 255, 255);

        cv2.imshow("Window", FRAME);
        newKey = cv2.waitKey(0);

        if newKey == ord("q"): # new choices
            mode = 0xFF;
            return None;

        if newKey == ord("s"): # saving into storage
            saveLetter(letter);
        elif newKey == ord("w"):
            FRAME[:, 600:] = (0, 0, 0);
            mode = 0x30;
        elif newKey == ord("n"):
            mode = 0x20;
            FRAME[:, 600:] = (0, 0, 0);

    cv2.imshow("Window", FRAME);

def initLetter(): # create the array of letters and check if the file is present
    global letters;
    try:
        storage_file = open('storage.txt', 'r+');
    except:
        raise ValueError("file 'storage.txt' not found!");
    contents = storage_file.read();
    storage_file.close();
    contents = contents.splitlines();

    if len(contents) < 2 or contents[0] != "<start>" or contents[-1] != "<end>":
        #raise ValueError("File format incompatible"); # for debugging
        pass;

    letters = [None for x in range(26 + 10)]; # create the range of possible letters

def saveLetter(letter): # attempt to save the letters
    global FRAME, letters;
    try:
        storage_file = open('storage.txt', 'r+');
    except:
        raise ValueError("file 'storage.txt' not found!");
    contents = storage_file.read();

    FRAME[:100, :] = (0, 0, 0);
    cv2.putText(FRAME, "Type the character of the input",
        (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

    cv2.imshow("Window", FRAME);

    key = cv2.waitKey(0); # save the letter to this key
    while key < ord('a') or key > ord('z'):
        key = cv2.waitKey(0);
    letters[key - ord('a')] = None;
    
    if key == ord("c"): # if c, then we clear the file
        storage_file.truncate();
        return None;

    mem = "";
    counter = 0;
    for x in range(600):
        for y in range(600):
            if letter[x, y] == 1:
                mem += str((x, y)) + ".";
                counter += 1;
    mem = "<%d, %d>." % (key, counter) + mem[:];

    storage_file.write(mem); # otherwise we write the file with the drawing

    storage_file.close();

def initLetterRef():
    global letterRef;
    # I am using a 5 deep by 3 wide grid to calculate letters
    # X X X 1 2 3
    # X   X 4 5 6
    # X X X 7 8 9
    # X    10 11 12
    # X    13 14 15
    # would be 'P'. I will use a binary tree of decisions starting from the top left
    # First reference to collection that have (0, 0) at white
    # Second reference to collection that have (0, 0) at black
    # then we move left to right, up and down
    # base reference (cell reference, "0" results, "1" results)

    # this indentation is so that it is slightly readable
    letterRef = ["1",
    ["2",
      ["3",
        ["4",
          ["5",
            ["8",
             ["10",
               "X",
               ["13",
                 "V",
                 "U"
                ]
              ],
             ["11",
               ["12",
                 ["14",
                  "R",
                  "C"
                  ],
                "O"
                ],
              "Z"
              ]
             ],
            "I"
            ],
          "A"
         ],
        "D"
       ],
     ["3",
      ["7",
       ["13",
        "L",
        "J"
       ],
       "T"
      ],
      "F"
     ]
    ],
    ["2",
     ["3",
      ["14",
       "H",
       "B"
      ],
      ["5",
       ["10",
        "Y",
        "M"
       ],
       ["6",
        "K",
        "N"
        ]
      ]
     ],
     ["3",
      " ",
      ["9",
       "S",
       ["10",
        ["13",
         "Q",
         "G"
        ],
        ["14",
         "P",
         "E"
        ]
       ]
      ]
     ]
    ]
    ]
    pass;

def findLetter(arr): # given an array of states for 1 through 15
    global letterRef;

    ref = letterRef;
    found = None;
    index = 0;
    while found == None:
        if index >= len(arr): # quick escape
            return "None";

        if type(ref) == str: # "base case"
            found = ref;
        elif type(ref) == list: # navigate the list
            if ref[0] == str(index + 1):
                if not arr[index]: # continue through the tree
                    ref = ref[1];
                else:
                    ref = ref[2];
            else:
                index += 1;
    return found

def mode3(frame, termination): # writing mode
    global mode, FRAME, ptHist, roiPts, orig, roiHist, roiBox;
    global letterRef, word, paused;
    
    if mode == 0x30: 
        FRAME[:100, :] = (0, 0, 0);
        cv2.putText(FRAME, "Ready to write 'w', 'd' to debug",
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));
    elif mode == 0x31:
        FRAME[:100, :] = (0, 0, 0);
        cv2.putText(FRAME, "Writing. Press 'w' again to stop and show'",
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

    frame = imutils.resize(frame, width = 600);
    frame = cv2.flip(frame, 1); # flip across y axis
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    backProj = cv2.calcBackProject([hsv], [0], roiHist, [0, 180], 1)
        
    newBackProj = np.zeros((337, 600, 3), np.uint8);
    newBackProj[:,:,0] = backProj[:,:];
    newBackProj[:,:,1] = newBackProj[:,:,2] = newBackProj[:,:,0];

    FRAME[0 + 120:337 + 120,600:] = newBackProj[:,:];

    if paused: # the debugging lines triggered by "d"
        # showing a set of grid lines for writing
        FRAME[120:337 + 120, 900 - 90 - 1: 900 - 90] = (0, 255, 0);
        FRAME[120:337 + 120, 900 + 90 - 1: 900 + 90] = (0, 255, 0);
        FRAME[290 - 110 - 1:290 - 110, 600:] = (0, 255, 0);
        FRAME[290 + 110 - 1:290 + 110, 600:] = (0, 255, 0);
        FRAME[290 - 35 - 1:290 - 35, 600:] = (0, 255, 0);
        FRAME[290 + 35 - 1:290 + 35, 600:] = (0, 255, 0);

    FRAME[0 + 120: 337 + 120, :600] = frame[:, :];

    # apply cam shift to the back projection, convert the
    # points to a bounding box, and then draw them
    try: # if the selected points are not working, we catch that
        (r, roiBox) = cv2.CamShift(backProj, roiBox, termination)
        pts = np.int0(cv2.cv.BoxPoints(r))
        for pt in pts:
            pt[1] = pt[1] + 120;
            
        cv2.polylines(FRAME, [pts], True, (0, 255, 0), 2)
    except:
        cv2.putText(FRAME, "NOT WORKING!!!", (300, 240),
            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255));
        cv2.imshow("Window", FRAME);
        cv2.waitKey(0); # this is how we make sure we can reset this thing
        mode = 0x10;
        roiPts = [];
        orig = None;
        roiHist = None;
        roiBox = None;
        return None;

    # the blue writing dot
    meanX = 0;
    meanY = 0;
    for pt in pts:
        meanX += pt[0];
        meanY += pt[1];
    if mode == 0x31:
        ptHist.append((meanX//len(pts) + 600, meanY//len(pts)));
    cv2.circle(FRAME, (meanX//len(pts), meanY//len(pts)), 4, (255, 0, 0), 2);

    # show the whole ptHistory
    for pt in ptHist:
        cv2.circle(FRAME, (pt[0], pt[1]), 4, (255, 0, 0), 2);

    # clean up the borders
    FRAME[100:120, :] = (0, 0, 0);
    FRAME[337+120:, :] = (0, 0, 0);
        
    cv2.putText(FRAME, "Text: %s" % word,
        (325, 525), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

    cv2.imshow("Window", FRAME);

    key = cv2.waitKey(1);

    # different states of writing or not
    if key == ord('q'):
        mode = 0xFF;
        return None;
    elif key == ord('w') and mode != 0x31:
        mode = 0x31;
    elif key == ord('w') and mode == 0x31:
        mode = 0x32;
    elif key == ord('d'):
        paused = not paused;

    if mode == 0x32: # we create a report of which cells are active or not
        freq = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
        # count the frequency of points in a certain region
        for pt in ptHist: 
            x = pt[0];
            y = pt[1];
            if x > 900 + 90 - 1:
                if y > 290 + 110 - 1: freq[14] += 1;
                elif y > 290 + 35 - 1: freq[11] += 1;
                elif y > 290 - 35 - 1: freq[8] += 1;
                elif y > 290 - 110 -1: freq[5] += 1;
                else: freq[2] += 1;
            elif x > 900 - 90 - 1:
                if y > 290 + 110 - 1: freq[13] += 1;
                elif y > 290 + 35 - 1: freq[10] += 1;
                elif y > 290 - 35 - 1: freq[7] += 1;
                elif y > 290 - 110 -1: freq[4] += 1;
                else: freq[1] += 1;
            else:
                if y > 290 + 110 - 1: freq[12] += 1;
                elif y > 290 + 35 - 1: freq[9] += 1;
                elif y > 290 - 35 - 1: freq[6] += 1;
                elif y > 290 - 110 -1: freq[3] += 1;
                else: freq[0] += 1;
                
        eps = 5; # must have at least this many points inside
        newFreq = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        for element in range(15):
            if freq[element] > eps:
                newFreq[element] = 1;
        
        letter = findLetter(newFreq); # check against our table to find a letter
                
        FRAME[:100, :] = (0, 0, 0);
        cv2.putText(FRAME, "Showing: %s Correct? Y/N" % (letter),
            (325, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255));

        cv2.imshow("Window", FRAME);
        
        key = cv2.waitKey(0);
        
        # either ignore, add or quit
        if key == ord('n'):
            ptHist = [];
            mode = 0x30;
            
        elif key == ord('y'):
            word += letter;
            ptHist = [];
            mode = 0x30;
            print word;

        elif key == ord('q'):
            mode = 0xFF;
            return None;

def mode4(): # the background screen
    global FRAME, mode;

    # image from UKRT 
    # http://www.thinkstockphotos.co.uk/image/
    # stock-photo-numbers-0-9-painting-with-light/135935723
    background = cv2.imread("123456789.jpg", 1);
    background = cv2.resize(background, (600*2, 337*2));
    cv2.imshow("Window", background);
    cv2.waitKey(0);
    mode = 0x00;

main()
