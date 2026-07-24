#include "CodeDependencies.iss"

#define   Name       "PPRCheat"
#define   Version    "0.9.2"
#define   Publisher  "Belisor"
#define   URL        "https://t.me/BEJlYA"
#define   ExeName    "PPRCheat.exe"

[Setup]
AppId={{82E8192C-F02E-43D8-A478-B4A07EB7889C}
AppName={#Name}
AppVersion={#Version}
AppVerName={#Name}
AppPublisher={#Publisher}
AppPublisherURL={#URL}
AppSupportURL={#URL}
AppUpdatesURL={#URL}
UninstallDisplayName={#Name}
PrivilegesRequired=admin

; Путь установки по-умолчанию
DefaultDirName={commonpf}\{#Name}
; Имя группы в меню "Пуск"
DefaultGroupName={#Name}
DisableProgramGroupPage=yes

; Каталог, куда будет записан собранный setup и имя исполняемого файла
OutputDir=F:\projects\PokePowerRequests
OutputBaseFileName=PPRCheat

; Файл иконки
SetupIconFile=F:\projects\PokePowerRequests\assets\images\favicon.ico

; Параметры сжатия
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "F:\projects\PokePowerRequests\EULA_ENG.txt"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"; LicenseFile: "F:\projects\PokePowerRequests\EULA_RU.txt"

[CustomMessages]
english.CreateStartMenuEntry=Create Start Menu entry
russian.CreateStartMenuEntry=Создать папку в меню "Пуск"

[Tasks]
; Создание иконки на рабочем столе
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
; Создание иконки в панели Пуск
Name: "startmenuicon"; Description: "{cm:CreateStartMenuEntry}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]

; Исполняемый файл
Source: "F:\projects\PokePowerRequests\build\windows\PPRCheat.exe"; DestDir: "{app}"; Flags: ignoreversion restartreplace
; Прилагающиеся ресурсы
Source: "F:\projects\PokePowerRequests\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs restartreplace
; Шаблон конфига (в AppData)
Source: "F:\projects\PokePowerRequests\user_data\config.json"; DestDir: "{commonappdata}\PPRCheat\user_data"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#Name}"; Filename: "{app}\{#ExeName}"; IconFilename: "{app}\app\assets\images\favicon.ico"; Tasks: startmenuicon
Name: "{commondesktop}\{#Name}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon; IconFilename: "{app}\app\assets\images\favicon.ico"

[Run]
Filename: "{app}\{#ExeName}"; Description: "{cm:LaunchProgram,{#Name}}"; Flags: postinstall nowait skipifsilent

[Code]
function InitializeSetup: Boolean;
begin
  Dependency_AddVC14;
  Result := True;
end;