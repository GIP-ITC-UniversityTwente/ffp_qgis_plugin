import os
import re
from datetime import datetime
from uuid import uuid4
from PyQt5.QtCore import QSettings, QPoint, Qt
from PyQt5.QtWidgets import QApplication, QAction, QInputDialog, QTableWidget, QTableWidgetItem, QComboBox, QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QLabel, QDialogButtonBox, QLineEdit, QTextEdit
from PyQt5.QtGui import QIcon, QFont, QColor
from qgis.gui import QgsRubberBand
from qgis.core import Qgis, QgsProject, QgsProviderRegistry, QgsDataSourceUri, QgsTransaction, QgsDistanceArea, QgsPoint, QgsGeometry, QgsVectorLayer, QgsFillSymbol, QgsMarkerSymbol, QgsPalLayerSettings, QgsTextFormat, QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsVectorLayerSimpleLabeling


class setFfpIcon():

    def __init__(self, window = None):
        if type(window) != type(None):
            basepath = os.path.dirname(os.path.realpath(__file__))
            window.icons_folder = os.path.join(basepath, 'icons/')
            window.setWindowIcon(QIcon(os.path.join(window.icons_folder, 'ffp.png')))
#---


class toleranceDialog(QDialog):

    def __init__(self, objectid):
        super(toleranceDialog, self).__init__()

        setFfpIcon(self)
        self.setWindowTitle(" Symplify spatialunit:  %s" % objectid)

        self.distanceLabel = QLabel('Simplification tolerance: ')
        self.toleranceValue = QLineEdit()

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.distanceLabel)
        hbox1.addWidget(self.toleranceValue)
        hbox1.addWidget(QLabel('m. '))

        hbox2 = QHBoxLayout()
        self.saveButton = QPushButton("Execute")
        self.saveButton.setFixedWidth(120)
        self.saveButton.clicked.connect(lambda:self.onExecute())
        hbox2.addWidget(self.saveButton)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedWidth(150)
        self.cancelButton.clicked.connect(lambda:self.onCancel())
        hbox2.addWidget(self.cancelButton)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)
    #---

    def onCancel(self):
        self.reject()
    #---

    def onExecute(self):
        self.done(1)
    #---

    def setTolerance(self, toleranceValue):
        self.toleranceValue.setText(str(toleranceValue))
    #---
#---


class settingsDialog(QDialog):

    def __init__(self):
        super(settingsDialog, self).__init__()

        setFfpIcon(self)
        self.setWindowTitle(" FFP Plugin Settings")

        self.distanceLabel = QLabel('Distnace Threshold: ')
        self.distanceValue = QLineEdit()

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.distanceLabel)
        hbox1.addWidget(self.distanceValue)
        hbox1.addWidget(QLabel('m. '))

        hbox2 = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.saveButton.setFixedWidth(120)
        self.saveButton.clicked.connect(lambda:self.onSave())
        hbox2.addWidget(self.saveButton)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedWidth(150)
        self.cancelButton.clicked.connect(lambda:self.onCancel())
        hbox2.addWidget(self.cancelButton)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)
    #---

    def onCancel(self):
        self.reject()
    #---

    def onSave(self):
        self.done(1)
    #---

    def setDistanceThreshold(self, thresholdValue):
        self.distanceValue.setText(str(thresholdValue))
    #---
#---


class selectSpatialunitDialog(QDialog):

    def __init__(self, layer, items):
        super(selectSpatialunitDialog, self).__init__()

        setFfpIcon(self)
        self.setWindowTitle('Spatialunit selection')
        self.layer = layer

        self.choices = QComboBox()
        self.choices.addItems(items)
        self.choices.currentTextChanged.connect(self.onChange)


        vbox = QVBoxLayout()
        vbox.addWidget(QLabel('Select the spatialunit to be deleted:'))
        vbox.addWidget(self.choices)


        hbox = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.setFixedWidth(120)
        self.okButton.clicked.connect(lambda:self.onOk())
        hbox.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedWidth(150)
        self.cancelButton.clicked.connect(lambda:self.onCancel())
        hbox.addWidget(self.cancelButton)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setSelection(items[0])
    #---

    def onChange(self, value):
        self.setSelection(value)
    #---

    def setSelection(self, objectid):
        self.layer.selectByExpression('"objectid"=%s' % (objectid))
    #---

    def onOk(self):
        self.done(int(self.choices.currentText()))
    #---

    def onCancel(self):
        self.reject()
    #---
#---


class tableWindow(QDialog):

    def __init__(self):
        super(tableWindow, self).__init__()

        setFfpIcon(self)
        self.setWindowTitle(' Records Associated with spatialunit: ')

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Table', 'Details', 'GlobalID'])

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.setColumnWidth(1, 400)
        self.tableWidget.setColumnWidth(2, 600)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tableWidget)

        self.question = QLabel('\nDo you want to deleete these records?\n')
        self.question.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.question)

        hbox = QHBoxLayout()
        self.okButton = QPushButton("Yes")
        self.okButton.setFixedWidth(120)
        self.okButton.clicked.connect(lambda:self.onYes())
        hbox.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedWidth(150)
        self.cancelButton.clicked.connect(lambda:self.onCancel())
        hbox.addWidget(self.cancelButton)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
    #---

    def setData(self, id, records, iface):
        self.tableWidget.setRowCount(len(records))
        for i, (table, desc, globalid) in enumerate(records):
            self.tableWidget.setItem(i,0, QTableWidgetItem(table))
            self.tableWidget.setItem(i,1, QTableWidgetItem(desc))
            self.tableWidget.setItem(i,2, QTableWidgetItem(globalid))

        if len(records) < 3:
            extraHeight = 0
        elif len(records) > 10:
            extraHeight = 480
        else:
            extraHeight = (len(records) - 2) * 70

        self.setWindowTitle(' Records Associated with spatialunit: %s' % id)
        self.setGeometry(0, 0, 1400, 390 + extraHeight)
        self.move(iface.mapCanvas().mapToGlobal(QPoint(50, 75)))
    #---

    def onYes(self):
        self.done(QMessageBox.Yes)
    #---

    def onCancel(self):
        self.reject()
    #---
#---


class moveOneToTwoWindow(QDialog):

    def __init__(self):
        super(moveOneToTwoWindow, self).__init__()

        setFfpIcon(self)
        self.setWindowTitle(" Move Point -1- to -2-")

        vbox = QVBoxLayout()
        self.radio1 = QRadioButton('Option 1')
        self.radio1.toggled.connect(lambda:self.onChange())
        vbox.addWidget(self.radio1)
        self.radio2 = QRadioButton("Option 2")
        self.radio2.toggled.connect(lambda:self.onChange())
        vbox.addWidget(self.radio2)
        self.label = QLabel('')
        vbox.addWidget(self.label)

        hbox = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.setFixedWidth(120)
        self.okButton.setDisabled(True)
        self.okButton.clicked.connect(lambda:self.onSelect())
        hbox.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedWidth(150)
        self.cancelButton.clicked.connect(lambda:self.onCancel())
        hbox.addWidget(self.cancelButton)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.pointIds = None
    #---

    def onChange(self):
        if self.radio1.isChecked():
            self.sqlSession.executeSql("""SELECT ffp_mueva_1_a_2(%s, %s, false);""" % (self.pointIds[0], self.pointIds[1]), False)
        elif self.radio2.isChecked():
            self.sqlSession.executeSql("""SELECT ffp_mueva_1_a_2(%s, %s, false);""" % (self.pointIds[1], self.pointIds[0]), False)
        self.iface.mapCanvas().refreshAllLayers()
        self.okButton.setEnabled(True)
    #---

    def setOptions(self, pointIds, distance, iface, session):
        self.iface = iface
        self.sqlSession = session
        self.pointIds = pointIds
        self.radio1.setText(' %s ⟶ %s' % (pointIds[0], pointIds[1]))
        self.radio2.setText(' %s ⟶ %s' % (pointIds[1], pointIds[0]))
        self.label.setText('  The distance between the points is:  %s m' % ('{:.1f}'.format(distance)))
        self.label.adjustSize()
        self.move(self.iface.mapCanvas().mapToGlobal(QPoint(50, 75)))
    #---

    def onSelect(self):
        if self.radio1.isChecked():
            self.done(1)
        elif self.radio2.isChecked():
            self.done(2)
    #---

    def onCancel(self):
        self.reject()
    #---
#---


class actionWindow(QDialog):

    def __init__(self, iface, title = 'FFP Window', choiceWindow = True, width = None, left = 50, top = 75):
        super(actionWindow, self).__init__()

        setFfpIcon(self)
        self.setWindowTitle(title)

        if choiceWindow:
            self.move(iface.mapCanvas().mapToGlobal(QPoint(left, top)))

        self.mainText = QLabel()
        self.mainText.setVisible(False)
        self.mainText.setWordWrap(True)

        self.descriptionText = QTextEdit()
        self.descriptionText.setMaximumHeight(220)
        self.descriptionText.setReadOnly(True)
        font = QFont()
        font.setFamily('Courier')
        self.descriptionText.setFont(font)
        self.descriptionText.setVisible(False)

        self.warningText = QLabel()
        self.warningText.setVisible(False)
        self.warningText.setWordWrap(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.mainText)
        vbox.addWidget(self.descriptionText)
        vbox.addWidget(self.warningText)

        hbox = QHBoxLayout()
        if choiceWindow:
            self.yesButton = QPushButton("Yes")
            self.yesButton.clicked.connect(lambda:self.onYes())
            hbox.addWidget(self.yesButton)
            self.noButton = QPushButton("No")
            self.noButton.clicked.connect(lambda:self.onNo())
            hbox.addWidget(self.noButton)
        else:
            self.okButton = QPushButton("OK")
            self.okButton.clicked.connect(lambda:self.onOk())
            hbox.addWidget(self.okButton)
        hbox.setAlignment(Qt.AlignRight)

        self.setMaximumHeight(400)
        self.setMaximumWidth(450)
        if type(width) != type(None):
            if width > 450:
                self.setMaximumWidth(width)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
    #---

    def setMainText(self, text):
        self.mainText.setVisible(True)
        self.mainText.setText(text)
    #---

    def setDescriptionText(self, text):
        self.descriptionText.setVisible(True)
        self.descriptionText.setText(text)
    #---

    def setWarningText(self, text):
        self.warningText.setVisible(True)
        self.warningText.setText(text)
    #---

    def onYes(self):
        self.done(QMessageBox.Yes)
    #---

    def onNo(self):
        self.done(QMessageBox.No)
    #---

    def onOk(self):
        self.done(0)
    #---
#---


