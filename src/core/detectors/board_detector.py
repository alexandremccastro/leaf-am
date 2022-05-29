
import cv2
import numpy as np

from core.detectors.contour_detector import ContourDetector

class BoardDetector(ContourDetector):
  def get_contour(self, frame):
    blur = cv2.GaussianBlur(frame, (5, 5), 1)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.ADAPTIVE_THRESH_MEAN_C)
    has_board, corners = cv2.findChessboardCorners(thresh, (8, 10), None, flags=cv2.CALIB_CB_ADAPTIVE_THRESH)

    contour = None

    if has_board:
      xy1 = corners[0].astype(np.uint)
      xy2 = corners[7].astype(np.uint)
      xy3 = corners[72].astype(np.uint)
      xy4 = corners[79].astype(np.uint)
      contour = np.array([xy1, xy2, xy4, xy3])
    
    return contour
