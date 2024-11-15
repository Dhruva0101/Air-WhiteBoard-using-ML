# whiteboard/whiteboard.py
import cv2
import numpy as np
import os
import HandTrackingM as htm

class Whiteboard:
    def __init__(self):
        # Initialize brush thickness and eraser thickness
        self.brushThickness = 5
        self.eraserThickness = 70

        # Initialize canvas
        self.xp, self.yp = 0, 0
        self.imgCanvas = np.zeros((720, 1280, 3), np.uint8)

        # Load header images for brush color selection
        self.folderPath = "Header"
        self.myList = os.listdir(self.folderPath)
        self.overlaylist = []

        for imPath in self.myList:
            image = cv2.imread(f'{self.folderPath}/{imPath}')
            self.overlaylist.append(image)
        self.header = self.overlaylist[0]  # Default header (brush color selection)
        self.drawColor = (255, 0, 255)    # Default draw color

    def process(self, img, PosList):
        if len(PosList) != 0:
            x1, y1 = PosList[8][1:]  # Tip of index finger
            x2, y2 = PosList[12][1:]  # Tip of middle finger

            fingers = detector.fingersUp()

            # If two fingers are up, enter selection mode
            if fingers[1] and fingers[2]:
                self.xp, self.yp = 0, 0
                cv2.rectangle(img, (x1, y1 - 15), (x2, y2 + 15), self.drawColor, cv2.FILLED)
                print('Selection Mode')

                if y1 < 125:
                    if 250 < x1 < 450:
                        self.header = self.overlaylist[0]
                        self.drawColor = (255, 0, 255)
                    elif 550 < x1 < 750:
                        self.header = self.overlaylist[1]
                        self.drawColor = (255, 255, 255)
                    elif 800 < x1 < 950:
                        self.header = self.overlaylist[2]
                        self.drawColor = (0, 255, 0)
                    elif 1050 < x1 < 1200:
                        self.header = self.overlaylist[3]
                        self.drawColor = (0, 0, 0)

            # If only the index finger is up, enter drawing mode
            if fingers[1] and not fingers[2]:
                cv2.circle(img, (x1, y1), 15, self.drawColor, cv2.FILLED)
                if self.xp == 0 and self.yp == 0:
                    self.xp, self.yp = x1, y1

                if self.drawColor == (0, 0, 0):  # Eraser mode
                    cv2.line(img, (self.xp, self.yp), (x1, y1), self.drawColor, self.eraserThickness)
                    cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.drawColor, self.eraserThickness)
                else:  # Drawing mode
                    cv2.line(img, (self.xp, self.yp), (x1, y1), self.drawColor, self.brushThickness)
                    cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.drawColor, self.brushThickness)

                self.xp, self.yp = x1, y1

        # Convert the canvas to grayscale and invert it for blending
        imgGrey = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGrey, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

        # Combine the canvas with the original image
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, self.imgCanvas)

        # Set the header image (brush color selection)
        img[0:125, 0:1280] = self.header

        return img
