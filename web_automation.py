"""
网页自动化操作类
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

from config import URLS, SELECTORS, WAIT_TIME, ORDER_THRESHOLDS, WORK_START_TIME, WORK_MIDDLE_TIME
from logger import logger

class WebAutomation:
    def __init__(self):
        """初始化WebAutomation类"""
        self.driver = None
        self.setup_driver()
        self.is_in_iframe = False  # 添加标记，记录是否在iframe中

    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            service = Service('./chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("浏览器驱动初始化成功")
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {str(e)}")
            raise

    def get_iframe_xpath(self, url):
        """根据不同的页面返回对应的iframe xpath"""
        if URLS['home'] in url:
            return '//*[@id="tabsetMain"]/contents/content/c-iframe/iframe'
        elif URLS['wave_picking'] in url:
            return '//*[@id="tabsetMain"]/contents/content[2]/c-iframe/iframe'
        else:
            return '//*[@id="tabsetMain"]/contents/content/c-iframe/iframe'  # 默认xpath

    def switch_to_iframe(self):
        """切换到iframe"""
        if not self.is_in_iframe:  # 只有不在iframe中才需要切换
            try:
                # 先切换到默认内容
                self.driver.switch_to.default_content()
                time.sleep(WAIT_TIME['short'])
                
                # 根据当前URL获取对应的iframe xpath
                iframe_xpath = self.get_iframe_xpath(self.driver.current_url)
                iframe = WebDriverWait(self.driver, WAIT_TIME['short']).until(
                    EC.presence_of_element_located((By.XPATH, iframe_xpath))
                )
                self.driver.switch_to.frame(iframe)
                time.sleep(WAIT_TIME['short'])
                self.is_in_iframe = True  # 设置标记
                logger.info("切换iframe成功")
                
            except Exception as e:
                logger.error(f"切换iframe失败: {str(e)}")
                raise

    def switch_to_default(self):
        """切换回主文档"""
        if self.is_in_iframe:  # 只有在iframe中才需要切换回主文档
            self.driver.switch_to.default_content()
            self.is_in_iframe = False  # 重置标记
            logger.info("切换回主文档")

    def navigate_to(self, url):
        """导航到新页面"""
        try:
            # 切换回主文档
            self.switch_to_default()
            # 导航到新页面
            self.driver.get(url)
            time.sleep(WAIT_TIME['medium'])
            # 如果不是登录页面，就切换到iframe
            if URLS['login'] not in url:
                self.switch_to_iframe()
        except Exception as e:
            logger.error(f"导航到页面失败: {str(e)}")
            raise

    def wait_for_element(self, xpath, timeout=WAIT_TIME['medium'], need_iframe=True):
        """等待元素可见"""
        try:
            # 只在登录页面不使用 iframe
            if not need_iframe:
                self.switch_to_default()
            
            # 等待并返回元素
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            return element
        except Exception as e:
            logger.error(f"等待元素超时 {xpath}: {str(e)}")
            raise

    def login(self, username, password):
        """登录系统"""
        try:
            logger.info("开始登录系统")
            self.navigate_to(URLS['login'])
            
            # 检查当前登录方式
            login_type_element = self.wait_for_element(SELECTORS['login']['login_type'], need_iframe=False)
            login_type = login_type_element.text
            
            # 如果是扫码登录，切换到密码登录
            if "扫码登录" in login_type:
                logger.info("当前为扫码登录页面，切换到密码登录")
                switch_button = self.wait_for_element(SELECTORS['login']['input'], need_iframe=False)
                switch_button.click()
                time.sleep(WAIT_TIME['short'])
            
            # 输入用户名和密码
            username_input = self.wait_for_element(SELECTORS['login']['username'], need_iframe=False)
            password_input = self.wait_for_element(SELECTORS['login']['password'], need_iframe=False)
            submit_button = self.wait_for_element(SELECTORS['login']['submit'], need_iframe=False)

            username_input.send_keys(username)
            password_input.send_keys(password)
            submit_button.click()
            time.sleep(WAIT_TIME['medium'])
            
            logger.info("登录系统成功")
        except Exception as e:
            logger.error(f"登录系统失败: {str(e)}")
            raise

    def order_count(self):
        """查询待打单数量"""
        try:
            logger.info("开始查询待打单数量")
            self.navigate_to(URLS['home'])
            
            # 刷新
            refresh_button = self.wait_for_element(SELECTORS['home']['refresh_button'])
            refresh_button.click()
            time.sleep(WAIT_TIME['medium'])

            # 查询待打单数量
            order_count_element = self.wait_for_element(SELECTORS['home']['order_count'])
            order_count = int(order_count_element.text)
            logger.info(f"当前订单数量: {order_count}")
            
            return order_count
        except Exception as e:
            logger.error(f"查询待打单数量失败: {str(e)}")
            return 0

    def create_wave(self, wave_time):
        """生成波次"""
        try:
            logger.info("开始生成波次")
            self.navigate_to(URLS['wave_picking'])

            # 点击生成波次
            create_wave = self.wait_for_element(SELECTORS['wave']['create_wave'])
            create_wave.click()
            time.sleep(WAIT_TIME['short'])

            # 判断当前时间应该生成什么波次
            if wave_time:
                # 勾选整波
                logger.info("勾选整波")
                first_checkbox = self.wait_for_element(SELECTORS['wave']['first_checkbox'])
                first_checkbox.click()
            else:
                # 勾选散单
                logger.info("勾选散单")
                second_checkbox = self.wait_for_element(SELECTORS['wave']['second_checkbox'])
                second_checkbox.click()
            
            # 点击生成波次
            logger.info("生成波次")
            create_wave_2 = self.wait_for_element(SELECTORS['wave']['create_wave_2'])
            create_wave_2.click()
            time.sleep(WAIT_TIME['long'])
            
            logger.info("生成波次完成")
        except Exception as e:
            logger.error(f"生成波次失败: {str(e)}")
            raise

    def execute_wave_picking(self):
        """执行波次配货"""
        try:
            logger.info("开始执行波次配货")
            self.navigate_to(URLS['wave_picking'])
            
            # 点击查询按钮
            query_button = self.wait_for_element(SELECTORS['wave']['query_button'])
            query_button.click()
            time.sleep(WAIT_TIME['medium'])

            # 查询波次数量
            wave_count_element = self.wait_for_element(SELECTORS['wave']['wave_count'])
            wave_count = int(wave_count_element.text)
            logger.info(f"当前波次数量: {wave_count}")

            # 依次处理波次
            for i in range(wave_count):
                logger.info(f"处理第{i+1}个波次")
                # 打单配货
                first_row = self.wait_for_element(SELECTORS['wave']['first_row'])
                generate_express = self.wait_for_element(SELECTORS['wave']['generate_express'])
                print_picking = self.wait_for_element(SELECTORS['wave']['print_picking'])
                print_express = self.wait_for_element(SELECTORS['wave']['print_express'])
                confirm_picking = self.wait_for_element(SELECTORS['wave']['confirm_picking'])

                first_row.click()
                generate_express.click()
                time.sleep(WAIT_TIME['long'])
                print_picking.click()
                time.sleep(WAIT_TIME['medium'])
                print_express.click()
                time.sleep(WAIT_TIME['medium'])
                confirm_picking.click()
                time.sleep(WAIT_TIME['medium'])
                logger.info(f"第{i+1}个波次处理完成")

        except Exception as e:
            logger.error(f"执行波次配货失败: {str(e)}")
            raise

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")
