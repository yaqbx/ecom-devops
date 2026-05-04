const mongoose = require('mongoose');

const specificationSchema = new mongoose.Schema({
  weight: { type: Number, required: true }, // kg
  height: { type: Number, required: true }, // cm
  width: { type: Number, required: true }, // cm
  length: { type: Number, required: true }, // cm
  power: { type: Number }, // hp or kW
  fuelType: { type: String, enum: ['diesel', 'electric', 'hybrid'] },
  operatingWeight: { type: Number },
  maxLiftCapacity: { type: Number },
  maxReach: { type: Number },
  fuelCapacity: { type: Number },
  customSpecs: [{ key: String, value: String }]
});

const availabilitySchema = new mongoose.Schema({
  startDate: { type: Date },
  endDate: { type: Date },
  status: { 
    type: String, 
    enum: ['available', 'rented', 'maintenance', 'reserved'],
    default: 'available'
  },
  location: {
    city: { type: String },
    region: { type: String },
    coordinates: {
      lat: { type: Number },
      lng: { type: Number }
    }
  }
});

const pricingSchema = new mongoose.Schema({
  dailyRate: { type: Number, required: true },
  weeklyRate: { type: Number },
  monthlyRate: { type: Number },
  purchasePrice: { type: Number },
  currency: { type: String, default: 'USD' }
});

const equipmentSchema = new mongoose.Schema({
  sku: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  description: { type: String, required: true },
  category: { 
    type: String, 
    required: true,
    enum: [
      'excavators',
      'bulldozers',
      'cranes',
      'loaders',
      'dump_trucks',
      'compactors',
      'graders',
      'forklifts',
      'aerial_lifts',
      'concrete_equipment',
      'attachments'
    ]
  },
  manufacturer: { type: String, required: true },
  model: { type: String, required: true },
  year: { type: Number, required: true },
  condition: {
    type: String,
    enum: ['new', 'excellent', 'good', 'fair'],
    default: 'good'
  },
  hoursUsed: { type: Number, default: 0 },
  specifications: specificationSchema,
  pricing: pricingSchema,
  availability: [availabilitySchema],
  images: [{ url: String, alt: String, isPrimary: Boolean }],
  documents: [{ title: String, url: String, type: String }], // manuals, specs
  features: [String],
  rentalOnly: { type: Boolean, default: false },
  purchaseOnly: { type: Boolean, default: false },
  requiresOperator: { type: Boolean, default: false },
  deliveryOptions: {
    available: { type: Boolean, default: true },
    radiusKm: { type: Number, default: 100 },
    baseFee: { type: Number, default: 0 }
  },
  insuranceRequired: { type: Boolean, default: true },
  depositRequired: { type: Boolean, default: true },
  depositAmount: { type: Number },
  tags: [String],
  rating: { type: Number, min: 0, max: 5, default: 0 },
  reviewCount: { type: Number, default: 0 },
  isActive: { type: Boolean, default: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Indexes for performance
equipmentSchema.index({ category: 1 });
equipmentSchema.index({ 'pricing.dailyRate': 1 });
equipmentSchema.index({ manufacturer: 1, model: 1 });
equipmentSchema.index({ tags: 1 });
equipmentSchema.index({ sku: 1 });
equipmentSchema.index({ name: 'text', description: 'text' }); // Full-text search

module.exports = mongoose.model('Equipment', equipmentSchema);
