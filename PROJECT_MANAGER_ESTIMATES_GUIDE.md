# Project Manager - Estimates API Guide

This guide covers the APIs available to Project Managers for viewing and managing estimates.

## Overview

Project Managers can:
- View a list of all estimates
- Search estimates by serial number, estimate number, client name, or project name
- Filter estimates by status
- View detailed information about specific estimates

## API Endpoints

### 1. Get Estimates List

**Endpoint:** `GET /api/pm/estimates/`

**Authentication:** Required (Project Manager or Admin role)

**Description:** Retrieve a list of all estimates with summary information.

**Query Parameters:**
- `q` (optional): Search term for serial_number, estimate_number, client_name, or project_name
- `status` (optional): Filter by status (pending, sent, approved, rejected)

**Example Request:**
```bash
curl -X GET 'http://localhost:8000/api/pm/estimates/' \
  -H 'Authorization: Bearer YOUR_TOKEN'

curl -X GET 'http://localhost:8000/api/pm/estimates/?q=Acme&status=approved' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**Response Example:**
```json
{
  "success": true,
  "message": "Retrieved 5 estimates",
  "data": [
    {
      "id": 1,
      "serial_number": "EST-2025-001",
      "estimate_number": "EST-2025-CLIENT-001",
      "client_name": "Acme Corporation",
      "project_name": "Office Renovation",
      "status": "approved",
      "estimate_date": "2025-11-12",
      "end_date": "2025-12-11",
      "items_count": 3,
      "total_cost": 2550.00,
      "created_at": "2025-11-12T10:30:00Z"
    },
    {
      "id": 2,
      "serial_number": "EST-2025-002",
      "estimate_number": "EST-2025-CLIENT-002",
      "client_name": "Beta Inc",
      "project_name": "Website Redesign",
      "status": "pending",
      "estimate_date": "2025-11-11",
      "end_date": "2025-12-15",
      "items_count": 2,
      "total_cost": 1500.00,
      "created_at": "2025-11-11T14:20:00Z"
    }
  ]
}
```

---

### 2. Get Estimate Detail

**Endpoint:** `GET /api/pm/estimates/<estimate_id>/`

**Authentication:** Required (Project Manager or Admin role)

**Description:** Retrieve detailed information about a specific estimate, including all items, costs, and calculations.

**URL Parameters:**
- `estimate_id`: The ID of the estimate to retrieve

**Example Request:**
```bash
curl -X GET 'http://localhost:8000/api/pm/estimates/1/' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**Response Example:**
```json
{
  "success": true,
  "message": "Retrieved estimate EST-2025-001",
  "data": {
    "id": 1,
    "serial_number": "EST-2025-001",
    "estimate_number": "EST-2025-CLIENT-001",
    "client_name": "Acme Corporation",
    "project_name": "Office Renovation",
    "status": "approved",
    "estimate_date": "2025-11-12",
    "end_date": "2025-12-11",
    "profit_margin": 15,
    "income_tax": 8,
    "notes": "Detailed project notes",
    "items": [
      {
        "item_type": "material",
        "item_id": 1,
        "quantity": 5,
        "unit_price": 100.0,
        "notes": "High quality material",
        "item_total_cost": 500.0,
        "item_details": {
          "id": 1,
          "material_name": "Premium Wood",
          "supplier": "Wood Suppliers Inc",
          "category": "Materials",
          "unit": "sq ft",
          "cost_per_unit": 100.0,
          "created_at": "2025-10-15T08:00:00Z",
          "created_by_email": "admin@example.com"
        }
      },
      {
        "item_type": "component",
        "item_id": 2,
        "quantity": 2,
        "unit_price": 250.0,
        "notes": "Standard component",
        "item_total_cost": 500.0,
        "item_details": {
          "id": 2,
          "component_name": "Door Unit",
          "description": "Standard door assembly",
          "base_price": 250.0,
          "labor_hours": 2.0,
          "material_used": [...],
          "estimate_defaults": [...],
          "created_at": "2025-10-15T08:00:00Z",
          "created_by_email": "admin@example.com"
        }
      },
      {
        "item_type": "estimate_default",
        "item_id": 1,
        "quantity": 1,
        "unit_price": 500.0,
        "notes": "Custom service",
        "item_total_cost": 500.0,
        "item_details": {
          "id": 1,
          "name": "Installation Service",
          "description": "Professional installation",
          "category": "Services",
          "created_at": "2025-10-15T08:00:00Z",
          "created_by_email": "admin@example.com"
        }
      }
    ],
    "items_count": 3,
    "total_items_cost": 1500.0,
    "total_cost": 1500.0,
    "profit_amount": 225.0,
    "total_with_profit": 1725.0,
    "tax_amount": 138.0,
    "total_with_tax": 1863.0,
    "cost_breakdown": {
      "items_total": 1500.0,
      "profit_margin_percentage": 15,
      "profit_amount": 225.0,
      "subtotal_with_profit": 1725.0,
      "income_tax_percentage": 8,
      "tax_amount": 138.0,
      "final_total": 1863.0
    },
    "created_at": "2025-11-12T10:30:00Z",
    "updated_at": "2025-11-12T11:45:00Z"
  }
}
```

