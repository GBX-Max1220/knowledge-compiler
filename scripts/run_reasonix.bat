@echo off
REM ============================================================
REM Knowledge Compiler — Reasonix Batch Runner for v0.1
REM Processes Chapters 1-3 (60 sections)
REM ============================================================
REM
REM Prerequisites:
REM   1. Reasonix CLI installed and in PATH
REM   2. prompts/02_extract.md and prompts/03_object_generate.md frozen
REM
REM Usage:
REM   scripts\run_reasonix.bat extract    -- Stage 1: chunk → extraction
REM   scripts\run_reasonix.bat generate   -- Stage 2: extraction → normalized
REM   scripts\run_reasonix.bat finish     -- Stage 3: decompose + validate
REM ============================================================

set PROMPT_EXTRACT=..\..\prompts\02_extract.md
set PROMPT_GENERATE=..\..\prompts\03_object_generate.md
set CHUNK_DIR=..\..\books\acsm12\chunks
set EXTRACT_DIR=..\..\books\acsm12\extraction
set NORM_DIR=..\..\books\acsm12\normalized

IF "%1"=="extract" GOTO EXTRACT
IF "%1"=="generate" GOTO GENERATE
IF "%1"=="finish" GOTO FINISH

echo Usage: scripts\run_reasonix.bat extract^|generate^|finish
GOTO END

:EXTRACT
echo === Stage 1: Extraction (chunk → extraction) ===
echo.
for %%f in (%CHUNK_DIR%\01_*.md %CHUNK_DIR%\02_*.md %CHUNK_DIR%\03_*.md) do (
    echo Processing %%~nxf ...
    type "%%f" | reasonix --prompt %PROMPT_EXTRACT% > "%EXTRACT_DIR%\%%~nf.yaml"
    echo   ^-> %EXTRACT_DIR%\%%~nf.yaml
)
echo.
echo Extraction complete. Check %EXTRACT_DIR%\ for output files.
GOTO END

:GENERATE
echo === Stage 2: Generation (extraction → normalized YAML) ===
echo.
for %%f in (%EXTRACT_DIR%\01_*.yaml %EXTRACT_DIR%\02_*.yaml %EXTRACT_DIR%\03_*.yaml) do (
    echo Processing %%~nxf ...
    type "%%f" | reasonix --prompt %PROMPT_GENERATE% > "%NORM_DIR%\%%~nf.yaml"
    echo   ^-> %NORM_DIR%\%%~nf.yaml
)
echo.
echo Generation complete. Check %NORM_DIR%\ for output files.
GOTO END

:FINISH
echo === Stage 3: Decompose + Validate ===
echo.
cd ..\..
echo Decomposing objects ...
python scripts\decompose_objects.py books\acsm12\normalized\
echo.
echo Validating ...
python scripts\knowledge-compiler validate acsm12
cd scripts
echo.
echo === Chapter 1-3 complete! ===
echo Tag release: python scripts\knowledge-compiler release acsm12 v0.1 --chapters 1 2 3
GOTO END

:END
