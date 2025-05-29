import matplotlib.pyplot as plt
import os
from git import Repo

# === 1. Gerar e salvar o gráfico ===
plt.figure(figsize=(6,4))
x = [1, 2, 4, 6, 8]
y = [14, 25, 10, 12, 30]
plt.plot(x, y, marker='o')
plt.title('Exemplo de Gráfico')
plt.xlabel('Eixo X')
plt.ylabel('Eixo Y')
plt.grid()

# Caminho onde o repositório está clonado
repo_dir = r'/home/ubuntu/repositorios/guvvv'  # <=== altere aqui

# Caminho do arquivo dentro do repo
image_path = os.path.join(repo_dir, 'mectrol.jpg')
plt.savefig(image_path)
plt.close()
print(f"Gráfico salvo em {image_path}")

# === 2. Git: adicionar, commit e push ===
try:
    repo = Repo(repo_dir)
    repo.git.add('mectrol.jpg')
    repo.index.commit('Adicionando gráfico gerado automaticamente')
    origin = repo.remote(name='origin')
    origin.push()
    print("Arquivo enviado para o GitHub com sucesso!")
except Exception as e:
    print(f"Erro ao enviar para o GitHub: {e}")
