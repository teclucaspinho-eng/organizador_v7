import sys
from pathlib import Path

# Garante que a pasta raiz do projeto esteja no path
sys.path.insert(0, str(Path(__file__).parent))

from interface.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
