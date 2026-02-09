from ext import log
from ext.gmail import TempGmail
from ext.mail_service import MailService
import time

def test_logger():
    logger = log.setup_logger("test_logger")
    logger.debug("这是一个 DEBUG 日志")
    logger.info("这是一个 INFO 日志")
    logger.warning("这是一个 WARNING 日志")
    logger.error("这是一个 ERROR 日志")
    logger.critical("这是一个 CRITICAL 日志")
    print("Logger 测试完成\n")

def test_temp_gmail():
    print("开始测试 TempGmail (emailnator.com)...")
    try:
        gmail = TempGmail()
        email = gmail.generate_email()
        print(f"成功生成 Gmail: {email}")
        
        print("正在获取邮件列表...")
        messages = gmail.get_message_list()
        print(f"当前邮件数量: {len(messages)}")
        print("TempGmail 测试完成\n")
    except Exception as e:
        print(f"TempGmail 测试失败: {e}\n")

def test_mail_service():
    print("开始测试 MailService (chatgpt.org.uk)...")
    try:
        service = MailService()
        email = service.create_temp_email()
        if email:
            print(f"成功生成临时邮箱: {email}")
            print("正在获取邮件列表...")
            emails = service.get_emails(email)
            print(f"当前邮件数量: {len(emails)}")
        else:
            print("生成临时邮箱失败")
        print("MailService 测试完成\n")
    except Exception as e:
        print(f"MailService 测试失败: {e}\n")

if __name__ == "__main__":
    print("=== 开始模块功能测试 ===\n")
    test_logger()
    test_temp_gmail()
    test_mail_service()
    print("=== 所有测试执行完毕 ===")
