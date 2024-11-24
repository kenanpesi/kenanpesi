import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "flask", "flask_sqlalchemy", "flask_login", "werkzeug", "win32serviceutil", 
                "win32service", "win32event", "servicemanager", "socket"],
    "excludes": [],
    "include_files": ["templates/"],
}

base = None
if sys.platform == "win32":
    base = "Win32Service"

setup(
    name="RemoteAccessService",
    version="1.0",
    description="Uzaktan Erişim Servisi",
    options={"build_exe": build_exe_options},
    executables=[Executable("service_handler.py", base=base)]
)
