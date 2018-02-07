# coding:utf-8
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
from rest_framework.decorators import api_view
from core.settings import RES_URL,HOST_IP,MEDIA_ROOT
from community.models import SquareInfo,CarouselInfo
from community.models import SquareGoods,GoodsEvaluate,SquareFileResouce
from community.models import GoodsEvaLike,GoodsFacility,ReceiptAddress 
from community.models import BuyerPayInfo,GoodsType,BuyerDetailAddress,BuyerPayInfo
from community.views import makeThumbnail

#RES_URL=>https://123.57.9.62/media/youlin/
#HOST_IP=>https://123.57.9.62

def GetRequestParams(request,paramLists):
    dicts = {}
    if request.method == 'POST':
        for param in paramLists:
            requestValue = request.POST.get(param, None)
            rDicts = { param : requestValue }
            dicts.update(rDicts)
    else:
        for param in paramLists:
            requestValue = request.GET.get(param, None)
            rDicts = { param : requestValue }
            dicts.update(rDicts)
    return dicts

def GenSquareInfoDict(SquareInfoObj):
    dicts = {}
    dicts.setdefault('id',SquareInfoObj.getSquareInfoId())
    dicts.setdefault('cid',SquareInfoObj.s_community)
    dicts.setdefault('img',RES_URL+SquareInfoObj.s_img)
    dicts.setdefault('url',HOST_IP+SquareInfoObj.s_url)
    dicts.setdefault('index',SquareInfoObj.s_index)
    dicts.setdefault('name',SquareInfoObj.s_name)
    return dicts

def GenCarouselInfoDict(CarouselInfoObj):
    dicts = {}
    dicts.setdefault('cid',CarouselInfoObj.c_community)
    dicts.setdefault('img',RES_URL+CarouselInfoObj.c_img)
    dicts.setdefault('url',HOST_IP+'/yl'+CarouselInfoObj.c_url)
    dicts.setdefault('index',CarouselInfoObj.c_index)
    dicts.setdefault('title',CarouselInfoObj.c_title)
    dicts.setdefault('content',CarouselInfoObj.c_content)
    return dicts

#获取广场初始化详细信息
def InitSquaresInfo(request):
    response_data = {}
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
    else:
        communityId = request.GET.get('community_id', None)
    if communityId is None:
        response_data['flag'] = 'argv_error'
        return  response_data
    carouselList = []
    """
    squareList = []
    squareQuerySet = SquareInfo.objects.filter(s_community=long(communityId)).order_by('s_index')
    squareCount = squareQuerySet.count() #一共有多少个模块
    targetSquareObjs = squareQuerySet[:8]
    for squareObj in targetSquareObjs:
        squareList.append(GenSquareInfoDict(squareObj))
    if squareCount == 0:
        response_data['square_count'] = squareCount
        response_data['square_status'] = 0
    else:
        response_data['square_status'] = 1
        response_data['square_count'] = squareCount
        response_data['square_info'] = squareList
        if squareCount >= 9:
            moreDict = {}
            moreDict['img'] = RES_URL+ 'res/default/avatars/head.jpg'
            moreDict['id'] = squareList[-1]['id']
            moreDict['count'] = squareCount - 8
            response_data['square_more'] = moreDict
    """
    carouselQuerySet = CarouselInfo.objects.filter(c_community=long(communityId)).order_by('c_index')
    carouselCount = carouselQuerySet.count() #一共有多少个模块
    for carouselObj in carouselQuerySet:
        carouselList.append(GenCarouselInfoDict(carouselObj))
    response_data['carousel_count'] = carouselCount
    response_data['carousel_info'] = carouselList
    return response_data

#获取更多广场模块        
def GetMoreSquare(request):
    response_data = {}
    if request.method == 'POST':
        communityId = request.POST.get('community_id', None)
        squareId    = request.POST.get('square_id', None)
    else:
        communityId = request.GET.get('community_id', None)
        squareId    = request.GET.get('square_id', None)
    if communityId is None or squareId is None:
        response_data['flag'] = 'argv_error'
        return  response_data
    
    squareQuerySet = SquareInfo.objects.filter(s_community=long(communityId),s_id__gt=long(squareId)).order_by('s_index')
    squareList = []
    squareCount = squareQuerySet.count() #一共有多少个模块
    for squareObj in squareQuerySet:
        squareList.append(GenSquareInfoDict(squareObj))
    if squareCount == 0:
        response_data['square_count'] = squareCount
        response_data['square_status'] = 0
    else:
        response_data['square_status'] = 1
        response_data['square_count'] = squareCount
        response_data['square_info'] = squareList
    return response_data   

