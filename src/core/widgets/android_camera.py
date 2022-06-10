from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.properties import BooleanProperty, NumericProperty, ListProperty, ObjectProperty
import cv2

from core.detectors.board_detector import BoardDetector
from core.detectors.leaf_detector import LeafDetector
from core.graphics.point2d import Point2D
from core.widgets.base_camera import BaseCamera

class AndroidCamera(BaseCamera):
    areas_list = ListProperty([])
    is_calibrated = BooleanProperty(False)
    is_able_to_calibrate = BooleanProperty(False)
    selected_point = Point2D(0, 0)
    play = BooleanProperty(False)
    calibration_button = ObjectProperty(None)

    current_object_area = NumericProperty(0)
    
    total_leaves_area = NumericProperty(0)
    bottom_grid = ObjectProperty(None)
    box_top = ObjectProperty(None)

    total_leaf_area_label = ObjectProperty(None)
    calibration_pad_area = NumericProperty(0)
    calibration_area_in_cm2 = (7 * 0.5) * (9 * 0.5) # 5mm2 for each square

    leaf_detector = LeafDetector()
    board_detector = BoardDetector()

    # core method, called from superclass
    def countour_detect(self, frame):
        if self.is_calibrated:
            self.detect_leaves(frame)
        else:
            self.detect_board(frame)

    def define_coordinates(self, x, y):
        (heigth, width) = self.resolution
        self.selected_point.setX(int(x / self.width * width))
        self.selected_point.setY(heigth - int(y / self.height * heigth))
        self.current_object_area = 0
        self.remove_leaf_area_box()

    def draw_contour(self, frame, contour):
        imgcopy = frame.copy()
        cv2.fillPoly(imgcopy, [contour], (205, 255, 0))
        cv2.addWeighted(imgcopy, 0.5, frame, 1 - 0.5, 0, frame)

    def detect_board(self, frame):
        board_contour = self.board_detector.get_contour(frame)

        if not board_contour is None:
            self.draw_contour(frame, board_contour)
            self.current_object_area = cv2.contourArea(board_contour)
            self.is_able_to_calibrate = True
        else:
            self.current_object_area = 0
            self.is_able_to_calibrate = False

    def detect_leaves(self, frame):
        leaf_contour = self.leaf_detector.get_contour(frame, self.selected_point)

        if not leaf_contour is None:
            self.draw_contour(frame, leaf_contour)
            if self.current_object_area == 0:
                self.current_object_area = cv2.contourArea(leaf_contour)
                self.show_current_object_area()

    def get_current_leaf_area(self):
        return self.current_object_area / self.calibration_pad_area * self.calibration_area_in_cm2

    def setup_calibration(self, *largs):
        self.clear_widgets()
        self.selected_point.clear()

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

    def remove_leaf_area_box(self):
        if self.box_top:
            self.bottom_grid.height = 160
            self.bottom_grid.remove_widget(self.box_top)

    def add_leaf_area_to_total(self, *largs):
        current_leaf_area = self.get_current_leaf_area()
        self.total_leaves_area += current_leaf_area
        self.areas_list.append(current_leaf_area)
        self.total_leaf_area_label.text = str(round(self.total_leaves_area, 2))
        self.selected_point.clear()
        self.current_object_area = 0
        self.remove_leaf_area_box()

    def finish_analyzes(self, *largs):
        self.parent.parent.manager.get_screen("details").leaf_area_list = self.areas_list
        self.parent.parent.manager.get_screen("details").total_leaves_area = self.total_leaves_area
        self.parent.parent.manager.current = "details"

    def calibrate(self, *largs):
        if self.is_able_to_calibrate:
            self.calibration_pad_area = self.current_object_area
            self.is_calibrated = True
            self.selected_point.clear()
            self.show_measure_area()
