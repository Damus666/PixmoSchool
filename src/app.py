import guiscript as guis
import pygame
import sys
import json
import typing
if typing.TYPE_CHECKING:
    from .pixmoschool import PixmoSchool

from .data import Data
from .builder import AppBuilder
from .schoolutils import ErrorType, error_message
from .constants import *

class Application:
    def __init__(self, main: "PixmoSchool"):
        self.main = main
        self.screen = main.screen
        
        self.done_hws = []
        with open("data/homeworks.json", "r") as hws_file:
            self.done_hws = json.load(hws_file)["done"]
        
        self.uimanager = guis.Manager(self.screen, is_current=False,
                                        gss_paths=["assets/pixmoschool.gss"], 
                                        gss_variables={"MULT": MULT, "ANIM": ANIM_TIME})
        
    def build(self):
        self.loading_screen()
        result = self.main.user.download_data()
        if result != ErrorType.ok:
            self.main.back_to_login(error_message(result), self.main.user.userid, self.main.user.password)
            return
        self.data = Data(self)
        self.builder = AppBuilder(self)
        
    def enter(self):
        self.uimanager.set_current()
        
    def destroy(self):
        self.uimanager.destroy()
        
    def refresh_done_hws(self):
        with open("data/homeworks.json", "w") as hws_file:
            json.dump({
                "done":self.done_hws
            }, hws_file)
        
    def loading_screen(self):
        pygame.display.set_caption(APP_NAME)
        
        self.screen.fill(COLORS["disabledoutline"])
        txt_surf = pygame.font.SysFont("Segoe UI", 50).render(LOADING_MSG, True, "white")
        txt_rect = txt_surf.get_rect(center=(W//2, H//2))
        self.screen.blit(txt_surf, txt_rect)
        
        pygame.display.flip()
        
    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.uimanager.event(event)
        
        self.screen.fill(COLORS["disabledbg"])
        
        self.uimanager.logic()
        guis.static_logic()
        
        self.uimanager.render()
            