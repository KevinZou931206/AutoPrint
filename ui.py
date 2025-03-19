"""
UI界面程序
"""
import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QCheckBox, 
                            QPushButton, QTimeEdit, QTextEdit, QGroupBox,
                            QTabWidget, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QTime, QThread, pyqtSignal
from datetime import datetime, time as datetime_time
import time as time_module

from logger import logger, set_ui_signal
# 防止循环导入，需要的时候再导入
# import main
from config import time_config
from mail_sender import email_sender
from version import VERSION, VERSION_DATE, VERSION_INFO

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

    def __init__(self, interval=10):
        super().__init__()
        self.is_running = True
        self.interval = interval  # 任务间隔时间，单位为分钟

    def run(self):
        # 导入放在函数内部，避免循环导入
        import main as main_module
        
        while self.is_running:
            try:
                main_module.main()
                # 等待设定的间隔时间
                logger.info(f"任务执行完成，等待 {self.interval} 分钟后重新执行")
                for i in range(self.interval):
                    if not self.is_running:
                        break
                    time_module.sleep(60)
            except Exception as e:
                # 使用logger记录错误，而不是直接使用信号
                logger.error(f"任务执行出错: {str(e)}")
                time_module.sleep(60)

    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    """主窗口类"""
    log_signal = pyqtSignal(str)
    # 添加新信号用于异常处理对话框
    error_dialog_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"自动化打单配货程序 v{VERSION}")
        self.setGeometry(100, 100, 800, 600)
        self.worker_thread = None
        
        # 设置日志信号
        set_ui_signal(self.log_signal)
        
        # 创建中心组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建标签页
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # 主配置页面
        main_tab = QWidget()
        tabs.addTab(main_tab, "主配置")
        self._setup_main_tab(main_tab)
        
        # 邮件配置页面
        mail_tab = QWidget()
        tabs.addTab(mail_tab, "邮件配置")
        self._setup_mail_tab(mail_tab)
        
        # 日志页面
        log_tab = QWidget()
        tabs.addTab(log_tab, "运行日志")
        self._setup_log_tab(log_tab)
        
        # 关于页面
        about_tab = QWidget()
        tabs.addTab(about_tab, "关于")
        self._setup_about_tab(about_tab)
        
        # 加载设置
        self.load_settings()
        
        # 连接异常处理信号
        self.error_dialog_signal.connect(self.show_error_dialog)
        
    def _setup_main_tab(self, tab):
        """设置主配置页面"""
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 登录信息组
        login_group = QGroupBox("登录信息")
        login_layout = QVBoxLayout()
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("账号:")
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
        middle_label = QLabel("截单时间:")
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

        # 添加任务间隔时间设置
        interval_group = QGroupBox("任务间隔设置")
        interval_layout = QHBoxLayout()
        interval_group.setLayout(interval_layout)
        
        interval_label = QLabel("任务执行间隔(分钟):")
        self.task_interval_spinbox = QSpinBox()
        self.task_interval_spinbox.setRange(1, 60)  # 允许设置1到60分钟的间隔
        self.task_interval_spinbox.setValue(10)     # 默认为10分钟
        self.task_interval_spinbox.setSingleStep(1)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.task_interval_spinbox)

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
        layout.addWidget(interval_group)
        layout.addLayout(button_layout)
        layout.addWidget(log_group)

        # 连接日志信号
        self.log_signal.connect(self.update_log)

    def _setup_mail_tab(self, tab):
        """设置邮件配置页面"""
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 邮件服务器设置
        mail_group = QGroupBox("邮件服务器设置")
        mail_layout = QVBoxLayout()
        mail_group.setLayout(mail_layout)
        layout.addWidget(mail_group)
        
        # SMTP服务器
        smtp_layout = QHBoxLayout()
        smtp_label = QLabel("SMTP服务器:")
        self.smtp_server_input = QLineEdit()
        self.smtp_server_input.setPlaceholderText("例如: smtp.qq.com")
        smtp_layout.addWidget(smtp_label)
        smtp_layout.addWidget(self.smtp_server_input)
        mail_layout.addLayout(smtp_layout)
        
        # SMTP端口
        port_layout = QHBoxLayout()
        port_label = QLabel("SMTP端口:")
        self.smtp_port_input = QSpinBox()
        self.smtp_port_input.setRange(0, 65535)
        self.smtp_port_input.setValue(465)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.smtp_port_input)
        mail_layout.addLayout(port_layout)
        
        # 发件人邮箱
        sender_layout = QHBoxLayout()
        sender_label = QLabel("发件人邮箱:")
        self.sender_email_input = QLineEdit()
        self.sender_email_input.setPlaceholderText("例如: your_email@qq.com")
        sender_layout.addWidget(sender_label)
        sender_layout.addWidget(self.sender_email_input)
        mail_layout.addLayout(sender_layout)
        
        # 发件人密码/授权码
        password_layout = QHBoxLayout()
        password_label = QLabel("邮箱密码/授权码:")
        self.sender_password_input = QLineEdit()
        self.sender_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.sender_password_input)
        mail_layout.addLayout(password_layout)
        
        # 收件人邮箱
        receiver_layout = QHBoxLayout()
        receiver_label = QLabel("接收通知的邮箱:")
        self.receiver_email_input = QLineEdit()
        self.receiver_email_input.setPlaceholderText("例如: your_email@qq.com")
        receiver_layout.addWidget(receiver_label)
        receiver_layout.addWidget(self.receiver_email_input)
        mail_layout.addLayout(receiver_layout)
        
        # 测试按钮
        test_button = QPushButton("测试邮件配置")
        test_button.clicked.connect(self.test_email)
        mail_layout.addWidget(test_button)
        
        # 保存按钮
        save_button = QPushButton("保存邮件配置")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        # 说明信息
        info_label = QLabel("说明: 配置邮件服务器后，程序异常时会自动发送通知邮件。对于QQ邮箱，密码需填写授权码而非登录密码。")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
    def test_email(self):
        """测试邮件配置"""
        # 保存配置并更新
        self.save_settings()
        self.update_mail_settings_from_ui()
        
        # 测试邮件发送
        try:
            result = email_sender.send_error_notification(
                "测试邮件",
                "这是一封测试邮件，如果您收到此邮件，说明邮件配置正确。",
                "测试堆栈跟踪信息"
            )
            if result:
                self.log_signal.emit("测试邮件发送成功，请检查您的邮箱")
            else:
                self.log_signal.emit("测试邮件发送失败，请检查邮件配置")
        except Exception as e:
            self.log_signal.emit(f"测试邮件发送异常: {str(e)}")
    
    def update_mail_settings_from_ui(self):
        """从UI更新邮件设置"""
        # 更新邮件配置
        os.environ['SMTP_SERVER'] = self.smtp_server_input.text()
        os.environ['SMTP_PORT'] = str(self.smtp_port_input.value())
        os.environ['SENDER_EMAIL'] = self.sender_email_input.text()
        os.environ['SENDER_PASSWORD'] = self.sender_password_input.text()
        os.environ['RECEIVER_EMAIL'] = self.receiver_email_input.text()
        
        # 更新email_sender对象的配置
        email_sender.smtp_server = self.smtp_server_input.text()
        email_sender.smtp_port = self.smtp_port_input.value()
        email_sender.sender_email = self.sender_email_input.text()
        email_sender.sender_password = self.sender_password_input.text()
        email_sender.receiver_email = self.receiver_email_input.text()
    
    def load_settings(self):
        """加载设置"""
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # 加载邮件设置
                if 'mail' in settings:
                    mail_settings = settings['mail']
                    self.smtp_server_input.setText(mail_settings.get('smtp_server', ''))
                    self.smtp_port_input.setValue(int(mail_settings.get('smtp_port', 465)))
                    self.sender_email_input.setText(mail_settings.get('sender_email', ''))
                    self.sender_password_input.setText(mail_settings.get('sender_password', ''))
                    self.receiver_email_input.setText(mail_settings.get('receiver_email', ''))
                    
                    # 更新环境变量
                    os.environ['SMTP_SERVER'] = mail_settings.get('smtp_server', '')
                    os.environ['SMTP_PORT'] = str(mail_settings.get('smtp_port', 465))
                    os.environ['SENDER_EMAIL'] = mail_settings.get('sender_email', '')
                    os.environ['SENDER_PASSWORD'] = mail_settings.get('sender_password', '')
                    os.environ['RECEIVER_EMAIL'] = mail_settings.get('receiver_email', '')
                    
                    # 更新email_sender对象
                    email_sender.smtp_server = mail_settings.get('smtp_server', '')
                    email_sender.smtp_port = int(mail_settings.get('smtp_port', 465))
                    email_sender.sender_email = mail_settings.get('sender_email', '')
                    email_sender.sender_password = mail_settings.get('sender_password', '')
                    email_sender.receiver_email = mail_settings.get('receiver_email', '')
                    
                # 加载其他设置
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
                
                # 加载任务间隔设置
                self.task_interval_spinbox.setValue(settings.get('task_interval', 10))
            except Exception as e:
                self.log_text.append(f"加载设置失败: {str(e)}")

    def start_program(self):
        """启动程序"""
        if self.worker_thread and self.worker_thread.isRunning():
            return

        # 获取登录信息
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        remember = self.remember_checkbox.isChecked()

        if not username or not password:
            self.update_log("请输入用户名和密码")
            return

        # 保存设置
        self.save_settings()
        
        # 设置环境变量，确保登录凭证可被main.py获取
        os.environ['USERNAME'] = username
        os.environ['PASSWORD'] = password
        
        # 设置时间
        start_time = self.start_time.time().toPyTime()
        middle_time = self.middle_time.time().toPyTime()
        end_time = self.end_time.time().toPyTime()
        time_config.set_times(start_time, middle_time, end_time)

        self.update_log(f"设置工作时间：开始={start_time.strftime('%H:%M')}，中间={middle_time.strftime('%H:%M')}，结束={end_time.strftime('%H:%M')}")

        # 禁用输入
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.remember_checkbox.setEnabled(False)
        self.start_time.setEnabled(False)
        self.middle_time.setEnabled(False)
        self.end_time.setEnabled(False)
        self.task_interval_spinbox.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # 设置web_automation模块的错误对话框信号
        import web_automation
        web_automation.ui_error_dialog_signal = self.error_dialog_signal

        # 创建线程
        interval = self.task_interval_spinbox.value()
        self.worker_thread = WorkerThread(interval)
        self.worker_thread.finished.connect(self.stop_program)

        # 启动线程
        self.worker_thread.start()
        self.update_log("程序已启动")
        
    def stop_program(self):
        """停止程序"""
        if not self.worker_thread or not self.worker_thread.isRunning():
            return

        # 停止线程
        self.worker_thread.stop()
        self.worker_thread.wait()  # 等待线程结束
        self.worker_thread = None

        # 重置web_automation模块的错误对话框信号
        import web_automation
        web_automation.ui_error_dialog_signal = None

        # 关闭浏览器
        try:
            # 导入main模块
            import main
            # 检查是否存在全局浏览器实例并关闭
            if hasattr(main, 'global_automation') and main.global_automation:
                logger.info("关闭浏览器")
                main.global_automation.close()
                main.global_automation = None
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")

        # 启用输入
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.remember_checkbox.setEnabled(True)
        self.start_time.setEnabled(True)
        self.middle_time.setEnabled(True)
        self.end_time.setEnabled(True)
        self.task_interval_spinbox.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.update_log("程序已终止")

    def update_log(self, text):
        """更新日志显示"""
        self.log_text.append(text)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def save_settings(self):
        """保存设置"""
        try:
            # 先读取现有设置
            settings = {}
            if os.path.exists('settings.json'):
                try:
                    with open('settings.json', 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except:
                    settings = {}
            
            # 更新主配置
            settings.update({
                'username': self.username_input.text(),
                'remember_password': self.remember_checkbox.isChecked(),
                'start_time': self.start_time.time().toString('HH:mm'),
                'middle_time': self.middle_time.time().toString('HH:mm'),
                'end_time': self.end_time.time().toString('HH:mm'),
                'task_interval': self.task_interval_spinbox.value()
            })
            
            if self.remember_checkbox.isChecked():
                settings['password'] = self.password_input.text()
                
            # 更新邮件配置
            if 'mail' not in settings:
                settings['mail'] = {}
                
            settings['mail']['smtp_server'] = self.smtp_server_input.text()
            settings['mail']['smtp_port'] = self.smtp_port_input.value()
            settings['mail']['sender_email'] = self.sender_email_input.text()
            settings['mail']['sender_password'] = self.sender_password_input.text()
            settings['mail']['receiver_email'] = self.receiver_email_input.text()
            
            # 保存所有设置
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            logger.info("所有设置已保存")
        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.stop_program()
        self.save_settings()
        event.accept()

    def _setup_log_tab(self, tab):
        """设置日志页面"""
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 日志显示区域
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        # 创建日志文本框
        self.log_tab_text = QTextEdit()
        self.log_tab_text.setReadOnly(True)
        log_layout.addWidget(self.log_tab_text)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        # 清除日志按钮
        clear_button = QPushButton("清除日志")
        clear_button.clicked.connect(self.clear_log)
        
        # 保存日志按钮
        save_button = QPushButton("保存日志")
        save_button.clicked.connect(self.save_log)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(save_button)
        log_layout.addLayout(button_layout)
        
        layout.addWidget(log_group)
        
        # 连接日志信号到这个页面
        self.log_signal.connect(self.update_log_tab)
        
    def clear_log(self):
        """清除日志内容"""
        self.log_tab_text.clear()
        self.log_text.clear()
        logger.info("日志已清除")
        
    def save_log(self):
        """保存日志到文件"""
        try:
            # 获取当前时间作为文件名
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"log_{current_time}.txt"
            
            # 保存日志内容
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_tab_text.toPlainText())
                
            logger.info(f"日志已保存到文件: {filename}")
        except Exception as e:
            logger.error(f"保存日志失败: {str(e)}")
            
    def update_log_tab(self, text):
        """更新日志标签页中的日志显示"""
        self.log_tab_text.append(text)
        # 自动滚动到底部
        self.log_tab_text.verticalScrollBar().setValue(
            self.log_tab_text.verticalScrollBar().maximum()
        )
        
    def update_log(self, text):
        """更新日志显示"""
        self.log_text.append(text)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _setup_about_tab(self, tab):
        """设置关于页面"""
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # 标题
        title_label = QLabel("自动化打单配货程序")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 版本信息
        version_label = QLabel(f"版本: v{VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 发布日期
        date_label = QLabel(f"发布日期: {VERSION_DATE}")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(date_label)
        
        layout.addSpacing(20)
        
        # 更新内容
        update_group = QGroupBox("版本更新内容")
        update_layout = QVBoxLayout()
        update_group.setLayout(update_layout)
        
        update_text = QTextEdit()
        update_text.setReadOnly(True)
        update_text.setPlainText(VERSION_INFO)
        update_layout.addWidget(update_text)
        
        layout.addWidget(update_group)
        
        layout.addSpacing(20)
        
        # 作者信息
        author_info = QLabel("© 2024-2025 @kevinZou1206 版权所有")
        author_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_info)
        
        layout.addStretch()

    def show_error_dialog(self, message):
        """显示异常处理对话框"""
        # 使用QMessageBox创建一个模态对话框
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        
        # 根据错误消息内容设置不同的标题和提示文本
        if "登录失败" in message:
            msg_box.setWindowTitle("登录失败")
            msg_box.setText("系统登录失败，请检查网络连接和登录凭证，或手动登录系统。\n处理完毕后点击确定继续。")
        else:
            msg_box.setWindowTitle("配货失败")
            msg_box.setText("波次配货过程中出现异常，请手动处理后点击确定继续执行程序。")
            
        msg_box.setDetailedText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # 设置样式以使对话框更明显
        msg_box.setStyleSheet("QMessageBox { font-size: 12pt; }")
        
        # 记录日志
        logger.warning(f"已弹出异常处理对话框，等待用户处理: {message}")
        
        # 显示对话框并等待用户点击确定
        msg_box.exec()
        
        # 用户点击确定后，记录日志
        logger.info("用户已确认异常处理完成，程序继续执行")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 