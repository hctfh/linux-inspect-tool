import asyncio
import asyncssh
import yaml
import time
import argparse

async def run_task(host_info, sem, cmd, retry=1):
    ip = host_info["ip"]
    port = host_info["port"]
    user = host_info["user"]
    pwd = host_info["pwd"]
    async with sem:
        for attempt in range(retry):
            try:
                async with asyncssh.connect(
                    ip, port=port, username=user, password=pwd,
                    known_hosts=None, login_timeout=5, connect_timeout=5
                ) as conn:
                    res = await conn.run(cmd)
                    return {
                        "status": "ok",
                        "ip": f"{ip}:{port}",
                        "stdout": res.stdout.strip(),
                        "stderr": res.stderr.strip()
                    }
            except Exception as e:
                if attempt == retry - 1:
                    return {
                        "status": "fail",
                        "ip": f"{ip}:{port}",
                        "err": str(e)
                    }
                await asyncio.sleep(0.3)

async def main():
    parser = argparse.ArgumentParser(description="批量主机SSH巡检工具")
    parser.add_argument("-f", "--file", default="hosts.yaml", help="主机清单yaml")
    parser.add_argument("-c", "--cmd", default="hostname; cat /proc/loadavg; nproc", help="远程执行命令")
    parser.add_argument("-n", "--concurrency", type=int, default=4, help="最大并发数")
    parser.add_argument("-r", "--retry", type=int, default=1, help="失败重试次数")
    parser.add_argument("-o", "--output", help="结果输出文件")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    hosts = cfg["hosts"]

    sem = asyncio.Semaphore(args.concurrency)
    start = time.time()
    tasks = [run_task(h, sem, args.cmd, args.retry) for h in hosts]
    results = await asyncio.gather(*tasks)
    end = time.time()

    output_lines = []
    for item in results:
        if item["status"] == "ok":
            line = f"✅ {item['ip']}\n{item['stdout']}"
        else:
            line = f"❌ {item['ip']} | {item['err']}"
        print(line)
        output_lines.append(line)

    print(f"\n总耗时：{end - start:.2f} 秒")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fw:
            fw.write("\n".join(output_lines))

if __name__ == "__main__":
    asyncio.run(main())
