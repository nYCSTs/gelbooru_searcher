import requests
import webbrowser
from bs4 import BeautifulSoup
import numpy as np
import time
import os
import platform 

def connection(url, url_alt, dados, quantidade, flag, name_dict):
    #dados = (nome [0], nome_trocado [1], tag [2], rating [3])  
    print(f"Personagem/anime: {dados[0]} | {dados[1]}\nTags: {dados[2]}\nRating: {dados[3]}\n" )
    intervalo = 0

    saida = check_url(url, url_alt, dados[2], dados[3])
    url = saida[1]
    nome = dados[saida[0]]

    if (url == 0):
        return name_dict

    char_page = get_soup(url)
    char_page[0].close()
    origUrl = url
    
    #OBTEM QUANTIDADE DE PAGINAS
    qnt_pages = get_qnt_pages(char_page)
    url = origUrl + '&pid=' + str(qnt_pages * 42 - 42)
    qnt_imagens = contarQuantidadeDeImagens(origUrl, qnt_pages)

    if (flag != 'c'):
        if (quantidade > qnt_imagens):
            if (qnt_imagens > 0):
                print(f'A quantidade solicitada de {quantidade} imagens excede a quantidade disponivel de {qnt_imagens}. Serão mostradas o maximo de imagens possiveis.')
            else:
                suggest((dados[0], dados[1]), dados[2])
                return name_dict
    
            quantidade = qnt_imagens
        
        else:
            print(f'Foram encontrados {qnt_imagens} resultado(s) em {qnt_pages} pagina(s)')
    else:
        print(f'Entrando em modo de exibicao continuo. Foram encontradas um total de {qnt_imagens} para as especificacoes passadas')
        quantidade = qnt_imagens
        intervalo = 5
    

    if (nome + ''.join(dados[2]) + dados[3] not in name_dict):
        imagesList = np.arange(0, qnt_imagens)
        name_dict[nome + ''.join(dados[2]) + dados[3]] = imagesList
    else:
        if (np.size(name_dict[nome + ''.join(dados[2]) + dados[3]]) == 0):
            print('Nenhuma nova imagem encontrada')
            return name_dict
        else:
            imagesList = name_dict.get(nome + ''.join(dados[2]) + dados[3])

    for i in range(quantidade):
        #SORTEIA UMA DAS PAGINAS

        ind = int(np.random.choice(imagesList,1))
        random_page = int(ind / 42)
        imagesList = np.delete(imagesList, np.argwhere(imagesList == ind))
        url = origUrl + '&pid=' + str(random_page)
        print(f"Imagem {ind - (random_page * 42) + 1} da pagina {random_page + 1}")

        #SORTEIA UMA DAS IMAGENS E GERA O LINK FINAL
        conn = get_soup(url)
        element = str(conn[1].findAll('div', class_ = 'thumbnail-container')).split('<div')[2:]
        conn[0].close()
        
        element = str(element[ind - (random_page * 42)])
        code = element[element.find(';id=') + 4:element.find('&amp;tags=')]
        url = 'https://gelbooru.com/index.php?page=post&s=view&id=' + code

        conn = get_soup(url)
        x = str(conn[1].findAll('meta', property = 'og:image'))
        img_link = x[16:-24]
        conn[0].close()
        time.sleep(intervalo)

        webbrowser.open_new_tab(img_link)

    name_dict[nome + ''.join(dados[2]) + dados[3]] = imagesList
    return name_dict

def contarQuantidadeDeImagens(url, qntPages):
    conn = get_soup(url + '&pid=' + str(int(qntPages * 42 - 42)))
    x = str(conn[1].findAll('div', class_ = 'thumbnail-container')).split('<div')[2:]
    conn[0].close()

    return int((qntPages - 1) * 42 + len(x))

