//index页面头部右侧地址省略号
var cT = $("#city").text();
	cT = cT.substring(0,3) + "...";
	$("#city").text(cT);
	
	$("#topic,#select").on("click",function(){
		$(".logout").hide();
	})
	
//index页面头部左侧判断是登录了还是没有登录，若是已经登录，则点击显示下拉列表，若未登录，则跳转到登录页面	
	function check(){
		if($("#user").text()!= "登录"){
			$(".logout").toggle();
		}else{
			location.href = "bind.html"
		}
	}
/*	$("#select").on("click",function(){
		$("#devide").toggle();
	})*/
/*	$("#topic,#header").on("click",function(){
		$("#devide").hide();
	})*/
//idnex页面头部下方分类点击下拉列表
/*	$("#select li").on("click",function(){
		var lT = $(this).text();
		$("#select a").text(lT);

	})*/
/*	$("#select li").on("click",function(){
		var lT = $(this).text();
		$("#select a").text(lT);

	})*/
//index页面点赞按钮拖拽和点击效果
$("#checkin").drag();
var checkin = 0;
$("#checkin").on("click",function(){
	$("#checkin").css("background","#ccc");
	if(checkin == 1){
		$("#pop").toggle();
	}else{
		checkin = 1;
		$(".checkinP").css("display","block");
		$(".checkinP").animate({
			"top":"-300%",
			"opacity":"0"
		},3000);
	}
})