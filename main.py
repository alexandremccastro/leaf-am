
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.properties import ObjectProperty, BooleanProperty
from widgets.home import Home
from widgets.setup import Setup
from widgets.meter import Meter
from widgets.details import Details
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.snackbar import Snackbar
from kivy.clock import mainthread

Clock.max_iteration = 10

class LeafAMApp(MDApp):
    manager = ObjectProperty()
    closing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def is_android(self):
        return platform == 'android'
    
    def check_camera_permission(self):
        if not self.is_android():
            return True
        from android.permissions import Permission, check_permission
        return check_permission(Permission.CAMERA)

    def check_request_permissions(self, callback=None):

        had_permissions = self.check_camera_permission()
        if not had_permissions:
            from android.permissions import Permission, request_permissions
            permissions = [Permission.CAMERA, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
            request_permissions(permissions, callback)
            had_permissions = self.check_camera_permission()

        return had_permissions
    
    def build(self):
        self.bind(on_start=self.bind_screen_switcher)
        self.theme_cls.primary_palette = 'LightGreen'
        self.manager = ScreenManager()

        @mainthread
        def on_permissions_callback(permissions, grant_results):
            
            if all(grant_results):
                self.setup_screens(self.manager)
                return True
            else:
                self.check_request_permissions(callback=on_permissions_callback)
        
        if self.check_request_permissions(callback=on_permissions_callback):
            self.setup_screens(self.manager)

        return self.manager
    
    def setup_screens(self, manager):
        manager.add_widget(Home())
        manager.add_widget(Setup())
        manager.add_widget(Meter())
        manager.add_widget(Details())
        
    
    def unset_close_status(self, *larggs):
        self.closing = False

    def bind_screen_switcher(self, *args):
        Window.bind(on_keyboard=self.handle_back)

    def handle_back(self, window, keycode1, keycode2, text, modifiers):
        if keycode1 in [27, 1001]:
            previous = self.manager.previous()

            if (self.manager.current == 'home'):
                
                if self.closing == True:
                    self.stop()
                else:
                    self.snackbar = Snackbar(text="Pressione novamente para sair.")
                    self.snackbar.bind(on_dismiss=self.unset_close_status)
                    self.snackbar.open()
                    self.closing = True
            else:
                found = False

                for screen in self.manager.screens:
                    if screen.name == previous:
                        found = True
                
                if found:
                    self.manager.transition = SlideTransition(direction="right")
                    self.manager.current = previous
                
        return True

if __name__ == '__main__':
    LeafAMApp().run()
