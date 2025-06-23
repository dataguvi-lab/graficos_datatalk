QUERY_GRAFICOS_ZEROUM = """select recepcao_json from mensagens_recepcionadas mr
where id_empresa = 26
and id_mensagem_estrutura = 130
order by mr.recepcao_data desc
limit 1"""

QUERY_GRAFICO_INPASA = """select replace(empresa, 'INPASA ', '') AS empresa, tipo_frete, sum(qtde) as qtde 
from inpasa_boletim_recebimento
where data = current_date - interval '1 day'
group by empresa, tipo_frete
order by empresa"""