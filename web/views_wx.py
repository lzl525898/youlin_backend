
# coding:utf-8
from . import commons
from models import *
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse,StreamingHttpResponse
from django.http import HttpResponseRedirect
from users.models import User,Admin,BlackList,Signin,Remarks,Invitation
from community.models import  Topic,Media_files,Activity,SecondHand,EnrollActivity
import datetime
import os
import time

second_of_1minute = 60*1000
second_of_30minutes = 30* 60*1000
second_of_1hour =  60*60*1000
second_of_1day = 24*60*60*1000
second_of_15day = second_of_1day*15
second_of_30day = second_of_1day*30
second_of_6months = second_of_30day*6
second_of_1year = second_of_30day*12


def cityView(request):
	if request.method == 'GET':
		auth_id   = 	request.GET.get('auth_id')
	else:
		auth_id   = 	request.POST.get('auth_id')
 	auth_id = auth_id or None
	if auth_id is not None:
		request.session['auth_id'] = auth_id
		a=request.session.get("auth_id","")
	else:
		return commons.res_fail(1, "请检查微信服务是否正常!")
 	return commons.render_template(request, "weixin/city.html")

def communityView(request):
	city_id=request.session.get("city_id",False)
	city_name=request.session.get("city_name",False)
	if city_id==False or city_name==False:
		return HttpResponseRedirect("/yl/wx/cv/")
	
	community_lists = Community.objects.filter(city_id=city_id)
 	community_list_json = []
#测试专用
#  	for community in community_lists:   
#  		 item={}
#  		 item['city_name']=city_name
#  		 item['com_id']=community.community_id
#  		 item['com_name']=community.community_name
#  		 community_list_json.append(item)
#3为测试小区1   4为测试小区2
 	for community in community_lists:   
 		 item={}
 		 community_id=community.community_id
 		 if int(community_id) == 3 or int(community_id) == 4:
 		 	continue
 		 item['com_id']=community_id
 		 item['city_name']=city_name
 		 item['com_name']=community.community_name
 		 community_list_json.append(item)
 	res_data={
			"city_name":city_name,
			"city_id":city_id,
			"reason":"",
 			"com_list":community_list_json,
			}
	return commons.render_template(request, "weixin/community.html",res_data)

#查找小区
def search(request):
	if request.method == 'GET':
		city_id      						= 	request.GET.get('city_id',None).encode("utf-8")
		searchContent			=	request.GET.get('search',None).encode("utf-8")
		city									=	City.objects.get(city_id=city_id)
		try:
			com_list=Community.objects .filter(community_name__contains=searchContent).filter(city_id=city_id)
			len=com_list.count()
			if len==0:
				return commons.res_fail(1, "未找到对应小区，请检查小区名称后重新搜索")
			else:
				com_list_json=[]
				for community in com_list: 
					item={}
					item['city_id']=city_id
					item['com_id']=community.community_id
					item['com_name']=community.community_name
					com_list_json.append(item)	
				res_data={
						"city_id":city_id,
						"city_name":city.city_name.encode("utf-8"),
						"reason":"",
			 			"com_list":com_list_json,
						}
				return commons.res_success("查询结果",res_data) 
		except:
			return commons.res_fail(1, "服务器繁忙，请返回上一级重新查询")
		
@csrf_exempt 
def neighbor(request):
	user_community_id = request.session.get("user_community_id","")
	try:
	    targetObj = Community.objects.filter(community_id = user_community_id)
	except Exception, e:
		print e
	if  targetObj is not None:
		community_name = targetObj[0].community_name  		
	topList2 = []	
	try:
	    topiclist = Topic.objects.filter(sender_community_id = user_community_id).order_by('-topic_id')[:6]
	except Exception, e:
		print e
  
	for topicObj in topiclist:	  
	   try:
	        medialist = Media_files.objects.filter(topic = topicObj.topic_id,comment_id = 0)
	   except Exception, e:
		    print e
	   if topicObj.comment_num is None:
	   	   topicObj.comment_num = "评论"
	   if topicObj.like_num is None:
	   	   topicObj.like_num = "赞"
	   if topicObj.view_num is None:
	   	   topicObj.view_num = "0"
	   timeStamp = int(topicObj.topic_time/1000) 
	   timespan = sendTime(timeStamp)
	   if topicObj.topic_category_type == 2 and topicObj.object_data_id == 1:
       	    activity = Activity.objects.get(topic = topicObj.topic_id)
	   dicts = {}
	   dicts.setdefault('topicObj', topicObj)
	   dicts.setdefault('medialist', medialist)
	   dicts.setdefault('timespan', timespan)
	   topList2.append(dicts)
 	   category  = "全部"
 	res_data={
 			"bool":request.session.get("bool",""),
 			"user_nick":request.session.get("user_nick",""),
 			"topList2":topList2,	
 			"community_name":community_name,
 			"category":category,		
 			
 			}
	return commons.render_template(request, "weixin/neighbor.html",res_data)
   # return commons.render_template(request, "weixin/neighbor.html")

