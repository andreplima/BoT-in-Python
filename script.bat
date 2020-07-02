echo CASE 1 - computing a distance matrix

@echo off
rem script for the video explaining why case 1 works and case 2 fails
rem first, let's show that the efficiency is "nearly constant" for doubling loads
rem (here, efficiency is the ratio between the load, measured as the number of tasks, and the duration from its processing)
rem +----+------------+----------+------+----------+
rem | #p | load spec  |  #tasks  | t(s) | eff(T/s) |
rem +----+------------+----------+------+----------+
rem |  1 |  500, 100  |   124750 |   8  |    15594 |
rem |  1 |  700, 100  |   244650 |  18  |    13592 |
rem |  1 | 1000, 100  |   499500 |  35  |    14271 |
rem +----+------------+----------+------+----------+
rem Things to watch out in the video:
rem 1) change in #tasks has no effect on efficiency
@echo on

cls
python case1.py 1  500 100
python case1.py 1  700 100
python case1.py 1 1000 100

@echo off
rem let's now show how the efficiency grows when more processes are engaged
rem (PS. the Movielens-1M dataset describes about 3500 items;
rem  supposing you decided to represent items as 100-dimensional vectors, then ...
rem  ... these two loads correspond to the computation of a distance matrix for the whole dataset)
rem +----+------------+----------+------+----------+
rem | #p | load spec  |  #tasks  | t(s) | eff(T/s) |
rem +----+------------+----------+------+----------+
rem |  1 | 3500, 100  |  6123250 | 424  |    14442 |
rem |  4 | 3500, 100  |  6123250 | 243  |    25199 |
rem +----+------------+----------+------+----------+
rem Things to watch out in the video:
rem 1) processing load owing to the processes
rem 2) sequence of spawning and completion
rem 3) memory consumption over time (slow growth)
rem 4) change in #p has large effect on efficiency (growth)
@echo on

python case1.py 1 3500 100
python case1.py 4 3500 100
pause


@echo off
rem CASE 2 - computing the average of a large sample
rem first, let's show that the efficiency is "nearly constant" for doubling loads
rem +----+------------+----------+------+----------+
rem | #p | load spec  |  #tasks  | t(s) | eff(T/s) |
rem +----+------------+----------+------+----------+
rem |  1 |        10  | 10000000 |   9  |  1111111 |
rem |  1 |        20  | 20000000 |  18  |  1111111 |
rem |  1 |        40  | 40000000 |  35  |  1142857 |
rem +----+------------+----------+------+----------+
rem Things to watch out in the video:
rem 1) processing load owing to the processes
rem 2) memory consumption over time (large growth)
@echo on

cls
python case2.py 1 10
python case2.py 1 20
python case2.py 1 40

@echo off
rem let's now show how the efficiency drops when more processes are engaged
rem +----+------------+----------+------+----------+
rem | #p | load spec  |  #tasks  | t(s) | eff(T/s) |
rem +----+------------+----------+------+----------+
rem |  4 |        10  | 10000000 |  81  |   123457 |
rem |  4 |        20  | 20000000 | 162  |   123457 |
rem |  4 |        40  | 40000000 | 385  |   103896 |
rem +----+------------+----------+------+----------+
rem 1) processing load owing to the processes
rem 2) sequence of spawning and completion
rem 3) memory consumption over time (large growth, and hard-faults in load spec 40)
rem 4) change in #p has large effect on efficiency (drop)
@echo on

python case2.py 4 10
python case2.py 4 20
python case2.py 4 40
pause

@echo off
rem So, if higher efficiency cannot be obtained by engaging more processes, ...
rem ... what can be done?
rem Well, in this case, a change in perspective helps:
rem Would you be able to trade efficiency for precision?
@echo on

cls
python case2.py 0 40    5
python case2.py 0 40   30
python case2.py 0 40  100
python case2.py 0 40 1000
