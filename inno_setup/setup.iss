#include "CodeDependencies.iss"

#define   Name       "PPRCheat"
#define   Version    "0.9.0"
#define   Publisher  "BEJlYA"
#define   URL        "https://t.me/BEJlYA"
#define   ExeName    "PPRCheat.exe"

[Setup]
AppId={{82E8192C-F02E-43D8-A478-B4A07EB7889C}
AppName={#Name}
AppVersion={#Version}
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

; Каталог, куда будет записан собранный setup и имя исполняемого файла
OutputDir=F:\projects\PokePowerRequests
OutputBaseFileName=PPRCheat

; Файл иконки
SetupIconFile=F:\projects\PokePowerRequests\assets\images\favicon.ico

; Параметры сжатия
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
; Создание иконки на рабочем столе
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "Создать папку в меню 'Пуск'"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]

; Исполняемый файл
Source: "F:\projects\PokePowerRequests\build\windows\PPRCheat.exe"; DestDir: "{app}"; Flags: ignoreversion
; Прилагающиеся ресурсы
Source: "F:\projects\PokePowerRequests\build\windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]

Name: "{group}\{#Name}"; Filename: "{app}\{#ExeName}"; IconFilename: "{app}\assets\images\favicon.ico"; Tasks: startmenuicon
Name: "{commondesktop}\{#Name}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon; IconFilename: "{app}\assets\images\favicon.ico"

[Code]
function InitializeSetup: Boolean;
begin
  Dependency_AddVC14;
  Result := True;
end;

[Messages]
NameAndVersion=%1