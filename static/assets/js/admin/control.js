 $(function() {
	 
	 //礼品兑换数量统计
	 $.ajax({
		 url:'ajax_Data_Statistics',
		 type:'POST',
		 enctype:'multipart/form-data',
		 dataType: 'JSON',
		 processData:false,
		 contentType:false,
		 success:function(data){
		 	 if (data.code==1){
		 		 alert(data.desc); 
			 }
			 else{
				 $("#cvbl_gift").html(data.data.convertible_gift);
				 $("#total_gift").text(data.data.total_gift);	
				 $("#un_address").html(data.data.unreviewed_address);
				 $("#total_address").text(data.data.total_address);
				 $("#un_exchange").html(data.data.un_exchange);
				 $("#total_exchange").text(data.data.total_exchange);
				 $("#su_count").html(data.data.suggest_count);
				 $("#total_suggest").text(data.data.total_suggest);	
			 } 
		 },
	 	});	 
 });
 function Page_Jump(name){
	 var temp = name;
	 $.ajax({     
	        type: "GET",     
	        url: "index?random=" + Math.random(),     
	        dataType: "html",  
	        data:{"action":temp},
	        success: function(data){  
	        	$(".main-content").html(data);
	        },
	});
	 
 }
 
 //onClick="Page_Jump()"
 /*	//圆盘
  			 var pieData1 = [
	{
		value:5,
		color:"#F38630",
		text: "已审核地址数",
	},
	{
		value : 6,
		color : "#E0E4CC",
		text:"未审核地址数",
	},

];
var myPie1 = new Chart(document.getElementById("canvas2").getContext("2d")).Pie(pieData1);*/
