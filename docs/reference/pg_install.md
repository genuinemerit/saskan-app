# Install Postgresql Database

Setting Up PostgreSQL on DigitalOcean

Since we need PostgreSQL on DigitalOcean, let’s set it up.
Same basic instructions no matter what platform.

1. Install PostgreSQL on the Droplet

SSH into your droplet:

```bash
ssh root@gmerit-nyc2
```

Then install PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev -y
```

- postgresql: the database server
- postgresql-contrib: extra utilities (like UUID generators, etc.)
- libpq-dev: C libraries for PostgreSQL needed to compile Python bindings (psycopg2 etc.)

Enable & start the service:

```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

1. Create a PostgreSQL User & Database

Enter the PostgreSQL shell:

```bash
sudo -i -u postgres
psql
```

Run these commands to create a database and user:

```sql
CREATE DATABASE mint_prod OWNER mint_user;;
CREATE USER mint_user WITH ENCRYPTED PASSWORD 'securepassword';
GRANT ALL PRIVILEGES ON DATABASE mint_prod TO mint_user;
ALTER USER mint_user CREATEDB;
```

This creates:

- A database user mint_user
- A database mint_prod owned by that user

Tip: You can use a different username/db name, but keeping them aligned with the app (mint) can help reduce confusion.
Exit:

```bash
\q
exit
```

🔹 Remember to replace 'securepassword' with a strong password!
🔹 You'll later store this in GitHub Secrets (instead of hardcoding it).

---

```bash
psql -U mint_user_ -d mint_prod_ -h 127.0.0.1 -W
```

Should be prompted for password

```bash
which psql
sudo systemctl status postgresql
```

---

Remove postgresql...

Got it — if you're confident that PostgreSQL isn't currently in use and you're ready for a clean slate, here's how to safely **completely remove PostgreSQL** (including databases, configs, and users):

---

### 🧹 Step-by-Step: Uninstall PostgreSQL

#### ✅ 1. Stop the PostgreSQL service

```bash
sudo systemctl stop postgresql
```

#### ✅ 2. Uninstall PostgreSQL and related packages

This removes the PostgreSQL server and client utilities:

```bash
sudo apt purge --autoremove -y postgresql\* libpq\*
```

> Note: The `\*` wildcard ensures all related versions (e.g. `postgresql-15`) are removed.

#### ✅ 3. Remove data and configuration directories (if you're sure)

```bash
sudo rm -rf /etc/postgresql/ /var/lib/postgresql/ /var/log/postgresql/
```

> Be **very careful** — this erases all databases, logs, and PostgreSQL configs.

#### ✅ 4. Remove the `postgres` system user and group

If PostgreSQL was the only reason the `postgres` user existed:

```bash
sudo deluser --remove-home postgres
sudo delgroup postgres
```

> If the `postgres` user was being used for other services (unlikely on a fresh setup), skip this step.

Once you've done all that, your system should be back to a PostgreSQL-free state.

---

Allow Local App to Connect

PostgreSQL is now running and ready for apps to connect over local UNIX sockets or localhost.

The connection string will look like:

postgresql://mintuser:your_secure_password@localhost/mintdb

Or via environment variable:

export DATABASE_URL="postgresql://mintuser:your_secure_password@localhost/mintdb"

From your Python app or shell:

```bash
psql -U mintuser -d mintdb -h localhost -W
```

You’ll be prompted for a password — verify that it works.

---

## Users

In Practice:

Root is best for setup: Use root or sudo for installing packages and configuring services.

postgres user is required for DB setup: You'll be switching into it regardless of starting user.

mintuser is great for testing your app connection: Once the DB is set up, run app-level things as mintuser.

---

in the Python shell:

```python
import psycopg2

conn = psycopg2.connect(
    dbname="mintdb",
    user="mintuser",
    password="your_password",
    host="localhost"
)

print("Connected:", conn.status)
```

This verifies that:

psycopg2 is installed and usable,

The user and password are correct,

The database exists and is accepting connections.

If it works, you’ll get a successful connection status. If not, you’ll get a traceback you can debug from.

---

`sudo -u postgres psql -c "\l"`

This command:

`sudo -u postgres psql -c "\l"`


Means:

`sudo -u postgres` → run the command as the postgres Unix user

`psql -c "\l"` → open psql, run the SQL meta-command \l (that's a backslash-L), and exit

`\l` (list) shows:

All PostgreSQL databases,

Their owners,

Encoding/collation info,

Access privileges.

📌 Should we include it in your verification steps?
Yes! It’s an excellent way to confirm that our mintdb and mintuser were created correctly and are recognized by PostgreSQL.

---

You got it, 🐢💚 — we’ll go slow, clear, and steady.

Let’s write a minimal **PostgreSQL connection test script** using:

* `psycopg2` (PostgreSQL driver)
* `dotenv` (to load `.env`)
* and a little 🐍 Python

---

### 🐢 Step-by-step Connection Test

#### ✅ 1. Make sure dependencies are installed:

From your virtual environment:

```bash
pip install psycopg2-binary python-dotenv
```

#### ✅ 2. Create a file like `test_db_connection.py`

Here’s the test script:

```python
# test_db_connection.py

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Pull values from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment.")
    exit(1)

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Successfully connected to the database!")

    # Optional: Run a simple query
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("🧠 PostgreSQL version:", version[0])

    conn.close()

except Exception as e:
    print("❌ Database connection failed:")
    print(e)
```

---

### 🧪 Test It:

Run it from the same directory where your `.env` file lives:

```bash
python test_db_connection.py
```

You should see:

```text
✅ Successfully connected to the database!
🧠 PostgreSQL version: PostgreSQL 16.x...
```

---

### 🐇 Optional Refinements (for later)

- Split `DB_NAME`, `DB_USER`, `DB_PASS` etc. if you don’t want to use a full `DATABASE_URL`
- Use SQLAlchemy in the actual app instead of raw psycopg2

Let me know once you run it — or if you’d like to test a query like listing tables or inserting mock data!
