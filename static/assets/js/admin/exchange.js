
var curr_page = 1; //当前页
var request_data = true; //这个变量是为了防止请求完数据后，更新分页导航数据时反复请求数据

$(function() {
	var url = "ajax_exchange_list?random=" + Math.random();
	$.getJSON(
		url,
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
	
	$("#exchangeForm").dialog({
	        height: 340,
	        width: 630,
	        cache: false,
	        autoOpen:false,//该选项默认是true，设置为false则需要事件触发才能弹出对话框 
            'class' : "exchangeForm-dialog", /*add custom class for this dialog*/
            dialogClass: "exchangeForm-dialog",
            modal:true,
            buttons: [
             {
                 text: '导出'
                         , 'class': 'btn btn-success'
                         , 'type': 'submit'
                         , click: function() {
                        	 	var formData = createFormData();
                	            if (formData){
                	            	exportRecord();
                            	 	$("#exchangeForm").dialog("close");
                    	        	cleanText();
                    	        	do_page();
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

		//getCommunity();
//		cleanBootscrapModal();
//		$(".modal-title").text("导出兑换记录");
//		$('#exchangeForm').dialog('open');
		//获取community
		 $.ajax({     
		        type: "GET",     
		        url: "ajax_community_list?random=" + Math.random(),     
		        dataType:   "json",     
		        success: function(json){ 
		        	$("#e_community_id").empty();
		        	item_str = '<option value="0">请选择小区</option>';
		        	for(i=0;i<json.length;i++){ 
		        		item_str += '<option value="'+json[i].text+'">'+json[i].label+'</option>';
		        	}
		        	$("#e_community_id").append(item_str);
		        	modDialogCss("exchangeForm-dialog");
		    		$('#exchangeForm').dialog("option","title", "导出兑换记录").dialog('open');
		        }      
		 })

		return false;
	});
	$("#change").on("click", function (e) {
		var ids= [];
		$("input[name='subcheck']:checked").each(function(){
			 ids.push($(this).val());
         });
		if (ids && ids.length == 0){
			alert("请选择需要更改兑换状态的记录!");
			return false;
		}
		if(confirm("确认更改以下记录的兑换状态吗？")) {
			$.getJSON(
				"ajax_exchange_status?ids=" + ids + "&random=" + Math.random(),
				function(data) {
					do_page();
				}
			);
		}
		return false;
	});
	
});

function show_common_data(data) {
	var list = data.list;
	$("#audit > thead").empty();
	//title部分
	var item_str = '<tr>';
	item_str += '<th><input type="checkbox" name="SelectAll" onclick="selectAll(this);"/></th>';
	item_str += '<th>礼品名称</th>';
	item_str += '<th>兑换数量</th>';
	item_str += '<th>兑换时间</th>';
	item_str += '<th>兑换状态</th>';
	item_str += '<th>兑换者手机号</th>';
	item_str += '<th>兑换者所在小区</th>';
	item_str += '</tr>';
	$("#audit > thead").append(item_str);
	$("#audit > tbody").empty();
	if (list){
		for(var i in list) {
			var item = list[i];
			i++;
			item_str = '<tr>';
			if(item.ue_status == '已兑换'){
				item_str += '<td><input type="checkbox" name="subcheck" value="' + item.ue_id + '" disabled /></td>';
			}else{
				item_str += '<td><input type="checkbox" name="subcheck" onclick="singleChk();" value="' + item.ue_id + '"/></td>';
			}
			item_str += '<td>' + item.ue_glid + '</td>';
			item_str += '<td>' + item.ue_count + '</td>';
			item_str += '<td>'+item.ue_time+'</td>';
			if(item.ue_status == '已兑换'){
				item_str += '<td><span class="label label-success">'+item.ue_status+'</span></td>';
			}else{
				item_str += '<td><span class="label label-warning">'+item.ue_status+'</span></td>';
			}
			
			item_str += '<td>' + item.user_id + '</td>';
			item_str += '<td>' + item.community_id + '</td>';
		
			
			item_str += '</tr>';
			$("#audit > tbody").append(item_str);
		}
	}else{
		
		$("#audit > tbody").append("还没有兑换记录!");
	}

	
}
function selectAll(obj){
	if(obj.checked){    
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
}

function singleChk(){ 
    var chknum = $("input[name='subcheck']").not("input:disabled").size();//未失效的input标签个数
    var chk = 0; 
    $("input[name='subcheck']").not("input:disabled").each(function () {  
    	if (this.checked == true){
            chk++; 
    	}
    }); 
    if(chknum == chk){//全选 
    	$("input[name='SelectAll']").each(function () {  
    		 this.checked = true;
    	}); 
    }else{//不全选 
   	 	$("input[name='SelectAll']").each(function () {  
   	 		this.checked = false;
   	 	}); 
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
		"ajax_exchange_list?page=" + curr_page + "&random=" + Math.random(),
		function(data) {
			show_common_data(data.data);
			update_page_nav(data.data);
		}
	);
}


function createFormData(){
    if ($("#beginDate").val() == "") {
    	$("#tip").children("font").text("开始时间不能为空!");
		return false;
    }
    
    if ($("#endDate").val() == "") {
    	$("#tip").children("font").text("结束时间不能为空!");
		return false;
    }
    var beginDate=$("#beginDate").val();  
    var start = new Date(beginDate.replace("-", "/").replace("-", "/"));  
    var endDate = $("#endDate").val();  
    var end = new Date(endDate.replace("-", "/").replace("-", "/"));  
    if(end < start){  
    	alert("结束日期不能小于开始日期");
    	$("#tip").children("font").text("结束日期不能小于开始日期!");
		return false;
    }  
    if($("#e_community_id").val() == 0){
    	$("#tip").children("font").text("请选择小区!");
		return false;
    }
    return true;
	
}


function cleanText(){
	$("input[type=reset]").trigger("click");
	$("#tip").children("font").text("");

}

function cleanBootscrapModal(){
	$(".modal-title").empty();  
	$(".modal-footer").css("text-align","center");
	$(".modal-header").css("background-color","#eff3f8");
	$(".modal-header").css("border-top-color","#e4e9ee");
	$(".modal-header").css("box-shadow","none");
	$(".close").hide();
}


function exportRecord() {
    var form = $("<form>");   //定义一个form表单
    form.attr('style', 'display:none');   //在form表单中添加查询参数
    form.attr('target', '');
    form.attr('method', 'post');
    form.attr('action', "ajax_export_submit/");
    var str = $('#endDate').val()+";"+$("#beginDate").val()+";"+$("#e_community_id").val()+";"+$("#ue_status").val();
    var input1 = $('<input>');
    input1.attr('type', 'hidden');
    input1.attr('name', 'conditon');
    input1.attr('value', str);
    $('body').append(form);  //将表单放置在web中
    form.append(input1);  

   form.submit();

 }