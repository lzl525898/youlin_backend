
$(function() {
	var new_id = get_menu_param("new_id");
	
	if (new_id == null){//添加
		$("#newsId").val(0);
		var url = "ajax_city_data?random="+ Math.random();
		$.ajax({     
				    type: "GET",     
				    url: url,     
				    dataType:   "json",     
				    success: function(json){
				    	$(".page-header").html("<h1>添加<small>新闻</small></h1>");
			            $("#city_id").empty();
			        	item_str = '<option value="0">请选择城市</option>';
			        	for(i=0;i<json.length;i++){ 
			        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
			        	}
			        	$("#city_id").append(item_str);
				    }      
		});
	}else{ //修改
		$("#menu_param").val("");
		$("#newsId").val(new_id);
		var url = "ajax_new_data?id="+new_id+"&random="+ Math.random();
		$.ajax({     
				    type: "GET",     
				    url: url,     
				    dataType:   "json",     
				    success: function(json){ 
				    	$(".page-header").html("<h1>修改<small>新闻</small></h1>");
				    	$("#title").val(json.data.new_title);
				    	$("#source").val(json.data.new_source);
				    	$("#introduce").val(json.data.new_introduce);
				    	setContext(json.data.new_content);
				    	$('input[name="pri_flag"]').each(function(){
				    		if ($(this).attr("value") == json.data.pri_flag){
				    			$(this).attr("checked","checked");
				    		}else{
				    			$(this).removeAttr("checked");
				    		}
						});
				    	item_str = '<option value="0">请选择城市</option>';
			        	var list = json.data.city_list;
			        	for(i=0;i<list.length;i++){ 
			        		if(json.data.city_id == list[i].text){
			        			item_str += '<option value="'+list[i].text+'" selected="selected">'+list[i].label+'</option>';
			        		}else{
			        			item_str += '<option value="'+list[i].text+'">'+list[i].label+'</option>';
			        		}
			        		
			        	}
			        	$("#city_id").append(item_str);
			        	$("#new_id").attr("value",json.data.new_id)
			        	item_community = '';
			        	var community_list = json.data.community_list;
			        	for(i=0;i < community_list.length;i++){ 
			        		if(json.data.community_id == community_list[i].text){
			        			item_community += '<option value="'+community_list[i].text+'" selected="selected">'+community_list[i].label+'</option>';
			        		}else{
			        			item_community += '<option value="'+community_list[i].text+'">'+community_list[i].label+'</option>';
			        		}
			        		
			        	}
			        	$("#community_id").append(item_community);
				    }      
				});
		
	}

	
	$("#csrftoken").attr("value",getCookie("csrftoken"))
	
	$("#btn_submit").click(function() {
		
		var title = $("#title").val();

		var content = getContext();
		var small_pic = $("#small_pic").val();
		var city_id  = $("#city_id").val();
		var community_id = $("#community_id").val();
		var msg = "";
		if($.trim(title) == "")
			msg += "标题不能为空\n";
		if(content == "")
			msg += "正文不能为空\n";
		if (!($("#newsId").val())){
			if($.trim(small_pic) == "")
				msg += "请选择要上传的图片\n";
		}
		
		if($.trim(city_id) == 0)
			msg += "请选择城市\n";
		if($.trim(community_id) == 0)
			msg += "请选择所属小区\n";
		if(msg != ""){
			alert(msg);
			return false;
		}else {
			$("#myform").submit(function(){
				var formData = new FormData($("#myform")[0]);
				$.ajax({
					 url:'ajax_new_submit',
					 type:'POST',
					 enctype:'multipart/form-data',
					 data:formData,
					 processData:false,
					 contentType:false,
					 success:function(data){
						 $(".main-content").load("../../static/assets/templates/newList.html?random=" + Math.random());
					 },
					 
				 });
				 return false;
			 
		 });
			 //$("#myform").attr("action","ajax_new_submit").submit();
		}
		
	});
	
});



function getCookie(name){ 
	var strCookie=document.cookie; 
	var arrCookie=strCookie.split("; "); 
	for(var i=0;i<arrCookie.length;i++){ 
		var arr=arrCookie[i].split("="); 
		if(arr[0]==name)return arr[1]; 
	} 
	return ""; 
}

function get_menu_param(name) {
	
	var param_str = $("#menu_param").val();
	
	if(!param_str || param_str == "")
		return null;
	
	var param = null;
	
	if(param_str.indexOf(",") > -1) {
		var params = param_str.split(",");
		for(var i in params) {
			param = params[i].split(":");
			
			if(param[0] == name)
				return param[1];
		}		
	}
	else {
		param = param_str.split(":");
		if(param[0] == name)
			return param[1];
	}
	return null;
}