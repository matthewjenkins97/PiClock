# -*- coding: utf-8 -*-

import sys
import os
import signal
import datetime
import time
import locale

from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.QtGui import QColor
from PyQt4.QtCore import Qt

sys.dont_write_bytecode = True


def tick():
    global hourpixmap, minpixmap, secpixmap
    global hourpixmap2, minpixmap2, secpixmap2
    global lastmin, lastday, lasttimestr
    global clockrect
    global datex, pdy

    if Config.DateLocale != "":
        try:
            locale.setlocale(locale.LC_TIME, Config.DateLocale)
        except:
            pass
    now = datetime.datetime.now()
    if Config.digital:
        timestr = Config.digitalformat.format(now)
        if Config.digitalformat.find("%I") > -1:
            if timestr[0] == '0':
                timestr = timestr[1:99]
        if lasttimestr != timestr:
            clockface.setText(timestr.lower())
        lasttimestr = timestr
    else:
        angle = now.second * 6
        ts = secpixmap.size()
        secpixmap2 = secpixmap.transformed(
            QtGui.QMatrix().scale(
                float(clockrect.width()) / ts.height(),
                float(clockrect.height()) / ts.height()
            ).rotate(angle),
            Qt.SmoothTransformation
        )
        sechand.setPixmap(secpixmap2)
        ts = secpixmap2.size()
        sechand.setGeometry(
            clockrect.center().x() - ts.width() / 2,
            clockrect.center().y() - ts.height() / 2,
            ts.width(),
            ts.height()
        )
        if now.minute != lastmin:
            lastmin = now.minute
            angle = now.minute * 6
            ts = minpixmap.size()
            minpixmap2 = minpixmap.transformed(
                QtGui.QMatrix().scale(
                    float(clockrect.width()) / ts.height(),
                    float(clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            minhand.setPixmap(minpixmap2)
            ts = minpixmap2.size()
            minhand.setGeometry(
                clockrect.center().x() - ts.width() / 2,
                clockrect.center().y() - ts.height() / 2,
                ts.width(),
                ts.height()
            )
            angle = ((now.hour % 12) + now.minute / 60.0) * 30.0
            ts = hourpixmap.size()
            hourpixmap2 = hourpixmap.transformed(
                QtGui.QMatrix().scale(
                    float(clockrect.width()) / ts.height(),
                    float(clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            hourhand.setPixmap(hourpixmap2)
            ts = hourpixmap2.size()
            hourhand.setGeometry(
                clockrect.center().x() - ts.width() / 2,
                clockrect.center().y() - ts.height() / 2,
                ts.width(),
                ts.height()
            )
    dy = "{0:%I:%M %p}".format(now)
    if dy != pdy:
        pdy = dy
    if now.day != lastday:
        lastday = now.day
        # date
        sup = 'th'
        if (now.day == 1 or now.day == 21 or now.day == 31):
            sup = 'st'
        if (now.day == 2 or now.day == 22):
            sup = 'nd'
        if (now.day == 3 or now.day == 23):
            sup = 'rd'
        if Config.DateLocale != "":
            sup = ""
        ds = "{0:%A, %B} {0.day}<sup>{1}</sup> {0.year}".format(now, sup)
        datex.setText(ds)


def qtstart():
    global ctimer

    ctimer = QtCore.QTimer()
    ctimer.timeout.connect(tick)
    ctimer.start(1000)


# needed for backwards compatibility
class Radar(QtGui.QLabel):
    pass


def realquit():
    QtGui.QApplication.exit(0)


def myquit(a=0, b=0):
    global ctimer
    ctimer.stop()
    QtCore.QTimer.singleShot(30, realquit)


def fixupframe(frame, onoff):
    for child in frame.children():
        if isinstance(child, Radar):
            if onoff:
                child.wxstart()
            else:
                child.wxstop()


def nextframe(plusminus):
    global frames, framep
    frames[framep].setVisible(False)
    fixupframe(frames[framep], False)
    framep += plusminus
    if framep >= len(frames):
        framep = 0
    if framep < 0:
        framep = len(frames) - 1
    frames[framep].setVisible(True)
    fixupframe(frames[framep], True)


# needed for backwards compatibility
class myMain(QtGui.QWidget):
    pass


configname = 'Config'

if len(sys.argv) > 1:
    configname = sys.argv[1]

if not os.path.isfile(configname + ".py"):
    print "Config file not found %s" % configname + ".py"
    exit(1)

Config = __import__(configname)

# define default values for new/optional config variables.

try:
    Config.metric
except AttributeError:
    Config.metric = 0

try:
    Config.weather_refresh
except AttributeError:
    Config.weather_refresh = 30   # minutes

try:
    Config.radar_refresh
except AttributeError:
    Config.radar_refresh = 10    # minutes

try:
    Config.fontattr
except AttributeError:
    Config.fontattr = ''

try:
    Config.dimcolor
except AttributeError:
    Config.dimcolor = QColor('#000000')
    Config.dimcolor.setAlpha(0)

try:
    Config.DateLocale
except AttributeError:
    Config.DateLocale = ''

try:
    Config.wind_degrees
except AttributeError:
    Config.wind_degrees = 0

try:
    Config.satellite
except AttributeError:
    Config.satellite = 0

try:
    Config.digital
except AttributeError:
    Config.digital = 0

try:
    Config.LPressure
except AttributeError:
    Config.wuLanguage = "EN"
    Config.LPressure = "Pressure "
    Config.LHumidity = "Humidity "
    Config.LWind = "Wind "
    Config.Lgusting = " gusting "
    Config.LFeelslike = "Feels like "
    Config.LPrecip1hr = " Precip 1hr:"
    Config.LToday = "Today: "
    Config.LSunRise = "Sun Rise:"
    Config.LSet = " Set: "
    Config.LMoonPhase = " Moon Phase:"
    Config.LInsideTemp = "Inside Temp "
    Config.LRain = " Rain: "
    Config.LSnow = " Snow: "


lastmin = -1
lastday = -1
pdy = ""
lasttimestr = ""
weatherplayer = None
lastkeytime = 0
lastapiget = time.time()

app = QtGui.QApplication(sys.argv)
desktop = app.desktop()
rec = desktop.screenGeometry()
height = rec.height()
width = rec.width()

signal.signal(signal.SIGINT, myquit)

w = myMain()
w.setWindowTitle(os.path.basename(__file__))

w.setStyleSheet("QWidget { background-color: black;}")

xscale = float(width) / 1440.0
yscale = float(height) / 900.0

frames = []
framep = 0

frame1 = QtGui.QFrame(w)
frame1.setObjectName("frame1")
frame1.setGeometry(0, 0, width, height)
frame1.setStyleSheet("#frame1 { background-color: black; border-image: url(" +
                     Config.background + ") 0 0 0 0 stretch stretch;}")
frames.append(frame1)

if not Config.digital:
    clockface = QtGui.QFrame(frame1)
    clockface.setObjectName("clockface")
    clockrect = QtCore.QRect(
        width / 2 - height * .4,
        height * .45 - height * .4,
        height * .8,
        height * .8)
    clockface.setGeometry(clockrect)
    clockface.setStyleSheet(
        "#clockface { background-color: transparent; border-image: url(" +
        Config.clockface +
        ") 0 0 0 0 stretch stretch;}")

    hourhand = QtGui.QLabel(frame1)
    hourhand.setObjectName("hourhand")
    hourhand.setStyleSheet("#hourhand { background-color: transparent; }")

    minhand = QtGui.QLabel(frame1)
    minhand.setObjectName("minhand")
    minhand.setStyleSheet("#minhand { background-color: transparent; }")

    sechand = QtGui.QLabel(frame1)
    sechand.setObjectName("sechand")
    sechand.setStyleSheet("#sechand { background-color: transparent; }")

    hourpixmap = QtGui.QPixmap(Config.hourhand)
    hourpixmap2 = QtGui.QPixmap(Config.hourhand)
    minpixmap = QtGui.QPixmap(Config.minhand)
    minpixmap2 = QtGui.QPixmap(Config.minhand)
    secpixmap = QtGui.QPixmap(Config.sechand)
    secpixmap2 = QtGui.QPixmap(Config.sechand)
else:
    clockface = QtGui.QLabel(frame1)
    clockface.setObjectName("clockface")
    clockrect = QtCore.QRect(
        width / 2 - height * .4,
        height * .45 - height * .4,
        height * .8,
        height * .8)
    clockface.setGeometry(clockrect)
    dcolor = QColor(Config.digitalcolor).darker(0).name()
    lcolor = QColor(Config.digitalcolor).lighter(120).name()
    clockface.setStyleSheet(
        "#clockface { background-color: transparent; font-family:sans-serif;" +
        " font-weight: light; color: " +
        lcolor +
        "; background-color: transparent; font-size: " +
        str(int(Config.digitalsize * xscale)) +
        "px; " +
        Config.fontattr +
        "}")
    clockface.setAlignment(Qt.AlignCenter)
    clockface.setGeometry(clockrect)

    glow = QtGui.QGraphicsDropShadowEffect()
    glow.setOffset(0)
    glow.setBlurRadius(50)
    glow.setColor(QColor(dcolor))
    clockface.setGraphicsEffect(glow)

datex = QtGui.QLabel(frame1)
datex.setObjectName("datex")
datex.setStyleSheet("#datex { font-family:sans-serif; color: " +
                    Config.textcolor +
                    "; background-color: transparent; font-size: " +
                    str(int(50 * xscale)) +
                    "px; " +
                    Config.fontattr +
                    "}")
datex.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datex.setGeometry(0, height / 1.15, width, 100)

glow = QtGui.QGraphicsDropShadowEffect()
glow.setOffset(0)
glow.setBlurRadius(50)
dcolor = QColor(Config.digitalcolor).darker(0).name()
glow.setColor(QColor(dcolor))
datex.setGraphicsEffect(glow)

manager = QtNetwork.QNetworkAccessManager()

stimer = QtCore.QTimer()
stimer.singleShot(10, qtstart)

w.show()
w.showFullScreen()

sys.exit(app.exec_())
