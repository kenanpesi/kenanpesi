const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

app.use(cors());
app.use(express.static('public'));
app.use(express.json());

// Connected clients
let connectedPCs = new Map();

io.on('connection', (socket) => {
    console.log('New connection:', socket.id);

    // PC client registration
    socket.on('register-pc', (data) => {
        console.log('PC registered:', data.pcName);
        connectedPCs.set(data.pcName, socket.id);
        io.emit('pc-list-update', Array.from(connectedPCs.keys()));
    });

    // Handle PC disconnection
    socket.on('disconnect', () => {
        for (let [pcName, socketId] of connectedPCs.entries()) {
            if (socketId === socket.id) {
                connectedPCs.delete(pcName);
                break;
            }
        }
        io.emit('pc-list-update', Array.from(connectedPCs.keys()));
    });

    // Handle commands from web to PC
    socket.on('send-command', (data) => {
        const targetSocketId = connectedPCs.get(data.pcName);
        if (targetSocketId) {
            io.to(targetSocketId).emit('execute-command', data.command);
        }
    });

    // Handle command results from PC to web
    socket.on('command-result', (data) => {
        socket.broadcast.emit('command-output', data);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
