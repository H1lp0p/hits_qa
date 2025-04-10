from datetime import datetime

test_date = datetime.today().date()

print(datetime.combine(test_date, datetime.min.time()))