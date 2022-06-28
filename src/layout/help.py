
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

Builder.load_file('./layout/help.kv')

class Help(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)