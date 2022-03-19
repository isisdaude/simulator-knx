import asyncio, aioconsole
from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime


def job(city):
    print("I'm working in %s...The time is: %s" % (city,datetime.now()))


async def start():
    # your infinite loop here, for example:
    while True:
        print('Async ....')
        await asyncio.sleep(5)
        print('      .... Function')

async def finish():
    while True:
        print("Finish ...")
        input = await aioconsole.ainput("Name of teh program? \n")
        print("             ... Program:",input)

async def main():
    task1 = loop.create_task (start())
    task2 = loop.create_task (finish())
    await asyncio.wait([task1, task2])

print("the file is lauched \n")

    #await task2

if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, 'interval', seconds=3, args=['Lausanne'])
    '''
    'date' : to run the code once at a certain time
    scheduler.add_job(job, 'date', run_date = date(2022, 8, 30),args=['Lausanne'])
    # run_date = date(year, month, day) or
    # run_date = datetime(year, month, day, hour, minute, seconds) or
    # run_date = '2022-4-30 08:00:00'
    'interval' : run the job at fixed intervals of time
    'cron' : periodically run the job at certain time(s) of day
    scheduler.add_job(job, 'cron', run_date = date(2022, 8, 30),args=['Lausanne'])

    to remove a job:
    either store the job object with jobObj=scheduler.add_job()
    or assign an id with scheduler.add_job(..., id='job_id_1')
    then jobObj.remove() or scheduler.remove_job('job_id_1')
    to close the scheduler: scheduler.shutdown()
    '''
    scheduler.start()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass

#asyncio.run(main())
#     task = asyncio.Task(start())
#
#     # let script some thime to work:
#     await asyncio.sleep(3)
#
#     # cancel task to avoid warning:
#     task.cancel()
#     with suppress(asyncio.CancelledError):
#         await task  # await for task cancellation
#
#
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# try:
#     loop.run_until_complete(main())
# finally:
#     loop.run_until_complete(loop.shutdown_asyncgens())
#     loop.close()
