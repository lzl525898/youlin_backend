
$(function() {
	var audit_id = get_menu_param("audit_id");
	var url = "ajax_fr_data?audit_id="+audit_id+"&random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){ 
			    	$("#city").val(json.data.family_city);
			    	//$("#city_id").val(json.data.family_city_id);
			    	//$("#city_code").val(json.data.city_code);
			    	$("#community").val(json.data.family_community);
			    	$("#community_id").val(json.data.family_community_id);
			    	$("#family_address").text(json.data.family_address);
			    	$("#fr_id").val(json.data.fr_id);
		            $("#block_id").empty();
		        	item_str = '<option value="0">请选择区域</option>';
		        	var list = json.data.block_list;
		        	for(i=0;i<list.length;i++){ 
		        		item_str += '<option value="'+list[i].text+'">'+list[i].label+'</option>';
		        	}
		        	$("#block_id").append(item_str);
		        	$("#buildnum_id").empty();
		        	item_str = '<option value="0">请选择楼栋</option>';
		        	var building_list = json.data.building_list;
		        	for(i=0;i<building_list.length;i++){ 
		        		item_str += '<option value="'+building_list[i].text+'">'+building_list[i].label+'</option>';
		        	}
		        	$("#buildnum_id").append(item_str);
		        	$("#apt_id").empty();
		        	item_str = '<option value="0">请选择门牌</option>';
		        	$("#apt_id").append(item_str);
			    }      
			});
})


function getAptOptions(id){
	//获取Apt
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_apt_data?buildnum_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#apt_id").empty();
	        	item_str = '<option value="0">请选择门牌</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#apt_id").append(item_str);
	        }      
	 })
}
function audit_submit(){
	var community_id =$("#community_id").val();
	var block_id =$("#block_id").val();
	var buildnum_id =$("#buildnum_id").val();
	var apt_id =$("#apt_id").val();
	var fr_id =$("#fr_id").val();
	var status =$("input:radio[name=status]:checked").val();
	 $.ajax({     
	        type: "GET",     
	        //url: "ajax_address_audit_submit?city_id="+city_id+"&community_id="+ community_id + "&block_id="+ block_id + "&buildnum_id="+buildnum_id+"&apt_id="+apt_id+"&city_code="+city_code+"&fr_id="+fr_id+"&status="+status+"&random=" + Math.random(),     
	        url: "ajax_address_audit_submit?community_id="+ community_id + "&block_id="+ block_id + "&buildnum_id="+buildnum_id+"&apt_id="+apt_id+"&fr_id="+fr_id+"&status="+status+"&random=" + Math.random(),  
	        dataType:   "json",     
	        success: function(json){  
	        	if(json.flag == 'ok'){
	        		$("#center-column").load("../../static/web/admin_templates/address_list.html?random=" + Math.random());
	        	}
	        	if(json.flag == 'error'){
	        		alert("请选择楼栋,门牌");
	        		
	        	}
	        }      
	 })
}

