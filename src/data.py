import typing
import dataclasses
import datetime
if typing.TYPE_CHECKING:
    from .app import Application
    
from .constants import *

@dataclasses.dataclass(slots=True)
class Grade:
    subjectid: str
    subject: str
    profs: str
    profsdisplay: str
    value: float
    display: str
    period: str
    mode: str
    counts: bool
    color: str
    colortype: str
    average: float
    date: str
    rawdate: str
    
@dataclasses.dataclass(slots=True)
class Homework:
    author: str
    authordisplay: str
    subject: str
    subjectdisplay: str
    description: str
    evtid: str
    
@dataclasses.dataclass(slots=True)
class Event:
    author: str
    authordisplay: str
    description: str
    
@dataclasses.dataclass(slots=True)
class Lesson:
    author: str
    authordisplay: str
    subject: str
    subjectdisplay: str
    type: str
    lesson: str
    datedisplay: str
    
@dataclasses.dataclass(slots=True)
class Absence:
    justified: bool
    justifydesc: str
    
@dataclasses.dataclass(slots=True)
class AgendaDay:
    date: str
    datedisplay: str
    dayname: str
    homeworks: list[Homework]
    events: list[Event]
    lessons: list[Lesson]
    grades: list[Grade]
    absence: Absence

class Data:
    def __init__(self, app: "Application"):
        self.app = app
        self.user = self.app.main.user
        self.parse()
        
    def calc_average(self, grades: list[Grade], round_to=4):
        grades = [grade.value for grade in grades if grade.counts]
        if len(grades) <= 0: return float("nan")
        return round(sum(grades)/len(grades), round_to)
    
    def sort_by_date(self, element):
        date = element["evtDate"]
        year, month, day = date.split("-")
        year, month, day = int(year), int(month), int(day)
        return (year/2023)*10000+(month/12)*1000+(day/31)*10
    
    def sort_keys_by_date(self, date):
        year, month, day = date.split("-")
        year, month, day = int(year), int(month), int(day)
        return (year/2023)*10000+(month/12)*1000+(day/31)*10
    
    def format_date(self, date):
        return "/".join(list(reversed(date.split("-")))).replace("2023", "23").replace("2024", "24")
        
    def parse(self):
        self.subject_profs: dict[str, list[str]] = {}
        self.profs_subject: dict[str, str] = {}
        for subj_data in self.user.raw_subjects:
            name = subj_data["description"]
            profs = [prof_data["teacherName"].title().split(" ")[0] for prof_data in subj_data["teachers"]]
                
            self.subject_profs[name] = profs
            for prof in profs:
                self.profs_subject[prof] = name
            
        self.grades: dict[str, list[Grade]|float] = {"grades": [], "average": -1}
        self.subject_grades: dict[str, dict[str, Grade|float]] = {}
        
        for grade_data in sorted(self.user.raw_grades, key=self.sort_by_date):
            grade = Grade(
                grade_data["subjectDesc"],
                SUBJ_NAME_TABLE.get(grade_data["subjectDesc"].lower(), "Unknown"),
                self.subject_profs[grade_data["subjectDesc"]],
                ", ".join(self.subject_profs[grade_data["subjectDesc"]]),
                grade_data["decimalValue"],
                grade_data["displayValue"].replace("½", " 1/2") if REPLACE_912 else grade_data["displayValue"],
                grade_data["periodDesc"],
                GRADE_MODE_TABLE[grade_data["componentDesc"]] if grade_data["componentDesc"] else "Grade",
                grade_data["displayValue"] not in ["+", "-"],
                grade_data["color"],
                GRADE_COLOR_TABLE[grade_data["color"]],
                -1,
                self.format_date(grade_data["evtDate"]),
                grade_data["evtDate"]
            )
            self.grades["grades"].append(grade)
            grade.average = self.calc_average(self.grades["grades"])
            if not grade.subjectid in self.subject_grades:
                self.subject_grades[grade.subjectid] = {"grades":[], "average":-1}
            self.subject_grades[grade.subjectid]["grades"].append(grade)
            
        self.grades["average"] = self.calc_average(self.grades["grades"])
        for name, subject in self.subject_grades.items():
            subject["average"] = self.calc_average(subject["grades"])
        
        event_dates = []
        for event in self.user.raw_agenda:
            event_date = event["evtDatetimeBegin"].split("T")[0]
            if not event_date in event_dates:
                event_dates.append(event_date)
        for lesson in self.user.raw_lessons:
            if not lesson["evtDate"] in event_dates:
                event_dates.append(lesson["evtDate"])
        for absence in self.user.raw_absences:
            if not lesson["evtDate"] in event_dates:
                event_dates.append(lesson["evtDate"])
        
        events_for_date = {}
        for date in event_dates:
            events = []
            for event in self.user.raw_agenda:
                if event["evtDatetimeBegin"].split("T")[0] == date:
                    events.append(event)
            for lesson in self.user.raw_lessons:
                if lesson["evtDate"] == date:
                    events.append(lesson)
            for absence in self.user.raw_absences:
                if absence["evtDate"] == date:
                    events.append(absence)
            events_for_date[date] = events
            
        date_keys = list(sorted(event_dates, key=self.sort_keys_by_date, reverse=True))
        sorted_events_date = {}
        for key in date_keys:
            sorted_events_date[key] = events_for_date[key]
            
        self.date_events:dict[str, AgendaDay] = {}
        self.subject_lessons: dict[str, list[Lesson]] = {}
        for date, events in sorted_events_date.items():
            homeworks = []
            agenda = []
            lessons = []
            grades = []
            absence = None
            for event in events:
                if event["evtCode"] == HOMEWORK_CODE:
                    homeworks.append(Homework(
                        event["authorName"],
                        event["authorName"].title().split(" ")[0],
                        event["subjectDesc"],
                        SUBJ_NAME_TABLE.get(event["subjectDesc"].lower(), "Unknown") if event["subjectDesc"] else None,
                        event["notes"],
                        str(event["evtId"])
                    ))
                elif event["evtCode"] == EVENT_CODE:
                    agenda.append(Event(
                        event["authorName"],
                        event["authorName"].title().split(" ")[0],
                        event["notes"]
                    ))
                elif event["evtCode"] == LESSON_CODE:
                    lessons.append((lesson:=Lesson(
                        event["authorName"],
                        event["authorName"].title().split(" ")[0],
                        event["subjectDesc"],
                        SUBJ_NAME_TABLE.get(event["subjectDesc"].lower(), "Unknown"),
                        event["lessonType"],
                        event["lessonArg"],
                        self.format_date(date)
                    )))
                    if lesson.subject not in self.subject_lessons:
                        self.subject_lessons[lesson.subject] = []
                    self.subject_lessons[lesson.subject].append(lesson)
                elif event["evtCode"] == ABSENCE_CODE:
                    absence = Absence(
                        event["isJustified"],
                        event["justifReasonDesc"] if event["justifReasonDesc"] else "No justification description"
                    )
            for grade in self.grades["grades"]:
                if grade.rawdate == date:
                    grades.append(grade)
            formatted_date = self.format_date(date)
            day, month, year = [int(n) for n in formatted_date.split("/")]
            self.date_events[date] = AgendaDay(date, formatted_date, datetime.datetime(year, month, day).strftime("%A"), homeworks, agenda, lessons, grades, absence)
