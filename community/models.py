# coding:utf-8
from django.db import models
from users.models import User
from billiard.dummy import Process

# Create your models here.

class Topic(models.Model):
    topic_id               = models.AutoField(primary_key = True)
    topic_title            = models.TextField(blank = True, null = True)
    topic_content          = models.TextField(blank = True, null = True)
    topic_category_type    = models.IntegerField(blank = True, null = True) #
    topic_time             = models.BigIntegerField(blank = True, null = True)
    topic_url              = models.TextField(blank = True, null = True)
    forum_id               = models.BigIntegerField(blank = True, null = True) # 0 community 1 round 2 city
    forum_name             = models.TextField(blank = True, null = True)
    sender_id              = models.BigIntegerField(blank = True, null = True)
    sender_name            = models.TextField(blank = True, null = True)
    sender_lever           = models.TextField(blank = True, null = True)
    sender_portrait        = models.TextField(blank = True, null = True)
    collect_status         = models.IntegerField(blank = True, null = True)
    sender_family_id       = models.BigIntegerField(blank = True, null = True)
    sender_family_address  = models.TextField(blank = True, null = True)
    display_name           = models.TextField(blank = True, null = True)
    comment_num            = models.IntegerField(blank = True, null = True)
    like_num               = models.IntegerField(blank = True, null = True)
    send_status            = models.IntegerField(blank = True, null = True)
    like_status            = models.IntegerField(blank = True, null = True)
    visiable_type          = models.IntegerField(blank = True, null = True)
    object_data_id         = models.IntegerField(blank = True, null = True)  # 0 topic  1 activity  (objectType) 3 news 4 change
    object_type            = models.TextField(blank = True, null = True)
    hot_flag               = models.IntegerField(blank = True, null = True)
    view_num               = models.IntegerField(blank = True, null = True)
    cache_key              = models.IntegerField(blank = True, null = True)
    circle_type            = models.IntegerField(blank = True, null = True) # 可用于判断是否创建帖子成功 
    forward_path           = models.TextField(blank = True, null = True)
    forward_refer_id       = models.IntegerField(blank = True, null = True)    
    sender_city_id         = models.IntegerField(blank=True,null=True)
    sender_community_id    = models.IntegerField(blank=True,null=True)
    sender_block_id        = models.IntegerField(blank=True,null=True)
    sender_building_id     = models.IntegerField(blank=True,null=True)
    sender_apt_id          = models.IntegerField(blank=True,null=True)
    process_status         = models.IntegerField(blank=True,null=True)
    process_data           = models.TextField(blank=True,null=True)
    delete_type            = models.IntegerField(blank=True,null=True) # 2表示已经删除 4表示物业删除普通用户可看

    class Meta:
        db_table="yl_topic"
    def __str__(self):
        if self.topic_content is None:
            return  'null'
        else:
            return  self.topic_content.encode("utf8")
  
    def getTopicId(self):
        return self.topic_id

#我想要的用户列表
class FavouriteList(models.Model):
    _id    = models.AutoField(primary_key = True)
    topic  = models.BigIntegerField(blank = True, null = True) 
    sender = models.BigIntegerField(blank = True, null = True)
    user   = models.BigIntegerField(blank = True, null = True)
    status = models.IntegerField(blank=True,null=True) #1洽谈中  2取消交易 3交易完成
    time   = models.BigIntegerField(blank = True, null = True) #操作时间
    
    class Meta:
        db_table="yl_favouritelist"

    def getFavourId(self):
        return self._id

class Praise(models.Model):
    _id   = models.AutoField(primary_key = True)
    topic = models.BigIntegerField(blank = True, null = True) 
    user  = models.BigIntegerField(blank = True, null = True)

    class Meta:
        db_table="yl_praise"

    def getPraiseId(self):
        return self._id

