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

SERVER_LIST = ["last.fm", "libre.fm"]
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
        
        #Set the UI according to the value of config dictionnary
        self.restore_config()
        
        #Show the main window  
        self.show()
    
    def restore_config(self):
        #Update option according to config
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
