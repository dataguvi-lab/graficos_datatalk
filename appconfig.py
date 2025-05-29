QUERY_GRAFICOS_ZEROUM = """select recepcao_json from mensagens_recepcionadas mr
where id_empresa = 26
and id_mensagem_estrutura = 130
order by mr.recepcao_data desc
limit 1"""