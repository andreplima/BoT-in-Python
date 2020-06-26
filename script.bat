rem script for the video explaining why case 1 works and case 2 fails
cls

python case1.py 1  500 100
python case1.py 1  700 100
python case1.py 1 1000 100

pause

python case1.py 1 3500 100
python case1.py 4 3500 100

pause
cls

python case2.py 1 10
python case2.py 1 20
python case2.py 1 40

pause

python case2.py 4 10
@echo off
pause
@echo on
rem 10x more time

python case2.py 4 20
python case2.py 4 40

pause
cls

python case2.py 0 40    5
python case2.py 0 40   30
python case2.py 0 40  100
python case2.py 0 40 1000
