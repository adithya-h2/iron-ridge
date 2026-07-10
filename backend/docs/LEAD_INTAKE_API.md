# Universal Lead Intake API

## Endpoint

```
POST /api/v1/leads
Content-Type: application/json
```

Public in development. In production, use rate limiting and optionally `X-API-KEY` or JWT.

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | enum | Yes | `WEBSITE`, `DASHBOARD`, `API`, `EMAIL`, `CSV`, `WHATSAPP`, `VOICE`, `TRADE_SHOW`, `PHONE`, `OTHER` |
| `submission_channel` | string | Yes | Channel detail, e.g. `web_form`, `n8n`, `mobile_app` |
| `company_name` | string | One of | Company name |
| `org_name` | string | One of | Alias for company name |
| `email` | string | No | Contact email |
| `phone` | string | No | Contact phone |
| `contact_person` | string | No | Contact name |
| `city` | string | No | City |
| `country` | string | No | Country |
| `vehicle_type` | string | No | Vehicle interest |
| `required_quantity` | int | No | Quantity |
| `notes` | string | No | Free text |

## Response

```json
{
  "success": true,
  "data": {
    "deal_id": "uuid",
    "customer_id": "uuid",
    "workflow_id": "uuid",
    "lead_source": "WEBSITE",
    "submission_channel": "web_form",
    "status": "LEAD",
    "is_duplicate": false,
    "matched_customer_id": null,
    "lead_score": null,
    "company_name": "Metro EMS"
  },
  "request_id": "..."
}
```

## Pipeline

1. Validate and normalize (`LeadValidator`)
2. Duplicate detection (`DuplicateDetectionService`)
3. Create customer + deal (`LeadCreationRepository`)
4. Audit log (`lead_intake` action)
5. Trigger workflow stub (`WorkflowService` — no direct n8n call)
6. Prepare notifications (`NotificationPreparationService`)

## Channel Mapping

| Channel | `source` | `submission_channel` example |
|---------|----------|------------------------------|
| Website form | `WEBSITE` | `web_form` |
| Internal dashboard | `DASHBOARD` | `sales_dashboard` |
| REST API | `API` | `rest_api` |
| n8n webhook | `API` | `n8n` |
| Marty agent | `API` | `marty_agent` |
| Email parser | `EMAIL` | `inbox` |
| CSV import | `CSV` | `bulk_import` |
| WhatsApp | `WHATSAPP` | `whatsapp_bot` |
| Voice assistant | `VOICE` | `voice_ivr` |
| Trade show | `TRADE_SHOW` | `badge_scan` |
| Phone operator | `PHONE` | `call_center` |

## Backward Compatibility

| Legacy path | Behavior |
|-------------|----------|
| `POST /webhooks/n8n/lead` | Delegates to `LeadIntakeService` |
| `POST /webhooks/n8n/lead/marty` | Legacy Marty scoring path |
| `POST /agents/marty` | Intake via service when no `deal_id`, then LLM score |

## Database

Requires migration `002_add_lead_intake_columns`:

```bash
cd backend
alembic upgrade head
```

Adds to `deals`: `lead_source`, `workflow_id`, `submission_channel`.

## Example (PowerShell)

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/leads" `
  -ContentType "application/json" `
  -Body '{"source":"WEBSITE","submission_channel":"web_form","company_name":"City Fire Dept","email":"sales@city.gov","city":"Denver","country":"USA"}'
```
