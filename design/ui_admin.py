# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'adminZcXrru.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from PySide2.QtWebKitWidgets import QWebView



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(884, 630)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 40, 111, 111))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.toolButton_3 = QToolButton(self.verticalLayoutWidget)
        self.toolButton_3.setObjectName(u"toolButton_3")

        self.verticalLayout.addWidget(self.toolButton_3)

        self.toolButton_2 = QToolButton(self.verticalLayoutWidget)
        self.toolButton_2.setObjectName(u"toolButton_2")

        self.verticalLayout.addWidget(self.toolButton_2)

        self.toolButton = QToolButton(self.verticalLayoutWidget)
        self.toolButton.setObjectName(u"toolButton")

        self.verticalLayout.addWidget(self.toolButton)

        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(130, 40, 741, 271))
        self.webView = QWebView(self.centralwidget)
        self.webView.setObjectName(u"webView")
        self.webView.setGeometry(QRect(340, 400, 531, 181))
        self.webView.setUrl(QUrl(u"about:blank"))
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(170, 310, 641, 51))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_5 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.horizontalLayout.addWidget(self.pushButton_5)

        self.pushButton_6 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.horizontalLayout.addWidget(self.pushButton_6)

        self.pushButton_4 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout.addWidget(self.pushButton_4)

        self.pushButton_3 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.pushButton = QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(340, 380, 91, 17))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(130, 10, 121, 17))
        self.horizontalLayoutWidget_2 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(260, 10, 611, 31))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.checkBox_3 = QCheckBox(self.horizontalLayoutWidget_2)
        self.checkBox_3.setObjectName(u"checkBox_3")

        self.horizontalLayout_2.addWidget(self.checkBox_3)

        self.checkBox_2 = QCheckBox(self.horizontalLayoutWidget_2)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.horizontalLayout_2.addWidget(self.checkBox_2)

        self.checkBox_5 = QCheckBox(self.horizontalLayoutWidget_2)
        self.checkBox_5.setObjectName(u"checkBox_5")

        self.horizontalLayout_2.addWidget(self.checkBox_5)

        self.checkBox_6 = QCheckBox(self.horizontalLayoutWidget_2)
        self.checkBox_6.setObjectName(u"checkBox_6")

        self.horizontalLayout_2.addWidget(self.checkBox_6)

        self.checkBox_4 = QCheckBox(self.horizontalLayoutWidget_2)
        self.checkBox_4.setObjectName(u"checkBox_4")

        self.horizontalLayout_2.addWidget(self.checkBox_4)

        self.checkBox = QCheckBox(self.horizontalLayoutWidget_2)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_2.addWidget(self.checkBox)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 380, 91, 17))
        self.openGLWidget = QOpenGLWidget(self.centralwidget)
        self.openGLWidget.setObjectName(u"openGLWidget")
        self.openGLWidget.setGeometry(QRect(10, 400, 321, 181))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 884, 22))
        self.menuSaskan_Schema_Services = QMenu(self.menubar)
        self.menuSaskan_Schema_Services.setObjectName(u"menuSaskan_Schema_Services")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuSaskan_Schema_Services.menuAction())
        self.menuSaskan_Schema_Services.addAction(self.actionExit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.toolButton_3.setText(QCoreApplication.translate("MainWindow", u"Admin", None))
        self.toolButton_2.setText(QCoreApplication.translate("MainWindow", u"Monitor", None))
        self.toolButton.setText(QCoreApplication.translate("MainWindow", u"Controller", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"User Guide", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Services Monitor", None))
        self.checkBox_3.setText(QCoreApplication.translate("MainWindow", u"Pending", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"Requests", None))
        self.checkBox_5.setText(QCoreApplication.translate("MainWindow", u"Responses", None))
        self.checkBox_6.setText(QCoreApplication.translate("MainWindow", u"Pressure", None))
        self.checkBox_4.setText(QCoreApplication.translate("MainWindow", u"Errors", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"Log", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Stats", None))
        self.menuSaskan_Schema_Services.setTitle(QCoreApplication.translate("MainWindow", u"Saskan Schema Services", None))
    # retranslateUi