def personal(request):
	res_data={	
			"user_portrait":request.session.get("user_portrait",""),		
 			"user_nick":request.session.get("user_nick",""),
 			"user_birthday":request.session.get("user_birthday",""),	
 			"user_gender":request.session.get("user_gender",""),
 			"user_profession":request.session.get("user_profession",""),		
 			}
	
	return commons.render_template(request, "weixin/personal.html",res_data)
	#return commons.render_template(request, "weixin/personal.html")

def unbind(request):
	
	return commons.render_template(request, "weixin/unbind.html")

def loginBind(request):
  
   return commons.render_template(request, "weixin/bind.html")

def registerDl(request):
	
	return commons.render_template(request, "weixin/dl.html")

def longToInt(value):
	 if value > 2147483647 :
	  return (value & (2 ** 31 - 1))
	 else :
	  return value
@csrf_exempt 
def AuthorBind(request):
    if request.method == 'POST':
        username = request.POST.get('yl-username',None)
        password = request.POST.get('yl-password',None)
    else:
        username = request.GET.get('yl-username',None)
        password = request.GET.get('yl-password',None)       
    try:
      	targetObj = User.objects.filter(user_phone_number=username)
    except Exception, e:
    	print e
    if  targetObj:
        from web.views_admin import generatePassword
        password = generatePassword(password,username)
        if (targetObj[0].user_password == password):
         	 request.session['bool'] = 0
         	 request.session['user_nick'] =  targetObj[0].user_nick
         	 request.session['user_birthday'] =  targetObj[0].user_birthday
         	 request.session['user_profession'] =  targetObj[0].user_profession
         	 request.session['user_community_id'] =  targetObj[0].user_community_id
         	 request.session['user_id'] =  targetObj[0].user_id
         	 auth_id = request.session.get("auth_id","")
           	 targetObj[0].auth_id = auth_id
           	 targetObj[0].save()
         
         	 str = targetObj[0].user_portrait
#          	 #path =  str[24:]
          	 path =  str.split("123.57.9.62")[-1]
         	 request.session['user_portrait'] = path
         	 if  targetObj[0].user_gender == 1:
         	 	request.session['user_gender'] =  "男"
         	 elif targetObj[0].user_gender == 2:
         	 	request.session['user_gender'] =  "女"
         	 else:
         	 	request.session['user_gender'] =  "保密"
         	 str = "/yl/wx/categType?type = 0&community_id ="+unicode(targetObj[0].user_community_id).encode("utf-8")
         	 #return HttpResponseRedirect(str)
         	 res_data={
 			"url":str,
 			"bool":1,
 			 "message":auth_id,		
 			
 			}
         	 return commons.res_success("验证通过",res_data) 
        else:
        	 res_data={
 			   "bool":1,
 			   "message":"密码错误",		
 			      }
        	 return commons.render_template(request, "weixin/bind.html",res_data)
    else :
     	res_data={
 			"bool":1,
 			"message":"用户不存在",	
 			
 			}
     	return commons.render_template(request, "weixin/bind.html",res_data)
            	 
    return commons.res_success("验证通过") 
   
  #签到界面返回 
def goback(request):
   	 auth_id = request.session.get("auth_id","")
   	 targetObj = User.objects.filter(auth_id=auth_id)
   	 str = "/yl/wx/categType?type = 0&community_id ="+unicode(targetObj[0].user_community_id).encode("utf-8")
   	 return HttpResponseRedirect(str)
   	
   
 
   
