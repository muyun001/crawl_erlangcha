from datetime import date, timedelta

yesterday = date.today() + timedelta(days=-1)
print(yesterday)
