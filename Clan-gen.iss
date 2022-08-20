; Clan-gen Installer Script

#define ApplicationBaseName "Clan-gen"
#define ApplicationFullName "Clan-gen (fan edit) by Sablesteel"

; Update this line to the date of the latest Clan-gen (fan edit) by Sablesteel release 
; (or choose your own version-numbering scheme)
#define ApplicationVersion "2022.08.10"

#define ApplicationURL "https://sablesteel.itch.io/clan-gen-fan-edit"

; Comment out the following line and uncomment the second one in order to place help files, EULA, etc.
; in the same program group as the main Clan-gen' shortcuts
;#define DocumentationFolder "Documentation"
;#define DocumentationFolder "."

; Filenames for the compiled installer
#define InstallerBaseName ApplicationBaseName + " " + ApplicationVersion
#define InstallerFullName InstallerBaseName + ".exe"

; Filenames for the Inno sourcecode
#define SourceFullName ApplicationBaseName + ".iss"

;-------------------------------------------------------------------------------

[Setup]
; if using a Eula uncomment this line
;LicenseFile=Eula.txt

OutputBaseFilename={#InstallerBaseName}

SourceDir=.
AppName={#ApplicationFullName}
DefaultDirName={commonpf}\{#ApplicationFullName}
DefaultGroupName={#ApplicationFullName}
OutputDir=.

; Control Panel information
AppPublisherURL={#ApplicationURL}
AppVersion={#ApplicationVersion}

; Installer icon (if you'd like to provide one)
SetupIconFile=.\main.ico
; Uninstalling will not delete saves so I figured no need for an uninstaller.
Uninstallable=no

; Installer information
VersionInfoProductName={#ApplicationFullName}
VersionInfoVersion={#ApplicationVersion}

;-------------------------------------------------------------------------------

[Files]
Source: "*"; DestDir: {app}; Excludes: "{#InstallerFullName},{#SourceFullName}";
Source: ".\resources\*"; DestDir: {app}\resources;
Source: ".\sprites\*"; DestDir: {app}\sprites;
; Flags: onlyifdoesntexist prevents settings and clanlist.txt from being overwritten after update
Source: ".\saves\*"; DestDir: {app}\saves; Flags: onlyifdoesntexist;
[Dirs]
; Permissions: users-full allows the user to write to the saves directory
Name: "{app}\saves"; Permissions: users-full

;-------------------------------------------------------------------------------
[Icons]
;; Create Clan-gen (fan edit) icons
Name: {group}\Clan-gen (fan edit); Filename: {app}\main.exe; Comment: "Clan-gen (fan edit) by Sablesteel"
Name: {commondesktop}\Clan-gen (fan edit); Filename: {app}\main.exe; Comment: "Clan-gen (fan edit) by Sablesteel";

; Uninstall program Comment out to disable shortcut 
;Name: {group}\Uninstall {#ApplicationFullName}; Filename: {uninstallexe}