@csrf_exempt 
def categType(request):
	type  = request.GET.get('type ',None)   
	#user_community_id  = request.GET.get('community_id ',None)
	
	user_community_id  = request.GET.get('community_id ',None)
	try:
	    targetObj = Community.objects.filter(community_id = user_community_id)
	except Exception, e:
		print e
	if  targetObj is not None:
		community_name = targetObj[0].community_name  		
		topList2 = []	
		try:
	          if int(type) == 0:
	                topiclist = Topic.objects.filter(sender_community_id = user_community_id).order_by('-topic_id')[:6]
	                category  = "全部"
	          elif int(type)  == 1:
	  	             topiclist = Topic.objects.filter(sender_community_id = user_community_id,topic_category_type = 2,object_data_id = 0).order_by('-topic_id')[:6] #3新闻
	  	             category  = "话题"
	          elif int(type)  == 2:
	  	             topiclist = Topic.objects.filter(sender_community_id = user_community_id,topic_category_type = 2,object_data_id=1).order_by('-topic_id')[:6]
	  	             category  = "活动"
	          elif int(type)  == 3:
	  	             topiclist = Topic.objects.filter(sender_community_id = user_community_id,topic_category_type = type).order_by('-topic_id')[:6]
	  	             category  = "公告"
	          elif int(type)  == 4:
	  	             topiclist = Topic.objects.filter(sender_community_id = user_community_id,topic_category_type = 2,object_data_id=4).order_by('-topic_id')[:6]
	  	             category  = "闲品会"
	          elif int(type)  == 5:
	  	             topiclist = Topic.objects.filter(sender_community_id = user_community_id,topic_category_type = type).order_by('-topic_id')[:6]
	  	             category  = "建议"	  	
	  	except Exception, e:
		       print e

        for topicObj in topiclist:	        
			       outtimetag = 0
			       activitytag = 0
			       SecondHandtag = 0
			       activitymessage =""
			       applynum = 0
			       secondlabel = ""
			       secondprice = ""
			       lists = []
			       try:
			            medialists = Media_files.objects.filter(topic = topicObj.topic_id)
			       except Exception, e:
				        print e
			       i = 97
			       for medialist in medialists:
				   	if (i > 99):
				   	    i = 97
				   	var = "ui-block-"+chr(i)
				   	i += 1
				   	str = medialist.resPath
				   	path =  str.split("123.57.9.62")[-1]
				   	lists.append((var,str))
			       if topicObj.comment_num is None:
			   	        topicObj.comment_num = "评论"
			       if topicObj.like_num is None:
			   	        topicObj.like_num = "赞"
			       if topicObj.view_num is None:
			   	        topicObj.view_num = "0"
			       timeStamp = int(topicObj.topic_time/1000) 
			       timespan = sendTime(timeStamp)
			       if topicObj.topic_category_type == 2 and topicObj.object_data_id == 1:#活动
			       		    activitytag = 1
			       		    activity = Activity.objects.get(topic = topicObj.topic_id)
			       		    activity_id = activity.activity_id
			       		    try:
			       		        enrollactivity = EnrollActivity.objects.get(activity_id = activity.activity_id)
			       		    except Exception, e:
				                print e
				                enrollactivity = None
			       		    if  enrollactivity is not None:
			       		    		applynum = enrollactivity.enrollUserCount
			       		    else:
			       		    	    applynum = 0
			       		    if  int(long(activity.endTime)/1000) < int(time.time()) :
				        	        	       outtimetag = 1
			       		    user_id = request.session.get("user_id","")
			       		    if  topicObj.sender_id ==  user_id:
			       		    	activitymessage = "报名详情"
			       		    else:
					        	activitymessage = "我要报名"
					       
			       if topicObj.topic_category_type == 2 and topicObj.object_data_id == 4:#闲品会
					       	SecondHandtag = 1
					       	secondhand = SecondHand.objects.get(topic = topicObj.topic_id)
					       	secondprice ="￥"+(secondhand.price).encode("utf-8") 
					       	print 	secondhand.oldornew				       	
					       	if secondhand.oldornew == 0:
					       		secondlabel = "全新"
					       	elif secondhand.oldornew == 1:
					       		secondlabel = "九成新"
					        elif secondhand.oldornew == 2:
					        	secondlabel = "八成新"
					        elif secondhand.oldornew == 3:
					        	secondlabel = "七成新"
					        elif secondhand.oldornew == 4:
					        	secondlabel = "六成新"
					        elif secondhand.oldornew == 5:
					        	secondlabel = "五成新"
					        elif secondhand.oldornew == 6:
					        	secondlabel = "五成新以下"
				
                  
			       dicts = {}
			       print  secondlabel
			       dicts.setdefault('topicObj', topicObj)
			       dicts.setdefault('medialist', lists)
			       dicts.setdefault('timespan', timespan)
			       dicts.setdefault('outtimetag', outtimetag)
			       dicts.setdefault('activitytag', activitytag)
			       dicts.setdefault('activitymessage', activitymessage)
			       dicts.setdefault('SecondHandtag', SecondHandtag)
			       dicts.setdefault('applynum', applynum)
			       dicts.setdefault('secondlabel', secondlabel)
			       dicts.setdefault('secondprice', secondprice)
			       topList2.append(dicts)
 	res_data={
 			    "bool":request.session.get("bool",""),
 			     "user_nick":request.session.get("user_nick",""),
 			     "topList2":topList2,	
 			     "community_name":community_name,
 			     "community_id":user_community_id,
 			     "category":category,		
 			}
 	return commons.render_template(request, "weixin/neighbor.html",res_data)
	
   
