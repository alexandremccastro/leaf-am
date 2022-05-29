
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder

Builder.load_file('./layout/setup.kv')

class Setup(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
