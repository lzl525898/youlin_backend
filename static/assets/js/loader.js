$(document).ready(function(){
   // alert($(window).height())
     var loader = $("#load-container");
     var w = 260;
     //var h = 260;
     loader.css('width' ,w+'px');
     loader.css('height' ,w+'px');
  
     $("#load-message").bind('click',function(){hideLoading();})
    // var loader = $("#loader");
});

function showLoading(){
    var loader = $("#load-container");
    var w = 260;
    loader.css('left' ,($(window).width()-w)/2+'px');
    loader.css('top' ,($(window).height()-w)/2+'px');
    var wrapper = $("#load-wrapper");
    wrapper.attr('class','load-wrapper');
}

function hideLoading(){
    var wrapper = $("#load-wrapper");
    wrapper.attr('class','load-wrapper hide');
}
