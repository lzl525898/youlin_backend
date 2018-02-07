<?php
//电商ID
//defined('EBusinessID') or define('EBusinessID', 1264550);
//电商加密私钥，快递鸟提供，注意保管，不要泄漏
//defined('AppKey') or define('AppKey', 'b408fc33-c715-46af-9620-50430518be86');
//请求url
defined('ReqURL') or define('ReqURL', 'http://api.kdniao.cc/Ebusiness/EbusinessOrderHandle.aspx');

$ShipperArgv = $argv[1]; 
$LogisticArgv = $argv[2];  
$method = $argv[3];
if(isset($method) && $method != ""){  
    echo $method($ShipperArgv,$LogisticArgv);  
}else{  
	echo "500";  
}  

/**
 * Json方式 查询订单物流轨迹
 */
function getOrderTracesByJson($Shipper,$Logistic){
	$requestData= "{'OrderCode':'','ShipperCode':'".$Shipper."','LogisticCode':'".$Logistic."'}";
	$datas = array(
        'EBusinessID' => '1264550',
        'RequestType' => '1002',
        'RequestData' => urlencode($requestData) ,
        'DataType' => '2',
    );
    $datas['DataSign'] = encrypt($requestData, 'b408fc33-c715-46af-9620-50430518be86');
	$result=sendPost(ReqURL, $datas);	
	//根据公司业务处理返回的信息......
	return $result;
}
 
/**
 *  post提交数据 
 * @param  string $url 请求Url
 * @param  array $datas 提交的数据 
 * @return url响应返回的html
 */
function sendPost($url, $datas) {
    $temps = array();	
    foreach ($datas as $key => $value) {
        $temps[] = sprintf('%s=%s', $key, $value);		
    }	
    $post_data = implode('&', $temps);
    $url_info = parse_url($url);
//	if($url_info['port']=='')
//	{
//		$url_info['port']=80;	
//	}
//	echo $url_info['port'];
	$url_info['port']=80;	
    $httpheader = "POST " . $url_info['path'] . " HTTP/1.0\r\n";
    $httpheader.= "Host:" . $url_info['host'] . "\r\n";
    $httpheader.= "Content-Type:application/x-www-form-urlencoded\r\n";
    $httpheader.= "Content-Length:" . strlen($post_data) . "\r\n";
    $httpheader.= "Connection:close\r\n\r\n";
    $httpheader.= $post_data;
    $fd = fsockopen($url_info['host'], $url_info['port']);
    fwrite($fd, $httpheader);
    $gets = "";
	$headerFlag = true;
	while (!feof($fd)) {
		if (($header = @fgets($fd)) && ($header == "\r\n" || $header == "\n")) {
			break;
		}
	}
    while (!feof($fd)) {
		$gets.= fread($fd, 128);
    }
    fclose($fd);  
    
    return $gets;
}

/**
 * 电商Sign签名生成
 * @param data 内容   
 * @param appkey Appkey
 * @return DataSign签名
 */
function encrypt($data, $appkey) {
    return urlencode(base64_encode(md5($data.$appkey)));
}

?>