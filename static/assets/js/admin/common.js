function cleanText(){
	
	$("input[type=reset]").trigger("click");
	$("#tip").children("font").text("");
	$("#tip_person").children("font").text("");
	$("#tip_pspswd").children("font").text("");
}

function modDialogCss(obj){

	$("."+obj+" .ui-dialog-titlebar-close").css("display","none");
	$("."+obj+" .ui-dialog-titlebar").css("background-color","#eff3f8");
	$("."+obj+" .ui-dialog-titlebar").css("background-image","none");
	$("."+obj+" .ui-dialog-titlebar").removeClass("ui-widget-header");
	$("."+obj+" .ui-dialog-titlebar").removeClass("ui-corner-all");
	$("."+obj+" .ui-widget-overlay").css("background-color","#eff3f8");
	
}