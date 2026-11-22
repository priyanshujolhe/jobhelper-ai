import os
import sys
from pathlib import Path

# Automatically detect and re-exec with the project's virtual environment if not already active
basedir = Path(__file__).resolve().parent
venv_python = basedir / ".venv" / "bin" / "python"
if venv_python.exists() and os.path.realpath(sys.executable) != os.path.realpath(venv_python):
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

from app import create_app

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    if "--check" in sys.argv:
        print("\n✅ JobHelper AI configuration, database, and blueprints are verified and healthy!")
        sys.exit(0)

    # Use port 5001 by default on macOS to avoid Apple AirPlay Receiver conflict on 5000
    port = int(os.getenv("PORT", 5001))

    print(f"\n=======================================================")
    print(f"🚀 JobHelper AI is running!")
    print(f"👉 Local Web URL:   http://127.0.0.1:{port}")
    print(f"👉 Alternative:     http://localhost:{port}")
    print(f"=======================================================\n", flush=True)

    # Bind to 0.0.0.0 so both 127.0.0.1 and localhost resolve seamlessly on macOS
    app.run(host="0.0.0.0", port=port, debug=True)
