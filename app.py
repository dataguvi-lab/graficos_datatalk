import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from git import Repo
import os
import ast
import json
from wrapper import DataWrapper


df = DataWrapper.get_reports_notifications()

# Função para converter string em dicionário estruturado
def processar_json_string(s):
    s = s.replace("\r\n", "").replace("\n", "").strip()
    dicionario = json.loads(s)

    # Separar as strings internas em listas de strings
    for chave in dicionario:
        dicionario[chave] = dicionario[chave][0].replace("'", "").split(", ")

    return dicionario

# Aplicar no dataframe
df['dicionario'] = df['recepcao_json'].apply(processar_json_string)

# # Dados do JSON
data = df['dicionario'][0]

# print(data)

# Conversão dos dados
datas = [d.strip().replace("'", "") for d in data["data"][0].split(",")]

depositos = [
    float(v.strip().replace("'", ""))
    for v in data["deposito"][0].split(",")]

saques = [
    float(v.strip().replace("'", ""))
    for v in data["saque"][0].split(",")]


# Criar DataFrame
df = pd.DataFrame(data)

df['data'] = pd.to_datetime(df['data'])
df['deposito'] = pd.to_numeric(df['deposito'], errors='coerce')
df['saque'] = pd.to_numeric(df['saque'], errors='coerce')

# ✅ Criar coluna do dia da semana (em português)
mapa_dias = {
    'Monday': 'Segunda',
    'Tuesday': 'Terça',
    'Wednesday': 'Quarta',
    'Thursday': 'Quinta',
    'Friday': 'Sexta',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}
df['dia_semana'] = df['data'].dt.day_name().map(mapa_dias)

# ✅ Ordenar os dias da semana corretamente no eixo X
ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=ordem_dias, ordered=True)

# ✅ Adicionar coluna de semana
df['semana'] = df['data'].dt.isocalendar().week
semana_atual = df['semana'].max()
semana_passada = semana_atual - 1

# ================================
# 📊 Gráfico de Depósitos
# ================================
plt.figure(figsize=(10,6))
sns.lineplot(
    data=df[df['semana']==semana_passada],
    x='dia_semana', y='deposito', label='Semana Passada', marker='o'
)
sns.lineplot(
    data=df[df['semana']==semana_atual],
    x='dia_semana', y='deposito', label='Semana Atual', marker='o'
)
plt.title('Comparativo de Depósitos')
plt.xlabel('Dia da Semana')
plt.ylabel('Valor (R$)')
plt.xticks(rotation=45)
plt.grid(visible=True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('grafico_depositos.png', dpi=300)
plt.close()

# ================================
# 📉 Gráfico de Saques
# ================================
plt.figure(figsize=(10,6))
sns.lineplot(
    data=df[df['semana']==semana_passada],
    x='dia_semana', y='saque', label='Semana Passada', marker='o'
)
sns.lineplot(
    data=df[df['semana']==semana_atual],
    x='dia_semana', y='saque', label='Semana Atual', marker='o'
)
plt.title('Comparativo de Saques')
plt.xlabel('Dia da Semana')
plt.ylabel('Valor (R$)')
plt.xticks(rotation=45)
plt.grid(visible=True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('grafico_saques.png', dpi=300)
plt.close()

# ===============================
# 📉 Gráfico de Saques
# ===============================
plt.figure(figsize=(10,6))
sns.lineplot(
    data=df[df['semana']==semana_passada],
    x='dia_semana', y='saque', label='Semana Passada', marker='o'
)
sns.lineplot(
    data=df[df['semana']==semana_atual],
    x='dia_semana', y='saque', label='Semana Atual', marker='o'
)
plt.title('Comparativo de Saques')
plt.xlabel('Dia da Semana')
plt.ylabel('Valor (R$)')
plt.xticks(rotation=45)
plt.grid(visible=True, linestyle='--', alpha=0.5)
plt.legend()

# Salvar
plt.tight_layout()
plt.savefig('grafico_saques.png', dpi=300)
plt.close()


# Caminho onde o repositório está clonado
repo_dir = '/home/ubuntu/repositorios/graficos_datatalk'  # <=== altere aqui

# === 2. Git: adicionar, commit e push ===
try:
    repo = Repo(repo_dir)
    repo.git.add(['grafico_saques.png', 'grafico_depositos.png'])
    repo.index.commit('Adicionando gráfico gerado automaticamente')
    origin = repo.remote(name='origin')
    origin.push()
    print("Arquivo enviado para o GitHub com sucesso!")
except Exception as e:
    print(f"Erro ao enviar para o GitHub: {e}")

print('✅ Gráficos gerados e salvos com sucesso!')
