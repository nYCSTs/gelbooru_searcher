import requests
import webbrowser
from bs4 import BeautifulSoup
import numpy as np
import time
import os
import platform 
import math

# A PARTE PRINCIPAL
def connection(urls, dados, quantidade, name_dict):
    #URLS  = (url, url_alt)
    #DADOS = (nome, nome_trocado, tag, rating)

    pos, url = check_url(urls, dados[2], dados[3])

    # DETALHES DA PESQUISA
    print(f"Personagem/anime: {dados[pos].replace('_', ' ')}\nTags: {dados[2]}\nClassificacao: {dados[3]}\nQuantidade: {quantidade}")
    if (url == ''):
        if (tag == ''):
            print("\n\tPersonagem não encontrado. Experimente usar '-a'.")
        else:
            print('\n\tNão foram encontrados resultados com as tags e/ou rating passados.') 
        return     
    else:
        nome = dados[pos]
        print(f'URL: {url}')
    
    # CRIA UMA COPIA 
    origUrl = url
    # OBTEM O HTML DA PAGINA
    html = getHTML(url)
    
    # OBTEM TOTAL DE IMAGENS
    qntPages = getQuantidadePaginas(html) #total de paginas
    url = origUrl + '&pid=' + str(qntPages * 42 - 42)
    qnt_imagens = getQuantidadeDeImagens(origUrl, qntPages)

    # MODO NORMAL
    if (quantidade != 'continuo'):
        intervalo = 2
        
        # CASO A QUANTIDADE DESEJADA SEJA MAIOR QUE A DISPONIVEL
        if (quantidade > qnt_imagens):
            if (qnt_imagens > 0):
                print(f'A quantidade solicitada de {quantidade} imagens excede a quantidade disponivel de {qnt_imagens}. Serão mostradas o maximo de imagens possiveis.')
            else:
                suggest((dados[0], dados[1]), dados[2])
                return name_dict
    
            quantidade = qnt_imagens
        
        # CASO A QUANTIDADE DESEJADA SEJA MENOR QUE O TOTAL
        else:
            print(f'\nForam encontrados {qnt_imagens} resultado(s) em {qntPages} pagina(s)')
    
    # MODO CONTINUO
    else:
        print(f'\nEntrando em modo de exibicao continuo.\nForam encontradas {qnt_imagens} imagens em {qntPages} paginas.\n\n')
        quantidade = qnt_imagens
        intervalo = 6
    
    if (nome + ''.join(dados[2]) + dados[3] not in name_dict):
        imagesList = np.arange(0, qnt_imagens)
        name_dict[nome + ''.join(dados[2]) + dados[3]] = imagesList
    else:
        if (np.size(name_dict[nome + ''.join(dados[2]) + dados[3]]) == 0):
            print('Nenhuma nova imagem encontrada')
            return name_dict
        else:
            imagesList = name_dict.get(nome + ''.join(dados[2]) + dados[3])


    for _ in range(quantidade):
        # PARA CADA IMAGEM E DADA UM 'ID', E COM ESSE ID E POSSIVEL CHEGAR NA PAGINA E NA IMAGEM DESSE ID
        # idSorteado: ID SORTEADO 
        idSorteado = int(np.random.choice(imagesList, 1))
        # REMOVE O ID SORTEADO, PARA QUE ELE NAO SEJA SELECIONADO NOVAMENTE
        imagesList = np.delete(imagesList, np.argwhere(imagesList == idSorteado))
        # imagem: A IMAGEM DA PAGINA EM QUESTAO
        # randomPage: REALIZA O CALCULO PARA CHEGAR NA PAGINA SORTEADA
        imagem, randomPage = math.modf(idSorteado / 42.0)
        imagem = round(imagem * 42)

        # CONSTROI URL
        url = origUrl + '&pid=' + str((randomPage - 1) * 42)
        print(f"Imagem {imagem + 1} da pagina {int(randomPage + 1)}")

        # OBTEM HTML(1) E DEPOIS PEGA A PARTE DAS IMAGENS(2)
        html = getHTML(url)
        element = str(html.findAll('div', class_ = 'thumbnail-container')).split('<div')[2:]
        
        element = str(element[imagem])
        code = element[element.find(';id=') + 4:element.find('&amp;tags=')]
        url = 'https://gelbooru.com/index.php?page=post&s=view&id=' + code
        print(f'Pagina da imagem: {url}\n')

        # URL DO POST RANDOMICO OBTIDO
        html = getHTML(url)
        # GERA INFORMACOES DA IMAGEM OBTIDA 
        info = html.findAll('div', id = 'searchTags')
        for _ in map(img_info, [info, info, info], ['character', 'copyright', 'general']):
            pass
        print('\n\n')
        # GERA O LINK FINAL DA IMAGEM
        img_link = str(html.findAll('meta', property = 'og:image'))
        img_link = img_link[img_link.find('content') + 9:img_link.find('property') - 2]
        
        # ABRE IMAGEM NO NAVEGADOR
        webbrowser.open_new_tab(img_link)
        # COOLDOWN
        time.sleep(intervalo)

    name_dict[nome + ''.join(dados[2]) + dados[3]] = imagesList
    return name_dict

