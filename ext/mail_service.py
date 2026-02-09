import re
import time
import random
from curl_cffi import requests as curl_requests
from ext import log

logger = log.setup_logger()

class MailService:
    def __init__(self, api_url="https://mail.chatgpt.org.uk"):
        self.api_url = api_url
        self.http = curl_requests.Session()
        self.headers = {
            "content-type": "application/json",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Google Chrome\";v=\"144\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Referer": "https://mail.chatgpt.org.uk/18eb3278@sanity-uk.org"
        }

    def log(self, msg):
        logger.info(f"{msg}")

    def create_temp_email(self):
        """申请临时邮箱"""
        try:
            self.log("正在申请邮箱...")
            r = self.http.get(
                f"{self.api_url}/api/generate-email", 
                headers=self.headers, 
                timeout=20
            )
            if r.json().get('success'):
                email = r.json()['data']['email']
                self.log(f"成功申请邮箱: {email}")
                return email
        except Exception as e:
            self.log(f"邮箱申请异常: {e}")
        return None

    def get_emails(self, email):
        """获取邮件列表"""
        try:
            r = self.http.get(
                f"{self.api_url}/api/emails", 
                params={"email": email}, 
                headers=self.headers,
                timeout=20
            )
            return r.json().get('data', {}).get('emails', [])
        except Exception as e:
            self.log(f"获取邮件列表异常: {e}")
            return []

    def get_latest_email_content(self, email):
        """获取最新一封邮件的内容（已清洗HTML）"""
        emails = self.get_emails(email)
        if emails:
            content = emails[0].get('content') or emails[0].get('html_content') or ''
            # 清洗HTML
            text_content = re.sub('<[^<]+?>', ' ', content)
            return text_content.strip()
        return None

    def get_content_by_regex(self, email, regex_pattern, timeout=60, sleep_interval=5):
        """通过正则从邮件中提取内容"""
        self.log(f"等待 {email} 的匹配内容 (pattern: {regex_pattern})...")
        start = time.time()
        seen_contents = set()
        
        while time.time() - start < timeout:
            text_content = self.get_latest_email_content(email)
            if text_content and text_content not in seen_contents:
                seen_contents.add(text_content)
                match = re.search(regex_pattern, text_content, re.IGNORECASE)
                if match:
                    # 如果有分组则返回分组内容，否则返回整个匹配
                    result = match.group(1) if match.groups() else match.group(0)
                    self.log(f"正则匹配成功: {result}")
                    return result
            
            time.sleep(sleep_interval)
        
        self.log("等待正则匹配超时")
        return None

    def wait_for_code(self, email, timeout=60, sleep_interval=5):
        """等待验证码"""
        # 匹配模式： "code: XXXXXX" 或 "code is XXXXXX" (支持字母+数字混合)
        regex_pattern = r'verification code[:\s]+([A-Z0-9]{6})'
        return self.get_content_by_regex(email, regex_pattern, timeout, sleep_interval)

    def wait_for_trae_code(self, email, timeout=60, sleep_interval=5):
        """等待 Trae 验证码"""
        # 匹配 6 位数字验证码，通常在 "enter the code in Trae" 之后
        regex_pattern = r'(?:enter the code in Trae|Verification Code)[\s\n]+(\d{6})'
        return self.get_content_by_regex(email, regex_pattern, timeout, sleep_interval)

    def wait_for_zenmux_link(self, email, timeout=60, sleep_interval=5):
        """预设：等待 Zenmux 注册/登录链接"""
        regex_pattern = r"https://zenmux\.ai\?token=[a-zA-Z0-9]{32,}"
        return self.get_content_by_regex(email, regex_pattern, timeout, sleep_interval)
    

if __name__ == "__main__":
    # 简单的模块测试
    service = MailService()
    test_email = "644168ac@cnhopmz.shop"
    
    logger.info(f"开始测试 Trae 验证码提取，从 {test_email} ...")
    code = service.wait_for_trae_code(test_email, timeout=30)
    
    if code:
        logger.info(f"Trae 验证码测试成功，提取到的验证码: {code}")
    else:
        logger.info("Trae 验证码测试失败，未能在超时时间内获取到匹配内容")
