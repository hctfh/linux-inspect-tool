# linux-ssh-inspect
异步批量SSH巡检工具，基于asyncio + asyncssh

## 环境
python venv
pip install asyncssh pyyaml

## 测试靶机
本机2个sshd：127.0.0.1:2221、127.0.0.1:2222
真实靶机数量：2

## 运行
python test_conn.py          # 单连接测试
python ssh_inspect.py        # 批量并发巡检