# DETALHES RELACIONADOS AO POST ENCONTRADO
def img_info(info, tipo_info):
    tipo = {'character':'personagens', 'copyright':'obra', 'general':'tags'}
    lista = ''

    for x in info[0].find_all('li', class_ = 'tag-type-' + tipo_info):
        x = str(x).split('">')
        lista += x[3][:x[3].find('</a>')] + ', '

    print(f'{tipo.get(tipo_info)}: {lista[:-2]}')

# OBTEM O TOTAL DE IMAGENS
def getQuantidadeDeImagens(url, qntPages):
    html = getHTML(url + '&pid=' + str(int(qntPages * 42 - 42)))
    x = str(html.findAll('div', class_ = 'thumbnail-container')).split('<div')[2:]

    return int((qntPages - 1) * 42 + len(x))

# SUGESTAO DE RESULTADOS SEMELHANTES
def suggest(names, tags = []):
    for name in names:
        url = 'https://gelbooru.com/index.php?page=tags&s=list&tags=' + name + '*&sort=desc&order_by=index_count'
        html = getHTML(url)

        # nao foi encontrado
        if (html.text.find('No results found') != -1):
            if (alternado != ''):
                continue
            else:
                print('Não foi encontrado nenhum resultado.')
                return
        elif (html.text.find('results found, refine your search.') != -1):
            print('Nome muito abrangente, tente novamente.')
        else:
            if (len(tags) > 0):
                print(f'Não foram encontrados resultados que satisfaçam as tags passadas ({tags})')
            else:
                print('Similares: ')
                display(html)
            break 
    return 

# OBTEM O TOTAL DE PAGINAS 
def getQuantidadePaginas(html):
    element = str(html.findAll('div', class_ = 'pagination')).split('<a')
    if (len(element) == 1):
        qntPages = 1
    elif (element[-1][-12] == '»'):
        qntPages = int(element[-1][element[-1].find('&amp;pid=') + 9:element[-1].find('">»</a>')])
        if qntPages > 20000:
            qntPages = 477
        else:
            qntPages = qntPages / 42
        qntPages += 1
    else:
        qntPages = int(element[-1][element[-1].find('">') + 2:element[-1].find('</a>')])
    
    return qntPages

# VERIFICA SE HA RESULTADO PARA TAL PESQUISA
def check_url(urls, tag, rating):
    html = str(getHTML(urls[0]))
    
    # URL1 INVALIDA
    if (html.find('Nobody here but us chickens!') != -1):
        if (urls[1] != ''):
            html = str(getHTML(urls[1]))

            if (html.find('Nobody here but us chickens!') != -1):
                return (0, '')
            else:
                return (1, urls[1])
        else:
            return (0, '')
    
    return (0, urls[0])

# PERSONAGENS/SHOWS RELACIONADOS COM A PESQUISA
def info_search(origUrl, name):
    character = []
    series = []
    check = [name]
    qntPaginasPesquisadas = 10

    html = getHTML(origUrl)
    qntPages = getQuantidadePaginas(html)

    if (qntPages < qntPaginasPesquisadas):
        random_pages = np.arange(0, qntPages)
    else:
        random_pages = np.random.randint(0, qntPages, qntPaginasPesquisadas)

    for pagina in random_pages:
        #obter url
        url = origUrl + '&pid=' + str(42 * pagina)
        html = getHTML(url)

        #pega elemento
        relation_element = str(html.findAll('div', id = 'searchTags')).split('<li')[1:]

        for tag in relation_element:
            #tipo de tag
            tag_type = tag[tag.find('tag-type') + 9:tag.find('">')]
            if (tag_type == 'character' or tag_type == 'copyright'):
                #qual o valor da tag
                curr_tag = tag[tag.rfind('nofollow') + 10:tag.rfind('</a>')]
                if (curr_tag not in check):
                    count = int(tag[tag.find(';">') + 3:tag.find('</span>')])
                    if (tag_type == 'copyright'):
                        series.append((curr_tag, count))
                    else:
                        character.append((curr_tag, count))

                    check.append(curr_tag)

    if (len(character) > 0 or len(series) > 0):
        character_list = ''
        series_list = ''
        # sort
        series.sort(key = lambda valor : valor[1], reverse = True)
        character.sort(key = lambda valor : valor[1], reverse = True)

        for item in character:
            character_list += f'{item[0]} [{item[1]}] ; '  

        for item in series:
            series_list += f'{item[0]} [{item[1]}] ; '

        print('\nSeries relacionadas:      ' + series_list[:-2])
        print('\nPersonagens relacionados: ' + character_list[:-2])
        print('\n')

