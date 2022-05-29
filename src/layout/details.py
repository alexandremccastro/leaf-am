
import csv
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar
from kivy.utils import platform

Builder.load_file("./layout/details.kv")

class CustomOneLineItem(MDBoxLayout, RectangularRippleBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.number.text = "#" + str(kwargs["number"])
        self.ids.area.text = str(kwargs["area"])

    number = NumericProperty(0)
    area = NumericProperty(0)

class Details(MDScreen):
    modal_view = ObjectProperty(None)
    
    leaf_area_list = ListProperty([])
    total_leaves_area = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)

        self.file_manager = MDFileManager(
            exit_manager=self.close_file_manager,
            select_path=self.on_select_path,
            preview=True,
            selector='folder'
        )

    def open_file_manager(self):
        base_path = '/'

        if platform == 'android':
            from android.storage import primary_external_storage_path
            base_path = primary_external_storage_path()
        
        self.file_manager.show(base_path)

    def close_file_manager(self, *largs):
        self.file_manager.close()

    def on_select_path(self, path):
        self.export_csv_file(path)

    def on_enter(self, *largs):
        self.ids.list_items.clear_widgets()

        count = 1
        
        for area in self.leaf_area_list:
            rounded = round(area, 2)

            self.ids.list_items.add_widget(
                CustomOneLineItem(number=count,area=rounded)
            )

            count += 1
    
    def export_csv_file(self, path):
        areas = []
        count = 1

        for leaf_area in self.leaf_area_list:
            areas.append({'number': count, 'area': round(leaf_area, 2)})
            count += 1
        
        with open(f'{path}/leaf_am_last_analyze.csv', mode='w') as csv_file:
            fieldnames = ['number', 'area']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(areas)

        self.close_file_manager()

        self.snackbar = Snackbar(text="Analise exportada com sucesso!")
        self.snackbar.open()

    