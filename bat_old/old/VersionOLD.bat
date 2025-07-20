@echo off
setlocal enabledelayedexpansion

title Minecraft Server Manager

:: 配置文件路径
set "CONFIG_FILE=ServerConfig.txt"

:: 初始化默认值
set "DEFAULT_MEMORY=2G"
set "DEFAULT_CORE=server.jar"
set "DEFAULT_ONLINE_MODE=true"
set "DEFAULT_MOTD=A Minecraft Server"
set "DEFAULT_PORT=25565"
set "DEFAULT_MAX_PLAYERS=20"
set "DEFAULT_VIEW_DISTANCE=10"

:: 检查配置文件是否存在
if not exist "%CONFIG_FILE%" (
    call :create_config
)

:: 主菜单
:main_menu
cls
echo ==============================
echo    Minecraft Server Manager
echo ==============================
echo 1. 启动服务器
echo 2. 配置服务器
echo 3. 编辑配置文件
echo 4. 退出
choice /c 1234 /n /m "请选择操作: "
goto option_%errorlevel%

:option_1
call :start_server
goto main_menu

:option_2
call :configure_server
goto main_menu

:option_3
notepad "%CONFIG_FILE%"
goto main_menu

:option_4
exit /b

:: 创建配置文件
:create_config
(
    echo MEMORY=%DEFAULT_MEMORY%
    echo CORE=%DEFAULT_CORE%
    echo ONLINE_MODE=%DEFAULT_ONLINE_MODE%
    echo MOTD=%DEFAULT_MOTD%
    echo PORT=%DEFAULT_PORT%
    echo MAX_PLAYERS=%DEFAULT_MAX_PLAYERS%
    echo VIEW_DISTANCE=%DEFAULT_VIEW_DISTANCE%
    echo JVM_ARGS=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions
    echo SERVER_ARGS=nogui
) > "%CONFIG_FILE%"
echo 已创建配置文件: %CONFIG_FILE%
timeout /t 2 >nul
goto :eof

:: 读取配置文件
:read_config
set "MEMORY="
set "CORE="
set "ONLINE_MODE="
set "MOTD="
set "PORT="
set "MAX_PLAYERS="
set "VIEW_DISTANCE="
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
    if "%%a"=="JVM_ARGS" set "JVM_ARGS=%%b"
    if "%%a"=="SERVER_ARGS" set "SERVER_ARGS=%%b"
)

:: 设置默认值（如果配置为空）
if "!MEMORY!"=="" set "MEMORY=%DEFAULT_MEMORY%"
if "!CORE!"=="" set "CORE=%DEFAULT_CORE%"
if "!ONLINE_MODE!"=="" set "ONLINE_MODE=%DEFAULT_ONLINE_MODE%"
if "!MOTD!"=="" set "MOTD=%DEFAULT_MOTD%"
if "!PORT!"=="" set "PORT=%DEFAULT_PORT%"
if "!MAX_PLAYERS!"=="" set "MAX_PLAYERS=%DEFAULT_MAX_PLAYERS%"
if "!VIEW_DISTANCE!"=="" set "VIEW_DISTANCE=%DEFAULT_VIEW_DISTANCE%"
goto :eof

:: 配置服务器
:configure_server
call :read_config

:config_menu
cls
echo ==============================
echo       服务器配置
echo ==============================
echo 当前配置:
echo 1. 内存分配: !MEMORY!
echo 2. 服务器核心: !CORE!
echo 3. 正版验证: !ONLINE_MODE!
echo 4. MOTD描述: !MOTD!
echo 5. 服务器端口: !PORT!
echo 6. 最大玩家数: !MAX_PLAYERS!
echo 7. 视距: !VIEW_DISTANCE!
echo 8. JVM参数: !JVM_ARGS!
echo 9. 服务器参数: !SERVER_ARGS!
echo 0. 返回主菜单
echo.
choice /c 1234567890 /n /m "选择要修改的选项: "

