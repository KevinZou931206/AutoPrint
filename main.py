"""
主程序文件
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv

from web_automation import WebAutomation
from config import WORK_START_TIME, WORK_END_TIME, ORDER_THRESHOLDS, WORK_MIDDLE_TIME
from logger import logger

# 加载环境变量
load_dotenv()

def is_work_time():
    """判断当前是否是工作时间"""
    current_time = datetime.now().time()
    return WORK_START_TIME <= current_time <= WORK_END_TIME

def is_wave_time():
    """判断当前是否是波次时间"""
    current_time = datetime.now().time()
    return WORK_START_TIME <= current_time < WORK_MIDDLE_TIME

def main():
    """主程序入口"""
    current_time = datetime.now()
    logger.info(f"开始执行任务，当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 首先检查是否是工作时间
    if not is_work_time():
        logger.info("当前不是工作时间，不执行任务")
        return
    
    try:
        # 获取登录凭证
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')

        if not username or not password:
            logger.error("未找到登录凭证，请检查环境变量")
            return
        
        logger.info(f"获取到登录凭证: {username}")
        
        # 只有在工作时间才初始化浏览器
        automation = WebAutomation()
        try:
            # 登录系统
            automation.login(username, password)

            # 查询待打单数量
            order_count = automation.order_count()

            # 根据时间执行不同的波次配货
            wave_time = is_wave_time()
            wave_order_count = order_count >= ORDER_THRESHOLDS['wave']
            if wave_time and wave_order_count:
                logger.info("执行整波配货任务")
                automation.create_wave(wave_time)
                automation.execute_wave_picking()
            elif wave_time and not wave_order_count:
                logger.info("当前订单数量不够整波，不执行任务")
            else:
                logger.info("执行散单配货任务")
                automation.create_wave(wave_time)
                automation.execute_wave_picking()
            
            logger.info("任务执行完成，等待10分钟后重新执行")
        except Exception as e:
            logger.error(f"任务执行失败: {str(e)}")
        finally:
            automation.close()
            
    except Exception as e:
        logger.error(f"程序运行异常: {str(e)}")

if __name__ == "__main__":
    logger.info("程序启动")
    
    try:
        while True:
            # 执行任务
            main()
            # 等待10分钟
            time.sleep(10 * 60)
                
    except KeyboardInterrupt:
        logger.info("程序被手动停止")
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}")