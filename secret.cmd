@echo off
SetLocal EnableDelayedExpansion
set TF_VAR_secretkey=
for /F "delims=" %%i in (%USERPROFILE%\Downloads\SecretKey.txt) do set TF_VAR_secretkey=!TF_VAR_secretkey!%%i
echo %TF_VAR_secretkey%
EndLocal