def GenAddressListDict(raInfoObj):
    dicts = {}
    dicts.setdefault('addressid',raInfoObj.getReceiptAddressId()) #收货地址id
    dicts.setdefault('consignee',raInfoObj.ra_consignee) #收货人名称
    dicts.setdefault('contactinfo',raInfoObj.ra_contactinfo)#联系方式
    dicts.setdefault('localarea',raInfoObj.ra_localarea)#所在地区
    dicts.setdefault('detailstreet',raInfoObj.ra_detailaddr)#详细地址
    dicts.setdefault('defaultflag',raInfoObj.ra_defaultflag)#默认地址 1表示默认0表示记录地址
    dicts.setdefault('province',raInfoObj.ra_province)#省份
    dicts.setdefault('city',raInfoObj.ra_city)#城市
    dicts.setdefault('block',raInfoObj.ra_block)#城区
    dicts.setdefault('detailaddr',raInfoObj.ra_localarea+raInfoObj.ra_detailaddr)#详细地址
    return dicts

#获取单个地址
def GetSingleAddress(request):
    response_data = {}
    if request.method == 'POST':
        addrId = request.POST.get('addr_id', None)
    else:
        addrId = request.GET.get('addr_id', None)
    try:
        raObj = ReceiptAddress.objects.get(ra_id=long(addrId))
        response_data['info'] = GenAddressListDict(raObj)
    except:
        response_data['info'] = 'error'
    return response_data
#进入收货地址页面
def IntoReceiptAddress(request):
    addressList = []
    addressDetail = {}
    addressDetail['default_addr'] = {}
    addressDetail['normal_addr'] = []
    response_data = {}
    if request.method == 'POST':
        userId = request.POST.get('user_id', None)
    else:
        userId = request.GET.get('user_id', None)
    raQuerySet = ReceiptAddress.objects.filter(user_id=long(userId))
    raCount = raQuerySet.count()
    if raCount > 0:#证明不是第一次进入该页面
        for i in range(0,raCount,1):
            if int(raQuerySet[i].ra_defaultflag)==1:
                addressDetail['default_addr'] = GenAddressListDict(raQuerySet[i])
            else:
                addressList.append(GenAddressListDict(raQuerySet[i]))
    addressDetail['normal_addr'] = addressList
    response_data['count'] = raCount
    response_data['info'] = addressDetail
    return response_data   
#新建收货地址
def AddReceiptAddress(request):
    response_data = {}
    if request.method == 'POST':
        userId      = request.POST.get('user', None)
        consignee   = request.POST.get('consignee', None)#收货人名称
        contactinfo = request.POST.get('contactinfo', None)#联系方式
        detailaddr  = request.POST.get('detailaddr', None)#详细街道
        province    = request.POST.get('province', None)#省份
        city        = request.POST.get('city', None)#城市
        block       = request.POST.get('block', None)#城区
        count       = request.POST.get('count', None) #地址数量
    else:
        userId      = request.GET.get('user', None)
        consignee   = request.GET.get('consignee', None)
        contactinfo = request.GET.get('contactinfo', None)
        detailaddr  = request.GET.get('detailaddr', None)
        province    = request.GET.get('province', None)
        city        = request.GET.get('city', None)
        block       = request.GET.get('block', None)
        count       = request.GET.get('count', None) #地址数量
    maxCount = ReceiptAddress.objects.filter(user_id = userId).count()
    if maxCount > 10:
        response_data['flag'] = 'overflow' 
        return response_data
    if province is None:
        localarea = city+block
    else:
        localarea = province+city+block
    raTuple = ReceiptAddress.objects.get_or_create(ra_consignee=consignee,
                                                   ra_contactinfo=contactinfo,
                                                   ra_localarea=localarea,
                                                   ra_detailaddr=detailaddr,
                                                   ra_province=province,
                                                   ra_city=city,
                                                   ra_block=block,
                                                   user_id = userId)
    if raTuple[1]==True:#新创建的对象        1表示默认0表示记录地址
        raId = raTuple[0].getReceiptAddressId()
        if int(count) == 0:#设置默认地址 
            raTuple[0].ra_defaultflag = 1
            raTuple[0].save()
        elif int(count) == 1:#设置新地址 
            raTuple[0].ra_defaultflag = 0
            raTuple[0].save()
        elif int(count) == 2:#设置新地址为默认地址 
            from django.db import connection,transaction
            cursor = connection.cursor()
            cursor.execute('update yl_receiptaddress set ra_defaultflag = 0 \
                            where user_id =%s',[long(userId)])    
            transaction.commit_unless_managed()
            rtObj = ReceiptAddress.objects.get(user_id = long(userId),ra_id = raId)
            rtObj.ra_defaultflag = 1
            rtObj.save()
            response_data['flag'] = 'ok'
            response_data['default'] = raTuple[0].ra_defaultflag
            response_data['info'] = GenAddressListDict(rtObj)
            response_data['addrID'] = raId
            return response_data
        response_data['flag'] = 'ok' 
        response_data['default'] = raTuple[0].ra_defaultflag
        response_data['info'] = GenAddressListDict(raTuple[0])
    else:
        response_data['flag'] = 'exist' 
        response_data['default'] = raTuple[0].ra_defaultflag
        response_data['info'] = GenAddressListDict(raTuple[0])
    response_data['addrID'] = raTuple[0].getReceiptAddressId()
    return response_data
