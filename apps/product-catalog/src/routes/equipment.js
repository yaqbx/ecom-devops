const express = require('express');
const router = express.Router();
const equipmentController = require('../controllers/equipmentController');
const { validateEquipment } = require('../middleware/validation');

// GET /api/v1/equipment - List all equipment with filters
router.get('/', equipmentController.getAllEquipment);

// GET /api/v1/equipment/:id - Get single equipment
router.get('/:id', equipmentController.getEquipmentById);

// GET /api/v1/equipment/:id/availability - Check availability
router.get('/:id/availability', equipmentController.checkAvailability);

// POST /api/v1/equipment - Create new equipment (admin)
router.post('/', validateEquipment, equipmentController.createEquipment);

// PUT /api/v1/equipment/:id - Update equipment
router.put('/:id', validateEquipment, equipmentController.updateEquipment);

// DELETE /api/v1/equipment/:id - Delete equipment
router.delete('/:id', equipmentController.deleteEquipment);

module.exports = router;
