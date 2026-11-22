# main_sem.py 带并发限制版本
import asyncio
import asyncssh
import yaml
import time

async def run_task(host_info, sem):
    ip = host_info["ip"]
    port = host_info["port"]
    user = host_info["user"]
    pwd = host_info["pwd"]
    async with sem:
        try:
            async with asyncssh.connect(
                ip, port=port, username=user, password=pwd,
                known_hosts=None, login_timeout=5, connect_timeout=5
            ) as conn:
                # sleep 0.5 模拟慢任务
                res = await conn.run("sleep 0.5; hostname; cat /proc/loadavg; nproc")
                return f"✅ {ip}:{port} | {res.stdout.strip()}"
        except Exception as e:
            return f"❌ {ip}:{port} | {str(e)}"

async def main():
    with open("hosts.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    hosts = cfg["hosts"]
    # 限制最大并发为4，你可以修改这个数字
    sem = asyncio.Semaphore(4)

    start = time.time()
    tasks = [run_task(h, sem) for h in hosts]
    results = await asyncio.gather(*tasks)
    end = time.time()

    for r in results:
        print(r)
    print(f"\n【带并发限制】总耗时：{end - start:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())

