import json
import requests
import base64
from datetime import datetime, timedelta, timezone
import iso8601

import pprint
pp = pprint.PrettyPrinter(indent=4)

check_seconds = 60 * 60 * 24 * 7

host = "10.10.0.31"
user = "admin"
token = "fddc063b-72bc-46a6-9060-6ae256455d5d"

# todo: urlparse.unparse or .unsplit
endpoint = 'https://%s/apiv1/' % (host)

def query_devices(props={}):
	url = endpoint + 'Device'
	return requests.get(url, auth=(user, token), params=props, verify=False)

def massage_devices(devices, keys):
	datekeys = ('lastDisconnectedAt', 'lastConnectedAt',
		'nextReservationStartTime', 'nextReservationEndTime',
		'lastInuseAt')
	devices = [ { k: d[k] for k in keys if k in d} for d in devices]
	for d in devices:
		d.update((k, iso8601.parse_date(d[k])) for k in datekeys if k in d)
		d['is_available'] = (d['availability'] == 'Online')
	return devices

def print_offline_devices(devices):
	recent_offlines = filter(lambda d: 'lastDisconnectedAt' in d and not d['is_available'] and (now - d['lastDisconnectedAt']) <= maxdelta, devices)
	
	print('The following devices have been offline for less than %d seconds:' % (check_seconds))
	for d in recent_offlines:
		print('%s (%s)\n\t%s\n\t%s' % (d['name'], d['friendlyModel'], d['model'], d['id']))


with query_devices({'enabled': True, 'availability': 'Offline'}) as res:
	res.raise_for_status()
	
	now = datetime.now(timezone.utc)
	maxdelta = timedelta(seconds=check_seconds)
	
	data = json.loads(res.content)
	keys = ('name', 'id', 'availability', 'enabled', 'model', 'friendlyModel', 'lastDisconnectedAt')
	devices = massage_devices(data, keys)
		
	print_offline_devices(devices)
