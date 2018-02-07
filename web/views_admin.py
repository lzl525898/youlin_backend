# coding:utf-8
from django.core.context_processors import request
from . import commons
from . import cfg
import time
import random
import sys
import os
import platform
import django
from django.http import HttpResponse,StreamingHttpResponse
from django.http import HttpResponseRedirect,Http404
from users.models import FamilyRecord
from addrinfo.models import City,Community,Block,BuildNum,AptNum,AddressDetails
from users.models import User,Admin
from feedback.models import OpinionRecord
from users.views import genAdminContentDict,genAdminDetailDict
from push.views import createPushRecord,readIni
from push.sample import pushMsgToTag,pushMsgToSingleDevice
from django.conf import settings
import jpush as jpush
import json
from community.models import Topic,SayHello
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from models import *
from django.shortcuts import render,render_to_response
from HTMLParser import HTMLParser
from PIL import Image
from addrinfo.models import City,Community
from feedback.models import OpinionRecord
from property.models import PropertyInfo
from web.tasks import *
from users.easemob_server import registUser
from exchange.models import *
import xlwt
import datetime
from django.core.servers.basehttp import FileWrapper
import re
from web.utils import *
from users.tasks import AsyncForcedReturn

def testajax(request):
	res_data = {}
	return commons.render_template(request,"ajax.html",res_data)

#订单支付	
def youlinPay(request):
	res_data = {}
	if request.method == 'POST':
		price = request.POST.get('price',None)
	else:
		price = request.GET.get('price',None)
	res_data = {
		"price":price
	}
	return commons.render_template(request,"square/youlinPay.html",res_data)
	
#订单提交	
def submitOrder(request):
	res_data = {}
	if request.method == 'POST':
		addressId  = request.POST.get('address_id',None)
		addrDetail = request.POST.get('addr_detail',None)
		addrName   = request.POST.get('addr_name',None)
		addrPhone  = request.POST.get('addr_phone',None)
		title      = request.POST.get('title',None)
		color      = request.POST.get('color',None)
		size       = request.POST.get('size',None)
		price      = request.POST.get('price',None)
		count      = request.POST.get('count',None)
	else:
		addressId  = request.GET.get('address_id',None)
		addrDetail = request.GET.get('addr_detail',None)
		addrName   = request.GET.get('addr_name',None)
		addrPhone  = request.GET.get('addr_phone',None)
		title      = request.GET.get('title',None)
		color      = request.GET.get('color',None)
		size       = request.GET.get('size',None)
		price      = request.GET.get('price',None)
		count      = request.GET.get('count',None)
	res_data = {
		'addressId':addressId,
		'addrDetail':addrDetail,
		'addrName':addrName,
		'addrPhone':addrPhone,
		'title':title,
		'color':color,
		'size':size,
		'price':price,
		'count':count
	}
	return commons.render_template(request,"square/submitOrder.html",res_data)
	
#物品详情	
def goodsDetail(request):
	res_data = {}
	if request.method == 'POST':
		communityId = request.POST.get('community_id',None)
		userId 		= request.POST.get('user_id',None)
		sgId 		= request.POST.get('sg_id',None)
	else:
		communityId = request.GET.get('community_id',None)
		userId 		= request.GET.get('user_id',None)
		sgId 		= request.GET.get('sg_id',None)
	res_data = {
		"communityId":communityId,
		"userId":userId,
		"sgId":sgId
	}
	return commons.render_template(request,"square/goodsDetail.html",res_data)
		
#物品列表	
def listGoods(request):
	res_data = {}
	if request.method == 'POST':
		communityId = request.POST.get('community_id',None)
	else:
		communityId = request.GET.get('community_id',None)
	res_data = {
		"communityId":communityId
	}
	return commons.render_template(request,"square/listGoods.html",res_data)
	
#地址创建	
def addressCreate(request):
	res_data = {}
	if request.method == 'POST':
		userId = request.POST.get('user_id',None)
		mCount = request.POST.get('count',None)
		type   = request.POST.get('type',None)
		defaultFlag=request.POST.get('default_flag',None)
		addressId=request.POST.get('address_id',None)
	else:
		userId = request.GET.get('user_id',None)
		mCount = request.GET.get('count',None)
		type   = request.GET.get('type',None)
		defaultFlag=request.GET.get('default_flag',None)
		addressId=request.GET.get('address_id',None)
	res_data = {
		"userId":userId,
		"count" :mCount,
		"type"  :type,
		"defaultFlag":defaultFlag,
		"addressId":addressId
	}
	
	return commons.render_template(request,"square/addressCreate.html",res_data);
#地址	
def address(request):
	res_data = {}
	if request.method == 'POST':
		userId = request.POST.get('user_id',None)
		addressId = request.POST.get('address_id',None)
	else:
		userId = request.GET.get('user_id',None)
		addressId = request.GET.get('address_id',None)
	res_data = {
		"userId":userId,
		"addressId":addressId
	}
	return commons.render_template(request,"square/address.html",res_data)
	
#报名	
def signUp(request):
	res_data = {}
	return commons.render_template(request,"square/signUp.html",res_data)
	
#广场
def mySquare(request):
	res_data = {}
	if request.method == 'POST':
		communityId = request.POST.get('community_id',None)
	else:
		communityId = request.GET.get('community_id',None)
	res_data = {
		"communityId":communityId
	}
	return commons.render_template(request,"square/mySquare.html",res_data)
	
#培训	
def myTraining(request):
	res_data = {}
	return commons.render_template(request,"square/myTraining.html",res_data)
	
#培训详情
def myTrainDetail(request):
	res_data = {}
	if request.method == 'POST':
		name = request.POST.get('name',None)
	else:
		name = request.GET.get('name',None)
	res_data = {
		"temp":name
	}
	return commons.render_template(request,"square/myTrainDetail.html",res_data)

#物品-我的
def ReplacementList(request):
	res_data = {}
	if request.method == 'POST':
		communityId = request.POST.get('community_id',None)
		topicId     = request.POST.get('topic_id',None)
		userId      = request.POST.get('user_id',None)
		userType    = request.POST.get('user_type',None)
	else:
		communityId = request.GET.get('community_id',None)
		topicId     = request.GET.get('topic_id',None)
		userId      = request.GET.get('user_id',None)
		userType    = request.GET.get('user_type',None)
	res_data = {
		"communityId":communityId,
		"topicId" : topicId,
		"userId":userId,
		"userType":userType
	}
	return commons.render_template(request,"square/myRepIndex.html",res_data)
#详情
def circleDetail(request):
	res_data = {}
	if request.method == 'POST':
		topicId = request.POST.get('topic_id',None)
		communityId = request.POST.get('community_id',None)
		userId      = request.POST.get('user_id',None)
		userType    = request.POST.get('user_type',None)
		senderId    = request.POST.get('sender_id',None)
	else:
		topicId = request.GET.get('topic_id',None)
		communityId = request.GET.get('community_id',None)
		userId      = request.GET.get('user_id',None)
		userType    = request.GET.get('user_type',None)
		senderId    = request.GET.get('sender_id',None)
	res_data = {
		"topicId" : topicId,
		"communityId" : communityId,
		"userId" : userId,
		"userType" : userType,
		"senderId" : senderId
	}
	return commons.render_template(request,"square/replaceDetail.html",res_data)
	
#详情
def wantPersonList(request):
	res_data = {}
	if request.method == 'POST':
		topicId = request.POST.get('topic_id',None)
		userId  = request.POST.get('user_id',None)
	else:
		topicId = request.GET.get('topic_id',None)
		userId  = request.GET.get('user_id',None)
	res_data = {
		"topicId" : topicId,
		"userId" : userId
	}
	return commons.render_template(request,"square/wantPersonList.html",res_data)
	
#我发布的
def myPush(request):
	res_data = {}
	if request.method == 'POST':
		communityId = request.POST.get('community_id',None)
		userId      = request.POST.get('user_id',None)
		userType    = request.POST.get('user_type',None)
		type        = request.POST.get('type',None)
		topicType   = request.POST.get('topic_type',None)   
	else:
		communityId = request.GET.get('community_id',None)
		userId      = request.GET.get('user_id',None)
		userType    = request.GET.get('user_type',None)
		type        = request.GET.get('type',None)
		topicType   = request.GET.get('topic_type',None)   
	res_data = {
		"userId" : userId,
		"communityId" : communityId,
		"userType" : userType,
		"type" : type,
		"topicType" : topicType
	}
	return commons.render_template(request,"square/myPush.html",res_data)
#搜索
def mySearch(request):
	res_data = {}
	if request.method == 'POST':
		communityId = request.POST.get('community_id',None)
		userId      = request.POST.get('user_id',None)
		userType    = request.POST.get('user_type',None)
		topicType   = request.POST.get('topic_type',None)
		type        = request.POST.get('type',None) 
	else:
		communityId = request.GET.get('community_id',None)
		userId      = request.GET.get('user_id',None)
		userType    = request.GET.get('user_type',None)
		topicType   = request.GET.get('topic_type',None)   
		type        = request.GET.get('type',None)
	res_data = {
		"userId" : userId,
		"communityId" : communityId,
		"userType" : userType,
		"topicType" : topicType,
		"type" : type
	}
	return commons.render_template(request,"square/mySearch.html",res_data)

def DevicePay(request):
	res_data = {}
	return commons.render_template(request,"pay/pay.html",res_data)

def IntegralInfo(request):
	res_data = {
        "info_list":[
				 {'info':'签到第1天可获得','integral':'+5'},
				 {'info':'签到第2天可获得','integral':'+7'},
				 {'info':'签到第3天可获得','integral':'+10'},
				 {'info':'签到第4天可获得','integral':'+13'},
				 {'info':'签到第5天或5天以上每天即可获得','integral':'+15'}
			   ],
		"question_list":{
				 'first' :'Q1 签到规则是什么？',
				 'second':'Q2 积分从哪里赚？',
				 'third' :'Q3 积分干什么用？'
			   },
		"content_list":{
				 'first' :{
						'detail1':'每天登陆优邻APP，点击我页右上角的"签到"按钮，进入签到页面进行签到，即可获得相应数量的积分。',
						'detail2':'(签到中断后，累积的连续签到天数将重新计算哦)'
						},
				 'second':{
						'title1' :'1.每日签到赚积分',
						'detail1':'APP我页右上角点击"签到"按钮即可进行签到。',
						'title2' :'2.发帖子赚积分',
						'detail2':'每天在邻居圈发布新话题、活动（每日上限）获取相应积分。',
						'title3' :'3.邀请新用户',
						'detail3':'可以通过手机号对新用户进行邀请，邀请成功后邀请者与被邀请者将获取相应积分。',
						},
				 'third' :'通过签到、发帖、邀请获得的积分可以用来兑换精美礼品，精彩的活动也需要用到哦!'
			   }
        }
	return commons.render_template(request,"integral/index.html",res_data)

def guaguale(request):
    res_data = {
        "title": "title",
        "content": "content"
        }
    return commons.render_template(request,"guaguale/index.html")
#     return commons.render_template(request, "baoxiang/baoxiang.html", res_data)

def baoxiang(request):
    res_data = {
        "title": "test",
        "content": "content"
        }
    return commons.render_template(request,"baoxiang/index.html",res_data)

#验证用户
def verify_user(request):
    if request.method == 'GET':
       name       	= 	request.GET.get('name',None)
       name1			=name or None
       if name1 == None:
       	return commons.res_fail(1, "请输入用户名")
       else:
	    try:
	        u_name=name.encode("utf-8")  
	        UserObj = WebUser.objects.get(u_name =u_name)
	        return commons.res_success("用户名输入正确，请输入密码。")
	    except Exception, e:
	    	return commons.res_fail(1, "无此用户")


   #验证登录密码
@csrf_exempt
def Verify_userLogin(request):
    if request.method == 'POST':
       name       	= 	request.POST.get('form-username',None)
       password 	=	request.POST.get('form-password',None)
       
       try:
       	name1			=name or None
        password1	=password or None
        if name1 == None:
       		request.session['uname'] = ""
        	request.session['reason'] = "请输入用户名"
        	return HttpResponseRedirect("/yl//web/user_login")
        elif password1 ==None:
        	request.session['uname'] = ""
        	request.session['reason'] = "请输入密码"
        	return HttpResponseRedirect("/yl/web/user_login")
        else:
		    try:
		        u_name=name.encode("utf-8")  
		        UserObj = WebUser.objects.get(u_name =u_name)
		        u_password=password.encode("utf-8")
		        u_password=webmd5(u_password, u_name) 
		        if u_password == UserObj.u_password:
		        	roleObj			=Role.objects.get(r_id =UserObj.role_id)
		        	request.session['uname'] = u_name
		        	request.session['reason'] = ""
		        	request.session['user_role'] = roleObj.r_name
		        	if int(UserObj.u_state)==1:
		        		request.session['user_state'] = "已激活"
		        		return HttpResponseRedirect("/yl/web/admin")
	        		else:
	        			request.session['uname'] = ""
	        			request.session['user_state'] = "未激活"
	        			request.session['reason'] = "用户未激活不可登录，请联系管理员。"
	        			return HttpResponseRedirect("/yl/web/user_login")
		        else:
		        	request.session['uname'] = ""
		        	request.session['reason'] = "密码输入不正确"
		        	return HttpResponseRedirect("/yl/web/user_login")
		 
		    except Exception, e:
		    	request.session['uname'] = ""
		    	request.session['reason'] = "无此用户"
		    	return HttpResponseRedirect("/yl/web/user_login")
       
       except:
       	request.session['uname'] = ""
       	request.session['reason'] = "服务器繁忙请刷新页面"
       	return HttpResponseRedirect("/yl/web/user_login")

    
#用户登录界面
def user_login(request):
	res_data={
			"uname":request.session.get("uname",""),
			"reason":request.session.get("reason",""),	
			"user_state":request.session.get("user_state",""),
			"user_role":request.session.get("user_role",""),
			}
	request.session['uname'] = ""
	request.session['user_state'] = ""
	request.session['reason'] = ""
	request.session['user_role'] =""
	return commons.render_template(request,"admin/user_login.html",res_data)

#用户注销方法
def user_logout(request):
	if not request.session.get("uname", False):
			request.session['reason'] = "登录超时，请重新登录"
			return HttpResponseRedirect("user_login")
	else:
		request.session['reason'] = "用户已注销"
		del request.session["uname"]
		return HttpResponseRedirect("user_login")
	
   

def index(request):
    #如果已登录就直接跳到管理界面
#     if request.session.get("sess_admin", False):
#         return HttpResponseRedirect("admin")
#   
    action = request.GET.get("action")
    layout = action+".html"
    return commons.render_template(request,layout)

