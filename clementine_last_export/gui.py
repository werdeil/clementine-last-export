#!/usr/bin/env python
#-*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
GUI to run the clementine_last_export tool
"""

from PyQt4 import QtGui, QtCore

import sys, os
import platform
import pickle

from optparse import OptionParser
import logging
from logging import info, warning, error, debug
from update_playcount import Update_playcount
from import_loved_tracks import Import_loved_tracks

# Import icons resource to have the icon image
import icons_rc

class ClemLastExportGui(QtGui.QMainWindow):

    def __init__(self):
        super(ClemLastExportGui, self).__init__()
        self.configfile = "config.pkl"
        if os.path.exists(self.configfile):
            self.load_config()
        else:
            self.config = {}
            self.config["username"] = ""
            self.config["server"] = "last.fm"
            self.config["backup_database"] = True
            self.config["force_update"] = False
            self.config["use_cache"] = True
            self.config["target"] = Update_playcount
        self.initUI()
        
        
        
    def initUI(self):
        """
        Init method to create the main window and its elements
        """   
        #MenuBar
        ##Exit menu
        exitAction = QtGui.QAction('&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        ##Import menu
        importAction = QtGui.QAction('&Run', self)
        importAction.triggered.connect(self.run_script)
        
        ##About menu
        aboutAction = QtGui.QAction('&About Clementine Last Export', self)
        aboutAction.triggered.connect(self.open_about)
        aboutQtAction = QtGui.QAction('&About Qt', self)
        aboutQtAction.triggered.connect(self.open_aboutQt)

        ##Menubar getting all the previously defined menus
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu2 = menubar.addMenu('&Import')
        fileMenu2.addAction(importAction)         
        fileMenu3 = menubar.addMenu('&About')
        fileMenu3.addAction(aboutAction)
        fileMenu3.addAction(aboutQtAction) 
        
        #Main window
        ##Part import
        lbl_part_import = QtGui.QLabel('Information about the server', self)
        lbl_part_import.resize(200, 20)
        lbl_part_import.move(15, 30)
        
        ###Server selection
        lbl_combo_server  = QtGui.QLabel('Select the server', self)
        lbl_combo_server.resize(120, 20)
        lbl_combo_server.move(20, 60)        
        
        server_combo = QtGui.QComboBox(self)
        server_combo.addItem("last.fm")
        server_combo.addItem("libre.fm")
        server_combo.move(140, 55)
        server_combo.activated[str].connect(self.serverChanged)
        
        ###Server credentials
        lbl_username  = QtGui.QLabel('Username', self)
        lbl_username.move(20, 90)
        field_username = QtGui.QLineEdit(self)
        field_username.move(140, 90)
        field_username.textChanged[str].connect(self.usernameChanged)
        
        ###Part target
        # Definition of the two radio buttons
        playcount_radio_button = QtGui.QRadioButton('Import playcount', self)
        playcount_radio_button.resize(160, 20)
        playcount_radio_button.move(20, 140)
        lovedtracks_radio_button = QtGui.QRadioButton('Import loved tracks', self)
        lovedtracks_radio_button.resize(160, 20)
        lovedtracks_radio_button.move(20, 170)
        
        #the playcount radio button is selected by default
        playcount_radio_button.toggle() 
        
        #Creation of the group of radio buttons
        radio_group = QtGui.QButtonGroup(self)
        radio_group.addButton(playcount_radio_button)
        radio_group.addButton(lovedtracks_radio_button)
        #Only one radio button can be selected at once
        radio_group.setExclusive(True)
        radio_group.buttonClicked.connect(self.targetChanged)
                
        ##Part options
        lbl_part_update = QtGui.QLabel('Options', self)
        lbl_part_update.move(15, 200)
        
        #Checkbox to activate or not the backup of the database
        backup_checkbox = QtGui.QCheckBox('Backup database', self)
        backup_checkbox.resize(200, 20)
        backup_checkbox.move(20, 230)
        #Backup is activated by default
        backup_checkbox.toggle()
        backup_checkbox.stateChanged.connect(self.backupChanged)
        
        #Checkbox to activate the force of the update (see tooltip for more information)
        force_update_checkbox = QtGui.QCheckBox('Force update', self)
        force_update_checkbox.resize(200, 20)
        force_update_checkbox.move(20, 260)
        force_update_checkbox.stateChanged.connect(self.forceUpdateChanged)
        force_update_checkbox.setToolTip('Check this box if you want to force the update\n - of loved tracks already rated at 4.5 stars\n - of playcounts higher locally than the one on the music server')
        
        #Checkbox to activate the use of a cache file
        use_cache_checkbox = QtGui.QCheckBox('Use cache file (if available)', self)
        use_cache_checkbox.resize(200, 20)
        use_cache_checkbox.move(20, 290)
        #Cache file is used by default        
        use_cache_checkbox.toggle()
        use_cache_checkbox.stateChanged.connect(self.useCacheChanged)
        use_cache_checkbox.setToolTip('Check this box if you want to use the cache file from a previous import')        
        
        self.progressbar = QtGui.QProgressBar(self)
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)
        self.progressbar.resize(260, 20)
        self.progressbar.move(20, 320)        
        
        ###Run button
        update_button = QtGui.QPushButton('Run', self)
        update_button.setToolTip('Run the script')
        update_button.resize(update_button.sizeHint())
        update_button.move(190, 150)  
        update_button.clicked.connect(self.run_script)
        #Run button can be triggered by pressing the return key
        update_button.setShortcut(update_button.tr("Return"))        
        
        ##Global window
        self.resize(300, 370)
        self.center()
        self.setWindowTitle('Clementine Last Export')  
        self.setWindowIcon(QtGui.QIcon(':/myresources/clementine_last_export.png'))
        
        #Status bar 
        self.statusBar().showMessage('Ready')
        
        #Show the main window  
        self.show()
        
        
    def center(self):
        """
        Method called to center the main window to the display screen
        """         
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def run_script(self):
        """
        Method called when pressing the "Run" button on the UI
        """
        if self.config["username"] == '':
            self.statusBar().showMessage('Username needed')
        else:
            cache_path = self.get_cachepath() 
            cache_file = cache_path+"cache_%s.txt" %self.config["target"].__name__
            print cache_file, os.path.exists(cache_path)
            self.store_config()
            self.progressbar.reset()
            self.statusBar().showMessage('Running')          
            debug("Running the process %s with the info: server = %s, username = %s, backup = %s, force update = %s, use cache = %s\n"
                    %(self.config["target"], self.config["server"], self.config["username"], self.config["backup_database"], self.config["force_update"], self.config["use_cache"]))
            
            thread1 = self.config["target"](self.config["username"], False, self.config["server"],
                cache_file, 1, self.config["backup_database"], self.config["force_update"], self.config["use_cache"])
                
            thread1.partDone.connect(self.updatePBar)
           
            thread1.run()
            
    
    def updatePBar(self, val):
        """
        Method called when the thread progress
        """
        self.progressbar.setValue(val)   
        
    def usernameChanged(self, text):
        """
        Method called when the username text field is changed
        """
        self.config["username"] = text
        
    def serverChanged(self, text):
        """
        Method called when the server combobox is changed
        """
        self.config["server"] = text
                
    def backupChanged(self, state):
        """
        Method called when the backup checkbox changes its state
        """
        if state == QtCore.Qt.Checked:
            self.config["backup_database"] = True
        else:
            self.config["backup_database"] = False        
        
    def forceUpdateChanged(self, state):
        """
        Method called when the force update checkbox changes its state
        """
        if state == QtCore.Qt.Checked:
            self.config["force_update"] = True
        else:
            self.config["force_update"] = False        
        
    def useCacheChanged(self, state):
        """
        Method called when the use cache checkbox changes its state
        """
        if state == QtCore.Qt.Checked:
            self.config["use_cache"] = True
        else:
            self.config["use_cache"] = False    
    
    def targetChanged(self, button):
        """
        Method called when clicked on one of the radiobuttons
        """
        if button.text() == 'Import playcount':
            self.config["target"] = Update_playcount
        else:
            self.config["target"] = Import_loved_tracks
        
    def import_completed(self, msg):
        """
        Run when the thread is finished (normally or not)
        """
        QtGui.QMessageBox.information(self, u"Operation finished", msg)        
        self.statusBar().showMessage('Import completed')
        
    def open_about(self):
        """
        Method called when the about dialog is requested
        """
        about_text="""<b>Clementine Last Export</b>
        <br/><br/>
        Developed by Vincent VERDEIL<br/><br/>
        <a href="http://code.google.com/p/clementine-last-export/">http://code.google.com/p/clementine-last-export/</a>"""
        QtGui.QMessageBox.about(self,"About Clementine Last Export", about_text)
        
    def open_aboutQt(self):
        """
        Method called when the aboutQt dialog is requested
        """
        QtGui.QMessageBox.aboutQt(self)
        
    def get_cachepath(self):
        """
        Method called to create the cache repository next to the Clementine data
        """
        operating_system = platform.system()
        if operating_system == 'Linux':
            cache_path = '~/.config/Clementine_last_export/'
        if operating_system == 'Darwin':
            cache_path = '~/Library/Application Support/Clementine_last_export/'
        if operating_system == 'Windows':
            cache_path = '%USERPROFILE%\\.config\\Clementine_last_export\\'''
        
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
            
        return cache_path

    def store_config(self):
        pickle.dump(self.config, open(self.configfile, 'w'))
        
    def load_config(self):
        self.config = pickle.load( open(self.configfile))
       
def main():
    """
    Main method of the script, called when the script is run
    """
    app = QtGui.QApplication(sys.argv)
    cleg = ClemLastExportGui()
    sys.exit(app.exec_())

if __name__ == "__main__":

    parser = OptionParser()
    parser.usage = """Usage: %prog [options]
    
    Run the GUI which will use the scripts of the package
    """
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="debug mode")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="activate verbose mode")
    
    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level="INFO")
    if options.debug:
        logging.basicConfig(level="DEBUG")
        
    main()
