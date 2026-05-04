const express = require('express');
const router = express.Router();
const Equipment = require('../models/Equipment');

// GET /api/v1/search?q=excavator&category=excavators&minPrice=100&maxPrice=500
router.get('/', async (req, res) => {
  try {
    const { 
      q, 
      category, 
      minPrice, 
      maxPrice, 
      manufacturer,
      condition,
      available,
      location,
      radius,
      sortBy = 'relevance',
      page = 1,
      limit = 20
    } = req.query;

    const query = { isActive: true };

    // Text search
    if (q) {
      query.$text = { $search: q };
    }

    // Category filter
    if (category) {
      query.category = category;
    }

    // Price range
    if (minPrice || maxPrice) {
      query['pricing.dailyRate'] = {};
      if (minPrice) query['pricing.dailyRate'].$gte = parseInt(minPrice);
      if (maxPrice) query['pricing.dailyRate'].$lte = parseInt(maxPrice);
    }

    // Manufacturer
    if (manufacturer) {
      query.manufacturer = new RegExp(manufacturer, 'i');
    }

    // Condition
    if (condition) {
      query.condition = condition;
    }

    // Availability
    if (available === 'true') {
      query['availability.status'] = 'available';
    }

    // Build sort
    let sort = {};
    switch (sortBy) {
      case 'price_asc':
        sort = { 'pricing.dailyRate': 1 };
        break;
      case 'price_desc':
        sort = { 'pricing.dailyRate': -1 };
        break;
      case 'newest':
        sort = { createdAt: -1 };
        break;
      case 'rating':
        sort = { rating: -1 };
        break;
      default:
        sort = q ? { score: { $meta: 'textScore' } } : { createdAt: -1 };
    }

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const [equipment, total] = await Promise.all([
      Equipment.find(query)
        .sort(sort)
        .skip(skip)
        .limit(parseInt(limit))
        .lean(),
      Equipment.countDocuments(query)
    ]);

    res.json({
      query: { q, category, minPrice, maxPrice },
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      },
      results: equipment
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
