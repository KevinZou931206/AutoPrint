"""
配置文件
"""
from datetime import time

class TimeConfig:
    """时间配置类"""
    def __init__(self):
        self.WORK_START_TIME = time(7, 0)
        self.WORK_MIDDLE_TIME = time(16, 0)
        self.WORK_END_TIME = time(17, 0)
    
    def update_times(self, start_time, middle_time, end_time):
        self.WORK_START_TIME = start_time
        self.WORK_MIDDLE_TIME = middle_time
        self.WORK_END_TIME = end_time

    def set_times(self, start_time, middle_time, end_time):
        """设置工作时间"""
        self.WORK_START_TIME = start_time
        self.WORK_MIDDLE_TIME = middle_time
        self.WORK_END_TIME = end_time
        return f"工作时间已设置：开始={start_time.strftime('%H:%M')}，中间={middle_time.strftime('%H:%M')}，结束={end_time.strftime('%H:%M')}"

# 创建全局配置实例
time_config = TimeConfig()

# URL配置
URLS = {
    'login': 'https://erp.hupun.com/login',
    'home': 'https://erp.hupun.com/frame/home',
    'order_picking': 'https://erp.hupun.com/frame/332',
    'wave_picking': 'https://erp.hupun.com/frame/3321'
}

# 等待时间配置（秒）
WAIT_TIME = {
    'short': 1,
    'medium': 5,
    'long': 10,
    'generate_express': 15,
    'page_load': 3,    # 页面加载等待时间
    'iframe_load': 3    # iframe加载等待时间
}

# 订单数量阈值
ORDER_THRESHOLDS = {
    'single': 1,
    'few': 5,
    'wave': 25
}

# XPath选择器
SELECTORS = {
    'login': {
        'login_type': '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[1]/div',  # 登录方式
        'input': '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[5]/button[1]',  # 切换账号登录
        'username': '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]/div/form/div[1]/div/div/input',  # 用户名
        'password': '//*[@id="input-password"]',  # 密码
        'submit': '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]/div/button',  # 登录按钮
        'error_message': '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]/div/div/div/span'  # 登录错误消息
    },
    'home': {
        'ad_close': '//*[@id="app"]/div/div/div[8]/div/i',  # 广告关闭
        'refresh_button': '//*[@id="app"]/div/div/div[6]/div[1]/div[2]/i',  # 刷新按钮
        'order_count': '//*[@id="app"]/div/div/div[6]/div[1]/div[1]/div[2]/ul/li[1]/strong'  # 待打单数量
    },
    'wave': {
        'query_button': '//*[@id="app"]/div/div[1]/div[1]/div[1]/div/button[1]',  # 查询按钮
        'wave_count': '//*[@id="app"]/div/div[1]/div[2]/div[2]/div[3]/div[4]/div[3]/div[2]/span',  # 波次数量
        'create_wave': '//*[@id="add-guide-step3-box"]/div[2]/div/div/button[1]',  # 生成波次按钮
        'first_checkbox': '//tr[@rowid="503871746583168614"]//td[@colid="col_76"]',  # 整波勾选框
        'first_checkbox_2': '//tr[@rowid="778233247578105467"]//td[@colid="col_76"]',  # 单品勾选框
        'second_checkbox': '//tr[@rowid="863005655571211718"]//td[@colid="col_76"]',  # 散单勾选框
        'create_wave_2': '/html/body/div[3]/div/div[3]/div/div[2]/button[1]',  # 生成波次按钮
        'close_window': '//*[@id="panelTask"]/div[1]/div[2]',  # 关闭弹窗
        'first_row': '//*[@id="app"]/div/div[2]/div/div[1]/div/div[1]/div[2]/div[2]/div/div[2]/table/tbody/tr/td[2]/div/span/span[2]',  # 勾选第一行
        'generate_express': '//*[@id="add-guide-step3-box"]/div[3]/div/div/button[1]',  # 生成快递单
        'print_picking': '//*[@id="add-guide-step3-box"]/div[7]/div/div/button[1]',  # 打配货单
        'print_express': '//*[@id="add-guide-step3-box"]/div[5]/div/div/button[1]',  # 打快递单
        'confirm_picking': '//*[@id="add-guide-step3-box"]/div[1]/button'  # 确认配货
    },
    'order': {
        'query_button': '//*[@id="app"]/div/div[1]/div[1]/div[1]/div/button[1]',  # 查询按钮
        'order_count': '//*[@id="app"]/div/div[1]/div[2]/div[2]/div[3]/div[4]/div[3]/div[2]/span',  # 波次数量
        'checkbox_all': '//*[@id="app"]/div/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div[1]/table/thead/tr/th[2]/div[1]/span/span/span',  # 全选框
        'get_express': '//*[@id="add-guide-step3-box"]/div[6]/button',  # 取号打单按钮
        'print_picking': '//*[@id="add-guide-step3-box"]/div[9]/div/div/button[1]',  # 打配货单按钮
        'confirm_picking': '//*[@id="add-guide-step3-box"]/div[1]/button',  # 确认配货按钮
    }
}
