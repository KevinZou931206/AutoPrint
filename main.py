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

# 全局浏览器实例，用于在工作时间内复用
global_automation = None
last_work_time_status = False  # 记录上一次的工作时间状态

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

def manage_browser():
    """管理浏览器实例"""
    global global_automation, last_work_time_status
    
    current_work_time = is_work_time()
    
    # 如果从工作时间变为非工作时间，关闭浏览器
    if last_work_time_status and not current_work_time:
        logger.info("工作时间结束，关闭浏览器")
        if global_automation:
            global_automation.close()
            global_automation = None
    
    # 如果在工作时间内且浏览器实例为空，创建新的浏览器实例
    if current_work_time and not global_automation:
        logger.info("工作时间内，初始化浏览器")
        global_automation = WebAutomation()
    
    # 更新工作时间状态
    last_work_time_status = current_work_time
    
    return current_work_time

def main():
    """主程序入口"""
    global global_automation
    
    current_time = datetime.now()
    logger.info(f"开始执行任务，当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 管理浏览器实例
    current_work_time = manage_browser()
    
    # 不是工作时间，不执行任务
    if not current_work_time:
        logger.info("当前不是工作时间，不执行任务")
        return False
    
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
        
        # 使用全局浏览器实例
        if not global_automation:
            logger.error("浏览器实例为空，无法执行任务")
            return False
            
        try:
            # 检查是否需要登录（未登录或会话过期）
            if not global_automation.is_logged_in():
                # 登录系统
                login_success = global_automation.login(username, password)
                
                # 如果登录失败，终止任务
                if not login_success:
                    logger.error("登录失败，终止任务")
                    return False

            # 查询待打单数量
            order_count = global_automation.order_count()

            # 根据时间执行不同的波次配货
            wave_time = is_wave_time()
            wave_order_count = order_count >= ORDER_THRESHOLDS['wave']
            if wave_time and wave_order_count:
                logger.info("执行整波配货任务")
                global_automation.create_wave(wave_time)
                global_automation.execute_wave_picking()
            elif wave_time and not wave_order_count:
                logger.info("当前订单数量不够整波，不执行任务")
            else:
                logger.info("执行散单配货任务")
                global_automation.create_wave(wave_time)
                global_automation.execute_wave_picking()
            
            logger.info("任务执行完成")
            return True
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(error_msg)
            # 发送邮件通知
            email_sender.send_error_notification("任务执行失败", error_msg, stack_trace)
            return False
            
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
                
                # 如果发生异常，确保浏览器已关闭
                if global_automation:
                    try:
                        global_automation.close()
                    except:
                        pass
                    global_automation = None
                
            # 等待时间由UI线程控制，这里不需要额外等待
            time.sleep(1)  # 仅短暂等待，避免CPU过度使用
                
    except KeyboardInterrupt:
        logger.info("程序被手动停止")
        # 确保浏览器已关闭
        if global_automation:
            global_automation.close()
    except Exception as e:
        error_msg = f"程序异常退出: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(error_msg)
        # 发送邮件通知
        email_sender.send_error_notification("程序崩溃", error_msg, stack_trace)
        # 确保浏览器已关闭
        if global_automation:
            global_automation.close()