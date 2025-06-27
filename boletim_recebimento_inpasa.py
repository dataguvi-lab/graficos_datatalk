import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from wrapper import DataWrapper # Supondo que este wrapper exista e funcione
from git import Repo

# --- CONFIGURAÇÕES DE ESTILO E FONTE ---
# Para um visual mais profissional, vamos tentar usar a fonte "Inter".
# Se não estiver instalada, o matplotlib usará uma fonte padrão.
font_path = fm.findfont("Inter", fallback_to_default=True)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.color'] = '#333333'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['xtick.color'] = '#666666'
plt.rcParams['ytick.color'] = '#666666'

# Define um estilo base limpo.
sns.set_style("white")

# --- DADOS ---
# Como não tenho acesso ao DataWrapper, vou criar um DataFrame de exemplo.
df = DataWrapper.get_boletim_inpasa()

# --- CRIAÇÃO DO GRÁFICO ---
# Criar a figura e os eixos com um tamanho ligeiramente maior para mais respiro.
fig, ax = plt.subplots(figsize=(14, 8))

# Paleta de cores moderna e sofisticada.
custom_palette = ["#1D4E56", "#E67A5B"] # Verde escuro e Laranja queimado

# Criar o gráfico de barras
sns.barplot(data=df, x='empresa', y='qtde', hue='tipo_frete', palette=custom_palette, ax=ax, saturation=1)

# --- APRIMORAMENTOS E RÓTULOS ---
# Adicionar rótulos sobre as barras
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%d',
        label_type='edge',
        padding=5,
        fontsize=10,
        color='#333333',
        fontweight='semibold'
    )

# --- TÍTULOS E EIXOS ---
# Remove todos os rótulos dos eixos, o título explicará tudo.
ax.set_ylabel('')
ax.set_xlabel('')
ax.set_facecolor('white')

# Adicionar um título e um subtítulo, com espaço para a legenda entre eles.
fig.text(0.5, 0.95, 'Quantidade por Empresa e Tipo de Frete', fontsize=20, fontweight='bold', ha='center')
#fig.text(0.08, 0.92, 'Comparativo entre os tipos de frete CIF e FOB', fontsize=14, fontweight='normal', ha='left', color='#666666')

# --- LIMPEZA E MINIMALISMO ---
# Remove todas as bordas (spines)
sns.despine(left=True, bottom=True, right=True, top=True)

# Adicionar uma grade horizontal muito sutil
ax.grid(axis='y', linestyle=':', linewidth=0.8, color='#CCCCCC', alpha=0.7)

# Limpar os ticks dos eixos (marcas de medida)
ax.tick_params(axis='x', length=0)
ax.tick_params(axis='y', length=0)

# Ajustar rótulos do eixo X
plt.xticks(rotation=0, ha='center', fontsize=11, fontweight='bold')
ax.tick_params(axis='y', labelsize=11)

# Legenda movida para o centro superior, acima do gráfico, para não sobrepor os dados.
ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, 1.01), # Posiciona a base da legenda acima do eixo do gráfico
    ncol=2,
    frameon=False,
    fontsize=12,
    handlelength=1.5,
    handletextpad=0.8
)

# Ajuste fino para garantir que nada seja cortado
plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.9]) # Ajusta para garantir que o título e legenda não sejam cortados

plt.savefig('/home/ubuntu/repositorios/graficos_datatalk/grafico_quantidade_por_empresa.png', dpi=300, bbox_inches='tight', facecolor='white')

# Caminho onde o repositório está clonado
repo_dir = '/home/ubuntu/repositorios/graficos_datatalk'  # <=== altere aqui

# Bloco do Git (mantido como no original)
try:
    # Descomente as linhas abaixo para usar o Git
    repo = Repo(repo_dir)
    repo.git.add('grafico_quantidade_por_empresa.png')
    repo.index.commit('Atualização Gráfico Recebimento INPASA')
    origin = repo.remote(name='origin')
    origin.push()
    print("Arquivo enviado para o GitHub com sucesso!")
except Exception as e:
    print(f"Erro ao enviar para o GitHub: {e}")

print('✅ Gráfico com design minimalista gerado e salvo com sucesso!')

# Para exibir o gráfico no ambiente de script/notebook
#plt.show()
