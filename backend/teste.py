import bcrypt
import mysql.connector
from config import Config

# Conectar ao banco
conn = mysql.connector.connect(**Config.DB_CONFIG)
cursor = conn.cursor()

# Gerar hash para senha "123456"
senha = "123456"
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"Hash gerado: {senha_hash}")

# Atualizar todos os usuários
cursor.execute("""
    UPDATE usuario SET senha_hash = %s
""", (senha_hash,))

conn.commit()
print(f"✅ {cursor.rowcount} usuários atualizados com a nova senha '123456'")

# Verificar
cursor.execute("SELECT id_usuario, nome, email, tipo, LENGTH(senha_hash) as tam_hash FROM usuario")
usuarios = cursor.fetchall()

print("\n📋 Usuários atualizados:")
for u in usuarios:
    print(f"  - {u[1]} ({u[2]}) - tipo: {u[3]} - hash length: {u[4]}")

cursor.close()
conn.close()