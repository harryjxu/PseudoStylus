This project allows for the tracking of an object to simulate writing or drawing. The writing component also features a letter detection algorithm to convert written letters into plain text. For best use, use a highly contrastable object such as a green pen against a black background. Hold the object close to the camera for selection and try to move the object to the box before the box sticks.

To run this project, one must be using OpenCV for Python2.7 and have Python2.7 installed. In addition, the python packages numpy and imutils must be installed (they should come with the installation of Python2.7).

To install OpenCV, I first install Homebrew. I am using OS X so I type the command
“brew install opencv”.

I navigate to the location where the opencv modules are installed, for me this is
“/usr/local/Cellar/opencv/2.4.9/lib/python2.7/site-packages/“

I have to move cv.py and cv2.so to this directory.

I redirect my interpreter bathing in Eclipse to use this pathing. This should install OpenCV. If you have any troubles, google is a helpful tool or you can email me at hjx@andrew.cmu.edu.