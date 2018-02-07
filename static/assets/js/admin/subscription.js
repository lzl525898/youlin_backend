var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(function() {
	//首页
	var url = "ajax_subscription_list?random=" + Math.random();
	$.getJSON(
			url,
			function(data) {
				redrawSubscription(data.data);
				update_page_nav(data.data);
				}
			);
	
	//初始化表单
	
	$("#as-form").dialog({
		height: 400,
		width: 630,
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
                	    				var formData = new FormData($("#as-form")[0]);
                	    				if (formData){
                	    					$.ajax({
                	    						url:'ajax_subscription_submit/',
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
                	    								 $("#as-form").dialog("close");
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
	
	$("#showDialog").on("click", function (e) {
		$("#sub_id").val(-1);
		$.ajax({
			type: "GET",   
			url: "ajax_city_data?random=" + Math.random(),
			dataType:   "json", 
			success: function(json){ 
				document.getElementById('city_id').options.length=1;
				var selectid=document.getElementById("city_id");
				for (var j = 0; j < json.length; j++) {
					selectid[j+1]=new Option( json[j].label, json[j].text);
					}//for循环结束，生成城市下拉菜单
				
				modDialogCss("mydialog");
				$('#as-form').dialog("option","title", "添加公众号").dialog('open');
				
				$("#city_id").change(function(){
					var city_id=$("#city_id").find('option:selected').val();
					$.get('ajax_community_data',
							{city_id : city_id,t:Math.random()}, 
							 function(data, status) {
								document.getElementById('select_community').options.length=1//初始化小区下拉菜单，保留第一个下拉列表按钮
								var selectid=document.getElementById("select_community");
								for (var j = 0; j < data.length; j++) {
									selectid[j+1]=new Option( data[j].label, data[j].text);
									}//for循环结束，生成小区下拉菜单
								},
								'json'
								);//get方法结束
					
					});   //选择城市后触发生成小区下拉菜单
				},
				})
				return false;
		});
	});

//编辑界面
function edit_Subscription(id){
	var id =id;
	$("#sub_id").val(id);
	$.get('echo_Subscription',  //表单回显部分
			{id : id,t:Math.random()}, 
			function(data, status) {
				var city_id = data.data[0].city_id;
				var community_id = data.data[0].community_id;
				var s_name=data.data[0].s_name;
				$("#v_subscription").val(s_name);
				$.ajax({     
					type: "GET",   
					url: "ajax_city_data?random=" + Math.random(), 
					dataType:   "json",  
					success: function(json){  
						document.getElementById('city_id').options.length=1;
						var selectid=document.getElementById("city_id");
						for (var j = 0; j < json.length; j++) {
							selectid[j+1]=new Option( json[j].label, json[j].text);
							}//生成城市下拉菜单
						$("#city_id").val(city_id);
						},
						})	
						
						$.get('ajax_community_data',
								 {city_id : city_id,t:Math.random()}, 
								 function(data, status) {
									 document.getElementById('select_community').options.length=1;
									 var selectid=document.getElementById("select_community");
									 for (var j = 0; j < data.length; j++) {
										 selectid[j+1]=new Option( data[j].label, data[j].text);
										  }
									 $("#select_community").val(community_id);
									 },
									 'json'
									 );//小区复显结束
				},//表单回显回调函数结束
				'json'
				);
	modDialogCss("mydialog");
	$('#as-form').dialog("option","title", "编辑公众号").dialog('open');
	
	$("#city_id").change(function(){
		var city_id=$("#city_id").find('option:selected').val();
		$.get('ajax_community_data',
				{city_id : city_id,t:Math.random()}, 
				 function(data, status) {
					document.getElementById('select_community').options.length=1//初始化小区下拉菜单，保留第一个下拉列表按钮
					var selectid=document.getElementById("select_community");
					for (var j = 0; j < data.length; j++) {
						selectid[j+1]=new Option( data[j].label, data[j].text);
						}//for循环结束，生成小区下拉菜单
					},
					'json'
					);//get方法结束
		
		});   //选择城市后触发生成小区下拉菜单
	
	return false;
	}

//删除记录
function del_Subscription(a){
	var f = confirm("是否删除该记录？");
	if (!f) {
		return false;
		}
	var id = a;
	$.get('del_Subscription',
			{id : id,t:Math.random()},
			function(data, status) {
				if (data.code==1){
					alert(data.desc);
					}
				else{
					do_page();
					}
				},
				'json'
				);
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
			"ajax_subscription_list?page=" + curr_page + "&random=" + Math.random(),
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
	    thead = thead.append("<th>ID</th><th>城市</th><th>关联小区</th><th>公众号名称</th><th>图片</th><th>操作</th>");
	    var sum = 0;
	    for(var j = 0 ; j <list.length;j++){
	       var tr =  $("<tr></tr>");
	       tr='<tr>';
	       tr+="<td>"+[j+1+(data.page-1)*data.page_size] +"</td>";
	       tr+="<td>"+list[j].city+"</td>";
	       tr+="<td>"+list[j].community+"</td>";
	       tr+="<td>"+list[j].name+"</td>";
	       tr+="<td >"+list[j].url+"</td>";
	       tr+='<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu"><li><a href="#" class="btn_detail" id="' + list[j].id + '" onclick="edit_Subscription(this.id)"><i class="icon-edit"></i>修改</a></li><li><a href="#" class="btn_del" id="' + list[j].id + '" onclick="del_Subscription(this.id)"><i class="icon-remove"></i> 删除</a></li></ul></div></td>';
	       tr+='</tr>';
	       tbody.append(tr)
	    }
	 }