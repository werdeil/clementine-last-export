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
Module containing the GUI of the clementine_last_export tool
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

SERVER_LIST = ["last.fm", "libre.fm"]

# Import icons resource to have the icon image
import icons_rc

class ClemLastExportGui(QtGui.QMainWindow):

    def __init__(self):
        """
        Init function of the class, called at each creation
        """
        super(ClemLastExportGui, self).__init__()
        self.cache_path = self.get_cachepath()
        self.configfile = os.path.expanduser("%sconfig.pkl" %self.cache_path)
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
        Initialisation of the UI, called during the creation of an instance of the class, to create the main window and its elements
        """   
        #MenuBar
        ##Exit menu
        self.exitAction = QtGui.QAction('&Exit', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(QtGui.qApp.quit)
        
        ##Import menu
        self.importAction = QtGui.QAction('&Run', self)
        self.importAction.triggered.connect(self.run_script)
        
        ##About menu
        self.aboutAction = QtGui.QAction('&About Clementine Last Export', self)
        self.aboutAction.triggered.connect(self.open_about)
        self.aboutQtAction = QtGui.QAction('&About Qt', self)
        self.aboutQtAction.triggered.connect(self.open_aboutQt)

        ##Menubar getting all the previously defined menus
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.exitAction)
        self.fileMenu2 = self.menubar.addMenu('&Import')
        self.fileMenu2.addAction(self.importAction)         
        self.fileMenu3 = self.menubar.addMenu('&About')
        self.fileMenu3.addAction(self.aboutAction)
        self.fileMenu3.addAction(self.aboutQtAction) 
        
        #Main window
        ##Part import
        self.lbl_part_import = QtGui.QLabel('Information about the server', self)
        self.lbl_part_import.resize(200, 20)
        self.lbl_part_import.move(15, 30)
        
        ###Server selection
        self.lbl_combo_server  = QtGui.QLabel('Select the server', self)
        self.lbl_combo_server.resize(120, 20)
        self.lbl_combo_server.move(20, 60)        
        
        self.server_combo = QtGui.QComboBox(self)
        for server in SERVER_LIST:
            self.server_combo.addItem(server)
        self.server_combo.move(140, 55)
        self.server_combo.activated[str].connect(self.serverChanged)
        
        ###Server credentials
        self.lbl_username  = QtGui.QLabel('Username', self)
        self.lbl_username.move(20, 90)
        self.field_username = QtGui.QLineEdit(self)
        self.field_username.move(140, 90)
        self.field_username.textChanged[str].connect(self.usernameChanged)
        
        ###Part target
        # Definition of the two radio buttons
        self.playcount_radio_button = QtGui.QRadioButton('Import playcount', self)
        self.playcount_radio_button.resize(160, 20)
        self.playcount_radio_button.move(20, 140)
        self.lovedtracks_radio_button = QtGui.QRadioButton('Import loved tracks', self)
        self.lovedtracks_radio_button.resize(160, 20)
        self.lovedtracks_radio_button.move(20, 170)
        
        #Creation of the group of radio buttons
        self.radio_group = QtGui.QButtonGroup(self)
        self.radio_group.addButton(self.playcount_radio_button)
        self.radio_group.addButton(self.lovedtracks_radio_button)
        #Only one radio button can be selected at once
        self.radio_group.setExclusive(True)
        self.radio_group.buttonClicked.connect(self.targetChanged)
                
        ##Part options
        self.lbl_part_update = QtGui.QLabel('Options', self)
        self.lbl_part_update.move(15, 200)
        
        #Checkbox to activate or not the backup of the database
        self.backup_checkbox = QtGui.QCheckBox('Backup database', self)
        self.backup_checkbox.resize(200, 20)
        self.backup_checkbox.move(20, 230)
        self.backup_checkbox.stateChanged.connect(self.backupChanged)
        
        #Checkbox to activate the force of the update (see tooltip for more information)
        self.force_update_checkbox = QtGui.QCheckBox('Force update', self)
        self.force_update_checkbox.resize(200, 20)
        self.force_update_checkbox.move(20, 260)
        self.force_update_checkbox.stateChanged.connect(self.forceUpdateChanged)
        self.force_update_checkbox.setToolTip('Check this box if you want to force the update\n - of loved tracks already rated at 4.5 stars\n - of playcounts higher locally than the one on the music server')
        
        #Checkbox to activate the use of a cache file
        self.use_cache_checkbox = QtGui.QCheckBox('Use cache file (if available)', self)
        self.use_cache_checkbox.resize(200, 20)
        self.use_cache_checkbox.move(20, 290)
        self.use_cache_checkbox.stateChanged.connect(self.useCacheChanged)
        self.use_cache_checkbox.setToolTip('Check this box if you want to use the cache file from a previous import')        
        
        self.progressbar = QtGui.QProgressBar(self)
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)
        self.progressbar.resize(260, 20)
        self.progressbar.move(20, 320)        
        
        ###Run button
        self.update_button = QtGui.QPushButton('Run', self)
        self.update_button.setToolTip('Run the script')
        self.update_button.resize(self.update_button.sizeHint())
        self.update_button.move(190, 150)  
        self.update_button.clicked.connect(self.run_script)
        #Run button can be triggered by pressing the return key
        self.update_button.setShortcut(self.update_button.tr("Return"))        
        
        ##Global window
        self.resize(300, 370)
        self.center()
        self.setWindowTitle('Clementine Last Export')  
        self.setWindowIcon(QtGui.QIcon(':/myresources/clementine_last_export.png'))
        
        #Status bar 
        self.statusBar().showMessage('Ready')
        
        #Set the UI according to the value of config
        self.restore_config()
        
        #Show the main window  
        self.show()
    
    def restore_config(self):
        """
        Function called to update the UI according to the configuration dictionary
        """
        self.server_combo.setCurrentIndex(SERVER_LIST.index(self.config["server"]))
        self.field_username.setText(self.config["username"])
        if self.config["target"] == Update_playcount:
            self.playcount_radio_button.toggle()
        else:
            self.lovedtracks_radio_button.toggle()
        if self.config["backup_database"]:
            self.backup_checkbox.toggle()
        if self.config["use_cache"]:        
            self.use_cache_checkbox.toggle()
        if self.config["force_update"]:
            self.force_update_checkbox.toggle()
            
        
    def center(self):
        """
        Function called to center the main window to the display screen
        """         
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def run_script(self):
        """
        Function called when pressing the "Run" button on the UI
        """
        if self.config["username"] == '':
            self.statusBar().showMessage('Username needed')
        else: 
            cache_file = os.path.expanduser("%scache_%s.txt" %(self.cache_path, self.config["target"].__name__))
            self.progressbar.reset()
            self.statusBar().showMessage('Running')          
            debug("Running the process %s with the info: server = %s, username = %s, backup = %s, force update = %s, use cache = %s\n"
                    %(self.config["target"], self.config["server"], self.config["username"], self.config["backup_database"], self.config["force_update"], self.config["use_cache"]))
            
            thread1 = self.config["target"](self.config["username"], False, self.config["server"],
                cache_file, 1, self.config["backup_database"], self.config["force_update"], self.config["use_cache"])
            
            #Connect the partDone signal of the thread to the progress bar    
            thread1.partDone.connect(self.updatePBar)
            #Run the thread
            thread1.run()
            
    
    def updatePBar(self, val):
        """
        Function called when the thread progress
        
        :param val: Value of the thread progress
        :type val: float
        """
        self.progressbar.setValue(val)   
        
    def usernameChanged(self, text):
        """
        Function called when the username text field is changed
        
        :param text: Text written in the text field by the user, representing his username
        :type text: string
        """
        self.config["username"] = text
        self.store_config()
        
    def serverChanged(self, text):
        """
        Function called when the server combobox is changed
        
        :param text: Value of the selected element in the combobox
        :type text: string
        """
        self.config["server"] = text
        self.store_config()
                
    def backupChanged(self, state):
        """
        Function called when the "backup database" checkbox changes its state
        
        :param state: State of the "backup database" checkbox, True if the database shall be backed up
        :type state: boolean
        """
        if state == QtCore.Qt.Checked:
            self.config["backup_database"] = True
        else:
            self.config["backup_database"] = False
        self.store_config()        
        
    def forceUpdateChanged(self, state):
        """
        Function called when the "force update" checkbox changes its state
        
        :param state: State of the "force update" checkbox, True if the update is forced
        :type state: boolean
        """
        if state == QtCore.Qt.Checked:
            self.config["force_update"] = True
        else:
            self.config["force_update"] = False
        self.store_config()        
        
    def useCacheChanged(self, state):
        """
        Function called when the "use cache" checkbox changes its state
        
        :param state: State of the "use cahce" checkbox, True if the cache shall be used
        :type state: boolean
        """
        if state == QtCore.Qt.Checked:
            self.config["use_cache"] = True
        else:
            self.config["use_cache"] = False
        self.store_config()    
    
    def targetChanged(self, button):
        """
        Function called when clicked on one of the radiobuttons to select which information shall be imported
        
        :param button: Radiobutton clicked (as they are exclusive, it means that the other one is no longer clicked)
        :type button: QtGui.QRadioButton
        """
        if button.text() == 'Import playcount':
            self.config["target"] = Update_playcount
        else:
            self.config["target"] = Import_loved_tracks
        self.store_config()
        
    def import_completed(self, msg):
        """
        Function called when the thread is finished (normally or not)
        
        :param message: Message sent from the thread
        :type message: string
        """
        QtGui.QMessageBox.information(self, u"Operation finished", msg)        
        self.statusBar().showMessage('Import completed')
        
    def open_about(self):
        """
        Function called when the about dialog is requested
        """
        about_text="""<b>Clementine Last Export</b>
        <br/><br/>
        Developed by Vincent VERDEIL<br/><br/>
        <a href="http://code.google.com/p/clementine-last-export/">http://code.google.com/p/clementine-last-export/</a>"""
        QtGui.QMessageBox.about(self,"About Clementine Last Export", about_text)
        
    def open_aboutQt(self):
        """
        Function called when the aboutQt dialog is requested
        """
        QtGui.QMessageBox.aboutQt(self)
        
    def get_cachepath(self):
        """
        Function called to create the cache repository next to the Clementine data
        
        :return: Path to the cache directory in which the file will be stored
        :rtype: string
        """
        operating_system = platform.system()
        if operating_system == 'Linux':
            cache_path = '~/.clementine_last_export/'
        if operating_system == 'Darwin':
            cache_path = '~/Library/Application Support/clementine_last_export/'
        if operating_system == 'Windows':
            cache_path = '%USERPROFILE%\\.clementine_last_export\\'''
        
        if not os.path.exists(os.path.expanduser(cache_path)):
            os.makedirs(os.path.expanduser(cache_path))
            
        return cache_path

    def store_config(self):
        """
        Function called to stored the configuration of the UI for the next use in a configuration file
        """
        pickle.dump(self.config, open(self.configfile, 'w'))
        
    def load_config(self):
        """
        Function called to load the configuraiton of the UI from a configuration file
        """
        self.config = pickle.load(open(self.configfile))
       
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
