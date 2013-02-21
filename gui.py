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
Gui to run the clementine last export tool
"""

from PyQt4 import QtGui, QtCore

import sys
import threading
from optparse import OptionParser
import logging
from logging import info, warning, error, debug
from update_playcount import update_playcount
from import_loved_tracks import import_loved_tracks
 

class ClemLastExportGui(QtGui.QMainWindow):

    def __init__(self):    
        super(ClemLastExportGui, self).__init__()
        self.initUI()
        self.username = ""
        self.server = "last.fm"
        self.backup_database = True
        self.target = update_playcount
        
        
    def initUI(self):   
        #MenuBar
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        importAction = QtGui.QAction('&Run', self)
        importAction.triggered.connect(self.run_script)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu2 = menubar.addMenu('&Import')
        fileMenu2.addAction(importAction) 
        
        #Main window
        ##Part import
        lbl_part_import = QtGui.QLabel('Information about the server', self)
        lbl_part_import.resize(200, 20)
        lbl_part_import.move(15, 10)
        
        ###Server selection
        lbl_combo_server  = QtGui.QLabel('Select the server', self)
        lbl_combo_server.resize(120, 20)
        lbl_combo_server.move(20, 40)        
        
        server_combo = QtGui.QComboBox(self)
        server_combo.addItem("last.fm")
        server_combo.addItem("libre.fm")
        server_combo.move(140, 35)
        server_combo.activated[str].connect(self.serverChanged)
        
        ###Server credentials
        lbl_username  = QtGui.QLabel('Username', self)
        lbl_username.move(20, 70)
        field_username = QtGui.QLineEdit(self)
        field_username.move(140, 70)
        self.username = field_username.textChanged[str].connect(self.usernameChanged)
                
        ##Part update
        lbl_part_update = QtGui.QLabel('Options', self)
        lbl_part_update.move(15, 120)
        
        backup_checkbox = QtGui.QCheckBox('Backup database', self)
        backup_checkbox.resize(200,20)
        backup_checkbox.move(20, 150)
        backup_checkbox.toggle()
        backup_checkbox.stateChanged.connect(self.backupChanged)
        
        radio_button1 = QtGui.QRadioButton('Import playcount', self)
        radio_button1.resize(160,20)
        radio_button1.move(20, 180)
        radio_button1.toggle()
        radio_button2 = QtGui.QRadioButton('Import loved tracks', self)
        radio_button2.resize(160,20)
        radio_button2.move(20, 210)
        
        radio_group = QtGui.QButtonGroup(self)
        radio_group.addButton(radio_button1)
        radio_group.addButton(radio_button2)
        radio_group.setExclusive(True)
        radio_group.buttonClicked.connect(self.targetChanged)
        
                    
        update_button = QtGui.QPushButton('Run', self)
        update_button.setToolTip('Run the script')
        update_button.resize(update_button.sizeHint())
        update_button.move(190, 190)  
        update_button.clicked.connect(self.run_script)    
        
        self.resize(300, 300)
        self.center()
        self.setWindowTitle('Clementine-Last-Export')
        
        #Status bar 
        self.statusBar().showMessage('Ready')
          
        self.show()
        
        
    def center(self):            
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def run_script(self):
        if self.username == '':
            self.statusBar().showMessage('Username needed')
        else:
            self.statusBar().showMessage('Running')            
            print "Running the process %s with the infos: server = %s, username = %s, backup = %s\n" %(self.target, self.server, self.username, self.backup_database)
            self.target(self.username, False, self.server, "%s.txt" %self.target.__name__,
                          1, self.backup_database)
            
            ## Thread part commented as it is not working as expected yet
            #thread1 = threading.Thread(group=None, target=self.target, name='clementine_last_export',
            #              args=(self.username, "extract_last_fm.txt", self.server, "extract_last_fm.txt",
            #              1, self.backup_database))
            #thread1.start()            
            #thread1.join()
            self.statusBar().showMessage('Import completed')
        
        
    def usernameChanged(self,text):
        self.username = text
        
    def serverChanged(self,text):
        self.server = text
        
        
    def backupChanged(self, state):
        if state == QtCore.Qt.Checked:
            self.backup_database = True
        else:
            self.backup_database = False
    
    
    def targetChanged(self, button):
        if button.text() == 'Import playcount':
            self.target = update_playcount
        else:
            self.target = import_loved_tracks
        
    def notYetImplemented(self):      
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' not yet implemented')
        
def main():

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
