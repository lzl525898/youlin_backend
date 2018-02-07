# coding:utf-8
from django.conf.urls import url

from web import views

urlpatterns = [
    #测试ajax
    url(r'^web/testajax$', 'web.views_admin.testajax'),
    #订单支付
    url(r'^web/youlinPay$', 'web.views_admin.youlinPay'),
    #订单提交
    url(r'^web/submitOrder$', 'web.views_admin.submitOrder'),
    #物品列表详情
    url(r'^web/goodsDetail$', 'web.views_admin.goodsDetail'),
    #物品列表详情
    url(r'^web/goodsDetail$', 'web.views_admin.goodsDetail'),
    #物品列表
    url(r'^web/listGoods$', 'web.views_admin.listGoods'),
    #地址创建
    url(r'^web/addressCreate$', 'web.views_admin.addressCreate'),
    #地址
    url(r'^web/address$', 'web.views_admin.address'),
    #报名
    url(r'^web/signUp$', 'web.views_admin.signUp'),
    #广场
    url(r'^web/mySquare$', 'web.views_admin.mySquare'),
    #培训
    url(r'^web/myTraining$', 'web.views_admin.myTraining'),
    #培训详情
    url(r'^web/myTrainDetail$', 'web.views_admin.myTrainDetail'),
    #旧物置换列表页
    url(r'^web/replacelist$', 'web.views_admin.ReplacementList'),
    #列表详情页
    url(r'^web/replacelistDetail$', 'web.views_admin.circleDetail'),
    #买家列表
    url(r'^web/wantPersonList$', 'web.views_admin.wantPersonList'),
    #我发布的
    url(r'^web/myPush$', 'web.views_admin.myPush'),
    #搜索
    url(r'^web/mySearch$', 'web.views_admin.mySearch'),
    ####################################################
    url(r'^web/guaguale$', 'web.views_admin.guaguale'),
    #宝箱弹出页
    url(r'^web/baoxiang$', 'web.views_admin.baoxiang'),
    #积分说明
    url(r'^web/integralinfo$', 'web.views_admin.IntegralInfo'),
    #移动支付
    url(r'^web/pay$', 'web.views_admin.DevicePay'),
    
    url(r'^pushView/$', views.pushView, name='pushView'),
    #后台页面部分
    url(r'^web/index$', 'web.views_admin.index'),
    url(r'^web/admin$', 'web.views_admin.admin'),
    url(r'^web/user_login$', 'web.views_admin.user_login'),
    url(r'^web/user_logout$', 'web.views_admin.user_logout'),
    #session过期
    url(r'^web/ajax_Session_term$', 'web.views_admin.ajax_Session_term'),
    #验证码
    url(r'^web/get_code$', 'web.views_admin.get_code'),

    #后台请求数据部分
    url(r'^web/ajax_login$', 'web.views_admin.ajax_login'),
    url(r'^web/ajax_logout$', 'web.views_admin.ajax_logout'),
    url(r'^web/ajax_menu_list$', 'web.views_admin.ajax_menu_list'),
    url(r'^web/ajax_admin_list$', 'web.views_admin.ajax_admin_list'),
    url(r'^web/ajax_admin_add$', 'web.views_admin.ajax_admin_add'),
    url(r'^web/ajax_admin_del$', 'web.views_admin.ajax_admin_del'),
    url(r'^web/ajax_admin_updatepwd$', 'web.views_admin.ajax_admin_updatepwd'),    
   
    url(r'^web/ajax_fr_data$', 'web.views_admin.ajax_fr_data'),
    url(r'^web/ajax_city_data', 'web.views_admin.ajax_city_data'),
    url(r'^web/ajax_community_data', 'web.views_admin.ajax_community_data'),
    url(r'^web/ajax_user_data', 'web.views_admin.ajax_user_data'),
    url(r'^web/ajax_audit_submit', 'web.views_admin.ajax_audit_submit'),
    url(r'^web/ajax_audit_list', 'web.views_admin.ajax_audit_list'),
    url(r'^web/ajax_address_list', 'web.views_admin.ajax_address_list'),
    url(r'^web/ajax_apt_data', 'web.views_admin.ajax_apt_data'),
    url(r'^web/ajax_address_audit_submit', 'web.views_admin.ajax_address_audit_submit'),
    url(r'^web/ajax_common_list', 'web.views_admin.ajax_common_list'),
    url(r'^web/ajax_admin_data', 'web.views_admin.ajax_admin_data'),
    url(r'^web/ajax_common_submit', 'web.views_admin.ajax_common_submit'),
    
    url(r'^web/ajax_upload$', 'web.views_admin.ajax_image_upload'),
    url(r'^web/ajax_new_submit', 'web.views_admin.ajax_new_submit'),
    url(r'^web/ajax_news_list', 'web.views_admin.ajax_news_list'),
    url(r'^web/getNews/$', 'web.views_admin.ajax_getNewsById'),
    url(r'^web/new_del/$', 'web.views_admin.ajax_new_del'),
    url(r'^web/ajax_push_new/$', 'web.views_admin.ajax_push_new'),
    
    url(r'^web/ajax_new_data/$', 'web.views_admin.ajax_new_data'),
#     url(r'^web/ajax_new_mod', 'web.views_admin.ajax_new_mod'),
    
    url(r'^web/ajax_feedback_list', 'web.views_admin.ajax_feedback_list'),
    url(r'^web/ajax_property_list', 'web.views_admin.ajax_property_list'),
    url(r'^web/ajax_property_submit', 'web.views_admin.ajax_property_submit'),
    url(r'^web/ajax_property_del', 'web.views_admin.ajax_property_del'),
    url(r'^web/ajax_getPropertyInfoById', 'web.views_admin.ajax_getPropertyInfoById'),
    
    
    url(r'^web/ajax_version_list', 'web.views_admin.ajax_version_list'),
    url(r'^web/ajax_version_submit', 'web.views_admin.ajax_version_submit'),
    url(r'^web/ajax_version_del', 'web.views_admin.ajax_version_del'),
    url(r'^web/ajax_getVersionById', 'web.views_admin.ajax_getVersionById'),
    
    url(r'^web/ajax_gift_list', 'web.views_admin.ajax_gift_list'),
    url(r'^web/ajax_gift_submit/$', 'web.views_admin.ajax_gift_submit'),
    url(r'^web/ajax_community_list/$', 'web.views_admin.ajax_community_list'),
    url(r'^web/ajax_gift_del/$', 'web.views_admin.ajax_gift_del'),
    url(r'^web/ajax_getGiftById/$', 'web.views_admin.ajax_getGiftById'),
    url(r'^web/ajax_gift_release/$', 'web.views_admin.ajax_gift_release'),
    url(r'^web/ajax_gift_down/$', 'web.views_admin.ajax_gift_down'),
    
    
    url(r'^web/ajax_exchange_list/$', 'web.views_admin.ajax_exchange_list'),
    url(r'^web/ajax_exchange_status/$', 'web.views_admin.ajax_exchange_status'),
    url(r'^web/ajax_export_submit/$', 'web.views_admin.ajax_export_submit'),

    
    url(r'^web/del_Subscription/$', 'web.views_admin.del_Subscription'),
    url(r'^web/echo_Subscription/$', 'web.views_admin.echo_Subscription'),
    url(r'^web/ajax_subscription_list/$', 'web.views_admin.ajax_subscription_list'),
    url(r'^web/ajax_subscription_submit/$', 'web.views_admin.ajax_subscription_submit'),
    
    url(r'^web/ajax_role_list/$', 'web.views_admin.ajax_role_list'),
    url(r'^web/ajax_role_submit/$', 'web.views_admin.ajax_role_submit'),
    url(r'^web/echo_Role/$', 'web.views_admin.echo_Role'),
    url(r'^web/del_Role/$', 'web.views_admin.del_Role'),
    url(r'^web/ajax_role_data/$', 'web.views_admin.ajax_role_data'),
    
    
    url(r'^web/ajax_webUser_submit/$', 'web.views_admin.ajax_webUser_submit'),
    url(r'^web/ajax_webUser_list/$', 'web.views_admin.ajax_webUser_list'),
    url(r'^web/del_webUser/$', 'web.views_admin.del_webUser'),
    url(r'^web/echo_webUser/$', 'web.views_admin.echo_webUser'),
    #前台
    url(r'^$', 'web.views_site.index'),#首页
    url(r'^dl/$', 'web.views_site.download'),#下载页
    url(r'^yllife/$', 'web.views_site.yllife'),#友邻生活
    url(r'^content/$', 'web.views_site.content'),#优邻生活详细内容
    url(r'^contact/$', 'web.views_site.contact'),#优邻生活详细内容
    url(r'^privacy_clause/$', 'web.views_site.privacy_clause'),#隐私条款 
    
  
    url(r'^wx/cv/$', 'web.views_wx.cityView'),#加载选择城市
    url(r'^wx/sc/$', 'web.views_wx.communityView',name="test"),#选择小区
    url(r'^wx/search/$', 'web.views_wx.search'),#搜索小区
    url(r'^wx/neighbor/$', 'web.views_wx.neighbor'),#邻居圈
    url(r'^wx/personal/$', 'web.views_wx.personal'),#个人信息
    url(r'^wx/dl/$', 'web.views_wx.registerDl'),#没有优邻账号，加载下载页
    url(r'^wx/bind/$', 'web.views_wx.loginBind'),#登录绑定微信帐号
    url(r'^wx/unbind/$', 'web.views_wx.unbind'),#登录解除绑定
    url(r'^wx/categType/$', 'web.views_wx.categType'),
    url(r'^wx/goback$', 'web.views_wx.goback'),#签到界面返回上一级
    
    url(r'^wx/authorbind', 'web.views_wx.AuthorBind'),#登录绑定接口
    
    
    url(r'^wechat1/', 'web.views_wechat.wechat_home'),#微信后台
    url(r'^wechat2/', 'web.views_wx_test.wechat_home1'),#微信后台test

    url(r'^wx/cv/verify_city$', 'web.views_wx.verify_city'),#验证城市
    url(r'^wx/cv/ajax_wxcity_data/$', 'web.views_wx.ajax_wxcity_data'),    #wechat 显示城市
    url(r'^wx/sign/$', 'web.views_wx.usersign'),#签到界面
    
    
    
    #登录验证
    url(r'^web/Verify_userLogin/$', 'web.views_admin.Verify_userLogin'),
    url(r'^web/verify_user/$', 'web.views_admin.verify_user'),
    #更换密码
    url(r'^web/ajax_Psd_change$', 'web.views_admin.ajax_Psd_change'),
    url(r'^web/ajax_person_data$', 'web.views_admin.ajax_person_data'),
    url(r'^web/ajax_person_update$', 'web.views_admin.ajax_person_update'),
    #数据统计
    url(r'^web/ajax_Data_Statistics$', 'web.views_admin.ajax_Data_Statistics'),
    
    #优邻生活
    url(r'^web/ajax_life_submit', 'web.views_admin.ajax_life_submit'),
    url(r'^web/ajax_life_list/$', 'web.views_admin.ajax_life_list'),
    url(r'^web/ajax_preview', 'web.views_admin.ajax_preview'),
    url(r'^web/ajax_upload_life/$', 'web.views_admin.ajax_upload_life'),
    url(r'^web/ajax_life_del/$', 'web.views_admin.ajax_life_del'),
    url(r'^web/ajax_life_data/$', 'web.views_admin.ajax_life_data'),
    url(r'^web/ajax_life_release/$', 'web.views_admin.ajax_life_release'),
]
