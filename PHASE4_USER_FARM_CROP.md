# Phase 4 — User, Farm, Crop & Scan Management

Phase 4 adds a product-oriented backend layer without changing the existing UI.

## Authentication

Use the existing Phase 2 endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Use the returned JWT as:

```text
Authorization: Bearer <access_token>
```

## Profile

`GET /api/profile`

`PATCH /api/profile`

Example body:

```json
{
  "name": "Arpit Singh"
}
```

## Farms

`GET /api/farms`

`POST /api/farms`

```json
{
  "farm_name": "My Mango Farm",
  "location": "Lucknow, Uttar Pradesh"
}
```

`GET /api/farms/<farm_id>`

`PATCH /api/farms/<farm_id>`

`DELETE /api/farms/<farm_id>`

All farm queries are scoped to the authenticated user.

## Crops

`GET /api/farms/<farm_id>/crops`

`POST /api/farms/<farm_id>/crops`

```json
{
  "crop_name": "Mango"
}
```

`GET /api/crops/<crop_id>`

`PATCH /api/crops/<crop_id>`

```json
{
  "crop_name": "Mango",
  "farm_id": 1
}
```

`DELETE /api/crops/<crop_id>`

Crop operations are restricted to farms owned by the authenticated user.

## Scan organization

The existing scan history remains available. The Phase 4 management routes also support filters by farm, crop and status where the route is available in the management layer.

`POST /api/scans/<scan_id>/organize`

```json
{
  "farm_id": 1,
  "crop_id": 2
}
```

Set either value to `null` to remove the association. A crop must belong to the selected farm.

## Product data model

```text
User
 ├── Farms
 │    └── Crops
 │         └── Scans
 └── Scans
```

This prepares ATHARVADRISHTI for future farmer dashboards, crop-wise history, analytics, alerts, expert review, and mobile clients.

## UI policy

No existing template, stylesheet, or Streamlit interface is modified by Phase 4. The management functionality is intentionally exposed through backend APIs first so the existing interface remains stable.