def admin(request):
	
    #需要登录才可以访问
    if not request.session.get("uname", False):
    	return HttpResponseRedirect("user_login")
    system = platform.uname()
    res_data = {
        "title": cfg.web_name,
        "django_version": django.get_version(),
        "python_version": platform.python_version(),
        "system": system[0] + " " + system[2],
        "username":request.session.get("uname"),
        "user_state":request.session.get("user_state"),
        "user_role":request.session.get("user_role"),
        }
    return commons.render_template(request, "admin/admin.html", res_data)
 
 #更改用户密码  
@csrf_exempt   
def ajax_Psd_change(request):
 	if not request.session.get("uname", False):
 		res_data={
							"text":"用户登录超时",
							"website":"user_login",
							}
		return commons.res_success("用户登录超时，请重新登录。",res_data) 
	if request.method	== 'POST':
		old_psd						=	request.POST.get('old_psd',None)
		new_psd					=	request.POST.get('new_psd',None)
		rnew_psd					=	request.POST.get('rnew_psd',None)
		name							=	request.session.get("uname", False)
		old_psd						=	old_psd or None
		new_psd					=	new_psd or None
		rnew_psd					=	rnew_psd or None
		psw_match				=re.compile('^[A-Za-z0-9]{6,16}$')
		if old_psd==None:
			return commons.res_fail(1, "原密码不能为空")
		elif psw_match.match(str(old_psd)) ==None:
	        		return commons.res_fail(1, "原密码格式不正确，请输入6-16位字母或数字组合")
		elif new_psd==None:
			return commons.res_fail(1, "新密码不能为空")
		elif psw_match.match(str(new_psd)) ==None:
	        		return commons.res_fail(1, "新密码格式不正确，请输入6-16位字母或数字组合")
		elif rnew_psd==None:
			return commons.res_fail(1, "确认密码不能为空")
		elif new_psd !=rnew_psd:
			return commons.res_fail(1, "密码输入不一致")
		else:
			try:
				name					=name.encode("utf-8")
				UserObj 			= WebUser.objects.get(u_name =name)
				old_psd				=webmd5(old_psd,name)
				if old_psd==UserObj.u_password:
					new_psd										=webmd5(new_psd,name)
					dataList										= UserObj
					dataList.u_password				=new_psd
					dataList.save()
					res_data={
							"text":"修改成功",
							"website":"user_login",
							}
					return commons.res_success("密码修改成功，请重新登录。",res_data) 
				else:
					return commons.res_fail(1, "原密码输入错误，请重新输入")
			except:
				return commons.res_fail(1, "修改失败，请确认是否登录")
			
#复现个人信息			
@csrf_exempt 
def ajax_person_data(request):
 	if not request.session.get("uname", False):
		res_data={
						"text":"用户登录超时",
						"website":"user_login",
						}
		return commons.res_fail(1,"用户登录超时，请重新登录。",res_data)
	else:
		name							=	request.session.get("uname", False)
		name							= name.encode("utf-8")
		try:
			dataObj	= WebUser.objects.get(u_name =name)
			#role_id		=dataObj.role_id.encode("utf-8")
			roleObj		=Role.objects.get(r_id =dataObj.role_id)
			rolename =roleObj.r_name
			if int(dataObj.u_state)==1:
				user_state = "已激活"
			else:
				user_state = "未激活"
			
			res_data	={
					'city_id':dataObj.city_id,
					'community_id':dataObj.community_id,
					'role_id':dataObj.role_id,
					'u_phone_number':dataObj.u_phone_number,
					'u_state':dataObj.u_state,
					'u_email':dataObj.u_email,
					'role_name':rolename,
					'user_state':user_state,
					
					}
			return commons.res_success("返回用户数据成功",res_data)
			
		except:
			res_data={
					'text':'请求失败请重新登录',
					'website':"user_login"}
			return commons.res_fail(1,"请求失败请重新登录。",res_data)
		
#保存个人信息		
@csrf_exempt
def ajax_person_update(request):	
 	if not request.session.get("uname", False):
		res_data={
						"text":"用户登录超时",
						"website":"user_login",
						}
		return commons.res_success("用户登录超时，请重新登录。",res_data)
	if request.method	== 'POST':
		email							=	request.POST.get('person_email',None)
		phone						=	request.POST.get('person_phone',None)
		city_id						=	request.POST.get('person_city',None)
		com_id						=	request.POST.get('person_com',None)
		name							=	request.session.get("uname", False)
		
        email							= email or None
        phone						=phone or None
        city_id						= city_id or None
        com_id						= com_id or None
        
        email_match			=re.compile('^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$')
        phone_match			=re.compile('^177\d{8}$|^1[358]\d{9}$|^147\d{8}$')
        
        if email ==None:
        	return commons.res_fail(1, "邮箱不能为空")        	
    	elif phone==None:
    		return commons.res_fail(1, "电话不能为空")
    	elif int(city_id)==-1:
    		return commons.res_fail(1, "未选择城市")
    	elif int(com_id)==-1:
    		return commons.res_fail(1, "未选择小区")
    	elif len(str(phone)) !=11:
    		return commons.res_fail(1, "请检查号码长度")
    	elif phone_match.match(str(phone)) ==None:
    		return commons.res_fail(1, "手机号格式不正确")
    	elif email_match.match(email) ==None:
    		return commons.res_fail(1, "邮箱格式不正确")
    	else:
    		try:
    			name												= name.encode("utf-8")
    			dataObj										=WebUser.objects .get(u_name=name)
    			dataList										= dataObj
        		dataList.u_email						=email
        		dataList.u_phone_number	=phone
        		dataList.city_id							=city_id
        		dataList.community_id			=com_id
        		dataList.save()
        		return commons.res_success("用户数据更改成功")
        	except:
        		return commons.res_fail(1, "修改失败，请检查用户登录状态")
        	
        
        
 #session期限       	

def ajax_Session_term(request):
	 if request.method == 'GET':
		try:
			if not request.session.get("uname", False):
				res_data={
							"text":"用户处于未登录状态",
							"website":"user_login",
							}
				return commons.res_success("用户处于未登录状态，请重新登录。",res_data) 
			else:
				del request.session["uname"]
				res_data={
							"text":"登录信息已过期",
							"website":"user_login",
							}
				return commons.res_success("登录信息已过期，请重新登录。",res_data)
		except:
			return commons.res_fail(1, "查询登录信息状态失败，请刷新界面")
	
	
        	
 #礼品，地址审核，用户兑换礼品，七天内用户意见数据       	
@csrf_exempt
def ajax_Data_Statistics(request):
	try:
		total_gift											=	Giftlist.objects.all().count()
		convertible_gift								=Giftlist.objects.filter(gl_status=1).count()
		inconvertible_gift							=Giftlist.objects.filter(gl_status=0).count()
		total_address									=	FamilyRecord.objects.all().count()
		unreviewed_address					=FamilyRecord.objects.filter(entity_type= 0).count()
		reviewed_address							=FamilyRecord.objects.filter(entity_type__in=[1,2]).count()
		total_exchange								=	UserExchange.objects.all().count()
		un_exchange									= UserExchange.objects.filter(ue_status= 1).count()
		exchange											= UserExchange.objects.filter(ue_status= 2).count()
		total_suggest									= OpinionRecord.objects.all().count()
		sevenDayAgo									= (datetime.datetime.now() - datetime.timedelta(days = 7))
		timeStamp										= time.mktime(sevenDayAgo.timetuple())
		timeStamp										=long(timeStamp*1000) 
		suggest_count								= OpinionRecord.objects.filter(opinion_time__gte = timeStamp).count()
		res_data={
				"total_gift":total_gift,
				"convertible_gift":convertible_gift,
				"inconvertible_gift":inconvertible_gift,
				"total_address":total_address,
				"unreviewed_address":unreviewed_address,
				"reviewed_address":reviewed_address,
				"total_exchange":total_exchange,
				"un_exchange":un_exchange,
				"exchange":exchange,
				"total_suggest":total_suggest,
				"suggest_count":suggest_count,
				}
		return commons.res_success("数据获取成功",res_data)
		
	except:
		return commons.res_fail(1, "获取统计数据失败，请刷新界面")
	
def get_code(request):
    ca = commons.Captcha(request)
    #ca.words = ['hello', 'world', 'helloworld']
    ca.type = 'number' #or word
    ca.img_width = 150
    ca.img_height = 30
    return ca.display()

def ajax_login(request):

    imgcode = request.GET.get("code")
    print(imgcode)
    if not imgcode or imgcode == "":
        return commons.res_fail(1, "验证码不能为空")

    ca = commons.Captcha(request)
    if ca.check(imgcode):
        
        name = request.GET.get("name")
        pwd = request.GET.get("pwd")
        
        try:
            admin = Admin.objects.get(name = name, pwd = pwd)
            admin_jsonstr = admin.toJSON()
            admin = json.loads(admin_jsonstr)
            
            #删除密码字段
            del(admin["pwd"])    
            request.session["sess_admin"] = admin
            
            return commons.res_success("登录成功")
        except:
            return commons.res_fail(1, "用户或密码不正确")
            
    else:
        return commons.res_fail(1, "验证码不正确")

def ajax_logout(request):    
    #需要登录才可以访问
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录才可以访问")
    
    del request.session["sess_admin"]
    return commons.res_success("退出登录")

def ajax_menu_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")

    return commons.res_success("请求成功", cfg.admin_menu_list)
    
def ajax_admin_list(request):
    #需要登录才可以访问
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))

    res_data = Admin.getList(page, page_size)
    
    return commons.res_success("请求成功", res_data)

def ajax_admin_add(request):
    #需要登录才可以访问
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录才可以访问")
    
    name = request.REQUEST.get("name")
    pwd = request.REQUEST.get("pwd")
    pwd2 = request.REQUEST.get("pwd2")
    
    if name == "":
        return commons.res_fail(1, "用户名不能为空")
    if pwd == "":
        return commons.res_fail(1, "密码不能为空")
    if pwd != pwd2:
        return commons.res_fail(1, "确认密码不正确")
    
    total = Admin.objects.filter(name = name).count()
    if total > 0:
        return commons.res_fail(1, "该管理员已存在")
    
    admin = Admin(
        name = name,
        pwd = pwd,
        add_time = int(time.time())
    )
    admin.save()
    
    return commons.res_success("添加成功", json.loads(admin.toJSON()))

def ajax_admin_del(request):
    #需要登录才可以访问
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录才可以访问")
    
    id = request.REQUEST.get("id")
        
    try:
        admin = Admin.objects.get(id = id)
        admin.delete()
        return commons.res_success("删除成功")
    except:
        return commons.res_fail(1, "该数据不存在")

def ajax_admin_updatepwd(request):
    #需要登录才可以访问
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录才可以访问")
    
    curr_admin = request.session.get("sess_admin")
    old_pwd = request.REQUEST.get("old_pwd")
    pwd = request.REQUEST.get("pwd")
    pwd2 = request.REQUEST.get("pwd2")
    
    if old_pwd == "":
        return commons.res_fail(1, "旧密码不能为空")
    if pwd == "":
        return commons.res_fail(1, "新密码不能为空")
    if pwd != pwd2:
        return commons.res_fail(1, "确认密码不正确")
    
    try:
        admin = Admin.objects.get(name = curr_admin["name"], pwd = old_pwd)
        admin.pwd = pwd
        admin.save()
    
        return commons.res_success("修改密码成功")
    except:
        return commons.res_fail(1, "旧密码不正确")


