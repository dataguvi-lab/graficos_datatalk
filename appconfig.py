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

QUERY_PROJECAO_ZEROUM = """WITH
    parametros AS (
        SELECT
            CURRENT_DATE AS dia_hoje,
            (CURRENT_DATE - INTERVAL '7 day') AS dia_semana_anterior,
            -- Encontra a última hora com dados de depósito para hoje na tabela
            (SELECT EXTRACT(HOUR FROM MAX(d.date + d.hora))::int
             FROM inplay.fact_deposits_withdraws_summarized d
             WHERE d.date = CURRENT_DATE AND d.tipo = 'deposit'
            ) AS hora_corte
    ),
    dados_hoje AS (
        SELECT
            EXTRACT(HOUR FROM (d.date + d.hora)) as hora_numero,
            SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM (d.date + d.hora))) AS acumulado_hoje
        FROM inplay.fact_deposits_withdraws_summarized d, parametros p
        WHERE d.date = p.dia_hoje AND d.tipo = 'deposit'
        GROUP BY 1
    ),
    dados_semana_anterior AS (
        SELECT
            EXTRACT(HOUR FROM (d.date + d.hora)) as hora_numero,
            SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM (d.date + d.hora))) AS acumulado_semana_anterior
        FROM inplay.fact_deposits_withdraws_summarized d, parametros p
        WHERE d.date = p.dia_semana_anterior AND d.tipo = 'deposit'
        GROUP BY 1
    ),
    fator_projecao AS (
        SELECT
            (SELECT acumulado_hoje FROM dados_hoje h, parametros p WHERE h.hora_numero = p.hora_corte)
            /
            NULLIF((SELECT acumulado_semana_anterior FROM dados_semana_anterior s, parametros p WHERE s.hora_numero = p.hora_corte), 0)
            AS fator
    )
    SELECT
        p.dia_hoje + (gs.hora_numero || ' hours')::interval AS hora,
        COALESCE(h.acumulado_hoje, (SELECT MAX(acumulado_hoje) FROM dados_hoje)) AS "AtualDepositoHoje",
        s.acumulado_semana_anterior AS "MaiorDeposito7DiasAtras",
        CASE
            WHEN gs.hora_numero > p.hora_corte
            THEN s.acumulado_semana_anterior * (SELECT fator FROM fator_projecao)
            ELSE h.acumulado_hoje
        END AS projecao
    FROM
        generate_series(0, 23) as gs(hora_numero)
        LEFT JOIN dados_hoje h ON gs.hora_numero = h.hora_numero
        LEFT JOIN dados_semana_anterior s ON gs.hora_numero = s.hora_numero
        CROSS JOIN parametros p
    ORDER BY
        gs.hora_numero"""