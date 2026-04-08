from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime
from utils.database import execute_query
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/registrar', methods=['POST'])
def registrar():
    data = request.json

    if not data.get('nome') or not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400

    # Verificar se email já existe
    existing = execute_query(
        "SELECT id_cliente FROM cliente WHERE email = %s",
        (data['email'],),
        fetch_one=True
    )

    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409

    # Hash da senha
    senha_hash = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Inserir cliente
    cliente_id = execute_query("""
        INSERT INTO cliente (nome, telefone, email, senha_hash, data_cadastro, status)
        VALUES (%s, %s, %s, %s, CURDATE(), 'ativo')
    """, (data['nome'], data.get('telefone', ''), data['email'], senha_hash), commit=True)

    return jsonify({'message': 'Cliente cadastrado com sucesso', 'id_cliente': cliente_id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    # Buscar cliente
    cliente = execute_query("""
        SELECT id_cliente, nome, email, senha_hash, status
        FROM cliente
        WHERE email = %s
    """, (data['email'],), fetch_one=True)

    if not cliente:
        return jsonify({'error': 'Email ou senha inválidos'}), 401

    if cliente['status'] != 'ativo':
        return jsonify({'error': 'Usuário não está ativo'}), 401

    # Verificar senha
    if not bcrypt.checkpw(data['senha'].encode('utf-8'), cliente['senha_hash'].encode('utf-8')):
        return jsonify({'error': 'Email ou senha inválidos'}), 401

    # Gerar JWT
    token = jwt.encode({
        'user_id': cliente['id_cliente'],
        'email': cliente['email'],
        'nome': cliente['nome'],
        'role': 'cliente',
        'exp': datetime.utcnow() + Config.JWT_EXPIRATION
    }, Config.JWT_SECRET, algorithm='HS256')

    # Remover senha_hash do retorno
    del cliente['senha_hash']

    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'usuario': cliente
    })

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
            'nome': payload['nome']
        })
    except:
        return jsonify({'authenticated': False}), 401