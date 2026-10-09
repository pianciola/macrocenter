@echo off
cd /d "%~dp0"
rem Corre en esta computadora: solo accesible desde ella, guarda tus preferencias en archivos locales
rem y abre la página en el navegador.
set MACROCENTER_LOCAL=1
.venv\Scripts\python.exe -m streamlit run app.py --server.headless false --server.address 127.0.0.1