class Comment(models.Model):
    comment_id      = models.AutoField(primary_key = True)
    topic           = models.ForeignKey('Topic', related_name='TOPIC_C', blank=True, null=True, on_delete=models.SET_NULL)
    content         = models.TextField(blank = True, null = True)
    senderAddress   = models.TextField(blank = True, null = True)
    senderAvatar    = models.TextField(blank = True, null = True)
    senderName      = models.TextField(blank = True, null = True)
    senderNcRoleId  = models.BigIntegerField(blank = True, null = True)
    sendTime        = models.TextField(blank = True, null = True)
    senderFamilyId  = models.BigIntegerField(blank = True, null = True)
    senderId        = models.BigIntegerField(blank = True, null = True)
    replayId        = models.BigIntegerField(blank = True, null = True)
    senderLevel     = models.TextField(blank = True, null = True)
    contentType     = models.IntegerField(blank = True, null = True)
    displayName     = models.TextField(blank = True, null = True)
    videoTime       = models.TextField(blank = True, null = True)

    class Meta:
        db_table="yl_comment"
    def __str__(self):
        if self.content is None:
            return 'null'#+str(self.comment_id)
        else:
            return self.content.encode("utf8")
    def getDispalyName(self):
        return self.displayName.encode("utf8")

    def getCommentId(self):
        return self.comment_id

class SayHello(models.Model):
    _id      = models.AutoField(primary_key = True)
    user_id  = models.BigIntegerField(blank=True, null=True, db_index=True)
    topic_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    
    class Meta:
        db_table="yl_sayhello"
    
    def getSayHelloId(self):
        return self._id
    
class Media_files(models.Model):
    mediafile_id  = models.AutoField(primary_key = True)
    topic         = models.ForeignKey('Topic', related_name='TOPIC_M', blank=True, null=True, on_delete=models.SET_NULL)
    resPath       = models.TextField(blank = True, null = True)
    fileKey       = models.TextField(blank = True, null = True)
    contentType   = models.TextField(blank = True, null = True)
    resId         = models.BigIntegerField(blank = True, null = True)   # is upload pic   default 0
    comment_id    = models.BigIntegerField(blank = True, null = True)   # is user avatar  default 0

    class Meta:
        db_table="yl_media_files"
    def __str__(self):
        if self.resPath is None:
            return 'null'
        else:
            return self.resPath.encode("utf8")

class SecondHand(models.Model):
    secondHand_id      = models.AutoField(primary_key = True)
    topic              = models.ForeignKey('Topic', related_name='TOPIC_S', blank=True, null=True, on_delete=models.SET_NULL)
    startTime          = models.TextField(blank = True, null = True)
    endTime            = models.TextField(blank = True, null = True)
    label              = models.TextField(blank = True, null = True)   #biao qian
    price              = models.TextField(blank = True, null = True)   #jia ge
    tradeStatus        = models.IntegerField(blank = True, null = True)#交易状态    1上架中 2洽谈中 3下架  4交易完成
    url                = models.TextField(blank = True, null = True)  # img
    oldornew           = models.IntegerField(blank = True, null = True) #xin jiu zhuangtai  1-10
    
    class Meta:
        db_table="yl_sencondhandle"
    
    def getSecondHandId(self):
        return self.secondHand_id
    
class Activity(models.Model):
    activity_id        = models.AutoField(primary_key = True)
    topic              = models.ForeignKey('Topic', related_name='TOPIC_A', blank=True, null=True, on_delete=models.SET_NULL)
    startTime          = models.TextField(blank = True, null = True)
    endTime            = models.TextField(blank = True, null = True)
    content            = models.TextField(blank = True, null = True)
    location           = models.TextField(blank = True, null = True)
    tag                = models.TextField(blank = True, null = True)
    signFlag           = models.IntegerField(blank = True, null = True)
    confirmFlag        = models.IntegerField(blank = True, null = True)
    lotteryFlag        = models.IntegerField(blank = True, null = True)
    enrollUserCount    = models.IntegerField(blank = True, null = True)
    enrollNeCount      = models.IntegerField(blank = True, null = True)
    checkinUserCount   = models.IntegerField(blank = True, null = True)
    checkinNeCount     = models.IntegerField(blank = True, null = True)
    rosterStatus       = models.IntegerField(blank = True, null = True)
    processStatus      = models.IntegerField(blank = True, null = True)
    ncId               = models.IntegerField(blank = True, null = True)
    longitude          = models.TextField(blank = True, null = True)
    latitude           = models.TextField(blank = True, null = True)

    class Meta:
        db_table="yl_activity"

    def getSignFlag(self):
        return self.signFlag.encode("utf8")
    
    def getActivityId(self):
        return self.activity_id
    
    
