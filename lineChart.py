#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited
## Copyright (C) 2012 Digia Plc
## All rights reserved.
##
## This file is part of the PyQtChart examples.
##
## $QT_BEGIN_LICENSE$
## Licensees holding valid Qt Commercial licenses may use this file in
## accordance with the Qt Commercial License Agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and Digia.
## $QT_END_LICENSE$
##
#############################################################################


import random
import math
import time
import threading

from PyQt5.QtChart import (QAreaSeries, QBarSet, QChart, QChartView,
        QLineSeries, QPieSeries, QScatterSeries, QSplineSeries,
        QStackedBarSeries, QValueAxis)
from PyQt5.QtCore import pyqtSlot, QPoint, QPointF, Qt, QEvent, QRectF, QTimer
from PyQt5.QtGui import QColor, QPainter, QPalette
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QGridLayout, QHBoxLayout,
        QLabel, QSizePolicy, QWidget)

class TestChart(QChart):
    def __init__(self, parent=None):
        super(TestChart, self).__init__(parent)
        self.xRange = 800
        self.sampleRate = 5
        self.counter = 0
        self.seriesList = []
        self.legend().show()

        self.axisX = QValueAxis()
        self.axisX.setRange(0, self.xRange)
        self.addAxis(self.axisX, Qt.AlignBottom)
        # self.setAxisX(self.axisX, series)

        self.axisY = QValueAxis()
        self.axisY.setRange(-1, 1)
        self.addAxis(self.axisY, Qt.AlignLeft)
        # self.setAxisY(self.axisY, series)

        for i in range(24):
            series = QLineSeries()
            series.setName("Series" + str(i))
            series.setUseOpenGL(True)
            self.addSeries(series)
            self.seriesList.append(series)
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)


    def handleUpdate(self):
        for channel in range(24):
            # print(channel)
            if (self.counter < self.xRange):
                for i in range(self.sampleRate):
                    self.seriesList[channel].append(self.counter+i, math.sin((self.counter+channel*5+i)*math.pi/180))
            else:
                points = self.seriesList[channel].pointsVector()
                for i in range(len(points) - self.sampleRate):
                    points[i].setY(points[i + self.sampleRate].y())
                for i in range(self.sampleRate):
                    points[len(points) - (self.sampleRate - i)].setY(math.sin((self.counter+channel*5+i)*math.pi/180))
                self.seriesList[channel].replace(points)
        self.counter += self.sampleRate

