import classeviva
from classeviva.variabili import data_inizio_anno, data_fine_anno
from classeviva.eccezioni import PasswordNonValida
import json
import asyncio
import requests
import enum

class ErrorType(enum.StrEnum):
    ok = "ok"
    credentials = "credentials"
    connection = "connection"
    timeout = "timeout"
    toomanyredirects = "toomanyredirects"
    http = "http"
    
def error_message(type_):
    return {
        "credentials":"Invalid user id or password. Try again with different credentials",
        "connection":"ERROR: Network error (refused connection, DNS failure, no internet...)",
        "timeout":"ERROR: Connection to the server timed out. Try again",
        "toomanyredirects":"ERROR: Too many redirects happened while connecting to the server",
        "http":"ERROR: Invalid HTTP response",
        "ok": None,
    }[type_]

class ClassevivaUser:
    def __init__(self, main):
        self.main = main
        self.login_success = False
        
    def login(self, userid, password):
        result = self.try_func(self.inner_login, userid, password)
        if result == ErrorType.ok:
            self.login_success = True
        return result
        
    def download_data(self):
        return self.try_func(self.inner_download_data)
        
    def try_func(self, func, *args):
        try:
            func(*args)
        except PasswordNonValida:
            return ErrorType.credentials
        except requests.ConnectionError:
            return ErrorType.connection
        except requests.Timeout:
            return ErrorType.timeout
        except requests.TooManyRedirects:
            return ErrorType.toomanyredirects
        except requests.HTTPError:
            return ErrorType.http
        return ErrorType.ok
    
    def inner_download_data(self):
        self.raw_grades = asyncio.run(self.userobj.voti())
        self.raw_subjects = asyncio.run(self.userobj.materie())
        self.raw_agenda = asyncio.run(self.userobj.agenda())
        self.raw_lessons = asyncio.run(self.userobj.lezioni_da_a(data_inizio_anno(), data_fine_anno()))
        self.raw_absences = asyncio.run(self.userobj.assenze())
        
    def inner_login(self, userid, password):
        self.userid, self.password = userid, password
        self.userobj = classeviva.Utente(self.userid, self.password)
        self.userobj()
        