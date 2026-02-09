"""
临时 Google Mail 模块
基于 emailnator.com 的 API 实现
"""
import httpx
import re
from typing import Optional, List, Dict, Any
from ext import log

logger = log.setup_logger()



class TempGmail:
    """临时 Gmail 邮箱管理类"""
    
    BASE_URL = "https://www.emailnator.com"
    
    def __init__(self):
        """初始化客户端"""
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Origin": self.BASE_URL,
                "Referer": f"{self.BASE_URL}/",
                "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",
            },
            follow_redirects=True,
            timeout=30.0
        )
        self.xsrf_token: Optional[str] = None
        self.email: Optional[str] = None
    
    def _get_xsrf_token(self) -> str:
        """获取 XSRF Token"""
        try:
            # 访问主页获取 cookie 和 session
            response = self.client.get(self.BASE_URL)
            response.raise_for_status()
            
            logger.info(f"成功获取主页 Cookie，状态码: {response.status_code}")
            
            # 从 cookie 中提取 XSRF-TOKEN（可能是 URL 编码的）
            xsrf_cookie = self.client.cookies.get("XSRF-TOKEN")
            if xsrf_cookie:
                # URL 解码 token
                from urllib.parse import unquote
                self.xsrf_token = unquote(xsrf_cookie)
                return self.xsrf_token
            
            logger.error(f"无法从 Cookie 中获取 XSRF Token: {xsrf_cookie}")
            raise Exception("无法从 Cookie 中获取 XSRF Token")
        except Exception as e:
            logger.error(f"获取 XSRF Token 失败: {str(e)}")
            raise Exception(f"获取 XSRF Token 失败: {str(e)}")
    
    def _ensure_token(self):
        """确保有有效的 token"""
        if not self.xsrf_token:
            self._get_xsrf_token()
        logger.info(f"成功获取 XSRF Token: {self.xsrf_token}")

    def generate_email(self, email_types: Optional[List[str]] = None) -> str:
        """
        生成临时邮箱地址
        
        Args:
            email_types: 邮箱类型列表，可选值: ["plusGmail", "dotGmail", "googleMail"]
                        默认为 ["plusGmail", "dotGmail"]
        
        Returns:
            生成的邮箱地址
        """
        logger.info(f"正在生成邮箱，类型: {email_types or ['plusGmail', 'dotGmail']}")
        self._ensure_token()
        
        if email_types is None:
            email_types = ["plusGmail", "dotGmail"]
        
        try:
            logger.info(f"正在申请邮箱类型: {email_types}")
            response = self.client.post(
                f"{self.BASE_URL}/generate-email",
                json={"email": email_types},
                headers={
                    "Content-Type": "application/json",
                    "X-Xsrf-Token": self.xsrf_token,
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if "email" in data:
                logger.info(f"成功生成邮箱: {data['email'][0]}")
                self.email = data["email"][0] if isinstance(data["email"], list) else data["email"]
            else:
                # 如果返回格式不同，尝试直接获取
                self.email = list(data.values())[0] if data else None
            
            if not self.email:
                logger.error(f"无法从响应中提取邮箱地址: {data}")
                raise Exception(f"无法从响应中提取邮箱地址: {data}")
            
            return self.email
        except httpx.HTTPStatusError as e:
            logger.error(f"生成邮箱失败 (HTTP {e.response.status_code}): {e.response.text}")
            raise Exception(f"生成邮箱失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            logger.error(f"生成邮箱失败: {str(e)}")
            raise Exception(f"生成邮箱失败: {str(e)}")
    
    def get_message_list(self, email: Optional[str] = None, filter_ads: bool = True) -> List[Dict[str, Any]]:
        """
        获取邮件列表
        
        Args:
            email: 邮箱地址，如果不提供则使用当前生成的邮箱
            filter_ads: 是否过滤广告邮件，默认为 True
        
        Returns:
            邮件列表
        """
        logger.info(f"正在获取邮箱 {email or self.email} 的邮件列表，过滤广告: {filter_ads}")
        self._ensure_token()
        
        target_email = email or self.email
        if not target_email:
            raise Exception("请先生成邮箱或提供邮箱地址")
        
        # 广告邮件的 messageID 列表
        AD_MESSAGE_IDS = {'ADSVPN'}
        
        try:
            response = self.client.post(
                f"{self.BASE_URL}/message-list",
                json={"email": target_email},
                headers={
                    "Content-Type": "application/json",
                    "X-Xsrf-Token": self.xsrf_token,
                    "Referer": f"{self.BASE_URL}/mailbox/",
                }
            )
            response.raise_for_status()
            
            data = response.json()
            # 返回邮件列表，可能是 messageData 字段
            messages = []
            if isinstance(data, dict):
                messages = data.get("messageData", [])
            elif isinstance(data, list):
                messages = data
            
            # 过滤广告邮件
            if filter_ads and messages:
                messages = [
                    msg for msg in messages
                    if msg.get("messageID") not in AD_MESSAGE_IDS
                ]
            
            return messages
        except httpx.HTTPStatusError as e:
            raise Exception(f"获取邮件列表失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"获取邮件列表失败: {str(e)}")
    
    def get_message_content(self, message_id: str) -> Dict[str, Any]:
        """
        获取邮件内容
        
        Args:
            message_id: 邮件 ID
        
        Returns:
            邮件内容
        """
        logger.info(f"正在获取邮件内容，ID: {message_id}")
        self._ensure_token()
        
        try:
            response = self.client.post(
                f"{self.BASE_URL}/message-list",
                json={"email": self.email, "messageID": message_id},
                headers={
                    "Content-Type": "application/json",
                    "X-Xsrf-Token": self.xsrf_token,
                    "Referer": f"{self.BASE_URL}/mailbox/",
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"获取邮件内容失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"获取邮件内容失败: {str(e)}")
    
    def close(self):
        """关闭客户端"""
        logger.info("正在关闭异步客户端")
        self.client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()


# 异步版本
class AsyncTempGmail:
    """异步临时 Gmail 邮箱管理类"""
    
    BASE_URL = "https://www.emailnator.com"
    
    def __init__(self):
        """初始化异步客户端"""
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Origin": self.BASE_URL,
                "Referer": f"{self.BASE_URL}/",
                "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",
            },
            follow_redirects=True,
            timeout=30.0
        )
        self.xsrf_token: Optional[str] = None
        self.email: Optional[str] = None
    
    async def _get_xsrf_token(self) -> str:
        """获取 XSRF Token"""
        try:
            # 访问主页获取 cookie 和 session
            response = await self.client.get(self.BASE_URL)
            response.raise_for_status()
            
            # 从 cookie 中提取 XSRF-TOKEN（可能是 URL 编码的）
            xsrf_cookie = self.client.cookies.get("XSRF-TOKEN")
            if xsrf_cookie:
                # URL 解码 token
                from urllib.parse import unquote
                self.xsrf_token = unquote(xsrf_cookie)
                return self.xsrf_token
            
            raise Exception("无法从 Cookie 中获取 XSRF Token")
        except Exception as e:
            raise Exception(f"获取 XSRF Token 失败: {str(e)}")
    
    async def _ensure_token(self):
        """确保有有效的 token"""
        if not self.xsrf_token:
            await self._get_xsrf_token()
        logger.info(f"正在生成邮箱，类型: {email_types or ['plusGmail', 'dotGmail']}")

    async def generate_email(self, email_types: Optional[List[str]] = None) -> str:
        """
        生成临时邮箱地址
        
        Args:
            email_types: 邮箱类型列表，可选值: ["plusGmail", "dotGmail", "googleMail"]
                        默认为 ["plusGmail", "dotGmail"]
        
        Returns:
            生成的邮箱地址
        """
        await self._ensure_token()
        logger.info(f"正在生成邮箱，类型: {email_types or ['plusGmail', 'dotGmail']}")
        if email_types is None:
            email_types = ["plusGmail", "dotGmail"]
        
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/generate-email",
                json={"email": email_types},
                headers={
                    "Content-Type": "application/json",
                    "X-Xsrf-Token": self.xsrf_token,
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if "email" in data:
                self.email = data["email"][0] if isinstance(data["email"], list) else data["email"]
            else:
                self.email = list(data.values())[0] if data else None
            
            if not self.email:
                raise Exception(f"无法从响应中提取邮箱地址: {data}")
            
            return self.email
        except httpx.HTTPStatusError as e:
            raise Exception(f"生成邮箱失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"生成邮箱失败: {str(e)}")
    
    async def get_message_list(self, email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取邮件列表
        
        Args:
            email: 邮箱地址，如果不提供则使用当前生成的邮箱
        
        Returns:
            邮件列表
        """
        await self._ensure_token()
        logger.info(f"正在获取邮箱 {email or self.email} 的邮件列表")

        target_email = email or self.email
        if not target_email:
            raise Exception("请先生成邮箱或提供邮箱地址")
        
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/message-list",
                json={"email": target_email},
                headers={
                    "Content-Type": "application/json",
                    "X-Xsrf-Token": self.xsrf_token,
                    "Referer": f"{self.BASE_URL}/mailbox/",
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict):
                return data.get("messageData", [])
            elif isinstance(data, list):
                return data
            else:
                return []
        except httpx.HTTPStatusError as e:
            raise Exception(f"获取邮件列表失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"获取邮件列表失败: {str(e)}")
    
    async def get_message_content(self, message_id: str) -> Dict[str, Any]:
        """
        获取邮件内容
        
        Args:
            message_id: 邮件 ID
        
        Returns:
            邮件内容
        """
        await self._ensure_token()
        logger.info(f"正在获取邮件内容，ID: {message_id}")
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/message-list",
                json={"email": self.email, "messageID": message_id},
                headers={
                    "Content-Type": "application/json",
                    "X-Xsrf-Token": self.xsrf_token,
                    "Referer": f"{self.BASE_URL}/mailbox/",
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"获取邮件内容失败 (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"获取邮件内容失败: {str(e)}")
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
        logger.info("正在关闭异步客户端")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

