
from abc import ABC, abstractmethod

class ContourDetector(ABC):
    @abstractmethod
    def get_contour(self, frame, point = None):
        pass

