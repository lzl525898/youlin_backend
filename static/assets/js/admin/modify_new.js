
$(function() {
	var new_id = get_menu_param("new_id");
	var url = "ajax_new_data?id="+new_id+"&random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){ 
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
		if($.trim(city_id) == 0)
			msg += "请选择城市\n";
		if($.trim(community_id) == 0)
			msg += "请选择所属小区\n";
		if(msg != "")
			alert(msg);
		else {
			 $("#myform").submit(function(){
				 $.ajax({
					 type:'POST',
					 data:$(this).serialize(),
					 url:'ajax_new_mod',
					 success:function(data){
						 $("#center-column").load("../../static/web/admin_templates/news_list.html?random=" + Math.random()); 
					 }
					 
				 });
				 return false;
				 
			 });
		}
		
	});
})

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