---

## Search Examples

### Search by Serial Number
```bash
curl -X GET 'http://localhost:8000/api/pm/estimates/?q=EST-2025-001' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Search by Client Name
```bash
curl -X GET 'http://localhost:8000/api/pm/estimates/?q=Acme' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Filter by Status
```bash
curl -X GET 'http://localhost:8000/api/pm/estimates/?status=approved' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Combined Search and Filter
```bash
curl -X GET 'http://localhost:8000/api/pm/estimates/?q=Acme&status=pending' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

---

## Status Values

Estimates can have the following status values:
- `pending`: Initial status, not yet sent to client
- `sent`: Sent to client for review
- `approved`: Client has approved the estimate
- `rejected`: Client has rejected the estimate

---

## Response Fields

### Estimate List Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique estimate identifier |
| serial_number | String | Internal serial number |
| estimate_number | String | Unique estimate number for tracking |
| client_name | String | Name of the client |
| project_name | String | Name of the project |
| status | String | Current status of estimate |
| estimate_date | Date | Date when estimate was created |
| end_date | Date | Estimated project end date |
| items_count | Integer | Number of items in estimate |
| total_cost | Float | Total cost of all items |
| created_at | DateTime | When estimate was created |

### Estimate Detail Response Fields

All fields from the list response, plus:

| Field | Type | Description |
|-------|------|-------------|
| profit_margin | Float | Profit margin percentage |
| income_tax | Float | Income tax percentage |
| notes | String | Additional notes about the estimate |
| items | Array | List of estimate items with full details |
| total_items_cost | Float | Sum of all item costs |
| profit_amount | Float | Calculated profit amount |
| total_with_profit | Float | Total including profit |
| tax_amount | Float | Calculated tax amount |
| total_with_tax | Float | Final total including tax |
| cost_breakdown | Object | Detailed cost breakdown |
| updated_at | DateTime | When estimate was last updated |

---

## Error Responses

### Estimate Not Found (404)
```json
{
  "success": false,
  "message": "Estimate with ID 999 not found",
  "data": null
}
```

### Unauthorized (401)
```json
{
  "success": false,
  "message": "Authentication credentials were not provided.",
  "data": null
}
```

### Permission Denied (403)
```json
{
  "success": false,
  "message": "You do not have permission to perform this action.",
  "data": null
}
```

---

## Notes

- Only Project Managers and Admins can access these endpoints
- Estimates are returned sorted by creation date (newest first)
- Search is case-insensitive and supports partial matches
- All monetary values are returned as floats
- All dates are returned in ISO 8601 format

