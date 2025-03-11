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

:: Configure Git to use our merge strategy
git config merge.ours.driver true

:: Backup important data files and configuration
echo Backing up your data files and configuration...
if not exist backup mkdir backup
if exist data\private_keys.txt copy /Y data\private_keys.txt backup\private_keys.txt
if exist data\proxies.txt copy /Y data\proxies.txt backup\proxies.txt
if exist data\twitter_tokens.txt copy /Y data\twitter_tokens.txt backup\twitter_tokens.txt
if exist data\keys_for_faucet.txt copy /Y data\keys_for_faucet.txt backup\keys_for_faucet.txt
if exist data\discord_tokens.txt copy /Y data\discord_tokens.txt backup\discord_tokens.txt

:: Backup config files
if exist config.yaml copy /Y config.yaml backup\config.yaml
if exist tasks.py copy /Y tasks.py backup\tasks.py

:: Try to pull the latest code
echo Pulling latest code from GitHub...
git pull --ff-only origin main
if %ERRORLEVEL% NEQ 0 (
    :: If fast-forward fails, do a proper merge
    echo Fast-forward update failed, performing merge favoring GitHub changes...
    
    :: Abort any existing merge first
    git merge --abort 2>nul
    
    :: Try to merge, accepting theirs in case of conflict
    git pull -X theirs origin main
    
    :: If there are still conflicts, resolve them by taking GitHub's version
    git diff --name-only --diff-filter=U | findstr /C:"data/" >nul
    if %ERRORLEVEL% EQU 0 (
        :: Only data files have conflicts, resolve manually
        for /f "tokens=*" %%f in ('git diff --name-only --diff-filter=U') do (
            git checkout --theirs -- "%%f"
            git add "%%f"
        )
        git commit -m "Auto-merged update with GitHub changes"
    )
)

:: Restore data files and configuration
echo Restoring your data files and configuration...
if exist backup\private_keys.txt copy /Y backup\private_keys.txt data\private_keys.txt
if exist backup\proxies.txt copy /Y backup\proxies.txt data\proxies.txt
if exist backup\twitter_tokens.txt copy /Y backup\twitter_tokens.txt data\twitter_tokens.txt
if exist backup\keys_for_faucet.txt copy /Y backup\keys_for_faucet.txt data\keys_for_faucet.txt
if exist backup\discord_tokens.txt copy /Y backup\discord_tokens.txt data\discord_tokens.txt

:: Restore config files
if exist backup\config.yaml copy /Y backup\config.yaml config.yaml
if exist backup\tasks.py copy /Y backup\tasks.py tasks.py

echo.
echo Update completed successfully!
echo Your data files and configuration have been preserved.

:end
echo.
echo Press any key to exit...
pause >nul 