class EnrollActivity(models.Model):
    enroll_id           = models.AutoField(primary_key = True)
    activity            = models.ForeignKey(Activity, related_name='Activity', blank=True, null=True, on_delete=models.SET_NULL)
    user                = models.ForeignKey(User, related_name='User', blank=True, null=True, on_delete=models.SET_NULL)
    enrollUserCount     = models.IntegerField(blank = True, null = True)
    enrollNeCount       = models.IntegerField(blank = True, null = True)
    enrollDate          = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "yl_enrollActivity"
        
    def getEnrollActivityId(self):
        return self.enroll_id
    
class ReportTopic(models.Model):
    report_id = models.AutoField(primary_key = True)
    topic_id         = models.BigIntegerField(blank = True, null = True)
    complain_user_id = models.BigIntegerField(blank = True, null = True)
    sender_user_id   = models.BigIntegerField(blank = True, null = True)
    community_id     = models.BigIntegerField(blank = True, null = True)
    title            = models.TextField(blank = True, null = True)
    content          = models.TextField(blank = True, null = True)
    time             = models.BigIntegerField(blank = True, null = True)
    class Meta:
        db_table = "yl_report"
        
    def getReportId(self):
        return self.report_id

class CollectionTopic(models.Model):
    collect_id = models.AutoField(primary_key = True)
    sender_id  = models.BigIntegerField(blank = True, null = True)
    user       = models.ForeignKey(User, related_name='collectUser', blank=True, null=True, on_delete=models.SET_NULL)
    topic      = models.ForeignKey(Topic, related_name='collectTopic', blank=True, null=True, on_delete=models.SET_NULL)
    community_id     = models.BigIntegerField(blank = True, null = True)
    
    
    class Meta:
        db_table = "yl_collectTopic"
        
    def getCollectId(self):
        return self.collect_id

#轮播推广模块
class CarouselInfo(models.Model):
    c_id        = models.AutoField(primary_key = True)
    c_img       = models.TextField(blank = True, null = True) #图片路径
    c_url       = models.TextField(blank = True, null = True) #访问网址
    c_index     = models.IntegerField(blank = True, null = True) #模块索引
    c_title     = models.CharField(max_length=50, blank=True, null=True) #模块标题
    c_content   = models.TextField(blank = True, null = True) #模块内容
    c_community = models.BigIntegerField(blank = True, null = True, db_index=True) #所在小区
    
    class Meta:
        db_table = "yl_carouselinfo"
    
    def getSquareInfoId(self):
        return self.c_id

#广场详情模块
class SquareInfo(models.Model):
    s_id        = models.AutoField(primary_key = True)
    s_img       = models.TextField(blank = True, null = True) #图片路径
    s_url       = models.TextField(blank = True, null = True) #访问网址
    s_index     = models.IntegerField(blank = True, null = True) #模块索引
    s_name      = models.CharField(max_length=50, blank=True, null=True) #模块名称
    s_community = models.BigIntegerField(blank = True, null = True, db_index=True) #所在小区
    
    class Meta:
        db_table = "yl_squareinfo"
    
    def getSquareInfoId(self):
        return self.s_id
    
