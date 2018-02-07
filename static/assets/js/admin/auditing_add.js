
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

function getUserOptions(id){
	//获取user
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_user_data?community_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#user_id").empty();
	        	item_str = '<option value="0">请选择</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#user_id").append(item_str);
	        }      
	 })
}
function audit_submit(){
	var city_id =$("#city_id").val();
	var community_id =$("#community_id").val();
	var user_id =$("#user_id").val();
	if(city_id ==0){
		alert("请选择城市!");
		return false;
	}
	if(community_id ==0){
		alert("请选择小区!");
		return false;
	}
	if(user_id == 0){
		alert("请选择待选物业管理员!");
		return false;
	}
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_audit_submit?city_id="+ city_id + "&community_id="+ community_id + "&user_id="+ user_id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	if(json.flag == 'ok'){
	        		$("#center-column").load("../../static/web/admin_templates/property_admin.html?random=" + Math.random());
	        	}
	        }      
	 })
}

