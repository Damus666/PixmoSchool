W, H = SIZES = 1920,1080 # 1200, 900
MULT = ((W+H)/2)/((1920+1080)/2)
FPS = 120

HIDE_PROFS = False
REPLACE_912 = False

BUTTON_BAR_H = H//11
GRADES_ROOT_W = W//2.6
GRADES_BUTTONS = ["All Grades", "Subject Grades", "Lessons"]
GRADE_SIZE = W//12
SEPARATOR_W = W//14
ENTRY_HEIGHT = 60
ANIM_TIME = 150

LOADING_MSG = "Downloading data and loading UI..."
APP_NAME = "Pixmo School"

COLORS = {
    "activebg":"#3B3F49",
    "activeoutline":"#7B7F88",
    "default":"#3B3F49",
    "defaultoutline":"#65666A",
    "shadow":"#2C2F38",
    "disabledbg":"#1D1F29",
    "disabledoutline":"#363946",
    "disabledshadow":"#1F2128"
}

SUBJ_NAME_TABLE = {
    "disegno e storia dell'arte": "Art",
    "filosofia": "Filosophy",
    "fisica": "Physics",
    "lingua e cultura straniera inglese": "English",
    "lingua e letteratura italiana": "Italian",
    "lingua e cultura latina": "Latin",
    "matematica": "Math",
    "materia alternativa": "Extra",
    "scienze motorie e sportive": "PE",
    "scienze naturali": "Science",
    "storia": "History",
    "supplenza": "Replacement",
    "progetti / potenziamento": "Projects",
    "educazione civica": "Civic Education"
}

GRADE_COLOR_TABLE = {
    "green": "good",
    "red": "bad",
    "blue": "neutral"
}

GRADE_MODE_TABLE = {
    "Orale": "Spoken",
    "Scritto/Grafico":"Written",
    "Pratico": "Practical"
}

HOMEWORK_CODE = "AGHW"
EVENT_CODE = "AGNT"
LESSON_CODE = "LSF0"
ABSENCE_CODE = "ABA0"
