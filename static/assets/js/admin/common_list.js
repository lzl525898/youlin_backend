﻿
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(document).ready(function(){
	var url = "ajax_common_list?type=2&random=" + Math.random();
	$.getJSON(
		url,
		function(data) {
			/*if(data.data.page_count == 1) {
				$(".pagetable").hide(); //只有一页的话就不显示分页导航
				show_common_data(data.data);
			}
			else {*/
				show_common_data(data.data);
				update_page_nav(data.data);
			/*}*/
		}
	);
	
	
	
});

function show_common_data(data) {
	var list = data.list
	$("#audit > thead").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th>ID</th>';
	item_str += '<th>帐号</th>';
	item_str += '<th>所在城市</th>';
	item_str += '<th>所属小区</th>';
	item_str += '<th>加入时间</th>';
	item_str += '</tr>';
	$("#audit > thead").append(item_str);
	
	$("#audit > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.user.user_phone_number + '</td>';
		item_str += '<td>' + item.city.city_name + '</td>';
		item_str += '<td>' + item.community.community_name + '</td>';
		item_str += '<td>' + item.app_time + '</td>';
		item_str += '</tr>';
		$("#audit > tbody").append(item_str);
	}
	
}

function update_page_nav(data) {			
	var opt = {
		callback: function(page_index, jq) {
			curr_page = page_index + 1;
			if(request_data) {
				request_data = false;
				do_page();
			}
			else
				request_data = true;
			return false;
		},
		items_per_page: data.page_size,
		current_page: curr_page - 1,
		num_edge_entries: 1
	};
	
	$("#Pagination").pagination(data.total, opt);
}

function do_page() {
	$.getJSON(
		"ajax_common_list?type=2&page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
}

function audit(){
	var url = "ajax_city_data?random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){    
		            $("#a_city_id").empty();
		        	item_str = '<option value="0">请选择城市</option>';
		        	for(i=0;i<json.length;i++){ 
		        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
		        	}
		        	$("#a_city_id").append(item_str);
			    }      
	});
	 initDialog();
	 modDialogCss("common-dialog");
 	 $('#admin-form').dialog("option","title", "管理员审核").dialog('open');
	 return false; 
      
}

function initDialog(){
	
	$("#admin-form").dialog({
        height: 300,
        width: 550,
        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框
        'class': "common-dialog",  /*add custom class for this dialog*/
        dialogClass: "common-dialog",
        modal:true,
        buttons: [
          {
              text: '审核'
                      , 'class': 'btn btn-success'
                      , 'type': 'submit'
                      , click: function() {
                      	var city_id =$("#a_city_id").val();
                      	var community_id =$("#a_community_id").val();
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
                      		alert("请选择待选管理员!");
                      		return false;
                      	}
                      	 $.ajax({     
                      	        type: "GET",     
                      	        url: "ajax_common_submit?city_id="+ city_id + "&community_id="+ community_id + "&user_id="+ user_id + "&random=" + Math.random(),     
                      	        dataType:   "json",     
                      	        success: function(data){  
                      	        	if (data.code==1){
              							$("#tip").children("font").text(data.desc);
              						 }else{
              							$("#admin-form").dialog("close");
                     	        		cleanText();
                     	        		do_page();
              						 }
                      	        }      
                      	 })
              }//end of create click
          }, 
          {
              text: "取消"
                      , 'class': "btn btn-primary"
                      , click: function() {
		                        $(this).dialog("close");
		                        cleanText();
              }
          }//end of 新建
      ]
  });
}



function getCommunityOptions(id){
	//获取community
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_community_data?city_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#a_community_id").empty();
	        	item_str = '<option value="0">请选择小区</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#a_community_id").append(item_str);
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

