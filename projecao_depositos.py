import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import psycopg2 # ou o conector do seu banco de dados
from io import StringIO
import numpy as np
from scipy.interpolate import make_interp_spline
from datetime import datetime, timedelta
from wrapper import DataWrapper
from git import Repo
from zoneinfo import ZoneInfo

# --- Configurações Visuais do Gráfico ---
COR_SEMANA_PASSADA = '#495057'
COR_HOJE_REALIZADO = '#d81d29'
COR_PROJECAO = '#d81d29'
COR_PREENCHIMENTO = '#EFBDBE'

def get_spline_smooth(x_series, y_series):
    """
    Helper function to generate smooth curve data using spline interpolation.
    It filters out NaN values before calculation.
    """
    valid_indices = ~y_series.isna()
    x_valid = x_series[valid_indices]
    y_valid = y_series[valid_indices]
    
    if len(x_valid) < 4:
        return x_valid, y_valid 
    
    spline = make_interp_spline(x_valid, y_valid, k=3) 
    x_smooth = np.linspace(x_valid.min(), x_valid.max(), 300)
    y_smooth = spline(x_smooth)
    
    return x_smooth, y_smooth

def criar_grafico_projecao():
    df = DataWrapper.get_projecao_deposito()
        
    df['hora_numero'] = pd.to_datetime(df['hora']).dt.hour

    df['hora_plot'] = df['hora_numero'].apply(lambda h: h+1)
    
    try:
        # A primeira hora em que os dados reais são diferentes da projeção SQL
        # Utiliza-se fillna(-1) para evitar comportamento inesperado ao comparar NaNs com floats
        df_projetado = df[~np.isclose(df['projecao'].fillna(-1), df['AtualDepositoHoje'].fillna(-1))]
        if not df_projetado.empty:
            primeira_hora_projetada = df_projetado['hora_numero'].min()
            hora_corte = int(primeira_hora_projetada) - 1
            print(f"Ponto de corte detectado pelo DB: Hora {hora_corte}")
        else:
            tz_sp = ZoneInfo("America/Sao_Paulo")
            agora = datetime.now(tz=tz_sp)
            hora_corte = (agora - timedelta(hours=1)).hour
            print(f"Ponto de corte detectado (fallback manual): Hora {hora_corte}")
    except Exception as e:
        hora_corte = 24
        print(f"Nenhuma projeção detectada ({e}). Exibindo dados completos.")

    df['realizado_hoje'] = df.apply(lambda row: row['AtualDepositoHoje'] if row['hora_numero'] <= hora_corte else np.nan, axis=1)
    print(df)
    df['linha_projecao'] = df.apply(lambda row: row['projecao'] if row['hora_numero'] >= hora_corte else np.nan, axis=1)
    df.loc[df['hora_numero'] == hora_corte, 'linha_projecao'] = df.loc[df['hora_numero'] == hora_corte, 'realizado_hoje']

    # --- Etapa 3: Criação do Gráfico ---
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 9))
    
    x_smooth_semana, y_smooth_semana = get_spline_smooth(df['hora_plot'], df['MaiorDepositoMesAnterior'])
    x_smooth_hoje, y_smooth_hoje = get_spline_smooth(df['hora_plot'], df['realizado_hoje'])
    x_smooth_proj, y_smooth_proj = get_spline_smooth(df['hora_plot'], df['linha_projecao'])

    ax.plot(x_smooth_semana, y_smooth_semana, color=COR_SEMANA_PASSADA, linewidth=2.5)
    ax.plot(x_smooth_hoje, y_smooth_hoje, color=COR_HOJE_REALIZADO, linewidth=2.5)
    ax.plot(x_smooth_proj, y_smooth_proj, color=COR_PROJECAO, linewidth=2.5, linestyle='--')
    
    ax.scatter(df['hora_plot'], df['MaiorDepositoMesAnterior'], color=COR_SEMANA_PASSADA, s=20, zorder=10)
    ax.scatter(df['hora_plot'], df['realizado_hoje'], color=COR_HOJE_REALIZADO, s=20, zorder=10)
    
    ax.fill_between(x_smooth_hoje, y_smooth_hoje, color=COR_PREENCHIMENTO, alpha=0.5)

    dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    tz_sp = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz=tz_sp)
    indice = agora.weekday()
    horario_atual = agora.strftime('%d/%m/%Y %H:%M:%S')

    # --- Formatação e Títulos ---
    fig.suptitle(f'Projeção dos depósitos ao longo do dia ({dias_semana[indice]})', fontsize=20, fontweight='bold', ha='center')
    ax.set_title(f"Comparativo hoje vs mesmo dia mês anterior | Última atualização: {horario_atual}", fontsize=14, pad=10, color='grey', loc='center')
    
    ax.set_xlabel('Hora do dia', fontsize=12, labelpad=10)
    ax.set_ylabel('Valor Acumulado (R$)', fontsize=12, labelpad=10)
    
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'R$ {x/1e6:.1f} Mi'))
    ax.set_xticks(range(1, 25))
    ax.set_xlim(0.5, 24.5)

    
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('lightgrey')
    ax.tick_params(colors='grey')
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='lightgrey')

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=COR_SEMANA_PASSADA, lw=2.5, marker='o', label='Semana Passada'),
        Line2D([0], [0], color=COR_HOJE_REALIZADO, lw=2.5, marker='o', label='Hoje'),
        Line2D([0], [0], color=COR_PROJECAO, lw=2.5, linestyle='--', label='Projeção')
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=False, fontsize=12, bbox_to_anchor=(0.01, 0.99))
    
    fig.tight_layout(rect=[0, 0, 1, 0.96]) 
    
    plt.savefig('grafico_projecao_deposito.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # Caminho onde o repositório está clonado
    import os
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    # Bloco do Git
    try:
        repo = Repo(repo_dir)
        repo.git.add('grafico_projecao_deposito.png')
        
        # Só faz o commit se houver mudanças
        if repo.is_dirty(untracked_files=True):
            commit_msg = f'Atualização gráfico de projeção depósito ZEROUM - {horario_atual}'
            repo.index.commit(commit_msg)
            origin = repo.remote(name='origin')
            origin.push()
            print(f"Arquivo enviado para o GitHub com sucesso! ({horario_atual})")
        else:
            print("Nenhuma alteração detectada no gráfico. Ignorando commit.")
    except Exception as e:
        print(f"Erro ao enviar para o GitHub: {e}")

    print('✅ Gráfico com design minimalista gerado e salvo com sucesso!')

if __name__ == '__main__':
    criar_grafico_projecao()
