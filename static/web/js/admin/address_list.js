
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_addess_data(list) {
	$(".listing > tbody").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th class="first" width="20%">申请人手机号</th>';
	item_str += '<th  width="12%">城市</th>';
	item_str += '<th  width="12%">小区</th>';
	item_str += '<th  width="35%">具体地址</th>';
	item_str += '<th  width="10%">验证码</th>';
	item_str += '<th class="last">操作</th>';
	item_str += '</tr>';
	$(".listing > tbody").append(item_str);
	
	for(var i in list) {
		var item = list[i];
		item_str = '<tr class="bg">';
		item_str += '<td class="first style1">' + item.user.user_phone_number + '</td>';
		item_str += '<td>' + item.family_city + '</td>';
		item_str += '<td>' + item.family_community + '</td>';
		item_str += '<td>' + item.family_address+ '</td>';
		item_str += '<td>' + item.address_mark+ '</td>';
		item_str += '<td class="last"><a href="#" class="btn_audit" id="btn_audit_' + item.fr_id + '" onclick="addess_audit(this.id);">审核</a></td>';
		item_str += '</tr>';
		$(".listing > tbody").append(item_str);
	}
	
}

//审核按钮
function addess_audit(id) {
	$("#menu_param").val("audit_id:" + id);
	 $("#center-column").load("../../static/web/admin_templates/address_audit.html?random=" + Math.random());
	
}

function update_page_nav(data,type) {
				
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
				do_page(type);
			}
			else
				request_data = true;
			return false;
		},
		items_per_page: data.page_size,
		current_page: curr_page - 1,
		num_edge_entries: 1
	};
	if(type == 1){
		$("#Pagination").pagination(data.total, opt);
		
	}else{
		$("#y_Pagination").pagination(data.total, opt);
	}
	
}

function do_page(type) {
	$.getJSON(
		"ajax_address_list?type=" + type + "&page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			if(type == 1){
				show_addess_data(data.data.list);
				update_page_nav(data.data,1);
			}else{
				show_f_addess_data(data.data.f_list);
				update_page_nav(data.data,2);
			}
			
		}
	);
}

$(function() {

	var url = null;
	if(get_menu_param("page")) {
		curr_page = get_menu_param("page");
		url = "ajax_address_list?type=1&page=" + get_menu_param("page") + "&random=" + Math.random();
	}else{
		url = "ajax_address_list?type=1&random=" + Math.random();
	}

	$.getJSON(
		url,
		function(data) {
			if(data.data.page_count == 1) {
				
				$(".pagetable").hide(); //只有一页的话就不显示分页导航
				
				show_addess_data(data.data.list);
			}
			else {
				show_addess_data(data.data.list);
				update_page_nav(data.data,1);
			}
		}
	);
	
});



$(document).ready(function() {  
  
    //Default Action  
    $(".tab_content").hide(); //Hide all content  
    $("ul.tabs li:first").addClass("active").show(); //Activate first tab  
    $(".tab_content:first").show(); //Show first tab content  
      
    //On Click Event  
    $("ul.tabs li").click(function() {  
        $("ul.tabs li").removeClass("active"); //Remove any "active" class  
        $(this).addClass("active"); //Add "active" class to selected tab  
        $(".tab_content").hide(); //Hide all tab content  
        var activeTab = $(this).find("a").attr("href"); //Find the rel attribute value to identify the active tab + content  
        $(activeTab).fadeIn(); //Fade in the active content
        if(activeTab == '#tab4'){
        	var url = null;
        	if(get_menu_param("page")) {
        		curr_page = get_menu_param("page");
        		url = "ajax_address_list?type=2&page=" + get_menu_param("page") + "&random=" + Math.random();
        	}else{
        		url = "ajax_address_list?type=2&random=" + Math.random();
        	}

        	$.getJSON(
        		url,
        		function(data) {
        			if(data.data.page_count == 1) {
        				
        				$(".pagetable").hide(); //只有一页的话就不显示分页导航
        				
        				show_f_addess_data(data.data.f_list);
        			}
        			else {
        				show_f_addess_data(data.data.f_list);
        				update_page_nav(data.data,2);
        			}
        		}
        	);
        	
        }
        
        return false;  
    });  
  
}); 

function show_f_addess_data(list) {
	$(".y_listing > tbody").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th class="first" width="20%">申请人手机号</th>';
	item_str += '<th  width="12%">城市</th>';
	item_str += '<th  width="12%">小区</th>';
	item_str += '<th  width="35%">具体地址</th>';
	item_str += '<th  width="10%">验证码</th>';
	item_str += '<th class="last">审核状态</th>';
	item_str += '</tr>';
	$(".y_listing > tbody").append(item_str);
	
	for(var i in list) {
		var item = list[i];
		item_str = '<tr class="bg">';
		item_str += '<td class="first style1"><a>' + item.user.user_phone_number + '</a></td>';
		item_str += '<td>' + item.family_city + '</td>';
		item_str += '<td>' + item.family_community + '</td>';
		item_str += '<td>' + item.family_address+ '</td>';
		item_str += '<td>' + item.address_mark+ '</td>';
		if(item.entity_type == 1 ){
			item_str += '<td>通过</td>';	
		}else{
			item_str += '<td>未通过</td>';
			
		}
		item_str += '</tr>';
		$(".y_listing > tbody").append(item_str);
	}
	
}
