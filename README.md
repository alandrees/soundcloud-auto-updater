soundcloud-auto-updater
=======================

Automatically encodes a PCM wave file (a lit of which is retrived from a specified directory) into a compressed format, properly tagging the file with the correct metadata (encoded into the filename), uploading it to the configured Soundcloud account, and optionally emailing about success/failure.

Depedencies:

Soundcloud SDK (https://www.github.com/soundcloud/soundcloud-python)

 - This requires the 'requests' module (if installing soundcloud module outside of package management)


Tools to automate the generation of the filenames:

Windows (C#.NET and WinForms): https://github.com/alandrees/sc-update-tool-win

Linux (using Python and QTPy): https://github.com/alandrees/sc-update-tool-linux

OSX (??? / Cocoa): Since I don't have access to OSX, I cannot create a Mac/Cocoa version.
