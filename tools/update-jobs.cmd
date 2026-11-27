@echo off
rem Double-click to run "update jobs" (PRD 2.5). Bypasses the PowerShell execution policy for this one script only; no system setting is changed.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update-jobs.ps1"