#删除收货地址
def DelReceiptAddress(request):
    response_data = {}
    if request.method == 'POST':
        raId = request.POST.get('id', None)
    else:
        raId = request.GET.get('id', None)
    ReceiptAddress.objects.filter(ra_id=long(raId)).delete()
    response_data['flag'] = 'ok'
    return response_data
#修改收货地址
def EditReceiptAddress(request):
    response_data = {}
    if request.method == 'POST':
        raId        = request.POST.get('id', None)
        userId      = request.POST.get('user', None)
        consignee   = request.POST.get('consignee', None)#收货人名称
        detailaddr  = request.POST.get('detailaddr', None)#详细街道
        contactinfo = request.POST.get('contactinfo', None)#联系方式
        province    = request.POST.get('province', None)#省份
        city        = request.POST.get('city', None)#城市
        block       = request.POST.get('block', None)#城区
        default     = request.POST.get('defaultflag', None) #默认状态值
    else:
        raId        = request.GET.get('id', None)
        userId      = request.GET.get('user', None)
        consignee   = request.GET.get('consignee', None)
        detailaddr  = request.GET.get('detailaddr', None)#详细街道
        contactinfo = request.GET.get('contactinfo', None)
        province    = request.GET.get('province', None)
        city        = request.GET.get('city', None)
        block       = request.GET.get('block', None)
        default     = request.GET.get('defaultflag', None)#默认地址 1表示默认0表示记录地址
    if province is None:
        localarea = city+block
    else:
        localarea = province+city+block
    try:
        #判断修改的地址是否存在
        try:
            ReceiptAddress.objects.get(user_id = long(userId),ra_id=long(raId),ra_consignee=consignee,\
                                       ra_contactinfo=contactinfo,ra_localarea=localarea,ra_city = city,\
                                       ra_detailaddr = detailaddr,ra_province = province,ra_block = block,\
                                       ra_defaultflag = default)
            response_data['flag'] = 'exist'
            return response_data
        except:
            pass
        raObj = ReceiptAddress.objects.get(user_id = long(userId),ra_id=long(raId))
        raObj.ra_consignee = consignee
        raObj.ra_contactinfo = contactinfo
        raObj.ra_localarea = localarea
        raObj.ra_detailaddr = detailaddr
        raObj.ra_province = province
        raObj.ra_city = city
        raObj.ra_block = block
        raObj.ra_defaultflag = default
        raObj.save()
        raObjId = raObj.getReceiptAddressId()
        if int(default)==1:
            raQuerySet = ReceiptAddress.objects.filter(user_id=long(userId))
            size = raQuerySet.count()
            for i in range(0,size,1):
                raTmpId = long(raQuerySet[i].getReceiptAddressId())
                obj = ReceiptAddress.objects.get(ra_id=raTmpId)
                if long(raObjId)==raTmpId:
                    obj.ra_defaultflag = 1
                else:
                    obj.ra_defaultflag = 0
                obj.save()
            """
            for addrObj in raQuerySet:
                if long(raObjId)==long(addrObj.getReceiptAddressId()):
                    addrObj.ra_defaultflag = 1
                else:
                    addrObj.ra_defaultflag = 0
                addrObj.save()
            """
        response_data['flag'] = 'ok'
    except Exception, e:
        response_data['error'] = str(e)
        response_data['flag'] = 'no'
    return response_data
