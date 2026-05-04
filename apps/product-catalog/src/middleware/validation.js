exports.validateEquipment = (req, res, next) => {
  const { sku, name, category, manufacturer, model, year, pricing } = req.body;
  
  const required = { sku, name, category, manufacturer, model, year, pricing };
  const missing = Object.entries(required).filter(([_, v]) => !v).map(([k]) => k);
  
  if (missing.length > 0) {
    return res.status(400).json({ error: `Missing required fields: ${missing.join(', ')}` });
  }
  
  const validCategories = [
    'excavators', 'bulldozers', 'cranes', 'loaders', 'dump_trucks',
    'compactors', 'graders', 'forklifts', 'aerial_lifts', 'concrete_equipment', 'attachments'
  ];
  
  if (!validCategories.includes(category)) {
    return res.status(400).json({ error: `Invalid category. Must be one of: ${validCategories.join(', ')}` });
  }
  
  next();
};