# PESQUISA GERAL
def display(soup):
    spacement = '      '
    table = str(soup.findAll('table', class_ = 'highlightable')).split('<tr')[2:7]

    print('\n')
    for element in table:
        element_name = element[element.find('<a href'):element.find('</a>')]
        name = element_name[element_name.find('">') + 2:]
        count = element[element.find('<td>') + 4:element.find('</td>')]
        print('\t\t' + count + spacement[:len(spacement) - len(count)] + '|   ' + name)
    print('\n')

# OBTEM HTML DA PAGINA
def getHTML(url):
    cookies = {"fringeBenefits":"yup", "resize-original":"1", "resize-notification":"1"}
    r = requests.get(url = url, cookies = cookies)
    content = r.content
    r.close()

    return BeautifulSoup(content, features="lxml")

# ARRUMAR SIMBOLOS INCOMPATIVEIS
def arrumarSimbolos(name):
    orig = ('(',   ')',   '!',   '/',   ':',   '?',   "'",   ';', '+')
    new = ('%28', '%29', '%21', '%2f', '%3a', '%3f', '%27', '%3b', '%2b')
    troca = zip(orig, new)
    for orig, new in troca:
        name = name.replace(orig, new)
    return name
    
commands = {'Windows':'cls', 'Linux':'clear'}
ratings = {'-s':'rating%3asafe+', '-q': 'rating%3aquestionable+', '-e':'rating%3aexplicit+', '~-s':'-rating%3asafe+', '~-q': '-rating%3aquestionable+',
'~-e':'-rating%3aexplicit+', 'rating%3asafe+':'seguro', 'rating%3aquestionable+':'questionavel', 'rating%3aexplicit+':'explicito', '-rating%3asafe+':'-seguro',
'-rating%3aquestionable+':'-questionavel', '-rating%3aexplicit+':'-explicito'}
name_dict = {}

