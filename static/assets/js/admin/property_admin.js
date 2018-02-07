
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(function() {
	
	var url = "ajax_audit_list?type=4&random=" + Math.random();
	$.getJSON(
		url,
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
	
	$("#propertyForm").dialog({
	        height: 600,
	        width: 550, 
	        cache: false,
	        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
	        'class' : "propertyForm-dialog", /*add custom class for this dialog*/
            dialogClass: "propertyForm-dialog",
            modal:true,
            buttons: [
             {
                 text: '添加'
                         , 'class': 'btn btn-success'
                         , 'type': 'submit'
                         , click: function() {
                         	 var formData = $("#propertyForm").serializeArray();
                         	 
                         	 if (mobileCheck() && passwordCheck()){
                         		$.ajax({     
                         	        type: "GET",     
                         	        url: "ajax_audit_submit?random=" + Math.random(),     
                         	        dataType:   "json",   
                         	        data:formData,
                         	        success: function(json){  
                         	        	if(json.code == 1){
                         	        		$("#tip").children("font").text(json.desc);
                         	        	}else{
	              							$("#propertyForm").dialog("close");
	                     	        		cleanText();
	                     	        		do_page();
	              						 }
                         	        }      
                         		}) 
                         		 
                         	 }
                         	 return false;
                         	 
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
	
	$("#showDialog").on("click", function (e) {
		var url = "ajax_city_data?random="+ Math.random();
		$.ajax({     
				    type: "GET",     
				    url: url,     
				    dataType:   "json",     
				    success: function(json){    
			            $("#p_city_id").empty();
			        	item_str = '<option value="0">请选择城市</option>';
			        	for(i=0;i<json.length;i++){ 
			        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
			        	}
			        	$("#p_city_id").append(item_str);
				    }      
		});
		modDialogCss("propertyForm-dialog");
		$('#propertyForm').dialog("option","title", "添加物业管理员").dialog('open');
		/*cleanBootscrapModal();
		$(".modal-title").text("添加物业管理员");
		$('#propertyForm').dialog('open');*/
		return false;
	});
	
	$("#btn_modify").on("click", function (e) {
		var url = "ajax_city_data?random="+ Math.random();
		$.ajax({     
				    type: "GET",     
				    url: url,     
				    dataType:   "json",     
				    success: function(json){    
			            $("#p_city_id").empty();
			        	item_str = '<option value="0">请选择城市</option>';
			        	for(i=0;i<json.length;i++){ 
			        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
			        	}
			        	$("#p_city_id").append(item_str);
				    }      
		});
		$('#propertyForm').dialog("option","title", "修改物业管理员").dialog('open');
		return false;
	});
	
	
	$("a[class='btn_del']").on("click", function (e) {
		alert("999");
		var url = "ajax_city_data?random="+ Math.random();
		$.ajax({     
				    type: "GET",     
				    url: url,     
				    dataType:   "json",     
				    success: function(json){    
			            $("#p_city_id").empty();
			        	item_str = '<option value="0">请选择城市</option>';
			        	for(i=0;i<json.length;i++){ 
			        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
			        	}
			        	$("#p_city_id").append(item_str);
				    }      
		});
		$('#propertyForm').dialog("option","title", "修改物业管理员").dialog('open');
		return false;
	});
	
	
});

function show_common_data(data) {
	var list = data.list
	$("#audit > thead").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th>ID</th>';
	item_str += '<th>帐号</th>';
	item_str += '<th>昵称</th>';
	item_str += '<th>所在城市</th>';
	item_str += '<th>所属小区</th>';
	item_str += '<th>添加时间</th>';
	item_str += '<th>操作</th>';
	item_str += '</tr>';
	$("#audit > thead").append(item_str);
	
	$("#audit > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.user.user_phone_number + '</td>';
		item_str += '<td>' + item.user.user_nick + '</td>';
		item_str += '<td>' + item.city.city_name + '</td>';
		item_str += '<td>' + item.community.community_name + '</td>';
		item_str += '<td>' + item.app_time + '</td>';
		item_str += '<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" class="btn_modify" id="btn_modify_' + item.gl_id + '"><span id="btn_modify"><i class="icon-edit"></i>修改</span></a></li><li><a href="#" class="btn_del" id="btn_del_' + item.gl_id + '"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
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
		"ajax_audit_list?type=4&page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
}

function getCommunityOptions(id){
	//获取community
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_community_data?city_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#p_community_id").empty();
	        	item_str = '<option value="0">请选择小区</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#p_community_id").append(item_str);
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


function mobileCheck(){
	var pattern=/^1\d{10}$/;
	var mobile=$("#user_phone").val();
	if(mobile.search(pattern)){
		$("#tip").children("font").text("手机号码必须是11位数字,格式不正确!");
		return false;
	}
	return true;
}
function passwordCheck(){
	var password=$("#user_password").val();
	var repassword=$("#repassword").val();
	if (password.length>16 || password.length<6){
		$("#tip").children("font").text("密码长度在6-16位!");
		return false;
	}
	if(password!=repassword){
		$("#tip").children("font").text("两次输入密码不一致");
		return false;
	}
	
	return true;
}

function cleanBootscrapModal(){
	$(".modal-title").empty();  
	$(".modal-footer").css("text-align","center");
	$(".close").hide();
}

