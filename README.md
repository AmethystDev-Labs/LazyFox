# LazyFox

> Hey! Lazyfox!

一个用于浏览器自动化与常见逆向场景的 Python 模板仓库。

当前内置能力：
- 彩色日志模块（`ext/log.py`）
- 临时邮箱模块（`ext/gmail.py`、`ext/mail_service.py`）
- 两个站点流程示例（`demo/trae.py`、`demo/zenmux.py`）

本模板还在 `requirements.txt` 中添加了Camoufox, Playwright, httpx, curl_cffi等常用工具

> 说明：本项目更偏“模板/脚手架”，适合二次开发，不是稳定生产工具。

## 环境要求

- Python 3.12+

## 安装

### 方式 1：使用 `uv`（推荐）

```bash
uv sync
```

### 方式 2：使用 `pip`

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 快速开始

运行项目入口：

```bash
python main.py
```

运行模块测试：

```bash
python ext/test.py
```

运行 Trae 示例：

```bash
python demo/trae.py
```

运行 Zenmux 示例：

```bash
python demo/zenmux.py
```

## 项目结构

```text
LazyFox/
├─ main.py                 # 项目入口（欢迎信息）
├─ demo/
│  ├─ trae.py              # Trae 注册流程示例
│  └─ zenmux.py            # Zenmux 登录/注册流程示例
├─ ext/
│  ├─ log.py               # 日志模块
│  ├─ gmail.py             # emailnator 临时邮箱封装（同步+异步）
│  ├─ mail_service.py      # 另一套临时邮箱 API 封装
│  ├─ test.py              # 模块测试脚本
│  └─ __init__.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

## 模板定位

这个仓库适合作为以下工作的起点：
- 新站点自动化流程 PoC
- 逆向接口调试时的基础工程
- 邮件验证码/邮件链接抓取的流程打通
- 注册机

## Tips

- 本项目默认按 Windows 指纹参数配置，若需其他系统/设备，请修改 `demo/zenmux.py` 中 `Camoufox` 初始化参数。
- 目前Camoufox FF146 在 MacOS 有大量问题，请降级至 FF135

## 提出你的建议
要提出建议，请通过以下联系方式联系我：
- 邮箱：[liu_qinyu@outlook.com](mailto:liu_qinyu@outlook.com)
- LinuxDO: [Lonely](https://linux.do/u/Lonely)
- QQ: 1280993766

> Made with ❤️ by Lonely