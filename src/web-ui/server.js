#!/usr/bin/env node

/**
 * Claude Code Web UI Server
 * =========================
 * Interactive dashboard for Claude development
 * Based on: sugyan/claude-code-webui architecture
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const helmet = require('helmet');
const morgan = require('morgan');

require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.WEB_UI_PORT || 3000;
const HOST = process.env.WEB_UI_HOST || 'localhost';

// Middleware
app.use(helmet({
  contentSecurityPolicy: false // Allow inline scripts for development
}));
app.use(morgan('combined'));
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// API Routes
app.get('/api/status', (req, res) => {
  res.json({
    status: 'active',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: require('./package.json').version
  });
});

app.get('/api/system-info', (req, res) => {
  try {
    // Read system information
    const projectRoot = path.resolve(__dirname, '../..');
    const runtimePath = path.join(projectRoot, 'runtime');
    
    res.json({
      project_root: projectRoot,
      runtime_available: fs.existsSync(runtimePath),
      node_version: process.version,
      platform: process.platform,
      arch: process.arch,
      env: process.env.NODE_ENV || 'development'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/tasks', (req, res) => {
  try {
    const tasksPath = path.resolve(__dirname, '../../runtime/task_management/tasks.json');
    if (fs.existsSync(tasksPath)) {
      const tasks = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
      res.json(tasks);
    } else {
      res.json({ tasks: [], message: 'No tasks file found' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/memory-stats', (req, res) => {
  try {
    const memoryPath = path.resolve(__dirname, '../../runtime/memory/session_logs.json');
    if (fs.existsSync(memoryPath)) {
      const memory = JSON.parse(fs.readFileSync(memoryPath, 'utf8'));
      res.json(memory);
    } else {
      res.json({ memory: {}, message: 'No memory logs found' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// WebSocket connections
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.emit('welcome', {
    message: 'Connected to Claude Code Web UI',
    timestamp: new Date().toISOString()
  });
  
  socket.on('request-status', () => {
    socket.emit('status-update', {
      type: 'system-status',
      data: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: new Date().toISOString()
      }
    });
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`,
    available_routes: [
      '/api/status',
      '/api/system-info', 
      '/api/tasks',
      '/api/memory-stats'
    ]
  });
});

// Error handler
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({
    error: 'Internal Server Error',
    message: error.message
  });
});

// Start server
server.listen(PORT, HOST, () => {
  console.log(`=€ Claude Code Web UI Server running at http://${HOST}:${PORT}`);
  console.log(`=Ê Dashboard: http://${HOST}:${PORT}`);
  console.log(`= WebSocket: ws://${HOST}:${PORT}`);
  console.log(`=á API: http://${HOST}:${PORT}/api/status`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});

module.exports = { app, server, io };