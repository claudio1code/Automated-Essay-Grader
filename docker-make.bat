@echo off
set DOCKER_PATH="C:\Program Files\Docker\Docker\resources\bin\docker.exe"
set PATH=%PATH%;C:\Program Files\Docker\Docker\resources\bin

if "%1"=="" goto help
if "%1"=="build" goto build
if "%1"=="run" goto run
if "%1"=="run-with-key" goto run-with-key
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="rebuild" goto rebuild
if "%1"=="logs" goto logs
if "%1"=="dev" goto dev
goto help

:build
echo 🐳 Construindo imagem Docker...
%DOCKER_PATH% build -t corretor-redacao .
goto end

:run
echo 🚀 Iniciando container...
%DOCKER_PATH% run -d --name corretor-redacao-container -p 8501:8501 corretor-redacao
goto end

:run-with-key
set /p API_KEY=Digite sua GEMINI_API_KEY: 
echo 🚀 Iniciando container com API Key...
%DOCKER_PATH% run -d --name corretor-redacao-container -p 8501:8501 -e GEMINI_API_KEY=%API_KEY% corretor-redacao
echo ✅ Container iniciado!
echo 📱 Acesse: http://localhost:8501
goto end

:stop
echo 🛑 Parando container...
%DOCKER_PATH% stop corretor-redacao-container
%DOCKER_PATH% rm corretor-redacao-container
goto end

:clean
echo 🧹 Limpando...
%DOCKER_PATH% stop corretor-redacao-container 2>nul
%DOCKER_PATH% rm corretor-redacao-container 2>nul
%DOCKER_PATH% rmi corretor-redacao 2>nul
goto end

:rebuild
call docker-make.bat clean
call docker-make.bat build
goto end

:logs
%DOCKER_PATH% logs -f corretor-redacao-container
goto end

:dev
call docker-make.bat build
call docker-make.bat run-with-key
goto end

:help
echo Comandos disponíveis:
echo   docker-make build         - Constrói a imagem Docker
echo   docker-make run           - Inicia o container (sem API Key)
echo   docker-make run-with-key  - Inicia com API Key
echo   docker-make stop          - Para o container
echo   docker-make clean         - Remove imagem e container
echo   docker-make rebuild       - Reconstrói a imagem
echo   docker-make logs          - Mostra logs
echo   docker-make dev           - Constrói e roda com API Key

:end
