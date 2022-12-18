#!/usr/bin/env python3

from asciimatics.widgets import Frame, Layout, Divider, Button, Text
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
from asciimatics.parsers import AsciimaticsParser

class Randul1(Layout):
    def __init__(self, frame, active_tab_idx):
        cols  = [1, 1, 1, 1]  
        super().__init__(cols)
        self._frame = frame
        btns = [Button("---", self._on_click_Q),
                Button("Display", self._on_click_Q),
                Button("---", self._on_click_Q),
                Text(name="RO", readonly=True),
                Button("Q", self._on_click_Q),
                Button(":", self._on_click_impartit),
                Button("clear", self._on_click_clear),
                Button("", self._on_click_clear),
                Button("7", self._on_click_sapte),
                Button("8", self._on_click_opt),
                Button("9", self._on_click_noua),
                Button("*", self._on_click_inmultire),
                Button("4", self._on_click_patru),
                Button("5", self._on_click_cinci),
                Button("6", self._on_click_sase),
                Button("-", self._on_click_minus),
                Button("1", self._on_click_unu),
                Button("2", self._on_click_doi),
                Button("3", self._on_click_trei),
                Button("+", self._on_click_plus),
                Button("0", self._on_click_zero),
                Button(",", self._on_click_virgula),
                Button("=", self._on_click_egal),
                Button("", self._on_click_clear)]
        
        for i, btn in enumerate(btns[:4]):
            self._header = btn
            self._header.value = "ecran"
            self.add_widget(self._header, i)
            self.add_widget(Divider(), i)
        for i, btn in enumerate(btns[4:8]):
            self.add_widget(btn, i)
            self.add_widget(Divider(), i)
        for i, btn in enumerate(btns[8:12]):
            self.add_widget(btn, i)
            self.add_widget(Divider(), i)
        for i, btn in enumerate(btns[12:16]):
            self.add_widget(btn, i)
            self.add_widget(Divider(), i)
        for i, btn in enumerate(btns[16:20]):
            self.add_widget(btn, i)
            self.add_widget(Divider(), i)
        for i, btn in enumerate(btns[20:24]):
            self.add_widget(btn, i)
        btns[active_tab_idx].disabled = False
    
    def _on_click_Q(self):
        raise StopApplication("Quit")

    def _on_click_impartit(self):
        self.save()
        value ="test"

    def _on_click_clear(self):
        raise NextScene("Tab1")

    def _on_click_sapte(self):
        ecran = 7 
        raise NextScene("Tab1")

    def _on_click_opt(self):
        raise NextScene("Tab1")

    def _on_click_noua(self):
        raise NextScene("Tab1")
    
    def _on_click_inmultire(self):
        raise NextScene("Tab1")
    
    def _on_click_patru(self):
        raise NextScene("Tab1")

    def _on_click_cinci(self):
        raise NextScene("Tab1")

    def _on_click_sase(self):
        raise NextScene("Tab1")
    
    def _on_click_minus(self):
        raise NextScene("Tab1")
    
    def _on_click_unu(self):
        raise NextScene("Tab1")

    def _on_click_doi(self):
        raise NextScene("Tab1")

    def _on_click_trei(self):
        raise NextScene("Tab1")
    
    def _on_click_plus(self):
        raise NextScene("Tab1")

    def _on_click_zero(self):
        raise NextScene("Tab1")

    def _on_click_virgula(self):
        raise NextScene("Tab1")

    def _on_click_egal(self):
        raise NextScene("Tab1")

class RootPage(Frame):
    def __init__(self, screen):
        super().__init__(screen,
                         screen.height,
                         screen.width,
                         can_scroll=False,
                         title="Calculator")
        layout1 = Layout([1], fill_frame=True)
        self.add_layout(layout1)

        layout2 = Randul1(self, 0)
        self.add_layout(layout2)
        self.fix()

def demo(screen, scene):
    scenes = [
        Scene([RootPage(screen)], -1, name="Tab1"),
    ]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene