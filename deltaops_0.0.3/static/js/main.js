var term;
var client;
function openTerminal(options) {
    var client = new WSSHClient();
    term = new Terminal({cols: 80, rows: 25, screenKeys: true, useStyle:true});
    term.on('data', function (data) {
        client.sendClientData(data);
    });
    term.open();
    var htmlterm = $("#term");
    htmlterm.children().remove();
    $('.terminal').detach().appendTo('#term');
    term.write('Connecting...');
    client.connect({
        onError: function (error) {
            term.write('Error: ' + error + '\r\n');
            console.debug('error happened');
        },
        onConnect: function () {
            client.sendInitData(options);
            client.sendClientData('\r');
            console.debug('connection established');
        },
        onClose: function () {
            term.write("\rconnection closed")
            console.debug('connection reset by peer');
        },
        onData: function (data) {
            term.write(data);
            console.debug('get data:' + data);
        }
    })
}

function store(options) {
    window.localStorage.host = options.host
    window.localStorage.port = options.port
    window.localStorage.username = options.username
    window.localStorage.password = options.password
}

function check() {
    var result = $("#host").val() && $("#port").val() && $("#username").val() && $("#password").val()
    if (result) {
        var spans = $("fieldset").find("span")
        for (var i = 0; i < spans.length; i++) {
            if (spans[i].innerHTML.trim() != "correct") {
                return false
            }
        }
    }
    return result
}

function connect() {
    var remember = $("#remember").is(":checked")
    var options = {
        host: checkip[0],
        port: '22',
        //host: $("#host").val(),
        //port: $("#port").val(),
        //username: $("#username").val(),
        //password: $("#password").val()
    }
    console.log(checkip[0])
    if (checkip[0]){
        $("#login").click();
        $("#loginhostModalLabel").text("WebSSH Connect:"+checkip[0]);
        openTerminal(options);
    }else{
        alert("Pls select a server.");
    }
    /*
    if (remember) {
        store(options)
    }
    
    if (check()) {
        openTerminal(options)
    } else {
        alert("please check the form!")
    }
    */
}