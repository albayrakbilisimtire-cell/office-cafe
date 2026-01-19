pip install -r requirements.txt

pyinstaller ^
 --onefile ^
 --noconsole ^
 --add-data "templates;templates" ^
 --add-data "static;static" ^
 --add-data "exports;exports" ^
 app.py
