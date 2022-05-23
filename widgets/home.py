
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder

Builder.load_file('./widgets/home.kv')

class Home(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
    
    
