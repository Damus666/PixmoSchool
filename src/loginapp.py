import pygame
import typing
import sys
import json
import guiscript as guis
if typing.TYPE_CHECKING:
    from .pixmoschool import PixmoSchool
    
from .constants import *
from .schoolutils import ErrorType, error_message
    
class LoginApp:
    def __init__(self, main:"PixmoSchool"):
        self.main = main
        self.screen = main.screen
        
        self.uimanager = guis.Manager(self.screen, is_current=False,
                                        gss_paths=["assets/pixmoschool.gss"], 
                                        gss_variables={"MULT": MULT, "ANIM": ANIM_TIME})
        
    def enter(self):
        self.uimanager.set_current()
        
    def on_login_click(self):
        userid, password = self.userid_entry.get_text().strip(), self.password_entry.get_text().strip()
        if not userid or not password:
            self.error_label.set_text("You must type a user id and a password to login")
            return
        result = self.main.user.login(userid, password)
        if result == ErrorType.ok:
            if self.remember_check.get_selected():
                with open("data/login.json", "w") as login_file:
                    json.dump({"userid": userid, "password": password}, login_file)
            self.main.enter_app()
        elif result == ErrorType.credentials:
            self.error_label.set_text(error_message(result))
            self.userid_entry.set_text("")
            self.password_entry.set_text("")
        else:
            self.error_label.set_text(error_message(result))
            
    def on_exit_click(self):
        pygame.quit()
        sys.exit()
        
    def build(self, error_message="", userid="", password=""):
        with guis.VStack(guis.SizeR(W, H), style_id="pixeldisabled"):
            guis.Label(APP_NAME, guis.ZeroR(), style_id="titlefont;fill_x;textgrow")
            guis.Label("LOGIN", guis.ZeroR(), style_id="subtitlefont;fill_x;textgrow")
            
            guis.Element(guis.SizeR(10, ENTRY_HEIGHT*2), style_id="invisible")
            
            self.error_label = guis.Label(error_message, guis.ZeroR(), style_id="fill_x;textgrow;errorlabel")
            
            with guis.HStack(guis.ZeroR(), style_id="invis_cont;fill_x;grow_y"):
                with guis.VStack(guis.ZeroR(), style_id="invis_cont;fill_x;grow_y;padding"):
                    guis.Label("User ID: ", guis.SizeR(0, ENTRY_HEIGHT), style_id="fill_x;bigfont;alignright")
                    guis.Label("Password: ", guis.SizeR(0, ENTRY_HEIGHT), style_id="fill_x;bigfont;alignright")
                with guis.VStack(guis.ZeroR(), style_id="invis_cont;fill_x;grow_y;padding"):
                    self.userid_entry = guis.Entry(guis.SizeR(W//4, ENTRY_HEIGHT), style_id="pixelbg;alignleft", 
                                                   settings=guis.EntrySettings("Enter user id...")).set_text(userid)
                    self.password_entry = guis.Entry(guis.SizeR(W//4, ENTRY_HEIGHT), style_id="pixelbg;alignleft",
                                                    settings=guis.EntrySettings("Enter password...")).set_text(password)
                    
            guis.Element(guis.SizeR(10, ENTRY_HEIGHT*2), style_id="invisible")
                    
            guis.Button("Login", guis.SizeR(W//6, ENTRY_HEIGHT), style_id="pixelbg")\
                .status.add_listener("on_click", self.on_login_click).element
            with guis.HStack(guis.ZeroR(), style_id="invis_cont;grow_x;grow_y;stackpadding"):
                guis.Label("Remember me", guis.ZeroR(), style_id="textgrow;textgrowx")
                self.remember_check = guis.Checkbox(guis.SizeR(GRADE_SIZE/3.2, GRADE_SIZE/3.2), False, style_id="donecheckbox;pixelbg")
        exitbtn = guis.Button("close", guis.ZeroR(), style_id="textgrow;textgrowx;pixelbg;boxpadding;extrabtn").status.add_listener("on_click", self.on_exit_click).element
        exitbtn.set_absolute_pos((W-exitbtn.relative_rect.w-8, 8))
        
    def destroy(self):
        self.uimanager.destroy()
        
    def run(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.uimanager.event(e)
    
        self.screen.fill(COLORS["disabledbg"])
        
        self.uimanager.logic()
        guis.static_logic()
        
        self.uimanager.render()
