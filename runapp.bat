@echo off
for /f "tokens=*" %%G in (env_standalone.txt) do (
  SET %%G
)
call .\venv\Scripts\activate
python run.py
deactivate
