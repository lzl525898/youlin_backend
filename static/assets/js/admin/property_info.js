
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_data(data) {
	var list = data.list
	$("#audit > thead").empty();

	//title部分
	var item_str = '<tr>';
	item_str += '<th width="5%">ID</th>';
	item_str += '<th width="12%">物业名称</th>';
	item_str += '<th width="10%">联系电话</th>';
	item_str += '<th width="18%">地址</th>';
	item_str += '<th width="15%">办公时间</th>';
	item_str += '<th width="10%">所属城市</th>';
	item_str += '<th width="18%">所属小区</th>';
	item_str += '<th width="12%">操作</th>';
	item_str += '</tr>';
	$("#audit > thead").append(item_str);
	
	$("#audit > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.name + '</td>';
		item_str += '<td>' + item.phone + '</td>';
		item_str += '<td>' + item.address + '</td>';
		item_str += '<td>' + item.office_hours + '</td>';
		item_str += '<td>' + item.city_id + '</td>';
		item_str += '<td>' + item.community_id + '</td>';
		item_str += '<td><a href="#" id="edit_' + item.info_id + '" onclick="edit(this.id)"><i class="icon-edit"></i> 修改</a>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#" id="del_' + item.info_id + '" onclick="delProperty(this.id);"><i class="icon-remove"></i> 删除</a></td>';
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
		"ajax_property_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_data(data.data);
			update_page_nav(data.data);			
		}
	);
}

$(function() {

	$.getJSON(
		"ajax_property_list?random=" + Math.random(),
		function(data) {
			/*if(data.data.page_count == 1 || data.data.list.length ==0) {
				$("#Pagination").hide(); //只有一页的话就不显示分页导航
				show_data(data.data);
			}
			else {*/
				show_data(data.data);				
				update_page_nav(data.data);
			/*}*/
		}
	);
	
	 $("#info-form").dialog({
	        height: 480,
	        width: 500,
	        cache: false,
	        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
	        'class' : "info-dialog", /*add custom class for this dialog*/
	        dialogClass: "info-dialog",
	        modal:true,
            buttons: [
             {
                 text: '提交'
                         , 'class': 'btn btn-success'
                         , 'type': 'submit'
                         , click: function() {
                         	
                            flag = createFormData();
                            if (flag){
                            	var formData = $("#info-form").serializeArray();
                            	 $.ajax({     
                             	        type: "GET", 
                             	        data:formData,
                             	        url: "ajax_property_submit",     
                             	        dataType:   "json",     
                             	        success: function(data){  
                             	        	if (data.code==1){
    	              							$("#tip").children("font").text(data.desc);
    	              						 }else{
    	              							$("#info-form").dialog("close");
    	                     	        		cleanText();
    	                     	        		do_page();
    	              						 }
                             	        }      
                             	 })
                            }
                         	
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
	
});
//删除按钮
function delProperty(id){
	var id = id.split("_")[1];
	if (confirm('你真的打算删除该物业信息吗?')){
		$.getJSON(
				"ajax_property_del?id="+id+"&random=" + Math.random(),
				function(data) {
					if (data.code == 1){
						alert(data.desc);
					}
					do_page();
				}
			);
	}
	
}
function audit(data){
	$("#idstr").val(0);
	var url = "ajax_city_data?random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){    
		            $("#i_city_id").empty();
		        	item_str = '<option value="0">请选择城市</option>';
		        	for(i=0;i<json.length;i++){ 
		        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
		        	}
		        	$("#i_city_id").append(item_str);
		        	
		        	$("#i_community_id").empty();
			        item_str2 = '<option value="0">请选择小区</option>';
			        $("#i_community_id").append(item_str2);
			    	
			    	modDialogCss("info-dialog");
			    	$('#info-form').dialog("option","title", "添加物业信息").dialog('open');
		        	
			    }      
	});

	return false;
}

function edit(idstr){
	v_id = idstr.split('_')[1];
	$("#idstr").val(v_id);
	var url = "ajax_getPropertyInfoById?id="+idstr+"&random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){   
			    	$("#name").val(json.data.p_data.name);
			    	$("#phone").val(json.data.p_data.phone);
			    	$("#address").val(json.data.p_data.address);
			    	$("#office_hours").val(json.data.p_data.office_hours);
			    	$("#i_city_id").empty();
			    	item_str = '<option value="0">请选择城市</option>';
		        	var list = json.data.city_list;
		        	for(i=0;i<list.length;i++){ 
		        		if(json.data.city_id == list[i].text){
		        			item_str += '<option value="'+list[i].text+'" selected="selected">'+list[i].label+'</option>';
		        		}else{
		        			item_str += '<option value="'+list[i].text+'">'+list[i].label+'</option>';
		        		}
		        		
		        	}
		        	$("#i_city_id").append(item_str);
		        	$("#i_community_id").empty();
		        	item_community = '<option value="0">请选择小区</option>';
		        	var community_list = json.data.community_list;
		        	for(i=0;i < community_list.length;i++){ 
		        		if(json.data.community_id == community_list[i].text){
		        			item_community += '<option value="'+community_list[i].text+'" selected="selected">'+community_list[i].label+'</option>';
		        		}else{
		        			item_community += '<option value="'+community_list[i].text+'">'+community_list[i].label+'</option>';
		        		}
		        		
		        	}
		        	$("#i_community_id").append(item_community);
		       	 	modDialogCss("info-dialog");
		       	 	$('#info-form').dialog("option","title", "修改物业信息").dialog('open');
			    }      
	 });

	 return false;
}
function getCommunityOptions(id){
	//获取community
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_community_data?city_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#i_community_id").empty();
	        	item_str = '<option value="0">请选择小区</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#i_community_id").append(item_str);
	        }      
	 })
}