set "option=!errorlevel!"
if !option! equ 10 goto main_menu

if !option! equ 1 (
    set /p "new_value=输入新内存分配 (例如 2G, 4G): "
    if "!new_value!" neq "" set "MEMORY=!new_value!"
)
if !option! equ 2 (
    echo 可用的服务器核心:
    dir /b *.jar
    set /p "new_value=输入核心文件名: "
    if "!new_value!" neq "" set "CORE=!new_value!"
)
if !option! equ 3 (
    set /p "new_value=启用正版验证? (true/false): "
    if "!new_value!" neq "" set "ONLINE_MODE=!new_value!"
)
if !option! equ 4 (
    set /p "new_value=输入新MOTD描述: "
    if "!new_value!" neq "" set "MOTD=!new_value!"
)
if !option! equ 5 (
    set /p "new_value=输入新端口号: "
    if "!new_value!" neq "" set "PORT=!new_value!"
)
if !option! equ 6 (
    set /p "new_value=输入最大玩家数: "
    if "!new_value!" neq "" set "MAX_PLAYERS=!new_value!"
)
if !option! equ 7 (
    set /p "new_value=输入视距 (4-32): "
    if "!new_value!" neq "" set "VIEW_DISTANCE=!new_value!"
)
if !option! equ 8 (
    set /p "new_value=输入JVM参数: "
    if "!new_value!" neq "" set "JVM_ARGS=!new_value!"
)
if !option! equ 9 (
    set /p "new_value=输入服务器参数: "
    if "!new_value!" neq "" set "SERVER_ARGS=!new_value!"
)

:: 保存配置
(
    echo MEMORY=!MEMORY!
    echo CORE=!CORE!
    echo ONLINE_MODE=!ONLINE_MODE!
    echo MOTD=!MOTD!
    echo PORT=!PORT!
    echo MAX_PLAYERS=!MAX_PLAYERS!
    echo VIEW_DISTANCE=!VIEW_DISTANCE!
    echo JVM_ARGS=!JVM_ARGS!
    echo SERVER_ARGS=!SERVER_ARGS!
) > "%CONFIG_FILE%"

goto config_menu

:: 启动服务器
:start_server
call :read_config

:: 更新 server.properties
if exist "server.properties" (
    call :update_properties
) else (
    echo 首次启动，请确保服务器核心已放置
    echo 按任意键启动服务器生成配置文件...
    pause >nul
)

echo 正在启动服务器...
echo 使用内存: !MEMORY!
echo 服务器核心: !CORE!
java -Xms!MEMORY! -Xmx!MEMORY! !JVM_ARGS! -jar !CORE! !SERVER_ARGS!

if errorlevel 1 (
    echo.
    echo 服务器启动失败，请检查:
    echo 1. 内存设置是否过大
    echo 2. 核心文件是否存在
    echo 3. Java是否安装正确
    echo.
    pause
)
goto :eof

:: 更新服务器属性文件
:update_properties
set "properties=server.properties"
set "temp_file=%properties%.tmp"

>"!temp_file!" (
    for /f "usebackq delims=" %%a in ("!properties!") do (
        set "line=%%a"
        set "key=!line: =!"
        set "key=!key:    =!"
        for /f "delims== tokens=1" %%b in ("!key!") do set "key=%%b"
        
        if "!key!"=="online-mode" (
            echo online-mode=!ONLINE_MODE!
        ) else if "!key!"=="motd" (
            echo motd=!MOTD!
        ) else if "!key!"=="server-port" (
            echo server-port=!PORT!
        ) else if "!key!"=="max-players" (
            echo max-players=!MAX_PLAYERS!
        ) else if "!key!"=="view-distance" (
            echo view-distance=!VIEW_DISTANCE!
        ) else (
            echo %%a
        )
    )
)

move /y "!temp_file!" "!properties!" >nul
goto :eof