#生成订单编号的方法
def GenOrderNumber(serial):
    val = ''
    if str(serial)=='A':
       val = 'B'
    elif str(serial)=='B':
        val = 'C'
    elif str(serial)=='C':
        val = 'D'
    elif str(serial)=='D':
        val = 'E'
    elif str(serial)=='E':
        val = 'F'
    elif str(serial)=='F':
        val = 'G'
    elif str(serial)=='G':
        val = 'H'
    elif str(serial)=='H':
        val = 'I'
    elif str(serial)=='I':
        val = 'J'
    elif str(serial)=='J':
        val = 'K'
    elif str(serial)=='K':
        val = 'L'
    elif str(serial)=='L':
        val = 'M'
    elif str(serial)=='M':
        val = 'N'
    return val

def imgGenNameWithGoods(filename):
    fName = time.strftime('%m%d%M%S')+str(random.randint(1000,9999))+filename[filename.rfind('.'):]
    return fName

def imgGenPathWithGoods(community_id):
    userDir = settings.MEDIA_ROOT+'youlin/res/commodity/' + str(community_id) + '/'
    if os.path.exists(userDir):
        pass
    else:
        try:
            os.makedirs(userDir, mode=0777)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                pass
            else:raise    
    return userDir

def imgGenNameWithFacility(filename):
    fName = time.strftime('%m%d%M%S')+str(random.randint(1000,9999))+filename[filename.rfind('.'):]
    return fName

def imgGenPathWithFacility(orderNumber):
    userDir = settings.MEDIA_ROOT+'youlin/res/facility/' + orderNumber + '/'
    if os.path.exists(userDir):
        pass
    else:
        try:
            os.makedirs(userDir, mode=0777)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(userDir):
                pass
            else:raise    
    return userDir

def GetGoodsValueFromGoodsNumber(number):
    value = number[:3]
    return value

#生成商品订单账号
def CreateOrderNumber():
    return str(long(time.time()*1000))+str(random.randint(100,999))

#生成指定商品的商品详情
def GenAppointGoodsDetail(goodsObj,userId):
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)
    dicts = {}
    imgLists = []
    addrDicts = {}
    goodsChoose = {}
    dicts['goods_hot']      = goodsObj.sg_hot   #火爆状态  0 正常  1 火爆
    dicts['goods_name']     = goodsObj.sg_name
    dicts['goods_deital']   = goodsObj.sg_detail
    dicts['goods_price']    = goodsObj.sg_price
    dicts['goods_number']   = goodsObj.sg_number
    dicts['goods_describe'] = dicts['goods_deital'] + " " + dicts['goods_name']
    sfrQuerySet = SquareFileResouce.objects.filter(SquareGoods_id=goodsObj.getSquareGoodsId(),sfr_res_type=0)
    for sfrObj in sfrQuerySet:
        imgLists.append(RES_URL+sfrObj.sfr_res_path)
    dicts['goods_imgs'] = imgLists
    try:
        raObj = ReceiptAddress.objects.get(user_id=userId,ra_defaultflag=1)
        addrDicts['addr_id'] = raObj.getReceiptAddressId()
        addrDicts['addr_detail'] = raObj.ra_detailaddr
        addrDetailDicts = {}
        tmpProvince = raObj.ra_province
        if tmpProvince is None or tmpProvince=='null' or tmpProvince =='NULL':
            tmpProvince = ''
        addrDetailDicts['province'] = tmpProvince
        tmpCity = raObj.ra_city
        if tmpCity is None or tmpCity=='null' or tmpCity =='NULL':
            tmpCity = ''
        addrDetailDicts['city'] = tmpCity
        tmpBlock = raObj.ra_block
        if tmpBlock is None or tmpBlock=='null' or tmpBlock =='NULL':
            tmpBlock = ''
        addrDetailDicts['block'] = tmpBlock
        detailAddress = tmpProvince+tmpCity+tmpBlock
        addrDetailDicts['detail'] = detailAddress+raObj.ra_detailaddr
        addrDetailDicts['consignee'] = raObj.ra_consignee
        addrDetailDicts['contactinfo'] = raObj.ra_contactinfo
        addrDicts['addr_info'] = addrDetailDicts
    except:
        addrDicts['addr_id'] = 0
        addrDicts['addr_detail'] = u'尚未设置默认收货地址'
    dicts['default_address'] = addrDicts
    gtObj = GoodsType.objects.get(gt_number=GetGoodsValueFromGoodsNumber(goodsObj.sg_number)) 
    goodsChoose['goods_type'] = gtObj.gt_type
    goodsChoose['goods_count'] = str(1) + u'个'
    goodsChoose['goods_attribute'] = u'黑色'
    goodsChoose['goods_detail'] = goodsChoose['goods_attribute'] + ',' + goodsChoose['goods_count']
    dicts['goods_choose'] = goodsChoose
    return dicts

