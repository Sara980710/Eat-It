
## 🛠️ Install & Run Instructions

This project is a minimal **Flask + SQLite** web app for managing recipes and shopping lists.

---

### ✅ Requirements

* Python 3.8+
* Git (optional)

---

### 🚀 Setup (Linux/macOS/Windows)

```bash
# 1. Clone or download the project
git clone https://github.com/your-user/your-repo.git
cd your-repo

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Initialize the SQLite database
flask --app app:create_app init-db

# 5. Start the development server
flask --app app:create_app run --debug
```

---

### 🌐 Open in Browser

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) to use the app.

---

### 🧪 Tips

* If you see `Error: Failed to find Flask application...`, make sure to use `--app app:create_app`
* To avoid repeating `--app app:create_app`, you can set it once:

  ```bash
  export FLASK_APP=app:create_app       # macOS/Linux
  set FLASK_APP=app:create_app          # Windows CMD
  $env:FLASK_APP = "app:create_app"     # PowerShell
  ```

---

Let me know if you want a `Dockerfile` or deployment instructions added too.

### Online database

  ```bash
export DATABASE_URL="postgresql://postgres:yourpassword@db.xxxx.supabase.co:5432/postgres"
  ```

  ```poweshell
  $env:DATABASE_URL="postgresql://postgres:4foo!QM74R2*@db.bpxxugxbxwrcvcghreco.supabase.co:5432/postgres"
  ```
  