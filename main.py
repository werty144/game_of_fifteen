from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import *
from random import shuffle
from os import path
from math import inf


class MenuScreen(Screen):
    pass


class RecordScreen(Screen):
    def on_enter(self, *args):
        storage = App.get_running_app().storage
        self.ids['fst'].text = '1. ' + storage['time']['fst']
        self.ids['snd'].text = '2. ' + storage['time']['snd']
        self.ids['thrd'].text = '3. ' + storage['time']['thrd']


class GameScreen(Screen):
    playground = ObjectProperty()
    time_label = ObjectProperty()
    win_label = ObjectProperty()
    clock_tick = NumericProperty(0.1)
    ticking_event = ObjectProperty()
    time_passed_ms = NumericProperty(0)

    def on_enter(self, *args):
        self.playground = Playground()
        self.win_label = Label(text='You win!', pos_hint={'center_x': 0.5, 'center_y': 0.5}, font_size=72,
                               halign='center')

        self.time_label = self.ids['time_label']
        self.time_passed_ms = 0
        self.ticking_event = Clock.schedule_interval(self.increase_time, self.clock_tick)

        self.add_widget(self.playground)

    def increase_time(self, dt):
        self.time_passed_ms += 1
        self.time_label.text = str_from_ms(self.time_passed_ms)

    def on_leave(self, *args):
        self.clear_widgets([self.win_label, self.playground])

    def win(self):
        self.ticking_event.cancel()
        self.remove_widget(self.playground)
        self.add_widget(self.win_label)
        self.manage_record()

    def manage_record(self):
        storage = App.get_running_app().storage
        cur_records = [storage['time']['fst'], storage['time']['snd'], storage['time']['thrd']]
        cur_records = list(map(ms_from_str, cur_records)) + [self.time_passed_ms]
        cur_records.sort()
        time = dict()
        for i, position in enumerate(['fst', 'snd', 'thrd']):
            time[position] = str_from_ms(cur_records[i])
        storage.put('time', **time)


def ms_from_str(time):
    if time == 'No results yet':
        return inf
    minutes, seconds = [int(i) for i in time.split(':')]
    return minutes * 600 + seconds * 10


def str_from_ms(time):
    if time == inf:
        return 'No results yet'
    seconds = time // 10
    minutes = seconds // 60
    return f'{minutes}:{seconds % 60}'


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
        # self.field = [[j + 1 for j in range(4 * i, 4 * (i + 1))] for i in range(4)]
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
                self.add_widget(Label(text=f'{self.field[i][j]}', center=(x, y), font_size=24))

    def check_win(self):
        if self.field == [[j + 1 for j in range(4*i, 4*(i + 1))] for i in range(4)]:
            self.parent.win()


class GameOfFifteenApp(App):
    storage = ObjectProperty()

    def build(self):
        self.init_storage()
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(RecordScreen(name='record'))
        sm.add_widget(GameScreen(name='game'))
        return sm

    def init_storage(self):
        self.storage = JsonStore('records.json')
        if path.exists('records.json'):
            return
        self.storage.put('time', fst='No results yet', snd='No results yet', thrd='No results yet')


if __name__ == '__main__':
    GameOfFifteenApp().run()
