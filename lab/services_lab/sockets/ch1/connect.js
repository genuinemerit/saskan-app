/* Chapter 1 WebSocket */
var ws = new WebSocket("ws://subhuti:8181");
ws.onpen = function(e) {
  console.log('Connection to server opened');
}
function sendMessage() {
  ws.send($('#message').val());
}