while True:
    # DECLARACAO
    name = alternado = rating = tags = tag = url = url_alt =  ''
    # OBTER ENTRADA DO USUARIO
    search = input('\n\t(pesquisar tag: 1; ajuda: 2; sair: 0) >> ').strip()
    os.system(commands.get(platform.system())) 

    #try:
    #OPCOES
    if (search in ['0', '1', '2']):
        # FECHAR
        if (search == '0'):    
            break

        # PESQUISAR TAG 
        elif (search == '1'):   
            tag_name = input('Tag a ser pesquisada (0: voltar): ')
            if (tag_name != '0'):
                url = 'https://gelbooru.com/index.php?page=tags&s=list&tags=' + tag_name + '*&sort=desc&order_by=index_count'
                display(getHTML(url))

        # AJUDA
        elif (search == '2'):
            print('-> PESQUISAR POR PERSONAGEM OU ANIME:\n\t[personagem/nome do anime]\n\n-> PESQUISA USANDO TAGS:\n\t[personagem/nome do anime] -t [tag1] [tag2] [tag3] ...\n\n-> PESQUISAR POR CLASSIFICACAO ESPECIFICA (S - SEGURO | Q - QUESTIONAVEL | E - EXPLICITO)\n\t[personagem/nome do anime] -s ou -q ou -e\n\n-> PESQUISAR POR PERSONAGENS/ANIMES PARECIDOS:\n\t[personagem/nome do anime] -a\n\n-> PESQUISAR POR PERSONAGENS/ANIMES RELACIONADOS:\n\t[personagem/nome do anime] -i\n\n-> MODO DE EXIBICAO CONTINUA:\n\t[personagem/nome do anime] -c\n\n-> MOSTRAR CERTA QUANTIDADE DE IMAGENS (PADRAO E 1 IMAGEM):\n\t[personagem/nome do anime] [QUANTIDADE]\n\nE possivel combinar algumas opcoes, como por exemplo tags especificas e rating. Ex:.\n\t[personagem/nome do anime] -t [tag1] [tag2] -q\n\nO modo de exibicao continuo e possivel em qualquer combinacao, mas deve ser colocado sempre no final de tudo.\n\n')
        continue

    else: 
        # QUANTIDADE DE IMAGENS
        try:
            quantidade = int(search[search.rfind(' '): ])
            search = search[:search.rfind(' ')]
        except:
            if (' -c' in search):
                quantidade = 'continuo'
                search = search[:search.rfind(' ')]
            else:
                quantidade = 1

        if ('-' in search):        
            # INFORMACOES 
            if ('-i' in search):
                search = arrumarSimbolos(search[:search.find('-i')].strip())
                if (len(search.split()) == 2):
                    split = search.split()
                    alternado = (split[1] + ' ' + split[0]).strip()
                    url_alt = 'https://gelbooru.com/index.php?page=post&s=list&tags=' + alternado.replace(' ', '_')

                url = 'https://gelbooru.com/index.php?page=post&s=list&tags=' + search.replace(' ', '_')
                _, url = check_url([url, url_alt], '', '')
                url += '+'
                if (len(tags) > 0):
                    for index, tag in enumerate(tags):
                        if (tag[0] == '~'):
                            url += f'-{tag[1:]}+'
                        else:
                            url += f'{tag}+'
                if (url != ''):
                    info_search(url, search)
                continue

            # OBTER RATING
            x = ''.join([item for item in search.split() if item in ('-s', '-q', '-e', '~-s', '~-q', '~-e')])
            if (len(x) > 0):
                rating = ratings.get(x)
                search = search.replace(' ' + x, '')

            # OBTER TAGS
            if (search.find('-t ') != -1):
                tags = search[search.find('-t') + 3:].split()
                search = search.replace('-t ' + ' '.join(tags), '')

            # SUGESTAO
            if ('-a' in search[-2:]):
                name = search[:search.find('-a')].strip()
                name_split = name.split()
                name = name.replace(' ', '_')
                if (len(name_split) == 2):
                    alternado = f'{name_split[1]} {name_split[0]}'
                    alternado = alternado.replace(' ', '_')

                suggest((name, alternado))
                continue

        # OBTEM NOME ALTERNADO       
        if (len(search.split()) == 2):
            split = search.split()
            alternado = f'{split[1]}_{split[0]}' 

        name = '_'.join(search.split())
        url = 'https://gelbooru.com/index.php?page=post&s=list&tags=' + arrumarSimbolos(name) + '+'

        # MONTAR URL --------------------------------------------------------------

        # COLOCA AS TAGS NA URL
        if (len(tags) > 0):
            for index, tag in enumerate(tags):
                if (tag[0] == '~'):
                    url += f'-{tag[1:]}+'
                else:
                    url += f'{tag}+'
                        
        # COLOCA O RATING NA URL
        if (rating != ''):
            url += rating
            rating = ratings.get(rating)

        if (alternado != ''):
            url_alt = url.replace(name, arrumarSimbolos(alternado))    

    #                           URLS                DADOS                  QNT. IMAGENS HISTORICO
    name_dict = connection((url, url_alt), (name, alternado, tags, rating), quantidade, name_dict)  

    '''
    except:
        print('Formato incorreto.\n')
    '''

# TODO
# acabar com o loop em caso de nao haver mais novas imagens                     X  
# arrumar a limitacao de 9 imagens em quantidade                                X
# nome + quantidade == erro (nome 10)                                           X
# nome -rating quantidade == erro (nome -s 10)                                  X
# arrumar a tosquice de texto sem sentido (testar akko_kagari -e)               X
# refine search (testar shiro -a)                                               X
# random                                                                        X
# erro com tags (testar -t animated loli uncensored -e)                         X
# proibir aisaka taiga                                                          X
# excluir tags (~)                                                              X                      
# inverter palavras caso (A B (algo))                                           P
# salvar links ja abertos                                                       A
# melhorar codigo                                                               X
# implementar uma gui                                                           P
# tutorial                                                                      X
# trabalhar com as diferentes "tag-type" (copyright, character)                 X
# opcao de ~rating para remover algum rating especifico                         X
# trocar if-elif-else por switch com dictionary                                 A
# verificar se e windows ou linux                                               X
# best tags [loli, lolicon, small_breasts, flat_chest, highres, uncensored]     X
# obter somente info de um personagem/anime                                     X
# escolher quando se quer info ao usar rating                                   X
# taiga                                                                         X
# BUG: tag com _                                                                X
# BUG: sword art online -t cat_ears uncensored animated -e                      X
# nomes em -i ordenados por quantidade                                          X
# BUG: toujou koneko -t animated -e                                             X
# BUG: contar a quantidade de paginas                                           X
# BUG: konosuba -a                                                              X
# BUG: miko iino -a                                                             X
# BUG: nefertari_vivi -e
# BUG: re:zero kara hajimeru isekai seikatsu -t loli -e
