const mongoose = require('mongoose');
require('dotenv').config();

const Equipment = require('../src/models/Equipment');

const equipment = [
  // ==================== EXCAVATORS ====================
  {
    sku: 'EXC-CAT-320-001',
    name: 'Caterpillar 320 Hydraulic Excavator',
    description: '20-ton hydraulic excavator with advanced hydraulics, ideal for medium to large construction sites. Features GPS tracking, grade control, and fuel-efficient engine.',
    category: 'excavators', manufacturer: 'Caterpillar', model: '320', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 20000, height: 3050, width: 2990, length: 9460, power: 128, fuelType: 'diesel', maxLiftCapacity: 5000, fuelCapacity: 350 },
    pricing: { dailyRate: 450, weeklyRate: 2500, monthlyRate: 8500 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/cat-320.jpg', alt: 'Cat 320 Excavator', isPrimary: true }],
    features: ['GPS tracking', 'Grade Control', 'Fuel Efficient', 'Low noise', 'Auto idle'], rentalOnly: false, requiresOperator: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['excavator', 'construction', 'caterpillar', 'new', '20-ton']
  },
  {
    sku: 'EXC-KOM-PC210-002',
    name: 'Komatsu PC210LC-11 Excavator',
    description: '21-ton excavator with long crawler undercarriage for superior stability. Excellent for heavy digging and trenching operations.',
    category: 'excavators', manufacturer: 'Komatsu', model: 'PC210LC-11', year: 2023,
    condition: 'excellent', hoursUsed: 320,
    specifications: { weight: 21000, height: 3000, width: 2800, length: 9500, power: 123, fuelType: 'diesel', maxLiftCapacity: 4800, fuelCapacity: 340 },
    pricing: { dailyRate: 420, weeklyRate: 2300, monthlyRate: 7800 },
    availability: [{ status: 'available', location: { city: 'Krakow', region: 'Lesser Poland' } }],
    images: [{ url: '/images/komatsu-pc210.jpg', alt: 'Komatsu PC210', isPrimary: true }],
    features: ['KomVision camera', 'Auto boom swing', 'KOMTRAX telematics', 'Eco mode'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['excavator', 'komatsu', '21-ton', 'crawler']
  },
  {
    sku: 'EXC-HIT-ZX330-003',
    name: 'Hitachi ZX330-6 Excavator',
    description: '33-ton class excavator with TRIAS HPU hydraulic system for powerful digging and fast cycle times. Perfect for quarry and heavy earthmoving.',
    category: 'excavators', manufacturer: 'Hitachi', model: 'ZX330-6', year: 2022,
    condition: 'good', hoursUsed: 1200,
    specifications: { weight: 33000, height: 3200, width: 3200, length: 11000, power: 202, fuelType: 'diesel', maxLiftCapacity: 8000, fuelCapacity: 480 },
    pricing: { dailyRate: 600, weeklyRate: 3400, monthlyRate: 11500 },
    availability: [{ status: 'rented', startDate: new Date('2025-06-01'), endDate: new Date('2025-06-30'), location: { city: 'Wroclaw', region: 'Lower Silesia' } }],
    images: [{ url: '/images/hitachi-zx330.jpg', alt: 'Hitachi ZX330', isPrimary: true }],
    features: ['TRIAS HPU', 'Diesel Particulate Filter', 'Large cab', 'ConSite monitoring'], rentalOnly: true, requiresOperator: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 5000,
    tags: ['excavator', 'hitachi', '33-ton', 'quarry', 'heavy']
  },
  {
    sku: 'EXC-VOL-EC220-004',
    name: 'Volvo EC220E Excavator',
    description: '22-ton excavator with CareTrack telematics and Volvo D6 engine. Low fuel consumption and excellent operator comfort.',
    category: 'excavators', manufacturer: 'Volvo', model: 'EC220E', year: 2023,
    condition: 'excellent', hoursUsed: 580,
    specifications: { weight: 22000, height: 3050, width: 2990, length: 9650, power: 135, fuelType: 'diesel', maxLiftCapacity: 5200, fuelCapacity: 360 },
    pricing: { dailyRate: 440, weeklyRate: 2500, monthlyRate: 8200 },
    availability: [{ status: 'available', location: { city: 'Gdansk', region: 'Pomerania' } }],
    images: [{ url: '/images/volvo-ec220.jpg', alt: 'Volvo EC220', isPrimary: true }],
    features: ['CareTrack', 'ECO mode', 'Slow-speed ventilation', 'ROPS cab'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['excavator', 'volvo', '22-ton', 'fuel-efficient']
  },
  {
    sku: 'EXC-LIE-R926-005',
    name: 'Liebherr R 926 Compact Excavator',
    description: '26-ton compact excavator with powerful Litronic control system. Ideal for urban worksites where space is limited.',
    category: 'excavators', manufacturer: 'Liebherr', model: 'R 926', year: 2022,
    condition: 'good', hoursUsed: 890,
    specifications: { weight: 26000, height: 3100, width: 3200, length: 10100, power: 150, fuelType: 'diesel', maxLiftCapacity: 6500, fuelCapacity: 400 },
    pricing: { dailyRate: 520, weeklyRate: 2900, monthlyRate: 9800 },
    availability: [{ status: 'maintenance', location: { city: 'Poznan', region: 'Greater Poland' } }],
    images: [{ url: '/images/liebherr-r926.jpg', alt: 'Liebherr R 926', isPrimary: true }],
    features: ['Litronic control', 'Compact design', 'Comfort cab', 'Low emissions'], rentalOnly: true, requiresOperator: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 3000,
    tags: ['excavator', 'liebherr', 'compact', 'urban']
  },

  // ==================== BULLDOZERS ====================
  {
    sku: 'BULD-CAT-D6-006',
    name: 'Caterpillar D6 XE Dozer',
    description: 'Next-generation electric drive dozer with up to 35% better fuel efficiency. Ideal for grading, backfilling, and site preparation.',
    category: 'bulldozers', manufacturer: 'Caterpillar', model: 'D6 XE', year: 2024,
    condition: 'new', hoursUsed: 10,
    specifications: { weight: 20500, height: 3300, width: 3200, length: 5300, power: 190, fuelType: 'diesel', operatingWeight: 20500 },
    pricing: { dailyRate: 480, weeklyRate: 2700, monthlyRate: 9200 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/cat-d6.jpg', alt: 'Cat D6 XE', isPrimary: true }],
    features: ['Electric drive', 'Grade control ready', 'AccuGrade', 'Remote control'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2500,
    tags: ['bulldozer', 'caterpillar', 'electric-drive', 'new']
  },
  {
    sku: 'BULD-KOM-D61-007',
    name: 'Komatsu D61EXi-24 Dozer',
    description: 'Intelligent Machine Control dozer with GPS-based grade control. Semi-U blade for superior material retention.',
    category: 'bulldozers', manufacturer: 'Komatsu', model: 'D61EXi-24', year: 2023,
    condition: 'excellent', hoursUsed: 450,
    specifications: { weight: 16500, height: 3100, width: 3200, length: 4850, power: 168, fuelType: 'diesel', operatingWeight: 16520 },
    pricing: { dailyRate: 380, weeklyRate: 2100, monthlyRate: 7200 },
    availability: [{ status: 'available', location: { city: 'Krakow', region: 'Lesser Poland' } }],
    images: [{ url: '/images/komatsu-d61.jpg', alt: 'Komatsu D61', isPrimary: true }],
    features: ['iMC 2.0', 'Ripper included', 'Auto grade control', 'LCD monitor'], rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 1500,
    tags: ['bulldozer', 'komatsu', 'imc', 'grading']
  },
  {
    sku: 'BULD-LIE-PR736-008',
    name: 'Liebherr PR 736 LGP Dozer',
    description: 'Low Ground Pressure dozer with extra-wide tracks for soft ground conditions. Excellent for swamp and wetland reclamation.',
    category: 'bulldozers', manufacturer: 'Liebherr', model: 'PR 736 LGP', year: 2022,
    condition: 'good', hoursUsed: 1100,
    specifications: { weight: 18500, height: 3300, width: 3700, length: 5100, power: 175, fuelType: 'diesel', operatingWeight: 18500 },
    pricing: { dailyRate: 420, weeklyRate: 2400, monthlyRate: 8000 },
    availability: [{ status: 'available', location: { city: 'Szczecin', region: 'West Pomerania' } }],
    images: [{ url: '/images/liebherr-pr736.jpg', alt: 'Liebherr PR 736', isPrimary: true }],
    features: ['LGP tracks', 'Pilot control', 'ROPS/FOPS cab', 'Reverse fan'], rentalOnly: true, requiresOperator: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['bulldozer', 'liebherr', 'lgp', 'wetlands']
  },

  // ==================== CRANES ====================
  {
    sku: 'CRANE-LIE-LTM-009',
    name: 'Liebherr LTM 1300-6.2 Mobile Crane',
    description: '300-ton all-terrain crane with 60m telescopic boom. 6-axle chassis for excellent mobility. Complete with outrigger mats and load charts.',
    category: 'cranes', manufacturer: 'Liebherr', model: 'LTM 1300-6.2', year: 2023,
    condition: 'excellent', hoursUsed: 800,
    specifications: { weight: 60000, height: 4000, width: 3000, length: 16800, power: 500, fuelType: 'diesel', maxLiftCapacity: 300000, maxReach: 142 },
    pricing: { dailyRate: 1200, weeklyRate: 7000, monthlyRate: 25000 },
    availability: [{ status: 'available', location: { city: 'Gdansk', region: 'Pomerania' } }],
    images: [{ url: '/images/liebherr-ltm1300.jpg', alt: 'Liebherr LTM 1300', isPrimary: true }],
    features: ['60m boom', 'VarioBase', 'LICCON control', 'All-terrain'], requiresOperator: true, rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 10000,
    tags: ['crane', 'mobile', 'liebherr', '300-ton', 'all-terrain']
  },
  {
    sku: 'CRANE-TAD-GT-010',
    name: 'Tadano GR-1000XL Rough Terrain Crane',
    description: '100-ton rough terrain crane with 44m 5-section boom. Ideal for off-road jobsites and industrial applications.',
    category: 'cranes', manufacturer: 'Tadano', model: 'GR-1000XL', year: 2023,
    condition: 'new', hoursUsed: 50,
    specifications: { weight: 42000, height: 3700, width: 3200, length: 14000, power: 320, fuelType: 'diesel', maxLiftCapacity: 100000, maxReach: 55 },
    pricing: { dailyRate: 850, weeklyRate: 5000, monthlyRate: 17000 },
    availability: [{ status: 'available', location: { city: 'Katowice', region: 'Silesia' } }],
    images: [{ url: '/images/tadano-gr1000.jpg', alt: 'Tadano GR-1000XL', isPrimary: true }],
    features: ['5-section boom', 'HELLO NET telematics', 'Carry deck', 'Outrigger monitoring'], requiresOperator: true, rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 7000,
    tags: ['crane', 'tadano', 'rough-terrain', '100-ton']
  },
  {
    sku: 'CRANE-CAT-CK-011',
    name: 'Caterpillar CK320-2 Crawler Crane',
    description: '20-ton crawler crane with lattice boom. Self-assembly capability. Perfect for foundation and piling work.',
    category: 'cranes', manufacturer: 'Caterpillar', model: 'CK320-2', year: 2022,
    condition: 'good', hoursUsed: 1500,
    specifications: { weight: 22000, height: 3500, width: 3300, length: 7200, power: 130, fuelType: 'diesel', maxLiftCapacity: 20000, maxReach: 40 },
    pricing: { dailyRate: 550, weeklyRate: 3200, monthlyRate: 10500 },
    availability: [{ status: 'available', location: { city: 'Rzeszow', region: 'Subcarpathia' } }],
    images: [{ url: '/images/cat-ck320.jpg', alt: 'Cat CK320', isPrimary: true }],
    features: ['Lattice boom', 'Self-assembly', 'Swing brake', 'Load moment indicator'], requiresOperator: true, rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 4000,
    tags: ['crane', 'caterpillar', 'crawler', '20-ton']
  },

  // ==================== LOADERS ====================
  {
    sku: 'LOAD-VOL-L120-012',
    name: 'Volvo L120H Wheel Loader',
    description: '20-ton wheel loader with OptiShift technology for up to 15% fuel savings. High breakout force for demanding applications.',
    category: 'loaders', manufacturer: 'Volvo', model: 'L120H', year: 2024,
    condition: 'new', hoursUsed: 50,
    specifications: { weight: 18800, height: 3450, width: 3020, length: 8300, power: 230, fuelType: 'diesel', operatingWeight: 18800 },
    pricing: { dailyRate: 350, weeklyRate: 2000, monthlyRate: 6500, purchasePrice: 285000 },
    availability: [{ status: 'available', location: { city: 'Lodz', region: 'Lodz' } }],
    images: [{ url: '/images/volvo-l120.jpg', alt: 'Volvo L120H', isPrimary: true }],
    features: ['OptiShift', 'On Board Weighing', 'Reverse camera', 'Auto bucket level'], rentalOnly: false, purchaseOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['loader', 'wheel', 'volvo', '20-ton', 'material handling']
  },
  {
    sku: 'LOAD-CAT-950-013',
    name: 'Caterpillar 950 GC Wheel Loader',
    description: 'Reliable mid-size wheel loader with proven Cat C7 engine. Lower operating costs without sacrificing productivity.',
    category: 'loaders', manufacturer: 'Caterpillar', model: '950 GC', year: 2023,
    condition: 'excellent', hoursUsed: 400,
    specifications: { weight: 17500, height: 3400, width: 2900, length: 8100, power: 213, fuelType: 'diesel', operatingWeight: 17500 },
    pricing: { dailyRate: 320, weeklyRate: 1800, monthlyRate: 6000 },
    availability: [{ status: 'available', location: { city: 'Bydgoszcz', region: 'Kuyavia-Pomerania' } }],
    images: [{ url: '/images/cat-950.jpg', alt: 'Cat 950 GC', isPrimary: true }],
    features: ['Cat C7 engine', 'Fusion AC cab', 'STIC steering', 'Payload control'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 1500,
    tags: ['loader', 'caterpillar', 'wheel', 'mid-size']
  },
  {
    sku: 'LOAD-JCB-435-014',
    name: 'JCB 435S Wheel Loader',
    description: 'Articulated wheel loader with JCB EcoMAX engine. Powershift transmission with torque lock-up for faster cycle times.',
    category: 'loaders', manufacturer: 'JCB', model: '435S', year: 2022,
    condition: 'good', hoursUsed: 950,
    specifications: { weight: 16500, height: 3350, width: 2850, length: 7900, power: 196, fuelType: 'diesel', operatingWeight: 16500 },
    pricing: { dailyRate: 300, weeklyRate: 1700, monthlyRate: 5500 },
    availability: [{ status: 'available', location: { city: 'Lublin', region: 'Lublin' } }],
    images: [{ url: '/images/jcb-435.jpg', alt: 'JCB 435S', isPrimary: true }],
    features: ['EcoMAX engine', 'Torque lock-up', 'Command Plus cab', 'LiveLink telematics'], rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 1500,
    tags: ['loader', 'jcb', 'articulated', 'wheel']
  },
  {
    sku: 'LOAD-KOM-WA270-015',
    name: 'Komatsu WA270-8 Wheel Loader',
    description: 'Versatile 16-ton loader with dual-mode transmission. Excellent fuel economy and superior digging performance.',
    category: 'loaders', manufacturer: 'Komatsu', model: 'WA270-8', year: 2023,
    condition: 'excellent', hoursUsed: 300,
    specifications: { weight: 16000, height: 3300, width: 2800, length: 7700, power: 185, fuelType: 'diesel', operatingWeight: 16000 },
    pricing: { dailyRate: 310, weeklyRate: 1750, monthlyRate: 5800 },
    availability: [{ status: 'available', location: { city: 'Torun', region: 'Kuyavia-Pomerania' } }],
    images: [{ url: '/images/komatsu-wa270.jpg', alt: 'Komatsu WA270', isPrimary: true }],
    features: ['KOMTRAX', 'Dual-mode transmission', 'Spacious cab', 'Auto idle stop'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 1500,
    tags: ['loader', 'komatsu', 'wheel', '16-ton']
  },

  // ==================== DUMP TRUCKS ====================
  {
    sku: 'DUMP-CAT-745-016',
    name: 'Caterpillar 745 Articulated Dump Truck',
    description: '45-ton capacity articulated dump truck. Superior traction with 6x6 drive. Ideal for mining and large earthmoving projects.',
    category: 'dump_trucks', manufacturer: 'Caterpillar', model: '745', year: 2023,
    condition: 'excellent', hoursUsed: 600,
    specifications: { weight: 41000, height: 3950, width: 3940, length: 11800, power: 469, fuelType: 'diesel', operatingWeight: 41000 },
    pricing: { dailyRate: 600, weeklyRate: 3500, monthlyRate: 12000 },
    availability: [{ status: 'available', location: { city: 'Walbrzych', region: 'Lower Silesia' } }],
    images: [{ url: '/images/cat-745.jpg', alt: 'Cat 745 ADT', isPrimary: true }],
    features: ['6x6 drive', 'Payload weighing', 'Traction control', 'Differential lock'], rentalOnly: true, requiresOperator: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 5000,
    tags: ['dump-truck', 'articulated', 'caterpillar', '45-ton']
  },
  {
    sku: 'DUMP-VOL-A40-017',
    name: 'Volvo A40G Articulated Hauler',
    description: '40-ton hauler with Volvo V-ACT engine. Fully automatic transmission with 6 forward gears. Excellent off-road mobility.',
    category: 'dump_trucks', manufacturer: 'Volvo', model: 'A40G', year: 2024,
    condition: 'new', hoursUsed: 20,
    specifications: { weight: 38000, height: 3800, width: 3700, length: 11500, power: 440, fuelType: 'diesel', operatingWeight: 38000 },
    pricing: { dailyRate: 580, weeklyRate: 3300, monthlyRate: 11000 },
    availability: [{ status: 'available', location: { city: 'Zielona Gora', region: 'Lubusz' } }],
    images: [{ url: '/images/volvo-a40.jpg', alt: 'Volvo A40G', isPrimary: true }],
    features: ['V-ACT engine', 'Fully auto transmission', 'Load & Dump Brakes', 'HaulerVision camera'], rentalOnly: true, requiresOperator: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 4000,
    tags: ['dump-truck', 'articulated', 'volvo', '40-ton']
  },
  {
    sku: 'DUMP-BELL-B50-018',
    name: 'Bell B50E Articulated Dump Truck',
    description: '50-ton payload ADT with Mercedes-Benz engine. Known for rugged reliability in African and European mining operations.',
    category: 'dump_trucks', manufacturer: 'Bell', model: 'B50E', year: 2022,
    condition: 'good', hoursUsed: 1300,
    specifications: { weight: 43000, height: 4000, width: 3800, length: 12000, power: 490, fuelType: 'diesel', operatingWeight: 43000 },
    pricing: { dailyRate: 650, weeklyRate: 3800, monthlyRate: 13000 },
    availability: [{ status: 'rented', startDate: new Date('2025-05-15'), endDate: new Date('2025-07-15'), location: { city: 'Belchatow', region: 'Lodz' } }],
    images: [{ url: '/images/bell-b50.jpg', alt: 'Bell B50E', isPrimary: true }],
    features: ['MB engine', 'Wet disc brakes', 'Emergency steering', 'Central tire inflation'], rentalOnly: true, requiresOperator: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 6000,
    tags: ['dump-truck', 'bell', '50-ton', 'mining', 'articulated']
  },

  // ==================== COMPACTORS ====================
  {
    sku: 'COMP-BOM-BW213-019',
    name: 'Bomag BW 213 DH-5 Smooth Drum Roller',
    description: '13-ton tandem vibratory roller with Economizer system. Ideal for asphalt and base course compaction on road construction.',
    category: 'compactors', manufacturer: 'Bomag', model: 'BW 213 DH-5', year: 2023,
    condition: 'excellent', hoursUsed: 400,
    specifications: { weight: 13000, height: 3000, width: 2130, length: 5600, power: 100, fuelType: 'diesel', operatingWeight: 13000 },
    pricing: { dailyRate: 250, weeklyRate: 1400, monthlyRate: 4500 },
    availability: [{ status: 'available', location: { city: 'Olsztyn', region: 'Warmia-Masuria' } }],
    images: [{ url: '/images/bomag-bw213.jpg', alt: 'Bomag BW 213', isPrimary: true }],
    features: ['Economizer', 'Vibration monitoring', 'ROPS cab', 'Water sprinkler'], rentalOnly: true,
    insuranceRequired: true, depositRequired: false,
    tags: ['compactor', 'roller', 'bomag', 'asphalt', '13-ton']
  },
  {
    sku: 'COMP-CAT-CS56-020',
    name: 'Caterpillar CS56 Vibratory Soil Compactor',
    description: '12-ton padfoot compactor for cohesive soil compaction. Cat C4.4 engine with patented vibration system.',
    category: 'compactors', manufacturer: 'Caterpillar', model: 'CS56', year: 2022,
    condition: 'good', hoursUsed: 850,
    specifications: { weight: 12000, height: 2900, width: 2130, length: 5800, power: 107, fuelType: 'diesel', operatingWeight: 12000 },
    pricing: { dailyRate: 230, weeklyRate: 1300, monthlyRate: 4200 },
    availability: [{ status: 'available', location: { city: 'Kielce', region: 'Swietokrzyskie' } }],
    images: [{ url: '/images/cat-cs56.jpg', alt: 'Cat CS56', isPrimary: true }],
    features: ['Padfoot drum', 'Vibratory system', 'ROPS/FOPS', 'Center pivot'], rentalOnly: false,
    insuranceRequired: true, depositRequired: false,
    tags: ['compactor', 'caterpillar', 'soil', 'padfoot']
  },
  {
    sku: 'COMP-HAM-HD12-021',
    name: 'Hamm HD 12 VV Tandem Roller',
    description: 'Compact 1.2-ton tandem roller with dual vibration. Perfect for small repair works, walkways, and parking lots.',
    category: 'compactors', manufacturer: 'Hamm', model: 'HD 12 VV', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 1200, height: 2200, width: 1000, length: 2600, power: 13, fuelType: 'diesel', operatingWeight: 1200 },
    pricing: { dailyRate: 90, weeklyRate: 500, monthlyRate: 1600 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/hamm-hd12.jpg', alt: 'Hamm HD 12', isPrimary: true }],
    features: ['Dual vibration', 'Water spray', 'Foldable ROPS', 'Transport wheels'], rentalOnly: false,
    insuranceRequired: false, depositRequired: false, depositAmount: 300,
    tags: ['compactor', 'roller', 'hamm', 'small', 'walk-behind']
  },

  // ==================== GRADERS ====================
  {
    sku: 'GRAD-CAT-140-022',
    name: 'Caterpillar 140 Motor Grader',
    description: 'Standard 14-foot grader with Cat C7 engine. Excellent for road maintenance, grading, and snow removal.',
    category: 'graders', manufacturer: 'Caterpillar', model: '140', year: 2023,
    condition: 'excellent', hoursUsed: 350,
    specifications: { weight: 16000, height: 3300, width: 2500, length: 8600, power: 200, fuelType: 'diesel', operatingWeight: 16000 },
    pricing: { dailyRate: 360, weeklyRate: 2100, monthlyRate: 6800 },
    availability: [{ status: 'available', location: { city: 'Plock', region: 'Masovia' } }],
    images: [{ url: '/images/cat-140.jpg', alt: 'Cat 140 Grader', isPrimary: true }],
    features: ['Grade control ready', 'All-wheel drive', 'Articulated frame', 'Cab with HVAC'], rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['grader', 'caterpillar', 'road', 'grading']
  },
  {
    sku: 'GRAD-VOL-G930-023',
    name: 'Volvo G930 Motor Grader',
    description: 'Versatile grader with Volvo D7 engine and load-sensing hydraulics. 14-foot moldboard for precise grading.',
    category: 'graders', manufacturer: 'Volvo', model: 'G930', year: 2022,
    condition: 'good', hoursUsed: 720,
    specifications: { weight: 15500, height: 3300, width: 2500, length: 8700, power: 185, fuelType: 'diesel', operatingWeight: 15500 },
    pricing: { dailyRate: 340, weeklyRate: 2000, monthlyRate: 6400 },
    availability: [{ status: 'available', location: { city: 'Gorzow', region: 'Lubusz' } }],
    images: [{ url: '/images/volvo-g930.jpg', alt: 'Volvo G930', isPrimary: true }],
    features: ['Load-sensing hydraulics', 'Auto grade control', 'Dual joystick', 'CareTrack'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 1800,
    tags: ['grader', 'volvo', '14-foot', 'road']
  },
  {
    sku: 'GRAD-KOM-GD675-024',
    name: 'Komatsu GD675-6 Motor Grader',
    description: 'Heavy-duty grader with hydraulic blade control and KOMTRAX telematics. 14-foot moldboard for demanding applications.',
    category: 'graders', manufacturer: 'Komatsu', model: 'GD675-6', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 17000, height: 3350, width: 2550, length: 8800, power: 210, fuelType: 'diesel', operatingWeight: 17000 },
    pricing: { dailyRate: 380, weeklyRate: 2200, monthlyRate: 7000 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/komatsu-gd675.jpg', alt: 'Komatsu GD675', isPrimary: true }],
    features: ['KOMTRAX', 'Auto-shift transmission', 'Tiltable steering', 'Large cab'], rentalOnly: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['grader', 'komatsu', 'heavy-duty', 'new']
  },

  // ==================== FORKLIFTS ====================
  {
    sku: 'FORK-TOY-FD70-025',
    name: 'Toyota FD70 Forklift',
    description: '7-ton diesel forklift with Toyota engine. Ideal for heavy warehouse and container loading operations.',
    category: 'forklifts', manufacturer: 'Toyota', model: 'FD70', year: 2023,
    condition: 'excellent', hoursUsed: 280,
    specifications: { weight: 9000, height: 2450, width: 1500, length: 4000, power: 55, fuelType: 'diesel', operatingWeight: 9000 },
    pricing: { dailyRate: 160, weeklyRate: 900, monthlyRate: 3000 },
    availability: [{ status: 'available', location: { city: 'Gdynia', region: 'Pomerania' } }],
    images: [{ url: '/images/toyota-fd70.jpg', alt: 'Toyota FD70', isPrimary: true }],
    features: ['Full free lift', 'Side shift', 'Pneumatic tires', 'Load capacity indicator'], rentalOnly: false,
    insuranceRequired: true, depositRequired: false, depositAmount: 1000,
    tags: ['forklift', 'toyota', 'diesel', '7-ton']
  },
  {
    sku: 'FORK-HYL-H16-026',
    name: 'Hyster H16XM-6 Forklift',
    description: '16-ton heavy-duty forklift with diesel engine. Designed for lumber yards, steel service centers, and heavy manufacturing.',
    category: 'forklifts', manufacturer: 'Hyster', model: 'H16XM-6', year: 2022,
    condition: 'good', hoursUsed: 1100,
    specifications: { weight: 19000, height: 2600, width: 1900, length: 4800, power: 90, fuelType: 'diesel', operatingWeight: 19000 },
    pricing: { dailyRate: 280, weeklyRate: 1600, monthlyRate: 5200 },
    availability: [{ status: 'available', location: { city: 'Dabrowa Gornicza', region: 'Silesia' } }],
    images: [{ url: '/images/hyster-h16.jpg', alt: 'Hyster H16XM', isPrimary: true }],
    features: ['Double reduction drive', 'Multi-function valve', 'Cushion tires', 'Excellent visibility'], rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 2000,
    tags: ['forklift', 'hyster', 'diesel', '16-ton', 'heavy-duty']
  },
  {
    sku: 'FORK-JUNG-TFZ-027',
    name: 'Jungheinrich TFZ 10 Reach Stacker',
    description: '10-ton reach stacker for container handling. 4-stage mast with up to 7m lift height. Ideal for intermodal terminals.',
    category: 'forklifts', manufacturer: 'Jungheinrich', model: 'TFZ 10', year: 2023,
    condition: 'excellent', hoursUsed: 500,
    specifications: { weight: 14000, height: 3000, width: 2000, length: 5500, power: 70, fuelType: 'diesel', operatingWeight: 14000 },
    pricing: { dailyRate: 350, weeklyRate: 2000, monthlyRate: 6500 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/jung-reach.jpg', alt: 'Jungheinrich TFZ 10', isPrimary: true }],
    features: ['4-stage mast', 'Container spreader', 'Reach capability', 'Side shift'], rentalOnly: true, requiresOperator: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 3000,
    tags: ['forklift', 'reach-stacker', 'jungheinrich', 'container']
  },

  // ==================== AERIAL LIFTS ====================
  {
    sku: 'AERIAL-GEN-Z60-028',
    name: 'Genie Z-60/37 Articulated Boom Lift',
    description: '60ft articulating boom lift with 30ft outreach. Zero tail swing design. Ideal for facade and maintenance work.',
    category: 'aerial_lifts', manufacturer: 'Genie', model: 'Z-60/37', year: 2023,
    condition: 'excellent', hoursUsed: 200,
    specifications: { weight: 7500, height: 2000, width: 2300, length: 7500, power: 22, fuelType: 'diesel', maxLiftCapacity: 230, maxReach: 18 },
    pricing: { dailyRate: 200, weeklyRate: 1100, monthlyRate: 3600 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/genie-z60.jpg', alt: 'Genie Z-60/37', isPrimary: true }],
    features: ['Zero tail swing', '4WD', 'Jib boom', 'Platform rotation'], rentalOnly: true,
    insuranceRequired: true, depositRequired: false, depositAmount: 1000,
    tags: ['aerial-lift', 'boom', 'genie', '60ft', 'articulating']
  },
  {
    sku: 'AERIAL-JLG-860-029',
    name: 'JLG 860SJ Telescopic Boom Lift',
    description: '86ft telescopic boom lift with up to 80ft horizontal outreach. Best-in-class platform capacity for welding and structural work.',
    category: 'aerial_lifts', manufacturer: 'JLG', model: '860SJ', year: 2022,
    condition: 'good', hoursUsed: 650,
    specifications: { weight: 14500, height: 2600, width: 2500, length: 10500, power: 37, fuelType: 'diesel', maxLiftCapacity: 340, maxReach: 26 },
    pricing: { dailyRate: 280, weeklyRate: 1600, monthlyRate: 5200 },
    availability: [{ status: 'available', location: { city: 'Tarnow', region: 'Lesser Poland' } }],
    images: [{ url: '/images/jlg-860.jpg', alt: 'JLG 860SJ', isPrimary: true }],
    features: ['Reach plus boom', 'QuickMark', 'Platform offset', 'Engine shutdown'], rentalOnly: true, requiresOperator: false,
    insuranceRequired: true, depositRequired: true, depositAmount: 1500,
    tags: ['aerial-lift', 'boom', 'jlg', '86ft', 'telescopic']
  },
  {
    sku: 'AERIAL-SKY-SJIII-030',
    name: 'Skyjack SJIII 3219 Electric Scissor Lift',
    description: '19ft compact electric scissor lift. Zero emissions for indoor use. Narrow width for doorways and tight spaces.',
    category: 'aerial_lifts', manufacturer: 'Skyjack', model: 'SJIII 3219', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 1300, height: 1800, width: 760, length: 1900, power: 2, fuelType: 'electric', maxLiftCapacity: 227 },
    pricing: { dailyRate: 65, weeklyRate: 350, monthlyRate: 1100 },
    availability: [{ status: 'available', location: { city: 'Krakow', region: 'Lesser Poland' } }],
    images: [{ url: '/images/skyjack-sjiii.jpg', alt: 'Skyjack SJIII 3219', isPrimary: true }],
    features: ['Electric', 'Compact', 'Pothole protection', 'Swing-out tray'], rentalOnly: true,
    insuranceRequired: false, depositRequired: false, depositAmount: 300,
    tags: ['aerial-lift', 'scissor', 'skyjack', 'electric', 'indoor']
  },

  // ==================== CONCRETE EQUIPMENT ====================
  {
    sku: 'CONC-PUTZ-BSF-031',
    name: 'Putzmeister BSF 58-6.16H Concrete Boom Pump',
    description: '58m 5-section placing boom with 6-1/2in delivery line. Highest output in its class. Ideal for high-rise and large slab pours.',
    category: 'concrete_equipment', manufacturer: 'Putzmeister', model: 'BSF 58-6.16H', year: 2023,
    condition: 'excellent', hoursUsed: 300,
    specifications: { weight: 32000, height: 3200, width: 2500, length: 12000, power: 280, fuelType: 'diesel', maxReach: 58 },
    pricing: { dailyRate: 800, weeklyRate: 4600, monthlyRate: 15000 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/putz-bsf58.jpg', alt: 'Putzmeister BSF 58', isPrimary: true }],
    features: ['5-section boom', 'Radio remote', 'ERP system', 'Stabilization system'], requiresOperator: true, rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 8000,
    tags: ['concrete', 'boom-pump', 'putzmeister', 'high-rise']
  },
  {
    sku: 'CONC-SCHW-P750-032',
    name: 'Schwing P 750 Concrete Pump',
    description: 'Semi-trailer concrete pump with 48m placing reach. Reliable S-valve technology for consistent concrete flow.',
    category: 'concrete_equipment', manufacturer: 'Schwing', model: 'P 750', year: 2022,
    condition: 'good', hoursUsed: 900,
    specifications: { weight: 25000, height: 3000, width: 2500, length: 10000, power: 200, fuelType: 'diesel', maxReach: 48 },
    pricing: { dailyRate: 600, weeklyRate: 3500, monthlyRate: 11000 },
    availability: [{ status: 'available', location: { city: 'Poznan', region: 'Greater Poland' } }],
    images: [{ url: '/images/schwing-p750.jpg', alt: 'Schwing P 750', isPrimary: true }],
    features: ['S-valve', 'Remote control', 'Hydraulic outriggers', 'Concrete hopper'], requiresOperator: true, rentalOnly: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 6000,
    tags: ['concrete', 'pump', 'schwing', 'trailer']
  },
  {
    sku: 'CONC-MIX-LIE-10-033',
    name: 'Liebherr HTM 1005 Truck Mixer',
    description: '10 cu.m concrete mixer truck with Liebherr drum drive. Hydraulic drive system with infinitely variable drum speed.',
    category: 'concrete_equipment', manufacturer: 'Liebherr', model: 'HTM 1005', year: 2023,
    condition: 'excellent', hoursUsed: 450,
    specifications: { weight: 15000, height: 3600, width: 2500, length: 8100, power: 300, fuelType: 'diesel' },
    pricing: { dailyRate: 350, weeklyRate: 2000, monthlyRate: 6500 },
    availability: [{ status: 'available', location: { city: 'Czestochowa', region: 'Silesia' } }],
    images: [{ url: '/images/liebherr-htm1005.jpg', alt: 'Liebherr HTM 1005', isPrimary: true }],
    features: ['Hydraulic drive', '10 cu.m capacity', 'Water tank', 'Drum reversal alarm'], rentalOnly: true, requiresOperator: true,
    insuranceRequired: true, depositRequired: true, depositAmount: 3000,
    tags: ['concrete', 'mixer', 'liebherr', 'truck']
  },

  // ==================== ATTACHMENTS ====================
  {
    sku: 'ATT-CAT-S60-034',
    name: 'Caterpillar S60 Hydraulic Quick Coupler',
    description: 'Pin-grab hydraulic quick coupler for Cat excavators 20-30 ton. Enables rapid attachment changes from the cab. Includes all mounting hardware.',
    category: 'attachments', manufacturer: 'Caterpillar', model: 'S60', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 350, height: 200, width: 400, length: 600, maxLiftCapacity: 30000 },
    pricing: { dailyRate: 45, weeklyRate: 250, monthlyRate: 800 },
    availability: [{ status: 'available', location: { city: 'Warsaw', region: 'Masovia' } }],
    images: [{ url: '/images/cat-s60.jpg', alt: 'Cat S60 Coupler', isPrimary: true }],
    features: ['Pin-grab design', 'Hydraulic lock', 'Safety pins', 'Universal fit'], rentalOnly: false,
    insuranceRequired: false, depositRequired: false, depositAmount: 200,
    tags: ['attachment', 'coupler', 'caterpillar', 'quick-hitch']
  },
  {
    sku: 'ATT-HYD-H70-035',
    name: 'Indeco HP 7000 Hydraulic Hammer',
    description: '7-ton class hydraulic breaker for excavators 25-35 ton. Ideal for rock breaking, demolition, and quarry applications.',
    category: 'attachments', manufacturer: 'Indeco', model: 'HP 7000', year: 2023,
    condition: 'excellent', hoursUsed: 150,
    specifications: { weight: 680, height: 150, width: 350, length: 2000, power: 180, operatingWeight: 680 },
    pricing: { dailyRate: 120, weeklyRate: 680, monthlyRate: 2200 },
    availability: [{ status: 'available', location: { city: 'Katowice', region: 'Silesia' } }],
    images: [{ url: '/images/indeco-hp7000.jpg', alt: 'Indeco HP 7000', isPrimary: true }],
    features: ['Auto lubrication', 'Sound suppression', 'Anti-blank firing', 'Tool bushing'], rentalOnly: true,
    insuranceRequired: false, depositRequired: true, depositAmount: 800,
    tags: ['attachment', 'hammer', 'breaker', 'indeco', 'demolition']
  },
  {
    sku: 'ATT-BOS-TRE-036',
    name: 'Boss Attachments Ditching Bucket 1200mm',
    description: '1200mm heavy-duty ditching bucket for excavators 20-25 ton. AR400 wear plating for extended life in abrasive conditions.',
    category: 'attachments', manufacturer: 'Boss Attachments', model: 'DB-1200', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 450, height: 800, width: 1200, length: 1300, maxLiftCapacity: 4000 },
    pricing: { dailyRate: 35, weeklyRate: 200, monthlyRate: 600, purchasePrice: 4500 },
    availability: [{ status: 'available', location: { city: 'Wroclaw', region: 'Lower Silesia' } }],
    images: [{ url: '/images/boss-db1200.jpg', alt: 'Boss Ditching Bucket', isPrimary: true }],
    features: ['AR400 plating', 'Reversible cutting edge', 'Gusset reinforcement', 'Pin-on design'], rentalOnly: false, purchaseOnly: false,
    insuranceRequired: false, depositRequired: false, depositAmount: 300,
    tags: ['attachment', 'bucket', 'ditching', 'excavator']
  },
  {
    sku: 'ATT-AUG-MC6-037',
    name: 'McLaughlin 36" Earth Auger Drive',
    description: '36-inch diameter hydraulic earth auger drive for excavators 15-25 ton. For drilling deep foundations, poles, and piles.',
    category: 'attachments', manufacturer: 'McLaughlin', model: 'H36', year: 2023,
    condition: 'excellent', hoursUsed: 100,
    specifications: { weight: 550, height: 300, width: 400, length: 1400, power: 80, operatingWeight: 550 },
    pricing: { dailyRate: 150, weeklyRate: 850, monthlyRate: 2800 },
    availability: [{ status: 'available', location: { city: 'Opole', region: 'Opole' } }],
    images: [{ url: '/images/mclaughlin-h36.jpg', alt: 'McLaughlin H36 Auger', isPrimary: true }],
    features: ['Torque limiter', 'Quick coupler mount', 'Down-feed guides', 'Flight extensions'], rentalOnly: true,
    insuranceRequired: false, depositRequired: true, depositAmount: 1000,
    tags: ['attachment', 'auger', 'drill', 'mclaughlin', 'foundation']
  },
  {
    sku: 'ATT-PAL-SK300-038',
    name: 'Paladin 3000 lb Fork Mount', description: 'Skid steer fork mount with 3000 lb capacity. 48-inch forks with poly backrest. Universal mounting plate fits most skid steers.',
    category: 'attachments', manufacturer: 'Paladin', model: '3000F', year: 2024,
    condition: 'new', hoursUsed: 0,
    specifications: { weight: 320, height: 500, width: 1200, length: 1500, maxLiftCapacity: 1360 },
    pricing: { dailyRate: 40, weeklyRate: 220, monthlyRate: 700, purchasePrice: 2800 },
    availability: [{ status: 'available', location: { city: 'Bialystok', region: 'Podlaskie' } }],
    images: [{ url: '/images/paladin-3k.jpg', alt: 'Paladin 3000 Fork', isPrimary: true }],
    features: ['Universal mount', 'Poly backrest', '48-inch forks', 'Load rated'], rentalOnly: false, purchaseOnly: false,
    insuranceRequired: false, depositRequired: false, depositAmount: 300,
    tags: ['attachment', 'forks', 'paladin', 'skid-steer']
  },
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

    console.log('Inserting equipment...');
    const result = await Equipment.insertMany(equipment);
    console.log(`Seeded ${result.length} equipment items:`);
    result.forEach(item => console.log(`  - ${item.sku}: ${item.name} [${item.category}]`));

    const counts = {};
    result.forEach(item => {
      counts[item.category] = (counts[item.category] || 0) + 1;
    });
    console.log('\nBy category:');
    for (const [cat, count] of Object.entries(counts)) {
      console.log(`  ${cat}: ${count}`);
    }

    console.log('\nTest queries:');
    console.log(`  GET http://localhost:3000/api/v1/equipment`);
    console.log(`  GET http://localhost:3000/api/v1/categories`);
    console.log(`  GET http://localhost:3000/api/v1/search?q=excavator`);
    console.log(`  GET http://localhost:3000/api/v1/search?category=cranes`);
    console.log(`  GET http://localhost:3000/api/v1/equipment/${result[0]._id}`);
  } catch (error) {
    console.error('Seeding failed:', error.message);
    process.exit(1);
  } finally {
    await mongoose.connection.close();
    console.log('\nDatabase connection closed.');
  }
}

seedDatabase();
