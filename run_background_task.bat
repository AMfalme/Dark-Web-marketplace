@echo off
cls
:begin
python3 manage.py process_tasks
cls

Goto begin