@echo off
cd /d "D:\Projects_New Energy\Personal_AI_Research_Agents\06_web_literature_agent"
if not exist .venv\Scripts\python.exe python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
pause

