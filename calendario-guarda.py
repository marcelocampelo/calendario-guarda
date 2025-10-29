from datetime import datetime, timedelta
from ics import Calendar, Event
import holidays

def calcular_pascoa(ano):
    """Calcula a data da Páscoa usando o algoritmo de Meeus"""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(ano, mes, dia)

def calcular_corpus_christi(ano):
    """Corpus Christi é 60 dias após a Páscoa"""
    pascoa = calcular_pascoa(ano)
    return pascoa + timedelta(days=60)

def calcular_carnaval(ano):
    """Carnaval é 47 dias antes da Páscoa"""
    pascoa = calcular_pascoa(ano)
    return pascoa - timedelta(days=47)

def calcular_semana_santa(ano):
    """Semana Santa começa no Domingo de Ramos (7 dias antes da Páscoa)"""
    pascoa = calcular_pascoa(ano)
    domingo_ramos = pascoa - timedelta(days=7)
    return [domingo_ramos + timedelta(days=i) for i in range(8)]  # 8 dias incluindo Páscoa

def calcular_ferias_meio_ano(ano):
    """Calcula o período de férias do meio do ano"""
    # Verifica a segunda-feira da última semana de junho
    ultima_seg_junho = None
    for dia in range(30, 26, -1):
        data = datetime(ano, 6, dia)
        if data.weekday() == 0:  # Segunda-feira
            ultima_seg_junho = data
            break
    
    if ultima_seg_junho and ultima_seg_junho.day in [27, 28, 29, 30]:
        inicio = ultima_seg_junho
    else:
        # Primeira segunda-feira de julho
        for dia in range(1, 8):
            data = datetime(ano, 7, dia)
            if data.weekday() == 0:
                inicio = data
                break
    
    fim = inicio + timedelta(days=29)  # 30 dias incluindo o primeiro
    return inicio, fim

def calcular_ferias_final_ano(ano):
    """Calcula o período de férias do final do ano"""
    # Primeira segunda-feira após pelo menos 12 dias de dezembro
    inicio = None
    for dia in range(13, 32):
        try:
            data = datetime(ano, 12, dia)
            if data.weekday() == 0:
                inicio = data
                break
        except ValueError:
            continue
    
    # Se não encontrou em dezembro, pega a primeira segunda de janeiro
    if not inicio:
        inicio = datetime(ano + 1, 1, 1)
        while inicio.weekday() != 0:
            inicio += timedelta(days=1)
    
    # Terceiro domingo de janeiro do ano seguinte
    janeiro_seguinte = ano + 1
    domingos = []
    for dia in range(1, 32):
        try:
            data = datetime(janeiro_seguinte, 1, dia)
            if data.weekday() == 6:
                domingos.append(data)
        except ValueError:
            break
    
    fim = domingos[2] if len(domingos) >= 3 else domingos[-1]
    return inicio, fim

def calcular_dia_pais(ano):
    """Segundo domingo de agosto"""
    domingos = []
    for dia in range(1, 32):
        data = datetime(ano, 8, dia)
        if data.weekday() == 6:
            domingos.append(data)
    return domingos[1]

def calcular_dia_maes(ano):
    """Segundo domingo de maio"""
    domingos = []
    for dia in range(1, 32):
        data = datetime(ano, 5, dia)
        if data.weekday() == 6:
            domingos.append(data)
    return domingos[1]

