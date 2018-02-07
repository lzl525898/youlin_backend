
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(document).ready(function(){
	var url = "ajax_address_list?type=1&random=" + Math.random();
	$.getJSON(
		url,
		function(data) {
			if(data.data.page_count == 1 || data.data.list.length ==0) {
				$("#Pagination").hide(); //只有一页的话就不显示分页导航
				show_addess_data(data.data);
			}
			else {
				show_addess_data(data.data);
				update_page_nav(data.data,1);
			}
		}
	);
    
    $('#myTab a').click(function (e) {
      e.preventDefault();//阻止a链接的跳转行为
     
      if($(this).attr("href") == '#yes'){
      	var url = "ajax_address_list?type=2&random=" + Math.random();
      	$.getJSON(
      		url,
      		function(data) {
      			if(data.data.page_count == 1|| data.data.f_list.length ==0) {
      				
      				$("#y_Pagination").hide(); //只有一页的话就不显示分页导航
      				
      				show_f_addess_data(data.data);
      			}
      			else {
      				curr_page = 1;
      				show_f_addess_data(data.data);
      				update_page_nav(data.data,2);
      			}
      		}
      	);
      	
      }
      $(this).tab('show');//显示当前选中的链接及关联的content
    });
    //dialog初始化
	$("#address-form").dialog({
        height: 580,
        width: 500,
        cache: false,
        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
        dialogClass: "my-dialog",
        modal:true,
        buttons: [
         {
             text: '审核'
                     , 'class': 'btn btn-success'
                     , 'type': 'submit'
                     , click: function() {
                		var flag = checkFormData();
        	            if (flag){
        	             	var formData = new FormData($("#address-form")[0]);
        	            	$.ajax({
             					 url:'ajax_address_audit_submit/',
             					 type:'POST',
             					 enctype:'multipart/form-data',
             					 data:formData,
             					 dataType: 'JSON',
             					 processData:false,
             					 contentType:false,
             					 success:function(data){
             						 if (data.code==1){
             							$("#tip").children("font").text(data.desc);
             						 }else{
             							$("#address-form").dialog("close");
                    	        		cleanText();
                    	        		do_page(1);
             						 }
             					 },
             					 
             				 	});
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
	
});


function checkFormData(){
	var status =$("input:radio[name=status]:checked").val();
	if (status == 0){
		if($("#reason").val() == ""){
        	$("#tip").children("font").text("请填写地址未审核通过原因!");
    		return false;
        }
	}else{
		if($("#buildnum_id").val() == 0){
	    	$("#tip").children("font").text("请选择楼栋!");
			return false;
	    }
	    
	    if($("#apt_id").val() == 0){
	    	$("#tip").children("font").text("请选择门牌!");
			return false;
	    }
	}
    return true;
}
function show_addess_data(data) {
	var list = data.list
	$("#notable > thead").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th>ID</th>';
	item_str += '<th>帐号</th>';
	item_str += '<th>所在城市</th>';
	item_str += '<th>所属小区</th>';
	item_str += '<th>具体地址</th>';
	item_str += '<th>验证码</th>';
	item_str += '<th>操作</th>';
	item_str += '</tr>';
	$("#notable > thead").append(item_str);
	
	$("#notable > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.user.user_phone_number + '</td>';
		item_str += '<td>' + item.family_city + '</td>';
		item_str += '<td>' + item.family_community + '</td>';
		item_str += '<td>' + item.family_address + '</td>';
		item_str += '<td>' + item.address_mark + '</td>';
		item_str += '<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" id="btn_audit_' + item.fr_id + '" onclick="audit(this.id)"><i class="icon-pencil"></i> 审核</a></li></ul></div></td>';
		item_str += '</tr>';
		$("#notable > tbody").append(item_str);
	}
	
}

//审核按钮
function audit(data){
	var url = "ajax_fr_data?audit_id="+data+"&random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){ 
			    	$("#city").val(json.data.family_city);
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
	 modDialogCss("my-dialog");
	 $('#address-form').dialog("option","title", "地址审核").dialog('open');
	 return false;
}

function update_page_nav(data,type) {
				
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
				show_addess_data(data.data);
				update_page_nav(data.data,1);
			}else{
				show_f_addess_data(data.data);
				update_page_nav(data.data,2);
			}
			
		}
	);
}

function show_f_addess_data(data) {
	var list = data.f_list;
	$("#yestable > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.user.user_phone_number + '</td>';
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
		$("#yestable > tbody").append(item_str);
	}
	
}
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