def sendTime(timeStamp):
    nowtime = int(time.time())
    difftime  = int( (nowtime - timeStamp)*1000)
    if difftime < second_of_1minute:
  	   	timespan = "刚刚"
    elif difftime < second_of_30minutes:
  	   	timespan = str(difftime/second_of_1minute)+"分钟前"
    elif difftime < second_of_1hour:	
  	   	timespan = "半小时前"
    elif difftime < second_of_1day:
  	   	timespan = str(difftime/second_of_1hour)+"小时前"
    elif difftime < second_of_15day:
  	   	timespan =str(difftime/second_of_1day)+"天前"
    elif difftime < second_of_30day:
  	   	timespan = "半个月前"
    elif difftime < second_of_6months:
  	   	timespan = str(difftime /second_of_30day)+"月前"
    elif difftime < second_of_1year:
  	   	timespan = "半年前"
    elif difftime >=  second_of_1year:
  	   	timespan = str(difftime/second_of_1year) +"半年前"
    return timespan    
#选定城市中的优邻小区
def verify_city(request):
	if request.method == 'POST':
		city_id				= int(request.POST.get("city_id"))
		city_name		=request.POST.get('city_name',None)
	else:
		city_id				= int(request.GET.get("city_id"))
		city_name		=request.GET.get('city_name',None)
	try:
		community_lists = Community.objects.filter(city_id=city_id)	
		len=community_lists.count()
		if len==0:
			request.session['city_name'] = ""
			request.session['city_id'] = ""
			return commons.res_fail(1, "该城市优邻小区正在加入，请耐心等待")
		else:
			request.session['city_name'] = city_name
			request.session['city_id'] = city_id
			res_data={
					"city_name":city_name,
					"city_id":city_id,
					}
			return commons.res_success("优邻小区已入住此城市",res_data) 
	except:
		request.session['city_name'] = ""
		request.session['city_id'] = ""
		return commons.res_fail(1, "服务器繁忙，请刷新")

