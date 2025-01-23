"""
日志处理模块
"""
import sys
import os
from loguru import logger
from datetime import datetime

class UILogHandler:
    """UI日志处理器"""
    def __init__(self):
        self.signal = None

    def write(self, message):
        if self.signal:
            self.signal.emit(message)

# 创建UI日志处理器实例
ui_handler = UILogHandler()

# 获取程序运行目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的程序
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是开发环境
    application_path = os.path.dirname(os.path.abspath(__file__))

# 创建日志目录
log_dir = os.path.join(application_path, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志格式
logger.remove()

# 添加文件日志
log_file = os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log")
logger.add(
    log_file,
    rotation="00:00",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    encoding="utf-8"
)

# 添加UI日志处理器
logger.add(
    ui_handler.write,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="INFO"  # 只显示 INFO 及以上级别的日志
)

# 如果是开发环境，添加控制台输出
if not getattr(sys, 'frozen', False):
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

def set_ui_signal(signal):
    """设置UI信号"""
    ui_handler.signal = signal 