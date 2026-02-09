from faulthandler import is_enabled
from playwright.sync_api import Page
from camoufox.sync_api import Camoufox
import time
from ext.gmail import TempGmail
from ext import log

logger = log.setup_logger()

mail = TempGmail()


def register():
    with Camoufox(
        headless=False,
        os="windows",
        geoip=True,
        window=(1280, 720),
        humanize=True
    ) as browser:
        page: Page = browser.new_page() 
        page.goto("https://zenmux.ai")

        logger.info("wait element load")

        # wait load
        page.wait_for_selector("button.bg-black:nth-child(4)")

        logger.info("click sign in button")

        SIGNIN_SELECTORS = [
            "button.bg-black:nth-child(4)",
            "html.light body div#root div.css-1u6ggfm.ant-app.css-var-r0 div div.p-0.pt-sans div.w-full.h-screen.flex.relative.bg-[#fafafa].dark:bg-[#1a1a1a] div.w-full.h-full.absolute.top-[0px].left-[0px] div.fixed.top-0.left-0.w-full.z-50.select-none div.w-full.flex.items-center.px-4.md:px-[20px].bg-transparent.justify-between.h-[56px] button.bg-black.min-w-[74px].h-[34px].rounded-[8px].flex.items-center.justify-center.text-white",
            "xpath=/html/body/div/div/div/div/div[1]/div[1]/div/div[2]/button"
        ]
        for selector in SIGNIN_SELECTORS:
            try:
                logger.info(f"try click {selector}")
                page.click(selector)
                logger.info(f"click {selector} success")
                # time.sleep(10) # 观察用的
                break
            except:
                logger.info(f"click {selector} failed")
                pass
        
        time.sleep(0.1)
        logger.info("Click continue with email button")

        CONTINUE_EMAIL_BTN = [
            "button.ant-btn:nth-child(3)",
            "html.light body div.ant-modal-root.css-1u6ggfm.modal-container-VNDKvDB_.undefined.css-var-r9.ant-modal-css-var div.ant-modal-wrap.ant-modal-centered div.ant-modal.css-1u6ggfm div div.ant-modal-content div.ant-modal-body div.mt-[4px].mb-[8px] div.ant-spin-nested-loading.css-1u6ggfm.css-var-r9 div.ant-spin-container div.min-h-[230px] div button.ant-btn.css-1u6ggfm.css-var-r9.ant-btn-primary.ant-btn-color-primary.ant-btn-variant-solid.ant-btn-block.primary-container-PueuJAL9.!font-normal.!h-[48px].text-[16px].h-[48px]",
            "xpath=/html/body/div[2]/div[2]/div/div[1]/div/div/div/div/div/div[2]/div/button[3]"
        ]

        for selector in CONTINUE_EMAIL_BTN:
            try:
                logger.info(f"try click {selector}")
                page.click(selector)
                logger.info(f"click {selector} success")
                # time.sleep(30)
                break
            except:
                logger.info(f"click {selector} failed")
                pass
        
        # 锚点路径
        CLOUDFLARE_TURNSTLIE_ANCHOR = [
            "span.text-\[16px\]:nth-child(1)",
            "html.light body div.ant-modal-root.css-1u6ggfm.modal-container-VNDKvDB_.undefined.css-var-r9.ant-modal-css-var div.ant-modal-wrap.ant-modal-centered div.ant-modal.css-1u6ggfm div div.ant-modal-content div.ant-modal-body div.mt-[4px].mb-[8px] div.ant-spin-nested-loading.css-1u6ggfm.css-var-r9 div.ant-spin-container div.min-h-[230px] form.ant-form.ant-form-vertical.css-var-r9.ant-form-css-var.css-1u6ggfm div.ant-form-item.css-var-r9.ant-form-css-var.css-1u6ggfm.mb-0.ant-form-item-vertical div.ant-row.ant-form-item-row.css-1u6ggfm.css-var-r9 div.ant-col.ant-form-item-label.css-1u6ggfm.css-var-r9 label span.text-[16px].text-[#666]",
            "xpath=/html/body/div[2]/div[2]/div/div[1]/div/div/div/div/div/div[2]/form/div[1]/div/div[1]/label/span"
        ]
        def click_turnstlie():
            time.sleep(10)
            # Get anchor point
            for anchor in CLOUDFLARE_TURNSTLIE_ANCHOR:
                try:
                    logger.info(f"try get anchor {anchor}")
                    element = page.query_selector(anchor)
                    logger.info(f"get anchor {anchor} success")
                    break
                except:
                    logger.info(f"get anchor {anchor} failed")
                    pass
            
            try:
                anchor_axis = element.bounding_box()
                logger.info(f"get anchor axis success: {anchor_axis}")
            except:
                logger.info(f"get anchor axis failed")

            # 基于偏移量计算Cloudflare Turnstlie
            # X坐标
            turnstlie_x = anchor_axis["x"] + 20
            # Y坐标
            turnstlie_y = anchor_axis["y"] + 110
            logger.info(f"Calculate turnstlie axis success: x={turnstlie_x}, y={turnstlie_y}")
            # 点击Cloudflare Turnstlie
            try:
                page.mouse.click(turnstlie_x, turnstlie_y)
                logger.info(f"Click turnstlie success")
                time.sleep(1)
            except:
                logger.info(f"Click turnstlie failed")
        click_turnstlie()

            
        # Input Email
        # wait load
        EMAIL_INPUT = [
            "#email",
            "html.light body div.ant-modal-root.css-1u6ggfm.modal-container-VNDKvDB_.undefined.css-var-r9.ant-modal-css-var div.ant-modal-wrap.ant-modal-centered div.ant-modal.css-1u6ggfm div div.ant-modal-content div.ant-modal-body div.mt-[4px].mb-[8px] div.ant-spin-nested-loading.css-1u6ggfm.css-var-r9 div.ant-spin-container div.min-h-[230px] form.ant-form.ant-form-vertical.css-var-r9.ant-form-css-var.css-1u6ggfm div.ant-form-item.css-var-r9.ant-form-css-var.css-1u6ggfm.mb-0.ant-form-item-with-help.ant-form-item-has-error.ant-form-item-vertical div.ant-row.ant-form-item-row.css-1u6ggfm.css-var-r9 div.ant-col.ant-form-item-control.css-1u6ggfm.css-var-r9 div.ant-form-item-control-input div.ant-form-item-control-input-content input#email.ant-input.css-1u6ggfm.ant-input-outlined.ant-input-status-error.h-[40px].pt-[8px].pb-[8px].pl-[12px].pr-[12px].rounded-[8px].css-var-r9.ant-input-css-var",
            "xpath=//*[@id=\"email\"]"
        ]

        email = mail.generate_email()
        logger.info(f"正在输入邮箱: {email}")

        for selector in EMAIL_INPUT:
            try:
                logger.info(f"try input email {selector}")
                page.fill(selector, email)
                logger.info(f"input email {selector} success")
                time.sleep(0.1)
                break
            except:
                logger.info(f"input email {selector} failed")
                pass
        
        logger.info(f"input email {selector} success, email: {email}")
        
        # click send mail button
        SEND_MAIL_BTN = [
            ".ant-btn",
            "html.light body div.ant-modal-root.css-1u6ggfm.modal-container-VNDKvDB_.undefined.css-var-r9.ant-modal-css-var div.ant-modal-wrap.ant-modal-centered div.ant-modal.css-1u6ggfm div div.ant-modal-content div.ant-modal-body div.mt-[4px].mb-[8px] div.ant-spin-nested-loading.css-1u6ggfm.css-var-r9 div.ant-spin-container div.min-h-[230px] form.ant-form.ant-form-vertical.css-var-r9.ant-form-css-var.css-1u6ggfm div.ant-form-item.mb-0.css-var-r9.ant-form-css-var.css-1u6ggfm.ant-form-item-vertical div.ant-row.ant-form-item-row.css-1u6ggfm.css-var-r9 div.ant-col.ant-form-item-control.css-1u6ggfm.css-var-r9 div.ant-form-item-control-input div.ant-form-item-control-input-content button.ant-btn.css-1u6ggfm.css-var-r9.ant-btn-primary.ant-btn-color-primary.ant-btn-variant-solid.ant-btn-block.primary-container-PueuJAL9.!h-[44px].text-[16px].h-[48px]",
            "/html/body/div[2]/div[2]/div/div[1]/div/div/div/div/div/div[2]/form/div[3]/div/div/div/div/button"
        ]
        
        for selector in SEND_MAIL_BTN:
            try:
                logger.info(f"try click send mail button {selector}")
                page.click(selector)
                logger.info(f"click send mail button {selector} success")
                # time.sleep(10)
                break
            except:
                logger.info(f"click send mail button {selector} failed")
                pass
        

        link = mail.wait_for_zenmux_link(email)

        if link:
            logger.info(f"get zenmux link success: {link}")
        else:
            logger.info(f"get zenmux link failed")
        
        page.goto(link)

        time.sleep(200)



        
if __name__ == "__main__":
    register()