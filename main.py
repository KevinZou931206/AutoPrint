"""
主程序文件
"""
import os
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv

from web_automation import WebAutomation
from config import ORDER_THRESHOLDS, time_config
from logger import logger
from mail_sender import email_sender

# 加载环境变量
load_dotenv()

def is_work_time():
    """判断当前是否是工作时间"""
    current_time = datetime.now().time()
    logger.info(f"当前时间: {current_time.strftime('%H:%M')}")
    logger.info(f"工作时间: {time_config.WORK_START_TIME.strftime('%H:%M')} - {time_config.WORK_END_TIME.strftime('%H:%M')}")
    return time_config.WORK_START_TIME <= current_time <= time_config.WORK_END_TIME

def is_wave_time():
    """判断当前是否是波次时间"""
    current_time = datetime.now().time()
    logger.info(f"波次时间: {time_config.WORK_START_TIME.strftime('%H:%M')} - {time_config.WORK_MIDDLE_TIME.strftime('%H:%M')}")
    return time_config.WORK_START_TIME <= current_time < time_config.WORK_MIDDLE_TIME

def main():
    """主程序入口"""
    current_time = datetime.now()
    logger.info(f"开始执行任务，当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 首先检查是否是工作时间
    if not is_work_time():
        logger.info("当前不是工作时间，不执行任务")
        return False
    
    automation = None
    try:
        # 获取登录凭证
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')

        if not username or not password:
            error_msg = "未找到登录凭证，请检查环境变量"
            logger.error(error_msg)
            email_sender.send_error_notification("登录凭证错误", error_msg)
            return False
        
        logger.info(f"获取到登录凭证: {username}")
        
        # 只有在工作时间才初始化浏览器
        automation = WebAutomation()
        try:
            # 登录系统
            login_success = automation.login(username, password)
            
            # 如果登录失败，直接返回False结束任务
            if not login_success:
                logger.error("登录失败，终止任务")
                return False

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
            return True
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(error_msg)
            # 发送邮件通知
            email_sender.send_error_notification("任务执行失败", error_msg, stack_trace)
            return False
        finally:
            if automation:
                automation.close()
            
    except Exception as e:
        error_msg = f"程序运行异常: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(error_msg)
        # 发送邮件通知
        email_sender.send_error_notification("程序异常", error_msg, stack_trace)
        return False

if __name__ == "__main__":
    logger.info("程序启动")
    
    try:
        # 验证邮件配置
        if email_sender.is_configured():
            logger.info("邮件配置有效，异常通知已启用")
        else:
            logger.warning("邮件配置不完整，异常通知将不可用")
            
        while True:
            try:
                # 执行任务
                main()
            except Exception as e:
                error_msg = f"主任务执行异常: {str(e)}"
                stack_trace = traceback.format_exc()
                logger.error(error_msg)
                # 发送邮件通知
                email_sender.send_error_notification("主任务异常", error_msg, stack_trace)
                
            # 等待10分钟
            time.sleep(10 * 60)
                
    except KeyboardInterrupt:
        logger.info("程序被手动停止")
    except Exception as e:
        error_msg = f"程序异常退出: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(error_msg)
        # 发送邮件通知
        email_sender.send_error_notification("程序崩溃", error_msg, stack_trace)