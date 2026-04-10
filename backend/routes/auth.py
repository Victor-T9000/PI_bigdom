from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime
from utils.database import execute_query
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# =============================================
# LOGIN CLIENTE (usa tabela usuario)
# =============================================
@auth_bp.route('/login', methods=['POST'])
def login_cliente():
    data = request.json
    
    print(f"🔍 Tentativa de login - Email: {data.get('email')}")  # DEBUG

    if not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    # Buscar na tabela usuario (tipo = 'cliente')
    usuario = execute_query("""
        SELECT id_usuario, nome, email, senha_hash, telefone, tipo, status
        FROM usuario
        WHERE email = %s AND tipo = 'cliente'
    """, (data['email'],), fetch_one=True)

    print(f"🔍 Usuario encontrado: {usuario}")  # DEBUG

    if not usuario:
        print(f"❌ Usuario não encontrado para email: {data['email']}")  # DEBUG
        return jsonify({'error': 'Email ou senha inválidos'}), 401

    if usuario['status'] != 'ativo':
        print(f"❌ Usuario status: {usuario['status']}")  # DEBUG
        return jsonify({'error': 'Usuário não está ativo'}), 401

    # Verificar senha
    senha_correta = bcrypt.checkpw(data['senha'].encode('utf-8'), usuario['senha_hash'].encode('utf-8'))
    print(f"🔍 Senha correta? {senha_correta}")  # DEBUG

    if not senha_correta:
        print(f"❌ Senha incorreta para: {data['email']}")  # DEBUG
        return jsonify({'error': 'Email ou senha inválidos'}), 401

    # Gerar JWT
    token = jwt.encode({
        'user_id': usuario['id_usuario'],
        'email': usuario['email'],
        'nome': usuario['nome'],
        'tipo': 'cliente',
        'exp': datetime.utcnow() + Config.JWT_EXPIRATION
    }, Config.JWT_SECRET, algorithm='HS256')

    del usuario['senha_hash']
    
    print(f"✅ Login成功 - Token gerado para: {usuario['email']}")  # DEBUG

    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'usuario': usuario,
        'tipo': 'cliente'
    })
# =============================================
# LOGIN BARBEARIA (usa tabela usuario)
# =============================================
@auth_bp.route('/barbearia/login', methods=['POST'])
def login_barbearia():
    data = request.json
    
    print(f"🔍 Tentativa login barbearia - Email: {data.get('email')}")  # DEBUG
    
    if not data.get('email') or not data.get('senha'):
        print("❌ Email ou senha não fornecidos")
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    # Buscar na tabela usuario (tipo = 'barbearia')
    usuario = execute_query("""
        SELECT id_usuario, nome, email, senha_hash, telefone, tipo, status, id_referencia
        FROM usuario
        WHERE email = %s AND tipo = 'barbearia'
    """, (data['email'],), fetch_one=True)
    
    print(f"🔍 Usuario encontrado: {usuario}")  # DEBUG

    if not usuario:
        print(f"❌ Usuario não encontrado para email: {data['email']}")
        return jsonify({'error': 'Email ou senha inválidos'}), 401

    if usuario['status'] != 'ativo':
        print(f"❌ Usuario status: {usuario['status']}")
        return jsonify({'error': 'Usuário não está ativo'}), 401

    # Verificar senha
    print(f"🔍 Hash no banco: {usuario['senha_hash']}")  # DEBUG
    print(f"🔍 Senha fornecida: {data['senha']}")  # DEBUG
    
    try:
        senha_correta = bcrypt.checkpw(data['senha'].encode('utf-8'), usuario['senha_hash'].encode('utf-8'))
        print(f"🔍 Senha correta? {senha_correta}")  # DEBUG
    except Exception as e:
        print(f"❌ Erro ao verificar senha: {e}")
        return jsonify({'error': 'Erro interno ao verificar senha'}), 500

    if not senha_correta:
        print(f"❌ Senha incorreta para: {data['email']}")
        return jsonify({'error': 'Email ou senha inválidos'}), 401

    # Gerar JWT
    token = jwt.encode({
        'user_id': usuario['id_usuario'],
        'email': usuario['email'],
        'nome': usuario['nome'],
        'tipo': 'barbearia',
        'barbearia_id': usuario['id_referencia'],
        'exp': datetime.utcnow() + Config.JWT_EXPIRATION
    }, Config.JWT_SECRET, algorithm='HS256')

    del usuario['senha_hash']
    
    print(f"✅ Login barbearia bem sucedido: {usuario['email']}")  # DEBUG

    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'usuario': usuario,
        'tipo': 'barbearia'
    })


# =============================================
# LOGIN ADMIN (usa tabela usuario)
# =============================================
@auth_bp.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.json

    if not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    # Buscar na tabela usuario (tipo = 'admin')
    usuario = execute_query("""
        SELECT id_usuario, nome, email, senha_hash, telefone, tipo, status
        FROM usuario
        WHERE email = %s AND tipo = 'admin'
    """, (data['email'],), fetch_one=True)

    if not usuario:
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if usuario['status'] != 'ativo':
        return jsonify({'error': 'Usuário não está ativo'}), 401

    # Verificar senha
    if not bcrypt.checkpw(data['senha'].encode('utf-8'), usuario['senha_hash'].encode('utf-8')):
        return jsonify({'error': 'Credenciais inválidas'}), 401

    # Gerar JWT
    token = jwt.encode({
        'user_id': usuario['id_usuario'],
        'email': usuario['email'],
        'nome': usuario['nome'],
        'tipo': 'admin',
        'exp': datetime.utcnow() + Config.JWT_EXPIRATION
    }, Config.JWT_SECRET, algorithm='HS256')

    # Remover senha_hash do retorno
    del usuario['senha_hash']

    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'usuario': usuario,
        'tipo': 'admin'
    })


# =============================================
# REGISTRAR CLIENTE (usa tabela usuario)
# =============================================
@auth_bp.route('/registrar', methods=['POST'])
def registrar_cliente():
    data = request.json

    if not data.get('nome') or not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400

    # Verificar se email já existe
    existing = execute_query(
        "SELECT id_usuario FROM usuario WHERE email = %s",
        (data['email'],),
        fetch_one=True
    )

    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409

    # Hash da senha
    senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Inserir na tabela usuario
    usuario_id = execute_query("""
        INSERT INTO usuario (nome, email, senha_hash, telefone, tipo, status)
        VALUES (%s, %s, %s, %s, 'cliente', 'ativo')
    """, (data['nome'], data['email'], senha_hash, data.get('telefone', '')), commit=True)

    return jsonify({'message': 'Cadastro realizado com sucesso! Faça login.', 'id_usuario': usuario_id}), 201


# =============================================
# VERIFICAR TOKEN
# =============================================
@auth_bp.route('/verificar', methods=['GET'])
def verificar_token():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'authenticated': False}), 401

    try:
        if token.startswith('Bearer '):
            token = token[7:]

        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return jsonify({
            'authenticated': True,
            'user_id': payload['user_id'],
            'email': payload['email'],
            'nome': payload.get('nome', ''),
            'tipo': payload.get('tipo', 'cliente')
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'authenticated': False, 'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'authenticated': False, 'error': 'Token inválido'}), 401