const express = require('express');
const router = express.Router();

const categories = [
  { id: 'excavators', name: 'Excavators', icon: '🚜', description: 'Hydraulic excavators for digging and earthmoving' },
  { id: 'bulldozers', name: 'Bulldozers', icon: '🚧', description: 'Tracked and wheeled bulldozers for grading' },
  { id: 'cranes', name: 'Cranes', icon: '🏗️', description: 'Tower, mobile and crawler cranes' },
  { id: 'loaders', name: 'Loaders', icon: '🔄', description: 'Wheel and track loaders' },
  { id: 'dump_trucks', name: 'Dump Trucks', icon: '🚛', description: 'Articulated and rigid dump trucks' },
  { id: 'compactors', name: 'Compactors', icon: '📉', description: 'Soil and asphalt compactors' },
  { id: 'graders', name: 'Motor Graders', icon: '🛣️', description: 'Road graders for fine grading' },
  { id: 'forklifts', name: 'Forklifts', icon: '🏭', description: 'Material handling equipment' },
  { id: 'aerial_lifts', name: 'Aerial Lifts', icon: '⬆️', description: 'Scissor and boom lifts' },
  { id: 'concrete_equipment', name: 'Concrete Equipment', icon: '🏗️', description: 'Mixers, pumps and finishers' },
  { id: 'attachments', name: 'Attachments', icon: '🔧', description: 'Buckets, breakers, grapples and more' }
];

// GET /api/v1/categories
router.get('/', (req, res) => {
  res.json({
    count: categories.length,
    categories: categories
  });
});

// GET /api/v1/categories/:id
router.get('/:id', (req, res) => {
  const category = categories.find(c => c.id === req.params.id);
  if (!category) {
    return res.status(404).json({ error: 'Category not found' });
  }
  res.json(category);
});

module.exports = router;
