import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from time import sleep

# Setup
cap = cv2.VideoCapture(0)
cap.set(3, 1200)
cap.set(4, 700)
detector = HandDetector(detectionCon=0.8)

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ","],
    ["space"]
]

finalText = ""

# Button class
class Button():
    def __init__(self, pos, text, size=(75, 75)):
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self, image, color=(255, 0, 255), alpha=0.5):
        x, y = self.pos
        w, h = self.size

        # Create transparent layer
        overlay = image.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        # Draw text
        fontColor = (0, 0, 0) if color == (0, 255, 0) else (255, 255, 255)
        cv2.putText(image, self.text, (x + 20, y + 50),
                    cv2.FONT_HERSHEY_PLAIN, 4, fontColor, 4)

    def isHovered(self, cursor):
        x, y = self.pos
        w, h = self.size
        return x < cursor[0] < x + w and y < cursor[1] < y + h

# Create button list only once
buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        if key == "space":
            buttonList.append(Button([400, 100 * i + 50], " ", size=(500, 75)))
        else:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    # Draw all buttons with base transparency
    for button in buttonList:
        button.draw(img, color=(255, 0, 255), alpha=0.5)

    # Check finger position and detect click
    if hands:
        lmList = hands[0]["lmList"]
        index_tip = lmList[8][0:2]
        middle_tip = lmList[12][0:2]
        length, _, _ = detector.findDistance(index_tip, middle_tip, img)

        for button in buttonList:
            if button.isHovered(index_tip):
                x, y = button.pos
                w, h = button.size

                if length < 40:
                    # Click effect
                    button.draw(img, color=(0, 255, 0), alpha=1)
                    finalText += button.text
                    sleep(0.4)
                else:
                    # Hover effect (darker)
                    button.draw(img, color=(175, 0, 175), alpha=0.8)

    # Draw final text box (translucent background)
    overlay = img.copy()
    cv2.rectangle(overlay, (300, 500), (950, 650), (0, 255, 175), cv2.FILLED)
    cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)
    cv2.putText(img, finalText, (320, 600),
                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # Show
    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
