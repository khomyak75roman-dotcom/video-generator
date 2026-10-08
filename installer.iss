; Инсталятор "Генератор відео" — кнопка на робочому столі ставиться автоматично
[Setup]
AppName=Генератор відео
AppVersion=1.0
AppPublisher=khomyak75roman
DefaultDirName={autopf}\VideoGenerator
DefaultGroupName=Генератор відео
OutputBaseFilename=VideoGenerator-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=low

[Files]
Source: "dist\VideoGenerator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; КНОПКА НА РОБОЧОМУ СТОЛІ:
Name: "{autodesktop}\🎬 Генератор відео"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"
Name: "{autoprograms}\🎬 Генератор відео"; Filename: "{app}\VideoGenerator.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\VideoGenerator.exe"; Description: "Запустити генератор"; Flags: nowait postinstall skipifsilent
