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
        -- Usa CURRENT_TIMESTAMP para garantir o fuso e converte direto para DATE
        (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')::DATE AS dia_hoje,
        DATEADD(month, -1, (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')::DATE)::DATE AS dia_mes_anterior
),
hora_corte_calc AS (
    SELECT COALESCE((
        -- Extrai a hora direto do campo hora, sem concatenar com a data
        SELECT MAX(EXTRACT(HOUR FROM d.hora::time))::int
        FROM inplay.fact_deposits_withdraws_summarized d
        CROSS JOIN parametros p
        WHERE d.date = p.dia_hoje AND d.tipo = 'deposit'
          -- Descartar a hora atual pois os dados ainda não fecharam (evita queda na curva de projeção)
          AND EXTRACT(HOUR FROM d.hora::time) < EXTRACT(HOUR FROM CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
    ), -1) AS hora_corte
),
dados_hoje AS (
    SELECT
        EXTRACT(HOUR FROM d.hora::time) AS hora_numero,
        SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM d.hora::time) ROWS UNBOUNDED PRECEDING) AS acumulado_hoje
    FROM inplay.fact_deposits_withdraws_summarized d
    CROSS JOIN parametros p
    WHERE d.date = p.dia_hoje AND d.tipo = 'deposit'
    GROUP BY 1
),
dados_mes_anterior AS (
    SELECT
        EXTRACT(HOUR FROM d.hora::time) AS hora_numero,
        SUM(SUM(d.amount)) OVER (ORDER BY EXTRACT(HOUR FROM d.hora::time) ROWS UNBOUNDED PRECEDING) AS acumulado_mes_anterior
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
    
    -- Formatando opcionalmente os campos principais para 2 casas decimais, caso necessário
    CAST(h.acumulado_hoje AS DECIMAL(18,2)) AS "AtualDepositoHoje",
    CAST(s.acumulado_mes_anterior AS DECIMAL(18,2)) AS "MaiorDepositoMesAnterior",
    
    CAST(CASE
        WHEN gs.hora_numero > hc.hora_corte THEN
            s.acumulado_mes_anterior * fp.fator
        ELSE
            h.acumulado_hoje
    END AS DECIMAL(18,2)) AS projecao
    
FROM
    horas_gs gs
    LEFT JOIN dados_hoje h ON gs.hora_numero = h.hora_numero
    LEFT JOIN dados_mes_anterior s ON gs.hora_numero = s.hora_numero
    CROSS JOIN parametros p
    CROSS JOIN hora_corte_calc hc
    CROSS JOIN fator_projecao fp
ORDER BY
    gs.hora_numero"""
