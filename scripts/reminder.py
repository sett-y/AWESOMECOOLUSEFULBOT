import asyncio

#this now only takes the time
async def remind(datestr: str) -> list[str]:
    hour = 0
    minute = 0.0
    dateli = datestr.split(' ')

    #in case user only adds 1 time argument
    #arguments will now only be <hour> <minute>
    if len(dateli) == 1:
        hour = int(dateli[0])
    else:
        hour = int(dateli[0])
        minute = float(dateli[1])

    #cant believe i tried to use a datetime object for this at first
    time_seconds = (hour * 3600) + (minute * 60)
    print(f"sleeping for {time_seconds} seconds")
    await asyncio.sleep(time_seconds)

    return dateli