import requests
import json
import iso8601

#todo: enum dcapi methods
#todo: enum known props?
#todo: keep_keys isn't general, should filter downstream in client code

class DCAPI:
	__endpoint = '{proto}://{host}/apiv1/'
	
	def __init__(self, host, user, token, proto='https', verify=True):
		self.auth = (user, token)
		self.verify = verify
		# todo: urlparse.unparse or .unsplit
		self.endpoint = DCAPI.__endpoint.format(proto=proto, host=host)
	
	def get(self, resource, params, object_hook):
		url = self.endpoint + resource
		with requests.get(url, auth=self.auth, params=params, verify=self.verify) as res:
			res.raise_for_status()
			return json.loads(res.content, object_hook=object_hook)
	
	def devices(self, props={}):
		return self.get('Device', props, self.as_device)			
	
	@staticmethod
	def as_device(obj):
		keep_keys = ('name', 'id', 'availability', 'enabled',
			'model', 'friendlyModel', 'lastDisconnectedAt')
		datekeys = ('lastDisconnectedAt', 'lastConnectedAt',
			'nextReservationStartTime', 'nextReservationEndTime',
			'lastInuseAt')
		d = { k: obj[k] for k in keep_keys if k in obj}
		d.update((k, iso8601.parse_date(d[k])) for k in datekeys if k in d) #promote datetimes
		d['is_available'] = (d['availability'] == 'Online') # boolified availability
		return d
