from datetime import datetime, tzinfo
async def get_current_datetime(timezone: tzinfo):
    return datetime.now(tz=timezone).strftime("[%d-%m-%Y %H:%M:%S]")