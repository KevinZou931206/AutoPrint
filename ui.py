"""
UI界面程序
"""
import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
                            QPushButton, QTimeEdit, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QTime, QThread, pyqtSignal
from datetime import datetime
import time

from logger import logger
from main import main as run_task

class LogHandler:
    """日志处理器，用于将日志输出到UI"""
    def __init__(self, signal):
        self.signal = signal

    def write(self, text):
        self.signal.emit(text)

class WorkerThread(QThread):
    """工作线程，用于运行自动化任务"""
    finished = pyqtSignal()
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                run_task()
                # 等待10分钟
                for i in range(10):
                    if not self.is_running:
                        break
                    time.sleep(60)
            except Exception as e:
                self.log_signal.emit(f"任务执行出错: {str(e)}")
                time.sleep(60)

    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.load_settings()
        
        # 设置日志信号
        from logger import set_ui_signal
        set_ui_signal(self.log_signal)

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('自动化打单配货程序')
        self.setMinimumSize(800, 600)

        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 登录信息组
        login_group = QGroupBox("登录信息")
        login_layout = QVBoxLayout()
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # 记住密码
        self.remember_checkbox = QCheckBox("记住密码")
        
        login_layout.addLayout(username_layout)
        login_layout.addLayout(password_layout)
        login_layout.addWidget(self.remember_checkbox)
        login_group.setLayout(login_layout)

        # 时间设置组
        time_group = QGroupBox("时间设置")
        time_layout = QHBoxLayout()
        
        # 开始时间
        start_layout = QVBoxLayout()
        start_label = QLabel("开始时间:")
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(7, 30))
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_time)
        
        # 中间时间
        middle_layout = QVBoxLayout()
        middle_label = QLabel("中间时间:")
        self.middle_time = QTimeEdit()
        self.middle_time.setTime(QTime(17, 0))
        middle_layout.addWidget(middle_label)
        middle_layout.addWidget(self.middle_time)
        
        # 结束时间
        end_layout = QVBoxLayout()
        end_label = QLabel("结束时间:")
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(17, 30))
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_time)
        
        time_layout.addLayout(start_layout)
        time_layout.addLayout(middle_layout)
        time_layout.addLayout(end_layout)
        time_group.setLayout(time_layout)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("启动程序")
        self.stop_button = QPushButton("终止程序")
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_program)
        self.stop_button.clicked.connect(self.stop_program)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        # 日志显示
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)

        # 添加所有组件到主布局
        layout.addWidget(login_group)
        layout.addWidget(time_group)
        layout.addLayout(button_layout)
        layout.addWidget(log_group)

        # 连接日志信号
        self.log_signal.connect(self.update_log)

    def load_settings(self):
        """加载保存的设置"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.username_input.setText(settings.get('username', ''))
                    if settings.get('remember_password', False):
                        self.password_input.setText(settings.get('password', ''))
                        self.remember_checkbox.setChecked(True)
                    
                    # 加载时间设置
                    start = settings.get('start_time', '07:30').split(':')
                    middle = settings.get('middle_time', '17:00').split(':')
                    end = settings.get('end_time', '17:30').split(':')
                    
                    self.start_time.setTime(QTime(int(start[0]), int(start[1])))
                    self.middle_time.setTime(QTime(int(middle[0]), int(middle[1])))
                    self.end_time.setTime(QTime(int(end[0]), int(end[1])))
        except Exception as e:
            self.log_signal.emit(f"加载设置失败: {str(e)}")

    def save_settings(self):
        """保存设置"""
        try:
            settings = {
                'username': self.username_input.text(),
                'remember_password': self.remember_checkbox.isChecked(),
                'start_time': self.start_time.time().toString('HH:mm'),
                'middle_time': self.middle_time.time().toString('HH:mm'),
                'end_time': self.end_time.time().toString('HH:mm')
            }
            
            if self.remember_checkbox.isChecked():
                settings['password'] = self.password_input.text()
            
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            self.log_signal.emit(f"保存设置失败: {str(e)}")

    def start_program(self):
        """启动程序"""
        # 保存设置
        self.save_settings()
        
        # 设置环境变量
        os.environ['USERNAME'] = self.username_input.text()
        os.environ['PASSWORD'] = self.password_input.text()
        
        # 禁用输入和启动按钮
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.remember_checkbox.setEnabled(False)
        self.start_time.setEnabled(False)
        self.middle_time.setEnabled(False)
        self.end_time.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # 启动工作线程
        self.worker = WorkerThread()
        self.worker.log_signal.connect(self.update_log)
        self.worker.start()
        
        self.log_signal.emit("程序已启动")

    def stop_program(self):
        """终止程序"""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
        
        # 启用输入和启动按钮
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.remember_checkbox.setEnabled(True)
        self.start_time.setEnabled(True)
        self.middle_time.setEnabled(True)
        self.end_time.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.log_signal.emit("程序已终止")

    def update_log(self, text):
        """更新日志显示"""
        self.log_text.append(text)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.stop_program()
        self.save_settings()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 