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

class ClemLastExportGui(QtGui.QMainWindow):

    def __init__(self):
    
        super(ClemLastExportGui, self).__init__()
        self.initUI()
        
        
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
        label1 = QtGui.QLabel('Import from the server', self)
        label1.move(15, 10)  
                    
        import_button = QtGui.QPushButton('Import playcount', self)
        import_button.setToolTip('Import playcount from Last.fm server')
        import_button.resize(import_button.sizeHint())
        import_button.move(20, 90)
        import_button.clicked.connect(self.notYetImplemented)
        
        server_combo = QtGui.QComboBox(self)
        server_combo.addItem("Last.fm")
        server_combo.addItem("Libre.fm")
        server_combo.move(20, 50)
        server_combo.activated[str].connect(self.notYetImplemented)
        
        label2 = QtGui.QLabel('Update Clementine Database', self)
        label2.move(15, 120)
        
        backup_checkbox = QtGui.QCheckBox('Backup database', self)
        backup_checkbox.move(20, 145)
        backup_checkbox.stateChanged.connect(self.notYetImplemented) 
                    
        update_button = QtGui.QPushButton('Update database', self)
        update_button.setToolTip('Update Playcount of the Clementine DB')
        update_button.resize(update_button.sizeHint())
        update_button.move(20, 175)  
        update_button.clicked.connect(self.notYetImplemented)    
        
        self.resize(350, 250)
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
        
        
    def notYetImplemented(self):
      
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' not yet implemented')
        
def main():

    app = QtGui.QApplication(sys.argv)
    cleg = ClemLastExportGui()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
