This tool allows you import playcounts from last.fm to update your clementine database.

This is a temporary solution until [Issue 90](http://code.google.com/p/clementine-player/issues/detail?id=90) of the Clementine project is implemented.
As it works outside of Clementine it needs to be run with Clementine closed (if it is not the case Clementine will raise some error while trying to reach its database).

Interface with the servers is inspired on the lastexport.py script from lasttolibre project:
https://gitorious.org/fmthings/lasttolibre

This tool is working on Linux and may work also on Mac and Windows but wasn't tested on these OS.

References:

http://addons.songbirdnest.com/addon/1458

http://code.google.com/p/sb-vandelay-industries/

Feel free to give me any feedback. I'm searching contributors, contact me if you want to be part of this project

**Changelog:**
  * _clementine\_last\_export-0.2.tar.gz_     Version 0.2:
    * Factorisation of script to improve the maintenance
    * Improve code comments
    * Add a progress bar (correct [issue 9](https://code.google.com/p/clementine-last-export/issues/detail?id=9))
    * Save the configuration of the options (correct [issue 10](https://code.google.com/p/clementine-last-export/issues/detail?id=10))

<font color='gray'>
<ul><li><i>clementine_last_export-0.1.tar.gz</i>     Version 0.1:<br>
<ul><li>Release the tool as a package, correct <a href='https://code.google.com/p/clementine-last-export/issues/detail?id=8'>issue 8</a>
</li><li>Add icon<br>
</li><li>Rename the tool from clementine-last-export to clementine_last_export to avoid dashes<br>
</li><li>Rework the UI<br>
</li><li>Add the option to use the cached file in the UI</li></ul></li></ul>


<ul><li><i>clementine-last-export_2013_04_07.zip</i> 	Version of the 2013-04-07:<br>
<ul><li>Improve speed on second run: the script will only download the titles listen since the previous update<br>
</li><li>Add an option to force the update: if activated, the playcount will be the one on last.fm (even if the one in the database is higher) and the loved tracks will be forced at 5 stars (even if they are already at 4.5 stars.</li></ul></li></ul>

<ul><li><i>clementine-last-export_2013_02_16.zip</i> 	Version of the 2013-02-16:<br>
<ul><li>Add a GUI (<a href='https://code.google.com/p/clementine-last-export/issues/detail?id=4'>issue 4</a>): see the Wiki for more information<br>
</li><li>Correct some errors</li></ul></li></ul>

<ul><li><i>clementine-last-export_2012_08_30.zip</i> 	Version of the 2012-08-30:<br>
<ul><li>Correct the <a href='https://code.google.com/p/clementine-last-export/issues/detail?id=5'>issue 5</a></li></ul></li></ul>

<ul><li><i>clementine-last-export_2012_08_29.zip</i> 	Version of the 2012-08-29:<br>
<ul><li>Add the capacity to import loved tracks (<a href='https://code.google.com/p/clementine-last-export/issues/detail?id=2'>issue 2</a>)</li></ul></li></ul>

<ul><li><i>clementine-last-export_2012_03_04.zip</i> 	Version of the 2012-03-04:<br>
<ul><li>Add a workaround against last.fm server time out</li></ul></li></ul>

<ul><li><i>clementine-last-export_2012_01_31.zip</i> 	Version of the 2012-01-31:<br>
<ul><li>Fix <a href='https://code.google.com/p/clementine-last-export/issues/detail?id=1'>issue 1</a>: The playcounts are updated only if the local playcount is lower than the last.fm playcount</li></ul></li></ul>

<ul><li><i>clementine-last-export_2012_01_06.zip</i> 	Alpha version<br>
</font>