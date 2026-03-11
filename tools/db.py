import sqlite3
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path("data/requests.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_submitted TEXT NOT NULL,
            secteur TEXT NOT NULL,
            requester TEXT NOT NULL,
            description TEXT NOT NULL,
            attachment_path TEXT,
            status TEXT NOT NULL DEFAULT 'SUBMITTED',
            assignee TEXT,
            date_assigned TEXT,
            date_in_progress TEXT,
            date_done TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    if count > 0:
        conn.close()
        return

    from datetime import timedelta
    today = date.today()

    records = [
        # (date_submitted, secteur, requester, description, type, status, assignee, date_assigned, date_in_progress, date_done)
        (today - timedelta(days=42), "Fonderie", "Marc Dupont",    "Révision du process de coulée pour réduire les porosités",          "Amélioration process",  "DONE",        "Sophie Martin",  today - timedelta(days=40), today - timedelta(days=38), today - timedelta(days=10)),
        (today - timedelta(days=38), "Usinage",  "Lucie Bernard",  "Mise à jour des paramètres d'usinage CNC sur ligne 3",              "Modification technique", "DONE",        "Thomas Leroy",   today - timedelta(days=36), today - timedelta(days=34), today - timedelta(days=15)),
        (today - timedelta(days=35), "Qualité",  "Jean Moreau",    "Analyse des non-conformités du lot QC-2024-112",                    "Analyse qualité",        "DONE",        "Sophie Martin",  today - timedelta(days=33), today - timedelta(days=31), today - timedelta(days=20)),
        (today - timedelta(days=30), "Fonderie", "Marie Lefebvre", "Optimisation du cycle thermique four 4",                            "Amélioration process",   "DONE",        "Thomas Leroy",   today - timedelta(days=28), today - timedelta(days=26), today - timedelta(days=12)),
        (today - timedelta(days=28), "Maintenance","Paul Girard",  "Inspection préventive robot de sablage",                            "Maintenance préventive", "DONE",        "Ahmed Benali",   today - timedelta(days=26), today - timedelta(days=25), today - timedelta(days=8)),
        (today - timedelta(days=25), "Usinage",  "Lucie Bernard",  "Qualification nouvel outil de fraisage Ø32",                        "Qualification",          "DONE",        "Thomas Leroy",   today - timedelta(days=23), today - timedelta(days=22), today - timedelta(days=5)),
        (today - timedelta(days=21), "Qualité",  "Jean Moreau",    "Mise à jour de la gamme de contrôle pièce ref. AT-7712",            "Modification technique",  "IN PROGRESS", "Sophie Martin",  today - timedelta(days=19), today - timedelta(days=17), None),
        (today - timedelta(days=18), "Fonderie", "Marc Dupont",    "Étude faisabilité nouveau alliage aluminium A357",                  "Étude faisabilité",      "IN PROGRESS", "Ahmed Benali",   today - timedelta(days=16), today - timedelta(days=14), None),
        (today - timedelta(days=14), "HSE",      "Claire Rousseau","Mise à jour procédure sécurité zone de fusion",                     "Documentation",          "IN PROGRESS", "Sophie Martin",  today - timedelta(days=12), today - timedelta(days=11), None),
        (today - timedelta(days=12), "Usinage",  "Paul Girard",    "Problème vibrations broche machine M12 à investiguer",              "Analyse qualité",        "ASSIGNED",    "Thomas Leroy",   today - timedelta(days=10), None,                       None),
        (today - timedelta(days=10), "Maintenance","Marie Lefebvre","Remplacement joints hydrauliques presse 500T",                     "Maintenance préventive", "ASSIGNED",    "Ahmed Benali",   today - timedelta(days=8),  None,                       None),
        (today - timedelta(days=7),  "Qualité",  "Jean Moreau",    "Dérogation client pièce hors-tolérance ref BT-4401",                "Modification technique",  "ASSIGNED",    "Sophie Martin",  today - timedelta(days=5),  None,                       None),
        (today - timedelta(days=5),  "Fonderie", "Marc Dupont",    "Calibration capteurs température four 2",                           "Qualification",          "SUBMITTED",   None,             None,                       None,                       None),
        (today - timedelta(days=4),  "Usinage",  "Lucie Bernard",  "Demande d'outillage spécial pour ref. AT-9003",                    "Étude faisabilité",      "SUBMITTED",   None,             None,                       None,                       None),
        (today - timedelta(days=3),  "HSE",      "Claire Rousseau","Formation sécurité machines équipe nuit",                          "Documentation",          "SUBMITTED",   None,             None,                       None,                       None),
        (today - timedelta(days=2),  "Qualité",  "Paul Girard",    "Audit interne procédure métrologie salle de contrôle",             "Analyse qualité",        "SUBMITTED",   None,             None,                       None,                       None),
        (today - timedelta(days=1),  "Fonderie", "Marie Lefebvre", "Demande de modification paramètres injection moule M-07",          "Amélioration process",   "SUBMITTED",   None,             None,                       None,                       None),
        (today,                      "Usinage",  "Marc Dupont",    "Optimisation trajectoires robot chargement/déchargement",          "Amélioration process",   "SUBMITTED",   None,             None,                       None,                       None),
        (today - timedelta(days=9),  "Maintenance","Jean Moreau",   "Remplacement variateur de fréquence convoyeur C3",                 "Maintenance préventive", "CANCELLED",   "Ahmed Benali",   today - timedelta(days=8),  None,                       None),
    ]

    now = datetime.now().isoformat(timespec="seconds")
    for r in records:
        (ds, secteur, requester, desc, rtype, status, assignee,
         date_assigned, date_in_progress, date_done) = r
        conn.execute(
            """INSERT INTO requests
               (date_submitted, secteur, requester, description, type,
                status, assignee, date_assigned, date_in_progress, date_done,
                attachment_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)""",
            (
                ds.isoformat(), secteur, requester, desc, rtype,
                status, assignee,
                date_assigned.isoformat() if date_assigned else None,
                date_in_progress.isoformat() if date_in_progress else None,
                date_done.isoformat() if date_done else None,
                now,
            ),
        )
    conn.commit()
    conn.close()


def create_request(secteur, requester, description, type=None, attachment_path=None):
    from tools.logger import log_creation

    conn = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    today = date.today().isoformat()
    cursor = conn.execute(
        """INSERT INTO requests
           (date_submitted, secteur, requester, description, type, attachment_path, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (today, secteur, requester, description, type, attachment_path, now),
    )
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()

    log_creation(request_id, secteur, requester, description, type)
    return request_id


def get_all_requests(requester=None, status=None, assignee=None, type=None):
    conn = get_connection()
    query = "SELECT * FROM requests WHERE 1=1"
    params = []
    if requester:
        query += " AND requester = ?"
        params.append(requester)
    if status:
        query += " AND status = ?"
        params.append(status)
    if assignee:
        query += " AND assignee = ?"
        params.append(assignee)
    if type:
        query += " AND type = ?"
        params.append(type)
    query += " ORDER BY date_submitted DESC, id DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    today = date.today()
    result = []
    for row in rows:
        r = dict(row)
        end = date.fromisoformat(r["date_done"]) if r.get("date_done") else today
        if r.get("date_in_progress"):
            start_ip = date.fromisoformat(r["date_in_progress"])
            r["aging_days"] = (end - start_ip).days
        else:
            r["aging_days"] = None
        start_sub = date.fromisoformat(r["date_submitted"])
        r["lead_time_days"] = (end - start_sub).days
        result.append(r)
    return result


def update_request(request_id, assignee=None, status=None, description=None, type=None):
    from tools.logger import log_changes

    conn = get_connection()
    today = date.today().isoformat()

    row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not row:
        conn.close()
        return None
    current = dict(row)

    fields = []
    params = []

    if description is not None:
        fields.append("description = ?")
        params.append(description)

    if type is not None:
        fields.append("type = ?")
        params.append(type)

    if assignee is not None:
        fields.append("assignee = ?")
        params.append(assignee if assignee else None)

    if status is not None and status != current["status"]:
        fields.append("status = ?")
        params.append(status)

        if status == "ASSIGNED":
            fields.append("date_assigned = ?")
            params.append(today)
        elif status == "IN PROGRESS":
            if not current.get("date_in_progress"):
                fields.append("date_in_progress = ?")
                params.append(today)
        elif status == "DONE":
            fields.append("date_done = ?")
            params.append(today)
            if not current.get("date_in_progress"):
                fields.append("date_in_progress = ?")
                params.append(today)

    if not fields:
        conn.close()
        return current

    params.append(request_id)
    query = f"UPDATE requests SET {', '.join(fields)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    conn.close()

    log_changes(request_id, current, assignee, status, description, type)


def get_dashboard_data():
    conn = get_connection()

    weekly_rows = conn.execute("""
        SELECT
            strftime('%Y-W%W', date_submitted) AS week,
            COUNT(*) AS count
        FROM requests
        GROUP BY week
        ORDER BY week
    """).fetchall()

    status_rows = conn.execute("""
        SELECT status, COUNT(*) AS count
        FROM requests
        GROUP BY status
    """).fetchall()

    type_rows = conn.execute("""
        SELECT COALESCE(type, 'Non spécifié') AS type, COUNT(*) AS count
        FROM requests
        GROUP BY type
        ORDER BY count DESC
    """).fetchall()

    aging_rows = conn.execute("""
        SELECT id, requester, secteur, date_submitted, description,
               assignee, status, date_in_progress, date_done
        FROM requests
        WHERE status NOT IN ('SUBMITTED', 'ASSIGNED', 'CANCELLED')
           OR date_in_progress IS NOT NULL
        ORDER BY date_submitted ASC
    """).fetchall()

    conn.close()

    today = date.today()
    aging = []
    for row in aging_rows:
        r = dict(row)
        end = date.fromisoformat(r["date_done"]) if r.get("date_done") else today
        r["lead_time_days"] = (end - date.fromisoformat(r["date_submitted"])).days
        if r.get("date_in_progress"):
            r["aging_days"] = (end - date.fromisoformat(r["date_in_progress"])).days
        else:
            r["aging_days"] = None
        aging.append(r)

    done = [r for r in aging if r.get("date_done")]
    avg_lead = round(sum(r["lead_time_days"] for r in done) / len(done), 1) if done else None
    avg_exec = round(sum(r["aging_days"] for r in done if r["aging_days"] is not None) /
                     len([r for r in done if r["aging_days"] is not None]), 1) if done else None

    return {
        "by_week": [dict(r) for r in weekly_rows],
        "by_status": [dict(r) for r in status_rows],
        "by_type": [dict(r) for r in type_rows],
        "aging": sorted(aging, key=lambda x: x["lead_time_days"], reverse=True),
        "avg_lead_time": avg_lead,
        "avg_exec_time": avg_exec,
    }
