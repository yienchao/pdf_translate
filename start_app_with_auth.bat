@echo off
chcp 65001 >nul
echo ========================================
echo Starting PDF Translator with Supabase Auth
echo ========================================
echo.

REM IMPORTANT: Set these environment variables before running this script!
REM You can set them in your Windows environment variables, or create a local
REM file named 'set_env_vars.bat' with your actual credentials (already gitignored)
REM
REM Example content for set_env_vars.bat:
REM set ANTHROPIC_API_KEY=your-anthropic-api-key-here
REM set SUPABASE_URL=your-supabase-url-here
REM set SUPABASE_KEY=your-supabase-anon-key-here

IF EXIST set_env_vars.bat (
    echo Loading environment variables from set_env_vars.bat...
    call set_env_vars.bat
) ELSE (
    echo.
    echo WARNING: set_env_vars.bat not found!
    echo Please create it with your credentials or set environment variables manually.
    echo.
    pause
    exit /b 1
)

echo Environment variables loaded!
echo - ANTHROPIC_API_KEY: Set
echo - SUPABASE_URL: %SUPABASE_URL%
echo - SUPABASE_KEY: Set
echo.
echo Starting Streamlit with authentication...
echo.

streamlit run app.py --server.port 8504

pause