def suggest(names, tags = []):
    for name in names:
        url = 'https://gelbooru.com/index.php?page=tags&s=list&tags=' + name + '*&sort=desc&order_by=index_count'
        conn = get_soup(url)
        conn[0].close() 

        # nao foi encontrado
        if (conn[0].text.find('No results found') != -1):
            if (alternado != ''):
                continue
            else:
                print('Não foi encontrado nenhum resultado.')
        elif (conn[0].text.find('results found, refine your search.') != -1):
            print('Nome muito abrangente, tente novamente.')
        else:
            if (len(tags) > 0):
                print(f'Não foram encontrados resultados que satisfaçam as tags passadas ({tags})')
            else:
                print('Similares: ')
                display(conn[1])
            break 
    return 

def get_qnt_pages(char_page):
    element = str(char_page[1].findAll('div', class_ = 'pagination')).split('<a')
    if (len(element) == 1):
        qnt_pages = 1
    elif (element[-1][-12] == '»'):
        qnt_pages = int(element[-1][element[-1].find('&amp;pid=') + 9:element[-1].find('">»</a>')])
        if qnt_pages > 20000:
            qnt_pages = 477
        else:
            qnt_pages = qnt_pages / 42
        qnt_pages += 1
    else:
        qnt_pages = int(element[-1][element[-1].find('">') + 2:element[-1].find('</a>')])
    
    return qnt_pages

def check_url(url, url_alt, tag, rating):
    char_page = get_soup(url)

    # nome invalido
    if (char_page[0].text.find('Nobody here but us chickens!') != -1 and url_alt != ''):
        char_page[0].close()
        char_page = get_soup(url_alt)
        if (char_page[0].text.find('Nobody here but us chickens!') != -1):
            if (tag == ''):
                print("\n\tPersonagem não encontrado. Experimente usar '-a'.")
            else:
                print('\n\tNão foram encontrados resultados com as tags e/ou rating passados.')
            
            return 0
        else:
            return (1, url_alt)

    else:
        return (0, url)
    
    return 0

# personagens relacionados
def info_search(origUrl, name):
    character = []
    series = []
    check = [name]
    pag_pesquisadas = 8

    conn = get_soup(origUrl)
    conn[0].close()
    qnt_pages = get_qnt_pages(conn)

    if (qnt_pages < 8):
        random_pages = np.arange(0, qnt_pages)
    else:
        random_pages = np.random.randint(0, qnt_pages, pag_pesquisadas)

    for pagina in random_pages:
        #obter url
        url = origUrl + '&pid=' + str(42 * pagina)
        conn = get_soup(url)
        conn[0].close()

        #pega elemento
        relation_element = str(conn[1].findAll('div', id = 'searchTags')).split('<li')[1:]


        for tag in relation_element:
            #tipo de tag
            tag_type = tag[17:21]
            if (tag_type == 'char' or tag_type == 'copy'):
                #qual o valor da tag
                curr_tag = tag[tag.rfind('nofollow') + 10:tag.rfind('</a>')]
                if (curr_tag not in check):
                    count = int(tag[tag.find(';">') + 3:tag.find('</span>')])
                    if (tag_type == 'copy'):
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

# obter conexao
def get_soup(url):
    cookies = {"fringeBenefits":"yup", "resize-original":"1", "resize-notification":"1"}
    r = requests.get(url = url, cookies = cookies)
    content = r.content
    soup = BeautifulSoup(content, features="lxml")
    return (r, soup)

# arrumar link
def fix(name):
    orig = ('(',   ')',   '!',   '/',   ':',   '?',   "'",   ';')
    new = ('%28', '%29', '%21', '%2f', '%3a', '%3f', '%27', '%3b')
    replace = zip(orig, new)
    for orig, new in replace:
        name = name.replace(orig, new)
    return name
    

