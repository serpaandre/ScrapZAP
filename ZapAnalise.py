# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 11:53:33 2020

Analise dos dados coletados do ZAP pelo script scrap_zap.py

@author: aserpa
"""

#Bibliotecas
import os
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from pandas_profiling import ProfileReport
from wordcloud import WordCloud
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_score



sns.set_palette(sns.xkcd_palette)

#Configura o display do pandas
pd.options.display.max_columns = 99
pd.options.display.max_rows = 99

#Variavel de controle
#vVlrALuguel = 5000

#Diretorio arquivos
vDirArqs = 'C:\Pessoal\Estudos\Scripts Python\ZAP Imoveis\Casas Aluguel\Guadalupe'

#Cria o dicionario para armazenar os dataframes
dfs = {}

#Cria a lista temporaria
vListaArqs = []


#Pra cada arquivo csv na pasta, adiciona na lista e no dicionario
for f in os.listdir(vDirArqs):
    if f.endswith('.csv'):
        #ADiciona na lista
        vListaArqs.append(f)
        #Adiciona no dicionario criando a entrada df_n e gerando o dataframe a partir do arquivo
        dfs['df_'+ str(vListaArqs.index(f))] = pd.read_csv(vDirArqs + '\\' + f, sep=';', dtype=str)


#Cria a lista para os dataframes
vAcaoFimLista = []

#Para cada entrada dinamica criada no Dicionário, adiciona na lista
for i in dfs.keys(): 
    print(i)
    vAcaoFimLista.append(dfs[i])


#Junta todos os dataframes da lista
df = pd.concat(vAcaoFimLista, sort=True)


#Informacoes sobre as colunas
print(df.info())
print(df.describe())
print(df.index)

#Lista o total de nulos por colunas
print(df.isnull().sum())



############################ Inicio tratamento dos dados ############################

#Separa os anuncios, pegando aqueles q sao somente aluguel
#df = df.loc[(df['listing.pricingInfo.isSale']) == False]

#Limpa o ponto da string, para evitar uma conversao errada pra float
df['listing.pricingInfo.rentalPrice'] = df['listing.pricingInfo.rentalPrice'].str.replace('.', '')
df['listing.pricingInfo.rentalTotalPrice'] = df['listing.pricingInfo.rentalTotalPrice'].str.replace('.', '')
df['listing.pricingInfo.salePrice'] = df['listing.pricingInfo.salePrice'].str.replace('.', '')
df['listing.pricingInfo.yearlyIptu'] = df['listing.pricingInfo.yearlyIptu'].str.replace('.', '')
df['listing.pricingInfo.monthlyCondoFee'] = df['listing.pricingInfo.monthlyCondoFee'].str.replace('.', '')
df['listing.pricingInfo.price'] = df['listing.pricingInfo.price'].str.replace('.', '')


#Faz a conversao dos campos
#FLOAT
df['listing.pricingInfo.rentalPrice'] = df['listing.pricingInfo.rentalPrice'].astype(float)
df['listing.pricingInfo.rentalTotalPrice'] = df['listing.pricingInfo.rentalTotalPrice'].astype(float)
df['listing.pricingInfo.salePrice'] = df['listing.pricingInfo.salePrice'].astype(float)
df['listing.pricingInfo.yearlyIptu'] = df['listing.pricingInfo.yearlyIptu'].astype(float)
df['listing.pricingInfo.monthlyCondoFee'] = df['listing.pricingInfo.monthlyCondoFee'].astype(float)
df['listing.pricingInfo.price'] = df['listing.pricingInfo.price'].astype(float)

#INT
df['listing.bedrooms'] = df['listing.bedrooms'].astype(int)
df['listing.bathrooms'] = df['listing.bathrooms'].astype(int)
df['listing.usableAreas'] = df['listing.usableAreas'].astype(int)

#DATE
df['listing.createdAt'] = pd.to_datetime(df['listing.createdAt'])
df['listing.updatedAt'] = pd.to_datetime(df['listing.updatedAt'])


#Limitando o aluguel até 5 mil
df = df.where(df['listing.pricingInfo.rentalPrice'] <= vVlrALuguel)

#Deleta as colunas que nao precisa para analise
vCol = ['listing.address.streetNumber','Page','account.legacyVivarealId','account.legacyZapId','listing.address.geoJson','account.licenseNumber',
        'listing.address.ibgeCityId','listing.id','listing.legacyId','listing.pricingInfo.priceVariation','listing.description','listing.images','listing.videos']
df.drop(columns=vCol, inplace=True)


#Deleta as colunas que possuem apenas um valor para todos os registros, pois so esta ocupando espaço
#df = df.loc[:, (df != df.iloc[0]).any()]


#Lista os valores nulos
print(df.isna().sum())


#Acerta os valores nulos
df = df.dropna(subset=['listing.address.zone','listing.address.street'])


#Transforma o nulo do campo Type para Standard
df['type'] = df['type'].fillna('standard')

#A coluna listingFloors possui muitos casos nulo.
#Como nao pode ter casa sem piso, sera transformado em 1 quando nulo
df['listing.floors'] = df['listing.floors'].fillna(1)

#Vaga de estacionamento nula, deve ser sem vagas
df['listing.parkingSpaces'] = df['listing.parkingSpaces'].fillna(0)

#Valor de iptu nula, deve ser sem iptu
df['listing.pricingInfo.yearlyIptu'] = df['listing.pricingInfo.yearlyIptu'].fillna(0)

#Area total nula, vamos admitir que é o mesmo tamanho da area usavel
df['listing.totalAreas'] = df['listing.totalAreas'].fillna(df['listing.usableAreas'])

#CEP nulo, marcar com 99999 
df['listing.address.zipCode'] = df['listing.address.zipCode'].fillna(99999)


#Retira jacarepagua dos campos
df['listing.address.neighborhood'] = df['listing.address.neighborhood'].str.replace('Freguesia- Jacarepaguá', 'Freguesia')


#Cria nova coluna agrupando pelo tamanho m2
df['group.usableAreas'] = ['0 a 100' if x <= 100 else 
                           '101 a 150' if x > 100 and x <= 150 else
                           '151 a 200' if x > 150 and x <= 200 else
                           '201 a 250' if x > 200 and x <= 250 else
                           '251 a 300' if x > 250 and x <= 300 else
                           '301 a 350' if x > 300 and x <= 350 else
                           '351 a 400' if x > 350 and x <= 400 else
                           '401 a 450' if x > 400 and x <= 450 else
                           '451 a 500' if x > 450 and x <= 500 else
                           'acima 500' for x in df['listing.usableAreas']]


#Cria uma coluna com o CEP reduzido por bairro
#Preenche os nulos com 99999
df['Cep_Bairro'] = df['listing.address.zipCode'].str[:5]

#Casos para valor do condominio nulo, vamos assumir que é zero
df['listing.pricingInfo.monthlyCondoFee'] = df['listing.pricingInfo.monthlyCondoFee'].fillna(0)



#Gera o doc com o pandas profile
profile = ProfileReport(df, title='Pandas Profiling Report', correlations={"cramers": False})
profile.to_file('C:\Pessoal\Estudos\Scripts Python\Report.html')

############################ Fim Tratamento dos dados ############################


############################ Inicio Analise pelos graficos ############################

#Verificando a localização para ver se tem algo alem de jacarepagua
print(df['listing.address.neighborhood'].unique())

############################ Inicio WOrdcloud ############################
#Gera a nuvem de palavras em cima da coluna listing.amenities
#COnverte a coluna para texto puro e tira os nulos
vText = df['listing.amenities'].str.replace('|', ' ').dropna()

#Agrupa os textos de cada linha do dataframe em uma unica variavel string
vText = ' '.join(vText)

#Limpa os espacos duplos
vText = vText.replace('  ',' ')

#Gera a nuvem de palavras baseada na variavel da coluna
wordcloud = WordCloud(width=800, height=400, collocations=False).generate(vText)
plt.title('palavras mais comuns nos imoveis listados')
plt.imshow(wordcloud)
plt.axis('off')
plt.show()
############################ Fim da WOrdcloud ############################

#Usando paleta de cores
#colors = ["dusty purple", "windows blue", "amber", "faded green"]
#pal = sns.xkcd_palette(colors)


#Quantidade de tipos de imoveis disponiveis por localizacao
sns.countplot(x='listing.address.neighborhood', data=df, hue='imvl_type')
plt.title('Quantidade de tipos de imoveis por localização')
plt.xticks(rotation=30)
plt.show()

#Quantidade de tipos de imoveis disponiveis por localizacao
sns.countplot(x='imvl_type', data=df)
plt.title('Quantidade de tipos de imoveis por localização')
plt.show()

#Distribuicao dos valores de aluguel
sns.distplot(df['listing.pricingInfo.rentalPrice'], bins=100, kde = False)
plt.title('Valores de aluguel')
plt.show()

#Distribuicao dos tamanhos em m2
sns.distplot(df['listing.usableAreas'], bins=100, kde = False)
plt.title('Tamanhos em m2')
plt.show()

#Distribuicao por numeros de quartos
sns.distplot(df['listing.bedrooms'], bins=20, kde = False)
plt.title('Numeros de quartos')
plt.show()

#Distribuicao de valor de aluguel por quartos
sns.catplot(x='listing.bedrooms', y='listing.pricingInfo.rentalPrice', data=df)
plt.title('Valor do aluguel por quartos')
plt.show()

#Distribuicao de valor de aluguel por Banheiros
sns.catplot(x='listing.bathrooms', y='listing.pricingInfo.rentalPrice', data=df)
plt.title('Valor do aluguel por Banheiros')
plt.show()

#Imoveis com Piscina
sns.countplot(x='listing.pool', data=df, hue='group.usableAreas')
plt.title('Total de imoveis com Piscina e tamanho m2')
plt.show()

#Distribuicao de valor de aluguel por Tamanho tendo ou nao piscina
sns.catplot(x='group.usableAreas', y='listing.pricingInfo.rentalPrice', hue='listing.pool', data=df)
plt.title('Valor do aluguel por tamanho e piscina')
plt.show()

#Distribuicao de valor de aluguel por Tamanho tendo ou nao Churrasqueira
sns.catplot(x='group.usableAreas', y='listing.pricingInfo.rentalPrice', hue='listing.barbgrill', data=df)
plt.title('Valor do aluguel por tamanho e Churrasqueira')
plt.show()

#Imoveis com Churrasqueira
sns.countplot(x='listing.barbgrill', data=df, hue='group.usableAreas')
plt.title('Total de imoveis com Churrasqueira e tamanho m2')
plt.show()

#Distribuicao de valor de aluguel por Tamanho tendo ou nao Churrasqueira
sns.catplot(x='group.usableAreas', y='listing.pricingInfo.rentalPrice', hue='listing.barbgrill', data=df)
plt.title('Valor do aluguel por tamanho e churrasqueira')
plt.show()

#Casas com piscina e churrasqueira
df_PiscChurr = df.loc[(df['listing.barbgrill'] == 'True') & (df['listing.pool'] == 'True')]
sns.catplot(x='group.usableAreas', y='listing.pricingInfo.rentalPrice', hue='listing.barbgrill', data=df_PiscChurr)
plt.title('Valor do aluguel por tamanho com piscina e churrasqueira')
plt.show()


df_PiscChurr = df.loc[(df['listing.barbgrill'] == 'True') & (df['listing.bedrooms'] == 2)]
sns.catplot(x='group.usableAreas', y='listing.pricingInfo.rentalPrice', hue='listing.barbgrill', data=df_PiscChurr)
plt.title('Valor do aluguel por tamanho com piscina e churrasqueira')
plt.show()


############################ Fim Analise pelos graficos ############################






############################ Inicio Analise IA ############################

#Retirar colunas que nao serao usadas na analise
#Algumas colunas retiradas por conter muitos nulos como vlor IPTU
#Colunas com descricao retiradas
#Colunas com nome de Rua retirada, embora fosse interessante iria onerar muito o modelo.
#Colunas com data de criação e atualizacao do anuncio retiradas
#Colunas com valores Lat e Long retiradas

print(df.columns)

vCol = ['listing.unitSubTypes','listing.pricingInfo.salePrice','listing.pricingInfo.rentalTotalPrice','listing.amenities','account.logoUrl',
        'account.name','link.href','listing.updatedAt','listing.subtitle','listing.title','listing.portal','listing.createdAt',
        'listing.externalId','listing.advertiserId','listing.address.zipCode','listing.address.street','listing.address.point.lon','listing.address.point.lat',
        'listing.address.precision','listing.videoTour','listing.address.point.source','listing.address.country','listing.address.confidence']
#Drop das colunas
df.drop(columns=vCol, inplace=True)

#Verifica se ainda tem nulos
print(df.isna().sum())


#Verifica as colunas que possuem binario True ou False no texto
for i in df.columns:
    if (df[i] == 'True').any():
        print(i)

#Fazendo Binary encoder dos campos True False
df = df.replace('True',1)
df = df.replace('False',0)

#Passando essas colunas para categorical
df['listing.acceptExchange'] = df['listing.acceptExchange'].astype('category')
df['listing.backyard'] = df['listing.backyard'].astype('category')
df['listing.barbgrill'] = df['listing.barbgrill'].astype('category')
df['listing.furnished'] = df['listing.furnished'].astype('category')
df['listing.garden'] = df['listing.garden'].astype('category')
df['listing.guestpark'] = df['listing.guestpark'].astype('category')
df['listing.gym'] = df['listing.gym'].astype('category')
df['listing.partyhall'] = df['listing.partyhall'].astype('category')
df['listing.playground'] = df['listing.playground'].astype('category')
df['listing.pool'] = df['listing.pool'].astype('category')
df['listing.pricingInfo.isSale'] = df['listing.pricingInfo.isSale'].astype('category')
df['listing.sauna'] = df['listing.sauna'].astype('category')
df['listing.soundproofing'] = df['listing.soundproofing'].astype('category')
df['listing.sportcourt'] = df['listing.sportcourt'].astype('category')
df['listing.tenniscourt'] = df['listing.tenniscourt'].astype('category')


#Passando as colunas para categorical
df['imvl_type'] = df['imvl_type'].astype('category')
df['listing.address.level'] = df['listing.address.level'].astype('category')
df['listing.address.neighborhood'] = df['listing.address.neighborhood'].astype('category')
df['listing.address.zone'] = df['listing.address.zone'].astype('category')
df['listing.displayAddressType'] = df['listing.displayAddressType'].astype('category')
df['listing.bathrooms'] = df['listing.bathrooms'].astype('category')
df['listing.bedrooms'] = df['listing.bedrooms'].astype('category')
df['listing.floors'] = df['listing.floors'].astype('category')
df['listing.parkingSpaces'] = df['listing.parkingSpaces'].astype('category')
df['listing.pricingInfo.businessLabel'] = df['listing.pricingInfo.businessLabel'].astype('category')
df['listing.pricingInfo.businessType'] = df['listing.pricingInfo.businessType'].astype('category')
df['listing.publicationType'] = df['listing.publicationType'].astype('category')
df['listing.suites'] = df['listing.suites'].astype('category')
df['listing.unitTypes'] = df['listing.unitTypes'].astype('category')
df['group.usableAreas'] = df['group.usableAreas'].astype('category')
df['Cep_Bairro'] = df['Cep_Bairro'].astype('category')


#Fazendo Hot Encoder usando o Get_Dummies do Pandas
imvl_type = pd.get_dummies(df['imvl_type'], prefix='imvl_type')
list_adr_city = pd.get_dummies(df['listing.address.city'], prefix='list_adr_city')
list_adr_lvl = pd.get_dummies(df['listing.address.level'], prefix='list_adr_lvl')
list_adr_nbh = pd.get_dummies(df['listing.address.neighborhood'], prefix='list_adr_nbh')
list_adr_state = pd.get_dummies(df['listing.address.state'], prefix='list_adr_state')
list_adr_zone = pd.get_dummies(df['listing.address.zone'], prefix='list_adr_zone')
list_dspadr_type = pd.get_dummies(df['listing.displayAddressType'], prefix='list_dspadr_type')
list_bath = pd.get_dummies(df['listing.bathrooms'], prefix='list_bath')
list_bed = pd.get_dummies(df['listing.bedrooms'], prefix='list_bed')
list_floor = pd.get_dummies(df['listing.floors'], prefix='list_floor')
list_parkspace = pd.get_dummies(df['listing.parkingSpaces'], prefix='list_parkspace')
list_prcinfo_buslbl = pd.get_dummies(df['listing.pricingInfo.businessLabel'], prefix='list_prcinfo_buslbl')
list_prcinfo_bustype = pd.get_dummies(df['listing.pricingInfo.businessType'], prefix='list_prcinfo_bustype')
list_pubtype = pd.get_dummies(df['listing.publicationType'], prefix='list_pubtype')
list_suites = pd.get_dummies(df['listing.suites'], prefix='list_suites')
list_unitTypes = pd.get_dummies(df['listing.unitTypes'], prefix='list_unitTypes')
group_usableAreas = pd.get_dummies(df['group.usableAreas'], prefix='group_usableAreas')
Cep_Bairro = pd.get_dummies(df['Cep_Bairro'], prefix='Cep_Bairro')
Type = pd.get_dummies(df['type'], prefix='type')
list_type = pd.get_dummies(df['listing.listingType'], prefix='list_type')
list_proper_type = pd.get_dummies(df['listing.propertyType'], prefix='list_proper_type')
list_use_type = pd.get_dummies(df['listing.usageTypes'], prefix='list_use_type')


print(df.columns)
#Sepatando a variavel target
vTarget = df['listing.pricingInfo.rentalPrice']

#Criando o conjunto de dados sem a variavel Target
vDados = df.drop(columns='listing.pricingInfo.rentalPrice')

#Retirando as colunas que foram feitas Hot Encoding
#Cria a lista
vColDados = ['account.id','imvl_type', 'listing.address.level','listing.address.neighborhood','listing.address.zone','listing.displayAddressType',
             'listing.bathrooms','listing.bedrooms','listing.floors','listing.parkingSpaces','listing.pricingInfo.businessLabel',
             'listing.pricingInfo.businessType','listing.publicationType','listing.suites','listing.unitTypes',
             'group.usableAreas','Cep_Bairro','type','listing.listingType','listing.address.state','listing.address.city',
             'listing.businessTypeContext','listing.propertyType','listing.usageTypes','listing.pricingInfo.period']

#Dropa a partir da lista
vDados = vDados.drop(columns=vColDados)



#Concatena as variaveis de Hot Encoder no dataframe
#Cria a lista
vVarHE = [vDados,imvl_type,list_adr_lvl,list_adr_nbh,list_adr_zone,list_dspadr_type,list_bath,list_bed,list_floor,
          list_parkspace,list_prcinfo_buslbl,list_prcinfo_bustype,list_pubtype,list_suites,list_adr_state,
          list_unitTypes,group_usableAreas,Cep_Bairro,Type,list_type,list_proper_type,list_use_type]


#COntacatena a partir da lista
vDados = pd.concat(vVarHE, axis=1)

print(vDados.head())

#Separando os dados em teste e treino
X_train, x_test, Y_train, y_test = train_test_split(vDados, vTarget, test_size=0.2, random_state=2)

#Verifica se os shapes das variaveis estao corretos
print(X_train.shape)
print(Y_train.shape)
print(x_test.shape)
print(y_test.shape)

#Instancia a LR
reg = LinearRegression()

#Fit dos dados das variaveis
reg.fit(X_train, Y_train)
y_pred = reg.predict(x_test)

#Verificar o MAE
print("Mean Absolute Error: " + str(mean_absolute_error(y_pred, y_test)))


#Verifica a predicao
y_test = np.array(list(y_test))
y_pred = np.array(y_pred)
df_final = pd.DataFrame({'Actual': y_test.flatten(), 'Predicted': y_pred.flatten()})
print(df_final.head(10))



#Testa a predicao com os dados da minha casa




#Testando com Decision Tree
#Instancia a DecTree
reg = DecisionTreeRegressor()

#Fit dos dados das variaveis
reg.fit(X_train, Y_train)
y_pred = reg.predict(x_test)

#Verificar o MAE
print("Mean Absolute Error: " + str(mean_absolute_error(y_pred, y_test)))

#Verifica a predicao
y_test = np.array(list(y_test))
y_pred = np.array(y_pred)
df_final = pd.DataFrame({'Actual': y_test.flatten(), 'Predicted': y_pred.flatten()})
print(df_final)






