import asyncio

async def fib(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a = asyncio.create_task(fib(n-1))
    b = asyncio.create_task(fib(n-2))
    await a
    await b
    return a.result() + b.result()

async def main():
    for i in range(10):
        f = asyncio.create_task(fib(i))
        await f
        print(f.result())

asyncio.run(main())