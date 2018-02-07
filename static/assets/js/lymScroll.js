(function(window,doc){
	var style = document.createElement('style'); 
	style.type = 'text/css'; 

	style.innerHTML='.loadDiv{margin-top:-60px;text-align: center;position: relative;\
		width:100%;height:60px;-webkit-transition: margin-top .3s;transition: margin-top .3s;}\
	.pullDown {\
		position: relative;display:inline-block;border-radius: 50%;height: 40px;width: 40px;\
	    background: none repeat scroll 0 0 #fff;overflow:hidden;\
	    box-shadow: 0 0 10px rgba(0,0,0,.1) inset, 0 0 25px rgba(0,0,255,0.075);}\
	.pullDown:after {\
	    content: "";position: absolute;top: 3px; left: 3px;display: block;\
	    height: 34px; width: 34px;background: none repeat scroll 0 0 #fff;\
	    border-radius: 50%;}\
	.pullDown > span {position: absolute;height: 100%; width: 50%;overflow: hidden;}\
	.labelFont{font-size:13px;color:#ccc;}\
	.left  { left:0   }\
	.right { left:50% }\
	.anim {\
	    position: absolute;left: 100%; top: 0;height: 100%; width: 100%;\
	    border-radius: 20px;background: none repeat scroll 0 0 #ddd;\
	    opacity: 0.8;-webkit-animation: ui-spinner-rotate-left 3s infinite;\
	    animation: ui-spinner-rotate-left 3s infinite;\
	    -webkit-transform-origin: 0 50% 0;transform-origin: 0 50% 0;\
	    -webkit-animation-delay: 0s;-webkit-animation-duration:3s;\
	    -webkit-animation-timing-function: linear;\
	    animation-delay: 0s;animation-duration:3s;\
	    animation-timing-function: linear;}\
	.left .anim {border-bottom-left-radius: 0;border-top-left-radius: 0;}\
	.right .anim {\
	    border-bottom-right-radius: 0;border-top-right-radius: 0;left: -100%;\
	    -webkit-transform-origin: 100% 50% 0;transform-origin: 100% 50% 0;\
	    -webkit-animation-name: ui-spinner-rotate-right;\
	    -webkit-animation-delay:0;-webkit-animation-delay: 1.5s;\
	    animation-name: ui-spinner-rotate-right;\
	    animation-delay:0;animation-delay: 1.5s;}\
	@keyframes ui-spinner-rotate-left{\
	  0%,25%{transform:rotate(0deg)}\
	  50%,75%{transform:rotate(180deg)}\
	  100%{transform:rotate(360deg)}\
	}\
	@-webkit-keyframes ui-spinner-rotate-left{\
	  0%,25%{-webkit-transform:rotate(0deg)}\
	  50%,75%{-webkit-transform:rotate(180deg)}\
	  100%{-webkit-transform:rotate(360deg)}\
	}\
	@-webkit-keyframes ui-spinner-rotate-right{\
	  0%{-webkit-transform:rotate(0deg)}\
	  25%,50%{-webkit-transform:rotate(180deg)}\
	  75%,100%{-webkit-transform:rotate(360deg)}\
	}\
	@keyframes ui-spinner-rotate-right{\
	  0%{transform:rotate(0deg)}\
	  25%,50%{transform:rotate(180deg)}\
	  75%,100%{transform:rotate(360deg)}\
	}'; 

	document.getElementsByTagName('HEAD').item(0).appendChild(style);
	var div = doc.createElement('div');
	div.className = 'loadDiv';
	var span = doc.createElement('span');
	span.className = 'pullDown';
	
	var lspan = doc.createElement('span');
	lspan.className = 'left';
	var lanimSpan = doc.createElement('span');
	lanimSpan.className = 'anim';
	lspan.appendChild(lanimSpan);
	span.appendChild(lspan);
	var rspan = doc.createElement('span');
	rspan.className = 'right';
	var ranimSpan = doc.createElement('span');
	ranimSpan.className = 'anim';
	rspan.appendChild(ranimSpan);
	span.appendChild(rspan);
	var label = doc.createElement('div');
	label.id = "pullLabel";
	label.className = "labelFont";
	label.innerHTML = "下拉刷新";
	div.appendChild(span);
	div.appendChild(label);
	//var first=document.body.firstChild;//得到页面的第一个元素
	var wrap = doc.getElementsByClassName("scrollWrap")[0];
	doc.body.insertBefore(div,wrap);//把动态创建的div添加到下拉容器的上面
	
	//isTouchPad = (/hp-tablet/gi).test(navigator.appVersion),
	//hasTouch = 'ontouchstart' in window && !isTouchPad,
	hasTouch = true;
	//START_EV = hasTouch ? 'touchstart' : 'mousedown',
	//MOVE_EV = hasTouch ? 'touchmove' : 'mousemove',
	//END_EV = hasTouch ? 'touchend' : 'mouseup',
	//CANCEL_EV = hasTouch ? 'touchcancel' : 'mouseup';
	START_EV = 'touchstart',
	MOVE_EV = 'touchmove',
	END_EV = 'touchend',
	CANCEL_EV = 'touchcancel';
	var qScroll = function(callBack){
		var that = this;
		that.callBack = callBack;
		that._bind(START_EV,wrap);
		
	};
	qScroll.prototype = {
		handleEvent: function (e) {
			var that = this;
			switch(e.type) {
				case START_EV:
					if (!hasTouch && e.button !== 0) return;
						that._start(e);
					break;
				case MOVE_EV: that._move(e); break;
				case END_EV:
				case CANCEL_EV: that._end(e); break;
			}
		},
		_start:function(e){
			var self = this,point = hasTouch ? e.touches[0] : e;
			//记录刚刚开始按下的时间
			self.startTime = new Date() * 1;		
			//记录手指按下的坐标
			self.startY = point.pageY;
			self.actionDir = '';
			self._bind(MOVE_EV, window);
			self._bind(END_EV, window);
			self._bind(CANCEL_EV, window);
		},
		_move:function(e){			
			var self = this,point = hasTouch ? e.touches[0] : e;
			//兼容chrome android，阻止浏览器默认行为
			e.preventDefault();
			//计算手指的偏移量
			self.offsetY = point.pageY - self.startY;
			if(self.offsetY > 0){//下拉
				self.actionDir = 'down';
				if (self.offsetY > 60) {
					self.offsetY = 60;
					label.innerHTML="释放即可刷新";
				}
				div.style.cssText = "margin-top:"+(self.offsetY-60)+"px";
				wrap.style.cssText = "margin-top:"+self.offsetY+"px";
				var endTime = new Date() * 1;
				if(endTime-self.startTime > 2000){
					div.style.cssText = "margin-top:-60px";
				}
			}else{//上拉
				self.actionDir = 'up';
				//可以扩展上拉的需求
			}			
		},
		_end:function(e){
			var that = this;
			
			e.preventDefault();
			if(that.actionDir == 'down'){
				label.innerHTML="下拉刷新";
				div.style.cssText = "margin-top:-60px";
				wrap.style.cssText = "margin-top:0px";
			}
			if(that.callBack instanceof Function){	
				that.callBack();//执行回调函数
			}
			that._unbind(MOVE_EV, window);
			that._unbind(END_EV, window);
			that._unbind(CANCEL_EV, window);
		},
		
		_bind: function (type, el, bubble) {
			el.addEventListener(type, this, !!bubble);
		},

		_unbind: function (type, el, bubble) {
			el.removeEventListener(type, this, !!bubble);
		}
	};
	
	if (typeof exports !== 'undefined') {
		exports.qScroll = qScroll;
	}else{
		window.qScroll = qScroll;
	}

})(window,document)