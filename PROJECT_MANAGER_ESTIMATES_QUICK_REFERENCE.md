# Project Manager - Estimates Quick Reference

## Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/pm/estimates/` | List all estimates with search & filter |
| GET | `/api/pm/estimates/<id>/` | Get detailed estimate information |

## Quick API Calls

### Get All Estimates
```bash
curl -X GET 'http://10.10.13.27:8002/api/pm/estimates/' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Search Estimates by Client Name
```bash
curl -X GET 'http://10.10.13.27:8002/api/pm/estimates/?q=Acme' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Filter by Status
```bash
curl -X GET 'http://10.10.13.27:8002/api/pm/estimates/?status=approved' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### Get Estimate Details
```bash
curl -X GET 'http://10.10.13.27:8002/api/pm/estimates/1/' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

## Features

✅ View all estimates from the system
✅ Search by serial_number, estimate_number, client_name, or project_name
✅ Filter by status (pending, sent, approved, rejected)
✅ View complete estimate details with all items
✅ See cost breakdown including profit and tax calculations
✅ View full item details (materials, components, services)

## Response Summary

- **List Endpoint:** Returns estimate summaries with totals
- **Detail Endpoint:** Returns complete estimate data with all items and their details

## Required Role

- Project Manager
- Admin

