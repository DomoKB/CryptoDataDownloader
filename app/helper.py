from datetime import datetime, timezone

def datetime_from_utc_to_local(utc_datetime, local_tz):
    # Ensure utc_datetime is timezone-aware in UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    else:
        utc_datetime = utc_datetime.astimezone(timezone.utc)
    
    # Convert to the specified local timezone
    local_datetime = utc_datetime.astimezone(local_tz)
    return local_datetime
