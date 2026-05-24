from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import os
from compilador.integrador import compilar_treino

app = Flask(__name__)
CORS(app)

def conectar():
    return psycopg2.connect(
        host="localhost",
        database="academia-jair",
        user="postgres",
        password="LucasLisboa123"
    )

# ── LOGIN ──────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    cpf = dados["cpf"]
    senha = dados["senha"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome FROM usuarios WHERE cpf = %s AND senha = %s",
        (cpf, senha)
    )
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return jsonify({"sucesso": True, "id": usuario[0], "nome": usuario[1]})
    else:
        return jsonify({"sucesso": False, "mensagem": "CPF ou senha incorretos"})

# ── DADOS DO USUARIO ───────────────────────────────
@app.route("/usuario/<int:usuario_id>", methods=["GET"])
def get_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, cpf, peso, altura, idade FROM usuarios WHERE id = %s",
        (usuario_id,)
    )
    u = cursor.fetchone()
    conn.close()

    if u:
        return jsonify({
            "id": u[0], "nome": u[1], "cpf": u[2],
            "peso": float(u[3]) if u[3] else None,
            "altura": float(u[4]) if u[4] else None,
            "idade": u[5],
            "frequencia": 3
        })
    return jsonify({"erro": "Usuário não encontrado"}), 404

# ── AVISOS ─────────────────────────────────────────
@app.route("/avisos", methods=["GET"])
def get_avisos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, mensagem FROM avisos ORDER BY data_criacao DESC LIMIT 5")
    avisos = cursor.fetchall()
    conn.close()
    return jsonify([{"id": a[0], "mensagem": a[1]} for a in avisos])

# ── TREINOS ────────────────────────────────────────
@app.route("/treinos/<int:usuario_id>/<string:letra>", methods=["GET"])
def get_treino(usuario_id, letra):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM treinos WHERE usuario_id = %s AND nome ILIKE %s",
        (usuario_id, f"%Treino {letra}%")
    )
    treino = cursor.fetchone()

    if not treino:
        conn.close()
        return jsonify([])

    cursor.execute(
        "SELECT nome, series, carga, repeticoes FROM exercicios WHERE treino_id = %s",
        (treino[0],)
    )
    exercicios = cursor.fetchall()
    conn.close()

    return jsonify([
        {"nome": e[0], "series": e[1], "carga": float(e[2]) if e[2] else 0, "repeticoes": e[3], "treino_id": treino[0]}
        for e in exercicios
    ])

# ── CRIAR TREINO ───────────────────────────────────
@app.route("/treinos", methods=["POST"])
def criar_treino():
    dados = request.json
    usuario_id = dados["usuario_id"]
    nome = dados["nome"]
    exercicios = dados["exercicios"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO treinos (nome, usuario_id) VALUES (%s, %s) RETURNING id",
        (nome, usuario_id)
    )
    treino_id = cursor.fetchone()[0]

    for ex in exercicios:
        cursor.execute(
            "INSERT INTO exercicios (nome, series, carga, repeticoes, treino_id) VALUES (%s, %s, %s, %s, %s)",
            (ex["nome"], ex["series"], ex["carga"], ex["repeticoes"], treino_id)
        )
    
    resultado = compilar_treino(nome, exercicios)
    print("Compilador rodou:", resultado["codigo_gerado"])

    conn.commit()
    conn.close()

    return jsonify({"sucesso": True, "treino_id": treino_id})

# ── SERVIR FRONTEND ────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:filename>")
def frontend(filename):
    return send_from_directory("../frontend", filename)

# ── REGISTRAR EXECUÇÃO DO TREINO ───────────────────
@app.route("/historico", methods=["POST"])
def registrar_historico():
    dados = request.json
    usuario_id = dados["usuario_id"]
    treino_id = dados["treino_id"]
    exercicios = dados["exercicios"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO historico_treino (usuario_id, treino_id) VALUES (%s, %s) RETURNING id",
        (usuario_id, treino_id)
    )
    historico_id = cursor.fetchone()[0]

    for ex in exercicios:
        cursor.execute(
            "INSERT INTO historico_exercicio (historico_treino_id, exercicio_nome, series, carga, repeticoes) VALUES (%s, %s, %s, %s, %s)",
            (historico_id, ex["nome"], ex["series"], ex["carga"], ex["repeticoes"])
        )

    conn.commit()
    conn.close()
    return jsonify({"sucesso": True})

