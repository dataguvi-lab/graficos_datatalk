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
    (CURRENT_DATE - INTERVAL '1 month') AS dia_mes_anterior,
    COALESCE((
        SELECT EXTRACT(HOUR FROM MAX(d.date + d.hora))::int
        FROM inplay.fact_deposits_withdraws_summarized d
        WHERE d.date = CURRENT_DATE AND d.tipo = 'deposit'
    ), 0) AS hora_corte
),
dados_hoje AS (
    SELECT
        EXTRACT(HOUR FROM (d.date + d.hora)) AS hora_numero,
        SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM (d.date + d.hora))) AS acumulado_hoje
    FROM inplay.fact_deposits_withdraws_summarized d, parametros p
    WHERE d.date = p.dia_hoje AND d.tipo = 'deposit'
    GROUP BY 1
),
dados_mes_anterior AS (
    SELECT
        EXTRACT(HOUR FROM (d.date + d.hora)) AS hora_numero,
        SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM (d.date + d.hora))) AS acumulado_mes_anterior
    FROM inplay.fact_deposits_withdraws_summarized d, parametros p
    WHERE d.date = p.dia_mes_anterior AND d.tipo = 'deposit'
    GROUP BY 1
),
fator_projecao AS (
    SELECT
        COALESCE((
            (SELECT acumulado_hoje FROM dados_hoje h, parametros p WHERE h.hora_numero = p.hora_corte)
            /
            NULLIF((SELECT acumulado_mes_anterior FROM dados_mes_anterior s, parametros p WHERE s.hora_numero = p.hora_corte), 0)
        ), 1) AS fator
)
SELECT
    p.dia_hoje + (gs.hora_numero || ' hours')::interval AS hora,
    h.acumulado_hoje AS "AtualDepositoHoje",
    s.acumulado_mes_anterior AS "MaiorDepositoMesAnterior",
    CASE
        WHEN gs.hora_numero > p.hora_corte THEN
            s.acumulado_mes_anterior * (SELECT fator FROM fator_projecao)
        ELSE
            h.acumulado_hoje
    END AS projecao
FROM
    generate_series(0, 23) AS gs(hora_numero)
    LEFT JOIN dados_hoje h ON gs.hora_numero = h.hora_numero
    LEFT JOIN dados_mes_anterior s ON gs.hora_numero = s.hora_numero
    CROSS JOIN parametros p
ORDER BY
    gs.hora_numero"""
