from faulthandler import is_enabled
from playwright.sync_api import Page
from camoufox.sync_api import Camoufox
import time
from ext import mail_service
from ext import log
import random

mail = mail_service.MailService()
logger = log.setup_logger()



def generate_password(length: int = 12) -> str:
    # 定义密码字符集
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    # 随机选择字符并拼接
    password = "".join(random.choice(characters) for _ in range(length))
    return password

def register():
    logger.info("Starting Browser and navigate to Trae.ai")
    with Camoufox(
        headless=True,
        os="windows",
        geoip=True,
        window=(1280, 720),
        humanize=False
    ) as browser:

        # 初始化计时器
        start_time = time.time()

        page: Page = browser.new_page() 

        # 定义一些函数，免得每次都要for循环
        def click_btn(selectors: list):
            for selector in selectors:
                try:
                    page.click(selector)
                    logger.info(f"Try to click {selector}")
                    break
                except Exception as e:
                    logger.error(f"Failed to click btn with selector {selector}: {e}")
                    # logger.info(f"Failed to click {selector}")
                    continue
        
        def fill_input(selectors: list, value: str):
            for selector in selectors:
                try:
                    page.fill(selector, value)
                    logger.info(f"Try to fill {selector}")
                    break
                except Exception as e:
                    logger.error(f"Failed to fill {selector} with value {value}: {e}")
                    # logger.info(f"Failed to fill {selector}")
                    continue
        
        def axis_input(asix: list, value: str):
            # 基于坐标输入
            x = asix[0]
            y = asix[1]
            try:
                page.mouse.move(x, y)
                page.mouse.click(x, y)
                page.keyboard.type(value)
                logger.info(f"Try to input {value} to {asix}")
            except Exception as e:
                logger.error(f"Failed to input {value} to {asix}: {e}")
        
        page.goto("https://trae.ai/sign-up", timeout=40000)

        logger.info("Create temp email")
        email = mail.create_temp_email()

        logger.info(f"Created temp email: {email}")

        logger.info("Queue input email")
        page.wait_for_selector("div.sc-eqUAAy:nth-child(1) > div:nth-child(1)")

        MAIL_INPUT = [
            "div.sc-eqUAAy:nth-child(1) > div:nth-child(1) > input:nth-child(1)",
            "html.cc--elegant-black body div#root div.sc-gsFSXq.etLQat div.sc-kAyceB.iShCeB div.sc-dhKdcB.ddLexq div.sc-eqUAAy.cliMhU.email div.input-con.undefined input",
            "xpath=/html/body/div/div[1]/div[2]/div[4]/div[1]/div[1]/input"
        ]

        fill_input(MAIL_INPUT, email)
        
        logger.info("Try to click Send mail btn")

        SENDMAIL_BTN = [
            ".send-code",
            "html.cc--elegant-black body div#root div.sc-gsFSXq.etLQat div.sc-kAyceB.iShCeB div.sc-dhKdcB.ddLexq div.sc-eqUAAy.cliMhU.verification-code div.input-con.undefined div.right-part.send-code",
            "xpath=/html/body/div/div[1]/div[2]/div[4]/div[2]/div[1]/div[2]"
        ]
        
        click_btn(SENDMAIL_BTN)

        trae_code = mail.wait_for_trae_code(email)
        if trae_code:
            logger.info(f"Received Trae code: {trae_code}")
        else:
            logger.error("Failed to receive Trae code")
        
        PASSWORD_INPUT = [
            "div.sc-eqUAAy:nth-child(3) > div:nth-child(1) > input:nth-child(1)"
        ]

        # 获取坐标
        password_input_asix = page.query_selector(PASSWORD_INPUT[0]).bounding_box()
        if password_input_asix:
            logger.info(f"Password input asix: {password_input_asix}")
        else:
            logger.error("Failed to get password input asix")
        
        # 输入验证码
        axis_input([password_input_asix["x"]+10, password_input_asix["y"]-54], trae_code)

        # 随机生成密码
        password = generate_password()
        logger.info(f"Generated password: {password}")

        # 输入密码
        fill_input(PASSWORD_INPUT, password)

        SIGNUP_BTN = [
            "div.sc-gEvEer:nth-child(5)",
            "html.cc--elegant-black body div#root div.sc-gsFSXq.etLQat div.sc-kAyceB.iShCeB div.sc-gEvEer.fQLTLP.mb-8.btn-submit.btn-large.trae__btn",
            "/html/body/div/div[1]/div[2]/div[5]"
        ]

        click_btn(SIGNUP_BTN)

        try:
            page.wait_for_url("https://www.trae.ai/account-setting")
            logger.info("Signup success")
            # time.sleep(30) # 测试用的，你瞅啥 :(
        except Exception as e:
            logger.error(f"Signup failed: {e}")

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Registration process completed in {duration:.2f} seconds")





        
if __name__ == "__main__":
    register()