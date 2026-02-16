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
call make-docker.bat clean
call make-docker.bat build
goto end

:logs
%DOCKER_PATH% logs -f corretor-redacao-container
goto end

:help
echo Comandos disponíveis:
echo   make-docker build         - Constrói a imagem Docker
echo   make-docker run           - Inicia o container
echo   make-docker run-with-key  - Inicia com API Key
echo   make-docker stop          - Para o container
echo   make-docker clean         - Remove imagem e container
echo   make-docker rebuild       - Reconstrói a imagem
echo   make-docker logs          - Mostra logs

:end
