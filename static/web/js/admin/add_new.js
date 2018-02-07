
$(function() {
	var url = "ajax_city_data?random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){    
		            $("#city_id").empty();
		        	item_str = '<option value="0">请选择城市</option>';
		        	for(i=0;i<json.length;i++){ 
		        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
		        	}
		        	$("#city_id").append(item_str);
			    }      
	});
	
	$("#csrftoken").attr("value",getCookie("csrftoken"))
	
	$("#btn_submit").click(function() {
		
		var title = $("#title").val();
		var introduce = $("#introduce").val();
		var content = getContext();
		var small_pic = $("#small_pic").val();
		var city_id  = $("#city_id").val();
		var community_id = $("#community_id").val();
		var msg = "";
		if($.trim(title) == "")
			msg += "标题不能为空\n";
		if($.trim(introduce) == "")
			msg += "摘要不能为空\n";
		
		if(content == "")
			msg += "正文不能为空\n";
		if($.trim(small_pic) == "")
			msg += "请选择要上传的图片\n";
		if($.trim(city_id) == 0)
			msg += "请选择城市\n";
		if($.trim(community_id) == 0)
			msg += "请选择所属小区\n";
		if(msg != "")
			alert(msg);
		else {
			
		/*	$("#myform").submit(function(){
				 $.ajax({
					 type:'POST',
					 enctype:'multipart/form-data',
					 data:$(this).serialize(),
					 url:'ajax_new_submit',
					 success:function(data){
						 $("#center-column").load("../../static/web/admin_templates/news_list.html?random=" + Math.random());
					 },
					 
				 });
				 return false;
				 
			 });*/
			 $("#myform").attr("action","ajax_new_submit").submit();
		}
		
	});
	
});

function getCommunityOptions(id){
	//获取community
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_community_data?city_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#community_id").empty();
	        	item_str = '<option value="0">请选择小区</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#community_id").append(item_str);
	        }      
	 })
}

function getCookie(name){ 
	var strCookie=document.cookie; 
	var arrCookie=strCookie.split("; "); 
	for(var i=0;i<arrCookie.length;i++){ 
		var arr=arrCookie[i].split("="); 
		if(arr[0]==name)return arr[1]; 
	} 
	return ""; 
}