
    const socket = new WebSocket('ws://localhost:5000/ws');

    socket.onopen = function() {
        console.log('WebSocket connection established');
    };

    socket.onmessage = function(event) {
        console.log('Received from server:', event.data);
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };

    socket.onclose = function() {
        console.log('WebSocket connection closed');
    };
