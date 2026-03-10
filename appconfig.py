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
        TRUNC(CONVERT_TIMEZONE('America/Sao_Paulo', GETDATE())) AS dia_hoje,
        (TRUNC(CONVERT_TIMEZONE('America/Sao_Paulo', GETDATE())) - INTERVAL '1 month')::DATE AS dia_mes_anterior
),
hora_corte_calc AS (
    SELECT COALESCE((
        SELECT EXTRACT(HOUR FROM MAX((d.date || ' ' || d.hora)::timestamp))::int
        FROM inplay.fact_deposits_withdraws_summarized d
        CROSS JOIN parametros p
        WHERE d.date = p.dia_hoje AND d.tipo = 'deposit'
    ), 0) AS hora_corte
),
dados_hoje AS (
    SELECT
        EXTRACT(HOUR FROM (d.date || ' ' || d.hora)::timestamp) AS hora_numero,
        SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM (d.date || ' ' || d.hora)::timestamp) ROWS UNBOUNDED PRECEDING) AS acumulado_hoje
    FROM inplay.fact_deposits_withdraws_summarized d
    CROSS JOIN parametros p
    WHERE d.date = p.dia_hoje AND d.tipo = 'deposit'
    GROUP BY 1
),
dados_mes_anterior AS (
    SELECT
        EXTRACT(HOUR FROM (d.date || ' ' || d.hora)::timestamp) AS hora_numero,
        SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM (d.date || ' ' || d.hora)::timestamp) ROWS UNBOUNDED PRECEDING) AS acumulado_mes_anterior
    FROM inplay.fact_deposits_withdraws_summarized d
    CROSS JOIN parametros p
    WHERE d.date = p.dia_mes_anterior AND d.tipo = 'deposit'
    GROUP BY 1
),
fator_projecao AS (
    SELECT
        COALESCE((
            (SELECT MAX(acumulado_hoje) FROM dados_hoje CROSS JOIN hora_corte_calc hc WHERE hora_numero = hc.hora_corte)
            /
            NULLIF((SELECT MAX(acumulado_mes_anterior) FROM dados_mes_anterior CROSS JOIN hora_corte_calc hc WHERE hora_numero = hc.hora_corte), 0)
        ), 1) AS fator
),
horas_gs AS (
    SELECT 0 AS hora_numero UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
    SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL
    SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL
    SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL
    SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL
    SELECT 20 UNION ALL SELECT 21 UNION ALL SELECT 22 UNION ALL SELECT 23
)
SELECT
    DATEADD(hour, gs.hora_numero, p.dia_hoje::timestamp) AS hora,
    h.acumulado_hoje AS "AtualDepositoHoje",
    s.acumulado_mes_anterior AS "MaiorDepositoMesAnterior",
    CASE
        WHEN gs.hora_numero > hc.hora_corte THEN
            s.acumulado_mes_anterior * fp.fator
        ELSE
            h.acumulado_hoje
    END AS projecao
FROM
    horas_gs gs
    LEFT JOIN dados_hoje h ON gs.hora_numero = h.hora_numero
    LEFT JOIN dados_mes_anterior s ON gs.hora_numero = s.hora_numero
    CROSS JOIN parametros p
    CROSS JOIN hora_corte_calc hc
    CROSS JOIN fator_projecao fp
ORDER BY
    gs.hora_numero"""

QUERY_PROJECAO_ENERGIA = """WITH
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