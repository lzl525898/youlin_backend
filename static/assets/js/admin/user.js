var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据


$(function() {
	 do_page() ;
	
	
$("#user_form").dialog({
		height: 550,
		width: 530,
		cache: false,
		autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
        'class' : "mydialog", /*add custom class for this dialog*/
        dialogClass: "mydialog",
        modal:true,
		buttons: [
	                {
	                    text: '添加'
	                            , 'class': ' btn btn-success'
	                            , 'type': 'submit'
	                            , click: function() {
	                            	var formData = createFormData();
	                	            if (formData){
	                	            	$.ajax({
	    	              					 url:'ajax_webUser_submit/',
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
	    	              							$("#user_form").dialog("close");
	    	                     	        		cleanText();
	    	                     	        		clean_tip();
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
	                        clean_tip();
	                    }
	                }//end of 新建
	            ]
	        });



	       
$("#showDialog").on("click", function (e) {
	   		cleanText();
	   		$("#idstr").val("-1");
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
					
					//生成角色下拉菜单
					$.ajax({
						type: "GET",   
						url: "ajax_role_data?random=" + Math.random(),
						dataType:   "json", 
						success: function(json){ 
							document.getElementById('role_id').options.length=1;
							var selectid=document.getElementById("role_id");
							for (var j = 0; j < json.length; j++) {
								selectid[j+1]=new Option( json[j].label, json[j].text);
								}
						}
					})
					modDialogCss("mydialog");
					document.getElementById('rpsd').className = 'form-group'; 
					document.getElementById('psd').className = 'form-group'; 
					
					
					$('#user_form').dialog("option","title", "添加用户").dialog('open');
					
					$("#city_id").change(function(){
						var city_id=$("#city_id").find('option:selected').val();
						$.get('ajax_community_data',
								{city_id : city_id,t:Math.random()}, 
								 function(data, status) {
									document.getElementById('com_id').options.length=1//初始化小区下拉菜单，保留第一个下拉列表按钮
									var selectid=document.getElementById("com_id");
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
	   	
//验证再次输入密码
function V_Password(){
	url1="<image src='../../static/assets/css/images/check.ico'>"
	url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var password=document.getElementById("password").value;
	var repassword=document.getElementById("repassword").value;
	if(!password){
		document.getElementById("t_password1").innerHTML=url2;
		$("#t_password2").children("font").text("不能为空");
		}
	else{
		if (password == repassword){
			document.getElementById("t_repassword1").innerHTML=url1;
			$("#t_repassword2").children("font").text("");
			}
		else{
			document.getElementById("t_repassword1").innerHTML=url2;
			$("#t_repassword2").children("font").text("密码不一致");
			}
		}
	}  

//输入密码
function Password(){
	url1="<image src='../../static/assets/css/images/check.ico'>"
	url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var password=document.getElementById("password").value;
	var repassword=document.getElementById("repassword").value;
	var pswreg=/^[A-Za-z0-9]{6,16}$/;
	if(!password){
		document.getElementById("t_password1").innerHTML=url2;
		$("#t_password2").children("font").text("不能为空");
		}
	else{
		if(!pswreg.test(password)) {
			document.getElementById("t_password1").innerHTML=url2;
			$("#t_password2").children("font").text("格式错误,密码为6到16位的字母或数字组合");
			}
		else{
			document.getElementById("t_password1").innerHTML=url1;
			$("#t_password2").children("font").text("");
			if(!repassword){
				$("#repassword2").val("");
				document.getElementById("t_repassword1").innerHTML="";
				$("#t_repassword2").children("font").text("");
				}
			else{
				if (password == repassword){
					document.getElementById("t_repassword1").innerHTML=url1;
					$("#t_repassword2").children("font").text("");
					}
				else{
					document.getElementById("t_repassword1").innerHTML=url2;
					$("#t_repassword2").children("font").text("密码不一致");
					}
				}
			}
		}
	}  	   	

//是否激活复选框选中状态
function check_box(){
	var len = $("input[name='active']:checked").length;
	if (len==0){
		$("#active").val("0");
		}
	else{
		$("#active").val("1");
		}
	}	

//邮箱格式
function V_email(){
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var email=$("#email")[0].value
	var reg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
	if(!email){
		document.getElementById("t_email1").innerHTML=url2;
		$("#t_email2").children("font").text("不能为空");
		}
	else{
		if(!reg.test(email)) {
			document.getElementById("t_email1").innerHTML=url2;
			$("#t_email2").children("font").text("格式错误");
			}
		else{
			document.getElementById("t_email1").innerHTML=url1;
			$("#t_email2").children("font").text("");
			}
		}
	}

//用户名	  
function V_Name(){
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var name=$("#name")[0].value
	name = name.replace(/\s/g, "");
	$("#name").val(name);
	var reg =/^[a-zA-Z][a-zA-Z0-9_]{3,14}[a-zA-Z0-9]$/;
	if(!name){
		document.getElementById("t_name1").innerHTML=url2;
		$("#t_name2").children("font").text("不能为空");
		}
	else{
		if(!reg.test(name)) {
			document.getElementById("t_name1").innerHTML=url2;
			$("#t_name2").children("font").text("格式错误,用户名为6-16位的字母数字下划线组成，且需以字母开头，不能以下划线结尾");
			}
		else{
			document.getElementById("t_name1").innerHTML=url1;
			$("#t_name2").children("font").text("");
			}
		}
	}
		   	
//手机号
function V_Phone(){ 
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var mobile=$("#phone")[0].value
	if(mobile.length==0){ 
		document.getElementById("t_phone1").innerHTML=url2;
		$("#t_phone2").children("font").text("不能为空");
		return false; 
		} 
	if(mobile.length!=11) { 
		document.getElementById("t_phone1").innerHTML=url2;
		$("#t_phone2").children("font").text("位数有误");
		return false;
		 } 
	 var myreg = /^(((13[0-9]{1})|(15[0-9]{1})|(147)|(177)|(18[0-9]{1}))+\d{8})$/;
	 if(!myreg.test(mobile)){ 
		 document.getElementById("t_phone1").innerHTML=url2;
		 $("#t_phone2").children("font").text("号码有误");
		 return false; 
		 } 
	 else{
		 document.getElementById("t_phone1").innerHTML=url1;
		 $("#t_phone2").children("font").text("");
		 }
	 } 


//城市	  
function V_city(){
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var city=$("#city_id")[0].value
	if(city==-1){
		document.getElementById("t_city1").innerHTML=url2;
		$("#t_city2").children("font").text("请选城市");
		}
	else{
		document.getElementById("t_city1").innerHTML=url1;
		$("#t_city2").children("font").text("");
		}
	}
//小区
function V_community(){
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var com_id=$("#com_id")[0].value
	if(com_id==-1){
		document.getElementById("t_com1").innerHTML=url2;
		$("#t_com2").children("font").text("请选 小区");
		}
	else{
		document.getElementById("t_com1").innerHTML=url1;
		$("#t_com2").children("font").text("");
		}
	}
//角色
function V_role(){
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"	
	var role_id=$("#role_id")[0].value
	if(role_id==-1){
		document.getElementById("t_role1").innerHTML=url2;
		$("#t_role2").children("font").text("请定义用户角色");
		}
	else{
		document.getElementById("t_role1").innerHTML=url1;
		$("#t_role2").children("font").text("");
		}
	}
//清空表单tip处文字
function clean_tip(){
	 document.getElementById("t_phone1").innerHTML="";
	 $("#t_phone2").children("font").text("");
	document.getElementById("t_email1").innerHTML="";
	$("#t_email2").children("font").text("");
	document.getElementById("t_city1").innerHTML="";
	$("#t_city2").children("font").text("");
	document.getElementById("t_name1").innerHTML="";
	$("#t_name2").children("font").text("");
	document.getElementById("t_repassword1").innerHTML="";
	$("#t_repassword2").children("font").text("");
	document.getElementById("t_password1").innerHTML="";
	$("#t_password2").children("font").text("");
	document.getElementById("t_role1").innerHTML="";
	$("#t_role2").children("font").text("");
	document.getElementById("t_com1").innerHTML="";
	$("#t_com2").children("font").text("");
	
}

function createFormData(){
	//clean_tip();
	var url1="<image src='../../static/assets/css/images/check.ico'>"
	var url2="<image src='../../static/assets/css/images/fork.jpg'>"
    var formData = new FormData($("#user_form")[0]);
	var id=document.getElementById("idstr").value;
	var reg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
	var myreg = /^(((13[0-9]{1})|(15[0-9]{1})|(147)|(177)|(18[0-9]{1}))+\d{8})$/;
	var pswreg=/^[A-Za-z0-9]{6,16}$/;
	var nreg =/^[a-zA-Z][a-zA-Z0-9_]{3,14}[a-zA-Z0-9]$/;
	
	var name=$("#name")[0].value
	name = name.replace(/\s/g, "");
	$("#name").val(name);
	if(!name){
		document.getElementById("t_name1").innerHTML=url2;
		$("#t_name2").children("font").text("不能为空");
		return false;
		}
	if(!nreg.test(name)) {
		document.getElementById("t_name1").innerHTML=url2;
		$("#t_name2").children("font").text("格式错误,用户名为5-16位的字母数字下划线组成，且需以字母开头，不能以下划线结尾");
		return false;
		
		}
    if(id==-1){
        if ($("#password").val() == "") {
        	document.getElementById("t_password1").innerHTML=url2;
    		$("#t_password2").children("font").text("不能为空");
    		return false;
        }
        
    	if(!pswreg.test($("#password").val())) {
    		document.getElementById("t_password1").innerHTML=url2;
    		$("#t_password2").children("font").text("格式错误,密码为6到16位的字母或数字组合");
    		return false;
        }
        
        if ($("#repassword").val() == "") {
        	document.getElementById("t_repassword1").innerHTML=url2;
    		$("#t_repassword2").children("font").text("不能为空");
    		return false;
        }
        
        if (!($("#repassword").val() == $("#password").val() )) {
        	document.getElementById("t_repassword1").innerHTML=url2;
    		$("#t_repassword2").children("font").text("密码不一致");
    		return false;
        }
    }

    
    if ($("#email").val() == "") {
    	document.getElementById("t_email1").innerHTML=url2;
		$("#t_email2").children("font").text("不能为空");
		return false;
    }
    
	if(!reg.test($("#email").val())) {
		document.getElementById("t_email1").innerHTML=url2;
		$("#t_email2").children("font").text("格式错误");
		return false;
    }
    
	if($("#phone").val().length==0){ 
		document.getElementById("t_phone1").innerHTML=url2;
		$("#t_phone2").children("font").text("不能为空");
		return false; 
		} 
	if($("#phone").val().length!==11){ 
		return false; 
		}
	if(!myreg.test($("#phone").val())){ 
		 return false; 
		 } 
    if($("#city_id").val() == -1){
    	document.getElementById("t_city1").innerHTML=url2;
		$("#t_city2").children("font").text("请选城市");
		return false;
		}
    if($("#com_id").val() == -1){
    	document.getElementById("t_com1").innerHTML=url2;
		$("#t_com2").children("font").text("请选 小区");
		return false;
    }
    if($("#role_id").val() == -1){
    	document.getElementById("t_role1").innerHTML=url2;
		$("#t_role2").children("font").text("请定义用户角色");
		return false;
    }

    formData.append('name', $('#name').val());
    formData.append('password', $('#password').val());
    formData.append('repassword', $('#repassword').val());
    formData.append('email', $('#email').val());
    formData.append('phone', $('#phone').val());
    formData.append('role_id', $('#role_id').val());
    formData.append('city_id', $('#city_id').val());
    formData.append('com_id', $('#com_id').val());
    formData.append('active', $('#active').val());
    formData.append('idstr', $("#idstr").val());
    
    return formData;
	
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
		"ajax_webUser_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
}

//渲染界面
function show_common_data(data){
	 	var list = data.list;
	    var thead =  $("#audit thead tr")
	    thead.empty();
	    var user_role=$("#rd_user_role").html();
	    //alert("user_role---"+user_role);
	    var tbody =  $("#audit tbody")
	    tbody.empty();
	    thead = thead.append("<th>ID</th><th>名字</th><th>邮箱</th><th>手机号码</th><th>所在城市</th><th>所属小区</th><th>角色</th><th>用户状态</th><th>操作</th>");
	    var sum = 0;
	    for(var j = 0 ; j <list.length;j++){
	       var tr =  $("<tr></tr>");
	       tr='<tr>';
	       tr+="<td>"+[j+1+(data.page-1)*data.page_size] +"</td>";
	       tr+="<td>"+list[j].name+"</td>";
	       tr+="<td>"+list[j].email+"</td>";
	       tr+="<td>"+list[j].phone+"</td>";
	       tr+="<td>"+list[j].city+"</td>";
	       tr+="<td>"+list[j].community+"</td>";
	       tr+="<td>"+list[j].role+"</td>";
	       if(list[j].state=="未激活"){
	    	   tr+="<td ><span class='label label-important'>"+list[j].state+"</span></td>";
	       }
	       else{
	    	   tr+='<td ><span class="label label-success">'+list[j].state+'</span></td>';
	       }
	       if(user_role=="超级管理员"){
	    	   tr+='<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu">'
		    	   +'<li><a href="#" class="btn_detail" id="' + list[j].id + '" onclick="edit_user(this.id)"><i class="icon-edit"></i>修改</a></li>'
		    	   +'<li><a href="#" class="btn_del" id="' + list[j].id + '" onclick="del_user(this.id)"><i class="icon-remove"></i> 删除</a></li>'
		    	  // +'<li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown"> 设置权限 <b class="caret"></b></a><ul class="dropdown-menu">'
		         //   +'</ul></li>'
		    	   +'</ul></div></td>';
	       }
	      /* tr+='<td><div class="dropdown"><a class="btn btn-xs dropdown-toggle" data-toggle="dropdown" href="#">操作 <span class="caret"></span></a><ul class="dropdown-menu">'
	    	   +'<li><a href="#" class="btn_detail" id="' + list[j].id + '" onclick="edit_user(this.id)"><i class="icon-edit"></i>修改</a></li>'
	    	   +'<li><a href="#" class="btn_del" id="' + list[j].id + '" onclick="del_user(this.id)"><i class="icon-remove"></i> 删除</a></li>'
	    	  // +'<li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown"> 设置权限 <b class="caret"></b></a><ul class="dropdown-menu">'
	         //   +'</ul></li>'
	    	   +'</ul></div></td>';*/
	       else{
	    	   tr+='<td ><span class="label label-success">无操作权限</span></td>';
	       }
	       tr+='</tr>';
	       tbody.append(tr)
	    }
	 }

function del_user(id){
	var f = confirm("是否删除该记录？");
	if (!f) {
		return false;
		}
	var id = id;
	$.get('del_webUser',
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


function edit_user(id){
	var id =id;
	document.getElementById('rpsd').className = 'hide'; 
	document.getElementById('psd').className = 'hide'; 
	$("#idstr").val(id);
	$.get('echo_webUser',  //表单回显部分
			{id : id,t:Math.random()}, 
			function(data, status) {
				var city_id 						= data.data[0].city;
				var community_id 		= data.data[0].community;
				var role_id						= data.data[0].role;
				var id 								= data.data[0].id;
				var name 						= data.data[0].name;
				var password 				= data.data[0].password;
				var email 							= data.data[0].email;
				var phone 						= data.data[0].phone;
				var state 							= data.data[0].state;
				$("#name").val(name);
				//$("#password").val(password);
				//$("#repassword").val(password);
				$("#email").val(email);
				$("#phone").val(phone);
				if (Number(state)==1){
					$("#active").val(state);
					$("#active").prop("checked", true);
				}
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
									 document.getElementById('com_id').options.length=1;
									 var selectid=document.getElementById("com_id");
									 for (var j = 0; j < data.length; j++) {
										 selectid[j+1]=new Option( data[j].label, data[j].text);
										  }
									 $("#com_id").val(community_id);
									 },
									 'json'
									 );//小区复显结束
				//生成角色下拉菜单
				$.ajax({
					type: "GET",   
					url: "ajax_role_data?random=" + Math.random(),
					dataType:   "json", 
					success: function(json){ 
						document.getElementById('role_id').options.length=1;
						var selectid=document.getElementById("role_id");
						for (var j = 0; j < json.length; j++) {
							selectid[j+1]=new Option( json[j].label, json[j].text);
							}
						$("#role_id").val(role_id);
					}
				})			
				
			},//表单回显回调函数结束
				'json'
				);
	modDialogCss("mydialog");
	$('#user_form').dialog("option","title", "修改用户信息").dialog('open');
	
	$("#city_id").change(function(){
		var city_id=$("#city_id").find('option:selected').val();
		$.get('ajax_community_data',
				{city_id : city_id,t:Math.random()}, 
				 function(data, status) {
					document.getElementById('com_id').options.length=1//初始化小区下拉菜单，保留第一个下拉列表按钮
					var selectid=document.getElementById("com_id");
					for (var j = 0; j < data.length; j++) {
						selectid[j+1]=new Option( data[j].label, data[j].text);
						}//for循环结束，生成小区下拉菜单
					},
					'json'
					);//get方法结束
		
		});   //选择城市后触发生成小区下拉菜单
	return false;
}

















