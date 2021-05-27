from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen


class MenuScreen(Screen):
    pass


class PlaygroundScreen(Screen):
    def on_enter(self, *args):
        self.add_widget(Playground())


class Playground(Widget):
    pass


class Menu(Widget):
    pass


class GameOfFifteenApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(PlaygroundScreen(name='playground'))
        return sm


if __name__ == '__main__':
    GameOfFifteenApp().run()