class simplifyMsgWindow(QDialog):

    def __init__(self, plugin, sqlCode, polygon):
        super(simplifyMsgWindow, self).__init__()
        self.plugin = plugin
        self.sqlCode = sqlCode
        self.polygon = polygon
        self.userAction = True

        setFfpIcon(self)
        self.setWindowTitle(' Check the Results')
        self.move(self.plugin.iface.mapCanvas().mapToGlobal(QPoint(50, 75)))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)

        self.setMaximumWidth(450)
        self.setMinimumWidth(450)
        self.setMaximumHeight(450)

        self.questionText = QLabel('\nClick OK to complete the operation...\n')

        vbox = QVBoxLayout()
        vbox.addWidget(self.questionText)

        hbox = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(lambda:self.onOk())
        hbox.addWidget(self.okButton)
        hbox.setAlignment(Qt.AlignRight)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
    #---

    def onOk(self):
        self.userAction = False
        self.close()
        self.plugin.endSimplify(self.sqlCode, self.polygon)
    #---

    def closeEvent(self, evt):
        if self.userAction:
            self.plugin.endSimplify(self.sqlCode, self.polygon)
    #---
#---


class mergePanel(QDialog):

    def __init__(self, plugin, details = None, width = None, left = 50, top = 75):
        super(mergePanel, self).__init__()
        self.plugin = plugin
        self.userAction = True

        setFfpIcon(self)
        self.setWindowTitle(' Merge Lines Info Panel')
        self.move(self.plugin.iface.mapCanvas().mapToGlobal(QPoint(left, top)))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)

        if width > 450:
            self.setMaximumWidth(width)
        self.setMinimumWidth(450)

        self.mainText = QLabel('Operation Details:')

        self.details = QTextEdit(details)
        self.details.setReadOnly(True)
        self.details.setMinimumHeight(120)
        descFont = QFont()
        descFont.setFamily('Courier')
        self.details.setFont(descFont)

        self.questionText = QLabel('\nDo you want to proceed?')

        vbox = QVBoxLayout()
        vbox.addWidget(self.mainText)
        vbox.addWidget(self.details)
        vbox.addWidget(self.questionText)

        hbox = QHBoxLayout()
        self.yesButton = QPushButton("Yes")
        self.yesButton.clicked.connect(lambda:self.onYes())
        hbox.addWidget(self.yesButton)
        self.noButton = QPushButton("No")
        self.noButton.clicked.connect(lambda:self.onNo())
        hbox.addWidget(self.noButton)
        hbox.setAlignment(Qt.AlignRight)

        vbox.addLayout(hbox)
        self.setLayout(vbox)
    #---

    def onYes(self):
        self.userAction = False
        self.close()
        self.plugin.performMerge()
    #---

    def onNo(self):
        self.userAction = False
        self.close()
        self.plugin.cancelMerge()
    #---

    def closeEvent(self, evt):
        if self.userAction:
            self.plugin.cancelMerge()
    #---
#---


