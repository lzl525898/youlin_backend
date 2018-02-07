# coding:utf-8
from django.db import models
    
class City(models.Model):
    city_id   = models.AutoField(primary_key=True)
    city_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    city_name = models.CharField(max_length=100, blank=True, null=True, unique=True)
 
    class Meta:
        db_table="yl_city"

    def __str__(self):
        if self.city_name is None:
            return 'null'
        else:
            return "["+ str(self.city_code) + "]" + self.city_name.encode("utf8")

    def getCityId(self):
        return self.city_id
    
class Community(models.Model):

    community_id   = models.AutoField(primary_key=True)
    community_name = models.CharField(max_length=100, blank=True, null=True)
    community_lng  = models.CharField(max_length=100, blank=True, null=True)#jing du
    community_lat  = models.CharField(max_length=100, blank=True, null=True)#wei  du
    city           = models.ForeignKey(City, related_name='CITY', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table="yl_community"

    def __str__(self):
        if self.community_name is None:
            return 'null'
        else:
            return "[" + self.city.city_name.encode("utf8") + "]-" + self.community_name.encode("utf8")

    def getCommunityId(self):
        return self.community_id

class Block(models.Model):
    block_id        = models.AutoField(primary_key=True)
    block_name      = models.CharField(max_length=100, blank=True, null=True)
    community       = models.ForeignKey(Community, related_name='COMMUNITY', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table="yl_block"
    
    def __str__(self):
        if self.block_name is None:
            return 'null'
        else:
            return "[" + self.community.city.city_name.encode("utf8") + "]-" +\
                   "[" + self.community.community_name.encode("utf8") + "]-" + self.block_name.encode("utf8")

    def getBlockId(self):
        return self.block_id
    def getBlockName(self):
        return  self.block_name

class BuildNum(models.Model):
    
    buildnum_id   = models.AutoField(primary_key=True)
    building_name = models.CharField(max_length=150, blank=True, null=True)
    block         = models.ForeignKey(Block, related_name='BLOCK', blank=True, null=True, on_delete=models.SET_NULL)
    community     = models.ForeignKey(Community, related_name='COMMUNITY_B', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table="yl_building_num"

    def __str__(self):
        if self.building_name is None:
            return 'null'
        else:
            if self.block is None:
                return "[" + self.community.city.city_name.encode("utf8") + "]-" + \
                       "[" + self.community.community_name.encode("utf8") + self.building_name.encode("utf8")
            else: 
                return "[" + self.block.community.city.city_name.encode("utf8") + "]-" + \
                       "[" + self.block.community.community_name.encode("utf8")+'-'+self.block.block_name.encode("utf8")+"]-"+ \
                       self.building_name.encode("utf8")

    def getBuildNumId(self):
        return self.buildnum_id

class AptNum(models.Model):

    apt_id   = models.AutoField(primary_key=True)
    apt_name = models.CharField(max_length=150, blank=True, null=True)
    buildnum = models.ForeignKey(BuildNum, related_name='BUILDNUM', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table="yl_apt_num"

    def __str__(self):
        if self.apt_name is None:
            return 'null'
        else:
            if self.buildnum.block is None:
                return "[" + self.buildnum.community.city.city_name.encode("utf8") + "]-" + \
                       "[" + self.buildnum.community.community_name.encode("utf8") + "-" + \
                       "[" + self.buildnum.building_name.encode("utf8")+"]-"+self.apt_name.encode("utf8")
            else: 
                return "[" + self.buildnum.block.community.city.city_name.encode("utf8") + "]-" + \
                       "[" + self.buildnum.block.community.community_name.encode("utf8") + "-" + \
                       self.buildnum.block.block_name.encode("utf8")+"]-"+ \
                       "[" + self.buildnum.building_name.encode("utf8")+"]-"+self.apt_name.encode("utf8")
    def getAptNumId(self):
        return self.apt_id

class AddressDetails(models.Model):
   
    ad_id                   = models.CharField(max_length=150, primary_key=True)
    family_name             = models.TextField(blank=True,null=True)   
    family_address          = models.TextField(blank=True,null=True)  
    city_name               = models.CharField(max_length=100, blank=True, null=True)
    community_name          = models.CharField(max_length=150, blank=True, null=True)
    block_name              = models.CharField(max_length=150, blank=True, null=True)
    building_name           = models.CharField(max_length=150, blank=True, null=True)
    apt_name                = models.CharField(max_length=150, blank=True, null=True)
    family_display_name     = models.TextField(blank=True,null=True)
    family_member_count     = models.IntegerField(blank=True,null=True)
    family_portrait         = models.TextField(blank=True,null=True)
    family_background_color = models.TextField(blank=True,null=True)
    apt_id                  = models.BigIntegerField(blank=True,null=True)
    city_id                 = models.BigIntegerField(blank=True,null=True)
    block_id                = models.BigIntegerField(blank=True,null=True)
    building_id             = models.BigIntegerField(blank=True,null=True)
    community_id            = models.BigIntegerField(blank=True,null=True)
    address_mark            = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table="yl_addrdetails"
    
    def getAddrDetailId(self):
        return self.ad_id

#商圈
class BusinessCircle(models.Model):
    bc_id        = models.AutoField(primary_key=True)
    bc_uid       = models.CharField(max_length=150, blank=True, null=True, db_index=True) # 唯一标识
    city         = models.ForeignKey(City, related_name='CITY_BC', blank=True, null=True, on_delete=models.SET_NULL) #所在城市
    community    = models.ForeignKey(Community, related_name='COMMUNITY_BC', blank=True, null=True, on_delete=models.SET_NULL)
    bc_name      = models.TextField(blank=True,null=True) #名称
    bc_address   = models.TextField(blank=True,null=True) # 地址
    bc_location  = models.TextField(blank=True,null=True) # 经纬度
    bc_tag       = models.CharField(max_length=100, blank=True, null=True) # 标签
    bc_distance  = models.BigIntegerField(blank=True,null=True) # 距离
    bc_telephone = models.CharField(max_length=100, blank=True, null=True) #电话
    bc_imgurl    = models.TextField(blank=True,null=True) # 图片
    bc_discount  = models.TextField(blank=True,null=True) # 优惠
    bc_describe  = models.TextField(blank=True,null=True) # 描述
    bc_shophours = models.CharField(max_length=100, blank=True, null=True) #营业时间
    bc_facility  = models.FloatField(default=0, editable = False) #星级评分
    bc_favorite  = models.FloatField(default=0, editable = False) #人气
    
    class Meta:
        db_table="yl_bizcir"
    def getBizCir(self):
        return self.bc_id

from users.models import User

#评分
class BizCirFacility(models.Model):
    bcf_id       = models.AutoField(primary_key = True)
    bcf_uid      = models.CharField(max_length=150, blank=True, null=True, db_index=True) # 唯一标识
    bcf_tag      = models.IntegerField(default=0, editable = False) # 标签
    bcf_facility = models.FloatField(default=0, editable = False) #星级评分
    bcf_attitude = models.FloatField(default=0, editable = False) #服务态度
    bcf_flavor   = models.FloatField(default=0, editable = False) #菜品口味
    bcf_env      = models.FloatField(default=0, editable = False) #环境等级
    
    class Meta:
        db_table="yl_bizcir_facility"
    def getBizCir(self):
        return self.bcf_id

#评论
class BizCirEvaluate(models.Model):
    bce_id          = models.AutoField(primary_key=True)
    bce_uid         = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    bce_content     = models.TextField(blank=True,null=True) # 内容
    bce_sendtime    = models.TextField(blank = True, null = True) 
    bce_status      = models.IntegerField(default=0, editable = False) #是否匿名 0否 1是
    bce_senderid    = models.BigIntegerField(default=0, editable = False)
    bce_replayid    = models.BigIntegerField(default=0, editable = False)
    bce_contenttype = models.IntegerField(default=0, editable = False) # 0 纯字符串  1 非纯字符串
    facility        = models.ForeignKey(BizCirFacility, related_name='BCFACILITY_BCE', blank=True, null=True, on_delete=models.SET_NULL) #星级评分
    community       = models.ForeignKey(Community, related_name='COMMUNITY_BCE', blank=True, null=True, on_delete=models.SET_NULL)
    user            = models.ForeignKey(User, related_name='USER_BCE', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table="yl_bizcir_eva"
    def getBizCirEva(self):
        return self.bce_id
    
#评论资源    
class BizCirMediaFiles(models.Model):
    bcmf_id          = models.AutoField(primary_key = True)
    uid              = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    bcmf_respath     = models.TextField(blank = True, null = True)
    bcmf_filekey     = models.TextField(blank = True, null = True)
    bcmf_contenttype = models.IntegerField(default=0, editable = False) #0-》图片  1-》语音
    bizcirevaluate   = models.ForeignKey('BizCirEvaluate', related_name='EVA_BCE', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table="yl_bizcir_media_files"
    def getBizCir(self):
        return self.bcmf_id

#获取用户评价操作记录
class UserEvaluatiorRecord(models.Model):
    uer_id     = models.AutoField(primary_key = True)
    uer_uid    = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    uer_status = models.IntegerField(default=0, editable = False) # 0 未评论  1 已评论  2 过期
    user       = models.ForeignKey(User, related_name='USER_UER', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table="yl_evaluat_record"
    def getBizCirRecordId(self):
        return self.uer_id
    
    