/*function checkForm(){
	var name =$("#name").val();
 	var phone =$("#phone").val();
 	var address =$("#address").val();
 	var office_hours =$("#office_hours").val();
 	var community_id =$("#i_community_id").val();
 	var city_id =$("#i_city_id").val();
 	var random = Math.random();
    var ok1=false;
    var ok2=false;
    var ok3=false;
    var ok4=false;
    var ok5=false;
    var ok6=false;
    // 验证用户名
    if(name.length <=20 && name!=''){
        ok1=true;
    }
    if(phone.length <=15 && phone!=''){
        ok2=true;
    }
    if(address.length <=50 && address!=''){
        ok3=true;
    }
    if(office_hours.length <=50 && office_hours!=''){
        ok4=true;
    }
    if(community_id>0&& community_id!=''){
        ok5=true;
    }
    if(city_id >0 && city_id!=''){
        ok6=true;
    }
	var data = {
			name:name,
			phone:phone,
			address:address,
			office_hours:office_hours,
			community_id:community_id,
			city_id:city_id,
			idstr:city_id,
			random: random
     }
    if (ok1&ok2&ok3&ok4&ok5&ok6){
    	return data;
    }else{
    	return false;
    }	
}*/

function createFormData(){
    if ($("#name").val() == "" || $("#name").val().length >20) {
    	$("#tip").children("font").text("物业名称不能为空,且最多输入20个字符!");
		return false;
    }
    
    if (isNaN($("#phone").val()) || ($("#phone").val() == "")) {
    	$("#tip").children("font").text("联系电话输入数字形式!");
		return false;
    }
    
    if ($("#address").val() == "" || $("#address").val().length >50) {
    	$("#tip").children("font").text("地址不能为空，且最多输入50个字符!");
		return false;
    }
    
    if ($("#office_hours").val() == "" || $("#office_hours").val().length >50) {
    	$("#tip").children("font").text("办公时间不能为空，且最多输入50个字符!");
		return false;
    }
    if($("#i_community_id").val() == 0){
    	$("#tip").children("font").text("请选择小区!");
		return false;
    }
    if($("#i_city_id").val() == 0){
    	$("#tip").children("font").text("请选择城市!");
		return false;
    }
    return true;
	
}