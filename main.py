import os
import os.path
import requests
import json

import cert  # the cert.py file contains a string named SPEECH_API_KEY

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


def speech2text_from_file(infilename, outfilename):
	with open(infilename) as infile, open(outfilename, 'w') as outfile:
		names = infile.readlines()
		tasks = []
		for name in names:
			task_id = speech2text(name.strip())
			tasks.append([name, response_url_temp % (task_id, cert.SPEECH_API_KEY)])
			outfile.write(','.join([name, response_url_temp % (task_id, cert.SPEECH_API_KEY), os.linesep]))
	infile.close()
	outfile.close()


def get_all_result(response_name, result_name):
	with open(response_name) as infile, open(result_name, 'w') as outfile:
		lines = infile.readlines()
		items = dict()
		for line in lines:
			voice_file, link = line.strip().split(',')
			r = requests.get(link)
			items[voice_file] = r.json()
		outfile.write(json.dumps(items, sort_keys=True))
	infile.close()
	outfile.close()


def parse_result_to_script(result_name, script_name):
	with open(result_name) as infile, open(script_name, 'w') as outfile:
		d = json.load(infile)
		lines = []
		for k in sorted(d.keys()):
			items = os.path.split(k)[1].split('_')
			people = items[-3]
			start_ms = int(items[-2])
			start = "%03d:%02d.%03d" % (start_ms//60000, (start_ms % 60000)//1000, start_ms % 1000)
			transcript = []
			for result in d[k]['response'].get("results", []):
				for sentence in result["alternatives"]:
					transcript.append(sentence["transcript"])
			line = '[%s][%s]: %s\n' % (start, people, '.'.join(transcript))
			lines.append(line)
		outfile.writelines(lines)
	infile.close()
	outfile.close()


def do_tasks_from_file(task, response, result, script):
	speech2text_from_file(task, response)
	get_all_result(response, result)
	parse_result_to_script(result, script)


def main():
	do_tasks_from_file('tasks.txt', 'task_response.txt', 'result.txt', 'script.txt')


if __name__ == '__main__':
	main()
