
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(function() {
	var url = "ajax_gift_list?random=" + Math.random();
	$.getJSON(
		url,
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
	$("#giftForm").dialog({
        height: 400,
        width: 630,
        cache: false,
        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
        'class' : "giftForm-dialog", /*add custom class for this dialog*/
        dialogClass: "giftForm-dialog",
        modal:true,
        buttons: [
         {
             text: '添加'
                     , 'class': 'btn btn-success'
                     , 'type': 'submit'
                     , click: function() {
                    	    //var formData = new FormData($("#giftForm")[0]);
                    	    //创建FormData对象
                    	 	var formData = createFormData();
            	            if (formData){
            	            	$.ajax({
	              					 url:'ajax_gift_submit/',
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
	              							$("#giftForm").dialog("close");
	                     	        		cleanText();
	                     	        		do_page();
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
	
	$("#showDialog").on("click", function (e) {
		$("#idstr").val(0);
		//getCommunity();
		//获取community
		 $.ajax({     
		        type: "GET",     
		        url: "ajax_community_list?random=" + Math.random(),     
		        dataType:   "json",  
		        success: function(json){  
		        	//alert(json.length);
		        	$("#g_community_id").empty();
		        	item_str = '<option value="0">请选择小区</option>';
		        	for(i=0;i<json.length;i++){ 
		        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
		        	}
		        	$("#g_community_id").append(item_str);
		        	modDialogCss("giftForm-dialog");
		    		$('#giftForm').dialog("option","title", "添加礼品").dialog('open');
		        },
		 })
	/*	cleanBootscrapModal();
		$(".modal-title").text("添加礼品");
		$('#giftForm').dialog('open');*/
		return false;
	});
	$("#release").on("click", function (e) {
		var ids= [];
		$("input[name='subcheck']:checked").each(function(){
			 ids.push($(this).val());
         });
		if (ids && ids.length == 0){
			alert("请选择需要发布的礼品!");
			return false;
		}
		if(confirm("确认发布以下礼品让用户兑换吗？")) {

			$.getJSON(
				"ajax_gift_release?ids=" + ids + "&random=" + Math.random(),
				function(data) {
					do_page();
				}
			);
		}
		return false;
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
	
});

function show_common_data(data) {
	var list = data.list
/*	$("#audit > thead").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th><input type="checkbox" id="SelectAll"/></th>';
	item_str += '<th>礼品名称</th>';
	item_str += '<th>所需积分</th>';
	item_str += '<th>礼品图片</th>';
	item_str += '<th>是否允许兑换</th>';
	item_str += '<th>添加时间</th>';
	item_str += '<th>操作</th>';
	item_str += '</tr>';
	$("#audit > thead").append(item_str);*/
	
	$("#audit > tbody").empty();
	for(var i in list) {
		var item = list[i];
		i++;
		item_str = '<tr>';
		if(item.gl_status == '是' || item.gl_end_time){
			item_str += '<td><input type="checkbox" name="subcheck" value="' + item.gl_id + '" disabled /></td>';
		}else{
			item_str += '<td><input type="checkbox" name="subcheck" value="' + item.gl_id + '"/></td>';
		}
		item_str += '<td>' + item.gl_name + '</td>';
		item_str += '<td>' + item.gl_credit + '</td>';
		item_str += '<td><img src="' + item.gl_pic + '"/></td>';
		item_str += '<td>' + item.gl_status + '</td>';
	
		item_str += '<td>' + item.gl_start_time + '</td>';
		if(item.gl_status == '是'){
			item_str += '<td><span class="label label-warning"><a href="#" class="btn_down" id="btn_down_' + item.gl_id + '" onclick="down_gift(this.id)"><i class="icon-inbox"></i>下架</a></span></td>';
		}else{
			if (item.gl_end_time){
				item_str += '<td><span class="label label-success">已下架</span></td>';
			}else{
				item_str += '<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" class="btn_detail" id="btn_modify_' + item.gl_id + '" onclick="edit_gift(this.id)"><i class="icon-edit"></i>修改</a></li><li><a href="#" class="btn_del" id="btn_del_' + item.gl_id + '" onclick="del_gift(this.id)"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
			}
			
		}
		
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
		"ajax_gift_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
}

function getCommunity(){

}

function del_gift(idstr){
	if(confirm("确认删除吗？")) {
		var id = idstr.split("_")[2];
		
		$.getJSON(
			"ajax_gift_del?id=" + id + "&random=" + Math.random(),
			function(data) {
				do_page();
			}
		);
	}
	return false;
}

function down_gift(idstr){
	if(confirm("确认下架该商品吗？")) {
		var id = idstr.split("_")[2];
		
		$.getJSON(
			"ajax_gift_down?id=" + id + "&random=" + Math.random(),
			function(data) {
				do_page();
			}
		);
	}
	return false;
}

function edit_gift(idstr){
	
	v_id = idstr.split('_')[2]
	$("#idstr").val(v_id);
	var url = "ajax_getGiftById?id="+idstr+"&random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){   
			    	$("#gl_name").val(json.data.list.gl_name);
			    	$("#gl_credit").val(json.data.list.gl_credit);
			    	$("#gl_pic_view").attr("src",json.data.list.gl_pic);
			    	$("#g_community_id").empty();
			    	item_community = '<option value="0">请选择小区</option>';
		        	var community_list = json.data.community_list;
		        	for(i=0;i < community_list.length;i++){ 
		        		if(json.data.list.gl_community_id == community_list[i].text){
		        			item_community += '<option value="'+community_list[i].text+'" selected="selected">'+community_list[i].label+'</option>';
		        		}else{
		        			item_community += '<option value="'+community_list[i].text+'">'+community_list[i].label+'</option>';
		        		}
		        		
		        	}
		        	$("#g_community_id").append(item_community);
		        	modDialogCss("giftForm-dialog");
		        	$('#giftForm').dialog("option","title", "修改礼品").dialog('open');
			    }      
	});
/*	cleanBootscrapModal();
	$(".modal-title").text("修改礼品");
	$('#giftForm').dialog('open');*/
	
	
	return false;
}

function createFormData(){
	
    var formData = new FormData();
    
    if ($("#gl_name").val() == "") {
    	$("#tip").children("font").text("礼品名称不能为空!");
		return false;
    }
    
    if (isNaN($('input[name="gl_credit"]').val()) || $('input[name="gl_credit"]').val() == "") {
    	$("#tip").children("font").text("积分必须输入数字形式!");
		return false;
    }
    
    if ($("#idstr").val() == 0){
    	if ($('input[type="file"]').val() == ""){
    		$("#tip").children("font").text("请上传礼品图片!");
    		return false;
    	}
    }
    if($("#g_community_id").val() == 0){
    	$("#tip").children("font").text("请选择小区!");
		return false;
    }
	$.each($('#gl_pic')[0].files, function(i, file) {
		formData.append('gl_pic', file);
	});
    formData.append('gl_name', $('#gl_name').val());
    formData.append('gl_credit', $('#gl_credit').val());
    formData.append('community_id', $('#g_community_id').val());
    formData.append('idstr', $("#idstr").val());
    
    return formData;
	
}

function cleanBootscrapModal(){
	$(".modal-title").empty();  
	$(".modal-footer").css("text-align","center");
	$(".modal-header").css("background-color","#eff3f8");
	$(".modal-header").css("border-top-color","#e4e9ee");
	$(".modal-header").css("box-shadow","none");
	$(".close").hide();
}