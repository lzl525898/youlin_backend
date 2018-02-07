
$(function() {
	var yl_id = get_menu_param("yl_id");
	if (yl_id == null){//添加

		$("#idstr").val(0);
		$(".page-header").html("<h1>添加<small>内容</small></h1>");	            
	}else{ //修改
		$("#menu_param").val("");
		$("#idstr").val(yl_id);
		var url = "ajax_life_data?id="+yl_id+"&random="+ Math.random();
		$.ajax({     
				    type: "GET",     
				    url: url,     
				    dataType:   "json",     
				    success: function(json){ 
				    	$(".page-header").html("<h1>修改<small>内容</small></h1>");
				    	$("#title").val(json.data.yl_title);
				    	$("#author").val(json.data.yl_author);
				    	$("#date").val(json.data.yl_date);
				    	setContext(json.data.yl_content);
			        	$("#idstr").attr("value",json.data.yl_id);
				    }      
				});
		
	}
	/*var csrftoken = getCookie("csrftoken");
	alert(csrftoken);
	$('input[name="csrfmiddlewaretoken"]').val('mHHbEVeF66MdUlndh7LcWhJHD6yHSjw8');*/
	//$("#csrftoken1").attr("value","");
	
	$("#btn_submit").click(function() {
			$("#myform").submit(function(event){
				//var formData = new FormData($("#myform")[0]);
				var formData = createFormData(event);
				if(formData){
					$.ajax({
						 url:'ajax_life_submit',
						 type:'POST',
						 enctype:'multipart/form-data',
						 data:formData,
						 processData:false,
						 contentType:false,
						 success:function(data){
							 $(".main-content").load("../../static/assets/templates/life.html?random=" + Math.random());
						 },
						 
					 });
					return false;
				}
					
			 
		 });
	});
	$("#btn_view").click(function(event) {
		var formData = new FormData($("#myform")[0]);
		var flag = createFormData(event);
		if(flag){
			
			$("#myform").attr('target', '_blank');
			$("#myform").attr("action","ajax_preview");
			
		}
	});
	
	
	
});

function createFormData(event){
	var title = $("#title").val();
	var content = getContext();
	var date = $("#date").val();
	var author  = $("#author").val();
	var avatar = $("#avatar").val();
    if ($("#title").val() == "" || $("#title").val().length>20) {
    	$("#title").parent().next().find("p").children("font").text("内容标题不能为空，且不能超过20个字!");
    	event.preventDefault();  //阻止默认行为 ( 表单提交 
		return false;
    }else{
    	$("#title").parent().next().find("p").children("font").text("");
    }
    
    if ($("#content").val() == "") {
    	$("#content").parent().next().find("p").children("font").text("内容不能为空!");
    	event.preventDefault();  //阻止默认行为 ( 表单提交 
		return false;
    }else{
    	$("#content").parent().next().find("p").children("font").text("");
    }
    

    
    if ($("#author").val() == "") {
    	$("#author").parent().next().find("p").children("font").text("请添加作者!");
    	event.preventDefault();  //阻止默认行为 ( 表单提交 
		return false;
    }else{
    	$("#author").parent().next().find("p").children("font").text("");
    }
    if ($("#date").val() == "") {
    	$("#date").parent().next().find("p").children("font").text("请选择添加时间!");
    	event.preventDefault();  //阻止默认行为 ( 表单提交 
		return false;
    }else{
    	$("#date").parent().next().find("p").children("font").text("");
    }
    var formData = new FormData();
	$.each($('#avatar')[0].files, function(i, file) {
		formData.append('avatar', file);
	});
    formData.append('title', $('#title').val());
    formData.append('author', $('#author').val());
    formData.append('date', $('#date').val());
    formData.append('content', $('#content').val());
    formData.append('idstr', $("#idstr").val());
    
    return formData;
	
}

function getCookie(name){ 

	var strCookie=document.cookie; 
	var arrCookie=strCookie.split("; "); 
	for(var i=0;i<arrCookie.length;i++){ 
		var arr=arrCookie[i].split("="); 
		if(arr[0]==name)return arr[1]; 
	} 
	return ""; 
}

function get_menu_param(name) {
	
	var param_str = $("#menu_param").val();
	
	if(!param_str || param_str == "")
		return null;
	
	var param = null;
	
	if(param_str.indexOf(",") > -1) {
		var params = param_str.split(",");
		for(var i in params) {
			param = params[i].split(":");
			
			if(param[0] == name)
				return param[1];
		}		
	}
	else {
		param = param_str.split(":");
		if(param[0] == name)
			return param[1];
	}
	return null;
}