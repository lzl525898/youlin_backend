
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_common_data(list) {
	$(".listing > tbody").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th class="first" width="20%">管理员手机号</th>';
	item_str += '<th  width="15%">城市</th>';
	item_str += '<th  width="15%">小区</th>';
	//item_str += '<th  width="35%">具体地址</th>';
	//item_str += '<th class="last">操作</th>';
	item_str += '<th  width="15%" class="last">加入时间</th>';
	item_str += '</tr>';
	$(".listing > tbody").append(item_str);
	
	for(var i in list) {
		var item = list[i];
		item_str = '<tr class="bg">';
		item_str += '<td class="first style1">' + item.user.user_phone_number + '</td>';
		item_str += '<td>' + item.city.city_name + '</td>';
		item_str += '<td>' + item.community.community_name + '</td>';
		item_str += '<td>' + item.app_time + '</td>';
		//item_str += '<td>' + item.family_address+ '</td>';
		//item_str += '<td class="last"><a href="#" class="btn_audit" id="btn_audit_' + item.fr_id + '" onclick="addess_audit(this.id);">审核</a></td>';
		item_str += '</tr>';
		$(".listing > tbody").append(item_str);
	}
	
}

function update_page_nav(data) {
				
	if(get_menu_param("page")) {
		//获取了当前页后，需要把已保存的当前页删除
		curr_page = get_menu_param("page");
		$("#menu_param").val("type:" + get_menu_param("type"));
	}
	
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
		"ajax_common_list?type=" + get_menu_param("type") + "&page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data.list);
			update_page_nav(data.data);
		}
	);
}

$(function() {
	var url = null;
	if(get_menu_param("page")) {
		curr_page = get_menu_param("page");
		url = "ajax_common_list?type=" + get_menu_param("type") + "&page=" + get_menu_param("page") + "&random=" + Math.random();
	}else{
		url = "ajax_common_list?type=" + get_menu_param("type") + "&random=" + Math.random();
	}
	$.getJSON(
		url,
		function(data) {
			if(data.data.page_count == 1) {
				
				$(".pagetable").hide(); //只有一页的话就不显示分页导航
				
				show_common_data(data.data.list);
			}
			else {
				show_common_data(data.data.list);
				update_page_nav(data.data);
			}
		}
	);
	//添加按钮
	$("#add_btn").click(function() {
		$("#menu_param").val("type:" + get_menu_param("type"));
		
		$("#center-column").load("../../static/web/admin_templates/common_audit.html?random=" + Math.random());
		
	});
	
});