class FfpToolsPlugin:

    def __init__(self, iface):
        self.iface = iface

        basepath = os.path.dirname(os.path.realpath(__file__))
        self.icons_folder = os.path.join(basepath, 'icons/')

        self.defaultThresholdMsg = 'Some distances fall outside the allowed distance threshold of 0000 meters!!!'
        self.calculator = QgsDistanceArea()
        self.calculator.setEllipsoid('WGS84')
        self.thresholdValue = 2.5
        self.toleranceValue = 0.5
        self.schema = 'load'
        self.activeSession = False

        self.actions = []
        self.canvasLines = []

        icon = os.path.join(os.path.join(self.icons_folder, 'edit.png'))
        editAction = QAction(QIcon(icon), 'Edit', self.iface.mainWindow())
        editAction.setToolTip("""
            <b>Edit</b>
            Start an editing session&nbsp;""")
        editAction.triggered.connect(self.startEditSession)
        editAction.setDisabled(True)
        self.actions.append(editAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'refresh.svg'))
        refreshAction = QAction(QIcon(icon), 'Refresh', self.iface.mainWindow())
        refreshAction.setToolTip("""
            <b>Refresh</b>
            Reloads the data of the layers of the active connection&nbsp;""")
        refreshAction.setDisabled(True)
        refreshAction.triggered.connect(self.onRefresh)
        self.actions.append(refreshAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'move_1_to_2.svg'))
        moveonetotwoAction = QAction(QIcon(icon), 'Move 1 to 2', self.iface.mainWindow())
        moveonetotwoAction.setToolTip("""
            <b>Move 1 to 2</b>
            Move point -1- to the position of point -2-&nbsp;""")
        moveonetotwoAction.setDisabled(True)
        moveonetotwoAction.triggered.connect(self.moveOneToTwo)
        self.actions.append(moveonetotwoAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'move_to_midpoint.svg'))
        movetomidpointAction = QAction(QIcon(icon), 'Move to Mid-Point', self.iface.mainWindow())
        movetomidpointAction.setToolTip("""
            <b>Move to Mid-Point</b>
            Repositions mutiple points to a weighted centroid location based on their accuracy&nbsp;""")
        movetomidpointAction.setDisabled(True)
        movetomidpointAction.triggered.connect(self.moveToMidpoint)
        self.actions.append(movetomidpointAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'set_anchor.png'))
        setanchorAction = QAction(QIcon(icon), 'Set Point to Anchor', self.iface.mainWindow())
        setanchorAction.setToolTip("""
            <b>Set Point to Anchor</b>
            Changes the type of a set of one or more points to "Anchor"&nbsp;""")
        setanchorAction.setDisabled(True)
        setanchorAction.triggered.connect(self.setToAnchor)
        self.actions.append(setanchorAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'set_vertex.png'))
        setanchorAction = QAction(QIcon(icon), 'Set Point to Vertex', self.iface.mainWindow())
        setanchorAction.setToolTip("""
            <b>Set Point to Vertex</b>
            Changes the type of a set of one or more points to "Vertex"&nbsp;""")
        setanchorAction.setDisabled(True)
        setanchorAction.triggered.connect(self.setToVertex)
        self.actions.append(setanchorAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'project_point.svg'))
        projectpointAction = QAction(QIcon(icon), 'Project Point', self.iface.mainWindow())
        projectpointAction.setToolTip("""
            <b>Project Point</b>
            Create a new vertex on the boundary of a spatialunit at the closest position to a given source point&nbsp;""")
        projectpointAction.setDisabled(True)
        projectpointAction.triggered.connect(self.projectPoint)
        self.actions.append(projectpointAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'project_vertex.svg'))
        projectvertexAction = QAction(QIcon(icon), 'Project Vertex', self.iface.mainWindow())
        projectvertexAction.setToolTip("""
            <b>Project Vertex</b>
            Create a projected vertex on the boundary of a chosen spatialunit&nbsp;""")
        projectvertexAction.setDisabled(True)
        projectvertexAction.triggered.connect(self.projectVertex)
        self.actions.append(projectvertexAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'join_lines.svg'))
        joinlinesAction = QAction(QIcon(icon), 'Join Adjacent Points', self.iface.mainWindow())
        joinlinesAction.setToolTip("""
            <b>Join Adjacent Points</b>
            Merge pairs of points located in adjecent line segments based on the distances from each other&nbsp;""")
        joinlinesAction.setDisabled(True)
        joinlinesAction.triggered.connect(self.joinLines)
        self.actions.append(joinlinesAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'add_midpoint.svg'))
        addmidpointAction = QAction(QIcon(icon), 'Add Mid-Point', self.iface.mainWindow())
        addmidpointAction.setToolTip("""
            <b>Add Mid-Point</b>
            Add a vertex in between a pair of points from one spatialunit&nbsp;""")
        addmidpointAction.setDisabled(True)
        addmidpointAction.triggered.connect(self.addMidpoint)
        self.actions.append(addmidpointAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'delete_point.svg'))
        deletepointAction = QAction(QIcon(icon), 'Delete Point', self.iface.mainWindow())
        deletepointAction.setToolTip("""
            <b>Delete Point</b>
            Remove selected point&nbsp;""")
        deletepointAction.setDisabled(True)
        deletepointAction.triggered.connect(self.deletePoint)
        self.actions.append(deletepointAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'delete_polygon.svg'))
        deletepolygontAction = QAction(QIcon(icon), 'Delete Spatialunit', self.iface.mainWindow())
        deletepolygontAction.setToolTip("""
            <b>Delete Spatialunit</b>
            Remove a specific spatilaunit and all its associated data (right, attachmets, etc.)&nbsp;""")
        deletepolygontAction.setDisabled(True)
        deletepolygontAction.triggered.connect(self.deletePolygon)
        self.actions.append(deletepolygontAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'simplify.svg'))
        simplifyAction = QAction(QIcon(icon), 'Simplify Boundaries', self.iface.mainWindow())
        simplifyAction.setToolTip("""
            <b>Merge Boundaries</b>
            Merge the boundaries of two adjacent spatialunits&nbsp;""")
        simplifyAction.setDisabled(True)
        simplifyAction.triggered.connect(self.simplifyBoundaries)
        self.actions.append(simplifyAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'merge.png'))
        mergeAction = QAction(QIcon(icon), 'Merge Boundaries', self.iface.mainWindow())
        mergeAction.setToolTip("""
            <b>Merge Boundaries</b>
            Merge the boundaries of two adjacent spatialunits&nbsp;""")
        mergeAction.setDisabled(True)
        mergeAction.triggered.connect(self.mergeBoundaries)
        self.actions.append(mergeAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'settings.png'))
        settingsAction = QAction(QIcon(icon), 'Settings', self.iface.mainWindow())
        settingsAction.setToolTip("""
            <b>Settings</b>
            Change default values for the current session&nbsp;""")
        settingsAction.setDisabled(True)
        settingsAction.triggered.connect(self.setSettings)
        self.actions.append(settingsAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'styling.svg'))
        resetStyles = QAction(QIcon(icon), 'Reset Styles', self.iface.mainWindow())
        resetStyles.setToolTip("""
            <b>Reset Styles</b>
            Use the default layers styles&nbsp;""")
        resetStyles.setDisabled(True)
        resetStyles.triggered.connect(self.resetStyles)
        self.actions.append(resetStyles)

        icon = os.path.join(os.path.join(self.icons_folder, 'undo.svg'))
        undoAction = QAction(QIcon(icon), 'Undo', self.iface.mainWindow())
        undoAction.setToolTip("""
            <b>Undo</b>
            Undo Last Action&nbsp;""")
        undoAction.setDisabled(True)
        undoAction.triggered.connect(self.undoLastAction)
        self.actions.append(undoAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'commit.svg'))
        commitAction = QAction(QIcon(icon), 'Commit', self.iface.mainWindow())
        commitAction.setToolTip("""
            <b>Commit</b>
            Save all changes to the database&nbsp;""")
        commitAction.setDisabled(True)
        commitAction.triggered.connect(self.commitChanges)
        self.actions.append(commitAction)

        icon = os.path.join(os.path.join(self.icons_folder, 'cancel_edit.png'))
        commitAction = QAction(QIcon(icon), 'Stop', self.iface.mainWindow())
        commitAction.setToolTip("""
            <b>Stop Editing</b>
            Finalize the editing session and save or discard the changes&nbsp;""")
        commitAction.setDisabled(True)
        commitAction.triggered.connect(self.closeSession)
        self.actions.append(commitAction)

        QgsProject.instance().readProject.connect(self.reset)
        QgsProject.instance().layersRemoved.connect(self.disableAllActions)
    #---


    def initGui(self):
        self.toolbar = self.iface.addToolBar("FFP Editing Toolbar")
        self.toolbar.setWindowIcon(QIcon(os.path.join(self.icons_folder, 'ffp.png')))
        self.toolbar.setFloatable(False)

        for action in self.actions:
            self.toolbar.addAction(action)

        self.actions[0].setEnabled(True)

        print('Ready...')
    #---


    def disableAllActions(self):
        if self.activeSession:
            self.pgSession.rollback()
            self.log('-- ***** SESSION ENDED ABNORMALY *****')
            del(self.pgSession)
            self.activeSession = False
        if len(QgsProject.instance().mapLayers().values()) == 0:
            for action in self.actions:
                action.setDisabled(True)
            self.actions[0].setEnabled(True)
    #---


    def reset(self):
        if self.activeSession:
            self.pgSession.rollback()
            self.log('-- ***** SESSION ENDED ABNORMALY *****')
            del(self.pgSession)
            self.activeSession = False
        for action in self.actions:
            action.setDisabled(True)
        self.actions[0].setEnabled(True)
        # self.actions[1].setEnabled(True)
    #---


    def startEditSession(self):
        if QgsProject.instance().readPath('./') == './':
            self.iface.messageBar().pushMessage('Message', 'Save the current project to disk before using this plugin...', level=Qgis.Info)
        elif len(QgsProviderRegistry.instance().providerMetadata('postgres').dbConnections()) == 0:
            self.iface.messageBar().pushMessage('Message', 'There are no PostGIS connections available...', level=Qgis.Info)
        else:
            connections = QgsProviderRegistry.instance().providerMetadata('postgres').dbConnections().keys().__str__()
            connections = connections.replace('dict_keys([','').replace('])','').replace("'",'')
            connectionList = connections.split(', ')

            self.connectionName, ok = QInputDialog.getItem(self.iface.mainWindow(), ' PostGIS Connections', 'Select the database connection to use: ', connectionList, 1)

            if ok:
                self.pgConnection = QgsProviderRegistry.instance().providerMetadata('postgres').findConnection(self.connectionName)
                self.params = dict(item.split("=") for item in self.pgConnection.uri().replace("'",'').split(' '))

                message, ready = self.checkLayers(True)

                if not ready:
                    self.iface.messageBar().pushMessage('Editing session cannot be initialized', message, level=Qgis.Info)
                else:
                    attDialogId = 'QgsAttributeTableDialog/' + self.pointsLayer.id()
                    dlgList = [el for el in QApplication.instance().allWidgets() if el.objectName() == attDialogId]
                    if len(dlgList) == 0:
                        dlgList = [self.iface.showAttributeTable(self.pointsLayer)]
                        dlgList[0].findChild(QAction,'mActionDockUndock').trigger()
                    for dlg in dlgList:
                        dlg.findChild(QAction,'mActionSelectedFilter').trigger()
                    self.iface.setActiveLayer(self.pointsLayer)

                #-----------
                    sqlCode = """
                        DROP TABLE IF EXISTS scratchpad;
                        CREATE TABLE scratchpad
                        (
                            col1 character varying,
                            col2 character varying,
                            col3 character varying,
                            geom geometry(PointZ,4326)
                        );
                    """
                    self.runSql(sqlCode)

                    resultsConn = QgsDataSourceUri()
                    resultsConn.setConnection(self.params['host'], self.params['port'], self.params['dbname'], self.params['user'], self.params['password'], 1)

                    resultsConn.setDataSource(self.schema, 'scratchpad', 'geom', None, 'tid')
                    self.resultsLayer = QgsVectorLayer(resultsConn.uri(True), "scratchpad", "postgres")
                #-----------


                    self.initLog()
                    self.runSql('TRUNCATE pto_ajuste;')
                    self.refresh(True)
                    self.pgSession = QgsTransaction.create(self.pgConnection.uri(), 'postgres')
                    self.pgSession.addLayer(self.resultsLayer)
                    self.pgSession.addLayer(self.scratchLayer)
                    self.pgSession.addLayer(self.pointsLayer)
                    self.pgSession.addLayer(self.spatialunitsLayer)
                    self.pgSession.begin()
                    self.pgSession.executeSql('SET search_path to %s, public' % (self.schema))
                    self.sessionIsDirty = False
                    self.undoMessages = []

                    self.threshold = self.thresholdValue
                    self.tolerance = self.toleranceValue
                    self.thresholdMsg = self.defaultThresholdMsg.replace('0000', str(self.threshold))
                    self.settingsWindow = settingsDialog()

                    for action in self.actions:
                        if action.text() not in ['Undo', 'Commit']:
                            action.setEnabled(True)
                    self.actions[0].setDisabled(True)
                    message = ('Editing session started ⟶ Using connection "%s"' % (self.connectionName))
                    self.iface.messageBar().pushMessage('Message:', message, level=Qgis.Success)
                    self.activeSession = True
                    QgsProject.instance().projectSaved.connect(self.endSession)
            else:
                self.connectionName = None
    #---


    def setSettings(self):
        self.settingsWindow.setDistanceThreshold(self.threshold)
        choice = self.settingsWindow.exec()
        if choice == 1:
            self.threshold = float(self.settingsWindow.distanceValue.text())
            self.thresholdMsg = self.defaultThresholdMsg.replace('0000', str(self.threshold))
            logCode = '--- *****\n'
            logCode += ('-- Distance threshold changed to: %s m\n' % (self.threshold))
            logCode += '--- *****\n\n'
            self.log(logCode)
    #---


    def checkLayers(self, setLayers = False):
        layerList = QgsProject.instance().mapLayers().values()
        ready = False
        message = ('The required tables are not available for connection "%s". Please include "puntos_predio", "pto_ajuste" & "spatialunit" to the project...' % (self.connectionName))

        databaseName = self.params['dbname']
        layerCheck = [False, False, False]
        if len(layerList) > 0:
            for layer in layerList:
                if layer.providerType() == 'postgres':
                    source = layer.dataProvider().dataSourceUri().split(' ')
                    databaseValue = None
                    tableName = None

                    for el in source:
                        if 'table' in el:
                            tableName = re.findall(r'"(.*?)"', el)[1]
                        if 'dbname' in el:
                            databaseValue = re.findall(r"'(.*?)'", el)[0]
                    if databaseValue == databaseName and tableName == 'pto_ajuste':
                        layerCheck[0] = True
                        if setLayers:
                            self.scratchLayer = layer
                    if databaseValue == databaseName and tableName == 'puntos_predio':
                        layerCheck[1] = True
                        if setLayers:
                            self.pointsLayer = layer
                    if databaseValue == databaseName and tableName == 'spatialunit':
                        layerCheck[2] = True
                        if setLayers:
                            self.spatialunitsLayer = layer

            if layerCheck.count(True) == 3:
                ready = True
                message = ''

        if setLayers and len(layerList) < 3:
            if not layerCheck[2]:
                if self.pgConnection.tableExists(self.schema,'spatialunit'):
                    conn2 = QgsDataSourceUri()
                    conn2.setConnection(self.params['host'], self.params['port'], self.params['dbname'], self.params['user'], self.params['password'], 1)
                    conn2.setDataSource(self.schema, 'spatialunit', 'geom', None, 'tid')
                    self.spatialunitsLayer = QgsVectorLayer(conn2.uri(True), "spatialunit", "postgres")
                    QgsProject.instance().addMapLayer(self.spatialunitsLayer)
                    layerCheck[2] = True
                    self.setStyle(2)
                    print("layer 'spatialunit' added...")
            if not layerCheck[1]:
                if self.pgConnection.tableExists(self.schema,'puntos_predio'):
                    conn1 = QgsDataSourceUri()
                    conn1.setConnection(self.params['host'], self.params['port'], self.params['dbname'], self.params['user'], self.params['password'], 1)
                    conn1.setDataSource(self.schema, 'puntos_predio', 'geom', None, 'tid')
                    self.pointsLayer = QgsVectorLayer(conn1.uri(True), "puntos_predio", "postgres")
                    QgsProject.instance().addMapLayer(self.pointsLayer)
                    layerCheck[1] = True
                    self.setStyle(1)
                    print("layer 'puntos_predio' added...")
            if not layerCheck[0]:
                if self.pgConnection.tableExists(self.schema,'pto_ajuste'):
                    conn0 = QgsDataSourceUri()
                    conn0.setConnection(self.params['host'], self.params['port'], self.params['dbname'], self.params['user'], self.params['password'], 1)
                    conn0.setDataSource(self.schema, 'pto_ajuste', 'geom', None, 'tid')
                    self.scratchLayer = QgsVectorLayer(conn0.uri(True), "pto_ajuste", "postgres")
                    QgsProject.instance().addMapLayer(self.scratchLayer)
                    layerCheck[0] = True
                    self.setStyle(0)
                    print("layer 'pto_ajuste' added...")

            if layerCheck.count(True) == 3:
                ready = True
                message = ''
                self.actions[1].setEnabled(True)

        if not ready and self.activeSession:
            self.pgSession.rollback()
            self.log('-- ***** SESSION ENDED ABNORMALY *****')
            del(self.pgSession)
            for action in self.actions:
                action.setDisabled(True)
            self.actions[0].setEnabled(True)
            self.actions[1].setEnabled(True)

        if not ready:
            self.iface.messageBar().pushMessage('Operation not possible', message, level=Qgis.Info)

        return message, ready
    #---


    def resetStyles(self):
        message, ok = self.checkLayers()
        if ok:
            self.setStyle(0)
            self.setStyle(1)
            self.setStyle(2)
            self.iface.mapCanvas().setMagnificationFactor(self.iface.mainWindow().physicalDpiX()/self.iface.mainWindow().logicalDpiX())
    #---


    def setStyle(self, layer):
        if layer == 0:
            sym = QgsMarkerSymbol.createSimple({'angle': '0', 'color': '219,11,25,229', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', \
                'name': 'diamond', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'outline_color': '161,13,26,255', \
                'outline_style': 'solid', 'outline_width': '0.2', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', 'outline_width_unit': 'MM', \
                'scale_method': 'diameter', 'size': '2.2', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', 'vertical_anchor_point': '1'})
            self.scratchLayer.renderer().setSymbol(sym)
            self.scratchLayer.triggerRepaint()
            self.iface.layerTreeView().refreshLayerSymbology(self.scratchLayer.id())
        if layer == 2:
            sym = QgsFillSymbol.createSimple({'color': '165,191,221,126', \
                'outline_color': '33,119,210,255', 'outline_style': 'solid', 'outline_width': '0.25'})
            self.spatialunitsLayer.renderer().setSymbol(sym)
            lbl_sett = QgsPalLayerSettings()
            lbl_sett.fieldName = 'objectid'
            lbl_format = QgsTextFormat()
            lbl_format.setSize(6)
            lbl_sett.setFormat(lbl_format)
            self.spatialunitsLayer.setLabelsEnabled(True)
            self.spatialunitsLayer.setLabeling(QgsVectorLayerSimpleLabeling(lbl_sett))
            self.spatialunitsLayer.triggerRepaint()
            self.iface.layerTreeView().refreshLayerSymbology(self.spatialunitsLayer.id())

        if layer == 1:
            sym1 = QgsMarkerSymbol.createSimple({'angle': '0', 'color': '247,128,30,255', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', \
                'name': 'circle', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', \
                'outline_color': '35,35,35,255', 'outline_style': 'solid', 'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', \
                'outline_width_unit': 'MM', 'scale_method': 'diameter', 'size': '1.8', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', \
                'vertical_anchor_point': '1'})
            sym2 = QgsMarkerSymbol.createSimple({'angle': '0', 'color': '0,224,90,204', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', \
                'name': 'circle', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', \
                'outline_color': '44,136,56,255', 'outline_style': 'solid', 'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', \
                'outline_width_unit': 'MM', 'scale_method': 'diameter', 'size': '1.8', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', \
                'vertical_anchor_point': '1'})
            sym3 = QgsMarkerSymbol.createSimple({'angle': '0', 'color': '149,149,149,255', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', \
                'name': 'circle', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', \
                'outline_color': '80,80,80,255', 'outline_style': 'solid', 'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', \
                'outline_width_unit': 'MM', 'scale_method': 'diameter', 'size': '1.5', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', \
                'vertical_anchor_point': '1'})

            cat1 = QgsRendererCategory('A', sym1, 'A')
            cat2 = QgsRendererCategory('T', sym2, 'T')
            cat3 = QgsRendererCategory('', sym3, '...')

            renderer = QgsCategorizedSymbolRenderer()
            renderer.addCategory(cat1)
            renderer.addCategory(cat2)
            renderer.addCategory(cat3)
            renderer.setClassAttribute('label')
            self.pointsLayer.setRenderer(renderer)

            lbl_sett = QgsPalLayerSettings()
            lbl_sett.fieldName = 'pto'
            lbl_format = QgsTextFormat()
            lbl_format.setSize(4)

            lbl_sett.setFormat(lbl_format)
            self.pointsLayer.setLabelsEnabled(True)
            self.pointsLayer.setLabeling(QgsVectorLayerSimpleLabeling(lbl_sett))

            self.pointsLayer.triggerRepaint()
    #---


    def initLog(self):
        print('\nFFP editing tools ready ⟶ Using connection "%s"' % (self.connectionName))
        print('------')

        ct = datetime.now()
        dateValue = '%s-%s-%s__%s-%s' % (ct.day, ct.strftime('%b'), ct.year, ct.strftime('%H'), ct.strftime('%M'))

        qs = QSettings()
        self.logFile = os.path.join(QgsProject.instance().readPath("./") + ('/ffp_plugin_%s.log' % (dateValue)))

        f = open(self.logFile, 'w')
        f.write('-----------------------------------')
        f.write('\n-- command log [%s]\n-----------------------------------\n' % (dateValue))
        f.write('-- host:     %s\n' % (qs.value('PostgreSQL/connections/' + self.connectionName + '/host')))
        f.write('-- port:     %s\n' % (qs.value('PostgreSQL/connections/' + self.connectionName + '/port')))
        f.write('-- database: %s\n' % (qs.value('PostgreSQL/connections/' + self.connectionName + '/database')))
        f.write('-----------------------------------\n')
        f.write('-- distance threshold:       %s m\n' % (self.thresholdValue))
        f.write('-- simplification tolerance: %s m\n' % (self.toleranceValue))
        f.write('-----------------------------------\n\n')
        f.close()
    #---


    def log(self, code):
        if code is not None:
            f = open(self.logFile, 'a')
            f.write(code + '\n\n')
            f.close()
    #---


    def onRefresh(self):
        self.refresh()
    #---


    def refresh(self, clearSelection = False):
        self.iface.mapCanvas().refreshAllLayers()
        self.clearCanvas()
        if clearSelection:
            attDialogId = 'QgsAttributeTableDialog/' + self.pointsLayer.id()
            dlgList = [el for el in QApplication.instance().allWidgets() if el.objectName() == attDialogId]
            if len(dlgList) > 0:
                for dlg in dlgList:
                    dlg.findChild(QAction,'mActionReload').trigger()
            self.iface.mainWindow().findChild(QAction,'mActionDeselectAll').trigger()
    #---


    def runSql(self, code):
        if type(code) == type(None):
            return ''
        else:
            self.pgConnection.executeSql('SET search_path TO %s, public;' % (self.schema))
            return self.pgConnection.executeSql(code)
    #---


    def clearScratch(self):
        self.pgSession.executeSql('TRUNCATE pto_ajuste;')
    #---


    def pgQuery(self, code, clearScratch = False, savePoint = False):
        if clearScratch:
            self.clearScratch()
        if savePoint:
            QgsProject.instance().setDirty(True)
        return self.pgSession.executeSql(code, savePoint, uuid4().hex)
    #---


    def undoLastAction(self):
        message, ok = self.checkLayers()
        if ok:
            msgWin = actionWindow(self.iface, ' Undo Last Action', True, 620)
            msgWin.setMainText('Do you want to revert the latest change?')
            msgWin.setDescriptionText(self.undoMessages[-1])
            msgWin.setWarningText('WARNING: This action cannot be reversed!')
            msgWin.adjustSize()
            choice = msgWin.exec()

            if choice == QMessageBox.Yes:
                self.pgSession.rollbackToSavepoint(self.pgSession.savePoints()[-1])
                undoMessage = self.undoMessages.pop().replace('will be', 'were').replace('<br/>','\n-- ')
                successMsg = 'Undo executed succesfully \n' + undoMessage
                print(successMsg + '\n---')
                self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                self.log('-- ******* UNDO ACTION EXECUTED *******\n-- ' + undoMessage)

                if len(self.pgSession.savePoints()) == 0:
                    for action in self.actions:
                        if action.text() in ['Undo', 'Commit']:
                            action.setDisabled(True)
                        elif action.text() == 'Merge Boundaries':
                            action.setEnabled(True)

                    self.sessionIsDirty = False

                self.clearScratch()
                self.refresh(True)
    #---


    def commitChanges(self):
        message, ok = self.checkLayers()
        if ok:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QIcon(os.path.join(self.icons_folder, 'ffp.png')))
            msgBox.setWindowTitle(' Commit Changes')
            msgBox.setText('Commit the changes to the database?    ')
            msgBox.setInformativeText('This action cannot be undone...   \n')
            msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
            msgBox.adjustSize()
            choice = msgBox.exec()

            if choice == QMessageBox.Yes:
                ok, message = self.pgSession.commit()
                for action in self.actions:
                    if action.text() in ['Undo', 'Commit']:
                        action.setDisabled(True)
                    elif action.text() == 'Merge Boundaries':
                        action.setEnabled(True)

                successMsg = 'All changes were committed succesfully'
                print(successMsg + '\n---')
                self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                self.log('-- ******* ' + successMsg.upper() + ' *******')

                del(self.pgSession)
                self.pgSession = QgsTransaction.create(self.pgConnection.uri(), 'postgres')
                self.pgSession.addLayer(self.resultsLayer)
                self.pgSession.addLayer(self.pointsLayer)
                self.pgSession.addLayer(self.scratchLayer)
                self.pgSession.addLayer(self.spatialunitsLayer)
                self.pgSession.begin()
                self.pgSession.executeSql('SET search_path to %s, public' % (self.schema))

                self.sessionIsDirty = False
                self.undoMessages = []
                QgsProject.instance().setDirty(False)
    #---


    def closeSession(self):
        message, ok = self.checkLayers()
        if ok:
            if self.sessionIsDirty:
                msgBox = QMessageBox()
                msgBox.setWindowIcon(QIcon(os.path.join(self.icons_folder, 'ffp.png')))
                msgBox.setWindowTitle(' End Current Edit Session')
                msgBox.setText('There are unsaved changes...    ')
                msgBox.setInformativeText('Do you want to SAVE the changes before ending the session?   \n')
                msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes | QMessageBox.No)
                msgBox.adjustSize()
                choice = msgBox.exec()
            else:
                choice = QMessageBox.No

            if choice == QMessageBox.No:
                self.pgSession.rollback()
                if self.sessionIsDirty:
                    message = 'Editing changes were discarded...'
                else:
                    message = 'There were no changes...'
            elif choice == QMessageBox.Yes:
                self.pgSession.commit()
                message = 'All changes have been saved...'

            if choice == QMessageBox.No or choice == QMessageBox.Yes:
                del(self.pgSession)
                for action in self.actions:
                    action.setDisabled(True)
                self.actions[0].setEnabled(True)
                self.actions[1].setEnabled(True)
                self.iface.messageBar().pushMessage('Editing session ended', message, level=Qgis.Info)
                print(message + '\n---')
                self.log('-- ***** SESSION ENDED - ' + message.upper() + ' *****')
                self.dropScratchpad()
                self.activeSession = False
                QgsProject.instance().setDirty(False)
    #---


    def orderPointSets(self, sets):
        setList = zip(sets['pos'], sets['ids'], sets['lbl'])
        sets['pos'], sets['ids'], sets['lbl'] = zip(*sorted(setList))
        points = {'ids':[], 'pos':[], 'lbl':[]}
        idx = 0
        for x in range(len(sets['ids'])):
            if len(points['ids']) == 0:
                points['ids'].append(sets['ids'][x])
                points['pos'].append(sets['pos'][x])
                points['lbl'].append(sets['lbl'][x])
            else:
                if sets['pos'][x] == points['pos'][-1] + 1:
                    points['ids'].append(sets['ids'][x])
                    points['pos'].append(sets['pos'][x])
                    points['lbl'].append(sets['lbl'][x])
                else:
                    points['ids'].insert(idx, sets['ids'][x])
                    points['pos'].insert(idx, sets['pos'][x])
                    points['lbl'].insert(idx, sets['lbl'][x])
                    idx += 1

        return points
    #---


    def mergeBoundaries(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count < 5:
                message = 'An incorrect number of features is currently are selected  from layer "puntos_predio"... '
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                spatialunitIdCounts = []
                for feature in features:
                    spatialunitIdCounts.append(feature['id_pol'])

                spatialunitIdCounts = dict([[x, spatialunitIdCounts.count(x)] for x in set(spatialunitIdCounts)])
                pointSets = {}
                droppedPoints = []
                anchors = 0
                vertices = 0
                for item in spatialunitIdCounts.items():
                    if item[1] > 1:
                        pointSets[item[0]] = {'ids':[], 'pos':[], 'lbl':[]}

                for feature in features:
                    if spatialunitIdCounts[feature['id_pol']] == 1:
                        droppedPoints.append([feature['pto'], feature['id_pol']])
                    else:
                        pointSets[feature['id_pol']]['ids'].append(feature['pto'])
                        pointSets[feature['id_pol']]['pos'].append(feature['num_pto'])
                        pointSets[feature['id_pol']]['lbl'].append(feature['label'])
                        if feature['label'] == 'A':
                            anchors += 1
                        else:
                            vertices += 1

                spatialunitIds = list(pointSets.keys())
                correctPoints = True
                for key in pointSets:
                    pointSets[key] = self.orderPointSets(pointSets[key])
                    if pointSets[key]['lbl'][0] != 'A' or pointSets[key]['lbl'][-1] != 'A':
                        correctPoints = False


                if anchors > 4 or vertices < 1 or not correctPoints:
                    message = 'The selected points do not correspond to "Vertex" & "Anchor" points of a shared boundary betewwn two spatialunits...'
                    self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
                else:
                    key1 = spatialunitIds[0]
                    key2 = spatialunitIds[1]

                    srcPoint = ([x for x in features if x.attribute('pto') == pointSets[key1]['ids'][0]])[0].geometry().asPoint()
                    trgPoint1 = ([x for x in features if x.attribute('pto') == pointSets[key2]['ids'][0]])[0].geometry().asPoint()
                    trgPoint2 = ([x for x in features if x.attribute('pto') == pointSets[key2]['ids'][-1]])[0].geometry().asPoint()
                    dist1 = self.calculator.measureLine(srcPoint, trgPoint1)
                    dist2 = self.calculator.measureLine(srcPoint, trgPoint2)
                    end1 = False
                    if dist1 == 0 or dist2 == 0:
                        end1 = True

                    srcPoint = ([x for x in features if x.attribute('pto') == pointSets[key1]['ids'][-1]])[0].geometry().asPoint()
                    dist1 = self.calculator.measureLine(srcPoint, trgPoint1)
                    dist2 = self.calculator.measureLine(srcPoint, trgPoint2)
                    end2 = False
                    if dist1 == 0 or dist2 == 0:
                        end2 = True

                    if end1 and end2:
                        self.mergeDetails = '<p><b>Points ignored:</b><br/>%s</p>' % ', '.join((str(x)).replace(',',' :') for x in droppedPoints)
                        self.mergeDetails += "<p><b>Boundaries to be merged:</b>"
                        self.mergeUndoDetails = ''
                        for key in pointSets:
                            self.mergeDetails += '<br/>[%s] : %s' % (key, pointSets[key]['ids'])
                            self.mergeUndoDetails += '<br/>[%s] : %s' % (key, pointSets[key]['ids'])
                        self.mergeDetails += "</p>"

                        sqlCode = ("""
                            WITH l1 AS (
                                SELECT row_number() over(ORDER BY num_pto), * FROM puntos_predio
                                WHERE id_pol = %s AND pto in (%s)
                                ORDER BY num_pto > %s DESC, 1
                            ), p1 AS (
                                SELECT id_pol, pto AS pto1, LEAD(pto, 1) OVER() as pto2,
                                    geom AS vertex1, LEAD(geom ,1) OVER() AS vertex2
                                FROM l1
                            ), g1 AS (
                                SELECT id_pol AS idx_pol, ARRAY[pto1, pto2] AS idx,
                                    ST_force2D(ST_Makeline(vertex1, vertex2)) as segment
                                FROM p1
                                WHERE pto2 IS NOT NULL
                            ), l2 AS (
                                SELECT row_number() over(ORDER BY num_pto), * FROM puntos_predio
                                WHERE id_pol = %s AND pto IN (%s)
                                ORDER BY num_pto > %s DESC, 1
                            ), p2 AS (
                                SELECT id_pol, pto AS pto1, LEAD(pto, 1) OVER() as pto2,
                                    geom AS vertex1, LEAD(geom ,1) OVER() AS vertex2
                                FROM l2
                            ), g2 AS (
                                SELECT id_pol AS idx_pol, ARRAY[pto1, pto2] AS idx,
                                    ST_force2D(ST_Makeline(vertex1, vertex2)) as segment
                                FROM p2
                                WHERE pto2 IS NOT NULL
                            )
                            SELECT row_number() over() as oid, pto, idx, idx_pol, point_1, point_2, dist, point_geom, seg_geom
                            FROM (
                                (SELECT * FROM
                                    (SELECT
                                        row_number() over(partition by l1.pto ORDER BY ST_Length(ST_ShortestLine(g2.segment, l1.geom))) as rowidx,
                                        l1.pto, g2.idx, g2.idx_pol,
                                        ST_AsText(ST_PointN(ST_ShortestLine(g2.segment, l1.geom),1)) AS point_1,
                                        ST_AsText(ST_PointN(ST_ShortestLine(g2.segment, l1.geom),2)) AS point_2,
                                        ST_PointN(ST_ShortestLine(g2.segment, l1.geom),1) AS point_geom,
                                        ST_Length(ST_ShortestLine(g2.segment, l1.geom)) as dist,
                                        ST_ShortestLine(g2.segment, l1.geom) AS seg_geom
                                    FROM l1, g2
                                    WHERE l1.label <> 'A') as foo
                                WHERE rowidx = 1
                                ORDER BY 1)
                                UNION
                                (SELECT * FROM
                                    (SELECT
                                        row_number() over(partition by l2.pto ORDER BY ST_Length(ST_ShortestLine(g1.segment, l2.geom))) as rowidx,
                                        l2.pto, g1.idx, g1.idx_pol,
                                        ST_AsText(ST_PointN(ST_ShortestLine(g1.segment, l2.geom),1)) AS point_1,
                                        ST_AsText(ST_PointN(ST_ShortestLine(g1.segment, l2.geom),2)) AS point_2,
                                        ST_PointN(ST_ShortestLine(g1.segment, l2.geom),1) AS point_geom,
                                        ST_Length(ST_ShortestLine(g1.segment, l2.geom)) as dist,
                                        ST_ShortestLine(g1.segment, l2.geom) AS seg_geom
                                    FROM l2, g1
                                    WHERE l2.label <> 'A') as foo
                                WHERE rowidx = 1
                                ORDER BY 1)
                            ) AS foo
                        """ % (
                            spatialunitIds[0],
                            ', '.join(str(f) for f in pointSets[spatialunitIds[0]]['ids']),
                            pointSets[spatialunitIds[0]]['pos'][0] - 1,
                            spatialunitIds[1],
                            ', '.join(str(f) for f in pointSets[spatialunitIds[1]]['ids']),
                            pointSets[spatialunitIds[1]]['pos'][0] - 1
                        ))

                        self.mergeRecords = self.runSql(sqlCode)
                        self.clearScratch()

                        self.mergeDetails += '<p><b>Distances:</b>'
                        insideThreshold = True
                        for item in self.mergeRecords:
                            if item[6] > 0.0:
                                coords = re.search(r'\((.*)\)', item[4]).group(1)
                                x1, y1 = coords.split(' ')
                                coords = re.search(r'\((.*)\)', item[5]).group(1)
                                x2, y2 = coords.split(' ')
                                polyline = QgsRubberBand(self.iface.mapCanvas(), False)
                                points = [QgsPoint(float(x1), float(y1)), QgsPoint(float(x2), float(y2))]
                                polyline.setToGeometry(QgsGeometry.fromPolyline(points), None)
                                polyline.setColor(QColor(255, 0, 0))
                                polyline.setWidth(2)
                                self.canvasLines.append(polyline)
                                sqlCode = ("""
                                    INSERT INTO pto_ajuste
                                    VALUES (%s, ST_Force4D('%s'::geometry));
                                """ % (item[0], item[7]))
                                self.pgQuery(sqlCode, False, False)

                                point1 = ([x for x in features if x.attribute('pto') == item[1]])[0].geometry().asPoint()
                                point2 = ([x for x in self.scratchLayer.getFeatures() if x.attribute('id') == item[0]])[0].geometry().asPoint()
                                distance = self.calculator.measureLine(point1, point2)
                                self.mergeDetails += '<br/> %s → %s : %s m' % (item[1], item[3], '{:.2f}'.format(distance))
                                if distance > self.threshold:
                                    insideThreshold = False

                        if insideThreshold:
                            self.mergeDetails += '</p>'
                            self.iface.mapCanvas().refreshAllLayers()

                            self.toolbar.setDisabled(True)
                            msgWin = mergePanel(self, self.mergeDetails, 700)
                            msgWin.show()
                        else:
                            msgBox = actionWindow(self.iface, 'Operation not possible', False)
                            msgBox.setMainText("Some distnaces are outside the threshold of %s m" % (self.threshold))
                            msgBox.setDescriptionText(self.mergeDetails)
                            msgBox.adjustSize()
                            msgBox.exec()
                            self.clearCanvas()
                            self.clearScratch()
                            self.refresh()

                    else:
                        message = 'The "Anchor" points at the end of the boundaries are not in the same location...'
                        self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
    #---


    def performMerge(self):
        self.clearScratch()
        addSavePoint = True
        fieldIdx = self.pointsLayer.fields().indexFromName('pto')
        logCode = 'BEGIN;\n\n'
        for item in self.mergeRecords:
            if item[6] > 0.0:
                sqlCode = ("""SELECT ffp_proyectar_punto(%s, %s);""" %(item[1], item[3]))
                self.pgQuery(sqlCode, True, addSavePoint)
                logCode += '  ' + sqlCode + '\n'
                addSavePoint = False

                idList = item[2].replace('{','').replace('}','')
                pointIds = idList.split(',')
                sqlCode = """SELECT ffp_nuevo_punto_proyectado(%s);""" % (idList)
                self.pgQuery(sqlCode, False, False)
                logCode += '  ' + sqlCode + '\n'

                newId = self.pointsLayer.maximumValue(fieldIdx)
                successMsg = ('Vertex [%s] was added to spatialunit %s, between points %s & %s'
                    % (newId, item[3], pointIds[0], pointIds[1]))
                logCode += '    -- ' + successMsg + '\n'

                sqlCode = """SELECT ffp_ver_pto_medio(%s, %s, true);""" % (item[1], newId)
                self.pgQuery(sqlCode, True, False)
                logCode += '  ' + sqlCode + '\n'
                logCode += '    -- Points %s, %s were joined\n\n' % (item[1], newId)

        logCode += 'END;\n\n'
        detailsCode = '-- ' + self.mergeDetails.replace('<br/>','\n-- ').replace('</p>','\n-- ').replace(' to be ', ' ')
        exp = re.compile(r'<.*?>')
        logCode += exp.sub('', detailsCode) + 'Boundaries merged succesfully'
        self.undoMessages.append('The following boundaries will be disconected:' + self.mergeUndoDetails)
        self.clearCanvas()
        self.onNewSavePoint()
        self.toolbar.setEnabled(True)
        self.log(logCode)
        print('Boundaries succesfully connected' + self.mergeUndoDetails.replace('<br/>','\n') + '\n---')
    #---


    def cancelMerge(self):
        print('cancel merge')
        self.clearCanvas()
        self.clearScratch()
        self.iface.mapCanvas().refreshAllLayers()
        self.toolbar.setEnabled(True)
    #---


    def simplifyBoundaries(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.spatialunitsLayer.selectedFeatures()
            count = len(features)

            if count != 1:
                message = 'Select (only) one spatialunit there are %s currently seleected... ' % count
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                targetPolygon =     features[0]['objectid']
                toleranceWindow = toleranceDialog(targetPolygon)
                toleranceWindow.setTolerance(self.tolerance)
                choice = toleranceWindow.exec()
                if choice == 1:
                    if self.tolerance != float(toleranceWindow.toleranceValue.text()):
                        self.tolerance = float(toleranceWindow.toleranceValue.text())
                        logCode = '--- *****\n'
                        logCode += ('-- Simplification tolerance set to: %s m\n' % (self.tolerance))
                        logCode += '--- *****\n\n'
                        self.log(logCode)

                    polygon = QgsRubberBand(self.iface.mapCanvas(), False)
                    polygon.setToGeometry(features[0].geometry(), None)
                    polygon.setFillColor(QColor(255, 0, 255, 10))
                    polygon.setStrokeColor(QColor(255, 0, 0))
                    polygon.setWidth(3)
                    self.canvasLines.append(polygon)

                    tab = '                      '
                    sqlCode = ("""
                        UPDATE spatialunit SET geom = ST_Multi(ST_SimplifyPreserveTopology(geom,%s)) WHERE objectid = %s;
                        DELETE FROM puntos_predio WHERE id_pol = %s;
                        SELECT ffp_adiciona_puntos_predio(%s);
                        UPDATE puntos_predio SET label = 'T' WHERE id_pol = %s;
                    """ % ('{:.7f}'.format(round(self.tolerance/111140,7)), targetPolygon, targetPolygon, targetPolygon, targetPolygon)).replace(tab,'')

                    ok, err = self.pgQuery(sqlCode, False, True)
                    if ok:
                        self.iface.mapCanvas().refreshAllLayers()
                        self.toolbar.setDisabled(True)

                        msgWin = simplifyMsgWindow(self, sqlCode, targetPolygon)
                        msgWin.show()
    #---


    def endSimplify(self, sqlCode, targetPolygon):
        logCode = 'BEGIN;\n' + sqlCode + '\nEND;'
        successMsg = ('Spatialunit %s was succesfully simplified' % (targetPolygon))
        logCode += '\n-- ' + successMsg
        self.log(logCode)
        self.undoMessages.append('Spatialunit %s will be restored to its original geometry' % (targetPolygon))

        self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
        print(successMsg + '\n---')

        self.clearCanvas()
        self.toolbar.setEnabled(True)
        self.onNewSavePoint()
    #---


    def clearCanvas(self):
        for line in self.canvasLines:
        	self.iface.mapCanvas().scene().removeItem(line)
    #---


    def moveToMidpoint(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count < 2 or count > 3:
                message = 'Select two or up to three features from layer "puntos_predio"...'
                self.iface.messageBar().pushMessage('Operation not possible', message, level=Qgis.Info)
            else:
                pointIds = []
                spatialunitIds = []
                details = ''
                for feature in features:
                    pointIds.append(feature['pto'])
                    if feature['id_pol'] not in spatialunitIds:
                        spatialunitIds.append(feature['id_pol'])
                    accuracy = '{:.2f}'.format(feature['accuracy']) if (str(feature['accuracy'])).isnumeric() == 'NULL' else '---'
                    details += ('%s %s: %s m\n' %
                        (feature['label'] == 'A' and 'Anchor' or 'Vertex', feature['pto'], accuracy))

                pointIds.sort()
                pointList = ', '.join(str(f) for f in pointIds)
                anchors = details.count('Anchor')

                if anchors == 0 or anchors == count:
                    if len(pointIds) == len(spatialunitIds):
                        insideThreshold = True
                        distances = ''
                        for i in range(count - 1):
                            for j in range(i + 1, count):
                                distance = self.calculator.measureLine(features[i].geometry().asPoint(), features[j].geometry().asPoint())
                                distances += ("""\n%s ←→ %s : %s m""" %
                                    (features[i]['pto'], features[j]['pto'], '{:.2f}'.format(distance)))
                                if distance > self.threshold:
                                    insideThreshold = False

                        if insideThreshold:
                            result = self.pgQuery("""SELECT ffp_ver_pto_medio(%s);""" % (pointList), True)
                            self.iface.mapCanvas().refreshAllLayers()

                            msgWin = actionWindow(self.iface, ' Move to Mid-Point')
                            msgWin.setMainText('Do you want to move points: %s to the new location as shown in the canvas?' % (pointList))
                            msgWin.setDescriptionText(details + '  ---  ' + distances)
                            msgWin.adjustSize()
                            choice = msgWin.exec()

                            if choice == QMessageBox.Yes:
                                sqlCode = """SELECT ffp_ver_pto_medio(%s, true);""" % (pointList)
                                ok, err = self.pgQuery(sqlCode, False, True)
                                if ok:
                                    self.undoMessages.append('Points %s will be restored to their previous locations' %(pointList))
                                    successMsg = 'Points %s have been modified!!!' % (pointList)
                                    logCode = sqlCode + '\n-- ' + successMsg + distances.replace('\n', '\n-- ')
                                    self.log(logCode)
                                    self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                                    print(successMsg + '\n---')

                                    self.onNewSavePoint()
                            else:
                                self.clearScratch()
                                self.refresh(False)

                        else:
                            msgBox = actionWindow(self.iface, ' Operation not Possible', False)
                            msgBox.setMainText(self.thresholdMsg)
                            msgBox.setDescriptionText(distances[1:])
                            msgBox.adjustSize()
                            msgBox.exec()
                    else:
                        message = 'The selected features do not belong to different spatialunits...'
                        self.iface.messageBar().pushMessage('Operation not possible', message, level=Qgis.Info)
                else:
                    message = 'The selected features are not of the same type (Anchor/Vertex)...'
                    self.iface.messageBar().pushMessage('Operation not possible', message, level=Qgis.Info)
    #---


    def setToAnchor(self):
        self.changePointType('Anchor')
    #---


    def setToVertex(self):
        self.changePointType('Vertex')
    #---


    def changePointType(self, pointType):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count == 0:
                message = 'Please select at least one feature from layer "puntos_predio"... '
                self.iface.messageBar().pushMessage('Operation not possible', message, level=Qgis.Info)
            else:
                pointIds = []
                for feature in features:
                    pointIds.append(feature['pto'])
                pointIds.sort()
                pointList = ', '.join(str(f) for f in pointIds)

                msgWin = actionWindow(self.iface, ' Set Point(s) to %s' % (pointType))
                msgWin.setMainText('Do you want to change point(s)\n%s to "%s"?' % (pointList, pointType))
                msgWin.adjustSize()
                choice = msgWin.exec()

                if choice == QMessageBox.Yes:
                    sqlCode = """
                        UPDATE puntos_predio
                        SET label = '%s'
                        WHERE pto IN (%s);""" % (pointType == 'Anchor' and 'A' or 'T', pointList)
                    ok, err = self.pgQuery(sqlCode, False, True)
                    if ok:
                        prevType = pointType == 'Anchor' and 'Vertex' or 'Anchor'
                        self.undoMessages.append('Point(s) %s will be restored to the original type (%s)' %(pointList, prevType))
                        logCode = re.sub(r"\s{2,}", '', sqlCode.replace('\n', '@'))[1:]
                        logCode = logCode.replace('@','\n')
                        self.log(logCode)
                        successMsg = 'Point(s) %s were set to %s' % (pointList, pointType)
                        self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                        print(successMsg + '\n---')

                        self.onNewSavePoint()
    #---


    def moveOneToTwo(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count != 2:
                message = 'Please select exactly two features from layer "puntos_predio"... '
                self.iface.messageBar().pushMessage('Operation not possible', message, level=Qgis.Info)
            else:
                pointIds = []
                spatialunitIds = []
                for feature in features:
                    pointIds.append(feature['pto'])
                    if feature['id_pol'] not in spatialunitIds:
                        spatialunitIds.append(feature['id_pol'])

                distance = self.calculator.measureLine(features[0].geometry().asPoint(), features[1].geometry().asPoint())
                if distance > self.threshold:
                    msgBox = actionWindow(self.iface, ' Operation not Possible', False)
                    msgBox.setMainText(self.thresholdMsg)
                    msgBox.setDescriptionText('%s ←→ %s : %s m' % (pointIds[0], pointIds[1], '{:.1f}'.format(distance)))
                    msgBox.adjustSize()
                    msgBox.exec()
                else:
                    msgWin = moveOneToTwoWindow()
                    msgWin.setOptions(pointIds, distance, self.iface, self.pgSession)
                    choice = msgWin.exec()

                    if choice != 0:
                        message = 'Point 001 has been moved to the location of point 002'

                        if choice == 1:
                            sqlCode = """SELECT ffp_mueva_1_a_2(%s, %s, true);""" % (pointIds[0], pointIds[1])
                            message = message.replace('001', str(pointIds[0]))
                            message = message.replace('002', str(pointIds[1]))
                            logCode = '[ %s - %s ] : %s m' % (pointIds[0], pointIds[1], '{:.1f}'.format(distance))
                        elif choice == 2:
                            sqlCode = """SELECT ffp_mueva_1_a_2(%s, %s, true);""" % (pointIds[1], pointIds[0])
                            message = message.replace('001', str(pointIds[1]))
                            message = message.replace('002', str(pointIds[0]))
                            logCode = '[ %s - %s ] : %s m' % (pointIds[1], pointIds[0], '{:.1f}'.format(distance))

                        ok, err = self.pgQuery(sqlCode, True, True)
                        if ok:
                            self.undoMessages.append('Point %s will be returned to its original location' %
                                (choice == 1 and pointIds[0] or pointIds[1]))
                            self.log(sqlCode + '\n-- ' + logCode)
                            self.iface.messageBar().pushMessage('Message:', message, level=Qgis.Success)
                            print(message + '\n---')

                            self.onNewSavePoint()
    #---


    def projectVertex(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            countOK = True
            if count > 1:
                pto = features[0].geometry().asPoint()
                for feat in features:
                    if not QgsGeometry.fromPointXY(feat.geometry().asPoint()).equals(QgsGeometry.fromPointXY(pto)):
                        countOK = False
                        break
            if not countOK:
                message = 'Select only one point from the layer "puntos_predio", there are currently %s seleected... ' % count
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                srcPolygon = features[0]['id_pol']
                pointId = features[0]['pto']
                srcPointGeom = features[0].geometry().asPoint()

                sqlCode = ("""
                    TRUNCATE scratchpad;
                    INSERT INTO scratchpad (col1, col2)
                        SELECT a.objectid, ST_Distance(a.geom, ST_ClosestPoint(b.geom, a.geom))
                        FROM spatialunit a, puntos_predio b
                        WHERE b.pto = %s AND a.objectid <> %s
                        ORDER BY 2
                        LIMIT 2;
                """ % (pointId, srcPolygon))

                ok, err = self.pgQuery(sqlCode)
                if ok:
                    polyList = []
                    for record in self.resultsLayer.getFeatures():
                        polyList.append(record.attributes()[0])

                    targetPolygon, ok = QInputDialog.getItem(self.iface.mainWindow(), ' Select One', 'Select the target spatialunit: ', polyList, 0)

                    if ok:
                        sqlCode = ("""SELECT ffp_proyectar_punto(%s, %s);""" %(pointId, targetPolygon))
                        self.pgQuery(sqlCode, True, False)

                        scratchPoint = list(self.scratchLayer.getFeatures())[0].geometry().asPoint()
                        distance = self.calculator.measureLine(srcPointGeom, scratchPoint)

                        if distance > self.threshold:
                            insideThreshold = False
                            message = 'The projection distance (%s m) is outside the allowed threshold.' % '{:.2f}'.format(distance)
                        else:
                            insideThreshold = True

                        if insideThreshold:
                            self.iface.mapCanvas().refreshAllLayers()

                            msgWin = actionWindow(self.iface, ' Split Segment')
                            msgWin.setMainText('Do you want to add the new vertex to spatialunit %s?' % (targetPolygon))
                            msgWin.adjustSize()
                            choice = msgWin.exec()

                            if choice == QMessageBox.Yes:
                                scratchPoint = 'SRID=4326;' + list(self.scratchLayer.getFeatures())[0].geometry().asWkt()

                                sql_code = ("""
                                    TRUNCATE scratchpad;
                                    INSERT INTO scratchpad (col1, col2)
                                        WITH s AS(
                                            SELECT (st_DumpSegments(geom)).geom
                                            FROM spatialunit WHERE objectid = %s
                                        ),
                                        t AS (
                                            SELECT ST_PointN(s.geom,1) AS p1, ST_PointN(s.geom,2) AS p2, ST_Distance(s.geom, ST_GeomFromEWKT('%s'))
                                            FROM s
                                            ORDER BY 3
                                            limit 1
                                        )
                                        SELECT l.* FROM (
                                            SELECT pto, num_pto
                                            FROM puntos_predio AS pp, t
                                            WHERE ST_Equals(t.p1, pp.geom) and id_pol = %s
                                            UNION
                                            SELECT pto, num_pto
                                            FROM puntos_predio AS pp, t
                                            WHERE ST_Equals(t.p2, pp.geom) and id_pol = %s
                                        ) AS l ORDER BY 2;
                                """ % (targetPolygon, scratchPoint, targetPolygon, targetPolygon))

                                ok, err = self.pgQuery(sql_code)
                                if ok:
                                    records = list(self.resultsLayer.getFeatures())
                                    print(records[0].attributes())
                                    print(records[1].attributes())
                                    if abs(int(records[0].attributes()[1]) - int(records[1].attributes()[1])) == 1:
                                        pointList = '%s, %s' % (records[0].attributes()[0], records[1].attributes()[0])
                                    else:
                                        pointList = '%s, %s' % (records[1].attributes()[0], records[0].attributes()[0])

                                    logCode = 'BEGIN;\n  ' + sqlCode + '\n'
                                    sqlCode = """SELECT ffp_nuevo_punto_proyectado(%s);""" % (pointList)
                                    ok, err = self.pgQuery(sqlCode, False, True)
                                    if ok:
                                        logCode += '  ' + sqlCode + '\nEND;'
                                        idx = self.pointsLayer.fields().indexFromName('pto')
                                        newId = self.pointsLayer.maximumValue(idx)
                                        successMsg = ('Vertex [%s] was added to spatialunit %s, between points %s'
                                            % (newId, targetPolygon, pointList.replace(', ', ' & ')))
                                        logCode += '\n-- ' + successMsg
                                        self.log(logCode)
                                        self.undoMessages.append('Vertex %s will be removed from spatialunit %s' % (newId, targetPolygon))

                                        self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                                        print(successMsg + '\n---')

                                        self.onNewSavePoint()
                                else:
                                    print('Query error:')
                                    print(err)

                            else:
                                self.clearScratch()
                                self.iface.mapCanvas().refreshAllLayers()

                        else:
                            msgBox = actionWindow(self.iface, ' Operation not Possible', False)
                            msgBox.setMainText(message)
                            msgBox.adjustSize()
                            msgBox.exec()
                            self.clearScratch()
                            self.iface.mapCanvas().refreshAllLayers()
                else:
                    print('Query Error:')
                    print('error:')
    #---


    def projectPoint(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count != 3:
                message = 'Exactly three features from two spatialunits must be selected from layer "puntos_predio"... '
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                spatialunitIds = []
                for feature in features:
                    if feature['id_pol'] not in spatialunitIds:
                        spatialunitIds.append(feature['id_pol'])
                    else:
                        target = feature['id_pol']

                if len(spatialunitIds) == 3:
                    message = 'The features belong to three different spatialunits...'
                    self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
                elif len(spatialunitIds) != 2:
                    message = 'Selected features must belong to two different spatialunts...'
                    self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
                else:
                    pointIds = []
                    for feature in features:
                        if feature['id_pol'] != target:
                            srcPoint = feature['pto']
                            srcPointGeom = feature.geometry().asPoint()
                        else:
                            if len(pointIds) == 0:
                                point1 = feature.geometry().asPoint()
                            else:
                                point2 = feature.geometry().asPoint()
                            pointIds.append([feature['pto'], feature['num_pto']])

                    targetPoints = self.pointsLayer.getFeatures('"id_pol"=%s' % (target))
                    vertexCount = len([point for point in targetPoints])

                    print(vertexCount)
                    print(pointIds)
                    delta = abs(pointIds[0][1] - pointIds[1][1])
                    pointSequence = True
                    if delta == vertexCount - 1:
                        desc = True
                    elif delta == 1:
                        desc = False
                    else:
                        pointSequence = False

                    if pointSequence:
                        pointIds.sort(key=lambda x: x[1], reverse = desc)
                        idList = '%s, %s' % (pointIds[0][0], pointIds[1][0])

                        sqlCode = ("""SELECT ffp_proyectar_punto(%s, %s);""" %(srcPoint, target))
                        self.pgQuery(sqlCode, True, False)

                        scratchPoint = list(self.scratchLayer.getFeatures())[0].geometry().asPoint()
                        distance = self.calculator.measureLine(srcPointGeom, scratchPoint)

                        if distance > self.threshold:
                            insideThreshold = False
                            extraText = ' Or the projection distance (%s m) is outside the allowed threshold.' % '{:.2f}'.format(distance)
                        else:
                            insideThreshold = True
                            extraText = ''

                        if insideThreshold:
                            baseDistance = self.calculator.measureLine(point1, point2)
                            refDistance1 = self.calculator.measureLine(point1, srcPointGeom)
                            refDistance2 = self.calculator.measureLine(point2, srcPointGeom)

                            if refDistance1 >= baseDistance or refDistance2 >= baseDistance:
                                insideThreshold = False

                        if insideThreshold:
                            self.iface.mapCanvas().refreshAllLayers()
                            msgWin = actionWindow(self.iface, ' Split Segment')
                            msgWin.setMainText('Do you want to add the new vertex to spatialunit %s?' % (target))
                            msgWin.adjustSize()
                            choice = msgWin.exec()

                            if choice == QMessageBox.Yes:
                                logCode = 'BEGIN;\n  ' + sqlCode + '\n'
                                sqlCode = """SELECT ffp_nuevo_punto_proyectado(%s);""" % (idList)
                                ok, err = self.pgQuery(sqlCode, False, True)
                                if ok:
                                    logCode += '  ' + sqlCode + '\nEND;'

                                    idx = self.pointsLayer.fields().indexFromName('pto')
                                    newId = self.pointsLayer.maximumValue(idx)
                                    successMsg = ('Vertex [%s] was added to spatialunit %s, between points %s & %s'
                                        % (newId, target, pointIds[0][0], pointIds[1][0]))
                                    logCode += '\n-- ' + successMsg
                                    self.log(logCode)
                                    self.undoMessages.append('Vertex %s will be removed from spatialunit %s' % (newId, target))

                                    self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                                    print(successMsg + '\n---')

                                    self.onNewSavePoint()
                            else:
                                self.clearScratch()
                                self.iface.mapCanvas().refreshAllLayers()
                        else:
                            msgBox = actionWindow(self.iface, ' Operation not Possible', False)
                            msgBox.setMainText('The spatial configuration of the selected points does not allow point projection.' + extraText)
                            msgBox.adjustSize()
                            msgBox.exec()
                            self.clearScratch()
                            self.iface.mapCanvas().refreshAllLayers()

                    else:
                        message = 'The selected source points %s are not sequencial...' % ([pointIds[0][0], pointIds[1][0]])
                        self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
    #---


    def addMidpoint(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count != 2:
                message = 'Please select exactly two feature from layer "puntos_predio"... '
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                pointIds = []
                spatialunitIds = []
                for feature in features:
                    pointIds.append([feature['pto'], feature['num_pto']])
                    if feature['id_pol'] not in spatialunitIds:
                        spatialunitIds.append(feature['id_pol'])

                if len(spatialunitIds) == 1:
                    targetPoints = self.pointsLayer.getFeatures('"id_pol"=%s' % (spatialunitIds[0]))
                    vertexCount = len([point for point in targetPoints])

                    delta = abs(pointIds[0][1] - pointIds[1][1])
                    pointSequence = True
                    if delta == vertexCount - 1:
                        desc = True
                    elif delta == 1:
                        desc = False
                    else:
                        pointSequence = False

                    if pointSequence:
                        pointIds.sort(key=lambda x: x[1], reverse = desc)
                        idList = '%s, %s' % (pointIds[0][0], pointIds[1][0])

                        sqlCode = ("""SELECT ffp_ver_pto_medio(%s);""" %(idList))
                        self.pgQuery(sqlCode, True, False)
                        self.iface.mapCanvas().refreshAllLayers()

                        msgWin = actionWindow(self.iface, ' Add Mid-Point')
                        msgWin.setMainText('Do you want to add the new midpoint to spatialunit %s?' % (spatialunitIds))
                        msgWin.setDescriptionText('In between points: %s' % (idList))
                        msgWin.adjustSize()
                        choice = msgWin.exec()

                        if choice == QMessageBox.Yes:
                            sqlCode = """SELECT ffp_nuevo_punto_medio(%s);""" % (idList)
                            self.pgQuery(sqlCode, True, True)
                            idx = self.pointsLayer.fields().indexFromName('pto')
                            newId = self.pointsLayer.maximumValue(idx)
                            logCode = sqlCode + '\n-- Added vertex [' + str(newId) + '] to spatialunit ' + str(spatialunitIds[0])
                            self.log(logCode)
                            self.undoMessages.append('Vertex %s will be removed from spatialunit %s' % (newId, spatialunitIds[0] ))

                            successMsg = 'Vertex %s has been added to spatialunit %s' % (newId, spatialunitIds[0])
                            self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                            print(successMsg + '\n---')

                            self.onNewSavePoint()
                        else:
                            self.clearScratch()
                            self.iface.mapCanvas().refreshAllLayers()

                    else:
                        message = 'The selected points are not sequencial...'
                        self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
                else:
                    message = 'The selected points belong to different spatialunits...'
                    self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
    #---


    def deletePoint(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count != 1:
                desc = count > 1 and ' just ' or ' '
                message = 'Please select%sone feature from layer "puntos_predio"... ' % (desc)
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                pointIds = []
                spatialunitIds = []
                startPoint = False
                for feature in features:
                    pointIds.append(feature['pto'])
                    if feature['num_pto'] == 1:
                        startPoint = True
                    if feature['id_pol'] not in spatialunitIds:
                        spatialunitIds.append(feature['id_pol'])

                if startPoint:
                    message = 'The selection contains the initial point of a spatiaunit, which cannot be deleted...'
                    self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
                else:
                    pointList = ', '.join(str(f) for f in pointIds)
                    sqlCode = ("""
                        INSERT INTO pto_ajuste
                            SELECT ROW_NUMBER() OVER(), geom
                            FROM puntos_predio
                            WHERE pto IN (%s);
                    """ % (pointList))
                    self.pgQuery(sqlCode, True, False)
                    self.iface.mapCanvas().refreshAllLayers()

                    msgWin = actionWindow(self.iface, ' Delete Point(s)')
                    msgWin.setMainText('Do you want to delete the selected point(s) from spatialunit %s?' % (spatialunitIds))
                    msgWin.setDescriptionText(pointList)
                    msgWin.adjustSize()
                    choice = msgWin.exec()

                    if choice == QMessageBox.Yes:
                        sqlCode = """SELECT ffp_borre_punto(%s, true);""" % (pointList)
                        self.pgQuery(sqlCode, True, True)

                        logCode = sqlCode + '\n-- Deleted vertex [ ' + pointList + ' ] from spatialunit ' + str(spatialunitIds[0])
                        self.log(logCode)
                        self.undoMessages.append('Vertex %s will be added back to spatialunit %s' % (pointList, spatialunitIds))

                        successMsg = 'Point %s was deleted succesfully' % (pointIds)
                        self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                        print(successMsg + '\n---')

                        self.onNewSavePoint()
                    else:
                        self.clearScratch()
                        self.iface.mapCanvas().refreshAllLayers()
    #---


    def joinLines(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.pointsLayer.selectedFeatures()
            count = len(features)
            if count % 2 != 0:
                message = 'An uneven number of features was selected from layer "puntos_predio"... '
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                correct = True
                pointIds = []
                spatialunitIds = []
                pointPairs = []

                for i in range(count):
                    if features[i]['id_pol'] not in spatialunitIds:
                        spatialunitIds.append(features[i]['id_pol'])
                    if features[i]['pto'] not in pointIds:
                        pointIds.append(features[i]['pto'])
                        distance = 10000
                        code = -1
                        for j in range(i+1, count):
                            if features[i]['id_pol'] != features[j]['id_pol']:
                                newDistance = self.calculator.measureLine(features[i].geometry().asPoint(), features[j].geometry().asPoint())
                                if newDistance < distance:
                                    code = j
                                    distance = newDistance
                        if code != -1:
                            pointPairs.append([features[i]['pto'], features[code]['pto'], distance])
                            if distance > self.threshold:
                                correct = False
                            pointIds.append(features[code]['pto'])
                            polyline = QgsRubberBand(self.iface.mapCanvas(), False)
                            x1, y1 = (float(x) for x in features[i].geometry().asPoint().toString().split(', '))
                            x2, y2 = (float(x) for x in features[code].geometry().asPoint().toString().split(', '))
                            polyline.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(x1, y1), QgsPoint(x2, y2)]), None)
                            polyline.setColor(QColor(255, 0, 0))
                            polyline.setWidth(2)
                            self.canvasLines.append(polyline)

                details = ''
                pointPairs.sort(key=lambda x: x[0])
                for item in pointPairs:
                    details += '%s ←→ %s : %s m\n' % (item[0], item[1], '{:.1f}'.format(item[2]))

                if correct:
                    msgWin = actionWindow(self.iface, ' Join Lines')
                    msgWin.setMainText('Do you want to combine the following pairs of points?')
                    msgWin.setDescriptionText(details)
                    msgWin.adjustSize()
                    choice = msgWin.exec()

                    if choice == QMessageBox.Yes:
                        logCode = ''
                        addSavePoint = True
                        for item in pointPairs:
                            sqlCode = """SELECT ffp_ver_pto_medio(%s, %s, true);""" % (item[0], item[1])
                            self.pgQuery(sqlCode, True, addSavePoint)
                            logCode += sqlCode + '\n'
                            addSavePoint = False
                        logCode += '-- The following point pairs were joined\n'
                        self.undoMessages.append('The following point pairs will be disconnected\n%s' % (details))
                        self.log(logCode + '-- '+ details.replace('\n', '\n-- ')[:-3])
                        self.iface.messageBar().pushMessage('Message:', 'Adjecent segments joined succesfully...', level=Qgis.Success)
                        message = 'Joined the following point pairs: %s' % (details)
                        print(message + '---')

                        self.onNewSavePoint()

                    self.clearCanvas()
                else:
                    self.clearCanvas()
                    msgBox = actionWindow(self.iface, ' Operation not Possible', False)
                    msgBox.setMainText(self.thresholdMsg)
                    msgBox.setDescriptionText(details)
                    msgBox.adjustSize()
                    msgBox.exec()
    #---


    def deletePolygon(self):
        message, ok = self.checkLayers()
        if ok:
            features = self.spatialunitsLayer.selectedFeatures()
            count = len(features)

            if count == 0:
                message = 'Select one spatialunit... '
                self.iface.messageBar().pushMessage('Operation not possible:', message, level=Qgis.Info)
            else:
                polyList = []
                for feature in features:
                    polyList.append(feature['objectid'])

                polyList.sort()
                targetPolygon = selectSpatialunitDialog(self.spatialunitsLayer, [str(r) for r in polyList]).exec()

                if targetPolygon != 0:
                    self.spatialunitsLayer.selectByExpression('"objectid"=%s' % (targetPolygon))
                    sql_code = ("""
                        TRUNCATE scratchpad;
                        INSERT INTO scratchpad (col1, col2, col3)
                            SELECT * FROM ffp_spatialunit_recordset(%s);
                    """ % (targetPolygon))

                    ok, err = self.pgQuery(sql_code)
                    if ok:
                        records = []
                        for record in self.resultsLayer.getFeatures():
                            records.append([record.attributes()[0], record.attributes()[1], record.attributes()[2]])
                        tblWin = tableWindow()
                        tblWin.setData(targetPolygon, records, self.iface)
                        choice = tblWin.exec()

                        if choice == QMessageBox.Yes:
                            sqlCode = ""
                            for i, (table, desc, globalid) in enumerate(records):
                                if i == 0:
                                    spatialunit_id = globalid
                                if '__attach' in table:
                                    sqlCode += ("""  INSERT INTO dump (table_name, objectid, record, data, deleted_on)
                                        SELECT '%s', %s, row(attachmentid, globalid, rel_globalid, content_type, att_name, data_size)::TEXT, data, to_char(now(), 'YYYY-MM-DD HH24:MI')
                                        FROM "%s" WHERE globalid = '%s';\n\n""" % (table, targetPolygon, table, globalid))
                                else:
                                    sqlCode += ("""  INSERT INTO dump (table_name, objectid, record, deleted_on) SELECT '%s', %s, row(t.*)::TEXT, to_char(now(), 'YYYY-MM-DD HH24:MI') FROM "%s" AS t WHERE globalid = '%s';\n\n""" % (table, targetPolygon, table, globalid))
                                sqlCode += """  DELETE FROM "%s" WHERE globalid = '%s';\n\n""" % (table, globalid)

                            sqlCode += """  DELETE FROM puntos_predio WHERE id_pol = '%s';\n\n""" % targetPolygon

                            sqlCode += """  INSERT INTO dump(table_name, objectid, record, deleted_on) SELECT 'anchorpoint', %s, row(p.*), to_char(now(), 'YYYY-MM-DD HH24:MI') FROM anchorpoint AS p WHERE p.spatialunit_id = '%s';\n\n""" % (targetPolygon, globalid)
                            sqlCode += """  DELETE FROM anchorpoint WHERE spatialunit_id = '%s';\n\n""" % spatialunit_id

                            sqlCode += """  INSERT INTO dump(table_name, objectid, record, deleted_on) SELECT 'vertexpoint', %s, row(p.*), to_char(now(), 'YYYY-MM-DD HH24:MI') FROM anchorpoint AS p WHERE p.spatialunit_id = '%s';\n\n""" % (targetPolygon, globalid)
                            sqlCode += """  DELETE FROM vertexpoint WHERE spatialunit_id = '%s';\n\n""" % spatialunit_id

                            sqlCode += """  INSERT INTO dump(table_name, objectid, record, deleted_on) SELECT 'referenceobject', %s, row(p.*), to_char(now(), 'YYYY-MM-DD HH24:MI') FROM anchorpoint AS p WHERE p.spatialunit_id = '%s';\n\n""" % (targetPolygon, globalid)
                            sqlCode += """  DELETE FROM referenceobject WHERE spatialunit_id = '%s';\n\n""" % spatialunit_id

                            ok, err = self.pgQuery(sqlCode, False, True)
                            if ok:
                                logCode = 'BEGIN;\n' + sqlCode + 'END;'
                                successMsg = ('All records associated with spatialunit %s were deleted.' % targetPolygon)
                                logCode += '\n-- ' + successMsg
                                self.log(logCode)
                                self.undoMessages.append('The records associated with spatialunit %s will be restored.' % targetPolygon)

                                self.iface.messageBar().pushMessage('Message:', successMsg, level=Qgis.Success)
                                print(successMsg + '\n---')

                                self.onNewSavePoint()
                            else:
                                print('Query error:')
                                print(err)
                        else:
                            self.refresh()
                    else:
                        print('Query error:')
                        print(err)
# #---


    def onNewSavePoint(self):
        self.sessionIsDirty = True
        self.refresh(True)
        self.clearScratch()
        for action in self.actions:
            if action.text() in ['Undo', 'Commit']:
                action.setEnabled(True)
            elif action.text() == 'Merge Boundaries':
                action.setDisabled(True)
    #---


    def endSession(self):
        if self.activeSession:
            self.pgSession.commit()
            self.log('-- ***** SESSION ENDED ON PROJECT CLOSE --- Changes were saved *****')
            del(self.pgSession)
            for action in self.actions:
                action.setDisabled(True)
            self.actions[0].setEnabled(True)
            self.actions[1].setEnabled(True)
            self.dropScratchpad()
            self.activeSession = False
            QgsProject.instance().projectSaved.disconnect(self.endSession)
            QgsProject.instance().setDirty(False)
    #---


    def unload(self):
        QgsProject.instance().readProject.disconnect(self.reset)
        QgsProject.instance().layersRemoved.disconnect(self.disableAllActions)

        if self.activeSession:
            self.pgSession.rollback()
            del(self.pgSession)
            self.dropScratchpad()
            self.activeSession = False
        del(self.toolbar)
    #---


    def dropScratchpad(self):
        sqlCode = """
            DROP TABLE IF EXISTS scratchpad;
        """
        self.runSql(sqlCode)
    #---

#---
