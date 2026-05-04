const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

// GET /health - Health check endpoint
router.get('/', async (req, res) => {
  const health = {
    service: 'product-catalog',
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '1.0.0',
    checks: {
      database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
      memory: process.memoryUsage(),
      cpu: process.cpuUsage()
    }
  };

  const statusCode = health.checks.database === 'connected' ? 200 : 503;
  res.status(statusCode).json(health);
});

// GET /health/ready - Kubernetes readiness probe
router.get('/ready', async (req, res) => {
  const isReady = mongoose.connection.readyState === 1;
  res.status(isReady ? 200 : 503).json({ 
    ready: isReady,
    database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected'
  });
});

// GET /health/live - Kubernetes liveness probe
router.get('/live', (req, res) => {
  res.status(200).json({ alive: true });
});

module.exports = router;
