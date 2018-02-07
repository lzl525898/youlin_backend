
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_data(data) {
	var list = data.list
	$("#audit > thead").empty();

	//title部分
	var item_str = '<tr>';
	item_str += '<th width="5%">ID</th>';
	item_str += '<th width="15%">用户帐号</th>';
	item_str += '<th width="15%">小区</th>';
	item_str += '<th width="10%">意见类型</th>';
	item_str += '<th width="40%">意见内容</th>';
	item_str += '<th width="15%">时间</th>';
	item_str += '</tr>';
	$("#audit > thead").append(item_str);
	
	$("#audit > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.user_id + '</td>';
		item_str += '<td>' + item.community_id + '</td>';
		item_str += '<td>' + item.opinion_type + '</td>';
		item_str += '<td>' + item.opinion_content + '</td>';
		item_str += '<td>' + item.opinion_time + '</td>';
		item_str += '</tr>';
		$("#audit > tbody").append(item_str);
	}
	
	//处理按钮
	/*$(".btn_del").click(function() {
		if(confirm("确认处理吗？")) {
			var id = $(this).attr("id").split("_")[2];
			$.getJSON(
				"ajax_feedback_del?id=" + id + "&random=" + Math.random(),
				function(data) {
					do_page();
				}
			);
		}
		return false;
	});*/
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
		"ajax_feedback_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_data(data.data);
			update_page_nav(data.data);			
		}
	);
}

$(function() {

	$.getJSON(
		"ajax_feedback_list?random=" + Math.random(),
		function(data) {
			if(data.data.page_count == 1 || data.data.list.length ==0) {
				$("#Pagination").hide(); //只有一页的话就不显示分页导航
				show_data(data.data);
			}
			else {
				show_data(data.data);				
				update_page_nav(data.data);
			}
		}
	);
	
});