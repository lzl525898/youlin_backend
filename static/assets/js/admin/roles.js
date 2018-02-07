var curr_page = 1; //当前页
var request_data = false; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(function() {
	//首页
	var url = "ajax_role_list?random=" + Math.random();
	$.getJSON(
			url,
			function(data) {
				redrawSubscription(data.data);
				update_page_nav(data.data);
				}
			);
	
	$("#role_form").dialog({
		height: 350,
		width: 550,
		cache: false,
		autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
        'class' : "mydialog", /*add custom class for this dialog*/
        dialogClass: "mydialog",
        modal:true,
        buttons: [
                   {
                	    text: '添加'
                	    	, 'class': 'btn btn-success'
                	    		, 'type': 'submit'
                	    			, click: function() {
                	    				var formData = new FormData($("#role_form")[0]);
                	    				if (formData){
                	    					$.ajax({
                	    						url:'ajax_role_submit/',
                	    						type:'POST',
                	    						enctype:'multipart/form-data',
                	    						data:formData,
                	    						 dataType: 'JSON',
                	    						 processData:false,
                	    						 contentType:false,
                	    						 success:function(data){
                	    								 if (data.code==1){
                	    								 $("#tip").children("font").text(data.desc);
                	    								  }
                	    							 else{
                	    								 $("#role_form").dialog("close");
                	    								 cleanText();
                	    								 do_page();
                	    								 }
                	    							  },//end of function(data)
                	    							  });// ajax
                	    					 }
                	    				return false;
                	    				 }//end of create click
                    }, 
                     {
                    	text: "取消" ,
                    	'class': "btn btn-primary" ,
                    	click: function() {
                    		$(this).dialog("close");
                    		cleanText();
                    		 }
                    }//end of 新建
                     ]
	 });
	
	//点击添加
	$("#showDialog").on("click", function (e) {
		$("#role_id").val(-1);
		$("#role_root").val(1);
		modDialogCss("mydialog");
		$('#role_form').dialog("option","title", "添加角色").dialog('open');
		return false;
		
	});

});


//编辑角色
function edit_Role(id){
	$.ajax({     
		type: "GET",   
		url: "echo_Role" , 
		data: {r_id:id, random:Math.random()},
		dataType:   "json",  
		success: function(data){  
			if( data.data[0].r_root==0)
				{
				alert("超级管理员不允许修改！");
				}
			else{
				$("#role_name").val(data.data[0].r_name);
				$("#role_describe").val(data.data[0].r_describe);
				$("#role_root").val(data.data[0].r_root);
				$("#role_id").val(id);
				modDialogCss("mydialog");
				$('#role_form').dialog("option","title", "编辑角色").dialog('open');
			}
		},
		})	//ajax结束

}

//删除
function del_Role(id,root){
	root=Number(root);
	if (root==0){
		alert("超级管理员不可删除！");
	}
	
	else{
		$.ajax({     
			type: "GET",   
			url: "del_Role" , 
			data: {r_id:id, random:Math.random()},
			dataType:   "json",  
			success: function(data){  
				if( data.code==1)
					{
					alert(data.desc);
					}
				else{
					 do_page();
				}
			},
			})	//ajax结束
	}
	/*var a = $("#"+id).attr('value');
	alert("a-----"+a);*/

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

//显示当前页面内容
function do_page() {
	$.getJSON(
			"ajax_role_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
				redrawSubscription(data.data);
				update_page_nav(data.data);
		}
	);
}


 //渲染界面
 function redrawSubscription(data){
	 	var list = data.list;
	    var thead =  $("#audit thead tr")
	    thead.empty();
	    var tbody =  $("#audit tbody")
	    tbody.empty();
	    thead = thead.append("<th>ID</th><th>角色</th><th>描述</th><th>操作</th>");
	    var sum = 0;
	    for(var j = 0 ; j <list.length;j++){
	       var tr =  $("<tr></tr>");
	       tr='<tr>';
	       tr+="<td>"+[j+1+(data.page-1)*data.page_size] +"</td>";
	       tr+="<td>"+list[j].name+"</td>";
	       tr+="<td>"+list[j].describe+"</td>";
	       tr+='<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a>'
	    	   +'<ul class="dropdown-menu"><li><a href="#" class="btn_detail" id="' + list[j].id + '" onclick="edit_Role(this.id)"><i class="icon-edit"></i>修改</a></li>'
	    	   +'<li><a href="#" class="btn_del" id="' + list[j].id + '"onclick="del_Role(this.id,'+list[j].root+')"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
	       tr+='</tr>';
	       tbody.append(tr)

	    }
	 }