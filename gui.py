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

from PyQt4 import QtGui

import sys
from update_playcount import main as update_playcount

class ClemLastExportGui(QtGui.QMainWindow):

    def __init__(self):
    
        super(ClemLastExportGui, self).__init__()
        self.initUI()
        self.username = ""
        self.server = "last.fm"
        self.backup_database = True
        
        
    def initUI(self):
    
        #MenuBar
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        importAction = QtGui.QAction('&Import from server', self)
        exitAction.triggered.connect(self.notYetImplemented)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu2 = menubar.addMenu('&Import')
        fileMenu2.addAction(importAction) 
        
        #Main window
        ##Part import
        lbl_part_import = QtGui.QLabel('Import from the server', self)
        lbl_part_import.resize(200, 20)
        lbl_part_import.move(15, 10)
        
        ###Server selection
        lbl_combo_server  = QtGui.QLabel('Select the server', self)
        lbl_combo_server.resize(200, 20)
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
        field_username.move(100, 70)
        self.username = field_username.textChanged[str].connect(self.usernameChanged)
        
        ###Import button            
#        import_button = QtGui.QPushButton('Import playcount', self)
#        import_button.setToolTip('Import playcount from Last.fm server')
#        import_button.resize(import_button.sizeHint())
#        import_button.move(20, 90)
#        import_button.clicked.connect(self.notYetImplemented)
        
        ##Part update
        lbl_part_update = QtGui.QLabel('Update Clementine database', self)
        lbl_part_update.resize(200, 20)
        lbl_part_update.move(15, 120)
        
        backup_checkbox = QtGui.QCheckBox('Backup database', self)
        backup_checkbox.resize(200,20)
        backup_checkbox.move(20, 150)
        backup_checkbox.toggle()
        backup_checkbox.stateChanged.connect(self.backupChanged) 
                    
        update_button = QtGui.QPushButton('Run', self)
        update_button.setToolTip('Run the script')
        update_button.resize(update_button.sizeHint())
        update_button.move(20, 175)  
        update_button.clicked.connect(self.run_script)    
        
        self.resize(450, 300)
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
        self.statusBar().showMessage('Running...')
        update_playcount(self.username, "extract_last_fm.txt", self.server, "extract_last_fm.txt", 1, self.backup_database)
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
               
        
    def notYetImplemented(self):
      
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' not yet implemented')
        
def main():

    app = QtGui.QApplication(sys.argv)
    cleg = ClemLastExportGui()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
