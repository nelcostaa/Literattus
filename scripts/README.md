# Literattus Management Scripts

Simple scripts to manage your Literattus development environment.

## Database Triggers and Procedures

The project includes database triggers and stored procedures for audit logging and statistics.

### Setup

Apply triggers and procedures to your database:

```bash
# Using Python script (recommended)
python3 scripts/apply_triggers_procedures.py

# Or manually via MySQL
mysql -u root -p literattus < scripts/triggers_and_procedures.sql
```

### What's Included

1. **Audit Log Table** (`audit_log`)
   - Tracks all changes to the `reading_progress` table
   - Records INSERT, UPDATE, and DELETE operations
   - Stores old and new values in JSON format

2. **Triggers** (on `reading_progress` table)
   - `trg_reading_progress_insert` - Logs new reading progress entries
   - `trg_reading_progress_update` - Logs updates to reading progress
   - `trg_reading_progress_delete` - Logs deletions of reading progress

3. **Stored Procedure** (`sp_get_user_reading_stats`)
   - Returns comprehensive reading statistics for a user
   - Includes: total books, reading/completed counts, pages read, average rating, etc.
   - Usage: `CALL sp_get_user_reading_stats(user_id);`

### Example Usage

```sql
-- View recent audit log entries
SELECT * FROM audit_log 
ORDER BY changed_at DESC 
LIMIT 10;

-- Get reading statistics for user ID 1
CALL sp_get_user_reading_stats(1);

-- View all triggers
SHOW TRIGGERS WHERE `Table` = 'reading_progress';
```

## Quick Start

```bash
# After booting your PC
./scripts/start

# To stop
./scripts/stop

# Check status
./scripts/status

# View logs
./scripts/logs
```

## Available Commands

### `./scripts/start [--force]`
Start all Literattus services (frontend, backend).

**Options:**
- `--force` - Clean up ports and force restart if services are stuck

**Examples:**
```bash
./scripts/start              # Normal start
./scripts/start --force      # Force start (cleans up stuck processes)
```

### `./scripts/stop`
Stop all Literattus services cleanly.

### `./scripts/status`
Show current status of all services.

### `./scripts/logs [service]`
View service logs in real-time.

**Examples:**
```bash
./scripts/logs              # All services
./scripts/logs frontend     # Frontend only
./scripts/logs backend      # Backend only
```

## Common Workflows

### After Booting Your PC
```bash
cd /home/nelso/Documents/Literattus
./scripts/start
```

### Making CSS Changes
1. Edit `frontend/static/css/main.css`
2. Save the file
3. Refresh your browser (`Ctrl+R`)
4. Changes appear immediately (hot reload)

### If Port is Already in Use
```bash
./scripts/start --force
```

This will:
- Stop all containers
- Kill processes on ports 8000 and 8080
- Start fresh

### Debugging Issues
```bash
# Check what's running
./scripts/status

# View logs
./scripts/logs

# View specific service logs
./scripts/logs backend
./scripts/logs frontend
```

## Access Points

Once started:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/api/docs

## Troubleshooting

### Services won't start
```bash
./scripts/start --force
```

### Can't see latest CSS changes
1. Hard refresh: `Ctrl+Shift+R`
2. If that doesn't work:
   ```bash
   ./scripts/stop
   ./scripts/start
   ```

### Check if Docker is running
```bash
sudo systemctl status docker
```

### Services are slow
```bash
# Check logs for errors
./scripts/logs
```
