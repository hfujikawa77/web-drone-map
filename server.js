import express from 'express';
import dgram from 'dgram';
import { Server } from 'socket.io';
import {
    MavLinkPacketSplitter,
    MavLinkPacketParser,
    minimal,
    common,
    ardupilotmega,
} from 'node-mavlink';

const app = express();
const HTTP_PORT = 3000;
const UDP_PORT = 14551;
const UDP_HOST = '0.0.0.0';

app.use(express.static('public'));

const server = app.listen(HTTP_PORT, () => {
    console.log(`[HTTP Server] Listening on http://localhost:${HTTP_PORT}`);
});

const io = new Server(server);
const udpServer = dgram.createSocket('udp4');
const splitter = new MavLinkPacketSplitter();
const parser = new MavLinkPacketParser();

const REGISTRY = {
    ...minimal.REGISTRY,
    ...common.REGISTRY,
    ...ardupilotmega.REGISTRY,
};

let attitude = { roll: 0, pitch: 0, yaw: 0 };
let globalPosition = { lat: 0, lon: 0, alt: 0, speed: 0, heading: 0 };
const pathCoordinates = [];

io.on('connection', (socket) => {
    console.log('Web client connected.');
    socket.emit('status', 'Connected to server.');

    socket.emit('path', pathCoordinates);

    socket.on('disconnect', () => {
        console.log('Web client disconnected.');
    });
});

udpServer.on('message', (msg) => {
    splitter.write(msg);
});

splitter.pipe(parser).on('data', (packet) => {
    const clazz = REGISTRY[packet.header.msgid];
    if (clazz) {
        const data = packet.protocol.data(packet.payload, clazz);

        if (clazz.name === 'GlobalPositionInt') {
            globalPosition = {
                lat: data.lat / 1e7,
                lon: data.lon / 1e7,
                alt: data.alt / 1000,
                speed: Math.sqrt(data.vx ** 2 + data.vy ** 2) / 100,
                heading: data.hdg / 100,
            };
            console.log('Global Position:', globalPosition);

            pathCoordinates.push([globalPosition.lat, globalPosition.lon]);
            io.emit('position', globalPosition);
            io.emit('path', pathCoordinates);
        } else if (clazz.name === 'Attitude') {
            attitude = {
                roll: data.roll * (180 / Math.PI), // Convert roll to degrees
                pitch: data.pitch * (180 / Math.PI), // Convert pitch to degrees
                yaw: data.yaw * (180 / Math.PI), // Convert yaw to degrees
            };
            console.log('Attitude:', attitude);

            io.emit('attitude', attitude);
        }
    }
});

udpServer.on('error', (error) => {
    console.error('[UDP Server Error]', error);
    udpServer.close();
});

udpServer.bind(UDP_PORT, UDP_HOST, () => {
    console.log(`[UDP Server] Listening on ${UDP_HOST}:${UDP_PORT}`);
});
