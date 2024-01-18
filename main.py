import sys
import datetime
from functools import partial

from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel,
                               QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                               QScrollArea, QDialog, QDialogButtonBox, QLineEdit,
                               QMessageBox, QDateTimeEdit)
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont

class AddNewTaskDialog(QDialog):
    def __init__(self, tNow):
        super().__init__()
        self.setWindowTitle('Add New Task')

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        titleLabel = QLabel('Title:')
        self.layout.addWidget(titleLabel)
        self.title = QLineEdit()
        self.layout.addWidget(self.title)

        descriptionLabel = QLabel("Description:")
        self.layout.addWidget(descriptionLabel)
        self.description = QLineEdit()
        self.layout.addWidget(self.description)

        endTimeLabel = QLabel('End time:')
        self.layout.addWidget(endTimeLabel)

        self.endTime = QDateTimeEdit()
        date_format = "%Y-%m-%d %H:%M:%S"
        now = datetime.datetime.strptime(tNow, date_format)
        self.endTime.setDateTime(now)
        self.layout.addWidget(self.endTime)

        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def getData(self):
        qdt = self.endTime.dateTime()
        dt = qdt.toPython()
        return {"title": self.title.text(), "description": self.description.text(), "endTime": dt}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # settings
        self.setWindowTitle('To Do List')
        self.setMinimumSize(QSize(1000,500))
        # self.setMaximumSize(QSize(1000,500))

        # mainLayout
        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        # header
        header = QLabel("To Do List")
        headerFont = QFont()
        headerFont.setPointSize(36)
        headerFont.setBold(True)
        header.setFont(headerFont)
        header.setAlignment(Qt.AlignCenter)

        header.setStyleSheet("border: 1px solid black;")

        main_layout.addWidget(header,10)

        # tasks
        tasks = QVBoxLayout()

        tasks_widget = QWidget()
        tasks_widget.setLayout(tasks)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(tasks_widget)

        # sidebar
        sidebar = QVBoxLayout()
        addTaskButton = QPushButton("Add new task")
        addTaskButton.clicked.connect(partial(self.addNewTask, tasks))
        sidebar.addWidget(addTaskButton, alignment=Qt.AlignCenter)

        clock = QLabel("")
        clockFont = QFont()
        clockFont.setPointSize(16)
        clock.setFont(clockFont)
        timer = QTimer(self)
        timer.timeout.connect(partial(self.updateTime, clock))
        timer.start(1000)
        self.updateTime(clock)
        sidebar.addWidget(clock, alignment=Qt.AlignBottom)

        # widget
        main_layout.addStretch(1)
        main_layout.addLayout(content_layout, 90)

        content_layout.addLayout(sidebar, 20)
        content_layout.addWidget(scroll_area, 80)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

    def timeNow(self):
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        return time

    def updateTime(self, label):
        label.setText(self.timeNow())

    def addNewTask(self, tasks):
        dialog = AddNewTaskDialog(self.timeNow())
        if dialog.exec():
            task = Task(dialog.getData()["title"], dialog.getData()["description"], self.timeNow(), dialog.getData()['endTime'])
            tasks.addWidget(task, alignment=Qt.AlignTop)
        else:
            print('adding new task canceled')




class Task(QWidget):
    def __init__(self, t, d, startT, endT):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel(str(t))
        titleFont = QFont()
        titleFont.setBold(True)
        title.setFont(titleFont)
        description = QLabel(str(d))
        time = QLabel("Start time: " + str(startT) + " | End time: " + endT.strftime("%d-%m-%Y %H:%M:%S"))
        timeFont = QFont()
        timeFont.setItalic(True)
        time.setFont(timeFont)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(time)

        self.setMaximumHeight(100)
        self.setMinimumHeight(100)

        self.setLayout(layout)


app = QApplication()
window = MainWindow()
window.show()
app.exec()