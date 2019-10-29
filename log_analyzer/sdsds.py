import datetime


date_time_obj = datetime.datetime.strptime("2019-10-27 22:16:29,317", '%Y-%m-%d %H:%M:%S,%f')

print('Date:', date_time_obj.date())
print('Time:', date_time_obj.time())
print('Date-time:', date_time_obj)
print('Date-time:', date_time_obj.timestamp())


a = "asdafs dfsdf sdf sdf sd f"
print(a[11:-1])