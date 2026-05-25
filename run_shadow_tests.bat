@echo off
cd /d T:\Project-AI-main
C:\Users\Quencher\AppData\Local\Programs\Python\Python312\python.exe -m pytest src\utf\tests\test_shadow_thirst.py -v --tb=short --override-ini="testpaths=src/utf/tests" > shadow_test_output.txt 2>&1
