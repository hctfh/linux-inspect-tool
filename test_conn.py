import asyncio
import asyncssh

async def main():
    async with asyncssh.connect(
        "127.0.0.1", port=2221, username="test", password="test",
        known_hosts=None, login_timeout=5
    ) as conn:
        r = await conn.run("hostname; cat /proc/loadavg; nproc")
        print("hostname/load/nproc:")
        print(r.stdout.strip())

asyncio.run(main())
