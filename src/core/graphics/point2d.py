
class Point2D():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def setX(self, x):
        self.x = x
    
    def getX(self):
        return self.x

    def setY(self, y):
        self.y = y

    def getY(self):
        return self.y
    
    def clear(self):
        self.x = 0
        self.y = 0
