
from abc import abstractmethod
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty
import numpy as np
import cv2

class BaseCamera(Camera):
    resolution = ListProperty([1280, 720])

    def on_play(self, instance, value):
        if not self._camera:
            return
        if value:
            self._camera.start()
            self._camera.bind(on_texture=self.on_tex)
        else:
            self._camera.stop()

    def _camera_loaded(self, *largs):
        self.texture = Texture.create(size=np.flip(self.resolution), colorfmt='rgb')
        self.texture_size = list(self.texture.size)

    def on_tex(self, *largs):
        if self._camera._buffer is None:
            return None
        frame = self.frame_from_buf()

        self.frame_to_screen(frame)
        super(BaseCamera, self).on_tex(*largs)

    def frame_from_buf(self):
        w, h = self.resolution
        frame = np.frombuffer(self._camera._buffer.tostring(), 'uint8').reshape((h + h // 2, w))
        frame_bgr = cv2.cvtColor(frame, 93)
        return np.rot90(frame_bgr, 3)

    def frame_to_screen(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.countour_detect(frame_rgb)

        flipped = np.flip(frame_rgb, 0)
        buf = flipped.tostring()
        if self.texture:
            self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

    @abstractmethod
    def contour_detect(self, frame):
      pass