#显示城市
def ajax_wxcity_data(request):
    city_lists = City.objects.filter()
    city_list_json = []
    for city in city_lists:        
        item={}
        item['text']=city.city_id
        item['label']=city.city_name
        item['firsit_letter']   =multi_get_letter(city.city_name )
        city_list_json.append(item)    
    li=[]
    li=city_list_json
    newlist = sorted(li, key=lambda k: k['firsit_letter'])    
    alist=[];		blist=[];		clist=[];		dlist=[];		elist=[];
    flist=[];		glist=[];		hlist=[];		ilist=[];		jlist=[];
    klist=[];		llist=[];		mlist=[];		nlist=[];		olist=[];
    plist=[];		qlist=[];		rlist=[];		slist=[];		tlist=[];
    ulist=[];		vlist=[];		wlist=[];		xlist=[];		ylist=[];		zlist=[];
    for n_list in newlist:
    	if n_list['firsit_letter'][0]=='a':
     		alist.append(n_list)
     	elif n_list['firsit_letter'][0]=='b':
     		blist.append(n_list)	
     	elif n_list['firsit_letter'][0]=='c':
     		clist.append(n_list)
     	elif n_list['firsit_letter'][0]=='d':
     		dlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='e':
     		elist.append(n_list)
     	elif n_list['firsit_letter'][0]=='f':
     		flist.append(n_list)
     	elif n_list['firsit_letter'][0]=='g':
     		glist.append(n_list)
     	elif n_list['firsit_letter'][0]=='h':
     		hlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='i':
     		ilist.append(n_list)
     	elif n_list['firsit_letter'][0]=='j':
     		jlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='k':
     		klist.append(n_list)
     	elif n_list['firsit_letter'][0]=='l':
     		llist.append(n_list)
     	elif n_list['firsit_letter'][0]=='m':
     		mlist.append(n_list)
    	elif n_list['firsit_letter'][0]=='n':
    		nlist.append(n_list)
    	elif n_list['firsit_letter'][0]=='o':
     		olist.append(n_list)
     	elif n_list['firsit_letter'][0]=='p':
     		plist.append(n_list)
     	elif n_list['firsit_letter'][0]=='q':
     		qlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='r':
     		rlist.append(n_list)
    	elif n_list['firsit_letter'][0]=='s':
     		slist.append(n_list)
     	elif n_list['firsit_letter'][0]=='t':
     		tlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='u':
     		ulist.append(n_list)
     	elif n_list['firsit_letter'][0]=='v':
     		vlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='w':
     		wlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='x':
     		xlist.append(n_list)
     	elif n_list['firsit_letter'][0]=='y':
     		ylist.append(n_list)
     	elif n_list['firsit_letter'][0]=='z':
     		zlist.append(n_list)
    res_data={
			'a_list':alist,'b_list':blist,'c_list':clist,'d_list':dlist,
			'e_list':elist,'f_list':flist,'g_list':glist,'h_list':hlist,
			'i_list':ilist,'j_list':jlist,'k_list':klist,'l_list':llist,
			'm_list':mlist,'n_list':nlist,'o_list':olist,'p_list':plist,
			'q_list':qlist,'r_list':rlist,
			's_list':slist,'t_list':tlist,'u_list':ulist,'v_list':vlist,
			'w_list':wlist,'x_list':xlist,'y_list':ylist,'z_list':zlist,
			}
    return commons.res_success("获取城市成功。",res_data)

   
   
  #拼音首字母 
def multi_get_letter(str_input): 

    if isinstance(str_input, unicode): 
        unicode_str = str_input 
    else: 
        try: 
            unicode_str = str_input.decode('utf8') 
        except: 
            try: 
                unicode_str = str_input.decode('gbk') 
            except: 
                print 'unknown coding' 
                return 

    return_list = [] 
    for one_unicode in unicode_str: 
        return_list.append(single_get_first(one_unicode)) 
    return return_list 
  #拼音首字母 