def gerar_calendario(ano_inicio, ano_fim):
    """Gera o calendário de guarda para o período especificado"""
    
    # Dicionário para armazenar prioridades por data
    prioridades = {}  # {data: [(prioridade, 'pai'/'mae', 'motivo')]}
    
    for ano in range(ano_inicio, ano_fim + 1):
        ano_impar = ano % 2 == 1
        
        # === FERIADOS GRANDES E ANIVERSÁRIO (Prioridade 0) ===
        # Natal (24 e 25 de dezembro)
        natal_pai = ano_impar
        for dia in [24, 25]:
            data = datetime(ano, 12, dia)
            responsavel = 'pai' if natal_pai else 'mae'
            prioridades.setdefault(data.date(), []).append((0, responsavel, 'Natal'))
        
        # Ano Novo (31 de dezembro e 1 de janeiro)
        ano_novo_mae = ano_impar
        data_31 = datetime(ano, 12, 31)
        prioridades.setdefault(data_31.date(), []).append((0, 'mae' if ano_novo_mae else 'pai', 'Ano Novo'))
        data_01 = datetime(ano + 1, 1, 1)
        prioridades.setdefault(data_01.date(), []).append((0, 'mae' if ano_novo_mae else 'pai', 'Ano Novo'))
        
        # Semana Santa e Páscoa
        semana_santa = calcular_semana_santa(ano)
        pascoa_pai = ano_impar
        for data in semana_santa:
            responsavel = 'pai' if pascoa_pai else 'mae'
            prioridades.setdefault(data.date(), []).append((0, responsavel, 'Semana Santa/Páscoa'))
        
        # Carnaval
        carnaval = calcular_carnaval(ano)
        carnaval_mae = ano_impar
        for i in range(-1, 2):  # Sábado, domingo, segunda
            data = carnaval + timedelta(days=i)
            responsavel = 'mae' if carnaval_mae else 'pai'
            prioridades.setdefault(data.date(), []).append((0, responsavel, 'Carnaval'))
        
        # Aniversário Letícia (06 de julho)
        data_aniv = datetime(ano, 7, 6)
        aniv_mae = ano_impar
        prioridades.setdefault(data_aniv.date(), []).append((0, 'mae' if aniv_mae else 'pai', 'Aniversário Letícia'))
        
        # === DIAS FIXOS (Prioridade 0) ===
        dias_fixos = [
            (datetime(ano, 1, 14), 'pai', 'Aniversário Vovó Sônia'),
            (datetime(ano, 6, 12), 'pai', 'Aniversário Vovô Joca'),
            (datetime(ano, 6, 1), 'pai', 'Aniversário Tia Ana'),
            (datetime(ano, 11, 3), 'pai', 'Aniversário do Pai'),
            (datetime(ano, 2, 14), 'mae', 'Aniversário Tia Ié'),
            (datetime(ano, 4, 16), 'mae', 'Aniversário Vovó Dudu'),
            (datetime(ano, 9, 25), 'mae', 'Aniversário Vovô Lulu'),
            (datetime(ano, 12, 31), 'mae', 'Aniversário Bisa Orquídea'),
            (datetime(ano, 12, 25), 'mae', 'Aniversário Tio Filipe'),
            (datetime(ano, 1, 20), 'mae', 'Aniversário da Mãe')
            
        ]
        
        for data, responsavel, motivo in dias_fixos:
            prioridades.setdefault(data.date(), []).append((0, responsavel, motivo))
        
        # Dia dos Pais e Dia das Mães
        dia_pais = calcular_dia_pais(ano)
        prioridades.setdefault(dia_pais.date(), []).append((0, 'pai', 'Dia dos Pais'))
        
        dia_maes = calcular_dia_maes(ano)
        prioridades.setdefault(dia_maes.date(), []).append((0, 'mae', 'Dia das Mães'))
        
        # === FÉRIAS MEIO DE ANO (Prioridade 1) ===
        inicio_ferias, fim_ferias = calcular_ferias_meio_ano(ano)
        primeiro_pai = not ano_impar  # Anos pares começa com pai
        
        dias_ferias = (fim_ferias - inicio_ferias).days + 1
        data_atual = inicio_ferias
        periodos = [(5, 'pai' if primeiro_pai else 'mae'),
                    (10, 'mae' if primeiro_pai else 'pai'),
                    (5, 'pai' if primeiro_pai else 'mae'),
                    (10, 'mae' if primeiro_pai else 'pai')]
        
        for duracao, responsavel in periodos:
            for _ in range(duracao):
                if data_atual <= fim_ferias:
                    prioridades.setdefault(data_atual.date(), []).append((1, responsavel, 'Férias Medianas'))
                    data_atual += timedelta(days=1)
        
        # === FÉRIAS FINAL DE ANO (Prioridade 1) ===
        inicio_ferias_fim, fim_ferias_fim = calcular_ferias_final_ano(ano)
        primeiro_pai_fim = ano_impar  # Anos ímpares começa com pai
        
        data_atual = inicio_ferias_fim
        contador = 0
        responsavel_atual = 'pai' if primeiro_pai_fim else 'mae'
        
        while data_atual <= fim_ferias_fim:
            prioridades.setdefault(data_atual.date(), []).append((1, responsavel_atual, 'Férias de Ano Novo'))
            contador += 1
            if contador == 7:
                responsavel_atual = 'mae' if responsavel_atual == 'pai' else 'pai'
                contador = 0
            data_atual += timedelta(days=1)
        
        # === FERIADOS COMUNS (Prioridade 2) ===
        feriados_comuns = [
            (datetime(ano, 5, 1), 'Dia do Trabalho'),
            (calcular_corpus_christi(ano), 'Corpus Christi'),
            (datetime(ano, 8, 16), 'Aniversário de Teresina'),
            (datetime(ano, 9, 7), 'Independência do Brasil'),
            (datetime(ano, 10, 12), 'Dia das Crianças'),
            (datetime(ano, 10, 15), 'Dia do Professor'),
            (datetime(ano, 10, 19), 'Aniversário do Piauí'),
            (datetime(ano, 4, 21), 'Tiradentes'),
            (datetime(ano, 11, 2), 'Finados'),
            (datetime(ano, 12, 8), 'Nossa Senhora da Conceição'),
            (datetime(ano, 11, 20), 'Consciência Negra')
        ]
        
        # Alternar feriados
        for idx, (data, nome) in enumerate(feriados_comuns):
            responsavel = 'pai' if (idx + ano) % 2 == 0 else 'mae'
            prioridades.setdefault(data.date(), []).append((2, responsavel, f'Feriado: {nome}'))
        
        # === FINAIS DE SEMANA (Prioridade 3) ===
        primeiro_fds_pai = ano_impar
        data_atual = datetime(ano, 1, 1)
        
        # Encontra a primeira sexta-feira do ano
        while data_atual.weekday() != 4:  # 4 = sexta
            data_atual += timedelta(days=1)
        
        # Se ano par, começa com mãe, então pula o primeiro fim de semana
        if not primeiro_fds_pai:
            data_atual += timedelta(days=7)
        
        responsavel_fds = 'pai' if primeiro_fds_pai else 'mae'
        
        while data_atual.year == ano:
            # Sexta, sábado, domingo
            for i in range(3):
                data = data_atual + timedelta(days=i)
                if data.year == ano:
                    prioridades.setdefault(data.date(), []).append((3, responsavel_fds, 'FDS'))
            
            data_atual += timedelta(days=7)
            responsavel_fds = 'mae' if responsavel_fds == 'pai' else 'pai'
    
    # === DECIDIR CADA DIA E CRIAR EVENTOS ===
    cal = Calendar()
    cal.creator = 'Calendário Guarda Letícia'
    
    data_inicio = datetime(ano_inicio, 1, 1)
    data_fim = datetime(ano_fim, 12, 31)
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        dia = data_atual.date()
        
        # Determinar responsável baseado em prioridades
        if dia in prioridades:
            # Ordena por prioridade (menor número = mais forte)
            prioridades[dia].sort(key=lambda x: x[0])
            prioridade_min, responsavel, motivo = prioridades[dia][0]
        else:
            # Dia normal (Prioridade 4) = mãe
            """responsavel = 'Sem Prioridade'
            motivo = 'Dia Normal'"""
            prioridade_min = 4
        
        # Criar evento de dia inteiro
        if prioridade_min <= 3:
            evento = Event()
            evento.name = f'Letícia - {responsavel.capitalize()}'
            evento.begin = dia
            evento.make_all_day()
            evento.transparent = True  # Não bloqueia agenda
            
            # Definir cor (não suportado nativamente em .ics, mas adicionamos como propriedade)
            # Azul para pai, preto para mãe
            cor = 'BLUE' if responsavel == 'pai' else 'BLACK'
            
            cal.events.add(evento)
        
        # Se prioridade <= 3, criar evento ao meio-dia explicando o motivo
        if prioridade_min <= 3:
            evento_motivo = Event()
            evento_motivo.name = f'Pq? {motivo}'
            evento_motivo.begin = datetime.combine(dia, datetime.min.time().replace(hour=12))
            evento_motivo.duration = timedelta(hours=0)
            cal.events.add(evento_motivo)
        
        data_atual += timedelta(days=1)
    
    # Salvar arquivo
    nome_arquivo = f'leticia_guarda_{ano_inicio}_{ano_fim}.ics'
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(str(cal))
    
    print(f'Calendário gerado: {nome_arquivo}')
    print(f'Período: {ano_inicio} a {ano_fim}')
    print(f'Total de eventos: {len(cal.events)}')
    print('\nImporte este arquivo no Google Calendar.')
    print('Após importar, você pode renomear o calendário para "Letícia - Guarda"')
    print('e ajustar as cores manualmente no Google Calendar:')
    print('- Azul para dias com o pai')
    print('- Preto para dias com a mãe')
    
    return nome_arquivo

# Gerar calendário para os próximos anos
if __name__ == '__main__':
    # Você pode ajustar os anos aqui
    gerar_calendario(2025, 2027)