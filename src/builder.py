import guiscript as guis
import datetime
import typing
import pygame
import json
import sys
if typing.TYPE_CHECKING:
    from .app import Application
    
from .constants import *
from .data import Grade, AgendaDay, Homework, Event


class AppBuilder:
    def __init__(self, app: "Application"):
        self.app = app
        self.data = app.data
        self.grade_containers: dict[str, guis.VStack] = dict.fromkeys(GRADES_BUTTONS, None)
        self.grade_buttons: list[guis.Button] = []
        self.subject_titles: list[guis.HStack] = []
        self.lesson_titles: list[guis.Button] = []
        self.selected_day_cont: guis.VStack = None
        self.selected_calendar: guis.Button = None
        self.build()
        
    def on_grade_category_select(self, button: guis.Button):
        for btn in self.grade_buttons:
            if btn.text.text != button.text.text:
                btn.status.deselect()
        for name, container in self.grade_containers.items():
            if name == button.text.text:
                if container is None:
                    container = self.build_grades_section_cont(name)
                container.show()
            else:
                if container is not None:
                    if name == "Subject Grades":
                        for subj_title in self.subject_titles:
                            if subj_title.get_attr("toggle_cont").visible:
                                subj_title.get_attr("toggle_cont").hide()
                    elif name == "Lessons":
                        for lesson_title in self.lesson_titles:
                            if lesson_title.get_attr("toggle_cont").visible:
                                lesson_title.get_attr("toggle_cont").hide()
                    container.hide()
                    
    def on_subject_average_click(self, average: guis.HStack):
        toggle_cont: guis.HStack = average.get_attr("toggle_cont")
        toggle_cont.hide() if toggle_cont.visible else toggle_cont.show()
                    
    def on_grade_category_deselect(self, button: guis.Button):
        button.status.select()
        
    def on_calendar_click(self, button: guis.Button):
        if self.selected_calendar is not None and button.get_attr("date") == self.selected_calendar.get_attr("date"):
            return
        
        if self.selected_day_cont is not None:
            self.selected_day_cont.status.add_listener("on_animation_end", self.on_calendar_animation_end)\
                .element.set_ignore(stack=True).animate_offset_x(self.selected_day_cont.relative_rect.w+100, 300, guis.AnimRepeatMode.norepeat)
            
        if self.selected_calendar is not None:
            if self.selected_calendar.get_attr("is_today"):
                self.selected_calendar.set_style_id("fill_y;calendartoday")
            elif self.selected_calendar.get_attr("is_tomorrow"):
                self.selected_calendar.set_style_id("fill_y;calendartomorrow")
            else:
                self.selected_calendar.set_style_id("fill_y;calendar")
        self.build_agenda_day(button.get_attr("date"))
        self.selected_calendar = button
        button.set_style_id("fill_y;calendarselected")
        
    def on_calendar_animation_end(self, element: guis.VStack, animation: guis.PropertyAnimType):
        element.destroy()
        
    def on_done_select(self, check: guis.Checkbox):
        if check.get_attr("hwid") not in self.app.done_hws:
            self.app.done_hws.append(check.get_attr("hwid"))
        check.get_attr("title").set_style_id(check.get_attr("title").style_id+";donetitle")
        self.app.refresh_done_hws()
        
    def on_done_deselect(self, check: guis.Checkbox):
        self.app.done_hws.remove(check.get_attr("hwid"))
        check.get_attr("title").set_style_id(check.get_attr("title").style_id.replace(";donetitle", ""))
        self.app.refresh_done_hws()
        
    def on_logout_click(self):
        with open("data/login.json", "w") as login_file:
            json.dump({"userid":"", "password":""}, login_file)
        self.app.main.back_to_login("You manually log out. Insert credentials to continue")
        
    def on_exit_click(self):
        pygame.quit()
        sys.exit()
        
    def on_refresh_click(self):
        self.app.enter()
        self.app.destroy()
        self.app.build()
        
    def build(self):
        with guis.HStack(guis.SizeR(W, H), style_id="invis_cont"):
            with guis.VStack(guis.SizeR(GRADES_ROOT_W, 0), style_id="fill_y;pixeldisabled") as self.grades_root:
                self.build_grades_root()
                
            with guis.VStack(guis.ZeroR(), style_id="fill;pixeldisabled") as self.agenda_root:
                self.build_agenda_root()
        self.build_extra_buttons()
    
    def build_extra_buttons(self):   
        logout_button = guis.Button("logout", guis.ZeroR(), style_id="pixelbg;textgrow;textgrowx;textpadding;extrabtn").status.add_listener("on_click", self.on_logout_click).element
        exit_btn = guis.Button("close", guis.ZeroR(), style_id="pixelbg;textgrow;textgrowx;textpadding;extrabtn").status.add_listener("on_click", self.on_exit_click).element
        refresh_btn = guis.Button("refresh", guis.ZeroR(), style_id="pixelbg;textgrow;textgrowx;textpadding;extrabtn").status.add_listener("on_click", self.on_refresh_click).element
        exit_btn.set_relative_pos((
            W-exit_btn.relative_rect.w-8,
            H-exit_btn.relative_rect.h-8
        ))
        logout_button.set_relative_pos((
            W-logout_button.relative_rect.w-12-exit_btn.relative_rect.w,
            H-logout_button.relative_rect.h-8
        ))
        refresh_btn.set_relative_pos((
            W-logout_button.relative_rect.w-exit_btn.relative_rect.w-refresh_btn.relative_rect.w-16,
            H-refresh_btn.relative_rect.h-8,
        ))
                
    def build_grades_root(self):
        with guis.HStack(guis.SizeR(0, BUTTON_BAR_H), style_id="fill_x;invis_cont"):
            for name in GRADES_BUTTONS:
                btn = guis.Button(name, guis.ZeroR(), style_id="fill;pixelbg;bigfont", selectable=True)\
                    .status.add_multi_listeners(on_select=self.on_grade_category_select, on_deselect=self.on_grade_category_deselect).element
                self.grade_buttons.append(btn)
                if name == "All Grades": btn.status.select()
            
        with guis.VStack(guis.ZeroR(), style_id="fill;pixeldisabled;anchortop;maskpadding;floatingscrollbars", scrollbars_style_id="noscrollbar") as grades_all_cont:
            self.build_grades_all()
        self.grade_containers["All Grades"] = grades_all_cont
        
    def build_grades_all(self):
        self.build_average_title(f"Average ({len(self.data.grades["grades"])})", self.data.grades["average"], False)
        guis.HLine(guis.SizeR(0, 2), style_id="fill_x;disabledoutlinecol")
        for grade in reversed(self.data.grades["grades"]):
            self.build_full_grade(grade)
        
    def build_grades_subject(self):
        guis.HLine(guis.SizeR(0, 2), style_id="fill_x;disabledoutlinecol")
        for name, subject in self.data.subject_grades.items():
            prof_txt = f" | "+", ".join(self.data.subject_profs[name]) if not HIDE_PROFS else ""
            average_cont = self.build_average_title(f"{SUBJ_NAME_TABLE.get(name.lower(), "Unknown")}{prof_txt} ({len(subject["grades"])})", subject["average"], True)\
                                .status.add_listener("on_click", self.on_subject_average_click).element
            with guis.HStack(guis.ZeroR(), style_id="fill_x;grow_y;pixeldisabled").hide() as grades_cont:
                guis.Element(guis.SizeR(SEPARATOR_W, 0), style_id="fill_y;invis_cont").deactivate()
                with guis.VStack(guis.ZeroR(), style_id="fill_x;invis_cont;grow_y"):
                    for grade in reversed(subject["grades"]):
                        self.build_grade(grade)
            average_cont.set_attr("toggle_cont", grades_cont)
            self.subject_titles.append(average_cont)
            
    def build_lessons(self):
        guis.HLine(guis.SizeR(0, 2), style_id="fill_x;disabledoutlinecol")
        for subjname, lessons in self.data.subject_lessons.items():
            prof_txt = (f" | "+(", ".join(self.data.subject_profs[subjname]))) if not HIDE_PROFS and subjname in self.data.subject_profs else ""
            toggle_btn = guis.Button(f"{SUBJ_NAME_TABLE.get(subjname.lower(), "Unknown")}{prof_txt} ({len(lessons)})", guis.SizeR(0, GRADE_SIZE//2), style_id="fill_x;alignleft;bigfont;pixelbg")\
                .status.add_listener("on_click", self.on_subject_average_click).element
            with guis.HStack(guis.ZeroR(), style_id="fill_x;grow_y;pixeldisabled").hide() as lessons_cont:
                guis.Element(guis.SizeR(SEPARATOR_W, 0), style_id="fill_y;invis_cont").deactivate()
                with guis.VStack(guis.ZeroR(), style_id="fill_x;invis_cont;grow_y"):
                    for lesson in lessons:
                        with guis.VStack(guis.ZeroR(), style_id="fill_x;grow_y;invis_cont"):
                            guis.Label(f"{lesson.datedisplay} | {lesson.type}", guis.SizeR(0,10), style_id="fill_x;alignleft;textgrow")
                            guis.Label(lesson.lesson if lesson.lesson else "No details", guis.SizeR(0,10), style_id="fill_x;smallfont;disabledtxt;alignleft;textgrow")
            toggle_btn.set_attr("toggle_cont", lessons_cont)
            self.lesson_titles.append(toggle_btn)
            
    def build_average_title(self, txt, average, active):
        gradetype = "good" if average >= 6 else "bad"
        extra_style = ";pixelbg" if active else ";invis_cont"
        with guis.HStack(guis.SizeR(0, GRADE_SIZE), style_id=f"fill_x{extra_style}") as main_cont:
            guis.Label(str(average), guis.SizeR(GRADE_SIZE, 0), style_id=f"fill_y;bigfont;{gradetype}").set_ignore(raycast=active)
            guis.Label(txt, guis.ZeroR(), style_id="fill;alignleft").set_ignore(raycast=active)
        if active: main_cont.activate()
        return main_cont
        
    def build_full_grade(self, grade: Grade):
        with guis.HStack(guis.SizeR(0, GRADE_SIZE), style_id="fill_x;invis_cont"):
            guis.Label(grade.display, guis.SizeR(GRADE_SIZE, 0), style_id=f"fill_y;bigfont;{grade.colortype}")
            with guis.VStack(guis.ZeroR(), style_id="fill;invis_cont;anchorcenter"):
                profs_txt = f" | {grade.profsdisplay}" if not HIDE_PROFS else ""
                if len(profs_txt) > 20:
                    profs_txt = " | Many Profs"
                guis.Label(f"{grade.subject}{profs_txt}", guis.ZeroR(), style_id="fill;alignleft;alignbottomleft")
                guis.Label(f"{grade.mode} | {grade.period} | {grade.date}", guis.ZeroR(), style_id="fill;alignleft;smallfont;alignbottomleft;disabledtxt")
                guis.Label(f"Current Avg: {grade.average}", guis.ZeroR(), style_id="fill;alignleft;smallfont;aligntopleft;disabledtxt")
        
    def build_grade(self, grade: Grade):
        with guis.HStack(guis.SizeR(0, GRADE_SIZE), style_id="fill_x;invis_cont"):
            guis.Label(grade.display, guis.SizeR(GRADE_SIZE, 0), style_id=f"fill_y;bigfont;{grade.colortype}")
            with guis.VStack(guis.ZeroR(), style_id="fill;invis_cont;anchorcenter"):
                guis.Label(f"{grade.mode}", guis.ZeroR(), style_id="fill;alignleft;smallfont;alignbottomleft")
                guis.Label(f"{grade.period} | {grade.date}", guis.ZeroR(), style_id="fill;alignleft;smallfont;aligntopleft;disabledtxt")
    
    def build_grades_section_cont(self, name):
        with self.grades_root:
            if name == "Subject Grades":
                with guis.VStack(guis.ZeroR(), style_id="fill;invis_cont;anchortop", scrollbars_style_id="noscrollbar") as cont:
                    self.build_grades_subject()
                    
            elif name == "Lessons":
                with guis.VStack(guis.ZeroR(), style_id="fill;invis_cont;anchortop", scrollbars_style_id="noscrollbar") as cont:
                    self.build_lessons()
                    
        self.grade_containers[name] = cont
        return cont
        
    def build_agenda_root(self):
        with guis.HStack(guis.SizeR(0, GRADE_SIZE), style_id="fill_x;pixeldisabled;maskpadding", scrollbars_style_id="noscrollbar"):
            self.build_agenda_calendar()
            
    def build_agenda_calendar(self):
        last_calendar, was_today_or_tomorrow = None, False
        date_events_items = list(self.data.date_events.items())
        for i, (date, day) in enumerate(date_events_items):
            now = datetime.datetime.now()
            split_date = date.split("-")
            is_today = now.year == int(split_date[0]) and now.month == int(split_date[1]) and now.day == int(split_date[2])
            is_tomorrow = False
            if not was_today_or_tomorrow and i < len(date_events_items)-1:
                next_date = date_events_items[i+1][0].split("-")
                if ((now.year == int(split_date[0]) and now.month == int(split_date[1]) and now.day < int(split_date[2]))or\
                    (now.year == int(split_date[0]) and now.month < int(split_date[1]))) and \
                        ((now.year == int(next_date[0]) and now.month == int(next_date[1]) and now.day >= int(next_date[2])) or \
                            ((now.year == int(next_date[0]) and now.month > int(next_date[1])))):
                    is_tomorrow = True
            style_extra = "today" if is_today else "tomorrow" if is_tomorrow else ""
            btn = guis.Button(date.split("-", 1)[-1].replace("-", "\n"), guis.SizeR(GRADE_SIZE-10, 0), style_id=f"fill_y;calendar{style_extra}")\
                .set_attrs(date=date, is_today=is_today, is_tomorrow=is_tomorrow).status.add_listener("on_click", self.on_calendar_click).element
            if is_today or is_tomorrow:
                btn.status.invoke_callback("on_click")
                was_today_or_tomorrow = True
            if i == 0: last_calendar = btn
        if not was_today_or_tomorrow and last_calendar is not None:
            last_calendar.status.invoke_callback("on_click")
                        
    def build_agenda_day(self, date):
        with self.agenda_root:
            day = self.data.date_events[date]
            with guis.VStack(guis.ZeroR(), style_id="fill;invis_cont;anchortop")\
                    .set_render_offset(pygame.Vector2(-W,0)).animate_offset_x_to(0, 300, guis.AnimRepeatMode.norepeat) as main_cont:
                guis.Label(f"{day.datedisplay} {day.dayname}", guis.SizeR(0,10), style_id="fill_x;calendarfont;textgrow")
                guis.HLine(guis.SizeR(0, 2), style_id="fill_x;disabledoutlinecol")
                
                if len(day.grades) > 0:
                    guis.Label("Grades", guis.SizeR(0,10), style_id="fill_x;bigbigfont;textgrow")
                    
                    for grade in day.grades:
                        style_extra = "good" if grade.value >= 6 else "bad"
                        with guis.VStack(guis.ZeroR(), style_id="fill_x;grow_y;invis_cont;boxpadding"):
                            with guis.HStack(guis.ZeroR(), style_id=f"fill_x;grow_y;agendagrade{style_extra}"):
                                guis.Label(f"{grade.display}", guis.SizeR(GRADE_SIZE/1.3, GRADE_SIZE/1.3), style_id="bigbigfont")
                                with guis.VStack(guis.ZeroR(), style_id="fill;invis_cont"):
                                    profs_txt = f" | {grade.profsdisplay}" if not HIDE_PROFS else ""
                                    guis.Label(f"{grade.subject}{profs_txt}", guis.ZeroR(), style_id="bigfont;fill_x;textgrow;alignleft")
                                    guis.HLine(guis.SizeR(0, 1), style_id="fill_x;whiteline")
                                    guis.Label(f"{grade.mode} | {grade.period} | Current Avg: {grade.average}", guis.ZeroR(), style_id="fill_x;textgrow;alignleft")
                
                if day.absence is not None:
                    with guis.VStack(guis.ZeroR(), style_id="fill_x;grow_y;invis_cont;boxpadding"):
                        with guis.VStack(guis.ZeroR(), style_id=f"fill_x;grow_y;agendagradebad"):
                            guis.Label(f"Absence", guis.ZeroR(), style_id="fill_x;bigfont;textgrow")
                            details_txt = "Justified: "+day.absence.justifydesc if day.absence.justified else "Not justified"
                            guis.Label(details_txt, guis.ZeroR(), style_id="fill_x;textgrow;smallfont")
                
                if len(day.homeworks) > 0:
                    guis.Label("Homeworks", guis.SizeR(0, 10), style_id="fill_x;bigbigfont;textgrow")
                    
                    for homework in day.homeworks:
                        with guis.VStack(guis.ZeroR(), style_id="pixeldisabled;grow_y;fill_x"):
                            author_txt = f" | {homework.authordisplay}" if not HIDE_PROFS else ""
                            title = guis.Label(f"{homework.subjectdisplay}{author_txt}", guis.SizeR(0, 0), style_id="alignleft;fill_x;textgrow")
                            with guis.HStack(guis.ZeroR(), style_id="fill_x;grow_y;invis_cont"):
                                guis.Label(homework.description if homework.description else "No details", guis.ZeroR(), style_id="fill_x;disabledtxt;smallfont;alignleft;textgrow")
                                cb = guis.Checkbox(guis.SizeR(GRADE_SIZE//3.2, GRADE_SIZE//3.2), style_id="pixelbg;donecheckbox")\
                                    .set_attrs(hwid=homework.evtid, title=title)\
                                    .status.add_multi_listeners(on_select=self.on_done_select, on_deselect=self.on_done_deselect).element
                                cb.set_tooltip("", "Did you complete the homework?", 300, 40)
                                if homework.evtid in self.app.done_hws:
                                    cb.status.select()
                                    self.on_done_select(cb)
                
                if len(day.events) > 0:                    
                    guis.Label("Agenda", guis.SizeR(0, 10), style_id="fill_x;bigbigfont;textgrow")
                    
                    for event in day.events:
                        with guis.VStack(guis.ZeroR(), style_id="pixeldisabled;grow_y;fill_x"):
                            author_txt = f"{event.authordisplay}" if not HIDE_PROFS else "[Censored]"
                            guis.Label(f"{author_txt}", guis.SizeR(0, 0), style_id="alignleft;fill_x;textgrow")
                            guis.Label(event.description if event.description else "No details", guis.ZeroR(), style_id="fill_x;disabledtxt;smallfont;alignleft;textgrow")
                    
                if len(day.lessons) > 0:
                    guis.Label("Lessons", guis.SizeR(0, 10), style_id="fill_x;bigbigfont;textgrow")
                    
                    for lesson in day.lessons:
                        with guis.VStack(guis.ZeroR(), style_id="pixeldisabled;grow_y;fill_x"):
                            author_txt = f" | {lesson.authordisplay}" if not HIDE_PROFS else ""
                            guis.Label(f"{lesson.subjectdisplay}{author_txt}", guis.SizeR(0, 0), style_id="alignleft;fill_x;textgrow")
                            guis.Label(lesson.type, guis.ZeroR(), style_id="fill_x;disabledtxt;smallfont;alignleft;textgrow")
                            guis.Label(lesson.lesson if lesson.lesson else "No details", guis.ZeroR(), style_id="fill_x;disabledtxt;smallfont;alignleft;textgrow")
                
                
            self.selected_day_cont = main_cont
    