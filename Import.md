# Introduction #

This page will explain how to import informations from last.fm when the server rejects you


# Details #

If when import playcounts from last fm the following information is displayed:

> _Getting page xx of yy.._

> _Failed to open page xx_

> _Wrote page 1-xx of yy to file extract\_last\_fm.txt, exiting._


You don't have to start from the begginning, you can use the -p option of the script to give it a startpage, if this option is provided the extract file (by default extract\_to\_last\_fm.txt) is not overwritten but completed.