# ── BUSCAR HISTORICO DO USUARIO ─────────────────────
@app.route("/historico/<int:usuario_id>", methods=["GET"])
def get_historico(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    treino_filtro = request.args.get('treino', '')

    cursor.execute("""
        SELECT ht.data_execucao, t.nome, he.exercicio_nome, he.carga, he.series, he.repeticoes
        FROM historico_treino ht
        JOIN treinos t ON t.id = ht.treino_id
        JOIN historico_exercicio he ON he.historico_treino_id = ht.id
        WHERE ht.usuario_id = %s AND (%s = '' OR t.nome ILIKE %s)
        ORDER BY ht.data_execucao DESC
    """, (usuario_id, treino_filtro, f"%Treino {treino_filtro}%"))

    rows = cursor.fetchall()
    conn.close()

    resultado = {}
    for row in rows:
        data = row[0].strftime("%d/%m/%Y")
        treino = row[1]
        ex_nome = row[2]
        carga = float(row[3]) if row[3] else 0
        series = row[4]
        reps = row[5]

        if ex_nome not in resultado:
            resultado[ex_nome] = []
        resultado[ex_nome].append({
            "data": data, "treino": treino,
            "carga": carga, "series": series, "repeticoes": reps
        })

    return jsonify(resultado)

# ── PROGRESSO GERAL DO PERFIL ──────────────────────
@app.route("/progresso_geral/<int:usuario_id>", methods=["GET"])
def progresso_geral(usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    # Total de treinos feitos
    cursor.execute(
        "SELECT COUNT(*) FROM historico_treino WHERE usuario_id = %s",
        (usuario_id,)
    )
    total_treinos = cursor.fetchone()[0]

    # Treinos por semana (últimas 4 semanas)
    cursor.execute("""
        SELECT DATE_TRUNC('week', data_execucao) as semana, COUNT(*) as total
        FROM historico_treino
        WHERE usuario_id = %s
        GROUP BY semana
        ORDER BY semana DESC
        LIMIT 4
    """, (usuario_id,))
    por_semana = [{"semana": str(r[0])[:10], "total": r[1]} for r in cursor.fetchall()]

    # Qual treino mais frequente
    cursor.execute("""
        SELECT t.nome, COUNT(*) as total
        FROM historico_treino ht
        JOIN treinos t ON t.id = ht.treino_id
        WHERE ht.usuario_id = %s
        GROUP BY t.nome
        ORDER BY total DESC
        LIMIT 1
    """, (usuario_id,))
    favorito = cursor.fetchone()

    # Evolução geral de carga média por data
    cursor.execute("""
        SELECT ht.data_execucao::date, AVG(he.carga) as media_carga
        FROM historico_treino ht
        JOIN historico_exercicio he ON he.historico_treino_id = ht.id
        WHERE ht.usuario_id = %s
        GROUP BY ht.data_execucao::date
        ORDER BY ht.data_execucao::date ASC
    """, (usuario_id,))
    evolucao = [{"data": str(r[0]), "media_carga": float(r[1])} for r in cursor.fetchall()]

    conn.close()
    return jsonify({
        "total_treinos": total_treinos,
        "por_semana": por_semana,
        "favorito": favorito[0] if favorito else "—",
        "evolucao": evolucao
    })

# ── CATÁLOGO DE EXERCÍCIOS ─────────────────────────
@app.route("/catalogo", methods=["GET"])
def get_catalogo():
    busca = request.args.get('busca', '')
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, grupo_muscular 
        FROM exercicios_catalogo 
        WHERE nome ILIKE %s
        ORDER BY grupo_muscular, nome
    """, (f'%{busca}%',))
    exercicios = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id": e[0], "nome": e[1], "grupo": e[2]} 
        for e in exercicios
    ])

# ── TREINOS DO USUARIO ─────────────────────────────
@app.route("/meus_treinos/<int:usuario_id>", methods=["GET"])
def meus_treinos(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome FROM treinos 
        WHERE usuario_id = %s 
        AND nome NOT ILIKE '%%Treino A%%'
        AND nome NOT ILIKE '%%Treino B%%'
        AND nome NOT ILIKE '%%Treino C%%'
        ORDER BY id DESC
    """, (usuario_id,))
    treinos = cursor.fetchall()
    conn.close()
    return jsonify([{"id": t[0], "nome": t[1]} for t in treinos])

# ── TREINO POR ID ──────────────────────────────────
@app.route("/treinos_por_id/<int:treino_id>", methods=["GET"])
def get_treino_por_id(treino_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM treinos WHERE id = %s", (treino_id,))
    treino = cursor.fetchone()
    nome_treino = treino[0] if treino else ""
    cursor.execute(
        "SELECT nome, series, carga, repeticoes FROM exercicios WHERE treino_id = %s",
        (treino_id,)
    )
    exercicios = cursor.fetchall()
    conn.close()
    return jsonify([
        {"nome": e[0], "series": e[1], "carga": float(e[2]) if e[2] else 0, "repeticoes": e[3], "treino_id": treino_id, "nome_treino": nome_treino}
        for e in exercicios
    ])

@app.route("/treinos/<int:treino_id>", methods=["DELETE"])
def deletar_treino(treino_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exercicios WHERE treino_id = %s", (treino_id,))
    cursor.execute("DELETE FROM treinos WHERE id = %s", (treino_id,))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": True})

if __name__ == "__main__":
    app.run(debug=True)