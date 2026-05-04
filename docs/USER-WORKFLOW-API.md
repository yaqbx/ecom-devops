# User Workflow: Browser to Product Catalog

## 📋 Overview

This document traces the complete journey of a user request from opening a browser to viewing products, showing **every component interaction** and clarifying **which communications use APIs** vs internal calls.

---

## 🎯 High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["🖥️ Client Layer"]
        Browser[User's Browser<br/>(Chrome/Firefox/Safari)]
    end

    subgraph Edge["🌐 Edge Layer"]
        DNS[DNS Server]
        ALB[AWS Load Balancer<br/>(ALB)]
        Ingress[Kubernetes Ingress<br/>(NGINX)]
    end

    subgraph App["🚀 Application Layer"]
        Frontend[Frontend Web Service<br/>(React SPA)]
        ProductAPI[Product Catalog API<br/>(Node.js)]
        UserAPI[User Management API<br/>(Django)]
        CheckoutAPI[Checkout Service API<br/>(FastAPI)]
    end

    subgraph Data["💾 Data Layer"]
        MongoDB[(MongoDB<br/>Products)]
        Postgres[(PostgreSQL<br/>Users)]
        Redis[(Redis<br/>Cache/Sessions)]
    end

    Browser -->|"1. DNS Lookup"| DNS
    DNS -->|"2. HTTPS Request"| ALB
    ALB -->|"3. Route to Cluster"| Ingress
    Ingress -->|"4a. / (static)"| Frontend
    Ingress -->|"4b. /api/* (API)"| ProductAPI
    Ingress -->|"4c. /api/* (API)"| UserAPI
    Ingress -->|"4d. /api/* (API)"| CheckoutAPI

    Frontend -.->|"5. API Calls"| ProductAPI
    Frontend -.->|"5. API Calls"| UserAPI
    Frontend -.->|"5. API Calls"| CheckoutAPI

    ProductAPI -->|"6. Query"| MongoDB
    UserAPI -->|"6. Query"| Postgres
    CheckoutAPI -->|"6. Cache"| Redis

    style Client fill:#e3f2fd
    style Edge fill:#fff3e0
    style App fill:#f3e5f5
    style Data fill:#e8f5e9
```

---

## 📍 Complete Step-by-Step Workflow

### Scenario: User Browses for Excavators

**User Action:** Opens browser and navigates to `https://ecommerce.com/products?category=excavators`

---

### Step 1: User Opens Browser

**Action:** User types URL in address bar and presses Enter

**What Happens:**
1. Browser parses the URL
2. Browser initiates DNS lookup for `ecommerce.com`
3. Operating system checks local DNS cache
4. If not cached, sends DNS query to DNS server

**Components Involved:**
- User's browser (Chrome, Firefox, Safari, Edge)
- Operating system DNS resolver
- DNS server (ISP or public like 8.8.8.8)

**Is this an API call?** ❌ **NO** - This is DNS resolution (infrastructure layer)

---

### Step 2: DNS Resolution

**DNS Query Flow:**
```
Browser → OS DNS Cache → DNS Resolver → Authoritative DNS Server
         ↓
Returns: 52.32.145.67 (AWS ALB IP Address)
```

**DNS Response:**
```
ecommerce.com.    IN    A    52.32.145.67
```

**Components Involved:**
- Local DNS cache
- DNS resolver (ISP or public)
- Authoritative DNS server (Route53, CloudFlare, etc.)

**Is this an API call?** ❌ **NO** - This is DNS protocol (infrastructure)

---

### Step 3: HTTPS Request to Load Balancer

**Browser Action:**
```http
GET /products?category=excavators HTTP/1.1
Host: ecommerce.com
User-Agent: Mozilla/5.0...
Accept: text/html,application/xhtml+xml...
```

**What Happens:**
1. Browser establishes TCP connection to `52.32.145.67:443`
2. TLS handshake (HTTPS encryption)
3. Request reaches AWS Application Load Balancer (ALB)
4. ALB terminates SSL (decrypts HTTPS → HTTP)
5. ALB forwards to Kubernetes cluster

**ALB Configuration:**
```yaml
# AWS ALB Listener Rules
- If path begins with /api/v1/*
  → Forward to k8s-ecom-ingress (Kubernetes)
- If path begins with /
  → Forward to k8s-ecom-ingress (Kubernetes)
```

**Components Involved:**
- Browser's HTTP client
- AWS ALB (Application Load Balancer)
- SSL/TLS certificates

**Is this an API call?** ❌ **NO** - This is HTTP transport layer (getting to the API)

---

### Step 4: Kubernetes Ingress Routing

**Ingress Controller (NGINX) receives request:**
```http
GET /products?category=excavators HTTP/1.1
Host: ecommerce.com
```

**Ingress Rules:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
spec:
  rules:
  - host: ecommerce.com
    http:
      paths:
      # Static files (React app)
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-web
            port:
              number: 80
      # API routes
      - path: /api/v1/products
        pathType: Prefix
        backend:
          service:
            name: product-catalog
            port:
              number: 3000
      - path: /api/v1/users
        pathType: Prefix
        backend:
          service:
            name: user-management
            port:
              number: 8000
      - path: /api/v1/quotes
        pathType: Prefix
        backend:
          service:
            name: checkout-service
            port:
              number: 8001
```

**Routing Decision:**
- Path `/products` → matches `/` (Prefix) → `frontend-web:80`
- Path `/api/v1/products` → matches specific API route → `product-catalog:3000`

**Components Involved:**
- Kubernetes Ingress Controller (NGINX, Traefik, etc.)
- Kubernetes Services
- Pod endpoints

**Is this an API call?** ❌ **NO** - This is internal Kubernetes routing (Layer 7 load balancing)

---

### Step 5: Frontend Application Loads

**First Request - Static Files:**
```
Browser → Ingress → frontend-web Service → React Pod
                                              ↓
                                    Returns: index.html, app.js, styles.css
```

**What Browser Receives:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>E-Commerce Platform</title>
</head>
<body>
  <div id="root"></div>
  <script src="/static/js/main.js"></script>
</body>
</html>
```

**React App Starts:**
```javascript
// main.js - Executes in browser
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
```

**Components Involved:**
- Frontend web server (Nginx, Apache, or Node.js serving static files)
- React application (JavaScript bundle)
- Browser's JavaScript engine

**Is this an API call?** ❌ **NO** - This is static file serving (HTML/CSS/JS)

---

### Step 6: React Makes API Call (First API Call!)

**React Component Mounts:**
```javascript
// ProductsPage.jsx
import { useEffect, useState } from 'react';

function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // THIS IS WHERE API CALL HAPPENS!
    fetchProducts();
  }, []);

  async function fetchProducts() {
    try {
      setLoading(true);
      
      // 🔹 API CALL #1: Get products
      const response = await fetch('/api/v1/products?category=excavators', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Auth token if user is logged in
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }

      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Excavators</h1>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

**Browser Sends API Request:**
```http
GET /api/v1/products?category=excavators HTTP/1.1
Host: ecommerce.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6Ikp...
Content-Type: application/json
```

**✅ THIS IS AN API CALL!**

**Characteristics:**
- ✅ HTTP request to backend service
- ✅ Returns JSON data (not HTML)
- ✅ Programmatic access (not page load)
- ✅ Used by application logic (not direct user navigation)

---

### Step 7: API Request Travels to Backend

**Request Flow:**
```
Browser (React)
  ↓ HTTPS
AWS ALB (SSL Termination)
  ↓ HTTP (internal)
Kubernetes Ingress (NGINX)
  ↓ Service Discovery
Product Catalog Service (ClusterIP: 10.96.x.x:3000)
  ↓ kube-proxy iptables
Product Catalog Pod (Node.js: 10.244.1.5:3000)
```

**Kubernetes Service Discovery:**
```yaml
# product-catalog-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: product-catalog
  namespace: ecommerce
spec:
  type: ClusterIP
  selector:
    app: product-catalog
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
```

**Is this an API call?** ✅ **YES** - The entire chain from Browser → Backend is one API call

---

### Step 8: Product Catalog Service Processes Request

**Node.js Application Receives Request:**
```javascript
// src/routes/products.js
const express = require('express');
const router = express.Router();
const Equipment = require('../models/Equipment');
const auth = require('../middleware/auth');

// GET /api/v1/products
router.get('/', auth.optional, async (req, res) => {
  try {
    // Extract query parameters
    const { category, page = 1, limit = 20 } = req.query;
    
    // Build MongoDB query
    const query = { isActive: true };
    if (category) {
      query.category = category;
    }

    // Calculate pagination
    const skip = (parseInt(page) - 1) * parseInt(limit);

    // 🔹 DATABASE QUERY (NOT an API call)
    const [products, total] = await Promise.all([
      Equipment.find(query)
        .skip(skip)
        .limit(parseInt(limit))
        .lean(),
      Equipment.countDocuments(query)
    ]);

    // Return API response
    res.json({
      success: true,
      data: products,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });

  } catch (error) {
    console.error('Error fetching products:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
```

**Is the database call an API call?** ❌ **NO**
- MongoDB driver uses binary protocol (not HTTP/REST)
- It's an internal library call
- Similar to calling a function in your code

---

### Step 9: MongoDB Query Execution

**Mongoose (ODM) to MongoDB:**
```javascript
// What happens inside Equipment.find(query)

// 1. Mongoose converts query to MongoDB wire protocol
{
  "find": "equipments",
  "filter": {
    "isActive": true,
    "category": "excavators"
  },
  "limit": 20,
  "skip": 0
}

// 2. Sends over TCP to MongoDB (port 27017)
// 3. MongoDB executes query
// 4. Returns documents

// Sample result:
[
  {
    "_id": "exc-001",
    "sku": "CAT-320-2024",
    "name": "Caterpillar 320 Hydraulic Excavator",
    "category": "excavators",
    "price_per_day": 450,
    "specifications": {
      "weight": 20000,
      "power": 128
    },
    "availability": {
      "status": "available",
      "quantity": 5
    }
  },
  // ... more products
]
```

**Is this an API call?** ❌ **NO**
- Uses MongoDB's native wire protocol (binary)
- Not HTTP-based
- Direct database driver communication

---

### Step 10: Response Returns to Browser

**Response Chain:**
```
MongoDB
  ↓ Documents
Product Catalog Service (Node.js)
  ↓ JSON Response
Kubernetes Pod Network
  ↓ Service IP
Kubernetes Service (ClusterIP)
  ↓ kube-proxy
Ingress Controller
  ↓ HTTP Response
AWS ALB
  ↓ HTTPS (re-encrypted)
Browser (React)
```

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-Id: req-123456
X-Response-Time: 145ms

{
  "success": true,
  "data": [
    {
      "id": "exc-001",
      "sku": "CAT-320-2024",
      "name": "Caterpillar 320 Hydraulic Excavator",
      "category": "excavators",
      "price_per_day": 450,
      "availability": {
        "status": "available",
        "quantity": 5
      }
    },
    {
      "id": "exc-002",
      "sku": "KOM-200-2023",
      "name": "Komatsu PC200 Excavator",
      "category": "excavators",
      "price_per_day": 380,
      "availability": {
        "status": "available",
        "quantity": 3
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "pages": 1
  }
}
```

**Is this an API response?** ✅ **YES** - This is the API response returning to the client

---

### Step 11: React Renders the Data

**React Receives Response:**
```javascript
async function fetchProducts() {
  const response = await fetch('/api/v1/products?category=excavators');
  const result = await response.json();
  
  // Update React state
  setProducts(result.data);
  setLoading(false);
  // React automatically re-renders with new data
}
```

**UI Updates:**
```javascript
function ProductsPage({ products }) {
  return (
    <div className="products-grid">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

function ProductCard({ product }) {
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p className="price">${product.price_per_day}/day</p>
      <p className="availability">
        {product.availability.status === 'available' 
          ? '✅ Available' 
          : '❌ Unavailable'}
      </p>
      <button onClick={() => {/* Request Quote */}}>
        Request Quote
      </button>
    </div>
  );
}
```

**Is this an API call?** ❌ **NO** - This is UI rendering (client-side)

---

## 🔍 Complete Communication Map

### What IS an API Call?

| # | From | To | Protocol | Is API? | Purpose |
|---|------|----|----------|---------|---------|
| 1 | Browser | Product Catalog | HTTP GET | ✅ **YES** | Get products list |
| 2 | Browser | User Management | HTTP POST | ✅ **YES** | Login/Register |
| 3 | Browser | Checkout Service | HTTP POST | ✅ **YES** | Create quote |
| 4 | Product Catalog | User Management | HTTP GET | ✅ **YES** | Validate user (if needed) |
| 5 | Checkout | Product Catalog | HTTP GET | ✅ **YES** | Get product details (if needed) |

### What is NOT an API Call?

| # | From | To | Protocol | Is API? | Purpose |
|---|------|----|----------|---------|---------|
| 1 | Product Catalog | MongoDB | MongoDB Wire Protocol | ❌ **NO** | Query database |
| 2 | User Management | PostgreSQL | SQL via libpq | ❌ **NO** | Query database |
| 3 | Checkout | Redis | Redis Protocol (TCP) | ❌ **NO** | Cache lookup |
| 4 | Ingress | Pod | TCP (kube-proxy) | ❌ **NO** | Internal routing |
| 5 | Browser | DNS Server | DNS Protocol | ❌ **NO** | Name resolution |

---

## 🎯 Key Distinctions

### API Call Characteristics:
✅ Uses HTTP/HTTPS (usually REST, GraphQL, or gRPC)  
✅ Request/Response pattern  
✅ Stateless (each request is independent)  
✅ Network-based (crosses process boundaries)  
✅ Used for service-to-service or client-to-service communication  

### NOT API Call Characteristics:
❌ Uses database protocols (SQL, MongoDB wire protocol)  
❌ Internal function/library calls  
❌ Same-process communication  
❌ Infrastructure protocols (DNS, TCP handshake)  
❌ Kubernetes internal routing  

---

## 📊 Complete Request Timeline

```
Time: 0ms     User types URL
      ↓
Time: 10ms    DNS Resolution (NOT API)
      ↓
Time: 50ms    HTTPS Connection to ALB (NOT API)
      ↓
Time: 60ms    Ingress Routes to Frontend (NOT API)
      ↓
Time: 100ms   React App Loads (static files, NOT API)
      ↓
Time: 150ms   React mounts, calls fetch()
      ↓
Time: 151ms   🔹 API CALL STARTS
      ↓
Time: 160ms   Reaches Product Catalog Service
      ↓
Time: 170ms   Service queries MongoDB (NOT API)
      ↓
Time: 180ms   MongoDB returns data
      ↓
Time: 190ms   Service formats JSON response
      ↓
Time: 200ms   🔹 API CALL ENDS
      ↓
Time: 210ms   React renders products
      ↓
Time: 250ms   User sees products on screen
```

**Total Time:** ~250ms  
**API Call Time:** ~50ms (151ms - 200ms)

---

## 🔄 Full User Journey Example

### Scenario: User Logs In, Browses, Creates Quote

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant React
    participant API Gateway
    participant UserAPI
    participant ProductAPI
    participant CheckoutAPI
    participant MongoDB
    participant PostgreSQL

    User->>Browser: Types ecommerce.com
    Browser->>API Gateway: GET / (static files)
    API Gateway-->>Browser: index.html, app.js
    Browser->>React: Executes JavaScript
    React->>UserAPI: POST /api/v1/users/login (API Call #1)
    UserAPI->>PostgreSQL: SELECT * FROM users
    PostgreSQL-->>UserAPI: User data
    UserAPI-->>React: JWT Token + User Info
    React->>Browser: Stores token in localStorage
    React->>ProductAPI: GET /api/v1/products (API Call #2)
    ProductAPI->>MongoDB: Find products
    MongoDB-->>ProductAPI: Products array
    ProductAPI-->>React: Products JSON
    React->>Browser: Renders product list
    Browser->>User: Shows products
    User->>Browser: Clicks "Request Quote"
    React->>CheckoutAPI: POST /api/v1/quotes (API Call #3)
    CheckoutAPI->>MongoDB: Store quote
    MongoDB-->>CheckoutAPI: Quote saved
    CheckoutAPI-->>React: Quote ID + Total
    React->>Browser: Shows quote confirmation
    Browser->>User: "Quote #QT-12345 created!"
```

**API Calls in this flow:**
1. ✅ `POST /api/v1/users/login` - User authentication
2. ✅ `GET /api/v1/products` - Fetch products
3. ✅ `POST /api/v1/quotes` - Create quote

**Non-API calls:**
- ❌ PostgreSQL queries (internal database)
- ❌ MongoDB queries (internal database)
- ❌ Static file serving (HTML/JS)
- ❌ DNS resolution
- ❌ Load balancer routing

---

## 🎯 Summary

### When a User Opens a Webpage:

1. **Initial Load** - NOT API calls
   - DNS resolution ❌
   - HTTPS connection ❌
   - Static file download (HTML/CSS/JS) ❌

2. **React App Executes** - NOT API calls
   - JavaScript parsing ❌
   - Component mounting ❌
   - State initialization ❌

3. **Data Fetching** - ✅ API calls start here
   - `fetch('/api/v1/products')` ✅
   - `fetch('/api/v1/users')` ✅
   - `fetch('/api/v1/quotes')` ✅

4. **Backend Processing** - Mixed
   - Service receives HTTP request ✅ (API)
   - Service calls database ❌ (not API)
   - Database returns data ❌ (not API)
   - Service sends HTTP response ✅ (API)

5. **Frontend Rendering** - NOT API calls
   - React updates state ❌
   - DOM re-renders ❌
   - User sees results ❌

### Key Takeaway:
**API calls are HTTP requests from client (browser) to backend services.** Everything else (database queries, internal routing, DNS) is infrastructure that supports the API but is not itself an API call.

---

## 📚 Additional Resources

- [What is an API?](https://www.redhat.com/en/topics/api/what-is-an-api)
- [REST API Best Practices](https://restfulapi.net/)
- [Kubernetes Networking](https://kubernetes.io/docs/concepts/services-networking/)
- [How Browsers Work](https://www.html5rocks.com/en/tutorials/internals/howbrowserswork/)

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-21  
**Maintained By:** DevOps Team
