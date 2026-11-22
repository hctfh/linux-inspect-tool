# serial_sleep.py
import asyncio
import asyncssh
import yaml
import time

async def run_task(host_info):
    ip = host_info["ip"]
    port = host_info["port"]
    user = host_info["user"]
    pwd = host_info["pwd"]
    try:
        async with asyncssh.connect(
            ip, port=port, username=user, password=pwd,
            known_hosts=None, login_timeout=5, connect_timeout=5
        ) as conn:
            res = await conn.run("sleep 0.5; hostname; cat /proc/loadavg; nproc")
            return f"✅ {ip}:{port} | {res.stdout.strip()}"
    except Exception as e:
        return f"❌ {ip}:{port} | {str(e)}"

async def main():
    with open("hosts.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    hosts = cfg["hosts"]

    start = time.time()
    results = []
    for h in hosts:
        results.append(await run_task(h))
    end = time.time()

    for r in results:
        print(r)
    print(f"\n【串行sleep】总耗时：{end - start:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())

