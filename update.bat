@echo off
echo ====================================
echo Monad Main Tool Updater
echo ====================================
echo.

:: SECURITY NOTICE: This updater does NOT upload your private keys
:: All operations are performed locally on your PC.

:: Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Please install Git to use this updater.
    goto end
)

:: Check if .git directory exists
if not exist .git (
    echo This is not a git repository. Please clone the repository first.
    goto end
)

:: Backup important data files
echo Backing up your data files...
if not exist backup mkdir backup
if exist data\private_keys.txt copy /Y data\private_keys.txt backup\private_keys.txt
if exist data\proxies.txt copy /Y data\proxies.txt backup\proxies.txt
if exist data\twitter_tokens.txt copy /Y data\twitter_tokens.txt backup\twitter_tokens.txt
if exist data\keys_for_faucet.txt copy /Y data\keys_for_faucet.txt backup\keys_for_faucet.txt
if exist data\discord_tokens.txt copy /Y data\discord_tokens.txt backup\discord_tokens.txt
if exist data\email_tokens.txt copy /Y data\email_tokens.txt backup\email_tokens.txt

:: Backup config files
echo Backing up configuration files...
if exist config.yaml copy /Y config.yaml backup\config.yaml
if exist tasks.py copy /Y tasks.py backup\tasks.py

:: Fetch latest changes from GitHub
echo Fetching latest changes from GitHub...
git fetch origin main
if %ERRORLEVEL% NEQ 0 (
    echo Failed to fetch updates. Please check your internet connection.
    goto end
)

:: Force reset to match GitHub version (this will overwrite ALL files except those in .gitignore)
echo Applying GitHub updates (overwriting local changes)...
git reset --hard origin/main

:: Restore data files (these will not be affected by GitHub changes)
echo Restoring your data files...
if exist backup\private_keys.txt copy /Y backup\private_keys.txt data\private_keys.txt
if exist backup\proxies.txt copy /Y backup\proxies.txt data\proxies.txt
if exist backup\twitter_tokens.txt copy /Y backup\twitter_tokens.txt data\twitter_tokens.txt
if exist backup\keys_for_faucet.txt copy /Y backup\keys_for_faucet.txt data\keys_for_faucet.txt
if exist backup\discord_tokens.txt copy /Y backup\discord_tokens.txt data\discord_tokens.txt
if exist backup\email_tokens.txt copy /Y backup\email_tokens.txt data\email_tokens.txt

echo.
echo Update completed successfully!
echo.
echo - Your data files have been preserved
echo - Configuration has been updated to match GitHub version
echo - Any conflicts were resolved by using GitHub's version

:end
echo.
echo Press any key to exit...
pause >nul
