import sys
import requests
import json

import cert

voice_file_encoding = 'LINEAR16'
voice_sample_rate = '16000'
voice_language = 'en-US'

req_json_temp = '{"config": {"encoding":"%s","sample_rate":%s,"languageCode":"%s"},"audio":{"uri":"%s"}}'
headers = {'Content-Type': 'application/json'}
request_url_temp = 'https://speech.googleapis.com/v1beta1/speech:asyncrecognize?key=%s'
response_url_temp = 'https://speech.googleapis.com/v1beta1/operations/%s?key=%s'

def speech2text(voice_file_uri):
	req_json = req_json_temp % (voice_file_encoding, voice_sample_rate, voice_language, voice_file_uri)
	req_data = json.loads(req_json)
	url = request_url_temp % (cert.SPEECH_API_KEY, )

	r = requests.post(url, data=json.dumps(req_data), headers=headers)
	task_id = r.json().get('name', 0)
	return task_id


def main():
	voice_file_uri = 'gs://speech2text/Benedict_Evans_Mono.wav'
	task_id = speech2text(voice_file_uri)
	print(response_url_temp % (task_id, cert.SPEECH_API_KEY))


if __name__ == '__main__':
	main()