###############################################################################################
###############################################################################################
#创建爆款商品
def CreateSquareGoods(request):
    response_data = {}
    if request.method == 'POST':
        name        = request.POST.get('name', None)#商品名称
        detail      = request.POST.get('detail', None)#商品详情
        price       = request.POST.get('price', None)#商品价格
        communityId = request.POST.get('community', None)#所在小区ID
        hotStatus   = request.POST.get('hot', None)#火爆状态  0 正常  1 火爆
        weight      = request.POST.get('weight', None)#商品毛重 字符串带单位
    else:
        name        = request.GET.get('name', None)#商品名称
        detail      = request.GET.get('detail', None)#商品详情
        price       = request.GET.get('price', None)#商品价格
        communityId = request.GET.get('community', None)#所在小区ID
        hotStatus   = request.GET.get('hot', None)#火爆状态  0 正常  1 火爆
        weight      = request.GET.get('weight', None)#商品毛重 字符串带单位
    imgFile = request.FILES.get('img', None)#图片文件
    if imgFile is not None:
        newImage = imgGenNameWithGoods(imgFile.name) # new image
        imgDir = imgGenPathWithGoods(communityId)
        bigImage = '0' + newImage
        streamfile = open(imgDir+bigImage, 'wb+')
        for chunk in image.chunks():
            streamfile.write(chunk)
        streamfile.close()
        imgUrl = '/media/youlin/res/commodity/' + str(community_id) + '/'+ bigImage
    else:
        imgUrl = '/media/youlin/res/default/avatars/head.jpg' #默认图片
    # 例子 AA99AA99ZZ ==> 最大sgNumber
    sgQuerySet = SquareGoods.objects.filter(sg_community=long(communityId)).order_by('-sg_id')[:1]
    if sgQuerySet.count()==0:#第一次创建
        sgNumber = 'A'+'0'+'A'+'00A'
    else:
        lastNumber = sgQuerySet[0].sg_number
        defaultNumber = 'A'+'0'+'A'+'00'
        try:
            int(lastNumber[-4:-1])
            serial = lastNumber[len(lastNumber)-2] + lastNumber[len(lastNumber)-1]
        except:
            int(lastNumber[-3:-1])
            serial = lastNumber[len(lastNumber)-1]
        sgNumber = defaultNumber + GenOrderNumber(serial)
    SquareGoods.objects.create(sg_name=name,sg_detail=detail,sg_price=price,sg_hot=hotStatus,
                               sg_category=0,sg_status=0,sg_community=long(communityId),
                               sg_imgurl=imgUrl,sg_weight=weight,sg_number=sgNumber,sg_rank=0)
    response_data['flag'] = 'ok'
    response_data['serial'] = serial
    response_data['lastNumber'] = lastNumber
    response_data['sgNumber'] = sgNumber
    return response_data

