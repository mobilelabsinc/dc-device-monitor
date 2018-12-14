from datetime import datetime, timedelta, timezone
from DCAPI import DCAPI

import pprint
pp = pprint.PrettyPrinter(indent=4)

check_seconds = 60 * 60 * 24 * 7

host = "10.10.0.31"
user = "admin"
token = "fddc063b-72bc-46a6-9060-6ae256455d5d"


def print_offline_devices(devices):
	now = datetime.now(timezone.utc)
	maxdelta = timedelta(seconds=check_seconds)

	recent_offlines = filter(lambda d: 'lastDisconnectedAt' in d and not d['is_available'] and (now - d['lastDisconnectedAt']) <= maxdelta, devices)
	
	print('The following devices have been offline for less than %d seconds:' % (check_seconds))
	for d in recent_offlines:
		print('%s (%s)\n\t%s\n\t%s' % (d['name'], d['friendlyModel'], d['model'], d['id']))

api = DCAPI(host, user, token, verify=False)
devices = api.devices({'enabled': True, 'availability': 'Offline'})
print_offline_devices(devices)
