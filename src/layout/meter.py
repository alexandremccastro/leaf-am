
from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen
from core.widgets.leaf_camera import LeafCamera

Builder.load_file('./layout/meter.kv')

class Meter(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
    
    def on_enter(self, *largs):
        self.ids.camera.setup_calibration()
        self.ids.camera.play = True

    def on_leave(self, *largs):
        self.ids.camera.play = False

    def on_resume(self, *largs):
        self.ids.camera.play = True

    def setup_points(self, touch):
        (x, y) = touch.pos

        if not self.collide_calibration_btn(x, y) and not self.collide_bottom_grid(x, y):
            self.ids.camera.define_coordinates(x, y)

    def collide_calibration_btn(self, x, y):
        return self.ids.camera.calibration_button.collide_point(x, y)

    def collide_bottom_grid(self, x, y):
        return self.has_bottom_grid() and self.ids.camera.bottom_grid.collide_point(x, y)

    def has_bottom_grid(self):
        return self.ids.camera.bottom_grid

