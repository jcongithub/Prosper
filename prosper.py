from secret import *
import requests
import pandas as pd
pd.options.display.width = 1000

base_uri = "https://api.prosper.com/v1"
token = ''

def get_token():
	url = "https://api.prosper.com/v1/security/oauth/token"
	params = {
		"grant_type"    : "password",
		"client_id"     : client_id,
		"client_secret" : client_secret,
		"username"      : username,
		"password"      : password
	}

	#payload = "grant_type=password&client_id=" + client_id + "&client_secret=" + client_secret + "&username=" + username + "&password=" + password
	headers = { 'accept': "application/json", 'content-type': "application/x-www-form-urlencoded" }
	#response = requests.request("POST", url, data=payload, headers=headers)
	response = requests.request("POST", url, params=params, headers=headers)
	#print(response.text)

	return response.json()

def notes():	
	token = get_token()
	limit = 100
	offset = 0
	result_count = 0
	total_count = 1

	print(token)
	url = base_uri + "/notes/"
	headers = { 'accept': "application/json", "authorization": "bearer " + token['access_token'] }
	
	notes = pd.DataFrame()
	while (offset < total_count):
		params = {"offset" : offset, "limit" : limit}
		response = requests.request("GET", url, params=params, headers=headers).json()
		result_count = response['result_count']
		total_count = response['total_count']
		print('offset:{} result_count:{} total_count:{}'.format(offset, result_count, total_count))
		offset = offset + result_count

		subset_notes = pd.DataFrame(response['result'])
		notes = notes.append(subset_notes, ignore_index=True)

	return notes

def listing():
	token = get_token()
	limit = 500
	offset = 0
	result_count = 0
	total_count = 1

	print(token)
	url = "https://api.prosper.com/listingsvc/v2/listings/?biddable=false"
	headers = { 'accept': "application/json", "authorization": "bearer " + token['access_token'] }
	params = {"limit" : limit}
	response = requests.request("GET", url, params=params, headers=headers).json()	
	print(response)
	result_count = response['result_count']
	print("result_count:{}".format(result_count))
	total_count = response['total_count']
	print("total_count:{}".format(total_count))

	listings = pd.DataFrame(response['result'])
	print(listings)
	return listings

	# notes = pd.DataFrame()
	# while (offset < total_count):
	# 	params = {"offset" : offset, "limit" : limit}
	# 	response = requests.request("GET", url, params=params, headers=headers).json()
	# 	result_count = response['result_count']
	# 	total_count = response['total_count']
	# 	print('offset:{} result_count:{} total_count:{}'.format(offset, result_count, total_count))
	# 	offset = offset + result_count

	# 	subset_notes = pd.DataFrame(response['result'])
	# 	notes = notes.append(subset_notes, ignore_index=True)

	# return notes


	

def account():
	token = get_token()
	headers = { 'accept': "application/json", "authorization": "bearer " + token['access_token'] }
	url = base_uri + "/accounts/prosper/"
	response = requests.request("GET", url, headers=headers).json()
	print(response)
	return pd.DataFrame(response)


