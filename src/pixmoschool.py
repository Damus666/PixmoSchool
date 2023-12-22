import pygame
import json

from .constants import *
from .app import Application
from .loginapp import LoginApp
from .schoolutils import ClassevivaUser, ErrorType, error_message

class PixmoSchool:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZES)
        self.clock = pygame.Clock()
        
        with open("data/login.json", "r") as login_file:
            login_data = json.load(login_file)
            userid, password = login_data["userid"], login_data["password"]
        
        self.user = ClassevivaUser(self)
        self.login_app = LoginApp(self)
        self.app = Application(self)
        
        self.selected_app = None
        if not userid or not password:
            self.login_app.enter()
            self.login_app.build()
            self.selected_app = self.login_app
        else:
            result = self.user.login(userid, password)
            if result == ErrorType.ok:
                self.app.enter()
                self.app.build()
                self.selected_app = self.app
            elif result == ErrorType.credentials:
                with open("data/login.json", "w") as login_file:
                    json.dump({"userid":"", "password":""}, login_file)
                self.login_app.enter()
                self.login_app.build(error_message(result))
                self.selected_app = self.login_app
            else:
                self.back_to_login(error_message(result), userid, password)
                
    def enter_app(self):
        self.login_app.destroy()
        self.app.enter()
        self.app.build()
        self.selected_app = self.app
        
    def back_to_login(self, error_message="", userid="", password=""):
        self.app.destroy()
        self.login_app.enter()
        self.login_app.build(error_message, userid, password)
        self.selected_app = self.login_app
        
    def run(self):
        while True:
            self.selected_app.run()
            
            self.clock.tick_busy_loop(FPS)
            pygame.display.set_caption(APP_NAME)
            pygame.display.flip()