def GenSingleGoodsWithListDick(goodsObj):
    dictWithSG = {}
    sgID      = goodsObj.getSquareGoodsId() #商品id
    sgNumber  = goodsObj.sg_number #商品编号
    sgName    = goodsObj.sg_name #商品名称
    sgDetail  = goodsObj.sg_detail #商品详情
    sgPrice   = goodsObj.sg_price #商品价格
    sgImgurl  = goodsObj.sg_imgurl #商品图片 第一张
    sgRank    = goodsObj.sg_rank #商品排名
    sgComment = GoodsEvaluate.objects.filter(squaregoods_id=sgID,ge_category=0).count()#只计算一级回复
    dictWithSG.setdefault('sgID', sgID)
    dictWithSG.setdefault('sgNumber', sgNumber)
    dictWithSG.setdefault('sgName', sgName)
    dictWithSG.setdefault('sgDetail', sgDetail)
    dictWithSG.setdefault('sgPrice', sgPrice)
    dictWithSG.setdefault('sgImgurl', HOST_IP + sgImgurl)
    dictWithSG.setdefault('sgRank', sgRank)
    dictWithSG.setdefault('sgDescribe', sgDetail+" "+sgName)
    dictWithSG.setdefault('sgComment', sgComment)
    return dictWithSG
    
#获取爆款商品列表
def GetSquareGoodsList(request):
    ListMerged = []
    response_data = {}
    if request.method == 'POST':
        commId = request.POST.get('community_id', None)#所在小区
        sgId   = request.POST.get('goods_id', None)# 0 表示初始化  非0开始正式加载
        sgType = request.POST.get('sg_type', None)# 0其他 1手机2数码3家用电器4代步工具5母婴用品6服装鞋帽7家具家居8电脑 -1全部
    else:
        commId = request.GET.get('community_id', None)#所在小区
        sgId   = request.GET.get('goods_id', None)# 0 表示初始化  非0开始正式加载
        sgType = request.GET.get('sg_type', None)# 0其他 1手机2数码3家用电器4代步工具5母婴用品6服装鞋帽7家具家居8电脑 -1全部
    if int(sgType) == -1:#表明查询全部
        if long(sgId) == 0:#初始化
            sgQuerySet = SquareGoods.objects.filter(sg_community=long(commId),sg_status=1).order_by('-sg_rank')[:6]
        else:#上拉
            sgQuerySet = SquareGoods.objects.filter(sg_community=long(commId),sg_status=1,sg_id__gt=sgId).order_by('-sg_rank')[:6]
    sgLength = sgQuerySet.count()
    for i in range(0,sgLength,1):
        ListMerged.append(GenSingleGoodsWithListDick(sgQuerySet[i]))
    response_data['lists'] = ListMerged
    return response_data

#进入爆款详情页面(商品、详情、评价)
def IntoGoodsDetailPage(request):
    response_data = {}
    paramLists = ['user_id','sg_id']
    paramDicts = GetRequestParams(request,paramLists)
    #获取商品对象，得到商品详情
    sgObj = SquareGoods.objects.get(sg_id=long(paramDicts['sg_id']))
    #生成指定商品的商品详情
    response_data['goodsInfo'] = GenAppointGoodsDetail(sgObj,paramDicts['user_id'])
    response_data['detailInfo'] = {}
    response_data['evaluateInfo'] = {}
    return response_data

#选择要购买爆款商品
def BuyGoodsWithUser(request):
    response_data = {}
    paramLists = ['user_id','goods_price','goods_count','goods_detail','community_id','img_url','goods_number']
    #买家ID      user_id
    #小区ID      community_id
    #当前商品单价    goods_price
    #当前商品图片    img_url
    #当前商品描述    goods_detail
    #品数量最少一个 goods_count
    #商品编号           goods_number
    paramDicts = GetRequestParams(request,paramLists)
    #获取商品属性
    gtObj = GoodsType.objects.get(gt_number=GetGoodsValueFromGoodsNumber(str(paramDicts['goods_number'])))
    #创建商品信息
    newOrderNumber = CreateOrderNumber()
    glObj = GoodsList(gl_goodsattr = gtObj.gt_type, gl_ordernumber = newOrderNumber,
                      buy_user_id=paramDicts['user_id'],gl_detail=paramDicts['goods_detail'],
                      gl_community=paramDicts['community_id'],gl_imgurl=paramDicts['img_url'],
                      gl_price=paramDicts['goods_price'],gl_count=paramDicts['goods_count'])
    raObj = ReceiptAddress.objects.get(user_id=paramDicts['user_id'],ra_defaultflag=1)
    bdaObj =BuyerDetailAddress(bda_ordernumber=newOrderNumber,bda_consignee=raObj.ra_consignee,
                               bda_contactinfo=raObj.ra_contactinfo,bda_localarea=raObj.ra_localarea,
                               bda_detailaddr=raObj.ra_detailaddr,bda_province=raObj.ra_province,
                               bda_city=raObj.ra_city,bda_block=raObj.ra_block)
    bdaObj.save()
    response_data['flag'] = 'ok'
    response_data['glID'] =  glObj.getGoodsListId()
    response_data['glOrderNum'] =  newOrderNumber
    return response_data

