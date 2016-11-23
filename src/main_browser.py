#!/usr/bin/env python

# Copyright (c) 2010 Harrison Erd
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.
import readline
import sys, urllib
from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.formatters import HtmlFormatter
from PyQt4 import QtCore, QtGui, QtWebKit
import resources
import os
import pyttsx
from bs4 import BeautifulSoup





class new_page(QtWebKit.QWebPage):

    def __init__(self, parent):
        super(new_page, self).__init__(parent)
        self.setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.nexturl = None
        self.connect(self, QtCore.SIGNAL("linkClicked (const QUrl&)"),
            self.link)

    def link(self, *args):
        print args

    def createStandardContextMenu(self):
        menu = QtWebKit.QWebPage.createStandardContextMenu(self)
        menu.addAction("Open in New tab")
        return menu

    def acceptNavigationRequest(self, frame, request, navtype):
        print "nav request to ", frame.url(), request.url()
        return True

class new_browser(QtWebKit.QWebView):

    def __init__(self, parent):
        super(new_browser, self).__init__(parent)
        self.tab = parent
        page = new_page(self)
        self.setPage(page)

    def createWindow(self, param):
        self.tab.mainUi.addNewTab(self.page().nexturl)

    def contextMenuEvent(self, event=None):
        menu = self.page().createStandardContextMenu()
        result = menu.exec_(event.globalPos())
        hit = self.page().mainFrame().hitTestContent(event.pos())
        self.page().nexturl =  hit.linkUrl()
        print "contextMenuEvent", result
        self.createWindow(None)


class new_tab(QtGui.QWidget):

    def __init__(self, index, url=None, parent=None):
        super(new_tab, self).__init__(parent)
        self.mainUi = parent
        self.index = index
        print "making new tab with index", index
        self.browser = new_browser(self)
        self.connect(self.browser, QtCore.SIGNAL('linkClicked (const QUrl&)'),
            self.updateLineEdit)
        self.connect(self.browser, QtCore.SIGNAL('linkClicked (const QUrl&)'),
            self.GoLink)
        self.connect(self.browser, QtCore.SIGNAL('urlChanged (const QUrl&)'),
            self.updateLineEdit)
        self.connect(self.browser, QtCore.SIGNAL('loadStarted ()'),
            self.loadStarted)
        self.connect(self.browser, QtCore.SIGNAL('loadFinished (bool)'),
            self.loadFinished)

        if url:
            self.current_url = url
        else:
            if len(sys.argv) > 1:
                print sys.argv[1]
                if sys.argv[1].find("http://") == -1:
                    strungurl = str(sys.argv[1])
                    self.current_url = QtCore.QUrl("http://%s" % strungurl)
                else:
                    self.current_url = QtCore.QUrl(sys.argv[1])
            else:
                self.current_url = QtCore.QUrl("http://www.google.com/")
        self.browser.setUrl(self.current_url)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.addWidget(self.browser)

    def GoLink(self, url):
        self.current_url = url
        self.browser.load(url)
        #self.browser.runjs(url)
        page = self.browser.page()
        page.setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        page.action = self.action
        print "new page"

    def loadStarted(self):
        print "loading page...",

    def loadFinished(self,arg):
        print "load finished...",
        if arg:
            print "sucess"
            import time, os
            self.mainUi.tabWidget.setTabText(self.index, self.browser.title())
            datetime= time.strftime("%A, %B %d, %Y, %H:%M:%S", time.localtime())
            url = str(self.mainUi.lineEdit.text())
            f1 = open("history.txt", "r")
            old_post = f1.read()
            os.remove("history.txt")
            f2 = open("history.txt", "w")
            if url == "browser.history":
                f2.write(old_post)
            else:
                f2.write('<small>%s</small> - <strong><a href="%s">%s</a></strong> </br></br>\n%s' % (datetime,url,url,old_post))
        else:
            print "failed"
            self.tellFailLoad()

    def updateLineEdit(self,url):
        self.current_url = url
        if self.index == self.mainUi.tabWidget.currentIndex():
            self.mainUi.updateLineEdit(url)

    def tellFailLoad(self):
        self.browser.setHtml("The page you are trying to view can not be loaded. You may want to try reloading or downloading the page.")

    def action (self, param=None, param2= None, param3=None):
        print param, param2, param3

