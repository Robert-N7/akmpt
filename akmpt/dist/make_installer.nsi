!define VERSION "0.2.0"
!define PROGRAM_NAME "ANoob's KMP Tool ${VERSION}"
InstallDir "$Documents\akmpt"
Name "${PROGRAM_NAME}"
OutFile "install.exe"
Icon "..\icon.ico"
LicenseData LICENSE
# Request admin rights
RequestExecutionLevel user
!include LogicLib.nsh

page license
page directory
page instfiles

Function .onInit
UserInfo::GetAccountType
pop $0
#${If} $0 != "admin"
 #   MessageBox mb_iconstop "Administrator rights required!"
  #  SetErrorLevel 740   # ERROR_ELEVATION_REQUIRED
   # Quit
# ${EndIf}
FunctionEnd

# INSTALL
Section "install"
SetOutPath "$INSTDIR"
WriteUninstaller "$INSTDIR\uninstall.exe"
File README.md
File LICENSE
# bin
SetOutPath "$INSTDIR\bin"
EnVar::AddValue "PATH" "$INSTDIR\bin"
File /a /r "bin\"
# Shortcuts
CreateDirectory "$SMPROGRAMS\akmpt"
CreateShortCut "$SMPROGRAMS\akmpt\uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

# UNINSTALL
Section "Uninstall"
SetOutPath "$INSTDIR\.."
RMDir /r "$INSTDIR\*.*"
EnVar::DeleteValue "PATH" "$INSTDIR\bin\akmpt.exe"
# RMDir /r "$SMPROGRAMS\akmpt"
SectionEnd

Function .onInstSuccess
  MessageBox MB_OK "Success! Use the command line to start the program."
FunctionEnd

Function un.onUninstSuccess
  MessageBox MB_OK "Akmpt has been removed."
FunctionEnd