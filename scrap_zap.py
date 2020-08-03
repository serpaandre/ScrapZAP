# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 19:30:44 2020

O Zap Imoveis possui parametros passados na URL. Usaremos como uma forma de controle da aplicação, sendo eles:
vTransação = aluguel ou venda
vImovel = apartamentos, studio, quitinetes, casas, casas-de-condominio, casas-de-vila, cobertura, flat, loft, 
          terrenos-lotes-condominios, fazendas-sitios-chacaras, loja-salao, conjunto-comercial-sala, casa-comercial,
          hoteis-moteis-pousadas, andares-lajes-corporativas, predio-inteiro, terrenos-lotes-comerciais,
          galpao-deposito-armazem, box-garagem
vUF = rj, sp, mg, etc 
vCidade = rio-de-janeiro, sao-paulo, belo-horizonte, rj+teresopolis, rj+petropolis, etc
vZona = zona-oeste, zona-norte, zona-sul, centro, etc
vBairro = jacarepagua, barra-da-tijuca, meier, etc
vPagina = pagina que se quer iniciar a coleta
vPagFinal = até ultima pagina a ser coletada

Podemos passar TODOS para vCidade, vZona e vBairro a fim de pegar todas as ocorrencias

@author: aserpa
"""


#Bibliotecas
import requests as rq
import json
import pandas as pd
from pandas.io.json import json_normalize


#Configura o display do pandas
pd.options.display.max_columns = 99
pd.options.display.max_rows = 99

#Imita um navegador para passar restricoes
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}


#Variaveis fixas
vPagFinal = 9999          #Numero total de paginas a serem buscadas, se houver menos o script controla
vTransacao = "aluguel"    #Tipo de transacao: venda ou aluguel
vUF = "rj"              #Unidade Federativa: rj, sp, mg, etc

#Listas para o script pegar automaticamente, pode aumentar ou diminuir com novos dados
vImovelLista = ["studio"]   #"casas","casas-de-vila","casas-de-condominio"
vCidadeLista = ["TODOS"] #Coloca o estado no formato "rio-de-janeiro","sao-paulo", ou "TODOS" sendo que tem q ajustar a vUF para pegar o estado
vZonaLista = ["TODOS"] #"zona-norte","centro","zona-sul", "zona-oeste", "zona-leste", "TODOS", etc
vBairroLista = ["TODOS"]   #"barra-da-tijuca","pechincha","freguesia-jacarepagua","anil" ou "TODOS" para pesquisar todos de determinada area


#Para cada cidade na lista
for vCidade in vCidadeLista:
    #para cada zona na lista de Zonas
    for vZona in vZonaLista:
        #Para cada bairro na lista de Bairros
        for vBairro in vBairroLista:
            #Para cada imovel na lista de imoveis
            for vImovel in vImovelLista:

                #Define a pagina inicial
                vPagina = 1
                    
                #Print dos dados para acompanhar
                print(vCidade + ' -> ' + vZona + ' -> ' + vBairro + ' -> ' + vImovel)
                
                #Teste se o Bairro é unico, alguns ou todos
                if vBairro == 'TODOS':
                    if vZona == 'TODOS':
                        if vCidade == 'TODOS':
                            vURL_B = "https://www.zapimoveis.com.br/" + vTransacao + "/" + vImovel 
                        else:
                            vURL_B = "https://www.zapimoveis.com.br/" + vTransacao + "/" + vImovel + "/" + vUF + "+" + vCidade
                    else:
                        vURL_B = "https://www.zapimoveis.com.br/" + vTransacao + "/" + vImovel + "/" + vUF + "+" + vCidade + "+" + vZona
                else:
                    vURL_B = "https://www.zapimoveis.com.br/" + vTransacao + "/" + vImovel + "/" + vUF + "+" + vCidade + "+" + vZona + "+" + vBairro 
                    
                #Cria o dicionario
                dfs = {}
                    
                #Itera entre as paginas
                while vPagina <= vPagFinal:
                        
                    #URL
                    vURL = vURL_B + "/?pagina=" + str(vPagina)
                    
                    print('Pagina: ' + str(vPagina))
                    #print(vURL)
                    #Testa o codigo de retorno do site
                    print(vURL+'\n')
                    vResp = rq.get(vURL,headers=headers)
                    vStat = vResp.status_code
                        
                    
                    #Se codigo 200, entao vai adiante
                    if vStat == 200:
                        vHTML = vResp.text
                        vHTML = str(vHTML)
                            
                        #Valida se a pagina existe ou nao
                        vValPag = 'OK' if 'Não encontramos resultados' in vHTML else 'NOK'
                            
                        #Continua se a pagina existir
                        if vValPag == 'NOK':
                        
                            #Pega apenas a parte do Json do codigo fonte
                            vHTML = vHTML.split('"results":{"listings":[',1)[1]
                            vHTML = vHTML.split('],"nearbyListings":[]',1)[0]
                            vHTML = vHTML.split(',"type":"nearby"}]',1)[0] 
                            #vHTML = vHTML.replace(',"superPremiumListings":[','')
                            #vHTML = vHTML.split(',"images":',1)[0]                    
                            
                            #Ao dar erro de delimitador, adicionar ou retirar chaves antes do colchetes na variavel abaixo
                            #Valida o fim da string, pois para alguns casos vem com char a menos
                            if vHTML[-2:] == '}}':
                                v1 = '{"listings":[' + vHTML + ']}'
                            elif vHTML[-10:] == '"premium"}':
                                vHTML = vHTML.split(',"type":"premium"}',1)[0]
                                #vHTML = vHTML.split(vHTML[-18],1)[0]
                                v1 = '{"listings":[' + vHTML + '}]}'
                            else:
                                v1 = '{"listings":[' + vHTML + '}]}'
                            #v1 = v1.replace(r'\u002',' ')
                                
                            
                            #x = 'id-2489012479\u002F"},"type":"premium"}],"superPremiumListings":['
                            #y = '"superPremiumListings":['
                            #print(x.split(y,1)[0])
                            
                            #print(vHTML)[-1:])
                            #print(v1)
                            #Retira a marcacao de moeda, deixando apenas o valor
                            v1 = v1.replace('R$ ','')
                            v1 = v1.replace(',"superPremiumListings":[}]}','}')
                            
                            #transforma para json
                            j = json.loads(v1)
                                
                            #Cria o dataframe do pandas, já normalizando o json
                            df = json_normalize(j['listings'])
                            
                                           
                                
                            #Cria a variavel com as colunas a serem deletadas
                            vCol = ['listing.nonActivationReason','listing.providerId','listing.address.stateAcronym','listing.address.source',
                                    'listing.address.locationId','listing.address.district','listing.address.name',
                                    'listing.address.poisList','listing.address.complement','listing.address.pois','listing.address.valuableZones',
                                    'listing.pricingInfos','listing.showPrice','listing.resale','listing.buildings','listing.capacityLimit','listing.constructionStatus',
                                    'listing.status','listing.hasAddress','listing.isDevelopment','listing.pricingInfo.showPrice','link.rel','account.showAddress',
                                    'link.data.street','link.data.streetNumber','link.data.state','link.data.city','link.data.zone','link.data.neighborhood','link.name',
                                    'listing.pricingInfo.businessDescription']
                                
                            #Deleta as colunas desnecessarias
                            df = df.drop(columns=vCol)
                                
                                
                            #print(df['listing.address.point.source'])
                            #Insere uma coluna referente a pagina lida
                            df['Page'] = vPagina
                                
                            #Insere a coluna com o tipo de imovel
                            df['imvl_type'] = vImovel
                                
                            #Tratamento dos dados
                            df['listing.publicationType'] = df['listing.publicationType'].fillna('Standard')
                                
                            #Retira o colchetes, transformando a lista em string dentro da coluna
                            df['listing.floors'] = [''.join(map(str, l)) for l in df['listing.floors']]
                            df['listing.unitTypes'] = [''.join(map(str, l)) for l in df['listing.unitTypes']]
                            df['listing.unitSubTypes'] = ['|'.join(map(str, l)) for l in df['listing.unitSubTypes']]
                            df['listing.parkingSpaces'] = [''.join(map(str, l)) for l in df['listing.parkingSpaces']]
                            df['listing.suites'] = [''.join(map(str, l)) for l in df['listing.suites']]
                            df['listing.bathrooms'] = [''.join(map(str, l)) for l in df['listing.bathrooms']]
                            df['listing.usageTypes'] = ['|'.join(map(str, l)) for l in df['listing.usageTypes']]
                            df['listing.totalAreas'] = [''.join(map(str, l)) for l in df['listing.totalAreas']]
                            df['listing.bedrooms'] = [''.join(map(str, l)) for l in df['listing.bedrooms']]
                            df['listing.amenities'] = ['|'.join(map(str, l)) for l in df['listing.amenities']]
                            df['listing.usableAreas'] = [''.join(map(str, l)) for l in df['listing.usableAreas']]
                                
                                
                            #Cria colunas baseadas na coluna listing.amenities
                            df['listing.pool'] = df['listing.amenities'].map(lambda x: 'True' if 'POOL' in x else 'False')                  #Piscina sim ou nao
                            df['listing.sauna'] = df['listing.amenities'].map(lambda x: 'True' if 'SAUNA' in x else 'False')                #Sauna sim ou nao
                            df['listing.backyard'] = df['listing.amenities'].map(lambda x: 'True' if 'BACKYARD' in x else 'False')          #Quintal sim ou nao
                            df['listing.garden'] = df['listing.amenities'].map(lambda x: 'True' if 'GARDEN' in x else 'False')              #Jardim sim ou nao
                            df['listing.barbgrill'] = df['listing.amenities'].map(lambda x: 'True' if 'BARBECUE_GRILL' in x else 'False')   #Churrasqueira sim ou nao
                            df['listing.partyhall'] = df['listing.amenities'].map(lambda x: 'True' if 'PARTY_HALL' in x else 'False')       #Salao de festas sim ou nao
                            df['listing.tenniscourt'] = df['listing.amenities'].map(lambda x: 'True' if 'TENNIS_COURT' in x else 'False')   #Quadra de Tennis sim ou nao
                            df['listing.sportcourt'] = df['listing.amenities'].map(lambda x: 'True' if 'SPORTS_COURT' in x else 'False')    #Quadra de Esportes sim ou nao
                            df['listing.bathtub'] = df['listing.amenities'].map(lambda x: 'True' if 'BATHTUB' in x else 'False')            #Banheira sim ou nao
                            df['listing.soundproofing'] = df['listing.amenities'].map(lambda x: 'True' if 'SOUNDPROOFING' in x else 'False')#Prova de som sim ou nao
                            df['listing.fireplace'] = df['listing.amenities'].map(lambda x: 'True' if 'FIREPLACE' in x else 'False')        #Lareira sim ou nao
                            df['listing.gym'] = df['listing.amenities'].map(lambda x: 'True' if 'GYM' in x else 'False')                    #Academia sim ou nao
                            df['listing.hottub'] = df['listing.amenities'].map(lambda x: 'True' if 'HOT_TUB' in x else 'False')             #Hidromassagem sim ou nao
                            df['listing.furnished'] = df['listing.amenities'].map(lambda x: 'True' if 'FURNISHED' in x else 'False')        #Mobiliado sim ou nao
                            df['listing.guestpark'] = df['listing.amenities'].map(lambda x: 'True' if 'GUEST_PARKING' in x else 'False')    #Estacionamento Visitantes sim ou nao
                            df['listing.playground'] = df['listing.amenities'].map(lambda x: 'True' if 'PLAYGROUND' in x else 'False')      #Playground sim ou nao
                            df['listing.mountainview'] = df['listing.amenities'].map(lambda x: 'True' if 'MOUNTAIN_VIEW' in x else 'False')    #Vista da montanha sim ou nao
                                
                            #Cria a entrada variavel no dicionario
                            dfs['df_' + str(vPagina)] = df
                
                            #Incrementa um na pagina
                            vPagina = vPagina + 1
                            
                        else:
                            break
                        
                        
                        #vStat = vResp.status_code 
                        #Sai do Loop
                    else:
                        print(vURL)
                        print('\n')
                        print(vStat)
                        break
                        
                    
                    
                    
                
                #Cria a lista 
                vAcaoFimLista = []
                    
                #Para cada entrada dinamica criada no Dicionário, adiciona na lista
                for i in dfs.keys(): 
                    #print(i)
                    vAcaoFimLista.append(dfs[i])
                    #df_acoes = pandas.DataFrame().append(dfs[i], ignore_index=False)
                    
                #Concatena os dados da lista em um unico dataframe
                df_Zap = pd.concat(vAcaoFimLista, sort=False)
                    
                #Exporta pra csv, usando encoding do windows
                
                print('\nCriando o arquivo dataZAP_'+vTransacao+'_'+vImovel+'_'+vBairro+'.csv com os dados')
                df_Zap.to_csv('dataZAP_'+vTransacao+'_'+vImovel+'_'+vBairro+'.csv', sep=';', index=False)
                print('\nArquivo criado\n')
                print('-----------------------------------------------------')