class browser(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(browser, self).__init__(parent)
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.centralwidget = QtGui.QWidget

        self.toolbar = QtGui.QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.addToolBar(self.toolbar)

        icon = QtGui.QIcon("icons/newt.png")
        self.action_ntab = QtGui.QPushButton(icon, (""), self)

        icon = QtGui.QIcon("icons/back.png")
        self.action_back = QtGui.QAction(icon, ("Back"), self)

        icon = QtGui.QIcon("icons/forward.png")
        self.action_forward = QtGui.QAction(icon, ("Forward"), self)

        icon = QtGui.QIcon("icons/go-home.png")
        self.action_home = QtGui.QAction(icon, ("Home"), self)

        icon = QtGui.QIcon("icons/go.png")
        self.action_go = QtGui.QAction(icon, ("Go"), self)

        icon = QtGui.QIcon("icons/other.png")
        self.button_other = QtGui.QToolButton(self)
        self.button_other.setPopupMode(2)
        self.button_other.setIcon(icon)

        self.action_goHome = QtGui.QAction("Home", self)
        self.action_newTab = QtGui.QAction("New tab", self)
        self.action_delTab = QtGui.QAction("Close current tab", self)
        self.action_vBooks = QtGui.QAction("View bookmarks", self)
        self.action_aBooks = QtGui.QAction("Add bookmark", self)
        self.action_source = QtGui.QAction("View source", self)
        self.action_incBrightness = QtGui.QAction("Increase brightness", self)
        self.action_decBrightness = QtGui.QAction("Decrease brightness", self)
        self.action_speakPage = QtGui.QAction("Read page aloud", self)
        self.action_highContrast = QtGui.QAction("Invert colors", self)
        self.action_viHist = QtGui.QAction("Web history", self)
        self.action_clHist = QtGui.QAction("Clear history", self)
        self.action_downld = QtGui.QAction("Download page", self)
        self.action_zoomin = QtGui.QAction("Zoom In", self)
        self.action_zoomot = QtGui.QAction("Zoom Out", self)

        self.action_goHome.setShortcut("Ctrl+H")
        self.action_newTab.setShortcut("Ctrl+T")
        self.action_delTab.setShortcut("Ctrl+W")
        self.action_vBooks.setShortcut("Ctrl+B")
        self.action_aBooks.setShortcut("Ctrl+A")
        self.action_downld.setShortcut("Ctrl+D")
        self.action_zoomin.setShortcut("Ctrl+Z")
        self.action_zoomot.setShortcut("Ctrl+O")

        self.other_menu = QtGui.QMenu(self)
        self.other_menu.addAction(self.action_goHome)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_newTab)
        self.other_menu.addAction(self.action_delTab)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_vBooks)
        self.other_menu.addAction(self.action_aBooks)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_source)
        self.other_menu.addAction(self.action_speakPage)
        self.other_menu.addAction(self.action_highContrast)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_incBrightness)
        self.other_menu.addAction(self.action_decBrightness)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_viHist)
        self.other_menu.addAction(self.action_clHist)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_downld)
        self.other_menu.addSeparator()
        self.other_menu.addAction(self.action_zoomin)
        self.other_menu.addAction(self.action_zoomot)

        self.button_other.setMenu(self.other_menu)

        self.lineEdit = QtGui.QLineEdit(self)

        self.toolbar.addAction(self.action_back)
        self.toolbar.addAction(self.action_forward)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_home)
        self.toolbar.addWidget(self.lineEdit)
        self.toolbar.addAction(self.action_go)
        self.toolbar.addWidget(self.button_other)

        self.statusbar = QtGui.QStatusBar(self)
        self.progress_bar = QtGui.QProgressBar()
        self.statusbar.addWidget(self.progress_bar, 5)
        self.statusbar.setMaximumSize(2000, 15)
        self.setStatusBar(self.statusbar)

        self.tabWidget = QtGui.QTabWidget()
        self.tabbar = QtGui.QTabBar(self)
        self.tabWidget.setTabBar(self.tabbar)
        self.addNewTab()
        self.setCentralWidget(self.tabWidget)

        self.setWindowTitle("Samavan")

        self.connect(self.action_back, QtCore.SIGNAL('triggered()'),
            self.goBack)
        self.connect(self.action_forward, QtCore.SIGNAL('triggered()'),
            self.goForward)
        self.connect(self.action_home, QtCore.SIGNAL('triggered()'),
            self.goHome)
        self.connect(self.lineEdit, QtCore.SIGNAL('returnPressed()'),
            self.lineEdited)
        self.connect(self.action_go, QtCore.SIGNAL('triggered()'),
            self.lineEdited)
        self.connect(self.tabWidget, QtCore.SIGNAL('currentChanged(int)'),
            self.tabChanged)
        self.connect(self.tabWidget.currentWidget().browser, QtCore.SIGNAL("loadProgress(int)"),
            self.progress_bar, QtCore.SLOT("setValue(int)"))
        self.connect(self.action_goHome, QtCore.SIGNAL('triggered()'),
            self.goHome)
        self.connect(self.action_newTab, QtCore.SIGNAL('triggered()'),
            self.addNewTab)
        self.connect(self.action_delTab, QtCore.SIGNAL('triggered()'),
            self.delOldTab)
        self.connect(self.action_vBooks, QtCore.SIGNAL('triggered()'),
            self.viewBookmarks)
        self.connect(self.action_aBooks, QtCore.SIGNAL('triggered()'),
            self.addABookmark)
        self.connect(self.action_source, QtCore.SIGNAL('triggered()'),
            self.viewSrc)
        self.connect(self.action_speakPage, QtCore.SIGNAL('triggered()'),
            self.speakPage)
        self.connect(self.action_highContrast, QtCore.SIGNAL('triggered()'),
            self.highContrast)
        self.connect(self.action_incBrightness, QtCore.SIGNAL('triggered()'),
            self.incBrightness)
        self.connect(self.action_decBrightness, QtCore.SIGNAL('triggered()'),
            self.decBrightness)
        self.connect(self.action_viHist, QtCore.SIGNAL('triggered()'),
            self.history)
        self.connect(self.action_clHist, QtCore.SIGNAL('triggered()'),
            self.clear_history)
        self.connect(self.action_downld, QtCore.SIGNAL('triggered()'),
            self.offerDownload)
        self.connect(self.action_zoomin, QtCore.SIGNAL('triggered()'),
            self.zoomIn)
        self.connect(self.action_zoomot, QtCore.SIGNAL('triggered()'),
            self.zoomOut)
        self.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested (int)'),
            self.removeTab)
        self.connect(self.action_ntab, QtCore.SIGNAL('clicked()'),
            self.addNewTab)
        self.tabWidget.setCornerWidget(self.action_ntab)

    def currentBrowser(self):
        widget = self.tabWidget.currentWidget()
        if widget is not None:
            return widget.browser

    def goForward(self):
        self.tabWidget.currentWidget().browser.forward()

    def goBack(self):
        self.tabWidget.currentWidget().browser.back()

    def zoomIn(self):
        current = self.tabWidget.currentWidget().browser.textSizeMultiplier()
        self.tabWidget.currentWidget().browser.setTextSizeMultiplier(current + 0.5)

    def zoomOut(self):
        current = self.tabWidget.currentWidget().browser.textSizeMultiplier()
        self.tabWidget.currentWidget().browser.setTextSizeMultiplier(current - 0.5)

    def addNewTab(self, url=None):
        i = self.renumberTabs()
        newtab = new_tab(i, url, self)
        self.tabWidget.addTab(newtab, '(untitled)')
        self.tabWidget.setCurrentWidget(newtab)
        self.tabWidget.setTabsClosable(self.tabWidget.count() > 1)

    def removeTab(self, i):
        self.tabWidget.removeTab(i)
        self.tabWidget.setTabsClosable(self.tabWidget.count() != 1)

    def history(self):
        try:
            fileHandle = open('history.txt')
            filehistroy = fileHandle.read()
            self.addNewTab(url=QtCore.QUrl("browser.history"))

            self.currentBrowser().setHtml("<title>History</title>%s" % (filehistroy))
        except IOError, e:
            self.currentBrowser().setHtml("<title>Error</title>\nError, no history file found.")

    def clear_history(self):
        fileHandle = open('history.txt', 'w')
        fileHandle.write("")
        fileHandle.close()

    def renumberTabs(self):
        i = 0
        while i < self.tabWidget.count():
            self.tabWidget.widget(i).index = i
            i += 1
        return i

    def tabChanged(self, index):
        self.updateLineEdit(self.tabWidget.currentWidget().current_url)

    def delOldTab(self):
        if self.tabWidget.count() == 1:
            return
        widget = self.tabWidget.currentWidget()
        if widget is not None:
            self.tabWidget.removeTab(self.tabWidget.indexOf(widget))
            widget.deleteLater()

    def viewBookmarks(self):
        try:
           bookread = open("browser_faves.txt", 'r')
           self.currentBrowser().setHtml(bookread.read())
           bookread.close()
        except IOError, e:
           self.currentBrowser().setHtml("Favourites file not found.")

    def addABookmark(self):
        link1 = '<a href="'
        link2 = '">%s</a><br>'%self.lineEdit.text()
        bookurl = ("%s%s%s"%(link1,self.lineEdit.text(),link2)).encode('ascii')
        hpaste = open('browser_faves.txt', 'a').write('%s'%(bookurl))
        bookwn = QtGui.QMessageBox.question(self,"browser",
            "The page has been bookmarked.", QtGui.QMessageBox.Ok)

    def inspect(self):
        QtWebKit.QWebInspector.setPage(self.currentBrowser())

    def viewSrc(self):
        html = self.currentBrowser().page().mainFrame().toHtml().toUtf8()
        try:
            url = str(self.lineEdit.text())
            self.addNewTab(url=QtCore.QUrl("view.source:%s" %url))
            html2 = highlight(str(html), HtmlLexer(), HtmlFormatter(linenos=True,full=True))
            self.currentBrowser().setHtml("<title>view.source:%s</title>%s" % (url,html2))
        except ImportError, e:
            self.currentBrowser().setHtml(str(html))

    def speakPage(self):
            html = self.currentBrowser().page().mainFrame().toHtml().toUtf8()
            soup=BeautifulSoup(str(html))
            for script in soup(["script", "style"]):
                script.extract()
            text=soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            engine=pyttsx.init()
            engine.setProperty('rate', 120)
            engine.say(text)
            engine.runAndWait()
            
    def highContrast(self):
        os.system("xcalib -invert -alter")

    def incBrightness(self):
        os.system("xbacklight -inc 20")

    def decBrightness(self):
        os.system("xbacklight -dec 20")

    def goHome(self):
        self.currentBrowser().setUrl(QtCore.QUrl("http://www.google.com"))

    def offerDownload(self):
        url = str(self.lineEdit.text())
        result=QtGui.QMessageBox.question(self,"Download File",
        "Download File <br />%s"%url,
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes )

        if result == QtGui.QMessageBox.Yes:
            filename, headers = urllib.urlretrieve(url)
            print "Downloaded: %s - Location: %s" % (url, filename)
            QtGui.QMessageBox.information(self,"browser",
            """
<title>Downloads</title> <h1>Downloading your file to %s...</h1><hr>
<h2>Info on browser Downloads:</h2>
If you wish to view this file go to %s. If you wish to save the file
go to %s and save, otherwise when browser is exited, you will lose the
file.
""" % (filename, filename, filename))

    def lineEdited(self):
        self.tabWidget.currentWidget().GoLink(QtCore.QUrl(self.lineEdit.text()))
        url = str(self.lineEdit.text())
        if url.find("browser.history") != -1:
            print "looking for history"
            fileHandle = open('history.txt')
            filehistroy = fileHandle.read()
            self.currentBrowser().setHtml("<title>History</title>%s" % (filehistroy))
        else:
           if url.find("http://") == -1:
               url = "http://%s" % (url)
               self.tabWidget.currentWidget().GoLink(QtCore.QUrl(url))
           if url.find(".") == -1:
               url = "http://www.google.com/search?q=%s" % (self.lineEdit.text())
               self.tabWidget.currentWidget().GoLink(QtCore.QUrl(url))

    def updateLineEdit(self,url):
        if url.toString() == "about:blank":
            pass
        else:
            self.lineEdit.setText(url.toString())
        self.connect(self.tabWidget.currentWidget().browser, QtCore.SIGNAL("loadProgress(int)"),
            self.progress_bar, QtCore.SLOT("setValue(int)"))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ui = browser()
    ui.show()
    sys.exit(app.exec_())
