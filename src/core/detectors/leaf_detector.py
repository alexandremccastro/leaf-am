
from core.detectors.contour_detector import ContourDetector
import cv2
import numpy as np

from core.graphics.point2d import Point2D

class LeafDetector(ContourDetector):
  def get_contour(self, frame, point):
    blur = cv2.GaussianBlur(frame, (5, 5), 1)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # threshold of green in HSV space
    lower_green = np.array([13, 40, 14])
    upper_green = np.array([255, 255, 255])

    # preparing the mask to overlay
    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (3,3))
    close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)

    # find contours
    contours, _ = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return self.get_selected_contour(point, contours)

  # returns the countor that intersects the given point
  def get_selected_contour(self, point, contours):
    selected_contour = None

    for cnt in contours:
      if (cv2.pointPolygonTest(cnt, [point.getX(), point.getY()], True) > 0):
        selected_contour = cnt
        break
    
    return selected_contour