#
def ajax_city_data(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #type = int(request.REQUEST.get("type"))
    city_lists = City.objects.filter()
    city_list_json = []
    for city in city_lists:        
        item={}
        item['text']=city.city_id
        item['label']=city.city_name    
        city_list_json.append(item)
        
    return HttpResponse(json.dumps(city_list_json), content_type="application/json") 

def ajax_community_data(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    city_id = int(request.GET.get("city_id"))
        
    community_lists = Community.objects.filter(city_id=city_id)
    community_list_json = []
    for community in community_lists:        
        item={}
        item['text']=community.community_id
        item['label']=community.community_name    
        community_list_json.append(item)
        
    return HttpResponse(json.dumps(community_list_json), content_type="application/json") 

def ajax_community_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    community_lists = Community.objects.all()
    community_list_json = []
    for community in community_lists:        
        item={}
        item['text']=community.community_id
        item['label']=community.community_name    
        community_list_json.append(item)
        
    return HttpResponse(json.dumps(community_list_json), content_type="application/json")

def ajax_user_data(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    community_id = int(request.GET.get("community_id"))
        
    user_lists = User.objects.filter(user_community_id=community_id)
    user_list_json = []
    for user in user_lists:        
        item={}
        item['text']=user.user_id
        item['label']=user.user_phone_number    
        user_list_json.append(item)
        
    return HttpResponse(json.dumps(user_list_json), content_type="application/json")

def generatePassword(user_password,user_phone):
    try:
        import hashlib
        hash = hashlib.md5()
    except ImportError:
        # for Python << 2.5
        import md5
        hash = md5.new()
    if isinstance(user_password, unicode):  
         user_password = user_password.encode("utf-8")  
    elif not isinstance(user_password, str):  
         user_password = str(user_password) 
    hash.update(user_password)       #md5(user_password)
    one = hash.hexdigest() 
    if isinstance(user_phone, unicode):  
         user_phone = user_phone.encode("utf-8")  
    elif not isinstance(user_phone, str):  
         user_phone = str(user_phone) 
    try:
        hash2 = hashlib.md5()
    except ImportError:
        hash2 = md5.new() 
    hash2.update(one)
    hash2.update(user_phone)    #md5(md5(user_password)+user_phone) 
    return hash2.hexdigest() 

def ajax_audit_submit(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    user_phone = request.GET.get("user_phone")
    user_nick = request.GET.get("user_nick")
    user_password = request.GET.get("user_password")
    repassword = request.GET.get("repassword")
    city_id = int(request.GET.get("p_city_id"))
    community_id = int(request.GET.get("p_community_id"))
    user_family_address = request.GET.get("user_family_address")
    ltime = long(time.time()*1000)
    if user_password  != repassword:
        return commons.res_fail(1, "两次密码输入不一致!")
    password = generatePassword(user_password,user_phone)
    try:
        userObj = User.objects.get(user_phone_number = user_phone)
    except:
    	userObj = createUser(user_phone,user_nick,password,str(city_id),str(community_id),ltime,user_family_address)

    if userObj:
        adminObj,created = Admin.objects.get_or_create(admin_type=4,city_id=city_id,community_id=community_id,user_id=userObj.user_id)
        adminObj.app_time = ltime
        adminObj.save()
     
    try:
        cityObj = City.objects.get(city_id=city_id)
    except City.DoesNotExist:
        return commons.res_fail(1, City.DoesNotExist)
    try:
        communityObj = Community.objects.get(community_id=community_id)
    except Community.DoesNotExist:
        return commons.res_fail(1, Community.DoesNotExist)

    familyId = str(1000) + str(cityObj.city_code) + str(community_id)
    addrDetailsObj,created = AddressDetails.objects.get_or_create(ad_id=familyId) 
    if created:#new
            addrMask = str(long(time.time()*1000))[-8:]
            addrDetailsObj.address_mark = addrMask
            addrDetailsObj.city_name = cityObj.city_name
            addrDetailsObj.community_name = communityObj.community_name
            addrDetailsObj.family_member_count = 0
            addrDetailsObj.family_address = cityObj.city_name+communityObj.community_name
            addrDetailsObj.city_id = city_id
            addrDetailsObj.community_id = community_id
            addrDetailsObj.save()
    else:
        pass
     
    fRecordObj,fcreated = FamilyRecord.objects.get_or_create(user_id=userObj.user_id,family=addrDetailsObj) 
    fRecordObj.ne_status = 0
    fRecordObj.entity_type = 1
    fRecordObj.family_city = cityObj.city_name
    fRecordObj.family_city_id = cityObj.city_id
    fRecordObj.family_community = communityObj.community_name
    fRecordObj.family_community_id = communityObj.community_id
    fRecordObj.family_address = cityObj.city_name + communityObj.community_name
    fRecordObj.primary_flag = 1
    fRecordObj.is_family_member = 0
    fRecordObj.save()
    #注册环信
    registUser(userObj.user_id,userObj.user_id)   
    user_json = []
    user_json.append(getUserJson(userObj.user_id,cityObj.city_name,userObj.user_type,fRecordObj.family_address,community_id,communityObj.community_name))
    userObj.user_json =  json.dumps(user_json)  
    userObj.user_type = 4
    userObj.addr_handle_cache = 0
    userObj.user_family_id = familyId
    userObj.save() 
    item={}
    item['flag']="ok" 
    return HttpResponse(json.dumps(item), content_type="application/json")

    
def createUser(user_phone,user_nick,user_password,city_id,community_id,ltime,user_family_address):
    user = User()
    try:
        user.user_phone_number = user_phone
        user.user_gender = 3
        user.user_nick = user_nick
        user.user_portrait = settings.RES_URL + 'res/default/avatars/default-property.png'
        user.user_password = user_password
        user.user_public_status = '4'
        user.user_type = 4
        user.user_exp =  5
        user.user_credit = 5
        user.user_family_id =  city_id+community_id
        user.user_community_id = community_id
        user.user_family_address = user_family_address
        user.user_time = ltime
        user.save()
    except Exception,e:
        return commons.res_fail(1, e)
    
    return user

def getUserJson(user_id,city_name,user_type,family_address,community_id,community_name):
    dicts = {}
    dicts.setdefault("userId",user_id)
    dicts.setdefault("cityName",city_name)
    dicts.setdefault("userType",user_type)
    dicts.setdefault("address",family_address)
    dicts.setdefault("communityId",community_id);
    dicts.setdefault("communityName",community_name);
    return dicts
# def ajax_audit_submit(request):
#     #需要登录才可以访问
#     #if not request.session.get("sess_admin", False):
#     #    return commons.res_fail(1, "需要登录才可以访问")
#     city_id = int(request.GET.get("city_id"))
#     community_id = int(request.GET.get("community_id"))
#     user_id = int(request.GET.get("user_id"))
#         
#     #获取的表单数据与数据库进行比较
#     
#     try:
#         userObj = User.objects.get(user_id =user_id)
#     except:
#         userObj = None
#         pass
#     if(userObj):
#         adminTuple = Admin.objects.get_or_create(admin_type=4,city_id=city_id,community_id=community_id,user_id=user_id)
#     adminObj = adminTuple[0]
#     ListAdmin = []
#     config = readIni()
#     if adminObj:
#             #baidu_channel_id = userObj.user_push_channel_id.encode('utf-8')
#             pushTitle = config.get("users", "title")
#             communityObj = adminObj.community
#             cityName = communityObj.city.city_name
#             communityName = communityObj.community_name
#             address = cityName+communityName
#             familyAddr = address.encode('utf-8')
#             pushContent = config.get("users", "content4")+ familyAddr + config.get("users", "content5")
#             ListAdmin.append(genAdminDetailDict(user_id,cityName,community_id,communityName,address,4))
#             userObj.user_json = json.dumps(ListAdmin)
#             adminObj.admin_info = json.dumps(ListAdmin)
#             userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
#             currentPushTime = long(time.time()*1000)
#             customContent = genAdminContentDict(user_id,userAvatar,pushTitle,pushContent,4,currentPushTime,1,ListAdmin,community_id)
#             recordId = createPushRecord(1,4,pushTitle,pushContent,currentPushTime,user_id,json.dumps(customContent),community_id,user_id)
#             customContent = genAdminContentDict(user_id,userAvatar,pushTitle,pushContent,4,currentPushTime,1,ListAdmin,community_id,recordId)
#             
#             apiKey = config.get("SDK", "apiKey")
#             secretKey = config.get("SDK", "secretKey")
#             alias = config.get("SDK", "youlin")
#             _jpush = jpush.JPush(apiKey,secretKey) 
#             
#             AsyncAuditSubmit.delay(apiKey, secretKey, alias, user_id, customContent, pushContent, pushTitle)
#             
#             adminObj.app_time = currentPushTime
#             adminObj.save()
#             userObj.user_type = 4
#             userObj.user_time = currentPushTime
#             userObj.save()
#             #比较成功，跳转index
#     item={}
#     item['flag']="ok"    
#     return HttpResponse(json.dumps(item), content_type="application/json")

# def ajax_audit_list(request):
#     #需要登录才可以访问
#     #if not request.session.get("sess_admin", False):
#     #    return commons.res_fail(1, "需要登录才可以访问")
#     
#     #分页索引和每页显示数
#     page = 1
#     if request.REQUEST.get("page"):
#         page = int(request.REQUEST.get("page"))
#     page_size = cfg.page_size
#     if request.REQUEST.get("page_size"):
#         page_size = int(request.REQUEST.get("page_size"))
#     
#     type = int(request.REQUEST.get("type"))
#     
#     res_data = getList(page, page_size, type)
#     return commons.res_success("请求成功", res_data)
#         
# 
# #获取分页数据
# def getList(page, page_size, type):
#     total = Admin.objects.filter(admin_type= type).count()
#     page_count = commons.page_count(total, page_size)
# 
#     offset = (page - 1) * page_size
#     limit = offset + page_size
# 
#     admin_lists = Admin.objects.filter(admin_type= type).order_by("-admin_id")[offset:limit]
#     data = []
#     for i in admin_lists:
#         item = json.loads(i.toJSON())
#         item["app_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["app_time"]/1000))
#         data.append(item)
# 
#     data = {
#         "page_size": page_size,
#         "page_count": page_count,
#         "total": total,
#         "page": page,
#         "list": data,
#     }
#     return data    

def ajax_address_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
        
    type = int(request.REQUEST.get("type"))
    res_data = getAddressList(page, page_size,type)
    return commons.res_success("请求成功", res_data)

#获取分页数据
def getAddressList(page, page_size,type):
    if(type == 1):
        total = FamilyRecord.objects.filter(entity_type= 0).count()
        page_count = commons.page_count(total, page_size)
    
        offset = (page - 1) * page_size
        limit = offset + page_size
    
        address_lists = FamilyRecord.objects.filter(entity_type= 0).order_by("-fr_id")[offset:limit]
        data = []
        for i in address_lists:
            item = json.loads(i.toJSON())
            if i.family is None:
                item['address_mark'] = "非法"
            else:
                item['address_mark'] = i.family.address_mark
            data.append(item)
        data = {
            "page_size": page_size,
            "page_count": page_count,
            "total": total,
            "page": page,
            "list": data,
        }
    else:
        total = FamilyRecord.objects.filter(entity_type__in=[1,2]).count()
        page_count = commons.page_count(total, page_size)
    
        offset = (page - 1) * page_size
        limit = offset + page_size
        
        f_address_lists = FamilyRecord.objects.filter(entity_type__in=[1,2]).order_by("-fr_id")[offset:limit]
        f_data = []
        for j in f_address_lists:
            item = json.loads(j.toJSON())
            if j.family is None:
                item['address_mark'] = "非法"
            else:
                item['address_mark'] = j.family.address_mark
            f_data.append(item)
    
        data = {
            "page_size": page_size,
            "page_count": page_count,
            "total": total,
            "page": page,
            "f_list": f_data,
        }
    return data    

def ajax_fr_data(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    audit_id = request.GET.get("audit_id")
    fr_id = audit_id.split('_')[2]
    try:
        familyRecord = FamilyRecord.objects.get(fr_id= fr_id)
    except:
        familyRecord = None
        pass
    if(familyRecord):
        block_lists = Block.objects.filter(community__community_id=familyRecord.family_community_id)
        data = []
        building = []
        if block_lists:
            block_ids = []
            for i in block_lists:
                item={}
                item['text']=i.block_id
                item['label']=i.block_name    
                data.append(item)
                block_ids.append(i.block_id)
            building_lists = BuildNum.objects.filter(block_id__in=block_ids)
            if building_lists is not None:
                for i in building_lists:
                    item={}
                    item['text']=i.buildnum_id
                    item['label']=i.building_name    
                    building.append(item)    
                
        else:
            building_lists = BuildNum.objects.filter(community_id=familyRecord.family_community_id)
            if building_lists is not None:
                for i in building_lists:
                    item={}
                    item['text']=i.buildnum_id
                    item['label']=i.building_name    
                    building.append(item)
        try:
            cityObj = City.objects.get(city_id=familyRecord.family_city_id)    
        except:
            cityObj = None
            pass    
        json_data = {
            "family_community": familyRecord.family_community,
            "family_city": familyRecord.family_city,
            "family_address": familyRecord.family_address,
            "family_city_id": familyRecord.family_city_id,
            "family_community_id": familyRecord.family_community_id,
            "fr_id": fr_id,
            "city_code": cityObj.city_code,
            "block_list": data,
            "building_list": building
        }    
    return commons.res_success("请求成功", json_data)

def ajax_apt_data(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    buildnum_id = int(request.GET.get("buildnum_id"))
        
    aptNum_lists = AptNum.objects.filter(buildnum_id=buildnum_id)
    aptNum_list_json = []
    for aptNum in aptNum_lists:        
        item={}
        item['text']=aptNum.apt_id
        item['label']=aptNum.apt_name    
        aptNum_list_json.append(item)
        
    return HttpResponse(json.dumps(aptNum_list_json), content_type="application/json")
@csrf_exempt
def ajax_address_audit_submit(request):
    ListFamilyInfo = []
    oldEnStatus = None
    userCurrentCommunityId = None
    config = readIni()
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    community_id = int(request.POST.get("community_id"))
    block_id = int(request.POST.get("block_id"))
    buildnum_id = int(request.POST.get("buildnum_id"))
    apt_id = int(request.POST.get("apt_id"))
    
    #city_id = request.GET.get("city_id")
    #city_code = request.GET.get("city_code")
    fr_id = int(request.POST.get("fr_id"))
    status = int(request.POST.get("status"))
    reason = request.POST.get("reason").encode("utf-8")
    
    try:
        communityObj = Community.objects.get(community_id=community_id)
    except:
        communityObj = None
        pass

    cityObj = communityObj.city
    city_id = cityObj.city_id
    try:    
        fRecordObj = FamilyRecord.objects.get(fr_id=fr_id)
    except:
        fRecordObj = None
        pass
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    frAddrCount = 0
    userObj = fRecordObj.user
    userCurrentCommunityId = userObj.user_community_id
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    alias = config.get("SDK", "youlin")
    pushTitle = config.get("users", "title")
    if not(status==1): #不通过
    	if int(block_id) == 0:
    		family_id = str(1000) + str(cityObj.city_code) + str(community_id) + str(buildnum_id) + str(apt_id)
    	else:
    		try:
    		    family_id = str(1000) + str(cityObj.city_code) + str(community_id) + str(block_id) + str(buildnum_id) + str(apt_id)
    		except:
    			family_id = 0
    else:
	    if (buildnum_id == 0) or (apt_id == 0):
	        msgInfo = "请选择楼栋,门牌"
	        return commons.res_fail(1, msgInfo)
	    if int(block_id) == 0:
	        family_id = str(1000) + str(cityObj.city_code) + str(community_id) + str(buildnum_id) + str(apt_id)
	    else:
	        family_id = str(1000) + str(cityObj.city_code) + str(community_id) + str(block_id) + str(buildnum_id) + str(apt_id)
    frAddrCount = FamilyRecord.objects.filter(family_id=family_id,entity_type=1).count()
    family_city= fRecordObj.family_city
    family_building_num = fRecordObj.family_building_num
    family_community = fRecordObj.family_community
    family_apt_num = fRecordObj.family_apt_num
    family_block =fRecordObj.family_block
    oldEnStatus = fRecordObj.ne_status
    try:
        blockObj = Block.objects.get(block_id=block_id)
    except:
        blockObj = None
        pass
    try:
        buildObj = BuildNum.objects.get(buildnum_id=buildnum_id)
    except:
        buildObj = None
        pass
    
    if status == 1: #通过
        if int(frAddrCount) > 5:#超过6个不可再审核
            msgInfo = "该地址拥挤，请重新选择"
            return commons.res_fail(1, msgInfo)
        
        familyTuple = AddressDetails.objects.get_or_create(ad_id=family_id)
        addrDetailsObj = familyTuple[0]
        if familyTuple[1]:
            addrMask = str(long(time.time()*1000))[-8:]
            addrDetailsObj.address_mark = addrMask
            addrDetailsObj.city_name=cityObj.city_name
            addrDetailsObj.building_name=buildObj.building_name
            aptObj = AptNum.objects.get(apt_id=apt_id)
            addrDetailsObj.apt_name=aptObj.apt_name
            if blockObj is not None:
                addrDetailsObj.block_name = blockObj.block_name
                addrDetailsObj.community_name=communityObj.community_name+"-"+blockObj.block_name
                addrDetailsObj.family_address = cityObj.city_name+communityObj.community_name+"-"+blockObj.block_name+"-"+buildObj.building_name+"-"+aptObj.apt_name
            else:
                addrDetailsObj.community_name=communityObj.community_name
                addrDetailsObj.family_address = cityObj.city_name+communityObj.community_name+buildObj.building_name+"-"+aptObj.apt_name
            addrDetailsObj.family_name = buildObj.building_name+"-"+aptObj.apt_name
            addrDetailsObj.family_member_count = 0
            addrDetailsObj.city_id = city_id
            addrDetailsObj.community_id = community_id
            addrDetailsObj.block_id = block_id
            addrDetailsObj.building_id = buildnum_id
            addrDetailsObj.apt_id = apt_id
            addrDetailsObj.save()
        fRecordObj.ne_status = 0
        fRecordObj.family_id = family_id
        fRecordObj.family_city_id = city_id
        fRecordObj.family_community_id = community_id
        if int(block_id) == 0:
            fRecordObj.family_block_id = 0
        else:
            fRecordObj.family_block_id = block_id
        fRecordObj.family_building_num_id = buildnum_id
        fRecordObj.family_apt_num_id = apt_id
        fRecordObj.entity_type = 1 # 通过 ,0:待审核
        
        userObj.user_family_id = family_id
        userObj.user_community_id = community_id
        if int(block_id) == 0:
            userObj.user_family_address = family_city+family_community+"-"+family_building_num+"-"+family_apt_num
        else:
            userObj.user_family_address = family_city+family_community+"-"+family_block+"-"+family_building_num+"-"+family_apt_num
        userObj.save()
        ListAdmin = []
        # familyId,cityId,blockId,communityId,entityType,neStatus,primaryFlag
        ListFamilyInfo.append(familyInfoDict(
                    family_id,city_id,block_id,community_id,1,oldEnStatus
                ))
        familyAddr = fRecordObj.family_address.encode('utf-8')
        pushContent = config.get("users", "content6")+ familyAddr + config.get("users", "content7")
        setWelcomeTopic(family_city,city_id,family_community,community_id,userObj.user_family_address,userObj.user_family_id,userObj.user_nick,userObj.getTargetUid())  
       
        user_id = userObj.user_id
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
        currentPushTime = long(time.time()*1000)
        customContent = genContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,1,currentPushTime,2,ListFamilyInfo,userCurrentCommunityId)
        recordId = createPushRecord(2,1,pushTitle,pushContent,currentPushTime,user_id,(json.dumps(customContent)),userObj.user_community_id,user_id)
        customContent = genContentDict(userObj.getTargetUid(),userAvatar,pushTitle,pushContent,1,currentPushTime,2,ListFamilyInfo,userCurrentCommunityId,recordId)
        ListFamilyInfo = []
        AsyncAddressAuditSubmit.delay(apiKey,secretKey,alias,user_id,customContent,pushContent,pushTitle)

    else:
        if reason.strip()=='':
            message = "请填写审核不通过原因！"
            return commons.res_fail(1, message)   
        
        fRecordObj.entity_type = 2 #未通过
        ListAdmin = []
        ListFamilyInfo.append(familyInfoDict(
                    family_id,city_id,block_id,community_id,2,oldEnStatus
                ))
        familyAddr = fRecordObj.family_address.encode('utf-8')
        pushContent = config.get("users", "content6")+ familyAddr + config.get("users", "content10") + config.get("users", "content11")+reason
        # add push with info
        currentPushTime = long(time.time()*1000)
        currentUserId = userObj.getTargetUid()
        userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
        customContent = genContentDict(currentUserId,userAvatar,pushTitle,pushContent,3,currentPushTime,2,ListFamilyInfo,userCurrentCommunityId)
        recordId = createPushRecord(2,3,pushTitle,pushContent,currentPushTime,currentUserId,(json.dumps(customContent)),userObj.user_community_id,currentUserId)
        customContent = genContentDict(currentUserId,userAvatar,pushTitle,pushContent,3,currentPushTime,2,ListFamilyInfo,userCurrentCommunityId,recordId)
    
        AsyncCFailureCauseWithAudit.delay(apiKey, secretKey, alias, currentUserId, customContent, pushContent, pushTitle)
        
    fRecordObj.save()
    return commons.res_success("地址审核完成!")
        


def genCustomContentDict(userId,userAvatar,title,content,contentType,pushTime,pushType,recordId=None):
    dicts = {}
    dicts.setdefault('userId',userId)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('title',title)
    dicts.setdefault('content',content)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('pushType',pushType)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

def genContentDict(userId,userAvatar,title,content,contentType,pushTime,pushType,familyDict,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('userId',userId)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('title',title)
    dicts.setdefault('content',content)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('pushType',pushType)
    dicts.setdefault('familyDict',familyDict)
    dicts.setdefault('communityId',communityId)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

def familyInfoDict(familyId,cityId,blockId,communityId,entityType,neStatus):
    dicts = {}
    dicts.setdefault('familyId',familyId)
    dicts.setdefault('cityId',cityId)
    dicts.setdefault('blockId',blockId)
    dicts.setdefault('communityId',communityId)
    dicts.setdefault('entityType',entityType)
    dicts.setdefault('neStatus',neStatus)#old
    return dicts
    
def ajax_common_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    
    type = int(request.REQUEST.get("type"))
    
    res_data = getCommonList(page, page_size, type)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getCommonList(page, page_size, type):
    total = Admin.objects.filter(admin_type= type).count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    admin_lists = Admin.objects.filter(admin_type= type).order_by("-admin_id")[offset:limit]
    data = []
    for i in admin_lists:
        item = json.loads(i.toJSON())
        if item["app_time"] is not None:
            item["app_time"] = time.strftime("%Y-%m-%d", time.localtime(item["app_time"]/1000))
        else:
            item["app_time"] = "---"
        data.append(item)

    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data    

def ajax_admin_data(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    community_id = int(request.GET.get("community_id"))
        
    admin_lists = Admin.objects.filter(community_id=community_id,admin_type = 1)
    admin_list_json = []
    for admin in admin_lists:        
        item={}
        item['text']=admin.user.user_id
        item['label']=admin.user.user_phone_number    
        admin_list_json.append(item)
        
    return HttpResponse(json.dumps(admin_list_json), content_type="application/json")

def ajax_common_submit(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    city_id = int(request.GET.get("city_id"))
    community_id = int(request.GET.get("community_id"))
    user_id = int(request.GET.get("user_id"))
        
    #获取的表单数据与数据库进行比较
    
    try:
        userObj = User.objects.get(user_id =user_id)
    except:
        userObj = None
        pass
    if(userObj):
        adminTuple = Admin.objects.get_or_create(admin_type=2,city_id=city_id,community_id=community_id,user_id=user_id)
    adminObj = adminTuple[0]
    ListAdmin = []
    config = readIni()
    if adminObj:
            pushTitle = config.get("users", "title")
            communityObj = adminObj.community
            cityName = communityObj.city.city_name
            communityName = communityObj.community_name
            address = cityName+communityName
            familyAddr = address.encode('utf-8')
            pushContent = config.get("users", "content1")+ familyAddr + config.get("users", "content3")
            ListAdmin.append(genAdminDetailDict(user_id,cityName,community_id,communityName,address,2))
            userObj.user_json = json.dumps(ListAdmin)
            adminObj.admin_info = json.dumps(ListAdmin)
            userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
            currentPushTime = long(time.time()*1000)
            customContent = genAdminContentDict(user_id,userAvatar,pushTitle,pushContent,2,currentPushTime,1,ListAdmin,community_id)
            recordId = createPushRecord(1,2,pushTitle,pushContent,currentPushTime,user_id,json.dumps(customContent),community_id,user_id)
            customContent = genAdminContentDict(user_id,userAvatar,pushTitle,pushContent,2,currentPushTime,1,ListAdmin,community_id,recordId)
            
            apiKey = config.get("SDK", "apiKey")
            secretKey = config.get("SDK", "secretKey")
            alias = config.get("SDK", "youlin")
            
            AsyncCommonSubmit.delay(apiKey,secretKey,alias,user_id,customContent,pushContent,pushTitle)
            
            adminObj.app_time = currentPushTime
            adminObj.save()
            userObj.user_type = 2
            userObj.user_time = currentPushTime
            userObj.save()

    return commons.res_success("管理员审核成功")

def setWelcomeTopic(family_city,family_city_id,family_community,family_community_id,user_family_address,user_family_id,user_nick,user_id):
    data = {}
    config = readIni()
    title                 = config.get('topic', "topic_title1")+ user_nick.encode('utf-8') +config.get('topic', "topic_title2")
    topic_content         = config.get('topic', "topic_content")
    topic_content_0       = config.get('topic', "topic_content_0")
    topic_content_1       = config.get('topic', "topic_content_1")
    topic_content_2       = config.get('topic', "topic_content_2")
    topic_content         = topic_content + '<br/>' + topic_content_0 + '<br/>' + topic_content_1 + '<br/>' + topic_content_2
    topic_time            = long(time.time()*1000)
    forum_name            = config.get('topic', "forum_name")
    sender_id             = config.get('topic', "sender_id")
    sender_name           = config.get('topic', "sender_name")
    userAvatar = settings.RES_URL+'res/default/avatars/default-avatar.png'
    sender_portrait       = userAvatar
    sender_family_id      = config.get('topic', "sender_family_id")
    sender_family_address = user_family_address
    display_name          = config.get('topic', "sender_name")+"@"+family_community.encode('utf-8')
    sender_city_id        = family_city_id
    sender_community_id   = family_community_id
    topicObj  = Topic.objects.create(topic_title=title,topic_content=topic_content,topic_category_type=2,topic_time=topic_time,\
                                       forum_id=1, forum_name=forum_name, sender_id=sender_id,sender_name=sender_name, sender_portrait=sender_portrait,\
                                       sender_family_id=sender_family_id,sender_family_address=sender_family_address, display_name=display_name,\
                                       object_data_id=0,circle_type=1,send_status=0,sender_city_id=sender_city_id,sender_community_id=sender_community_id,\
                                       cache_key=user_id)
    topicId = topicObj.getTopicId() 
        
    AsyncSetWelcomeTopic.delay(topicId,sender_id,sender_community_id)

    
def getCacheKey():
    cacheKey = int(time.time()) + int(random.randint(100,999))
    return cacheKey  
   
@csrf_exempt
def ajax_image_upload(request):
    if request.method == 'POST':
        callback = request.GET.get('CKEditorFuncNum')
        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
        try:
            f = request.FILES["upload"]
            postfix = (f.name).split(".")[1].lower()
            postfixList = ['jpg','jpeg','gif','bmp','png']
            if not postfix in postfixList:
                message = "请上传jpg,jpeg,gif,bmp,png类型的图片"
                return commons.res_fail(1, message)
            
            path = BASE_ROOT+"/media/youlin/newspic/" 
            if not os.path.exists(path):
                os.mkdir(path, 0777)
            file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + f.name
            file_path = path+file_name
            des_origin_f = open(file_path, "wb+")  
            for chunk in f.chunks():
                des_origin_f.write(chunk)
            des_origin_f.close()
            im = Image.open(file_path)
            mode = im.mode
            if mode not in ('L', 'RGB'):
                im = im.convert('RGB')
            width, height = im.size
            if width > 300 :
                nwidth = 300
                nheight = int(height * 300/width)
                thumb = im.resize((nwidth,nheight), Image.ANTIALIAS)
                file_new = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + f.name
                thumb.save(path+file_new)
                file_jump = "/media/youlin/newspic/" + file_new
            else:
                file_jump = "/media/youlin/newspic/" + file_name
        except Exception, e:
            print e
        
        res = "<script>window.parent.CKEDITOR.tools.callFunction("+callback+",'"+file_jump+"', '');</script>"
        return HttpResponse(res)
    else:
        raise Http404()
    
def makeThumbnail(userDir, bigImg, smallImg, percent, suffix = None):
    filePath = userDir + bigImg
    im = Image.open(filePath)
    mode = im.mode
    if mode not in ('L', 'RGB'):
        im = im.convert('RGB')
    width, height = im.size
    n = int(percent)
    nwidth = int(width * n/100)
    nheight = int(height * n/100)
    thumb = im.resize((nwidth,nheight), Image.ANTIALIAS)
    if suffix:
        thumb.save(userDir+smallImg+suffix)
    else:
        thumb.save(userDir+smallImg) 
               
@csrf_exempt
def ajax_new_submit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        source = request.POST.get('source')
        introduce = request.POST.get('introduce')
        content = request.POST.get('content')
        pri_flag = request.POST.get('pri_flag')
        city_id = request.POST.get('city_id')
        community_id = request.POST.get('community_id')
        new_add_time = long(time.time()*1000)
        new_id = request.POST.get('newsId',None)
        if int(new_id) == 0:
            
            #新闻小图
            try:
                BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                small_pic = request.FILES.get("small_pic", None)
                #small_pic = request.POST.get["small_pic"]
                postfix = (small_pic.name).split(".")[1].lower()
                postfixList = ['jpg','jpeg','gif','bmp','png']
                if not postfix in postfixList:
                    message = "请上传jpg,jpeg,gif,bmp,png类型的图片"
                    return commons.res_fail(1, message)
                
                path = BASE_ROOT+"/media/youlin/newspic/" 
                if not os.path.exists(path):
                    os.mkdir(path, 0777)
                file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + small_pic.name
                file_path = path+file_name
                des_origin_f = open(file_path, "wb+")  
                for chunk in small_pic.chunks():
                    des_origin_f.write(chunk)
                des_origin_f.close()
                file_jump = "/media/youlin/newspic/" + file_name
                newsObj = News.objects.create(new_title = title,new_source = source,new_introduce=introduce,\
                                           pri_flag=pri_flag,new_content=content,new_small_pic=file_jump,\
                                           city_id=city_id,community_id=community_id,new_add_time=new_add_time)
                response_data = {}
                response_data['flag'] = 'ok'
                return HttpResponse(json.dumps(response_data), content_type="application/json")   
            except Exception, e:
                print e
        else:
            #新闻小图
            file_name = ''
            res_data = ""
            try:
                newObj = News.objects.get(new_id=new_id)
                newObj.new_title = title
                newObj.new_source = source
                newObj.new_introduce = introduce
                newObj.new_content = content
                newObj.pri_flag = pri_flag
                newObj.city_id = city_id
                newObj.community_id = community_id
                
                small_pic = request.FILES.get('small_pic')
                if small_pic :
                    small_pic = request.FILES['small_pic']
                    BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                    postfix = (small_pic.name).split(".")[1].lower()
                    postfixList = ['jpg','jpeg','gif','bmp','png']
                    if not postfix in postfixList:
                        message = "请上传jpg,jpeg,gif,bmp,png类型的图片"
                        return commons.res_fail(1, message)
                    
                    path = BASE_ROOT+"/media/youlin/newspic/" 
                    if not os.path.exists(path):
                        os.mkdir(path, 0777)
                    file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + small_pic.name
                    file_path = path+file_name
                    des_origin_f = open(file_path, "wb+")  
                    for chunk in small_pic.chunks():
                        des_origin_f.write(chunk)
                    des_origin_f.close()
                    file_jump = "/media/youlin/newspic/" + file_name
                    image_del(BASE_ROOT+newObj.new_small_pic)
                    newObj.new_small_pic = file_jump
                newObj.save()
            except Exception, e:
                return commons.res_success("修改失败", res_data)
            res_data= "ok"
            return commons.res_success("修改成功", res_data)
    else:
        raise Http404()
    
def ajax_news_list(request):
        #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    
    res_data = getNewsList(page, page_size)
    
    
    return HttpResponse(json.dumps(res_data), content_type="application/json")
    #return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getNewsList(page, page_size):
    news = News.objects.all()
    total = news.count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    news_lists = News.objects.all().order_by("-new_id")[offset:limit]
    data = []
    for i in news_lists:
        item = {}
        item['new_title'] = i.new_title
        item['new_source'] = i.new_source
        item['new_introduce'] = i.new_introduce
        
        item['new_small_pic'] = i.new_small_pic
        item['city_name'] = i.city.city_name
        item['community_id'] = i.community_id
        item['community_name'] = i.community.community_name
        #item['new_add_time'] = i.new_add_time
        add_time = long(i.new_add_time)
        item['new_add_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(add_time/1000))
        item['new_id'] = i.new_id
        item['new_content'] = i.new_content
        item['push_flag'] = i.push_flag
        if i.pri_flag == 0:
            item['pri_flag'] = "否"
        else:
            item['pri_flag'] = "是"
        data.append(item)

    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data    

def ajax_getNewsById(request):
    
    if request.method == "GET":
        id = request.GET.get("id")
    try:
        newObj = News.objects.get(new_id =id)
    except Exception, e:
        print e
    dict = getNewDict(newObj)
    return render_to_response('site/new.html',{'newDict':dict })
    
def getNewDict(newObj):
    dicts = {}
    dicts.setdefault('new_title',newObj.new_title)
    dicts.setdefault('new_source',newObj.new_source)
    dicts.setdefault('new_introduce',newObj.new_introduce)
    dicts.setdefault('new_small_pic',newObj.new_small_pic)
    dicts.setdefault('city_name',newObj.city.city_name)
    dicts.setdefault('community_name',newObj.community.community_name)
    add_time = long(newObj.new_add_time)
    dicts.setdefault('new_add_time',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(add_time/1000)))
    dicts.setdefault('new_id',newObj.new_id)
    dicts.setdefault('new_content',newObj.new_content)
    
    if newObj.pri_flag == 0:
        dicts.setdefault('pri_flag',"否")
    else:
        dicts.setdefault('pri_flag',"是")
    return dicts
   
def ajax_new_del(request):
    
    if request.method == "GET":
        id = request.GET.get("id")
    try:
        newObj = News.objects.get(new_id =id)
        
        image_del(newObj.new_small_pic)
        content_image_del(newObj.new_content)
        newObj.delete()
        return commons.res_success("删除成功")
    except Exception, e:
        return commons.res_fail(1, "该数据不存在")
        

def image_del(path):
    if os.path.exists(path):
        os.remove(path)
    return 

def content_image_del(html_code):
      hp = MyHTMLParser()
      hp.feed(html_code)
      hp.close()
      for path in hp.links:
          #BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
          image_del(settings.BASE_ROOT+path)

def getNewMsgDict(pushType,contentType,title,message,userAvatar,pushTime,newsType,communityId,recordId=None):
    dicts = {}
    dicts.setdefault('pushType',pushType)
    dicts.setdefault('contentType',contentType)
    dicts.setdefault('title',title)
    dicts.setdefault('message',message)
    dicts.setdefault('userAvatar',userAvatar)
    dicts.setdefault('pushTime',pushTime)
    dicts.setdefault('newsType',newsType)
    dicts.setdefault('communityId',communityId)
    if recordId is None:
        pass
    else:
        dicts.setdefault('recordId',recordId)
    return dicts

def ajax_push_new(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    if request.method == "GET":
        ids = request.REQUEST.getlist("ids")
        community_id = request.REQUEST.get("community_id")
        
    communityName = Community.objects.get(community_id=long(community_id)).community_name
    # tag push     
    config = readIni()
    tagSuffix = config.get('news', "tagSuffix")
    pushTitle = config.get('news', "content0")
    customTitle = config.get("news", "content0")
    currentPushTime = long(time.time()*1000)
    userAvatar = settings.RES_URL+'res/default/avatars/default-comm-news.png'
    message1 = communityName + config.get("news", "content1")      
    custom_content = getNewMsgDict(5,1,pushTitle,message1,userAvatar,currentPushTime,2001,community_id)
    recordId = createPushRecord(5,1,customTitle,message1,currentPushTime,2001,json.dumps(custom_content),community_id,2001)   
    custom_content = getNewMsgDict(5,1,pushTitle,message1,userAvatar,currentPushTime,2001,community_id,recordId)
    apiKey = config.get("SDK", "apiKey")
    secretKey = config.get("SDK", "secretKey")
    tagName = tagSuffix+str(community_id)
    
    #新闻推送纪录
    try:
        idstring = (','.join(ids))
        push_time = currentPushTime
        pushObj = NewsPush.objects.create(push_newIds=idstring,push_time=push_time,community_id=community_id)
        #修改推送flag
        newIds = idstring.split(",")
        newObjList = News.objects.filter(new_id__in=newIds)
        for newObj in newObjList:
            newObj.push_flag=1   #是否推送,1:推送
            newObj.save()
        AsyncPushNew.delay(apiKey,secretKey,custom_content,tagName,message1,customTitle)
        return commons.res_success("推送成功")
    except Exception, e:
        return commons.res_fail(1, "该数据不存在")    
           
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
 
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            if len(attrs) == 0: pass
            else:
                for (variable, value)  in attrs:
                    if variable == "src":
                        self.links.append(value)
def ajax_new_data(request):
      #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    id = request.GET.get("id")
    try:
        newObj = News.objects.get(new_id =id)
    except:
        newObj = None
        pass
    cityObjs = City.objects.all()
    city_data = []
    for cityObj in cityObjs:
        item = {}
        item["label"] = cityObj.city_name
        item["text"] = cityObj.city_id
        city_data.append(item) 
    communityObjs = Community.objects.filter(city_id=newObj.city.city_id)
    community_data = []
    for communityObj in communityObjs:
        item = {}
        item["label"] = communityObj.community_name
        item["text"] = communityObj.community_id
        community_data.append(item)    
    json_data = {
        "new_id": newObj.new_id,
        "new_title": newObj.new_title,
        "new_source": newObj.new_source,
        "new_introduce": newObj.new_introduce,
        "pri_flag": newObj.pri_flag,
        "new_content": newObj.new_content,
        "new_small_pic": newObj.new_small_pic,
        "city_id": newObj.city.city_id,
        "city_name": newObj.city.city_name,
        "city_list":city_data,
        "community_id": newObj.community.community_id,
        "community_name": newObj.community.community_name,
        "community_list":community_data,
    }    
    return commons.res_success("请求成功", json_data)

# def ajax_new_mod(request):
#     if request.method == 'POST':
#         new_id = request.POST.get('new_id')
#         title = request.POST.get('title')
#         source = request.POST.get('source')
#         introduce = request.POST.get('introduce')
#         content = request.POST.get('content')
#         pri_flag = request.POST.get('pri_flag')
#         city_id = request.POST.get('city_id')
#         community_id = request.POST.get('community_id')
#         #新闻小图
#         file_name = ''
#         res_data = ""
#         try:
#             newObj = News.objects.get(new_id=new_id)
#             newObj.new_title = title
#             newObj.new_source = source
#             newObj.new_introduce = introduce
#             newObj.new_content = content
#             newObj.pri_flag = pri_flag
#             newObj.city_id = city_id
#             newObj.community_id = community_id
#             
#             small_pic = request.FILES.get('small_pic')
#             if small_pic :
#                 small_pic = request.FILES['small_pic']
#                 BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#                 postfix = (small_pic.name).split(".")[1].lower()
#                 postfixList = ['jpg','jpeg','gif','bmp','png']
#                 if not postfix in postfixList:
#                     message = "请上传jpg,jpeg,gif,bmp,png类型的图片"
#                     return commons.res_fail(1, message)
#                 
#                 path = BASE_ROOT+"/media/youlin/newspic/" 
#                 if not os.path.exists(path):
#                     os.mkdir(path, 0777)
#                 file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + small_pic.name
#                 file_path = path+file_name
#                 des_origin_f = open(file_path, "wb+")  
#                 for chunk in small_pic.chunks():
#                     des_origin_f.write(chunk)
#                 des_origin_f.close()
#                 file_jump = "/media/youlin/newspic/" + file_name
#                 image_del(newObj.new_small_pic)
#                 newObj.new_small_pic = file_jump
#             newObj.save()
#         except Exception, e:
#             return commons.res_success("修改fail", res_data)
#         res_data= "ok"
#         return commons.res_success("修改成功", res_data)
#     else:
#         raise Http404()
    
#意见统计
def ajax_feedback_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    
    #type = int(request.REQUEST.get("type"))
    type = 0
    res_data = getFeedBackList(page, page_size, type)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getFeedBackList(page, page_size, type):
    total = OpinionRecord.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    record_lists = OpinionRecord.objects.all().order_by("-opinion_id")[offset:limit]
    
    data = []
    if record_lists is not None:
        for i in record_lists:
            
            item = json.loads(i.toJSON())
            item["opinion_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(long(item["opinion_time"])/1000))
            if item['opinion_type'] == 1:
                item['opinion_type'] = '界面'
            elif item['opinion_type'] == 2:
                item['opinion_type'] = '功能'
            else:
                item['opinion_type'] = '其他'
            try:
                userObj = User.objects.get(user_id = item['user_id'])
            except Exception,e:
                userObj = None
            if  userObj is not None:
                item['user_id'] = userObj.user_phone_number 
            try:
                
                communityObj = Community.objects.get(community_id = item['community_id'])
            except Exception,e:
                communityObj = None
            if  communityObj is not None:
                item['community_id'] = communityObj.community_name  
            data.append(item)
    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data  

#物业信息管理
def ajax_property_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    
    res_data = getPropertyInfoList(page, page_size)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getPropertyInfoList(page, page_size):
    total = PropertyInfo.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    record_lists = PropertyInfo.objects.all().order_by("-info_id")[offset:limit]
    
    data = []
    if record_lists is not None:
        for i in record_lists: 
             
            item = json.loads(i.toJSON())
            try:
                cityObj = City.objects.get(city_id = item['sender_id'])
            except Exception,e:
                cityObj = None
                
            if  cityObj is not None:
                item['city_id'] = cityObj.city_name  
            try:
                communityObj = Community.objects.get(community_id = item['community_id'])
            except Exception,e:
                communityObj = None
                
            if  communityObj is not None:
                item['community_id'] = communityObj.community_name  
            data.append(item)
    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data 

def ajax_property_submit(request):
    print "物业"
    if request.method == 'GET':

        title         = request.GET.get('name', None)
        phone         = request.GET.get('phone', None)
        address       = request.GET.get('address', None)
        office_hours  = request.GET.get('office_hours', None)
        community_id  = request.GET.get('i_community_id', None)
        sender_id     = request.GET.get('i_city_id', None)
        idstr         = request.GET.get('idstr', None)
    if int(idstr) == 0:
        try:
            propertyInfo = PropertyInfo.objects.create(name = title,phone = phone,address=address,\
                                           office_hours=office_hours,sender_id=sender_id,community_id=community_id)
        except:
            return commons.res_fail(1, "创建物业信息失败")
    else:
        try:
            propertyInfo = PropertyInfo.objects.get(info_id = idstr)
        except Exception, e:
            return commons.res_fail(1, "该物业信息不存在")
        propertyInfo.name = title
        propertyInfo.phone = phone
        propertyInfo.address = address
        propertyInfo.office_hours = office_hours
        propertyInfo.community_id = community_id
        propertyInfo.sender_id = sender_id
        propertyInfo.save()
    
    return commons.res_success("添加成功")     
           
def ajax_property_del(request):
    print "物业信息删除"
    if request.method == "GET":
        id = request.GET.get("id")
    try:
        infoObj = PropertyInfo.objects.get(info_id =id)
        infoObj.delete()
        return commons.res_success("删除成功")
    except Exception, e:
        return commons.res_fail(1, "该数据不存在")
    
def ajax_getPropertyInfoById(request):
    #print "获取待修改物业信息"
    if request.method == 'GET':
        id         = request.GET.get('id', None)
    info_id = id.split('_')[1]
    try:
        propertyInfo = PropertyInfo.objects.get(info_id = info_id)
    except Exception, e:
        return commons.res_fail(1, "该物业信息不存在")
    cityObjs = City.objects.all()
    city_data = []
    for cityObj in cityObjs:
        item = {}
        item["label"] = cityObj.city_name
        item["text"] = cityObj.city_id
        city_data.append(item) 
    communityObjs = Community.objects.filter(city_id=propertyInfo.sender_id)
    community_data = []
    for communityObj in communityObjs:
        item = {}
        item["label"] = communityObj.community_name
        item["text"] = communityObj.community_id
        community_data.append(item)  
    response_data = {
        "city_id": propertyInfo.sender_id,
        "city_list":city_data,
        "community_id": propertyInfo.community_id,
        "community_list":community_data,
        "p_data":json.loads(propertyInfo.toJSON())
    }
    return commons.res_success("请求成功", response_data) 

def ajax_version_list(request):
    
        #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    res_data = getVersionList(page, page_size)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getVersionList(page, page_size):
    total = APK.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    apk_lists = APK.objects.all().order_by("-v_id")[offset:limit]
    data = []
    for i in apk_lists:
        item = json.loads(i.toJSON())
        item["v_time"] = time.strftime("%Y-%m-%d", time.localtime(int(item["v_time"])/1000))
        item["v_size"] = str(item["v_size"])+"MB"
        if int(item["v_force"]) == 0:
            item["v_force"] = "否"
        else:
            item["v_force"] = "是"
        data.append(item)

    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data 

@csrf_exempt
def ajax_version_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        function = request.POST.get('function')
        bug = request.POST.get('bug')
        force = request.POST.get('force')
        add_time = long(time.time()*1000)
        v_id = request.POST.get('idstr',None)
        if int(v_id) == 0:
            #新闻小图
            try:
                BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                inputfile = request.FILES.get("inputfile", None)
                if inputfile is not None :
	                postfix = (inputfile.name).split(".")[1].lower()
	                postfixList = ['apk']
	                if not postfix in postfixList:
	                    message = "请上传apk类型的文件"
	                    return commons.res_fail(1, message)
	                
	                path = BASE_ROOT+"/media/update/" 
	                if not os.path.exists(path):
	                    os.mkdir(path, 0777)
	                #file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + inputfile.name
	                file_path = path+inputfile.name
	                des_origin_f = open(file_path, "wb+")  
	                for chunk in inputfile.chunks():
	                    des_origin_f.write(chunk)
	                des_origin_f.close()
	                #size = inputfile.size/(1024*1024)
	                #size = int(inputfile.size)/(1024*1024)
	                size = round((int(inputfile.size)/float(1024*1024)),3)
	                url = "/media/update/" + inputfile.name
                else:
                	size = 0
                	url = ''
                apkObj = APK.objects.create(v_name = name,v_size = size,v_url=url,\
                                           v_force=force,v_function=function,v_bug=bug,v_time=add_time)	
                if int(force) == 1:
#                 	User.objects.all().update(user_push_user_id='')
					AsyncForcedReturn.delay()
                return commons.res_success("添加成功")  
            except Exception, e:
                return commons.res_fail(1, e)
        else:
            
            file_name = ''
            res_data = ""
            try:
                apkObj = APK.objects.get(v_id = v_id)
                apkObj.v_name = name
                apkObj.v_force = force
                apkObj.v_function = function
                apkObj.v_bug = bug
                
                inputfile = request.FILES.get("inputfile", None)
                if inputfile is not None :
                    BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))

                    postfix = (inputfile.name).split(".")[1].lower()
                    postfixList = ['apk']
                    if not postfix in postfixList:
                        message = "请上传apk类型的文件"
                        return commons.res_fail(1, message)
                    
                    path = BASE_ROOT+"/media/update/" 
                    if not os.path.exists(path):
                        os.mkdir(path, 0777)
                    #file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + inputfile.name
                    file_path = path+inputfile.name
                    des_origin_f = open(file_path, "wb+")  
                    for chunk in inputfile.chunks():
                        des_origin_f.write(chunk)
                    des_origin_f.close()
                    size = round((int(inputfile.size)/float(1024*1024)),3)
                    url = "/media/update/" + inputfile.name
                    apkObj.v_size = size
                    apkObj.v_url = url
                apkObj.save()
                if int(force) == 1:
# 					User.objects.all().update(user_push_user_id='')
					AsyncForcedReturn.delay()
            except Exception, e:
                return commons.res_success("修改失败", res_data)
            return commons.res_success("修改成功")
    else:
        raise Http404()
    
def ajax_version_del(request):
    
    if request.method == "GET":
        id = request.GET.get("id")
    try:
        apkObj = APK.objects.get(v_id =id)
#         BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
#         image_del(BASE_ROOT+apkObj.v_url)
        apkObj.delete()
        return commons.res_success("删除成功")
    except Exception, e:
        return commons.res_fail(1, "该数据不存在")
    
def ajax_getVersionById(request): 
    #print "获取待修改版本"
    if request.method == 'GET':
        id         = request.GET.get('id', None)
    v_id = id.split('_')[2]
    try:
        apkObj = APK.objects.get(v_id = v_id)
    except Exception, e:
        return commons.res_fail(1, "该版本信息不存在")
 
    response_data = {
        "list":json.loads(apkObj.toJSON())
    }
    return commons.res_success("请求成功", response_data) 

def ajax_audit_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    
    type = int(request.REQUEST.get("type"))
    
    res_data = getList(page, page_size, type)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getList(page, page_size, type):
    total = Admin.objects.filter(admin_type= type).count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    admin_lists = Admin.objects.filter(admin_type= type).order_by("-admin_id")[offset:limit]
    data = []
    for i in admin_lists:
        item = json.loads(i.toJSON())
        item["app_time"] = time.strftime("%Y-%m-%d", time.localtime(item["app_time"]/1000))
        data.append(item)

    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data    
  
  
def ajax_gift_list(request):
    #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    res_data = getGiftList(page, page_size)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getGiftList(page, page_size):
    total = Giftlist.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    gift_lists = Giftlist.objects.filter().order_by("-gl_id")[offset:limit]
    data = []
    for i in gift_lists:
        item = json.loads(i.toJSON())
        item["gl_start_time"] = time.strftime("%Y-%m-%d", time.localtime(item["gl_start_time"]/1000))
        if item["gl_status"] == 0:
            item["gl_status"] = "否"
        else:
            item["gl_status"] = "是"
        data.append(item)

    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data 

@csrf_exempt
def ajax_gift_submit(request):
    if request.method == 'POST':
        gl_name = request.POST.get('gl_name')
        gl_credit = request.POST.get('gl_credit')
        community_id = request.POST.get('community_id')
        add_time = long(time.time()*1000)
        v_id = request.POST.get('idstr',None)
        
        if int(v_id) == 0:
            #礼品图片
            try:
                BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                inputfile = request.FILES.get("gl_pic", None)
                postfix = (inputfile.name).split(".")[1].lower()
                postfixList = ['bmp','jpg','jpeg','png','gif']
                if not postfix in postfixList:
                    message = "请上传bmp、jpg、jpeg、png、gif类型的图片"
                    return commons.res_fail(1, message)
                
                path = BASE_ROOT+"/media/gift/" 
                if not os.path.exists(path):
                    os.mkdir(path, 0777)
                
                file_path = path+inputfile.name
                if not os.path.exists(file_path):
                    des_origin_f = open(file_path, "wb+")  
                    for chunk in inputfile.chunks():
                        des_origin_f.write(chunk)
                    des_origin_f.close()
                else:
                    message2 = "该文件名已存在，请更换"
                    return commons.res_fail(1, message2)
                thumb_name = (inputfile.name).split(".")[0]+"-t."+postfix
                thumb_path = os.path.join(path,thumb_name)
                makeThumbnail(thumb_path,file_path)
                url = "/media/gift/" + thumb_name
                gift = Giftlist()
                gift.gl_pic = url
                gift.gl_status = 0
                gift.gl_credit = gl_credit     
                gift.gl_name = gl_name
                gift.gl_start_time = add_time 
                gift.gl_community_id = community_id
                gift.save()
                return commons.res_success("添加成功")  
            except Exception, e:
                return commons.res_fail(1, e)
        else:
            res_data = ""
            try:
                gift = Giftlist.objects.get(gl_id = v_id)
                
                gift.gl_status = 0
                gift.gl_credit = gl_credit     
                gift.gl_name = gl_name
                gift.gl_start_time = add_time 
                gift.gl_community_id = community_id
                
                inputfile = request.FILES.get("gl_pic", None)
                if inputfile is not None :
                    BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                    inputfile = request.FILES.get("gl_pic", None)
                    postfix = (inputfile.name).split(".")[1].lower()
                    postfixList = ['bmp','jpg','jpeg','png','gif']
                    if not postfix in postfixList:
                        message = "请上传bmp、jpg、jpeg、png、gif类型的图片"
                        return commons.res_fail(1, message)
                    
                    path = BASE_ROOT+"/media/gift/" 
                    if not os.path.exists(path):
                        os.mkdir(path, 0777)
                    
                    file_path = path+inputfile.name
                    if not os.path.exists(file_path):
                        des_origin_f = open(file_path, "wb+")  
                        for chunk in inputfile.chunks():
                            des_origin_f.write(chunk)
                        des_origin_f.close()
                    else:
                        message2 = "该文件名已存在，请更换"
                        return commons.res_fail(1, message2)
                    thumb_name = (inputfile.name).split(".")[0]+"-t."+postfix
                    thumb_path = os.path.join(path,thumb_name)
                    makeThumbnail(thumb_path,file_path)
                    
                    thumbPath = BASE_ROOT+gift.gl_pic
                    image_del(thumbPath)
                    
                    str = gift.gl_pic
                    big = str.split('-t.')[0]+"."+str.split('-t.')[1];
                    path = BASE_ROOT+big
                    image_del(path)
                    url = "/media/gift/" + thumb_name
                    gift.gl_pic = url
                gift.save()
            except Exception, e:
                return commons.res_fail(1, e)
            #response_data = {}
            #response_data['flag'] = 'ok'
            return commons.res_success("修改成功")
            #return HttpResponse(json.dumps(response_data), content_type="application/json") 
    else:
        raise Http404()
    
def makeThumbnail(thumb_path,path):
    im = Image.open(path)
    mode = im.mode
    if mode not in ('L', 'RGB'):
        im = im.convert('RGB')
    width, height = im.size
    if width>124:
        nwidth = 124
        nheight = int(height * 124/width)
        size = (nwidth, nheight)
        im.thumbnail(size, Image.ANTIALIAS) 
    im.save(thumb_path) 
    
def ajax_gift_del(request):
    if request.method == "GET":
        id = request.GET.get("id")
    try:
        giftObj = Giftlist.objects.get(gl_id =id)
        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
       
        thumbPath = BASE_ROOT+giftObj.gl_pic
        image_del(thumbPath)
        
        str = giftObj.gl_pic
        big = str.split('-t.')[0]+"."+str.split('-t.')[1];
        path = BASE_ROOT+big
        image_del(path)
        
        giftObj.delete()
        return commons.res_success("删除成功")
    except Exception, e:
        return commons.res_fail(1, e)    
    
def ajax_getGiftById(request): 
    #print "获取待修改版本"
    if request.method == 'GET':
        id         = request.GET.get('id', None)
    v_id = id.split('_')[2]
    try:
        giftObj = Giftlist.objects.get(gl_id = v_id)
    except Exception, e:
        return commons.res_fail(1, e)
    
    communityObjs = Community.objects.all()
    community_data = []
    for communityObj in communityObjs:
        item = {}
        item["label"] = communityObj.community_name
        item["text"] = communityObj.community_id
        community_data.append(item)
    response_data = {
        "list":json.loads(giftObj.toJSON()),
        "community_list":community_data
    }
    return commons.res_success("请求成功", response_data)

def ajax_gift_release(request):
    #print "发布"
    if request.method == 'GET':
        ids         = request.GET.get('ids', None)
    if ids is not None:
        vIds = ids.split(",")
        try:
            giftObjList = Giftlist.objects.filter(gl_id__in=vIds)
            for giftObj in giftObjList:
                giftObj.gl_status=1   #wei兑换,1:兑换
                giftObj.save()
            return commons.res_success("发布成功")
        except Exception, e:
            return commons.res_fail(1, e)
    return commons.res_fail(1, "请选择需要发布的礼品!")
    
    
def ajax_gift_down(request):
    if request.method == "GET":
        id = request.GET.get("id")
    try:
        giftObj = Giftlist.objects.get(gl_id =id)
        gl_end_time = long(time.time()*1000)
        giftObj.gl_end_time = gl_end_time
        giftObj.gl_status = 0    
        giftObj.save()
        return commons.res_success("礼品下架成功")
    except Exception, e:
        return commons.res_fail(1, e)  
    
    
def ajax_exchange_list(request):
        #需要登录才可以访问
    #if not request.session.get("sess_admin", False):
    #    return commons.res_fail(1, "需要登录才可以访问")
    
    #分页索引和每页显示数
    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    res_data = getExchangeList(page, page_size)
    return commons.res_success("请求成功", res_data)
        

#获取分页数据
def getExchangeList(page, page_size):
    total = UserExchange.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size

    ue_lists = UserExchange.objects.filter().order_by("-ue_id")[offset:limit]
    data = []
    for i in ue_lists:
        item = json.loads(i.toJSON())

       # item["ue_time"] = time.strftime("%Y-%m-%d", time.localtime(item["ue_time"]/1000))
        try:
            communityObj = Community.objects.get(community_id=item["community_id"])
            item["community_id"] = communityObj.community_name
        except DoesNotExist:
            communityObj = None
            item["community_id"] = "----"
        
        try:
            userObj = User.objects.get(user_id =item["user_id"])
            item["user_id"] = userObj.user_phone_number
        except:
            userObj = None
            item["user_id"] = "----"
            pass
        
        try:
            giftObj = Giftlist.objects.get(gl_id=item["ue_glid"])
            item["ue_glid"] = giftObj.gl_name
        except:
            userObj = None
            item["ue_glid"] = "----"
            pass
        
        if item["ue_status"] == 2:
            item["ue_status"] = "已兑换"
        else:
            item["ue_status"] = "进行中"
            
        
        data.append(item)

    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data 

def ajax_exchange_status(request):
    
    if request.method == 'GET':
        ids         = request.GET.get('ids', None)
    if ids is not None:
        vIds = ids.split(",")
        try:
            ueObjList = UserExchange.objects.filter(ue_id__in=vIds)
            for ueObj in ueObjList:
                ueObj.ue_status=2   #兑换礼品状态 1进行中 2已交换
                ueObj.save()
            return commons.res_success("更改兑换状态成功")
        except Exception, e:
            return commons.res_fail(1, e)
    return commons.res_fail(1, "请选择需要更改兑换状态的记录!")

@csrf_exempt
def ajax_export_submit(request):

    if request.method == 'POST':
        conditon       = request.POST.get('conditon', None)
    if conditon is not None:
        conditonList     = conditon.split(";")
        try:
            endDate = time.mktime(time.strptime(str(conditonList[0]),'%Y-%m-%d'))*1000
            beginDate = time.mktime(time.strptime(str(conditonList[1]),'%Y-%m-%d'))*1000
            ueObjList = UserExchange.objects.filter(ue_time__lte = endDate,ue_time__gte = beginDate,community_id=conditonList[2],ue_status=conditonList[3])

            wb = xlwt.Workbook(encoding = 'utf-8')
            sheet = wb.add_sheet(u'兑换记录')
            #1st line   
            sheet.write(0,0, '礼品名称')
            sheet.write(0,1, '兑换数量')
            sheet.write(0,2, '兑换时间')
            sheet.write(0,3, '兑换状态')
            sheet.write(0,4, '手机号')
            sheet.write(0,5, '兑换者所在小区')
            sheet.write(0,6, '签字')

            row = 1
            for i in ueObjList:
                item = json.loads(i.toJSON())
                try:
                    communityObj = Community.objects.get(community_id=item["community_id"])
                    community_name = communityObj.community_name
                except:
                    community_name = ""
                
                try:
                    userObj = User.objects.get(user_id =item["user_id"])
                    user_phone_number = userObj.user_phone_number
                except:
                    user_phone_number = ""
                    pass
                
                try:
                    giftObj = Giftlist.objects.get(gl_id=item["ue_glid"])
                    gl_name = giftObj.gl_name
                except:
                    gl_name = ""
                    pass
                ue_time = time.strftime("%Y-%m-%d", time.localtime(item["ue_time"]/1000))
                if item["ue_status"] == 2:
                    item["ue_status"] = "已兑换"
                else:
                    item["ue_status"] = "进行中"
                    
                sheet.write(row,0, gl_name)
                sheet.write(row,1, item['ue_count'])
                sheet.write(row,2, ue_time)
                sheet.write(row,3, item['ue_status'])
                sheet.write(row,4, user_phone_number)
                sheet.write(row,5, community_name)
                sheet.write(row,6, "")
                row=row + 1
            BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
            path = BASE_ROOT+'/media/export.xls'
            wb.save(path)
            filename = "兑换记录-"+str(datetime.date.today())+".xls"
            wrapper = FileWrapper(file(path))
            response = HttpResponse(wrapper, content_type='application/vnd.ms-excel')
            response['Content-Length'] = os.path.getsize(path)
            response['Content-Encoding'] = 'utf-8'
            response['Content-Disposition'] = 'attachment;filename=%s' % filename
            return response

        except Exception, e:
            return commons.res_fail(1, e)
    return commons.res_fail(1, "导出条件不能为空!")


#删除公众号
def del_Subscription(request):
    if request.method == 'POST':
       id        = request.POST.get('id',None)    
    else:
       id          = request.GET.get('id',None)
    try:
        SubscriptionObj = Subscription.objects.get(s_id =id)
        BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
        a= file_del(BASE_ROOT+SubscriptionObj.s_url)
        if not a is False:
            SubscriptionObj.delete()
            return commons.res_success("删除文件成功")
        else:
            SubscriptionObj.delete()
            return commons.res_success("该文件不存在，已删除数据库记录")

    except Exception, e:
        message= "该版本不存在"
        return commons.res_fail(1, message) 
  
def file_del(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    else:
        return  False
    
#公众号表单回显    
def echo_Subscription(request):
    if request.method == 'POST':
       id        = request.POST.get('id',None)  
    else:
       id          = request.GET.get('id',None)
       
       dataObj = Subscription.objects.get(s_id=id)   
    retList = []
    if  dataObj:
             set = {}
             set['city_id'] = dataObj.city_id
             set['s_url'] = dataObj.s_url
             set['s_name'] = dataObj.s_name
             set['s_id'] = dataObj.s_id
             set['community_id'] = dataObj.community_id
             retList.append(set)
    responseData ={}
    responseData['data'] = retList
    return HttpResponse(json.dumps(responseData), content_type="application/json")

                        
 #分页索引      
def ajax_subscription_list(request):

    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    res_data = getSubscriptionList(page, page_size)
    response_data = {}
    response_data['data'] = res_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

        

#获取分页数据
def  getSubscriptionList(page, page_size):
    total = Subscription.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size
    
    dataList = Subscription.objects.all().order_by("s_id")
       
    retList = []
    if dataList:
        for dataObj in dataList:
            cityObj = City.objects.get(city_id =dataObj.city_id)
            CommunityObj=Community.objects.get(community_id =dataObj.community_id)
           
            set = {}
            set['city'] = cityObj.city_name
            set['community'] = CommunityObj.community_name
            set['url'] = dataObj.s_url
            set['name'] = dataObj.s_name
            set['id'] = dataObj.s_id
            retList.append(set)
   # d=len(retList)           
    data=[]
    data=retList[offset:limit]
   # b=len(data)
    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data


  #上传图片文件
@csrf_exempt
def ajax_subscription_submit(request):
    if request.method == 'POST':
        sub_id=request.POST.get('sub_id',None)
        city_id=request.POST.get('city_id',None)
        com_id = request.POST.get('com_id',None)
        name = request.POST.get('v_subscription',None)
        
        sub_id=int(sub_id)
        if sub_id==-1:
            name1 =name or None
            city_id=int(city_id)
            com_id=int(com_id)
    
            if name1 is None :
                message = "亲，公众号名称 不能为空哦～"
                return commons.res_fail(1, message) 
            elif city_id<0:
                message = "亲，请选择城市～"
                return commons.res_fail(1, message)
            elif com_id<0:
                message= "亲，请选择小区～"
                return commons.res_fail(1, message)
    
            else:
                try:
                    BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                    inputfile = request.FILES.get("inputfile", None)
                    if inputfile is None:
                      message = "亲，忘记上传头像图片了哦～"
                      return commons.res_fail(1, message) 
                    postfix = (inputfile.name).split(".")[-1].lower()
                    postfixList = ['bmp','jpg','jpeg','png','gif']
                    if not postfix in postfixList:
                        message = "请上传bmp、jpg、jpeg、png、gif类型的图片"
                        return commons.res_fail(1, message)   
                    else:
                        path = BASE_ROOT+"/media/subscription/" 
                        if not os.path.exists(path):
                            os.mkdir(path, 0777)             
                        file_path = path+inputfile.name
                        if not os.path.exists(file_path):
                            des_origin_f = open(file_path, "wb+")  
                            for chunk in inputfile.chunks():
                                des_origin_f.write(chunk)
                            des_origin_f.close()
                        else:
                            message = "文件名已存在，请更换文件名"
                            return commons.res_fail(1, message) 
                        size = round((int(inputfile.size)/float(1024*1024)),3)
                        url = "/media/subscription/" + inputfile.name
                        Obj =Subscription.objects.create(s_name = name,s_url=url,\
                                                       city_id=city_id,community_id=com_id)
                        return commons.res_success("上传成功") 
                except Exception, e:
                    message = "上传失败"
                    return commons.res_fail(1, message) 
                
        else:
            
            name1 =name or None
            city_id=int(city_id)
            com_id=int(com_id)
    
            if name1 is None :
                message = "亲，公众号名称 不能为空哦～"
                return commons.res_fail(1, message)
            elif city_id<0:
                message = "亲，请选择城市～"
                return commons.res_fail(1, message)
                
            elif com_id<0:
                message = "亲，请选择小区～"
                return commons.res_fail(1, message)
            else:
                 try:
                    BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                    inputfile = request.FILES.get("inputfile", None)
                    
                    if inputfile is None:
                        dataList= Subscription.objects .get(s_id=sub_id)
                        dataList.s_name=name
                        dataList.city_id=city_id
                        dataList.community_id=com_id
                        dataList.save()
                        return commons.res_success("修改成功") 
                    else:
                        postfix = (inputfile.name).split(".")[-1].lower() 
                        postfixList = ['bmp','jpg','jpeg','png','gif']
                        if not postfix in postfixList:
                            message = "请上传bmp、jpg、jpeg、png、gif类型的图片"
                            return commons.res_fail(1, message)   
                        else:
                            SubObj = Subscription.objects .get(s_id=sub_id)
                            path = BASE_ROOT+"/media/subscription/" 
                            if not os.path.exists(path):
                                os.mkdir(path, 0777)
                            file_path = path+inputfile.name
                            if not os.path.exists(file_path):
                                file_del(BASE_ROOT+SubObj.s_url)
                                des_origin_f = open(file_path, "wb+")  
                                for chunk in inputfile.chunks():
                                    des_origin_f.write(chunk)
                                des_origin_f.close()
                            else:
                                message = "头像文件已存在，请更换文件"
                                return commons.res_fail(1, message)
                            size = round((int(inputfile.size)/float(1024*1024)),3)
                            url = "/media/subscription/" + inputfile.name
                                
                            dataList= Subscription.objects .get(s_id=sub_id)
                            dataList.s_name=name
                            dataList.city_id=city_id
                            dataList.community_id=com_id
                            dataList.s_url=url
                            dataList.save() 
                            return commons.res_success("修改成功") 
                 except Exception, e:
                            message = "修改失败"
                            return commons.res_fail(1, message)
                        
                        
                        
                        
                        
                        
                        
 #角色分页索引      
def ajax_role_list(request):

    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    res_data = getRoleList(page, page_size)
    response_data = {}
    response_data['data'] = res_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

        

#获取分页数据
def  getRoleList(page, page_size):
    total = Role.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size
    
    dataList = Role.objects.all().order_by("r_id")
       
    retList = []
    if dataList:
        for dataObj in dataList: 
            set = {}
            set['describe'] = dataObj.r_describe
            set['name'] = dataObj.r_name
            set['id'] = dataObj.r_id
            set['root'] = dataObj.r_root
            retList.append(set)
   # d=len(retList)           
    data=[]
    data=retList[offset:limit]
   # b=len(data)
    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data


  #上传角色
@csrf_exempt
def ajax_role_submit(request):
    if request.method == 'POST':
        r_id=request.POST.get('role_id',None)
        r_name=request.POST.get('role_name',None)
        r_describe = request.POST.get('role_describe',None)
        r_root=request.POST.get('role_root',None)
        r_id=int(r_id)
        r_root=int(r_root)
        
        if r_id== -1:
            name =r_name or None
            describe=r_describe or None
            try:
                if name is None :
                    message = "亲，角色名称 不能为空哦～"
                    return commons.res_fail(1, message) 
                elif describe is None :
                    message = "亲，角色描述 不能为空哦～"
                    return commons.res_fail(1, message) 
                else:
                    Obj =Role.objects.create(r_name = r_name,r_describe =r_describe ,r_root=1)
                    return commons.res_success("添加角色成功") 
            except Exception, e:
                    message = "添加角色失败"
                    return commons.res_fail(1, message) 
                
        else:
            try:
                if r_root ==1:
                    name =r_name or None
                    describe=r_describe or None
                    try:
                        if name is None :
                            message = "亲，角色名称 不能为空哦～"
                            return commons.res_fail(1, message) 
                        elif describe is None :
                            message = "亲，角色描述 不能为空哦～"
                            return commons.res_fail(1, message)
                        else:
                             dataList= Role.objects .get(r_id=r_id)
                             dataList.r_name=r_name
                             dataList.r_describe=r_describe
                             dataList.save()
                             return commons.res_success("修改成功") 
                    except Exception, e:
                          message = "超级管理员不允许修改"
                          return commons.res_fail(0, message)
                           

            except Exception, e:
                message = "修改失败"
                return commons.res_fail(0, message)
            
            
            
#Role表单回显    
def echo_Role(request):
    if request.method == 'POST':
       r_id        = request.POST.get('r_id',None)  
    else:
       r_id          = request.GET.get('r_id',None)
       
       dataObj = Role.objects.get(r_id=r_id)   
    retList = []
    if  dataObj:
             set = {}
             set['r_id'] = dataObj.r_id
             set['r_name'] = dataObj.r_name
             set['r_describe'] = dataObj.r_describe
             set['r_root'] = dataObj.r_root
             retList.append(set)
    responseData ={}
    responseData['data'] = retList
    return HttpResponse(json.dumps(responseData), content_type="application/json")


#删除Role
def del_Role(request):
    if request.method == 'POST':
       r_id        = request.POST.get('r_id',None)    
    else:
       r_id          = request.GET.get('r_id',None)
    try:
        r_id=int(r_id)
        roleObj = Role.objects.get(r_id =r_id)
        roleObj.delete()
        return commons.res_success("删除角色成功")

    except Exception, e:
        message= "删除失败"
        return commons.res_fail(1, message)
    
#生成角色下拉菜单
def ajax_role_data(request):
    role_lists = Role.objects.filter()
    role_list_json = []
    for role in role_lists:        
        item={}
        item['text']=role.r_id
        item['label']=role.r_name    
        role_list_json.append(item)
        
    return HttpResponse(json.dumps(role_list_json), content_type="application/json") 
   
   
def count_charnum(s):
	s1 = s
	s2 = s.lower();#字符串转换成小写
	fomart = 'abcdefghijklmnopqrstuvwxyz0123456789'
	for c in s2:
		if not c in fomart:
			s1 = s1.replace(c,'');
			
	return s1;
  
  #生成用户                      
@csrf_exempt
def ajax_webUser_submit(request):
    if request.method == 'POST':
        name        = request.POST.get('name',None)
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        active = request.POST.get('active')
        city_id= request.POST.get('city_id')
        com_id = request.POST.get('com_id')
        role_id = request.POST.get('role_id')
        
        v_id = request.POST.get('idstr',None)
        
        name						= name or None
        password				= password or None
        repassword			= repassword or None
        email						= email or None
        phone					=phone or None
        active						= active or None
        city_id					= city_id or None
        com_id					= com_id or None
        role_id					= role_id or None
        v_id							=int(v_id)

        
        if v_id == -1:
        	#email_match							=re.compile('[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+([A-Za-z]{2,3})+$')
        	email_match							=re.compile('^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$')
        	phone_match							=re.compile('^177\d{8}$|^1[358]\d{9}$|^147\d{8}$')
        	psw_match								=re.compile('^[A-Za-z0-9]{6,16}$')
        	name_match							=re.compile('^[a-zA-Z][a-zA-Z0-9_]{3,14}[a-zA-Z0-9]$')
         	try:
	        	if name==None:
	        		return commons.res_fail(1, "名称不能为空")
 	        	elif name.find(" ") >0:
 	        		return commons.res_fail(1, "名称不能含有空格")
	        	name										= name.replace(' ', '')
	        	if name_match.match(str(name)) ==None:
	        		return commons.res_fail(1, "格式错误,用户名为6-16位的字母数字下划线组成，且需以字母开头，不能以下划线结尾")
	        	elif password==None:
	        		return commons.res_fail(1, "密码不能为空")
	        	elif psw_match.match(str(password)) ==None:
	        		return commons.res_fail(1, "密码格式不正确，请输入6-16位字母或数字组合")
	        	elif repassword==None:
	        		return commons.res_fail(1, "确认密码不能为空")
	        	elif password != repassword:
	        		return commons.res_fail(1, "两次输入密码不一致")
	        	elif email ==None:
	        		return commons.res_fail(1, "邮箱不能为空")        	
	        	elif phone==None:
	        		return commons.res_fail(1, "电话不能为空")
	        	elif int(city_id)==-1:
	        		return commons.res_fail(1, "未选择城市")
	        	elif int(com_id)==-1:
	        		return commons.res_fail(1, "未选择小区")
	        	elif int(role_id)==-1:
	        		return commons.res_fail(1, "未选择角色")
	        	elif len(str(phone)) !=11:
	        		return commons.res_fail(1, "请检查号码长度")
	        	elif phone_match.match(str(phone)) ==None:
	        		return commons.res_fail(1, "手机号格式不正确")
	        	elif email_match.match(email) ==None:
	        		return commons.res_fail(1, "邮箱格式不正确")
	        	
	        	else:
	        		total= WebUser.objects.filter(u_name = name.encode("utf-8")).count()
	        		if total > 0:
	        			return commons.res_fail(1, "该用户已存在")
	        		else:
	        			password=webmd5(password, name)
	        			Obj =WebUser.objects.create(u_name = name,u_password =password ,u_email=email,\
											u_phone_number=phone,u_state=active,\
											role_id=role_id,city_id=city_id,community_id=com_id)
	        			return commons.res_success(0,"上传用户信息成功")
 	      	except Exception, e:
 	      		message= "创建用户失败"
 	       		return commons.res_fail(1, message)
        		

        else:
        	email_match							=re.compile('^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$')
        	phone_match							=re.compile('^177\d{8}$|^1[358]\d{9}$|^147\d{8}$')
#        	psw_match								=re.compile('^[A-Za-z0-9]{6,16}$')
        	name_match							=re.compile('^[a-zA-Z][a-zA-Z0-9_]{3,14}[a-zA-Z0-9]$')
        	dataObj= WebUser.objects .get(u_id=v_id)
         	try:
         		
	        	if name==None:
	        		return commons.res_fail(1, "名称不能为空")
 	        	elif name.find(" ") >0:
 	        		return commons.res_fail(1, "名称不能含有空格")
	        	name										= name.replace(' ', '')
	        	if name_match.match(str(name)) ==None:
	        		return commons.res_fail(1, "格式错误,用户名为6-16位的字母数字下划线组成，且需以字母开头，不能以下划线结尾")
	        	
 	        	total= WebUser.objects.filter(u_name = name.encode("utf-8")).count()	
# 	        	if password==None:
# 	        		return commons.res_fail(1, "密码不能为空")
# 	        	elif psw_match.match(str(password)) ==None:
# 	        		return commons.res_fail(1, "密码格式不正确，请输入6-16位字母或数字组合")
# 	        	elif repassword==None:
# 	        		return commons.res_fail(1, "确认密码不能为空")
# 	        	elif password != repassword:
# 	        		return commons.res_fail(1, "两次输入密码不一致")
	        	if email ==None:
	        		return commons.res_fail(1, "邮箱不能为空")        	
	        	elif phone==None:
	        		return commons.res_fail(1, "电话不能为空")
	        	elif int(city_id)==-1:
	        		return commons.res_fail(1, "未选择城市")
	        	elif int(com_id)==-1:
	        		return commons.res_fail(1, "未选择小区")
	        	elif int(role_id)==-1:
	        		return commons.res_fail(1, "未选择角色")
	        	elif len(str(phone)) !=11:
	        		return commons.res_fail(1, "请检查号码长度")
	        	elif phone_match.match(str(phone)) ==None:
	        		return commons.res_fail(1, "手机号格式不正确")
	        	elif email_match.match(email) ==None:
	        		return commons.res_fail(1, "邮箱格式不正确")
	        	elif name.encode("utf-8")==dataObj.u_name:
	        		#password										=webmd5(password, name)
	        		dataList										= WebUser.objects .get(u_id=v_id)
	        		dataList.u_name						=name
	        		#dataList.u_password				=password
	        		dataList.u_email						=email
	        		dataList.u_phone_number	=phone
	        		dataList.u_state							=active
	        		dataList.role_id							=role_id
	        		dataList.city_id							=city_id
	        		dataList.community_id			=com_id
	        		dataList.save()
	        		return commons.res_success("修改成功") 
	        	else:
	        		#
	        		if total > 0:
	        			return commons.res_fail(1, "该用户已存在")
	        		else:
	        			#password										=webmd5(password, name)
		        		dataList										= WebUser.objects .get(u_id=v_id)
		        		dataList.u_name						=name
		        		#dataList.u_password				=password
		        		dataList.u_email						=email
		        		dataList.u_phone_number	=phone
		        		dataList.u_state							=active
	                 	dataList.role_id							=role_id
	                 	dataList.city_id							=city_id
	                 	dataList.community_id			=com_id
	                 	dataList.save()
	                 	return commons.res_success("修改成功") 
	        	
	        except Exception, e:
	        	message= "修改用户失败"
 	       		return commons.res_fail(1, message)

#用户密码md5加密    
def webmd5(password,name):
    import hashlib
    m					= hashlib.md5()  
    password		=str(password)
    name				=str(name)
    c=password+name
    m.update(c)
    return m.hexdigest()




 #用户分页索引      
def ajax_webUser_list(request):

    page = 1
    if request.REQUEST.get("page"):
        page = int(request.REQUEST.get("page"))
    page_size = cfg.page_size
    if request.REQUEST.get("page_size"):
        page_size = int(request.REQUEST.get("page_size"))
    res_data = getwebUserList(page, page_size)
    response_data = {}
    response_data['data'] = res_data
    return HttpResponse(json.dumps(response_data), content_type="application/json")

        

#获取用户分页数据
def  getwebUserList(page, page_size):
    total = WebUser.objects.all().count()
    page_count = commons.page_count(total, page_size)

    offset = (page - 1) * page_size
    limit = offset + page_size
    
    dataList = WebUser.objects.all().order_by("u_id")
       
    retList = []
    if dataList:
        for dataObj in dataList:
        	
        	 cityObj = City.objects.get(city_id =dataObj.city_id)
        	 ComObj=Community.objects.get(community_id =dataObj.community_id)
        	 roleObj=Role.objects.get(r_id =dataObj.role_id)
        	 if int(dataObj.u_state)==1:
        	 	state="激活"
        	 else:
        	 	state="未激活"
        	 	
        	 
        	 set = {}
        	 set['city'] 						= cityObj.city_name
        	 set['community'] 		= ComObj.community_name
        	 set['id']							= dataObj.u_id
        	 set['name']		 			= dataObj.u_name
        	 set['password'] 		= dataObj.u_password
        	 set['email'] 					= dataObj.u_email
        	 set['phone'] 				= dataObj.u_phone_number
        	 set['state'] 					= state
        	 set['role'] 					= roleObj.r_name
#         	 set['city'] 						= cityObj.city_name
#         	 set['community'] 		= CommunityObj.community_name
        	 retList.append(set)
   # d=len(retList)           
    data=[]
    data=retList[offset:limit]
   # b=len(data)
    data = {
        "page_size": page_size,
        "page_count": page_count,
        "total": total,
        "page": page,
        "list": data,
    }
    return data
   
   
   
   
   #删除用户
def del_webUser(request):
    if request.method == 'POST':
       id        = request.POST.get('id',None)    
    else:
       id          = request.GET.get('id',None)
    try:
        u_id=int(id)
        UserObj = WebUser.objects.get(u_id =u_id)
        UserObj.delete()
        return commons.res_success("删除用户成功")

    except Exception, e:
        message= "删除失败"
        return commons.res_fail(1, message)
       
       
#USER表单回显    
def echo_webUser(request):
    if request.method == 'POST':
       id        = request.POST.get('id',None)  
    else:
       id          = request.GET.get('id',None)
       
       u_id=int(id)
       dataObj = WebUser.objects.get(u_id =u_id)
    retList = []
    if  dataObj:
    	set = {}
    	set['city'] 						= dataObj.city_id
    	set['community'] 		= dataObj.community_id
    	set['id']							= dataObj.u_id
    	set['name']		 			= dataObj.u_name
    	set['password'] 			= dataObj.u_password
    	set['email'] 					= dataObj.u_email
    	set['phone'] 				= dataObj.u_phone_number
    	set['state'] 					= dataObj.u_state
    	set['role'] 						= dataObj.role_id
    	retList.append(set)
    responseData ={}
    responseData['data'] = retList
    return HttpResponse(json.dumps(responseData), content_type="application/json")
   
   


@csrf_exempt
def ajax_life_submit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        date = request.POST.get('date')
        content = request.POST.get('content')
        yl_id = request.POST.get('idstr',None)
        if int(yl_id) == 0:       
            #新闻小图
            try:
                #BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                avatar = request.FILES.get("avatar", None)
                if avatar is not None:
                	
                 	postfix = (avatar.name).split(".")[1].lower()
                  	postfixList = ['jpg','jpeg','gif','bmp','png']
	                if not postfix in postfixList:
	                    message = "请上传jpg,jpeg,gif,bmp,png类型的图片"
	                    return commons.res_fail(1, message)
	                
	                path = settings.BASE_ROOT+"/media/youlin/life/" 
	                if not os.path.exists(path):
	                    os.mkdir(path, 0777)
	                file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + avatar.name
	                file_path = path+file_name
	                des_origin_f = open(file_path, "wb+")  
	                for chunk in avatar.chunks():
	                    des_origin_f.write(chunk)
	                des_origin_f.close()
	                file_jump = "/media/youlin/life/" + file_name
                else:
                	file_jump = "/media/youlin/res/default/avatars/head.jpg"
                ylObj = YLife.objects.create(yl_title = title,yl_author = author,\
											yl_date = date,yl_content=content,yl_avatar=file_jump,yl_flag=0)
                response_data = {}
                response_data['flag'] = 'ok'
                return HttpResponse(json.dumps(response_data), content_type="application/json")   
            except Exception, e:
                print e
        else:
            
            file_name = ''
            res_data = ""
            try:
                ylObj = YLife.objects.get(yl_id=yl_id)
                ylObj.yl_title = title
                ylObj.yl_author = author
                ylObj.yl_date = date
                ylObj.yl_content = content
                ylObj.yl_flag = 0
                
                avatar = request.FILES.get("avatar", None)
                if avatar :
                    #small_pic = request.FILES['small_pic']
                    #BASE_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))
                    postfix = (avatar.name).split(".")[1].lower()
                    postfixList = ['jpg','jpeg','gif','bmp','png']
                    if not postfix in postfixList:
                        message = "请上传jpg,jpeg,gif,bmp,png类型的图片"
                        return commons.res_fail(1, message)
                    
                    path = settings.BASE_ROOT+"/media/youlin/life/"
                    if not os.path.exists(path):
                        os.mkdir(path, 0777)
                    file_name = time.strftime("%Y%m%d%H%M%S",time.localtime())+"_" + avatar.name
                    file_path = path+file_name
                    des_origin_f = open(file_path, "wb+")  
                    for chunk in avatar.chunks():
                        des_origin_f.write(chunk)
                    des_origin_f.close()
                    file_jump = "/media/youlin/life/" + file_name
                    image_del(settings.BASE_ROOT+ylObj.yl_avatar)
                
                    ylObj.yl_avatar = file_jump
                ylObj.save()
            except Exception, e:
                return commons.res_success("修改失败", res_data)
            res_data= "ok"
            return commons.res_success("修改成功", res_data)
    else:
        raise Http404()	
	
def ajax_life_list(request):
			#需要登录才可以访问
	#if not request.session.get("sess_admin", False):
	#	return commons.res_fail(1, "需要登录才可以访问")
	
	#分页索引和每页显示数
	page = 1
	if request.REQUEST.get("page"):
		page = int(request.REQUEST.get("page"))
	page_size = cfg.page_size
	if request.REQUEST.get("page_size"):
		page_size = int(request.REQUEST.get("page_size"))
	
	res_data = getlifesList(page, page_size)
	
	
	return HttpResponse(json.dumps(res_data), content_type="application/json")
	#return commons.res_success("请求成功", res_data)
		

#获取分页数据
def getlifesList(page, page_size):
	ylifes = YLife.objects.all()
	total = ylifes.count()
	page_count = commons.page_count(total, page_size)

	offset = (page - 1) * page_size
	limit = offset + page_size

	ylife_lists = YLife.objects.all().order_by("-yl_id")[offset:limit]
	data = []
	for i in ylife_lists:
		item = {}
		item['yl_title'] = i.yl_title
		item['yl_id'] = i.yl_id
		item['yl_author'] = i.yl_author
		item['yl_date'] = i.yl_date
		item['yl_content'] = i.yl_content
		item['yl_avatar'] = i.yl_avatar
		if i.yl_flag == 0:
			item['yl_flag'] = "否"
		else:
			item['yl_flag'] = "是"
		data.append(item)

	data = {
		"page_size": page_size,
		"page_count": page_count,
		"total": total,
		"page": page,
		"list": data,
	}
	return data 


@csrf_exempt
def ajax_upload_life(request):
	import sys
	reload(sys)
	sys.setdefaultencoding('utf8')
	upload = request.FILES['upload']
	file_root, file_ext = os.path.splitext(upload.name)
	f_ext = file_ext.encode("utf-8")
	postfixList = ['.jpg','.jpeg','.gif','.bmp','.png']
	if  f_ext not in postfixList:
 		message = "文件格式不正确,必须为jpg、gif、bmp、png、jpeg文件"
 		res = "<script>window.parent.CKEDITOR.tools.callFunction("+request.GET['CKEditorFuncNum']+",'','"+message+"');</script>"
 		return HttpResponse(res)
	destination_filename = get_available_name(os.path.join(settings.CKEDITOR_UPLOAD_PATH+"/life", upload.name))
	destination = open(destination_filename, 'wb+')
	for chunk in upload.chunks():
		destination.write(chunk)
	destination.close()
	#create_thumbnail(destination_filename)
	url = get_media_url(destination_filename)
	return HttpResponse("""
	<script type='text/javascript'>
	window.parent.CKEDITOR.tools.callFunction(%s, '%s');
	</script>""" % (request.GET['CKEditorFuncNum'], url))
    
       
def ajax_preview(request):
	title = request.POST.get('title')
	date = request.POST.get('date')
	author = request.POST.get('author')
	zw = request.POST.get('content')
	content = "<h1>"+title+"</h1><br>"+zw
	content = content.encode("utf-8")
	#avatar = request.FILES.get('avatar')
	#avatar = request.POST.get('avatar')
	res_data = {
		"title": title,
		"author": author,
		"date": date,
		"content":content,
		#"avatar":avatar,
	}
	
	return commons.render_template(request,"site/preview.html",res_data)

def ajax_life_del(request):
	if request.method == "GET":
		id = request.GET.get("id")
	try:
		ylObj = YLife.objects.get(yl_id =id)
		str = (ylObj.yl_avatar).encode("utf-8") 
		if str.strip():
			if str.find("head.jpg") == -1:
				path = settings.BASE_ROOT+ylObj.yl_avatar
				image_del(path)
		content_image_del(ylObj.yl_content)
		ylObj.delete()
		return commons.res_success("删除成功")
	except Exception, e:
		return commons.res_fail(1, "该数据不存在") 
	
def ajax_life_data(request):
		  #需要登录才可以访问
	#if not request.session.get("sess_admin", False):
	#	return commons.res_fail(1, "需要登录才可以访问")
	
	id = request.GET.get("id")
	try:
		ylObj = YLife.objects.get(yl_id =id)
	except:
		ylObj = None
		pass
	json_data = {
		"yl_id": ylObj.yl_id,
		"yl_author": ylObj.yl_author,
		"yl_date": ylObj.yl_date,
		"yl_title": ylObj.yl_title,
		"yl_avatar": ylObj.yl_avatar,
		"yl_content": ylObj.yl_content,

	}	
	return commons.res_success("请求成功", json_data)


def ajax_life_release(request):
	
	if request.method == 'GET':
		ids		 = request.GET.get('ids', None)
	if ids is not None:
		vIds = ids.split(",")
		try:
			ylifeList = YLife.objects.filter(yl_id__in=vIds)
			for ylife in ylifeList:
				ylife.yl_flag=1   #1：发布
				ylife.save()
			return commons.res_success("发布成功")
		except Exception, e:
			return commons.res_fail(1, e)
	return commons.res_fail(1, "请选择需要发布的内容!")