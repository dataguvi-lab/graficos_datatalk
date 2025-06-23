import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wrapper import DataWrapper
from git import Repo

# Obter os dados do boletim da Inpasa
df = DataWrapper.get_boletim_inpasa()

# Definir o estilo
sns.set(style="whitegrid")

# Criar figura
plt.figure(figsize=(10, 6))

# Criar o gráfico
ax = sns.barplot(data=df, x='empresa', y='qtde', hue='tipo_frete', palette='Set2')

# Adicionar rótulos sobre as barras
for container in ax.containers:
    ax.bar_label(container, fmt='%d', label_type='edge', padding=3, fontsize=9, color='black')

# Remover título do eixo X
plt.xlabel('')

# Configurar rótulos e título
plt.ylabel('Quantidade')
plt.title('Quantidade por Empresa e Tipo de Frete')

# Ajustar rótulos do eixo X
plt.xticks(rotation=0, ha='right')

# Legenda
plt.legend(title='Tipo de Frete')

# Ajustar layout
plt.tight_layout()

# Salvar o gráfico
plt.savefig('grafico_quantidade_por_empresa.png')

# Caminho onde o repositório está clonado
repo_dir = r'C:\\home\\ubuntu\\repositorios\\graficos_datatalk'  # <=== altere aqui

# === 2. Git: adicionar, commit e push ===
try:
    repo = Repo(repo_dir)
    repo.git.add('grafico_quantidade_por_empresa.png')
    repo.index.commit('Adicionando gráfico gerado automaticamente')
    origin = repo.remote(name='origin')
    origin.push()
    print("Arquivo enviado para o GitHub com sucesso!")
except Exception as e:
    print(f"Erro ao enviar para o GitHub: {e}")

print('✅ Gráficos gerados e salvos com sucesso!')