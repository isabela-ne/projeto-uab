import sys
import os

# Adiciona a raiz do projeto ao sys.path para que o pytest encontre o módulo 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
