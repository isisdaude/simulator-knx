
import schedule
import time
import aioconsole, asyncio

def job():
    print("I'm working...")
async def work():
    subject = await aioconsole.ainput("What subject are you workign on? ")
    print("I'm still working on ", subject)
schedule.every(4).seconds.do(work)
schedule.every(1).seconds.do(job)


while True:
    schedule.run_pending()
    time.sleep(0.5)
