import sys
import os

# Garante que a pasta raiz do projeto esteja sempre no sys.path ao rodar pytest no Windows/Linux
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
