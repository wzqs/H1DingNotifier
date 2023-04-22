# H1DingNotifier
H1DingNotifier是一款开源工具，实时监控HackerOne报告并自动推送至钉钉。通过追踪推特账号，帮助安全团队掌握最新公开的漏洞信息。轻量级且配置简单，适用于各种规模的组织和个人。PS: 源代码由 ChatGPT 编写。

![image](https://user-images.githubusercontent.com/71961807/233784860-16e5c475-1d64-4d21-af63-3531fff3e709.png)


# Usage

1. 创建钉钉机器人，选择自定义 WEBHOOK 类型，可通过自定义关键词或 IP 地址进行安全设置。创建完成后，复制机器人的 accesstoken。
2. 将源代码中的 accesstoken 替换为您自己的，使用 Python3.8.X 在后台运行。您可以直接输入 `python3 h1_notifier.py` & 或在 tmux 中运行。

PS: 若提示缺少库，请根据提示使用 `pip` 进行安装。
