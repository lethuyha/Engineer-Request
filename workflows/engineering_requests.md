# Workflow: Engineering Request Management

## Objective
Manage the full lifecycle of engineering requests — from submission by operators to assignment, tracking, and completion by engineers — with a reporting dashboard.

## Setup (one-time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create staff Excel file with sample names
python tools/setup_staff.py

# 3. Edit data/staff.xlsx to add real team members
#    Sheet "Requesters": one name per row starting row 2
#    Sheet "Engineers": one name per row starting row 2
#    Save the file, then restart the server.

# 4. Start the server
uvicorn main:app --reload
# App runs at http://localhost:8000
```

## File Structure

```
main.py              # FastAPI server — routes and startup
tools/
  db.py              # SQLite CRUD for requests (data/requests.db)
  excel_reader.py    # Reads data/staff.xlsx (requesters + engineers)
  setup_staff.py     # One-time seed: creates data/staff.xlsx
data/
  staff.xlsx         # Edit this to manage your team list
  requests.db        # Auto-created SQLite database
uploads/             # Uploaded file attachments (auto-created)
static/
  index.html         # Landing page
  submit.html        # Operator: submit new request
  review.html        # Engineer: review, assign, update status
  dashboard.html     # Reporting: weekly volume, status, aging
```

## Tools Used

| Tool | Purpose |
|------|---------|
| `tools/db.py` | SQLite read/write for all request data |
| `tools/excel_reader.py` | Parse staff names from Excel |
| `tools/setup_staff.py` | Bootstrap the staff Excel file |

## Pages & API

| Route | Description |
|-------|-------------|
| `GET /` | Landing page |
| `GET /submit` | Request submission form |
| `GET /review` | Engineer review & edit interface |
| `GET /dashboard` | Reporting dashboard |
| `GET /api/staff` | Returns requesters and engineers lists |
| `POST /api/requests` | Create new request (multipart/form-data) |
| `GET /api/requests` | List requests with optional filters: `requester`, `status`, `assignee` |
| `PATCH /api/requests/{id}` | Update assignee and/or status |
| `GET /api/dashboard` | Aggregated stats for dashboard charts |

## Status Lifecycle

```
SUBMITTED → ASSIGNED → IN PROGRESS → DONE
```

- **SUBMITTED**: Request received, awaiting assignment
- **ASSIGNED**: Engineer assigned, `date_assigned` recorded
- **IN PROGRESS**: Work started, `date_in_progress` recorded (Aging clock starts)
- **DONE**: Completed, `date_done` recorded

## Aging Definition

> Aging = number of calendar days from `date_in_progress` to today (or `date_done` if completed).

Aging is only shown when status is IN PROGRESS or DONE. Color coding:
- Green: ≤ 3 days
- Amber: 4–7 days
- Red: > 7 days

## Managing Staff

1. Open `data/staff.xlsx`
2. Edit the **Requesters** sheet (column A, starting row 2) to add/remove requesters
3. Edit the **Engineers** sheet (column A, starting row 2) to add/remove engineers
4. Save the file
5. **Restart the server** — staff lists are loaded at startup

## Edge Cases & Known Constraints

| Situation | Behavior |
|-----------|---------|
| `data/staff.xlsx` missing | App starts normally; dropdowns show empty lists |
| File attachment exceeds disk | OS error — no size limit enforced (add if needed) |
| Status set backward (e.g., DONE → IN PROGRESS) | Allowed; `date_in_progress` is preserved (not reset) |
| Multiple requests by same person | Supported; filter by Requester on Review page |
| No requests yet | Dashboard shows empty charts gracefully |
| Server restart | All data persists in `data/requests.db` |

## Notes

- The server must be restarted after editing `data/staff.xlsx`
- Uploaded files are stored in `uploads/` with a random hex prefix to prevent collisions
- The dashboard auto-refreshes every 60 seconds
- SQLite is sufficient for small teams; migrate to PostgreSQL for > 1,000 concurrent users
