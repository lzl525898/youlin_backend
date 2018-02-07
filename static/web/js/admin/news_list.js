
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_data(list) {
	$(".listing > tbody").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th class="first" width="5%"><input type="checkbox" id="SelectAll"/></th>';
	item_str += '<th width="30%">标题</th>';
	item_str += '<th width="15%">城市</th>';
	item_str += '<th width="15%">所属小区</th>';
	item_str += '<th width="15%">添加时间</th>';
	item_str += '<th class="last" width="20%">操作</th>';
	item_str += '</tr>';
	$(".listing > tbody").append(item_str);
	
	for(var i in list) {
		var item = list[i];
		
		item_str = '<tr class="bg">';
		if(item.push_flag == 1){
			item_str += '<td class="first style1"><input type="checkbox" name="subcheck" value="' + item.new_id + '" disabled /><input type="hidden" name="community" value="'+item.community_id+'"/></td>';
		}else{
			item_str += '<td class="first style1"><input type="checkbox" name="subcheck" value="' + item.new_id + '"/><input type="hidden" name="community" value="'+item.community_id+'"/></td>';
		}
		item_str += '<td><a href="./getNews?id='+item.new_id+'" class="show_new" id="show_new_' + item.new_id + '">' + item.new_title + '</a></td>';
		item_str += '<td>' + item.city_name + '</td>';
		item_str += '<td>' + item.community_name + '</td>';
		item_str += '<td>' + item.new_add_time + '</td>';
		if(item.push_flag == 1){
			item_str += '<td class="last">已推送</td>';
		}else{
			item_str += '<td class="last"><a href="#" class="btn_detail" id="btn_modify_' + item.new_id + '">修改</a>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#" class="btn_del" id="btn_del_' + item.new_id + '">删除</a></td>';
		}
		
		item_str += '</tr>';
		$(".listing > tbody").append(item_str);
	}
	
	//删除按钮
	$(".btn_del").click(function() {
		if(confirm("确认删除吗？")) {
			var id = $(this).attr("id").split("_")[2];
			$.getJSON(
				"new_del?id=" + id + "&random=" + Math.random(),
				function(data) {
					do_page();
				}
			);
		}
		return false;
	});
	//修改按钮
	$(".btn_detail").click(function() {
		
		var id = $(this).attr("id").split("_")[2];
		$("#menu_param").val("new_id:" + id);
		$("#center-column").load("../../static/web/admin_templates/modify_new.html?random=" + Math.random());
	});
	$("#SelectAll").click(function(){     
	    if(this.checked){    
	    	 $("input[name='subcheck']").each(function(){
	    		 if(!this.disabled){
	    			 this.checked = true;
	    		 }
	             
	         });    
	    }else{    
	    	$("input[name='subcheck']").each(function(){
	             this.checked = false;
	         });   
	    }     
	});
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
		"ajax_news_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_data(data.list);
			update_page_nav(data);			
		}
	);
}

$(function() {

	$.getJSON(
		"ajax_news_list?random=" + Math.random(),
		function(data) {
			//if(data.page_count == 1) {
			//	$(".pagetable").hide(); //只有一页的话就不显示分页导航
			//	show_data(data.list);
			//}else {
				show_data(data.list);				
				update_page_nav(data);
		   // }
		}
	);
	
	//推送按钮
	$("#add_btn").click(function() {
		
		var ids= [];
		var communityIds = [];
		 $("input[name='subcheck']:checked").each(function(){
			 ids.push($(this).val());
			 communityIds.push($(this).next().val());
         });
		if(ids.length<3){
			alert("每次推送新闻数量不少于3条!");
			return false;
		}
		var new_arr = [];
		for(var i=0;i<communityIds.length;i++){
			var items = communityIds[i];
			if($.inArray(items,new_arr) == -1){
				new_arr.push(items);
				
			}
		}
		if(new_arr.length > 1){
			alert("推送小区不一致!");
			return false;
		}
		$.getJSON(
				"ajax_push_new?ids="+ids+"&community_id="+new_arr[0]+"&random=" + Math.random(),
				function(data) {
					do_page();
				}
			);
		
	});
	
});
