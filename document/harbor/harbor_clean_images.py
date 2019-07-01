#! /usr/bin/env python
# -*- coding:utf-8 -*-


import requests
import json


class RequestClient(object):

	def __init__(self, login_url, username, password):
		self.username = username
		self.password = password
		self.login_url = login_url
		self.session = requests.Session()
		self.login()

	def login(self):
		self.session.post(self.login_url, params = {"principal": self.username, "password": self.password})


class ClearHarbor(object):

	def __init__(self, harbor_domain, password, schema = "https",
	             username = "admin"):
		self.schema = schema
		self.harbor_domain = harbor_domain
		self.harbor_url = self.schema + "://" + self.harbor_domain
		self.login_url = self.harbor_url + "/login"
		self.api_url = self.harbor_url + "/api"
		self.pro_url = self.api_url + "/projects"
		self.repos_url = self.api_url + "/repositories"
		self.username = username
		self.password = password
		self.client = RequestClient(self.login_url, self.username, self.password)

	def __fetch_pros_obj(self):
		# TODO
		self.pros_obj = self.client.session.get(self.pro_url).json()
		return self.pros_obj

	def fetch_pros_id(self):
		self.pros_id = []
		# TODO
		pro_res = self.__fetch_pros_obj()
		for i in pro_res:
			self.pros_id.append(i['project_id'])
		return self.pros_id

	def fetch_del_repos_name(self, pro_id):
		self.del_repos_name = []
		repos_res = self.client.session.get(self.repos_url, params = {"project_id": pro_id})
		# TODO
		for repo in repos_res.json():
			if repo["tags_count"] > 30:
				self.del_repos_name.append(repo['name'])
		return self.del_repos_name

	def fetch_del_repos(self, repo_name):
		self.del_res = []
		tag_url = self.repos_url + "/" + repo_name + "/tags"
		# TODO
		tags = self.client.session.get(tag_url).json()
		tags_sort = sorted(tags, key = lambda a: a["created"])
		# print(tags_sort)
		del_tags = tags_sort[0:len(tags_sort) - 30]
		# print(del_tags)
		for tag in del_tags:
			del_repo_tag_url = tag_url + "/" + tag['name']
			print(del_repo_tag_url)
			del_res = self.client.session.delete(del_repo_tag_url)
			self.del_res.append(del_res)

		return self.del_res


if __name__ == "__main__":

	harbor_domain = "hub.test.com"
	password = "xxxxxxx"
	res = ClearHarbor(harbor_domain, password)
	# 循环所有的project id
	for i in res.fetch_pros_id():
		# 获取所有tag超过30的repos
		repos = res.fetch_del_repos_name(i)
		if repos:
			print(repos)
			for repo in repos:
				del_repos = res.fetch_del_repos(repo)
				print(del_repos)
