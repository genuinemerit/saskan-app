# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'saskan_servicesBSotXX.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from PySide2.QtWebKitWidgets import QWebView



class Ui_saskan_services(object):
    def setupUi(self, saskan_services):
        if not saskan_services.objectName():
            saskan_services.setObjectName(u"saskan_services")
        saskan_services.resize(630, 517)
        self.action_save = QAction(saskan_services)
        self.action_save.setObjectName(u"action_save")
        self.action_exit = QAction(saskan_services)
        self.action_exit.setObjectName(u"action_exit")
        self.action_add = QAction(saskan_services)
        self.action_add.setObjectName(u"action_add")
        self.action_remove = QAction(saskan_services)
        self.action_remove.setObjectName(u"action_remove")
        self.action_undo = QAction(saskan_services)
        self.action_undo.setObjectName(u"action_undo")
        self.action_schema = QAction(saskan_services)
        self.action_schema.setObjectName(u"action_schema")
        self.action_monitor = QAction(saskan_services)
        self.action_monitor.setObjectName(u"action_monitor")
        self.action_control = QAction(saskan_services)
        self.action_control.setObjectName(u"action_control")
        self.action_test = QAction(saskan_services)
        self.action_test.setObjectName(u"action_test")
        self.action_help = QAction(saskan_services)
        self.action_help.setObjectName(u"action_help")
        self.root_w = QWidget(saskan_services)
        self.root_w.setObjectName(u"root_w")
        self.horizontalLayoutWidget = QWidget(self.root_w)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 631, 31))
        self.tool_bar = QHBoxLayout(self.horizontalLayoutWidget)
        self.tool_bar.setObjectName(u"tool_bar")
        self.tool_bar.setContentsMargins(0, 0, 0, 0)
        self.tool_save = QToolButton(self.horizontalLayoutWidget)
        self.tool_save.setObjectName(u"tool_save")

        self.tool_bar.addWidget(self.tool_save)

        self.tb_line_1 = QFrame(self.horizontalLayoutWidget)
        self.tb_line_1.setObjectName(u"tb_line_1")
        self.tb_line_1.setFrameShape(QFrame.VLine)
        self.tb_line_1.setFrameShadow(QFrame.Sunken)

        self.tool_bar.addWidget(self.tb_line_1)

        self.tool_add = QToolButton(self.horizontalLayoutWidget)
        self.tool_add.setObjectName(u"tool_add")

        self.tool_bar.addWidget(self.tool_add)

        self.tool_remove = QToolButton(self.horizontalLayoutWidget)
        self.tool_remove.setObjectName(u"tool_remove")

        self.tool_bar.addWidget(self.tool_remove)

        self.tool_undo = QToolButton(self.horizontalLayoutWidget)
        self.tool_undo.setObjectName(u"tool_undo")

        self.tool_bar.addWidget(self.tool_undo)

        self.tb_line_2 = QFrame(self.horizontalLayoutWidget)
        self.tb_line_2.setObjectName(u"tb_line_2")
        self.tb_line_2.setFrameShape(QFrame.VLine)
        self.tb_line_2.setFrameShadow(QFrame.Sunken)

        self.tool_bar.addWidget(self.tb_line_2)

        self.tool_schema = QToolButton(self.horizontalLayoutWidget)
        self.tool_schema.setObjectName(u"tool_schema")

        self.tool_bar.addWidget(self.tool_schema)

        self.tool_monitor = QToolButton(self.horizontalLayoutWidget)
        self.tool_monitor.setObjectName(u"tool_monitor")

        self.tool_bar.addWidget(self.tool_monitor)

        self.tool_control = QToolButton(self.horizontalLayoutWidget)
        self.tool_control.setObjectName(u"tool_control")

        self.tool_bar.addWidget(self.tool_control)

        self.tool_test = QToolButton(self.horizontalLayoutWidget)
        self.tool_test.setObjectName(u"tool_test")

        self.tool_bar.addWidget(self.tool_test)

        self.tb_line_3 = QFrame(self.horizontalLayoutWidget)
        self.tb_line_3.setObjectName(u"tb_line_3")
        self.tb_line_3.setFrameShape(QFrame.VLine)
        self.tb_line_3.setFrameShadow(QFrame.Sunken)

        self.tool_bar.addWidget(self.tb_line_3)

        self.tool_help = QToolButton(self.horizontalLayoutWidget)
        self.tool_help.setObjectName(u"tool_help")

        self.tool_bar.addWidget(self.tool_help)

        self.tool_exit = QToolButton(self.horizontalLayoutWidget)
        self.tool_exit.setObjectName(u"tool_exit")

        self.tool_bar.addWidget(self.tool_exit)

        self.verticalLayoutWidget = QWidget(self.root_w)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 30, 631, 301))
        self.editor = QVBoxLayout(self.verticalLayoutWidget)
        self.editor.setObjectName(u"editor")
        self.editor.setContentsMargins(0, 0, 0, 0)
        self.editor_display = QPlainTextEdit(self.verticalLayoutWidget)
        self.editor_display.setObjectName(u"editor_display")

        self.editor.addWidget(self.editor_display, 0, Qt.AlignTop)

        self.editor_buttons = QHBoxLayout()
        self.editor_buttons.setObjectName(u"editor_buttons")
        self.btn_top = QPushButton(self.verticalLayoutWidget)
        self.btn_top.setObjectName(u"btn_top")

        self.editor_buttons.addWidget(self.btn_top, 0, Qt.AlignBottom)

        self.btn_tail = QPushButton(self.verticalLayoutWidget)
        self.btn_tail.setObjectName(u"btn_tail")

        self.editor_buttons.addWidget(self.btn_tail, 0, Qt.AlignBottom)

        self.btn_clear = QPushButton(self.verticalLayoutWidget)
        self.btn_clear.setObjectName(u"btn_clear")

        self.editor_buttons.addWidget(self.btn_clear, 0, Qt.AlignBottom)


        self.editor.addLayout(self.editor_buttons)

        self.gridLayoutWidget = QWidget(self.root_w)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 330, 631, 141))
        self.assistant = QGridLayout(self.gridLayoutWidget)
        self.assistant.setObjectName(u"assistant")
        self.assistant.setContentsMargins(0, 0, 0, 0)
        self.status_box = QLineEdit(self.gridLayoutWidget)
        self.status_box.setObjectName(u"status_box")

        self.assistant.addWidget(self.status_box, 1, 0, 1, 1)

        self.analysis = QHBoxLayout()
        self.analysis.setObjectName(u"analysis")
        self.help_display = QWebView(self.gridLayoutWidget)
        self.help_display.setObjectName(u"help_display")
        self.help_display.setUrl(QUrl(u"about:blank"))

        self.analysis.addWidget(self.help_display)

        self.stats_display = QOpenGLWidget(self.gridLayoutWidget)
        self.stats_display.setObjectName(u"stats_display")

        self.analysis.addWidget(self.stats_display)


        self.assistant.addLayout(self.analysis, 0, 0, 1, 1)

        saskan_services.setCentralWidget(self.root_w)
        self.menu_bar = QMenuBar(saskan_services)
        self.menu_bar.setObjectName(u"menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 630, 22))
        self.menu_file = QMenu(self.menu_bar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_edit = QMenu(self.menu_bar)
        self.menu_edit.setObjectName(u"menu_edit")
        self.menu_window = QMenu(self.menu_bar)
        self.menu_window.setObjectName(u"menu_window")
        self.menu_help = QMenu(self.menu_bar)
        self.menu_help.setObjectName(u"menu_help")
        saskan_services.setMenuBar(self.menu_bar)
        self.statusbar = QStatusBar(saskan_services)
        self.statusbar.setObjectName(u"statusbar")
        saskan_services.setStatusBar(self.statusbar)

        self.menu_bar.addAction(self.menu_file.menuAction())
        self.menu_bar.addAction(self.menu_edit.menuAction())
        self.menu_bar.addAction(self.menu_window.menuAction())
        self.menu_bar.addAction(self.menu_help.menuAction())
        self.menu_file.addAction(self.action_save)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.menu_edit.addAction(self.action_add)
        self.menu_edit.addAction(self.action_remove)
        self.menu_edit.addAction(self.action_undo)
        self.menu_window.addAction(self.action_schema)
        self.menu_window.addAction(self.action_monitor)
        self.menu_window.addAction(self.action_control)
        self.menu_window.addAction(self.action_test)
        self.menu_help.addAction(self.action_help)

        self.retranslateUi(saskan_services)

        QMetaObject.connectSlotsByName(saskan_services)
    # setupUi

    def retranslateUi(self, saskan_services):
        saskan_services.setWindowTitle(QCoreApplication.translate("saskan_services", u"MainWindow", None))
        self.action_save.setText(QCoreApplication.translate("saskan_services", u"Save", None))
        self.action_exit.setText(QCoreApplication.translate("saskan_services", u"Exit", None))
        self.action_add.setText(QCoreApplication.translate("saskan_services", u"Add", None))
        self.action_remove.setText(QCoreApplication.translate("saskan_services", u"Remove", None))
        self.action_undo.setText(QCoreApplication.translate("saskan_services", u"Undo", None))
        self.action_schema.setText(QCoreApplication.translate("saskan_services", u"Schema", None))
        self.action_monitor.setText(QCoreApplication.translate("saskan_services", u"Monitor", None))
        self.action_control.setText(QCoreApplication.translate("saskan_services", u"Control", None))
        self.action_test.setText(QCoreApplication.translate("saskan_services", u"Test", None))
        self.action_help.setText(QCoreApplication.translate("saskan_services", u"User Guide", None))
        self.tool_save.setText(QCoreApplication.translate("saskan_services", u"Save", None))
        self.tool_add.setText(QCoreApplication.translate("saskan_services", u"Add", None))
        self.tool_remove.setText(QCoreApplication.translate("saskan_services", u"Remove", None))
        self.tool_undo.setText(QCoreApplication.translate("saskan_services", u"Undo", None))
        self.tool_schema.setText(QCoreApplication.translate("saskan_services", u"Schema", None))
        self.tool_monitor.setText(QCoreApplication.translate("saskan_services", u"Monitor", None))
        self.tool_control.setText(QCoreApplication.translate("saskan_services", u"Control", None))
        self.tool_test.setText(QCoreApplication.translate("saskan_services", u"Test", None))
        self.tool_help.setText(QCoreApplication.translate("saskan_services", u"Help", None))
        self.tool_exit.setText(QCoreApplication.translate("saskan_services", u"Exit", None))
        self.btn_top.setText(QCoreApplication.translate("saskan_services", u"Top", None))
        self.btn_tail.setText(QCoreApplication.translate("saskan_services", u"Tail", None))
        self.btn_clear.setText(QCoreApplication.translate("saskan_services", u"Clear", None))
        self.menu_file.setTitle(QCoreApplication.translate("saskan_services", u"File", None))
        self.menu_edit.setTitle(QCoreApplication.translate("saskan_services", u"Edit", None))
        self.menu_window.setTitle(QCoreApplication.translate("saskan_services", u"Window", None))
        self.menu_help.setTitle(QCoreApplication.translate("saskan_services", u"Help", None))
    # retranslateUi

