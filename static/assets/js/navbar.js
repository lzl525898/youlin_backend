	 $(function() {
		 //修改密码
			 $("#cpsd_form").dialog({
					height: 320,
					width:550,
					cache: false,
					autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
			        'class' : "mydialog", 
			        dialogClass: "mydialog",
			        modal:true,
					buttons: [
				                {
				                    text: '修改'
				                            , 'class': ' btn btn-success'
				                            , 'type': 'submit'
				                            , click: function() {
				                            	var formData = create_FormData();
				                	            if (formData){
				                	            	$.ajax({
				    	              					 url:'ajax_Psd_change',
				    	              					 type:'POST',
				    	              					 enctype:'multipart/form-data',
				    	              					 data:formData,
				    	              					 dataType: 'JSON',
				    	              					 processData:false,
				    	              					 contentType:false,
				    	              					 success:function(data){
				    	              					 	 if (data.code==1){
				    	              							 $("#tip_pspswd").children("font").text(data.desc);
				    	              						 }
				    	              						 else{
				    	              							$("#cpsd_form").dialog("close");
				    	                     	        		cleanText(); 
				    	                     	        		alert(data.desc);
				    	                     	        		self.location=data.data.website;
				    	              						 } 
				    	              					 },
				    	              					 
				    	              				 	});
				                	            }
				                            	
				                            	//$("#cpsd_form").dialog("close");
				                    }//end of create click
				                }, 
				                {
				                    text: "取消"
				                            , 'class': "btn btn-primary"
				                            , click: function() {
				                            	
				                        $("#cpsd_form").dialog("close");
				                        cleanText();
				                        
				                    }
				                }//end of 新建
				            ]
				        });
			 
			 
			 
			 //修改个人信息
			 $("#person_form").dialog({
					height: 500,
					width:550,
					cache: false,
					autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
			        'class' : "mydialog", 
			        dialogClass: "mydialog",
			        modal:true,
					buttons: [
				                {
				                    text: '修改'
				                            , 'class': ' btn btn-success'
				                            , 'type': 'submit'
				                            , click: function() {
				                            	var formData = create_PFormData();
				                            	if (formData){
				                	            	$.ajax({
				    	              					 url:'ajax_person_update',
				    	              					 type:'POST',
				    	              					 enctype:'multipart/form-data',
				    	              					 data:formData,
				    	              					 dataType: 'JSON',
				    	              					 processData:false,
				    	              					 contentType:false,
				    	              					 success:function(data){
				    	              					 	 if (data.code==1){
				    	              							 $("#tip_person").children("font").text(data.desc);
				    	              						 }
				    	              						 else{
				    	                     	        		cleanText(); 
				    	                     	        		$("#person_form").dialog("close");
				    	              						 } 
				    	              					 },
				    	              					 
				    	              				 	});
				                            }
				                   
				                }, 
				                },
				                {
				                    text: "取消"
				                            , 'class': "btn btn-primary"
				                            , click: function() {  	
				                        $("#person_form").dialog("close");
				                        
				                        cleanText(); 
				                    }
				                },//end of 新建
				            ]
				        });
			 
			 
			 
		 });  
	 
	 
	
	
	$("#person_data").on("click", function (e) {
		$.ajax({
				 url:'ajax_person_data',
				 type:'POST',
				 enctype:'multipart/form-data',
				 dataType: 'JSON',
				 processData:false,
				 contentType:false,
				 success:function(data){
				 	 if (data.code==1){
				 		 alert(data.desc);
				 		 $("#person_form").dialog("close");
				 		 cleanText(); 
				 		 self.location=data.data.website;
						 }
						 else{
							 var email				=data.data.u_email;
							 var phone			=data.data.u_phone_number;
							 var city_id			=data.data.city_id;
							 var com_id			=data.data.community_id;
							 var role_name	=data.data.role_name
							 var state				=data.data.user_state
							 $("#rd_user_role").html(role_name);
							 $("#rd_user_state").html(state);
							 $("#person_email").val(email);
							 $("#person_phone").val(phone);
							 $.ajax({     
									type: "GET",   
									url: "ajax_city_data?random=" + Math.random(), 
									dataType:   "json",  
									success: function(json){  
										document.getElementById('person_city').options.length=1;
										var selectid=document.getElementById("person_city");
										for (var j = 0; j < json.length; j++) {
											selectid[j+1]=new Option( json[j].label, json[j].text);
											}
										$("#person_city").val(city_id);
										},
										})
										
										//生成小区下拉菜单并选中
										$.get('ajax_community_data',
										 {city_id : city_id,t:Math.random()}, 
										 function(data, status) {
											 document.getElementById('person_com').options.length=1;
											 var selectid=document.getElementById("person_com");
											 for (var j = 0; j < data.length; j++) {
												 selectid[j+1]=new Option( data[j].label, data[j].text);
												  }
											 $("#person_com").val(com_id);
											 },
											 'json'
											 );//小区复显结束
						 } //else分支结束
				 },
				 
			 	});
		modDialogCss("mydialog");
		$('#person_form').dialog("option","title", "个人资料").dialog('open');
		
		$("#person_city").change(function(){
			var city_id=$("#person_city").find('option:selected').val();
			$.get('ajax_community_data',
					{city_id : city_id,t:Math.random()}, 
					 function(data, status) {
						document.getElementById('person_com').options.length=1//初始化小区下拉菜单，保留第一个下拉列表按钮
						var selectid=document.getElementById("person_com");
						for (var j = 0; j < data.length; j++) {
							selectid[j+1]=new Option( data[j].label, data[j].text);
							}//for循环结束，生成小区下拉菜单
						},
						'json'
						);//get方法结束
			
			});   //选择城市后触发生成小区下拉菜单
		return false;
		
	});
	
	
	$("#set_up").on("click", function (e) {
		cleanText();
		modDialogCss("mydialog");
		$('#cpsd_form').dialog("option","title", "修改密码").dialog('open');
		return false;
		
	});
	
	function create_FormData(){
		//alert("创建表单内容");
		var formData = new FormData($("#cpsd_form")[0]);
	    formData.append('old_psd', $('#old_psd').val());
	    formData.append('new_psd', $('#new_psd').val());
	    formData.append('rnew_psd', $('#rnew_psd').val());
	    return formData;
	}
	
	function create_PFormData(){
		//alert("创建表单内容");
		var formData = new FormData($("#person_form")[0]);
	    formData.append('person_email', $('#person_email').val());
	    formData.append('person_phone', $('#person_phone').val());
	    formData.append('person_city', $('#person_city').val());
	    formData.append('person_com', $('#person_com').val());
	    return formData;
	}
	
	
	
	
	
	
	