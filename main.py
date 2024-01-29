import sys
import sqlite3
import datetime
from functools import partial

from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel,
                               QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                               QScrollArea, QDialog, QDialogButtonBox, QLineEdit,
                               QMessageBox, QDateTimeEdit)
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont, QPalette

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
        addTaskButton.setStyleSheet("padding: 10px;")
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

        timertask = QTimer(self)
        timertask.timeout.connect(partial(self.loadTasks, tasks))
        timertask.start(1000)
        self.loadTasks(tasks)

    def timeNow(self):
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        return time

    def updateTime(self, label):
        label.setText(self.timeNow())

    def addNewTask(self, tasks):
        dialog = AddNewTaskDialog(self.timeNow())
        if dialog.exec():
            t = dialog.getData()["title"]
            d = dialog.getData()["description"]
            end = dialog.getData()['endTime']
            error = QMessageBox()
            error.setWindowTitle("Error")

            if(t == ""):
                error.setText("Title cannot be empty!")
                error.exec()
            elif(end < datetime.datetime.now()):
                error.setText("End time must be in the future!")
                error.exec()
            else:
                start = datetime.datetime.strptime(self.timeNow(), "%Y-%m-%d %H:%M:%S")
                task = Task(t,d, start, end, 0, 1)
                task.addToDb()
                # tasks.addWidget(task, alignment=Qt.AlignTop)
                self.loadTasks(tasks)
        else:
            print('adding new task canceled')

    def loadTasks(self, tasks):
        conn = sqlite3.connect('data')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks ORDER BY end_time ASC")
        tasksList = cursor.fetchall()

        while tasks.count():
            item = tasks.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for t in tasksList:
            start = datetime.datetime.strptime(t[3], "%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.strptime(t[4], "%Y-%m-%d %H:%M:%S")
            task = Task(t[1], t[2], start, end, t[0], t[5])
            tasks.addWidget(task, alignment=Qt.AlignTop)

        cursor.close()
        conn.close()

class Task(QWidget):
    def __init__(self, t, d, startT, endT, id_, act):
        super().__init__()

        self.id = id_

        layout = QVBoxLayout()

        now = datetime.datetime.now()

        self.active = act

        titleLbl = QLabel(str(t))
        titleFont = QFont()
        titleFont.setBold(True)
        titleLbl.setFont(titleFont)
        if(endT >= now and act == 1):
            titleLbl.setStyleSheet("color: orange;")
        elif(endT < now and act == 1):
            titleLbl.setStyleSheet("color: red;")
        elif(act == 0):
            titleLbl.setStyleSheet("color: green;")
        descriptioLbl = QLabel(str(d))
        self.startTime = startT
        self.endTime = endT
        self.title = str(t)
        self.description = str(d)

        time = QLabel("Start time: " + startT.strftime("%Y-%m-%d %H:%M:%S") + " | End time: " + endT.strftime("%Y-%m-%d %H:%M:%S"))
        timeFont = QFont()
        timeFont.setItalic(True)
        time.setFont(timeFont)

        layout.addWidget(titleLbl)
        layout.addWidget(descriptioLbl)
        layout.addWidget(time)

        delBtn = QPushButton("Delete")
        delBtn.clicked.connect(self.delFromDb)
        delBtn.setFixedSize(100, 25)
        layout.addWidget(delBtn)

        actBtn = QPushButton("End task")
        actBtn.clicked.connect(self.endTask)
        actBtn.setFixedSize(100, 25)
        layout.addWidget(actBtn)

        bottom = QLabel("")
        lineFont = QFont()
        lineFont.setPointSize(1)
        bottom.setFont(lineFont)
        bottom.setStyleSheet("background-color: black;")
        layout.addWidget(bottom)

        self.setMaximumHeight(150)
        self.setMinimumHeight(150)

        self.setLayout(layout)

    def addToDb(self):
        conn = sqlite3.connect('data')
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO tasks (title, description, start_time, end_time) values (?, ?, ?, ?)
        ''', (self.title, self.description, self.startTime, self.endTime))

        conn.commit()

        cursor.close()
        conn.close()

    def delFromDb(self):
        confirm = QMessageBox()
        confirm.setWindowTitle("Delete")
        confirm.setText("Are you sure?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.setDefaultButton(QMessageBox.No)
        result = confirm.exec()

        if (result == QMessageBox.Yes):
            conn = sqlite3.connect('data')
            cursor = conn.cursor()

            cursor.execute('DELETE FROM tasks WHERE id = ?', (self.id,))

            conn.commit()

            cursor.close()
            conn.close()

    def endTask(self):
        if(self.active == 1):
            confirm = QMessageBox()
            confirm.setWindowTitle("End")
            confirm.setText("Are you sure?")
            confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm.setDefaultButton(QMessageBox.No)
            result = confirm.exec()

            if(result == QMessageBox.Yes):
                conn = sqlite3.connect('data')
                cursor = conn.cursor()

                now = datetime.datetime.now()
                time = now.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('UPDATE tasks SET end_time = ? WHERE id = ?', (time,self.id))
                cursor.execute('UPDATE tasks SET active = ? WHERE id = ?', (0,self.id))

                conn.commit()

                cursor.close()
                conn.close()


app = QApplication()
window = MainWindow()
window.show()
app.exec()