import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import time
import math
from os import path

#EXPERIMENT CONFIGURATION
    #GENERAL
FONT_SIZE = 17                          #THE SIZE OF FONT IN PIXELS
    #MOVING DOT
FILENAME0 = "video_1_audio.m4a"         #FILENAME OF THE DOT AUDIO
DOT_RADIUS = 40                         #THE RADIUS OF THE DOT IN PIXELS
FREQUENCY = 1.2                         #THE NUMBER OF FULL PERIODS PER SECONDS
EXP_TIME = 120                          #THE DURATION OF THE MOVING DOT EXPERIMENT IN SECONDS
UPDATE_TIME = 5                         #THE TIME BETWEEN EVERY UPDATE IN MILLISECONDS
    #VIDEO
FILENAME1 = 'video_part1.mp4'           #FILENAME OF THE WAR VIDEO
FILENAME2 = 'video_part2.mp4'           #FILENAME OF THE FUNNY VIDEO


class Experiment(QMainWindow):
    '''main experiment window'''

    def __init__(self, scenario):
        super().__init__()
        self.scenario = scenario
        self.next_in_scenario(True)


    def next_in_scenario(self, first = False):
        new_active, parameter = self.scenario[0]
        del self.scenario[0]
        if new_active == None:
            info_message(QMessageBox.Information, 'The end of the experiment', 'This is the end of the experiment.\nThank you for your participation.')
            self.close()
        else:
            if parameter == None:
                active_window = new_active()
            else:
                active_window = new_active(parameter)
            self.active_window = active_window

            self.layout = QVBoxLayout()                                         #creating main layout to place inside widget
            self.layout.addWidget(self.active_window)
            self.controlLayout = QHBoxLayout()
            if first:
                self.start_button = QPushButton('Start', self)                  #creating the start button
                self.start_button.clicked.connect(self.main_start)              #configuring the button
                self.controlLayout.addWidget(self.start_button)                 #adding button widget
            self.exit_button = QPushButton('Exit the experiment', self)         #creating the exit button
            self.exit_button.clicked.connect(active_window.exit_confirmation)   #configuring the button
            self.controlLayout.addWidget(self.exit_button)                      #adding button widget
            self.layout.addLayout(self.controlLayout)                           #adding layout

            self.main_window = QWidget()                                        #creating a widget for window contents
            self.main_window.setLayout(self.layout)                             #setting the layout
            self.setCentralWidget(self.main_window)                             #setting the widget to be the main window's central widget
            self.showFullScreen()
            if not first:
                self.active_window.start()


    def main_start(self):
        '''ask for ID, check if it's good, return it'''
        inputWindow = QWidget()
        while True:
            new_id, okPressed = QInputDialog().getText(inputWindow, 'User identification', 'Please enter your ID:', QLineEdit.Normal, 'Type here')
            if okPressed:
                if ID_checker(new_id): break
            else:
                self.active_window.exit_confirmation()
        experiment.sub_id = new_id
        experiment.next_in_scenario()


class StartWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        self.width = SCREEN_WIDTH


    def exit_confirmation(self):                                #asking confirmation to stop the
        returnValue = exit_question_message()
        if returnValue == QMessageBox.Yes:
            info_message(QMessageBox.Information, 'Experiment termination', 'The experiment has been stopped by the user')
            quit()


class DotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateValues)
        self.x = (SCREEN_WIDTH - DOT_RADIUS) / 2
        self.y = (SCREEN_HEIGHT) / 2 - DOT_RADIUS

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

        if not path.exists(FILENAME0):
            print("\nFile '{}' doesn't exist!".format(FILENAME0))
            quit()
        self.audio = QMediaPlayer(None)
        self.audio.setMedia(QMediaContent(QUrl.fromLocalFile(FILENAME0)))


    def start(self):
        info_message(QMessageBox.Information, 'Instruction', 'In this part of the experiment, you will see a red dot moving on a black screen. You need to follow the red dot with your eyes without moving your head.\n\nNote: If you want to exit the experiment before the end, click the "Exit the experiment" buttom at the bottom of the screen.')
        self.audio.play()
        self.start_time = time.time()
        self.update_timer.start(UPDATE_TIME)


    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(QPen(Qt.red, 0, Qt.SolidLine))
        qp.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        qp.drawEllipse(self.x, self.y, DOT_RADIUS, DOT_RADIUS)


    def updateValues(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time < EXP_TIME:
            self.x = DOT_RADIUS + (SCREEN_WIDTH - 3 * DOT_RADIUS) / 2 * ( 1 - math.sin(6.28318530718 * FREQUENCY * elapsed_time) )
            self.update()
        else:
            self.end_of_dot()


    def exit_confirmation(self):                    #asking confirmation to stop the simulation
        self.audio.pause()
        self.update_timer.stop()
        waisted_time_start = time.time()
        returnValue = exit_question_message()
        if returnValue == QMessageBox.Yes:
            info_message(QMessageBox.Information, 'Experiment termination', 'The experiment has been stopped by the user')
            quit()
        else:
            self.update_timer.start(UPDATE_TIME)
            self.start_time += time.time() - waisted_time_start
            self.audio.play()


    def end_of_dot(self):                            #the end of the simulation
        self.update_timer.stop()
        self.audio.pause()
        info_message(QMessageBox.Information, 'The end of the simulation', 'The simulation has finished')
        experiment.next_in_scenario()


class VideoWindow(QVideoWidget):
    def __init__(self, filename):
        super().__init__()

        if not path.exists(filename):
            print("\nFile '{}' doesn't exist!".format(filename))
            quit()
        self.width = SCREEN_WIDTH
        self.filename = filename
        self.video = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video.setVideoOutput(self)                                         #setting the video output
        self.video.mediaStatusChanged.connect(self.end_of_video)                #setting a signal of the video end
        self.video.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))        #openning the file
        self.video.play()
        self.video.pause()


    def start(self):
        info_message(QMessageBox.Information, 'Instruction', 'In this part of the experiment, you will need to watch a video from the beginning till the end.\n\nNote: If you want to exit the experiment before the end, click the "Exit the experiment" buttom at the bottom of the screen.')
        self.video.play()


    def exit_confirmation(self):                                #asking confirmation to stop the video
        self.video.pause()
        returnValue = exit_question_message()
        if returnValue == QMessageBox.Yes:
            info_message(QMessageBox.Information, 'Experiment termination', 'The experiment has been stopped by the user')
            quit()
        else:
            self.video.play()


    def end_of_video(self, status):                             #responding to the end signal
        if status == self.video.EndOfMedia:
            info_message(QMessageBox.Information, 'The end of the video', 'The video has finished')
            if self.filename == FILENAME1:
                a = self.ask_A()
                if a != '3':
                    info_message(QMessageBox.Information, 'The end of the experiment', 'This is the end of the experiment.\nThank you for your participation.')
                    quit()
            experiment.next_in_scenario()


    def ask_A(self):
        '''ask how many A'''
        while True:             #Doesn't allow to close the window
            items = ('0', '1', '2', '3', '4', '5')
            item, okPressed = QInputDialog().getItem(self, 'Question','How many letters A have you seen?\nThe number of A:', items, 0, False)
            if okPressed and item:
                return item


def dark_theme(app):
    '''setting dark theme for app'''
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    #app.setStyleSheet("* {font-size: " + str(FONT_SIZE) + "px}\n")      #setting text size

def ask_scenario(scenario_window):
    '''ask how many A'''
    while True:             #Doesn't allow to close the window
        items = ('1', '2', '3', '4')
        item, okPressed = QInputDialog().getItem(scenario_window, 'Setup','Choose the scenario', items, 0, False)
        if okPressed and item:
            return item


def assign_scenario():
    '''return the number of the scenario'''
    scenario_window = QMainWindow()
    scenario = int(ask_scenario(scenario_window))
    if scenario == 1:
        return 1, [(StartWindow, None), (DotWindow, None), (VideoWindow, FILENAME1), (DotWindow, None), (VideoWindow, FILENAME2), (DotWindow, None), (None, None)]
    elif scenario == 2:
        return 2, [(StartWindow, None), (VideoWindow, FILENAME1), (VideoWindow, FILENAME2), (None, None)]
    elif scenario == 3:
        return 3, [(StartWindow, None), (DotWindow, None), (VideoWindow, FILENAME1), (DotWindow, None), (None, None)]
    elif scenario == 4:
        return 4, [(StartWindow, None), (DotWindow, None), (VideoWindow, FILENAME2), (DotWindow, None), (None, None)]
    else:
        return 1, [(StartWindow, None), (DotWindow, None), (VideoWindow, FILENAME1), (DotWindow, None), (VideoWindow, FILENAME2), (DotWindow, None), (None, None)]


def info_message(type, title, text):
    '''qmessage showing information'''
    msgBox = QMessageBox()
    msgBox.setIcon(type)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()


def exit_question_message():
    '''ask the user about terminating the program and return the answer'''
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Warning)
    msgBox.setWindowTitle('Experiment termination')
    msgBox.setText('Do you want to stop the experiment?')
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    msgBox.setDefaultButton(QMessageBox.Cancel)
    return msgBox.exec_()


def ID_checker(id_to_check):
    '''check that id is 3 or 4 digits, numerical and hasn't been used'''
    if len(id_to_check) not in [3, 4] or not id_to_check.isdigit():
        info_message(QMessageBox.Warning, 'Wrong ID', 'Incorrect ID input!')
        return False
    else:
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_theme(app)
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    SCREEN_WIDTH = rect.width()
    SCREEN_HEIGHT = rect.height()
    num, scenario = assign_scenario()

    experiment = Experiment(scenario)
    app.exec_()