class ThemeWidget(QWidget):

    def __init__(self, parent=None):
        super(ThemeWidget, self).__init__(parent)

        self.m_charts = []
        self.timer = QTimer()
        # self.timer.setInterval(25)
        # self.timer.start()
        self.m_listCount = 3
        self.m_valueMax = 10
        self.m_valueCount = 7
        self.m_dataTable = self.generateRandomData(self.m_listCount,
                self.m_valueMax, self.m_valueCount)
        self.m_themeComboBox = self.createThemeBox()
        self.m_antialiasCheckBox = QCheckBox("Anti-aliasing")
        self.m_animatedComboBox = self.createAnimationBox()
        self.m_legendComboBox = self.createLegendBox()

        self.connectSignals()

        # Create the layout.
        baseLayout = QGridLayout()
        settingsLayout = QHBoxLayout()
        settingsLayout.addWidget(QLabel("Theme:"))
        settingsLayout.addWidget(self.m_themeComboBox)
        settingsLayout.addWidget(QLabel("Animation:"))
        settingsLayout.addWidget(self.m_animatedComboBox)
        settingsLayout.addWidget(QLabel("Legend:"))
        settingsLayout.addWidget(self.m_legendComboBox)
        settingsLayout.addWidget(self.m_antialiasCheckBox)
        settingsLayout.addStretch()
        baseLayout.addLayout(settingsLayout, 0, 0, 1, 3)

        # Create the charts.
        # chartView = QChartView(self.createLineChart())
        self.myChart = TestChart()
        chartView = QChartView(self.myChart)

        baseLayout.addWidget(chartView)
        self.m_charts.append(chartView)

        self.setLayout(baseLayout)

        # Set the defaults.
        self.m_antialiasCheckBox.setChecked(True)
        self.updateUI()

        receiveProcess = threading.Thread(target=self.test)
        receiveProcess.setDaemon(True)
        receiveProcess.start()

    def test(self):
        while True:
            self.onTimerOut()
            time.sleep(0.025)

    def connectSignals(self):
        self.m_themeComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_antialiasCheckBox.toggled.connect(self.updateUI)
        self.m_animatedComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_legendComboBox.currentIndexChanged.connect(self.updateUI)
        self.timer.timeout.connect(self.onTimerOut)

    def onTimerOut(self):
        # print('time out')
        start = time.clock()
        self.myChart.handleUpdate()
        QApplication.processEvents()
        elapsed = (time.clock() - start)
        print("Time used: %.3fs" % elapsed)

    def generateRandomData(self, listCount, valueMax, valueCount):
        random.seed()

        dataTable = []

        for i in range(listCount):
            dataList = []
            yValue = 0.0
            f_valueCount = float(valueCount)

            for j in range(valueCount):
                yValue += random.uniform(0, valueMax) / f_valueCount
                value = QPointF(
                        j + random.random() * self.m_valueMax / f_valueCount,
                        yValue)
                label = "Slice " + str(i) + ":" + str(j)
                dataList.append((value, label))

            dataTable.append(dataList)

        return dataTable

    def createThemeBox(self):
        themeComboBox = QComboBox()

        themeComboBox.addItem("Light", QChart.ChartThemeLight)
        themeComboBox.addItem("Blue Cerulean", QChart.ChartThemeBlueCerulean)
        themeComboBox.addItem("Dark", QChart.ChartThemeDark)
        themeComboBox.addItem("Brown Sand", QChart.ChartThemeBrownSand)
        themeComboBox.addItem("Blue NCS", QChart.ChartThemeBlueNcs)
        themeComboBox.addItem("High Contrast", QChart.ChartThemeHighContrast)
        themeComboBox.addItem("Blue Icy", QChart.ChartThemeBlueIcy)

        return themeComboBox

    def createAnimationBox(self):
        animationComboBox = QComboBox()

        animationComboBox.addItem("No Animations", QChart.NoAnimation)
        animationComboBox.addItem("GridAxis Animations", QChart.GridAxisAnimations)
        animationComboBox.addItem("Series Animations", QChart.SeriesAnimations)
        animationComboBox.addItem("All Animations", QChart.AllAnimations)

        return animationComboBox

    def createLegendBox(self):
        legendComboBox = QComboBox()

        legendComboBox.addItem("No Legend ", 0)
        legendComboBox.addItem("Legend Top", Qt.AlignTop)
        legendComboBox.addItem("Legend Bottom", Qt.AlignBottom)
        legendComboBox.addItem("Legend Left", Qt.AlignLeft)
        legendComboBox.addItem("Legend Right", Qt.AlignRight)

        return legendComboBox

    def createLineChart(self):
        chart = QChart()
        chart.setTitle("Line chart")

        for i, data_list in enumerate(self.m_dataTable):
            series = QLineSeries(chart)
            for value, _ in data_list:
                series.append(value)

            series.setName("Series " + str(i))
            series.setUseOpenGL(True)
            chart.addSeries(series)

        chart.createDefaultAxes()

        return chart

    @pyqtSlot()
    def updateUI(self):
        theme = self.m_themeComboBox.itemData(
                self.m_themeComboBox.currentIndex())

        if self.m_charts[0].chart().theme() != theme:
            for chartView in self.m_charts:
                chartView.chart().setTheme(theme)

            pal = self.window().palette()

            if theme == QChart.ChartThemeLight:
                pal.setColor(QPalette.Window, QColor(0xf0f0f0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif theme == QChart.ChartThemeDark:
                pal.setColor(QPalette.Window, QColor(0x121218))
                pal.setColor(QPalette.WindowText, QColor(0xd6d6d6))
            elif theme == QChart.ChartThemeBlueCerulean:
                pal.setColor(QPalette.Window, QColor(0x40434a))
                pal.setColor(QPalette.WindowText, QColor(0xd6d6d6))
            elif theme == QChart.ChartThemeBrownSand:
                pal.setColor(QPalette.Window, QColor(0x9e8965))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif theme == QChart.ChartThemeBlueNcs:
                pal.setColor(QPalette.Window, QColor(0x018bba))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif theme == QChart.ChartThemeHighContrast:
                pal.setColor(QPalette.Window, QColor(0xffab03))
                pal.setColor(QPalette.WindowText, QColor(0x181818))
            elif theme == QChart.ChartThemeBlueIcy:
                pal.setColor(QPalette.Window, QColor(0xcee7f0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            else:
                pal.setColor(QPalette.Window, QColor(0xf0f0f0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))

            self.window().setPalette(pal)

        checked = self.m_antialiasCheckBox.isChecked()
        for chartView in self.m_charts:
            chartView.setRenderHint(QPainter.Antialiasing, checked)

        options = QChart.AnimationOptions(
                self.m_animatedComboBox.itemData(
                        self.m_animatedComboBox.currentIndex()))

        if self.m_charts[0].chart().animationOptions() != options:
            for chartView in self.m_charts:
                chartView.chart().setAnimationOptions(options)

        alignment = self.m_legendComboBox.itemData(
                self.m_legendComboBox.currentIndex())

        for chartView in self.m_charts:
            legend = chartView.chart().legend()

            if alignment == 0:
                legend.hide()
            else:
                legend.setAlignment(Qt.Alignment(alignment))
                legend.show()




if __name__ == '__main__':

    import sys

    from PyQt5.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    window = QMainWindow()
    widget = ThemeWidget()
    window.setCentralWidget(widget)
    window.resize(900, 600)
    window.show()

    sys.exit(app.exec_())
