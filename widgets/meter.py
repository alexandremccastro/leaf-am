
from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton
from kivy.properties import BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.graphics.texture import Texture
from kivy.uix.camera import Camera
import numpy as np
import cv2

Builder.load_file('./widgets/meter.kv')

class AndroidCamera(Camera):
    resolution = ListProperty([640, 480])
    areas_list = ListProperty([])
    is_calibrated = BooleanProperty(False)
    is_able_to_calibrate = BooleanProperty(False)
    selected_point =  ListProperty([0, 0])
    play = BooleanProperty(False)
    index = NumericProperty(-1)
    calibration_button = ObjectProperty(None)

    current_object_area = NumericProperty(0)
    
    total_leaves_area = NumericProperty(0)
    bottom_grid = ObjectProperty(None)
    box_top = ObjectProperty(None)

    total_leaf_area_label = ObjectProperty(None)
    calibration_pad_area = NumericProperty(0)
    detected_calib_count = NumericProperty(0)
    calibration_area_in_cm2 = (7 * 0.5) * (9 * 0.5) # 5mm2 for each square

    
    def define_coordinates(self, touch):
        (x, y) = touch.pos
        (h, w) = self.resolution
        self.point_x = int(x / self.width * w)
        self.point_y = h - int(y / self.height * h)
        self.current_object_area = 0
        self.remove_leaf_area_box()
        return True

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

    def setup_calibration(self, *largs):
        self.clear_widgets()
        self.point_x = 0
        self.point_y = 0
        self.is_calibrated = False
        self.current_object_area = 0
        self.areas_list = []
        boxlayout = MDBoxLayout(orientation="vertical", padding=16,width=self.width, pos=[0, "10dp"])
        self.calibration_button = MDFillRoundFlatButton(
            text="Calibrar"
        )
        self.calibration_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.calibration_button.size_hint_x = 0.8
        self.calibration_button.bind(on_release=self.calibrate)

        boxlayout.add_widget(self.calibration_button)
        self.add_widget(boxlayout)

    def calibrate(self, *largs):
        if self.is_able_to_calibrate:
            self.calibration_pad_area = self.current_object_area
            self.is_calibrated = True
            self.clear_points()
            self.show_measure_area()

    def hide_snackbar(self, *largs):
        self.snackbar.dismiss()

    def show_measure_area(self):
        self.clear_widgets()
        self.total_leaves_area = 0
        self.current_object_area = 0
        self.bottom_grid = MDGridLayout(rows=2, cols=1, width=self.width, pos=(0, 0), size_hint=(None, None))
        self.bottom_grid.md_bg_color = (1, 1, 1, 1)
        self.bottom_grid.height = 160

        box_bottom = MDGridLayout(cols=3,rows=1, padding=32,width=self.width)
        box_bottom.md_bg_color = [0.40784313725490196, 0.6235294117647059, 0.2196078431372549, 1.0]
        total_text_label = MDLabel(text="Total")
        total_text_label.font_size = "24dp"
        self.total_leaf_area_label = MDLabel(text=str(round(self.total_leaves_area, 2)))
        self.total_leaf_area_label.font_size = "24dp"
        box_bottom.add_widget(total_text_label)
        box_bottom.add_widget(self.total_leaf_area_label)
        finish_button = MDFillRoundFlatButton(text="Finalizar")
        finish_button.bind(on_press=self.finish_analyzes)
        box_bottom.add_widget(finish_button)
        self.bottom_grid.add_widget(box_bottom)

        self.add_widget(self.bottom_grid)

    def finish_analyzes(self, *largs):
        self.parent.parent.manager.get_screen("details").leaf_area_list = self.areas_list
        self.parent.parent.manager.get_screen("details").total_leaves_area = self.total_leaves_area
        self.parent.parent.manager.current = "details"

    def on_tex(self, *largs):
        if self._camera._buffer is None:
            return None
        frame = self.frame_from_buf()

        self.frame_to_screen(frame)
        super(AndroidCamera, self).on_tex(*largs)

    def frame_from_buf(self):
        w, h = self.resolution
        frame = np.frombuffer(self._camera._buffer.tostring(), 'uint8').reshape((h + h // 2, w))
        frame_bgr = cv2.cvtColor(frame, 93)
        return np.rot90(frame_bgr, 3)

    def show_current_object_area(self):
        self.remove_leaf_area_box()
        self.box_top = MDGridLayout(cols=3,rows=1, padding=32,width=self.width)
        self.box_top.md_bg_color = [0.7725490196078432, 0.8823529411764706, 0.6470588235294118, 1.0]
        area_text_label = MDLabel(text="Area")
        area_text_label.font_size = "24dp"
        self.remove_leaf_area_box()
        current_leaf_area = round(self.get_current_leaf_area(), 2)

        leaf_area_label = MDLabel(text=str(current_leaf_area))
        leaf_area_label.text_color = [1, 1, 1, 1]
        leaf_area_label.font_size = "24dp"
        self.box_top.add_widget(area_text_label)
        self.box_top.add_widget(leaf_area_label)
        self.box_top.add_widget(MDFillRoundFlatButton(text="Adicionar", on_press=self.add_leaf_area_to_total))
        self.bottom_grid.height = 320
        self.bottom_grid.add_widget(self.box_top, 1)

    def add_leaf_area_to_total(self, *largs):
        current_leaf_area = self.get_current_leaf_area()
        self.total_leaves_area += current_leaf_area
        self.areas_list.append(current_leaf_area)
        self.total_leaf_area_label.text = str(round(self.total_leaves_area, 2))
        self.clear_points()
        self.current_object_area = 0
        self.remove_leaf_area_box()

    def clear_points(self):
        self.point_x = 0
        self.point_y = 0

    def get_current_leaf_area(self):
        return self.current_object_area / self.calibration_pad_area * self.calibration_area_in_cm2

    def remove_leaf_area_box(self):
        if self.box_top:
            self.bottom_grid.height = 160
            self.bottom_grid.remove_widget(self.box_top)

    def frame_to_screen(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.countour_detect(frame_rgb)

        flipped = np.flip(frame_rgb, 0)
        buf = flipped.tostring()
        if self.texture:
            self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

    def get_selected_contour(self, contours):
        selected_contour = None

        for cnt in contours:
            if (cv2.pointPolygonTest(cnt, [self.point_x, self.point_y], True) > 0):
                selected_contour = cnt
                break
        
        return selected_contour

    def countour_detect(self, frame):
        blur = cv2.GaussianBlur(frame, (5, 5), 1)

        if self.is_calibrated:
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
            selected_contour = self.get_selected_contour(contours)

            if not selected_contour is None:
                imgcopy = frame.copy()
                cv2.fillPoly(imgcopy, [selected_contour], (205, 255, 0))
                cv2.addWeighted(imgcopy, 0.5, frame, 1 - 0.5, 0, frame)

                if self.current_object_area == 0:
                    self.current_object_area = cv2.contourArea(selected_contour)
                    
                    if (self.is_calibrated):
                        self.show_current_object_area()
        else:
            gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(gray, 80, 255, cv2.ADAPTIVE_THRESH_MEAN_C)
            found_board, corners = cv2.findChessboardCorners(thresh, (8, 10), None, flags=cv2.CALIB_CB_ADAPTIVE_THRESH)

            if found_board:
                # 0, 7, 72, 79
                xy1 = corners[0].astype(np.uint)
                xy2 = corners[7].astype(np.uint)
                xy3 = corners[72].astype(np.uint)
                xy4 = corners[79].astype(np.uint)

                contour = np.array([xy1, xy2,xy4, xy3])
                imgcopy = frame.copy()
                cv2.fillPoly(imgcopy, [contour], (205, 255, 0))
                cv2.addWeighted(imgcopy, 0.5, frame, 1 - 0.5, 0, frame)
                self.current_object_area = cv2.contourArea(contour)
                self.is_able_to_calibrate = True
            else:
                self.current_object_area = 0
                self.is_able_to_calibrate = False

            

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
        if not self.ids.camera.calibration_button.collide_point(x, y) and not (self.ids.camera.bottom_grid and self.ids.camera.bottom_grid.collide_point(x, y)):
            self.ids.camera.define_coordinates(touch)

