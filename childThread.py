#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/4/14 15:06
# @Author  : 
# @File    : childThread.py
# @Software: PyCharm
from PyQt5.QtCore import QThread, pyqtSignal
import os
import functions

req_header = {
                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'accept-encoding': 'gzip, deflate, br',
                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
              }

class CheckNetworkThread(QThread):
    _signal = pyqtSignal(bool)

    def __init__(self):
        super(CheckNetworkThread, self).__init__()

    def run(self):
        status = functions.isConnected()
        self._signal.emit(status)

class SearchFilmThread(QThread):
    _signal = pyqtSignal(dict)

    def __init__(self, filmName):
        super(SearchFilmThread, self).__init__()
        self.filmName = filmName

    def run(self):
        searchResult = functions.searchFilm(self.filmName)
        self._signal.emit(searchResult)

class GetFilmInfoThread(QThread):
    _signal = pyqtSignal(list)

    def __init__(self, url):
        super(GetFilmInfoThread, self).__init__()
        self.url = url

    def run(self):
        info = functions.getFilmInfo(self.url)
        self._signal.emit(info)

class DownloadThread(QThread):
    _signal = pyqtSignal(bool)

    def __init__(self, fileName, url):
        super(DownloadThread, self).__init__()
        self.fileName = fileName
        self.url = url

    def run(self):
        functions.downloadBtFile(self.fileName, self.url)
        if os.path.exists("download/" + self.fileName):
            self._signal.emit(True)
        else:
            self._signal.emit(False)