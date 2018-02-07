
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_data(list) {
	
	
	$("#listtable > thead").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th width="5%"><input type="checkbox" name="SelectAll" onclick="selectAll(this);"/></th>';
	item_str += '<th width="35%">标题</th>';
	item_str += '<th width="10%">作者</th>';
	item_str += '<th width="10%">头像</th>';
	item_str += '<th width="15%">添加时间</th>';
	item_str += '<th width="12%">操作</th>';
	item_str += '</tr>';
	$("#listtable > thead").append(item_str);
	$("#listtable > tbody").empty();
	for(var i in list) {
		var item = list[i];
		
		item_str = '<tr class="list-users">';
		if(item.yl_flag == "是"){
			item_str += '<td><input type="checkbox" name="subcheck" value="' + item.yl_id + '" disabled /></td>';
		}else{
			item_str += '<td><input type="checkbox" name="subcheck" onclick="singleChk();"value="' + item.yl_id + '"/></td>';
		}
		item_str += '<td><a href="../content?id='+item.yl_id+'" class="show_new" id="show_new_' + item.yl_id + '">' + item.yl_title + '</a></td>';
		item_str += '<td>' + item.yl_author + '</td>';
		item_str += '<td>' + item.yl_avatar + '</td>';
		item_str += '<td>' + item.yl_date + '</td>';
		if(item.yl_flag == "是"){
			item_str += '<td><span class="label label-success">已发布</span></td>';
		}else{
			item_str += '<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" class="btn_detail" id="btn_modify_' + item.yl_id + '"><i class="icon-edit"></i>修改</a></li><li><a href="#" class="btn_del" id="btn_del_' + item.yl_id + '"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
		}
		
		item_str += '</tr>';
		$("#listtable > tbody").append(item_str);
	}
	
	//删除按钮
	$(".btn_del").click(function() {
		if(confirm("确认删除吗？")) {
			var id = $(this).attr("id").split("_")[2];
			$.getJSON(
				"ajax_life_del?id=" + id + "&random=" + Math.random(),
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
		$("#menu_param").val("yl_id:" + id);
		//$("#center-column").load("../../static/web/admin_templates/modify_new.html?random=" + Math.random());
		$(".main-content").load("../../static/assets/templates/add_life.html?random=" + Math.random());
	});
} 

function selectAll(obj){
	if(obj.checked){    
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
}

function singleChk(){ 
    var chknum = $("input[name='subcheck']").not("input:disabled").size();//未失效的input标签个数
    var chk = 0; 
    $("input[name='subcheck']").not("input:disabled").each(function () {  
    	if (this.checked == true){
            chk++; 
    	}
    }); 
    if(chknum == chk){//全选 
    	$("input[name='SelectAll']").each(function () {  
    		 this.checked = true;
    	}); 
    }else{//不全选 
   	 	$("input[name='SelectAll']").each(function () {  
   	 		this.checked = false;
   	 	}); 
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
		"ajax_life_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_data(data.list);
			update_page_nav(data);			
		}
	);
}

$(function() {

	$.getJSON(
		"ajax_life_list?random=" + Math.random(),
		function(data) {
				show_data(data.list);				
				update_page_nav(data);
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
	
	

	
	$("#release").on("click", function (e) {
		var ids= [];
		$("input[name='subcheck']:checked").each(function(){
			 ids.push($(this).val());
         });
		if (ids && ids.length == 0){
			alert("请选择需要发布的内容!");
			return false;
		}
		if(confirm("确认发布以下内容供前台显示吗？")) {

			$.getJSON(
				"ajax_life_release?ids=" + ids + "&random=" + Math.random(),
				function(data) {
					do_page();
				}
			);
		}
		return false;
	});
	
});

function addNew(){
    var temp = "add_life";
	$.ajax({     
	        type: "GET",     
	        url: "index?random=" + Math.random(),     
	        dataType: "html",  
	        data:{"action":temp},
	        success: function(data){  
	        	$(".main-content").html(data);
	        },
	});
	
}