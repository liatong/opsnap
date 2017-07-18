

$(document).ready(function(){
    var session = $("#session").val();
    setTimeout(webSocketClient,100);
})

var webSocketServer = {
    'server' : "ws://172.17.92.167:8000/wechatServer",
    'init' : function(){
        $(this)[0].socketServer  = new WebSocket($(this)[0].server);
        
    },
    
}

function webSocketClient(){
    var host = "ws://172.17.92.167:8000/wechatServer";
    websocket = new WebSocket(host);
    websocket.onerror = function(evt){ console.log('error'); };
    websocket.onmessage = function(evt){
        
        console.log($.parseJSON(evt.data));
        var data = $.parseJSON(evt.data);
        
        ///console.log(evt['data']['data']);
       
        if( data['action'] == 'login' ){
            $("#user").append('<p>'+data['data']+'</p>');
        }else{
            $("#talking").append('<p>'+data['data']+'</p>')
        };
        
    };
}
function tologin(){
    var data = {};
    data['action']='login';
    data['data']=$("#session").val();
    window.websocket.send(JSON.stringify(data));
   
}

$("#tologin").click(function(){
    tologin();
})

$("#tosend").click(function(){
    var data={};
    data['action']='message';
    data['data']=$("#session").val()+':'+$("#content").val();
    window.websocket.send(JSON.stringify(data));
})
