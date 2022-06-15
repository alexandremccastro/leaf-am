
from core.detectors.contour_detector import ContourDetector
import cv2
import numpy as np

from core.graphics.point2d import Point2D

class LeafDetector(ContourDetector):
  def get_contour(self, frame, point):
    blur = cv2.blur(frame, (3,3))
    lab = cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)

    # only use the a channel to find objects
    a_channel = lab[:,:,1]

    rt, th = cv2.threshold(a_channel,105,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ERODE, (3,3))
    close = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=3)

    # mask the result with the original image
    masked = cv2.bitwise_and(frame, frame, mask = close)
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)

    contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return self.get_selected_contour(point, contours)

  # returns the countor that intersects the given point
  def get_selected_contour(self, point, contours):
    selected_contour = None

    for cnt in contours:
      if (cv2.pointPolygonTest(cnt, [point.getX(), point.getY()], True) > 0):
        selected_contour = cnt
        break
    
    return selected_contour
