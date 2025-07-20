@echo off
setlocal enabledelayedexpansion

set "EULA_FILE=eula.txt"
if not exist "%EULA_FILE%" (
    call :create_eula
)
:create_eula
(
    echo eula=true
) > "%EULA_FILE%"
echo EULA�Ѿ�Ĭ��ͬ�⣬�������ͬ��Mojang Studios��EULA����رմ˳���

title Minecraft Server Manager - By PowerCMD

:: �����ļ�·��
set "CONFIG_FILE=Config.txt"

:: ��ʼ��Ĭ��ֵ
set "DEFAULT_MEMORY=2G"
set "DEFAULT_CORE=server.jar"
set "DEFAULT_ONLINE_MODE=true"
set "DEFAULT_MOTD=A Minecraft Server"
set "DEFAULT_PORT=25565"
set "DEFAULT_MAX_PLAYERS=20"
set "DEFAULT_VIEW_DISTANCE=10"
set "DEFAULT_SEED=15"

:: ��������ļ��Ƿ����
if not exist "%CONFIG_FILE%" (
    call :create_config
)

:: ���˵�
:main_menu
cls
echo ==============================
echo    Minecraft Server Manager
echo ==============================
echo 1. ����������
echo 2. ���÷�����
echo 3. �༭�����ļ�
echo 4. �˳�
choice /c 1234 /n /m "��ѡ�����: "
goto option_%errorlevel%

:option_1
call :read_config
call :create_properties
call :start_server
goto main_menu

:option_2
call :configure_server
goto main_menu

:option_3
notepad "%CONFIG_FILE%"
goto main_menu

:option_4
exit

:: ���������ļ�
:create_config
(
    echo MEMORY=%DEFAULT_MEMORY%
    echo CORE=%DEFAULT_CORE%
    echo ONLINE_MODE=%DEFAULT_ONLINE_MODE%
    echo MOTD=%DEFAULT_MOTD%
    echo PORT=%DEFAULT_PORT%
    echo MAX_PLAYERS=%DEFAULT_MAX_PLAYERS%
    echo VIEW_DISTANCE=%DEFAULT_VIEW_DISTANCE%
    echo LEVEL_SEED=%DEFAULT_SEED%
    echo JVM_ARGS=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions
    echo SERVER_ARGS=nogui
) > "%CONFIG_FILE%"
echo �Ѵ��������ļ�: %CONFIG_FILE%
timeout /t 2 >nul
goto :eof

:: ��ȡ�����ļ�
:read_config
set "MEMORY="
set "CORE="
set "ONLINE_MODE="
set "MOTD="
set "PORT="
set "MAX_PLAYERS="
set "VIEW_DISTANCE="
set "LEVEL_SEED="
set "JVM_ARGS="
set "SERVER_ARGS="

for /f "tokens=1,* delims==" %%a in ('type "%CONFIG_FILE%"') do (
    if "%%a"=="MEMORY" set "MEMORY=%%b"
    if "%%a"=="CORE" set "CORE=%%b"
    if "%%a"=="ONLINE_MODE" set "ONLINE_MODE=%%b"
    if "%%a"=="MOTD" set "MOTD=%%b"
    if "%%a"=="PORT" set "PORT=%%b"
    if "%%a"=="MAX_PLAYERS" set "MAX_PLAYERS=%%b"
    if "%%a"=="VIEW_DISTANCE" set "VIEW_DISTANCE=%%b"
    if "%%a"=="LEVEL_SEED" set "LEVEL_SEED=%%b"
    if "%%a"=="JVM_ARGS" set "JVM_ARGS=%%b"
    if "%%a"=="SERVER_ARGS" set "SERVER_ARGS=%%b"
)

:: ����Ĭ��ֵ���������Ϊ�գ�
if "!MEMORY!"=="" set "MEMORY=%DEFAULT_MEMORY%"
if "!CORE!"=="" set "CORE=%DEFAULT_CORE%"
if "!ONLINE_MODE!"=="" set "ONLINE_MODE=%DEFAULT_ONLINE_MODE%"
if "!MOTD!"=="" set "MOTD=%DEFAULT_MOTD%"
if "!PORT!"=="" set "PORT=%DEFAULT_PORT%"
if "!MAX_PLAYERS!"=="" set "MAX_PLAYERS=%DEFAULT_MAX_PLAYERS%"
if "!VIEW_DISTANCE!"=="" set "VIEW_DISTANCE=%DEFAULT_VIEW_DISTANCE%"
if "!LEVEL_SEED!"=="" set "LEVEL_SEED=%DEFAULT_SEED%"
goto :eof

