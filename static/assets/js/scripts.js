
jQuery(document).ready(function() {
	
    /*
        Fullscreen background
    */
	
    $.backstretch("../../../static/assets/img/backgrounds/1.jpg");
    $("#form-username").val("");
    $("#form-password").val("");
 
    /*
        Form validation
    */
  /*  $('.login-form input[type="text"], .login-form input[type="password"], .login-form textarea').on('focus', function() {
    	$(this).removeClass('input-error');
    });*/
    
  //  $('.login-form').on('submit', function(e) {
    	//alert($(this).text());
    	
/*    	var  name=document.getElementById("form-username").value;
    	alert("form-username-----"+name);
    	var  form-password=document.getElementById("form-password").value;
    	alert("form-password-----"+form-password);*/
    	//return false;
 	//$(this).find('input[type="text"], input[type="password"]').each(function(){
 	//	alert($(this).text());
 		
/*    		if( $(this).val() == "" ) {
    			e.preventDefault();
    			$(this).addClass('input-error');
    		}
    		else {
    			$(this).removeClass('input-error');
    		}*/
//    	});
// 	return false;
 //   });
    
    
});

function V_FName(){
	var  name=document.getElementById("form-username").value;
	var nreg =/^[a-zA-Z][a-zA-Z0-9_]{3,14}[a-zA-Z0-9]$/;
	name = name.replace(/\s/g, "");
	$("#form-username").val(name);
	if(!name){
		$("#tip_login").children("font").text("用户名不能为空");
		return false;
		}
	else if(!nreg.test(name)) {
		$("#tip_login").children("font").text("格式错误,用户名为6-16位的字母数字下划线组成，且需以字母开头，不能以下划线结尾");
		return false;
		}
	else {
		$.get('verify_user',
				{name : name,t:Math.random()}, 
				 function(data, status) {
					if (data.code==1){
							 $("#tip_login").children("font").text(data.desc);
						 }
					else{
						$("#tip_login").children("font").text("");
					}
					},
					'json'
					);//get方法结束
	}
}


function checkUser(){
	var  nreg        =/^[a-zA-Z][a-zA-Z0-9_]{3,14}[a-zA-Z0-9]$/;
	var  pswreg   =/^[A-Za-z0-9]{6,16}$/;
	var  name      =document.getElementById("form-username").value;
	var  password=document.getElementById("form-password").value;
	if(!name){
		$("#tip_login").children("font").text("用户名不能为空");
		return false;
		}
	if(!nreg.test(name)) {
		$("#tip_login").children("font").text("格式错误,用户名为6-16位的字母数字下划线组成，且需以字母开头，不能以下划线结尾");
		return false;
		}
	if(!password){
		$("#tip_login").children("font").text("密码不能为空");
		return false;
		}
	if(!pswreg.test(password)) {
		$("#tip_login").children("font").text("格式错误,密码为6到16位的字母或数字组合");
		return false;
    }
	$("#tip_login").children("font").text("");

}
