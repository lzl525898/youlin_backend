
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

function show_data(list) {
	
	$("#listtable > tbody").empty();
	for(var i in list) {
		var item = list[i];
		
		item_str = '<tr class="list-users">';
		if(item.push_flag == 1){
			item_str += '<td><input type="checkbox" name="subcheck" value="' + item.new_id + '" disabled /><input type="hidden" name="community" value="'+item.community_id+'"/></td>';
		}else{
			item_str += '<td><input type="checkbox" name="subcheck" value="' + item.new_id + '"/><input type="hidden" name="community" value="'+item.community_id+'"/></td>';
		}
		item_str += '<td><a href="./getNews?id='+item.new_id+'" class="show_new" id="show_new_' + item.new_id + '">' + item.new_title + '</a></td>';
		item_str += '<td>' + item.city_name + '</td>';
		item_str += '<td>' + item.community_name + '</td>';
		item_str += '<td>' + item.pri_flag + '</td>';
		item_str += '<td>' + item.new_add_time + '</td>';
		if(item.push_flag == 1){
			item_str += '<td><span class="label label-success">已推送</span></td>';
		}else{
			item_str += '<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" class="btn_detail" id="btn_modify_' + item.new_id + '"><i class="icon-edit"></i>修改</a></li><li><a href="#" class="btn_del" id="btn_del_' + item.new_id + '"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
		}
		
		item_str += '</tr>';
		$("#listtable > tbody").append(item_str);
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
		//$("#center-column").load("../../static/web/admin_templates/modify_new.html?random=" + Math.random());
		$(".main-content").load("../../static/assets/templates/add_new.html?random=" + Math.random());
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

/*function add(title){
	var url = "ajax_city_data?random="+ Math.random();
	$.ajax({     
			    type: "GET",     
			    url: url,     
			    dataType:   "json",     
			    success: function(json){    
		            $("#city_id").empty();
		        	item_str = '<option value="0">请选择城市</option>';
		        	for(i=0;i<json.length;i++){ 
		        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
		        	}
		        	$("#city_id").append(item_str);
		            
		            $("#login-form").dialog({
		      	        height: 680,
		      	        width: 850,
		      	        modal:false,
		      	        open: function () {
		      	        	　CKEDITOR.replace('content',{
		      	        	    language: 'zh-cn',
		      	        	    width:600,
		      	        	    height:180,
		      	        	    //uiColor: '#9AB8F3',
		      	        	    toolbar :
		      	        	        [
		      	        	　　　　  //加粗     斜体，     下划线      穿过线      下标字        上标字
		      	        	           ['Bold','Italic','Underline','Strike','Subscript','Superscript'],
		      	        	　　　　  //数字列表          实体列表            减小缩进    增大缩进
		      	        	           ['NumberedList','BulletedList','-','Outdent','Indent'],
		      	        	　　　　  //左对齐             居中对齐          右对齐          两端对齐
		      	        	           ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
		      	        	　　　　  //超链接 取消超链接 锚点
		      	        	           ['Link','Unlink','Anchor'],
		      	        	　　　　  //图片   flash    表格       水平线            表情       特殊字符        分页符
		      	        	           ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak'],
		      	        	'/',
		      	        	　　　　　//样式       格式      字体    字体大小
		      	        	           ['Styles','Format','Font','FontSize'],
		      	        	　　　　  //文本颜色     背景颜色
		      	        	           ['TextColor','BGColor'],
		      	        	　　　　　//全屏           显示区块
		      	        	           ['Maximize', 'ShowBlocks','-']
		      	        	         ],
		      	        	      filebrowserImageUploadUrl:'ajax_upload',   //图片上传
		      	        	      image_previewText:' ',//预览区域显示内容
		      	        	});

		      	    	},
		                 title: title
		                         , 'class': "mydialog"  add custom class for this dialog
		                         , onClose: function() {
		                              $(this).dialog("close");
		                          }
		                 , buttons: [
		                     {
		                         text: '提交'
		                                 , 'class': 'btn-success'
		                                 , 'type': 'submit'
		                                 , click: function() {
		                             var options = {
		                                 dataType: 'json',
		                                 success: function(data) {
		                                     if (data.success) {
		                                         alert(data.msg);
		                                     }
		                                 } //end of success
		                             };//end of options
		                            // validForm();
		                             var result = $('#login-form').valid();
		                             //alert(result)
		                             if (result) {
		                                 $('#login-form').ajaxSubmit(options);
		                             }
		                         }//end of create click
		                     }, 
		                     {
		                         text: "取消"
		                                 , 'class': "btn-primary"
		                                 , click: function() {
		                             $(this).dialog("close");
		                         }
		                     }//end of 新建
		                 ]
		             });
			    }      
	});
   }*/
$(function() {

	$.getJSON(
		"ajax_news_list?random=" + Math.random(),
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
	
});

function getCommunityOptions(id){
	//获取community
	 $.ajax({     
	        type: "GET",     
	        url: "ajax_community_data?city_id="+ id + "&random=" + Math.random(),     
	        dataType:   "json",     
	        success: function(json){  
	        	$("#community_id").empty();
	        	item_str = '<option value="0">请选择小区</option>';
	        	for(i=0;i<json.length;i++){ 
	        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
	        	}
	        	$("#community_id").append(item_str);
	        }      
	 })
}
function addNew(){
	$(".main-content").load("../../static/assets/templates/add_new.html?random=" + Math.random());
}