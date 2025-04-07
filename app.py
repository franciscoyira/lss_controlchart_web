"""
Entry point for the application.
This file exposes the Flask server that Gunicorn will use.
"""

try:
    from app.app import server
except Exception as e:
    import sys
    print(f"Failed to import server: {e}", file=sys.stderr)
    raise

if __name__ == '__main__':
    import os
    from app.app import app
    port = int(os.environ.get('PORT', 8080))
    app.run_server(host='0.0.0.0', port=port, debug=False) 