:: ���÷�����
:configure_server
call :read_config

:config_menu
cls
echo ==============================
echo       ����������
echo ==============================
echo ��ǰ����:
echo 1. �ڴ����: !MEMORY!
echo 2. ����������: !CORE!
echo 3. ������֤: !ONLINE_MODE!
echo 4. MOTD����: !MOTD!
echo 5. �������˿�: !PORT!
echo 6. ��������: !MAX_PLAYERS!
echo 7. �Ӿ�: !VIEW_DISTANCE!
echo 8. ��������: !LEVEL_SEED!
echo 9. JVM����: !JVM_ARGS!
echo 10. ����������: !SERVER_ARGS!
echo 0. �������˵�
echo.
choice /c 1234567890 /n /m "ѡ��Ҫ�޸ĵ�ѡ��: "

set "option=!errorlevel!"
if !option! equ 10 goto main_menu

if !option! equ 1 (
    set /p "new_value=�������ڴ���� (���� 2G, 4G): "
    if "!new_value!" neq "" set "MEMORY=!new_value!"
)
if !option! equ 2 (
    echo ���õķ���������:
    dir /b *.jar
    set /p "new_value=��������ļ���: "
    if "!new_value!" neq "" set "CORE=!new_value!"
)
if !option! equ 3 (
    set /p "new_value=����������֤? (true/false): "
    if "!new_value!" neq "" set "ONLINE_MODE=!new_value!"
)
if !option! equ 4 (
    set /p "new_value=������MOTD����: "
    if "!new_value!" neq "" set "MOTD=!new_value!"
)
if !option! equ 5 (
    set /p "new_value=�����¶˿ں�: "
    if "!new_value!" neq "" set "PORT=!new_value!"
)
if !option! equ 6 (
    set /p "new_value=������������: "
    if "!new_value!" neq "" set "MAX_PLAYERS=!new_value!"
)
if !option! equ 7 (
    set /p "new_value=�����Ӿ� (4-32): "
    if "!new_value!" neq "" set "VIEW_DISTANCE=!new_value!"
)
if !option! equ 8 (
    set /p "new_value=������������: "
    if "!new_value!" neq "" set "LEVEL_SEED=!new_value!"
)
if !option! equ 9 (
    set /p "new_value=����JVM����: "
    if "!new_value!" neq "" set "JVM_ARGS=!new_value!"
)
if !option! equ 10 (
    set /p "new_value=�������������: "
    if "!new_value!" neq "" set "SERVER_ARGS=!new_value!"
)

:: ��������
(
    echo MEMORY=!MEMORY!
    echo CORE=!CORE!
    echo ONLINE_MODE=!ONLINE_MODE!
    echo MOTD=!MOTD!
    echo PORT=!PORT!
    echo MAX_PLAYERS=!MAX_PLAYERS!
    echo VIEW_DISTANCE=!VIEW_DISTANCE!
    echo LEVEL_SEED=!LEVEL_SEED!
    echo JVM_ARGS=!JVM_ARGS!
    echo SERVER_ARGS=!SERVER_ARGS!
) > "%CONFIG_FILE%"

goto config_menu

:: ����������
:start_server
call :read_config

echo ��������������...
echo ʹ���ڴ�: !MEMORY!
echo ����������: !CORE!
java -Xms!MEMORY! -Xmx!MEMORY! !JVM_ARGS! -jar !CORE! !SERVER_ARGS!

if errorlevel 1 (
    echo.
    echo ����������ʧ�ܣ�����:
    echo 1. �ڴ������Ƿ����
    echo 2. �����ļ��Ƿ����
    echo 3. Java�Ƿ�װ��ȷ
    echo.
    pause
)
goto :eof

:create_properties
call :read_config

set "PROP_FILE=server.properties"

if exist "%PROP_FILE%" (
    echo online-mode=!ONLINE_MODE!
    echo motd=!MOTD!
    echo server-port=!PORT!
    echo max-players=!MAX_PLAYERS!
    echo view-distance=!VIEW_DISTANCE!
    echo level-seed=!LEVEL_SEED!
) >> "%PROP_FILE%"

if not exist "%PROP_FILE%" (
    echo online-mode=!ONLINE_MODE!
    echo motd=!MOTD!
    echo server-port=!PORT!
    echo max-players=!MAX_PLAYERS!
    echo view-distance=!VIEW_DISTANCE!
    echo level-seed=!LEVEL_SEED!
) > "%PROP_FILE%"
goto :eof