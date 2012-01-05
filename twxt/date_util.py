#!/user/bin/python2.7

import time;
from datetime import datetime

def str_from_timestamp(timestamp):
	return str_from_datetime(datetime_from_timestamp(timestamp))

def str_from_datetime(date_time):
	return date_time.strftime('%Y-%m-%d %H:%M:%S')

def now_timestamp():
	return timestamp_from_datetime(datetime.now())

#date: datetime
def timestamp_from_datetime(date_time):
    return time.mktime(date_time.timetuple())

def datetime_from_timestamp(timestamp):
	return datetime.fromtimestamp(timestamp)
	
	
def now_datetime():
	return datetime.now()

if __name__ == '__main__':
    print now_timestamp()
    print repr(datetime_from_timestamp(1320908435))
    print str_from_timestamp(1320908435)
    
