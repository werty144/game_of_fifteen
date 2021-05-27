from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import *
from random import shuffle


class MenuScreen(Screen):
    pass


class GameScreen(Screen):
    playground = ObjectProperty()
    win_label = ObjectProperty()

    def on_enter(self, *args):
        self.playground = Playground()
        self.win_label = Label(text='You win!', pos_hint={'center_x': 0.5, 'center_y': 0.5}, font_size=72,
                               halign='center')
        self.add_widget(self.playground)

    def on_leave(self, *args):
        self.clear_widgets([self.win_label, self.playground])

    def win(self):
        self.remove_widget(self.playground)
        self.add_widget(self.win_label)


def is_even(sequence):
    my_count = 0
    for i, num in enumerate(sequence, start=1):
        if num == 16:
            continue
        my_count += sum(num > num2 for num2 in sequence[i:])
    return not my_count % 2


def find_16(sequence):
    return sequence.index(16) // 4


def generate_solvable_permutation():
    while True:
        attempt = list(range(1, 17))
        shuffle(attempt)
        row16 = find_16(attempt)
        if ((row16 == 0 or row16 == 2) and not is_even(attempt)) or ((row16 == 1 or row16 == 3) and is_even(attempt)):
            return [[attempt[i*4 + j] for j in range(4)] for i in range(4)]


class Playground(Widget):
    def __init__(self, **kwargs):
        self.bind(pos=self.create_grid)
        self.bind(pos=self.draw_tiles)
        self.line_width = 2
        self.field = generate_solvable_permutation()
        self.tiles = []
        super().__init__(**kwargs)

    def create_grid(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1)
            for i in range(5):
                Rectangle(pos=(self.x + self.width*(i/4), self.y), size=(self.line_width, self.height))
                Rectangle(pos=(self.x, self.y + self.height * (i/4)), size=(self.width, self.line_width))

    @staticmethod
    def get_neighbours(i, j):
        neighbours = []
        if i < 3:
            neighbours.append((i + 1, j))
        if i > 0:
            neighbours.append((i - 1, j))
        if j < 3:
            neighbours.append((i, j + 1))
        if j > 0:
            neighbours.append((i, j - 1))
        return neighbours

    def make_move(self, i, j):
        if self.field[i][j] == 16:
            return

        for neighbour_i, neighbour_j, in self.get_neighbours(i, j):
            if self.field[neighbour_i][neighbour_j] == 16:
                self.field[neighbour_i][neighbour_j] = self.field[i][j]
                self.field[i][j] = 16
                self.draw_tiles()
                self.check_win()
                return

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            x, y = self.to_widget(*touch.pos, relative=True)
            cell_size = self.width // 4
            i, j = round((self.height - y) // cell_size), round(x // cell_size)
            self.make_move(i, j)

    def get_cell_center(self, i, j):
        cell_size = self.width // 4
        return self.x + cell_size * (j + 0.5), self.y + self.height - cell_size * (i + 0.5)

    def draw_tiles(self, *args):
        self.clear_widgets(self.tiles)
        for i in range(4):
            for j in range(4):
                if self.field[i][j] == 16:
                    continue
                x, y = self.get_cell_center(i, j)
                self.add_widget(Label(text=f'{self.field[i][j]}', center=(x, y)))

    def check_win(self):
        if self.field == [[j + 1 for j in range(4*i, 4*(i + 1))] for i in range(4)]:
            self.parent.win()


class GameOfFifteenApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(MenuScreen(name='menu'))
        return sm


if __name__ == '__main__':
    GameOfFifteenApp().run()
