# coding:utf-8
from django.db import models
from addrinfo.models import AddressDetails,City,Community,Block,BuildNum
import json
from web import commons

# Create your models here.

class GiftsList(models.Model):#宝物列表
    g_id          = models.AutoField(primary_key=True)
    g_name        = models.TextField(blank=True, null=True)
    g_img         = models.TextField(blank=True, null=True)
    g_count       = models.BigIntegerField(blank=True, null=True) #数量
    g_type        = models.IntegerField(default=1, editable=False)#宝物类别 1表示A 2表示B 3表示C 4表示D
    g_info        = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table="yl_giftslist" 
    def getInvId(self):
        return self.g_id

class Treasurebox(models.Model):#宝箱
    tb_id         = models.AutoField(primary_key=True)
    tb_comm_id    = models.BigIntegerField(blank=True, null=True, db_index=True)#分发小区id
    tb_status     = models.IntegerField(default=0, editable=False)#1表示开始分发 0表示不分发
    tb_start_time = models.BigIntegerField(blank=True, null=True) #开始时间
    tb_end_time   = models.BigIntegerField(blank=True, null=True) #结束时间
    tb_gift_list  = models.ForeignKey(GiftsList, related_name='GIFT_LSIT',\
                           blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table="yl_treasure" 
    def getInvId(self):
        return self.tb_id

class UserGiftsRecord(models.Model):#用户所得宝物记录
    ug_id         = models.AutoField(primary_key=True)
    ug_comm_id    = models.BigIntegerField(blank=True, null=True, db_index=True)#分发小区id
    ug_user_id    = models.BigIntegerField(blank=True, null=True, db_index=True)#分发用户id
    ug_type       = models.IntegerField(blank=True, null=True, db_index=True)#1表示A 2表示B 3表示C 4表示D
    ug_start_time = models.BigIntegerField(blank=True, null=True) #开始时间
    ug_end_time   = models.BigIntegerField(blank=True, null=True) #结束时间
    ug_name       = models.TextField(blank=True, null=True)
    ug_img        = models.TextField(blank=True, null=True)
    ug_count      = models.BigIntegerField(blank=True, null=True) #数量
    ug_status     = models.IntegerField(default=0, editable=False) #发送状态 0=》 否 1=》 是
    ug_year       = models.IntegerField(blank=True,null=True, db_index=True)
    ug_month      = models.IntegerField(blank=True,null=True, db_index=True)
    ug_day        = models.IntegerField(blank=True,null=True, db_index=True)
    
    class Meta:
        db_table="yl_usergiftsrecord" 
    def getInvId(self):
        return self.ug_id

class Invitation(models.Model):#邀请
    
    inv_id        = models.AutoField(primary_key=True)  
    inv_time      = models.BigIntegerField(blank=True, null=True) #邀请时间
    inv_phone     = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    inv_status    = models.IntegerField(blank=True, null=True)#1表示邀请中 2表示邀请完毕并注册 3表示超时邀请失败
    inv_type      = models.IntegerField(blank=True, null=True)#1表示邀请家人 2表示邀请朋友
    inv_code      = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    user_id       = models.BigIntegerField(blank=True, null=True, db_index=True)#发动邀请用户id
    inv_family_id = models.CharField(max_length=150, blank=True, null=True)#邀请用户的familyId
    
    class Meta:
        db_table="yl_invitation" 
    def getInvId(self):
        return self.inv_id

class Remarks(models.Model):#备注
    
    rem_id       = models.AutoField(primary_key=True)  
    tag_id       = models.IntegerField(blank=True, null=True, db_index=True)# 默认为1
    target_id    = models.BigIntegerField(blank=True, null=True, db_index=True)#目标用户id
    remuser_id   = models.BigIntegerField(blank=True, null=True, db_index=True)#已经备注的用户id
    user_remarks = models.CharField(max_length=50, blank=True, null=True, db_index=True)#备注信息
    
    class Meta:
        db_table="yl_remarks" 
    
    def getRemarksId(self):
        return self.rem_id

#游客guest
class Guest(models.Model):
    
    g_id             = models.AutoField(primary_key=True)   
    g_gender         = models.IntegerField(blank=True, null=True) # 1->male 2->female 3->secret      
    g_name           = models.TextField(blank=True, null=True)  
    g_portrait       = models.TextField(blank=True, null=True)
    g_note           = models.TextField(blank=True, null=True)
    g_phone          = models.CharField(max_length=50, blank=True, null=True)
    g_birthday       = models.BigIntegerField(blank=True, null=True) 
    g_email          = models.EmailField(blank=True, null=True, unique=True)
    g_chat           = models.TextField(blank=True, null=True)
    g_imei           = models.TextField(blank=True, null=True)
    g_profession     = models.TextField(blank=True, null=True)
    g_public_status  = models.IntegerField(blank=True, null=True) # 1->no addr no pro 2->ok addr no pro 3->no addr ok pro 4->ok addr ok pro
    g_news_receive   = models.IntegerField(blank=True, null=True) # 1-> 接收  非 1->不接收
    g_handle_cache   = models.IntegerField(blank=True, null=True) # 用户操作记录
    g_handle_cache   = models.IntegerField(blank=True, null=True) # 地址操作记录
    
    class Meta:
        db_table="yl_guest" 
    
    def getGuestId(self):
        return self.g_id

#第三方登录
class Third(models.Model):
    
    t_id           = models.AutoField(primary_key=True)
    t_nick         = models.TextField(blank=True, null=True)  
    t_portrait     = models.TextField(blank=True, null=True) #avatar
    t_gender       = models.IntegerField(blank=True, null=True) # 1->male 2->female 3->secret    
    t_phone_number = models.CharField(max_length=50, blank=True, null=True)
    t_email        = models.EmailField(blank=True, null=True, unique=True)
    t_birthday     = models.BigIntegerField(blank=True, null=True)
    t_imei         = models.TextField(blank=True, null=True)
    t_auth         = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table="yl_third" 
    
    def getThirdId(self):
        return self.t_id
    
class User(models.Model):
    
    user_id             = models.AutoField(primary_key=True)        
    user_nick           = models.TextField(blank=True, null=True)  
    user_password       = models.TextField(blank=True, null=True)
    user_portrait       = models.TextField(blank=True, null=True) #avatar
    user_gender         = models.IntegerField(blank=True, null=True) # 1->male 2->female 3->secret    
    user_phone_number   = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    user_family_id      = models.BigIntegerField(blank=True, null=True)  # current family_id
    user_community_id   = models.BigIntegerField(blank=True, null=True)  # current community_id
    user_family_address = models.TextField(blank=True, null=True)  # current family_address
    user_email          = models.EmailField(blank=True, null=True, unique=True)
    user_birthday       = models.BigIntegerField(blank=True, null=True) 
    user_public_status  = models.IntegerField(blank=True, null=True) # 1->no addr no pro 2->ok addr no pro 3->no addr ok pro 4->ok addr ok pro
    user_profession     = models.TextField(blank=True, null=True)
    user_level          = models.TextField(blank=True, null=True)
    user_signature      = models.TextField(blank=True, null=True)
    user_type           = models.IntegerField(blank=True, null=True) # 0->normal 1->admin
    user_push_user_id   = models.TextField(blank=True, null=True)
    user_push_channel_id= models.TextField(blank=True, null=True)
    user_news_receive   = models.IntegerField(blank=True, null=True) # 1-> 接收  非 1->不接收
    user_time           = models.BigIntegerField(blank=True, null=True)  
    user_json           = models.TextField(blank=True, null=True)
    user_exp            = models.BigIntegerField(blank=True, null=True)  #经验
    user_credit         = models.BigIntegerField(blank=True, null=True)  #积分
    user_handle_cache   = models.IntegerField(blank=True, null=True) # 用户操作记录
    addr_handle_cache   = models.IntegerField(blank=True, null=True) # 地址操作记录
    auth_id             = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table="yl_user" 
   
    def __str__(self):
        if self.user_nick is None:
            return 'null'
        else:
            return "[id:"+str(self.user_id)+"]"+self.user_nick.encode("utf8") + "[phone:"+self.user_phone_number.encode("utf8")+"]"

    def getPhoneNumber(self):
        return self.user_phone_number

    def getTargetUid(self):
        return self.user_id

    def getTargetPwd(self):
        return self.user_password

    def getTargetNick(self):
        return self.user_nick

    def getTargetSex(self):
        return self.user_gender

    def getTargetFamilyAddr(self):
        return self.user_family_address

    def getTargetFamilyId(self):
        return self.user_family_id
    
    def toJSON(self):
        return to_json(self)

class BlackList(models.Model):
    
    bl_id    = models.AutoField(primary_key=True)
    user_id  = models.BigIntegerField(db_index=True) #用户自己
    black_id = models.BigIntegerField(db_index=True) #黑名单用户
    
    class Meta:
        db_table="yl_blacklist"     
        
    def getBlackId(self):
        return self.bl_id
    
class Admin(models.Model):

    admin_id       = models.AutoField(primary_key=True)
    admin_type     = models.IntegerField(blank=True, null=True) # 1->property 2->building
    city           = models.ForeignKey(City, related_name='CITY_A', blank=True, null=True, on_delete=models.SET_NULL)
    community      = models.ForeignKey(Community, related_name='COMMUNITY_A', blank=True, null=True, on_delete=models.SET_NULL)
    block          = models.ForeignKey(Block, related_name='BLOCK_A', blank=True, null=True, on_delete=models.SET_NULL)
    buildnum       = models.ForeignKey(BuildNum, related_name='BUILDNUM_A', blank=True, null=True, on_delete=models.SET_NULL)
    user           = models.ForeignKey(User, related_name='USER_A', \
                     blank=True, null=True, on_delete=models.SET_NULL)
    app_time       = models.BigIntegerField(blank=True, null=True)  
    admin_info     = models.TextField(blank=True, null=True)
    class Meta:
        db_table="yl_admin"     
              
    def __str__(self):
        if self.admin_type is None:
            return 'null'
        else:
            if self.block is None:
                return "["+self.user.user_phone_number.encode("utf8")+"]"+\
                       "["+self.city.city_name.encode("utf8")+"]"+\
                       "["+self.community.community_name.encode("utf8")+"]"
            else:
                return "["+self.user.user_phone_number.encode("utf8")+"]"+\
                       "["+self.city.city_name.encode("utf8")+"]"+\
                       "["+self.community.community_name.encode("utf8")+"]"+\
                       "["+self.block.block_name.encode("utf8")+"]"
    def getAdminId(self):
        return self.admin_id
    
    def toJSON(self):
        return to_json(self)

class Signin(models.Model):
    
    _id       = models.AutoField(primary_key=True)
    year      = models.IntegerField(blank=True,null=True, db_index=True)
    month     = models.IntegerField(blank=True,null=True, db_index=True)
    day       = models.IntegerField(blank=True,null=True, db_index=True)
    timestamp = models.BigIntegerField(blank=True, null=True, db_index=True)
    user_id   = models.BigIntegerField(blank=True, null=True, db_index=True)

    class Meta:
        db_table="yl_signin"    
    
    def getSigninId(self):
        return self._id
        
class FamilyRecord(models.Model):

    fr_id                     = models.AutoField(primary_key=True)
    family_name               = models.TextField(blank=True,null=True)   
    family_display_name       = models.TextField(blank=True,null=True)
    family_address            = models.TextField(blank=True,null=True)  
    family_desc               = models.TextField(blank=True,null=True)
    family_portrait           = models.TextField(blank=True,null=True)
    family_background_color   = models.IntegerField(blank=True,null=True)
    family_city               = models.TextField(blank=True,null=True)
    family_city_id            = models.BigIntegerField(blank=True,null=True)
    family_block              = models.TextField(blank=True,null=True) 
    family_block_id           = models.BigIntegerField(blank=True,null=True)
    family_community_id       = models.BigIntegerField(blank=True,null=True)
    family_community          = models.TextField(blank=True,null=True) 
    family_community_nickname = models.TextField(blank=True,null=True) 
    family_building_num       = models.TextField(blank=True,null=True)
    family_building_num_id    = models.BigIntegerField(blank=True,null=True) 
    family_apt_num            = models.TextField(blank=True,null=True) 
    family_apt_num_id         = models.BigIntegerField(blank=True,null=True)
    is_family_member          = models.IntegerField(blank=True,null=True)
    is_attention              = models.IntegerField(blank=True,null=True)
    family_member_count       = models.IntegerField(blank=True,null=True)
    entity_type               = models.IntegerField(blank=True,null=True) # lllegal address 
    ne_status                 = models.IntegerField(blank=True,null=True) # lllegal address ID
    nem_status                = models.IntegerField(blank=True,null=True)
    primary_flag              = models.IntegerField(blank=True,null=True) # current address
    belong_family_id          = models.BigIntegerField(blank=True,null=True)
    user_alias                = models.TextField(blank=True,null=True) 
    user_avatar               = models.TextField(blank=True,null=True) 
    user                      = models.ForeignKey(User, related_name='USER', \
                                blank=True, null=True, on_delete=models.SET_NULL)
    family                    = models.ForeignKey(AddressDetails, related_name='ADDRESSDETAILS', \
                                blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table="yl_familyRecord"
    
    def __str__(self):
        if self.family_name is None:
            return 'null'
        else:
            return self.family_address.encode("utf8")
    
    def getFamilyRecordID(self):
        return self.fr_id
    
    def getTargetFamilyId(self):
        return self.family_id
    
    def getTargetCommunityId(self):
        return self.family_community_id    
    
    def toJSON(self):
        return to_json(self)
    
def to_json(obj):
    fields = []
    for field in obj._meta.fields:
        fields.append(field.name)
    d = {}
    for attr in fields:
        val = getattr(obj, attr)
        
        #如果是model类型，就要再一次执行model转json
        if isinstance(val, models.Model):
            val = json.loads(to_json(val))
        d[attr] = val
    return json.dumps(d)