#爆款商品
class SquareGoods(models.Model):
    
    sg_id        = models.AutoField(primary_key = True)
    sg_name      = models.TextField(blank = True, null = True) #商品名称
    sg_detail    = models.TextField(blank = True, null = True) #商品详情
    sg_price     = models.TextField(blank = True, null = True) #商品价格
    sg_imgurl    = models.TextField(blank = True, null = True) #商品图片 第一张
    sg_category  = models.IntegerField(blank = True, null = True) #类别 默认为0 
    sg_status    = models.IntegerField(blank = True, null = True) #状态  0 编辑中  1 上架   2 下架  
    sg_community = models.BigIntegerField(blank = True, null = True, db_index=True) #所在小区
    sg_hot       = models.IntegerField(blank = True, null = True) #火爆状态  0 正常  1 火爆
    sg_weight    = models.TextField(blank = True, null = True) #商品毛重
    sg_number    = models.TextField(blank = True, null = True) #商品编号
    sg_rank      = models.BigIntegerField(blank = True, null = True)#商品排名
    
    class Meta:
        db_table = "yl_squaregoods"
    
    def getSquareGoodsId(self):
        return self.sg_id

#爆款商品评价
class GoodsEvaluate(models.Model):

    ge_id        = models.AutoField(primary_key = True)
    ge_type      = models.IntegerField(blank = True, null = True) #状态  0 好评  1 中评   2 差评
    ge_category  = models.IntegerField(blank = True, null = True) #评价类型  0 一级回复 1 二级回复
    ge_sender_id = models.BigIntegerField(blank = True, null = True) #发布者
    ge_replay_id = models.BigIntegerField(blank = True, null = True) #回复发布者
    ge_send_time = models.BigIntegerField(blank = True, null = True) #评价时间
    ge_buy_time  = models.BigIntegerField(blank = True, null = True) #购买时间
    ge_content   = models.TextField(blank = True, null = True) #评价内容
    ge_status    = models.IntegerField(blank = True, null = True) # 0表示没有图片 1表示有图片
    squaregoods  = models.ForeignKey(SquareGoods, related_name='SquareGoods_S', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = "yl_goodsevaluate"
    
    def getGoodsEvaluateId(self):
        return self.ge_id

#爆款商品评价的点赞
class GoodsEvaLike(models.Model):

    gel_id       = models.AutoField(primary_key = True)
    ge_id        = models.BigIntegerField(blank = True, null = True) #爆款商品评价
    ge_sender_id = models.BigIntegerField(blank = True, null = True) #发布者
    ge_liker_id  = models.BigIntegerField(blank = True, null = True) #点赞者
    
    class Meta:
        db_table = "yl_goodsevalike"
    
    def getGoodsEvaLikeId(self):
        return self.gel_id
    
#爆款商品评分
class GoodsFacility(models.Model):
    
    gf_id       = models.AutoField(primary_key = True)
    gf_tag      = models.IntegerField(default=0, editable = False) # 标签
    gf_facility = models.FloatField(default=0, editable = False) #星级评分
    user        = models.ForeignKey(User, related_name='USER_SF', blank=True, null=True, on_delete=models.SET_NULL)
    evaluate    = models.ForeignKey(GoodsEvaluate, related_name='GoodsEvaluate_SF', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = "yl_goodsfacility"
    
    def getGoodsFacilityId(self):
        return self.gf_id

#买家爆款商品列表
class GoodsList(models.Model):
    
    gl_id          = models.AutoField(primary_key = True)
    gl_count       = models.IntegerField(default=0, editable = False) # 商品数量 最少一个
    gl_imgurl      = models.TextField(blank = True, null = True) # 当前商品图片
    gl_price       = models.TextField(blank = True, null = True) # 当前商品单价
    gl_detail      = models.TextField(blank = True, null = True) # 当前商品描述
    gl_community   = models.BigIntegerField(blank = True, null = True) #小区id
    gl_goodsattr   = models.IntegerField(blank = True, null = True) #属性id 对应GoodsType表的id
    gl_ordernumber = models.TextField(blank = True, null = True) # 订单编号
    buy_user       = models.ForeignKey(User, related_name='USER_GL', blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = "yl_goodslist"
    
    def getGoodsListId(self):
        return self.gl_id
#买家交易时使用的地址详情
class BuyerDetailAddress(models.Model):
    
    bda_id          = models.AutoField(primary_key = True)
    bda_ordernumber = models.TextField(blank = True, null = True)#订单编号
    bda_consignee   = models.TextField(blank = True, null = True)#收货人名称
    bda_contactinfo = models.TextField(blank = True, null = True)#联系方式
    bda_localarea   = models.TextField(blank = True, null = True)#所在地区
    bda_detailaddr  = models.TextField(blank = True, null = True)#详细地址
    bda_province    = models.TextField(blank = True, null = True)#所在省份
    bda_city        = models.TextField(blank = True, null = True)#所在城市
    bda_block       = models.TextField(blank = True, null = True)#所在区域
    class Meta:
        db_table = "yl_buyerdetailaddr"
    
    def getBuyerAddrId(self):
        return self.bda_id
#买家交易时的付款信息
class BuyerPayInfo(models.Model):
    
    bpi_id          = models.AutoField(primary_key = True)
    bpi_ordernumber = models.TextField(blank = True, null = True)#订单编号
    bpi_paytype     = models.IntegerField(default=0, editable = False) # 支付类型 0 支付宝 1 微信 2 银联 3货到付款
    bpi_paystatus   = models.IntegerField(default=0, editable = False) # 支付状态 0 未支付 1已支付
    bpi_goodsprice  = models.TextField(blank = True, null = True) #商品总额
    bpi_payprice    = models.TextField(blank = True, null = True) #支付总额
    bpi_benefit     = models.TextField(blank = True, null = True) #订单优惠 钱
    bpi_coupon      = models.TextField(blank = True, null = True) #优惠卷 钱
    bpi_freight     = models.TextField(blank = True, null = True) #运费 钱
    bpi_paytime     = models.BigIntegerField(blank = True, null = True) #付款时间
    class Meta:
        db_table = "yl_buyerpayinfo"
    
    def getBuyerPayInfoId(self):
        return self.bpi_id

#商品类型（便于管理商品属性）
class GoodsType(models.Model):
    
    gt_id     = models.AutoField(primary_key = True)
    gt_number = models.TextField(blank = True, null = True) # 商品编号的缩写形式
    gt_type   = models.IntegerField(default=0, editable = False) # 0表示食品
    
    class Meta:
        db_table = "yl_goodstypes"
    
    def getGoodsTypeId(self):
        return self.gt_id
    
#食物商品的属性
class FoodGoodsAttribute(models.Model):
    
    fga_id          = models.AutoField(primary_key = True)
    
    class Meta:
        db_table = "yl_foodgoodsattr"
    
    def getFoodGoodsAttId(self):
        return self.fga_id

#爆款商品文件资源（图片+语音）
class SquareFileResouce(models.Model):
    
    sfr_id         = models.AutoField(primary_key = True)
    user_id        = models.BigIntegerField(blank = True, null = True)
    evaluate_id    = models.BigIntegerField(blank = True, null = True)
    SquareGoods_id = models.BigIntegerField(blank = True, null = True)
    sfr_res_path   = models.TextField(blank = True, null = True)
    sfr_res_type   = models.BigIntegerField(blank = True, null = True) # 0 爆款宣传图片  # 1 评论图片  2 评论语音   3 评论视频  
                                                                     # 4 回复评论图片  # 5 回复语音  6 回复视频 

    class Meta:
        db_table = "yl_squarefileres"
    
    def getSquareGoodsId(self):
        return self.sfr_id
    
#用户收货地址
class ReceiptAddress(models.Model):
    
    ra_id          = models.AutoField(primary_key = True)
    ra_consignee   = models.TextField(blank = True, null = True)#收货人名称
    ra_contactinfo = models.TextField(blank = True, null = True)#联系方式
    ra_localarea   = models.TextField(blank = True, null = True)#所在地区
    ra_detailaddr  = models.TextField(blank = True, null = True)#详细地址
    ra_province    = models.TextField(blank = True, null = True)#所在省份
    ra_city        = models.TextField(blank = True, null = True)#所在城市
    ra_block       = models.TextField(blank = True, null = True)#所在区域
    ra_defaultflag = models.IntegerField(default=0, editable = False) #默认地址 1表示默认0表示记录地址
    user           = models.ForeignKey(User, related_name='USER_RA', blank=True, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = "yl_receiptaddress"
    
    def getReceiptAddressId(self):
        return self.ra_id