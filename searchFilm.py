#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/14 22:38
# @Author  : 
# @File    : searchFilm.py
# @Software: PyCharm
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QLabel, \
                            QMessageBox, QDialog, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QIcon, QMovie, QPalette, QBrush, QPixmap, QImage

import sys
import os
import webbrowser
from childThread import *
from SearchFilmUI import *

class SearchFilm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(SearchFilm, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(u'找电影')
        self.setFixedSize(991, 700)
        # 窗口居中显示
        # desktop = QtWidgets.QApplication.desktop()
        # x = (desktop.width() - self.width()) // 2
        # y = (desktop.height() - self.height()) // 2
        # self.move(x, y)

        # self.buttonBack.setStyleSheet("QPushButton{border-image: url(img/back_16px.png)}")
        self.buttonBack.setIcon(QIcon('img/back_16px.png'))
        # self.buttonDownload.setStyleSheet("QPushButton{border-image: url(img/download_16px.png)}")
        self.buttonDownload.setIcon(QIcon('img/download_16px.png'))
        # self.buttonZoomOut.setStyleSheet("QPushButton{border-image: url(img/zoom_out_16px.png)}")
        self.buttonZoomOut.setIcon(QIcon('img/zoom_out_16px.png'))
        # self.buttonZoomIn.setStyleSheet("QPushButton{border-image: url(img/zoom_in_16px.png)}")
        self.buttonZoomIn.setIcon(QIcon('img/zoom_in_16px.png'))

        self.settingsMenu = self.menuBar().addMenu(u'设置')
        self.helpMenu = self.menuBar().addMenu(u'帮助')

        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.lableNetStatus = QLabel()
        self.lableNetStatus.setText(u"网络状态: ")
        self.statusbar.addWidget(self.lableNetStatus)

        self.permanent = QLabel()
        self.permanent.setText("<a href=\"http://www.415.net\">bt之家</a>")
        self.permanent.setOpenExternalLinks(True) # 设置可以打开网站链接
        self.statusbar.addPermanentWidget(self.permanent)

        self.checkNetwork()

        self.buttonSearchMain.clicked.connect(self.search)
        self.buttonSearch.clicked.connect(self.getSearchResult)
        self.listWidget.itemClicked.connect(self.itemClicked)
        self.buttonBack.clicked.connect(self.backToIndex1)
        self.buttonOpenUrl.clicked.connect(self.openUrl)
        self.buttonZoomIn.clicked.connect(self.zoom_in_func)
        self.buttonZoomOut.clicked.connect(self.zoom_out_func)
        self.buttonDownload.clicked.connect(self.downloadBT)

    def showDialog(self):
        self.dialog = QDialog()
        self.dialog.setWindowFlags(Qt.FramelessWindowHint) # 无边框

        # 设置显示位置在主窗口中央，大小100*100
        rect = self.frameGeometry()
        x = rect.x() + rect.width() // 2 - 50
        y = rect.y() + rect.height() // 2 - 50
        self.dialog.setGeometry(x, y, 100, 100)

        #dialog.setAttribute(Qt.WA_TranslucentBackground)
        label = QLabel(self.dialog)
        #label.setText("pic")
        gif = QMovie('img/loading.gif')
        label.setMovie(gif)
        gif.start()
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.exec_()

    def search(self):
        filmName = self.lineEditFilmNameMain.text()
        if filmName == '':
            QMessageBox.information(self, u'提示', u'请在搜索框内填写电影名', QMessageBox.Yes)
        else:
            self.stackedWidgetMain.setCurrentIndex(1)
            self.lineEditFilmName.setText(filmName)
            self.searchFilmThread = SearchFilmThread(filmName)
            self.searchFilmThread._signal.connect(self.addItems)
            self.searchFilmThread.start()
            self.showDialog()

    def getSearchResult(self):
        filmName = self.lineEditFilmName.text()
        if filmName == '':
            QMessageBox.information(self, u'提示', u'请在搜索框内填写电影名', QMessageBox.Yes)
        else:
            self.listWidget.clear()
            self.stackedWidget.setCurrentIndex(0)
            self.searchFilmThread = SearchFilmThread(filmName)
            self.searchFilmThread._signal.connect(self.addItems)
            self.searchFilmThread.start()
            self.showDialog()

    def itemClicked(self, item):
        # 清理之前显示的内容
        info = "<!DOCTYPE html>\n<html>\n</head>\n</html>\n"
        self.browser.setHtml(info)
        self.browser.clearFocus()
        self.stackedWidget.setCurrentIndex(1)
        url = self.searchResult[item.text()]
        self.getFilmInfoThread = GetFilmInfoThread(url)
        self.getFilmInfoThread._signal.connect(self.showFilmInfo)
        self.getFilmInfoThread.start()
        self.showDialog()

    def backToIndex1(self):
        self.stackedWidget.setCurrentIndex(0)
        # 清理之前显示的内容
        info = "<!DOCTYPE html>\n<html>\n</head>\n</html>\n"
        self.browser.setHtml(info)
        self.browser.clearFocus()

    def addItems(self, filmList):
        self.listWidget.clear()
        self.searchResult = filmList
        for film in filmList:
            self.listWidget.addItem(''.join(film))
        self.dialog.close()

    def showFilmInfo(self, info):
        self.browser.setHtml(info[0])
        self.browser.setZoomFactor(0.7)
        self.fileName = info[1]
        self.labelFileName.setText(self.fileName)
        self.downloadUrl = info[2]
        self.dialog.close()

    def openUrl(self):
        webbrowser.open_new_tab("www.415.net")

    def zoom_in_func(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1)

    def zoom_out_func(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() - 0.1)

    def downloadBT(self):

        self.downloadThread = DownloadThread(self.fileName, self.downloadUrl)
        self.downloadThread._signal.connect(self.updateDownloadStatus)
        self.downloadThread.start()

    def updateDownloadStatus(self, status):
        if status:
            QMessageBox.information(self, u'下载提示', u'下载完成', QMessageBox.Yes)
        else:
            QMessageBox.information(self, u'下载提示', u'下载失败！', QMessageBox.Yes)

    def checkNetwork(self):
        self.checkNetworkThread = CheckNetworkThread()
        self.checkNetworkThread._signal.connect(self.updateNetStatus)
        self.checkNetworkThread.start()

    def updateNetStatus(self, status):
        if status:
            self.lableNetStatus.setText(u"网络状态: 已连接")
        else:
            self.lableNetStatus.setText(u"网络状态: 已断开")


    def closeEvent(self, event):
        """
        对MainWindow的函数closeEvent进行重构
        退出软件时结束所有进程
        """
        reply = QMessageBox.question(self, u'关闭提示', "是否要退出程序？",
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            os._exit(0)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SearchFilm()
    ui.show()
    sys.exit(app.exec_())
