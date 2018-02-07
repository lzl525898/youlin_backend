# coding:utf-8
from . import commons
from models import *
from core.settings import HOST_IP,NEW_VERSION_URL
import re
import json

def download(request):
	apkObj = APK.objects.latest('v_id')
	res_data = {
		"v_url": HOST_IP + str(apkObj.v_url)
	}
	return commons.render_template(request, "site/download.html",res_data)

def index(request):
	try:
		aObj = APK.objects.filter(v_name__contains="A").latest('v_id')
		a_url = NEW_VERSION_URL
	except:
		a_url = "#"
	try:
		iObj = APK.objects.filter(v_name__contains="I").latest('v_id')
		i_url = HOST_IP + str(iObj.v_url)
	except:
		i_url = "#"
	res_data = {
		"a_url": a_url,
		"i_url":i_url
	}
	return commons.render_template(request, "site/index.html",res_data)


def yllife(request):
	
	try:
		ylObjs = YLife.objects.filter(yl_flag =1).order_by("-yl_id")
	except Exception,e:
		return commons.res_fail(1, e)
	
	data = []
	if ylObjs is not None:
		for ylObj in ylObjs:
			dict = {}
			dict.setdefault("yl_title",ylObj.yl_title)
			dict.setdefault("yl_author",ylObj.yl_author)
			dict.setdefault("yl_date",ylObj.yl_date)
			#dict.setdefault("yl_content",ylObj.yl_content)
			dict.setdefault("yl_avatar",ylObj.yl_avatar)
			dict.setdefault("yl_id",ylObj.yl_id)
			pics = re.findall('src="(.*?)"',ylObj.yl_content)
			if len(pics):
				dict.setdefault("yl_pic",pics[0])
			else:
				dict.setdefault("yl_pic","/static/assets/css/images/b1.jpg")
			brief_contents = re.findall('(?<=\<p\>).*?(?=\<\/p\>)',ylObj.yl_content)
			dict.setdefault("yl_bc",brief_contents[1])
			data.append(dict)
		return commons.render_template(request, "site/yllife.html",data)
	else:
		return commons.res_fail(1, "该数据不存在") 
	
def content(request):
	if request.method == 'GET':
		id		 = request.GET.get('id', None)
	else:
		return commons.res_fail(1, "请用GET方式")
	try:
		ylObj = YLife.objects.get(yl_id =id)
	except Exception,e:
		return commons.res_fail(1, "该数据不存在")

	content = "<h1>"+ylObj.yl_title+"</h1><br>"+ylObj.yl_content
	res_data = {
		"title": ylObj.yl_title,
		"author": ylObj.yl_author,
		"date": ylObj.yl_date,
		"content":content,
		"avatar":ylObj.yl_avatar,
	}
	
	return commons.render_template(request,"site/preview.html",res_data)
	
	
def contact(request):
	
		
	return commons.render_template(request,"site/contact.html")
	


def privacy_clause(request):
	return commons.render_template(request, "site/privacy_clause.html")



