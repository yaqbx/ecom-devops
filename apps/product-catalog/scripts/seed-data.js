/**
 * Seed data script for testing
 * Run: node scripts/seed-data.js
 */

const mongoose = require('mongoose');
require('dotenv').config();

const Equipment = require('../src/models/Equipment');

const sampleEquipment = [
  {
    sku: 'EXC-CAT-320-001',
    name: 'Caterpillar 320 Hydraulic Excavator',
    description: '20-ton hydraulic excavator with advanced hydraulics, ideal for construction sites',
    category: 'excavators',
    manufacturer: 'Caterpillar',
    model: '320',
    year: 2023,
    condition: 'new',
    hoursUsed: 0,
    specifications: {
      weight: 20000,
      height: 3050,
      width: 2990,
      length: 9460,
      power: 128,
      fuelType: 'diesel',
      maxLiftCapacity: 5000,
      fuelCapacity: 350
    },
    pricing: {
      dailyRate: 450,
      weeklyRate: 2500,
      monthlyRate: 8500,
      currency: 'USD'
    },
    availability: [{
      status: 'available',
      location: { city: 'Warsaw', region: 'Masovia' }
    }],
    images: [{ url: 'https://s7d2.scene7.com/is/image/Caterpillar/C10276062', alt: 'Cat 320 Excavator', isPrimary: true }],
    features: ['GPS tracking', 'Grade Control', 'Fuel Efficient', 'Low noise'],
    rentalOnly: false,
    insuranceRequired: true,
    depositRequired: true,
    depositAmount: 2000,
    tags: ['excavator', 'construction', 'caterpillar', 'new']
  },
  {
    sku: 'BULD-KOM-D61-002',
    name: 'Komatsu D61 Bulldozer',
    description: '15.5-ton crawler dozer with excellent pushing power',
    category: 'bulldozers',
    manufacturer: 'Komatsu',
    model: 'D61PXi-24',
    year: 2022,
    condition: 'excellent',
    hoursUsed: 450,
    specifications: {
      weight: 15500,
      height: 3100,
      width: 3200,
      length: 4850,
      power: 168,
      fuelType: 'diesel',
      operatingWeight: 15520
    },
    pricing: {
      dailyRate: 380,
      weeklyRate: 2100,
      monthlyRate: 7200,
      currency: 'USD'
    },
    availability: [{
      status: 'available',
      location: { city: 'Krakow', region: 'Lesser Poland' }
    }],
    images: [{ url: 'https://www.komatsu.eu/products/d61pxi-24', alt: 'Komatsu D61', isPrimary: true }],
    features: ['Intelligent Machine Control', 'Ripper included', 'GPS ready'],
    rentalOnly: true,
    insuranceRequired: true,
    depositRequired: true,
    depositAmount: 1500,
    tags: ['bulldozer', 'crawler', 'komatsu', 'grading']
  },
  {
    sku: 'CRANE-LIE-130-003',
    name: 'Liebherr LTM 1300 Mobile Crane',
    description: '300-ton all-terrain mobile crane for heavy lifting operations',
    category: 'cranes',
    manufacturer: 'Liebherr',
    model: 'LTM 1300-6.2',
    year: 2021,
    condition: 'good',
    hoursUsed: 1200,
    specifications: {
      weight: 60000,
      height: 4000,
      width: 3000,
      length: 16800,
      power: 500,
      fuelType: 'diesel',
      maxLiftCapacity: 300000,
      maxReach: 142
    },
    pricing: {
      dailyRate: 1200,
      weeklyRate: 7000,
      monthlyRate: 25000,
      currency: 'USD'
    },
    availability: [{
      status: 'available',
      location: { city: 'Gdansk', region: 'Pomerania' }
    }],
    images: [{ url: 'https://www.liebherr.com/products/mobile-cranes/ltm-1300-6.2', alt: 'Liebherr LTM 1300', isPrimary: true }],
    features: ['60m boom', 'Automatic setup', 'Remote control', 'All-terrain'],
    requiresOperator: true,
    rentalOnly: true,
    insuranceRequired: true,
    depositRequired: true,
    depositAmount: 10000,
    tags: ['crane', 'mobile', 'liebherr', 'lifting', 'heavy']
  },
  {
    sku: 'LOAD-VOL-L120-004',
    name: 'Volvo L120H Wheel Loader',
    description: '20-ton wheel loader with high breakout force',
    category: 'loaders',
    manufacturer: 'Volvo',
    model: 'L120H',
    year: 2023,
    condition: 'new',
    hoursUsed: 50,
    specifications: {
      weight: 18800,
      height: 3450,
      width: 3020,
      length: 8300,
      power: 230,
      fuelType: 'diesel',
      operatingWeight: 18800
    },
    pricing: {
      dailyRate: 320,
      weeklyRate: 1800,
      monthlyRate: 6000,
      purchasePrice: 285000,
      currency: 'USD'
    },
    availability: [{
      status: 'available',
      location: { city: 'Wroclaw', region: 'Lower Silesia' }
    }],
    images: [{ url: 'https://www.volvoce.com/united-states/en/products/wheel-loaders/l120h', alt: 'Volvo L120H', isPrimary: true }],
    features: ['OptiShift', 'On Board Weighing', 'Reversing camera', 'Auto bucket levelling'],
    rentalOnly: false,
    insuranceRequired: true,
    depositRequired: true,
    depositAmount: 3000,
    tags: ['loader', 'wheel', 'volvo', 'material handling']
  },
  {
    sku: 'DUMP-CAT-745-005',
    name: 'Caterpillar 745 Articulated Dump Truck',
    description: '45-ton payload capacity for mining and quarry operations',
    category: 'dump_trucks',
    manufacturer: 'Caterpillar',
    model: '745',
    year: 2022,
    condition: 'good',
    hoursUsed: 890,
    specifications: {
      weight: 41000,
      height: 3950,
      width: 3940,
      length: 11800,
      power: 469,
      fuelType: 'diesel',
      operatingWeight: 41000
    },
    pricing: {
      dailyRate: 550,
      weeklyRate: 3200,
      monthlyRate: 11000,
      currency: 'USD'
    },
    availability: [{
      status: 'rented',
      startDate: '2024-04-01',
      endDate: '2024-04-30',
      location: { city: 'Poznan', region: 'Greater Poland' }
    }],
    images: [{ url: 'https://s7d2.scene7.com/is/image/Caterpillar/C831332', alt: 'Cat 745', isPrimary: true }],
    features: ['45-ton payload', 'Cab suspension', 'Automatic traction control', 'Tailgate'],
    rentalOnly: true,
    insuranceRequired: true,
    depositRequired: true,
    depositAmount: 5000,
    tags: ['dump truck', 'articulated', 'caterpillar', 'mining', 'quarry']
  }
];

async function seedDatabase() {
  try {
    const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/equipment_catalog';
    
    console.log('Connecting to MongoDB...');
    await mongoose.connect(MONGODB_URI);
    console.log('Connected!');
    
    console.log('Clearing existing data...');
    await Equipment.deleteMany({});
    console.log('Existing data cleared.');
    
    console.log('Inserting sample equipment...');
    const result = await Equipment.insertMany(sampleEquipment);
    console.log(`✅ Seeded ${result.length} equipment items:`);
    result.forEach(item => console.log(`  - ${item.sku}: ${item.name}`));
    
    console.log('\nTest queries:');
    console.log(`  GET http://localhost:3000/api/v1/equipment`);
    console.log(`  GET http://localhost:3000/api/v1/search?q=excavator`);
    console.log(`  GET http://localhost:3000/api/v1/equipment/${result[0]._id}`);
    
  } catch (error) {
    console.error('❌ Seeding failed:', error.message);
  } finally {
    await mongoose.connection.close();
    console.log('\nDatabase connection closed.');
  }
}

seedDatabase();
