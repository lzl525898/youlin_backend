
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(function() {
	var url = "ajax_version_list?random=" + Math.random();
	$.getJSON(
		url,
		function(data) {
/*			if(data.data.page_count == 1 || data.data.list.length ==0) {
				$(".pagination").hide(); //只有一页的话就不显示分页导航
				show_common_data(data.data);
			}else {*/
				show_common_data(data.data);
				update_page_nav(data.data);
			/*}*/
		}
	);
	
	$("#v-form").dialog({
        height: 630,
        width: 650,
        cache: false,
        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
        dialogClass: "v-dialog",
        modal:true,
        buttons: [
          {
              text: '提交'
                      , 'class': 'btn btn-success'
                      , 'type': 'submit'
                      , click: function() {
              				var formData = new FormData($("#v-form")[0]);
              				var flag = createFormData();
              				if (flag){
	              				$.ajax({
	              					 url:'ajax_version_submit',
	              					 type:'POST',
	              					 enctype:'multipart/form-data',
	              					 data:formData,
	              					 processData:false,
	              					 contentType:false,
	              					 success:function(data){
	              						if (data.code==1){
	              							$("#tip").children("font").text(data.desc);
	              						 }else{
	              							$("#v-form").dialog("close");
	                     	        		cleanText();
	                     	        		do_page();
	              						 }
	              					 },
	              					 
	              				 });
	              				 return false;
                    	 
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
	
	
	$("#showDialog").click(function() {
		$("#idstr").val(0);
		modDialogCss("v-dialog");
		$('#v-form').dialog("option","title", "添加版本").dialog('open');
		return false;

	});
	
});

function createFormData(){
    if ($("#name").val() == "") {
    	$("#tip").children("font").text("版本名称不能为空!");
		return false;
    }
    if ($("#name").val().substr(0,1) != "A" && $("#name").val().substr(0,1) != "I") {
    	$("#tip").children("font").text("请在android版本前加A，iphone版本前加I");
		return false;
    }
    if ($("#idstr").val() == 0){
    	if ($('input[type="file"]').val() == ""){
    		$("#tip").children("font").text("请上传apk!");
    		return false;
    	}
    }
    return true;
	
}

function show_common_data(data) {
	var list = data.list;
	
	$("#audit > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		item_str += '<td>' + (i+(data.page-1)*data.page_size)+ '</td>';
		item_str += '<td>' + item.v_name + '</td>';
		item_str += '<td>' + item.v_size + '</td>';
		item_str += '<td>' + item.v_url + '</td>';
		item_str += '<td>' + item.v_force + '</td>';
		item_str += '<td>' + item.v_function + '</td>';
		item_str += '<td>' + item.v_bug + '</td>';
		item_str += '<td>' + item.v_time + '</td>';
		item_str += '<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" class="btn_detail" id="btn_modify_' + item.v_id + '" onclick="edit_Version(this.id)"><i class="icon-edit"></i>修改</a></li><li><a href="#" class="btn_del" id="btn_del_' + item.v_id + '" onclick="del_Version(this.id)"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
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
		"ajax_version_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
}

function del_Version(idstr){
	if(confirm("确认删除吗？")) {
		var id = idstr.split("_")[2];
		
		$.getJSON(
			"ajax_version_del?id=" + id + "&random=" + Math.random(),
			function(data) {
				do_page();
			}
		);
	}
	return false;
}

function edit_Version(idstr){
	
	v_id = idstr.split('_')[2];
	$("#idstr").val(v_id);
	var url = "ajax_getVersionById?id="+idstr+"&random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){   
			    	$("#name").val(json.data.list.v_name);
			    	$("#function").val(json.data.list.v_function);
			    	$("#bug").val(json.data.list.v_bug);
			    	$('input[name="force"]').each(function(){
			    		//alert($(this).attr("value") == json.data.list.v_force);
			    		if ($(this).attr("value") == json.data.list.v_force){
			    			$(this).attr("checked","checked");
			    		}else{
			    			$(this).removeAttr("checked");
			    		}
					});
			    
			    }      
	});
	modDialogCss("v-dialog");
	$('#v-form').dialog("option","title", "修改版本").dialog('open');
	return false;
}