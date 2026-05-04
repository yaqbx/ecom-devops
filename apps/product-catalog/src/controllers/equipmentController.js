const Equipment = require('../models/Equipment');

// GET /api/v1/equipment
exports.getAllEquipment = async (req, res) => {
  try {
    const { category, manufacturer, minPrice, maxPrice, page = 1, limit = 20 } = req.query;
    
    const query = { isActive: true };
    if (category) query.category = category;
    if (manufacturer) query.manufacturer = new RegExp(manufacturer, 'i');
    if (minPrice || maxPrice) {
      query['pricing.dailyRate'] = {};
      if (minPrice) query['pricing.dailyRate'].$gte = parseInt(minPrice);
      if (maxPrice) query['pricing.dailyRate'].$lte = parseInt(maxPrice);
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const [equipment, total] = await Promise.all([
      Equipment.find(query).skip(skip).limit(parseInt(limit)),
      Equipment.countDocuments(query)
    ]);

    res.json({
      data: equipment,
      pagination: { page: parseInt(page), limit: parseInt(limit), total, pages: Math.ceil(total / parseInt(limit)) }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// GET /api/v1/equipment/:id
exports.getEquipmentById = async (req, res) => {
  try {
    const equipment = await Equipment.findById(req.params.id);
    if (!equipment) return res.status(404).json({ error: 'Equipment not found' });
    res.json(equipment);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// GET /api/v1/equipment/:id/availability
exports.checkAvailability = async (req, res) => {
  try {
    const { startDate, endDate } = req.query;
    const equipment = await Equipment.findById(req.params.id);
    if (!equipment) return res.status(404).json({ error: 'Equipment not found' });
    
    // Simple availability check
    const isAvailable = equipment.availability.some(a => 
      a.status === 'available' || a.status === 'reserved'
    );
    
    res.json({ equipmentId: req.params.id, isAvailable, availability: equipment.availability });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// POST /api/v1/equipment
exports.createEquipment = async (req, res) => {
  try {
    const equipment = new Equipment(req.body);
    await equipment.save();
    res.status(201).json(equipment);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// PUT /api/v1/equipment/:id
exports.updateEquipment = async (req, res) => {
  try {
    const equipment = await Equipment.findByIdAndUpdate(
      req.params.id, 
      { ...req.body, updatedAt: Date.now() },
      { new: true, runValidators: true }
    );
    if (!equipment) return res.status(404).json({ error: 'Equipment not found' });
    res.json(equipment);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// DELETE /api/v1/equipment/:id
exports.deleteEquipment = async (req, res) => {
  try {
    const equipment = await Equipment.findByIdAndDelete(req.params.id);
    if (!equipment) return res.status(404).json({ error: 'Equipment not found' });
    res.json({ message: 'Equipment deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
