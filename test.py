import datetime
from datetime import timezone

now = datetime.datetime.now()
print(now)

print(datetime.datetime.now(tz=timezone.utc))