VERSION = '1.5.0 Beta'
print(VERSION)
name_dict = {}
while True:
    # declaracao
    name = alternado = rating = tags = tag = url = url_alt = remove = flag = ''
    # input
    search = input('\n\t(pesquisar tag: 1; ajuda: 2; sair: 0) >> ').strip()
    #os.system('cls')

    if (len(search) <= 2):
        # sair
        if (search == '0'):    
            break

        # pesquisar tag
        elif (search == '1'):   
            tag_name = input('Tag a ser procurada (0: voltar): ')
            if (tag_name == '0'):
                continue
            url = 'https://gelbooru.com/index.php?page=tags&s=list&tags=' + tag_name + '*&sort=desc&order_by=index_count'
            display(get_soup(url)[1])
            continue

        # ajuda
        elif (search == '2'):
            print('-------------------\n[personagem/anime]\n[personagem/anime] [-t: TAGS] [-s/-q/-e: RATING] [-i: INFO] [QUANTIDADE] : padrao\n[personagem/anime] [-a: similares] : verifica a validade de um personagem/show\n[personagem/anime] [-i: info] : personagens/animes relacionados\n[-r: random] : imagem aleatoria\n-------------------')
            continue

        # random 
        elif (search == '-r'):
            url = 'https://gelbooru.com/index.php?page=post&s=list&tags=all'

    # vericar taiga
    elif (('taiga' in search) and ('aisaka' in search) and (('-q' in search) or ('-e' in search))):
        print('Proibido.')
        continue

    else:  
        if (search[-2:] == '-c'):
            flag = 'c'
            search = search[:-2].strip()
            quantidade = 1
        else:
            # obter quantidade
            try:
                quantidade = int(search[search.rfind(' ') + 1:])
                search = search[:search.rfind(' ')]
            except:
                quantidade = 1

        if ('-' in search):
            # obtem rating
            if (search[-2:] in ('-s', '-q', '-e')):
                if (search[-3] == '~'):
                    remove = '-'
                    rating = '~'
                if (search[-2:] == '-s'):
                    rating += 'safe'
                elif (search[-2:] == '-q'):
                    rating += 'questionable'
                elif (search[-2:] == '-e'):
                    rating += 'explicit'

                search = search[:search.rfind(' ')]

            # obtem tags
            if ('-t' in search):
                tags = search[search.find('-t') + 2:].split()
                search = search[:search.find('-t')]

            # info 
            elif ('-i' in search):
                search = search[:search.find('-i')].strip()
                if (len(search.split()) == 2):
                    split = search.split()
                    alternado = (split[1] + ' ' + split[0]).strip()
                    url_alt = 'https://gelbooru.com/index.php?page=post&s=list&tags=' + alternado.replace(' ', '_')

                url = 'https://gelbooru.com/index.php?page=post&s=list&tags=' + search.replace(' ', '_')
                
                url = check_url(url, url_alt, '', '')
                if (url != 0):
                    info_search(url, search)
                continue

            # suggest
            elif ('-a' in search):
                name = search[:search.find('-a')].strip()
                name = name.replace(' ', '_')
                if (len(name.split()) == 2):
                    split = name.split()
                    alternado = f'{split[1]} {split[0]}'

                suggest((name, alternado))
                continue

        #obtem alternado        
        if (len(search.split()) == 2):
            split = search.split()
            alternado = f'{split[1]}_{split[0]}' 

        name = '_'.join(search.split())
        url = 'https://gelbooru.com/index.php?page=post&s=list&tags=' + fix(name) + '+'

        # com tag
        if (len(tags) > 0):
            for index, tag in enumerate(tags):
                if (tag[0] == '~'):
                    url += f'-{tag[1:]}+'
                else:
                    url += f'{tag}+'
                        
        # com rating
        if (rating != ''):
            url += f'{remove}rating%3a{rating}'

        if (alternado != ''):
            url_alt = url.replace(name, fix(alternado))    

    name_dict = connection(url, url_alt, (name, alternado, tags, rating), quantidade, flag, name_dict)  

    '''
    except:
        print('Formato incorreto.\n')
    else:
        print('\n')
        if (platform.system() == 'Windows'):
            os.system('cls')
        else:
            os.system('clear')          
    '''

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
# BUG: konosuba -a