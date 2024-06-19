import asyncio
import subprocess


async def run_script(script_path):
    process = await asyncio.create_subprocess_exec(
        'python', script_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if stdout:
        print(f'[stdout]: {stdout.decode()}')
    if stderr:
        print(f'[stderr]: {stderr.decode()}')


async def main():
    script1 = run_script('controller.py')
    script2 = run_script('listener.py')

    # Run both scripts concurrently
    await asyncio.gather(script1, script2)


if __name__ == '__main__':
    asyncio.run(main())
