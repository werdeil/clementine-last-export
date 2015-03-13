# Introduction #

This section will describe how to use the script and its options

# Details #

  * If you have installed it through the package, simply run **_clementine\_last\_export_** in a bash, the GUI shall start.

# Old way to run it (or if you didn't install the package #
  * Through the gui, by simply running the gui.py python script:
```
>python gui.py
```
> or
```
>./gui.py
```
> if the file has the correct permissions.

  * Through a command line:
```
>python update_playcount.py <username> [options]
```
> or
```
>python import_loved_tracks.py <username> [options]
```

> The following options are available:
|-h|--help|show the help message and exit|
|:-|:-----|:-----------------------------|
|-p STARTPAGE|--page=STARTPAGE|page to start fetching tracks from, default is 1|
|-e EXTRACT\_FILE| --extract-file=EXTRACT\_FILE|extract file name, default is extract\_last\_fm.txt|
|-s SERVER|--server=SERVER|server to fetch track info from, default is last.|
|-b|--backup|backup db first|
|-i INPUT\_FILE|--input-file=INPUT\_FILE|give already extracted file as input|
|-d|--debug|activate debug mode|
|-v| --verbose|activate verbose mode|