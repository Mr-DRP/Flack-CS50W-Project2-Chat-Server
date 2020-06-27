document.addEventListener('DOMContentLoaded', () => {
    var element = document.getElementById("chatBox");
    element.scrollTop = element.scrollHeight;
    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#dismiss, .overlay').on('click', function () {
        $('#sidebar').removeClass('active');
        $('.overlay').removeClass('active');
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').addClass('active');
        $('.overlay').addClass('active');
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port );
    function sendMsg() {
        var message = document.getElementById("messageId").value;
        if(message.length == 0){
            return false;
        }
        socket.emit('sendMessage',{message});
        document.getElementById("messageId").value = null;
    };
    
    
    socket.on('connect', () => {
        sendMessage.onclick = sendMsg;
        var send = document.getElementById("messageId");
        send.addEventListener('keydown', function onEvent(event) {
            if (event.key === "Enter") {
                sendMsg();
            }
        });
        channelCreate.onclick = function () {
            var name = document.getElementById("channelName").value;
            if(name.length == 0){
                return false;
            }
            socket.emit('createChannel',{name});
            document.getElementById("channelName").value = null;
        };
    });

    socket.on('received message', data => {
        var template = Handlebars.templates.message;
        var msg = template({message: data.message,author: data.user,time: data.time})
        document.querySelector('#chatBox').insertAdjacentHTML('beforeend', msg);
        var element = document.getElementById("chatBox");
        element.scrollTop = element.scrollHeight;
    });

    socket.on('channel create', data => {
        var li = document.createElement("li");
        li.innerHTML = `<a href="/channel/${data.channelname}">#${data.channelname}</a>`
        document.querySelector('#channelList').append(li);
    });
       
});