def single_get_first(unicode1): 
    str1 = unicode1.encode('gbk') 
    try:         
        ord(str1) 
        return str1 
    except: 
        asc = ord(str1[0]) * 256 + ord(str1[1]) - 65536 
        if asc >= -20319 and asc <= -20284: 
            return 'a' 
        if asc >= -20283 and asc <= -19776: 
            return 'b' 
        if asc >= -19775 and asc <= -19219: 
            return 'c' 
        if asc >= -19218 and asc <= -18711: 
            return 'd' 
        if asc >= -18710 and asc <= -18527: 
            return 'e' 
        if asc >= -18526 and asc <= -18240: 
            return 'f' 
        if asc >= -18239 and asc <= -17923: 
            return 'g' 
        if asc >= -17922 and asc <= -17418: 
            return 'h' 
        if asc >= -17417 and asc <= -16475: 
            return 'j' 
        if asc >= -16474 and asc <= -16213: 
            return 'k' 
        if asc >= -16212 and asc <= -15641: 
            return 'l' 
        if asc >= -15640 and asc <= -15166: 
            return 'm' 
        if asc >= -15165 and asc <= -14923: 
            return 'n' 
        if asc >= -14922 and asc <= -14915: 
            return 'o' 
        if asc >= -14914 and asc <= -14631: 
            return 'p' 
        if asc >= -14630 and asc <= -14150: 
            return 'q' 
        if asc >= -14149 and asc <= -14091: 
            return 'r' 
        if asc >= -14090 and asc <= -13119: 
            return 's' 
        if asc >= -13118 and asc <= -12839: 
            return 't' 
        if asc >= -12838 and asc <= -12557: 
            return 'w' 
        if asc >= -12556 and asc <= -11848: 
            return 'x' 
        if asc >= -11847 and asc <= -11056: 
            return 'y' 
        if asc >= -11055 and asc <= -10247: 
            return 'z' 
        return '错误' 
       
       
       
       
#签到
def usersign(request):
	if request.method == 'GET':
		auth_id   = 	request.GET.get('auth_id')
	else:
		auth_id   = 	request.POST.get('auth_id')
	auth_id1	=	request.session.get("auth_id","")
	auth_id		=auth_id or auth_id1
	auth_id		=auth_id or None
	if auth_id is not None:
		request.session['auth_id'] = auth_id
	else:
		return commons.res_fail(1, "请检查微信服务是否正常!")
	auth_id				=	auth_id.encode("utf-8")
	user_id			=	int(14)
	curTimestamp = time.time()
	curTime = time.localtime(curTimestamp)
	curYear = int(curTime[0])
	curMon  = int(curTime[1])
	curDay  = int(curTime[2])
	
	try:
		userObj				= User.objects.get(auth_id = auth_id)
		user_id				=userObj.user_id
		userCredit 		= userObj.user_credit#用户积分
		userExp			=	userObj.user_exp#用户经验
		print"用户数将获取成功"
	except:
		res_data={
				"reason":"用户未绑定",
				}
		return HttpResponseRedirect("/yl/wx/bind/")
	try:
		signinObj = Signin.objects.filter(year=curYear,month=curMon,day=curDay,user_id = long(user_id))
		size = signinObj.count()
		if size ==0:
			signinObj = None
		else:
			signinObj = Signin.objects.filter(year=curYear,month=curMon,user_id = long(user_id))
			sign_title	=	Signin.objects.filter(user_id = long(user_id)).count()#签到总数
			sign_month_title	=	signinObj.count()#本月签到数
			sign_list_json =[]
			for User_sign in signinObj:
				item={}
				item['signDay']=int(User_sign.day)
				sign_list_json.append(item)
			res_data={
 					"reason":"用户已签到",
					"userCredit":userCredit,
					"userExp":userExp,
					"user_sign_title":sign_title,
					"user_month_title":sign_month_title,
					"sign_list":sign_list_json
					}
			return commons.render_template(request, "weixin/wxsign2.html",res_data)
	except:
		signinObj = None	
	if signinObj==None:
			print"用户未签到"
			try:
				Signin.objects.create(year=curYear,month=curMon,day=curDay,timestamp=long(curTimestamp),user_id = long(user_id))
				reason="签到成功"
				userObj.user_exp = userExp + 3 #签到给3经验值
				userObj.user_credit = userCredit + 3 #签到给3积分
				userObj.save()
			except:
				reason="今日签到失败，请返回上一级重新签到"
			
			signinObj = Signin.objects.filter(year=curYear,month=curMon,user_id = long(user_id))
			sign_title	=	Signin.objects.filter(user_id = long(user_id)).count()
			sign_month_title	=	signinObj.count()
			
			sign_list_json =[]
			for User_sign in signinObj:
				item={}
				item['signDay']=int(User_sign.day)
				sign_list_json.append(item)
			res_data={
					"reason":reason,
					"userCredit":userObj.user_credit,
					"userExp":userObj.user_exp,
					"user_sign_title":sign_title,
					"user_month_title":sign_month_title,
					"sign_list":sign_list_json
					}
 	return commons.render_template(request, "weixin/wxsign2.html",res_data)

