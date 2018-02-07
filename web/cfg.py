
web_name = "友邻"
jquery = "http://ajax.useso.com/ajax/libs/jquery/2.1.1/jquery.min.js" #jquery2.0以上
page_size = 12

#后台菜单，只支持3级
admin_menu_list = [
	{ 
		"id": 1, 
		"name": "后台管理", 
		"selected": True, 
		"child_menu": [
			{
				"id": 2,
				"name": "审核管理",
				"child_menu": [
					{
						"id": 5,
						"name": "地址审核",
						"url": "address_list.html",
						"param": "type:1", #demo type:1,id:2
					},
					{
						"id": 6,
						"name": "物业管理员审核",
						"url": "property_admin.html",
						"param": "type:4",
					},
					{
						"id": 7,
						"name": "管理员审核",
						"url": "common_admin.html",
						"param": "type:2",
					},
				]
			},
			{
				"id": 3,
				"name": "新闻管理",
				"child_menu": [
					{
						"id": 10,
						"name": "添加新闻",
						"url": "add_new.html",
						"param": "id:1",
					},
					{
						"id": 11,
						"name": "管理新闻",
						"url": "news_list.html",
						"param": "id:1",
					},		
				]
			},
			{
				"id": 4,
				"name": "意见统计",
				"child_menu": [
					{
						"id": 12,
						"name": "意见统计",
						"url": "feedback.html",
						"param": "type:1",
					},
				]
			},
			{
				"id": 14,
				"name": "物业管理",
				"child_menu": [
					{
						"id": 15,
						"name": "物业信息",
						"url": "property_info.html",
						"param": "type:1",
					},
				]
			},
			{
				"id": 13,
				"name": "管理员管理",
				"child_menu": [
					{
						"id": 8,
						"name": "修改密码",
						"url": "admin_pwd.html",
					},
					{
						"id": 9,
						"name": "管理员列表",
						"url": "admin_list.html",
					},
				]
			},
		]
	},
	
]