#购买爆款商品的相关信息确认
def GoodsConfirmeMessage(request):
    response_data = {}
    paramLists = ['user_id','goods_price']
    paramDicts = GetRequestParams(request,paramLists)
    
    """
    bda_ordernumber = models.TextField(blank = True, null = True)#订单编号
    bda_consignee   = models.TextField(blank = True, null = True)#收货人名称
    bda_contactinfo = models.TextField(blank = True, null = True)#联系方式
    bda_localarea   = models.TextField(blank = True, null = True)#所在地区
    bda_detailaddr  = models.TextField(blank = True, null = True)#详细地址
    bda_province    = models.TextField(blank = True, null = True)#所在省份
    bda_city        = models.TextField(blank = True, null = True)#所在城市
    bda_block       = models.TextField(blank = True, null = True)#所在区域
    """
    
    return response_data
    
#发布爆款商品评价
def ReleaseGoodsEvaluation(request):
    response_data = {}
    filesTuple = ('img_0','img_1','img_2','img_3','img_4','img_5','img_6','img_7','img_8')
    paramLists = ['sender_id','replay_id','sg_id','content','sg_facility','order_number']
    #发布者ID        sender_id
    #回复发布者ID     replay_id
    #评价的爆款商品ID  sg_id
    #评价的内容              content
    #评分                        sg_facility
    #订单编号（物品/份）order_number
    paramDicts = GetRequestParams(request,paramLists)
    if int(paramDicts['replay_id']) == 0:#表明是一级回复
        # 0 一级回复 1 二级回复
        geCategory = 0
    else:
        geCategory = 1
    geSendTime = long(time.time()*1000)   
    geObj = GoodsEvaluate(ge_content=paramDicts['content'],ge_send_time=geSendTime,
                          squaregoods_id=paramDicts['sg_id'],ge_category=geCategory,
                          ge_sender_id=paramDicts['sender_id'],ge_status=geStatus,
                          ge_replay_id=paramDicts['replay_id'])
    geID = geObj.getGoodsEvaluateId()
    gFacility = int(float(paramDicts['sg_facility']))
    GoodsFacility(user_id=paramDicts['sender_id'],evaluate_id=geID,gf_facility=gFacility)
    if gFacility > 7:
        geType = 0#0 好评  
    elif gFacility < 8 and gFacility > 4:
        geType = 1#1 中评   
    elif gFacility < 5:
        geType = 2#2 差评
    #设置商品评价类型
    geObj.ge_type = geType
    #设置购买商品的时间
    paytime = BuyerPayInfo.objects.get(bpi_ordernumber=paramDicts['order_number']).bpi_paytime
    geObj.ge_buy_time = paytime
    imgCounter = 0
    for ft in filesTuple:
        if ft in request.FILES:
            imgCounter = imgCounter + 1
            image = request.FILES.get(ft, None)
            newImage = imgGenNameWithFacility(image.name) # new image
            imgDir = imgGenPathWithFacility(paramDicts['order_number'])
            smaillImage = '0' + newImage
            bigImage = newImage
            streamfile = open(imgDir+bigImage, 'wb+')
            for chunk in image.chunks():
                streamfile.write(chunk)
            streamfile.close()
            makeThumbnail(imgDir, bigImage, smaillImage,25)
            imgUrl = '/media/youlin/res/facility/' + paramDicts['order_number'] + '/'+ smaillImage
            if geCategory == 0:# 0 一级回复 1 二级回复
                SquareFileResouce(evaluate_id=geID,sfr_res_type=1,sfr_res_path=imgUrl,
                                  user_id=paramDicts['sender_id'],SquareGoods_id=paramDicts['sg_id'])
            else:
                SquareFileResouce(evaluate_id=geID,sfr_res_type=4,sfr_res_path=imgUrl,
                                  user_id=paramDicts['sender_id'],SquareGoods_id=paramDicts['sg_id'])
    if imgCounter > 0:#表明评论有图片
        geStatus = 1
    else:
        geStatus = 0
    geObj.save()
    response_data['flag'] = 'ok'
    return response_data
    