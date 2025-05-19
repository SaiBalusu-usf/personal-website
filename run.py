import os
import sys
sys.path.insert(0, os.path.dirname(__file__ ))
from src.main import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
