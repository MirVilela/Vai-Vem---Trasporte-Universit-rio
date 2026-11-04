"""Sobe o app em uma porta de teste usando uma COPIA do banco.
Uso: python servidor_teste.py <caminho_da_copia.db> <porta>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import app  # noqa: E402

app.DB_PATH = sys.argv[1]
app.init_db()
app.app.run(host="127.0.0.1", port=int(sys.argv[2]), debug=False, threaded=True)
