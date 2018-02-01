from urllib import request, parse
from datetime import datetime, timedelta
import re, requests, csv, time, sys, DataAccess
import logging, logging.config
from lxml import html

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simpleExample')

def get_page(url="http://devnovo.alianca.com.br"):
    req = request.urlopen(url)
    content = req.read()
    req.close()
    return content.decode('utf-8')

def get_links(url):
    """Faz scan no texto para encontrar URLs e retorna um conjunto de URLS"""

    text = get_page(url)
    links = set()
    padraoUrl = r"(https?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/[^<'\";]*)?)"

    matches = re.findall(padraoUrl, text)

    for match in matches:
        links.add(match[0])

    return links

def scrapeLogIn(*argv):
    """Realiza o scrape no log in da pagina inicial"""
       
    """Sessão iniciada e encarrega de fechá-la ao final com o with"""
    with requests.session() as session_request:

        try:
            url="https://pagseguro.uol.com.br/login.jhtml"
            urlPrefix = ['https://pagseguro.uol.com.br']

            "Início da requisição GET na página de log in"
            logger.info('requisicao GET na pagina de log in')
            result = session_request.get(url)
            tree = html.fromstring(result.text)

            "Payload com os parâmetros de entrada para o log in"
            payload = formatPayloadLogIn(argv[0], argv[1])
                   
            authenticity_token = list(set(tree.xpath("//input[@name='acsrfToken']/@value")))[0]
            skin = list(set(tree.xpath("//input[@name='skin']/@value")))[0]
            dest = list(set(tree.xpath("//input[@name='dest']/@value")))[0]
            payload['acsrfToken'] = authenticity_token
            payload['skin'] = skin
            payload['dest'] = dest
            
            logger.info('requisicao POST na pagina de log in')
            result = session_request.post(url, payload)

            """Requisição GET ao painel de extrato"""
            url2 = "https://pagseguro.uol.com.br/transaction/search.jhtml"
            logger.info('requisicao GET na pagina de extrato')
            result2 = session_request.get(url2)

            """ Payload com as datas e filtros"""
            logger.info('formatando payload com datas')
            payloadComDatas = formatPayload(argv[2], argv[3])
            
            "Codifica o payload para inserir na URL"
            logger.info('codificando payload com datas')
            params = parse.urlencode(payloadComDatas)
            url4 = "https://pagseguro.uol.com.br/transaction/find.jhtml"

            "Requisicao GET para exibir o extrato com as datas"
            logger.info('requisicao GET na pagina de transações')
            result4 = session_request.get(url4, params = params)

            "Requisicao GET para acessar o histórico gerado"
            logger.info('acessando o histórico com requisicao GET')
            url5 = "https://pagseguro.uol.com.br/transaction/hist.jhtml"
            result5 = session_request.get(url5)

            """Recupera o nome do primeiro arquivo gerado no histórico"""
            logger.info('recuperando arquivo gerado')
            urlFile = findFile(result5, urlPrefix)
    
            """Download do arquivo gerado no histórico"""
            logger.info('baixando arquivo gerado')
            data = session_request.get(urlFile)
    
            fileWriter(data)

            """Faz log out da página"""
            logger.info('realizando log out..')
            session_request.get("https://pagseguro.uol.com.br/logout.jhtml")
            time.sleep(5)
        except IndexError as error:
            logger.error(error)
            raise

def scrapeEstabelecimentos(*argv):
    """Realiza scrape para estabelecimentos no banco de dados ou pelos params"""
    if(argv):
        "Dados de um usuario do banco"
        codigo = argv[0]
        result = DataAccess.getById(str(codigo))
        user = result[0][0]
        passw = result[0][1]
        logger.info('usuario %s', user)
        scrapeLogIn(user, passw, argv[1], argv[2])

    else:
        estabs = DataAccess.getAll()
        for estab in estabs:
            user = estab[0]
            passw = estab[1]
            dataFrom = datetime.strftime(datetime.now() - timedelta(1), '%d/%m/%Y')
            logger.info('usuario %s - data %s', user, dataFrom)
            scrapeLogIn(user, passw, dataFrom, dataFrom)

def formatPayloadLogIn(*args):
    payload = {'user': '<USERNAME>', 
               'pass': '<PASSWORD>',
               'dest' : '',
               'skin' : '',
               'acsrfToken' : ''}

    payload['user'] = args[0]
    payload['pass'] = args[1]
    return payload

def formatPayload(*argv):
    payloadComDatas = {'page': '1', 'pageCmd' : '', 'exibirFiltro' : 'false', 'exibirHora' : 'false', 'interval' : '3', 
                               'dateFrom' : '', 'dateTo' : '', 'dateToInic' : '', 'timeFrom' : '00:00', 'timeTo' : '23:59',
                              'status' : '3', 'status' : '1', 'status' : '4', 'status' : '2', 'status' : '5', 'status' : '6', 
                              'paymentMethod' : '', 'type' : '', 'operationType' : 'T', 'selectedFilter' : 'all', 'filterText' : '', 'fileType' : ''}
    payloadComDatas['dateFrom'] = argv[0]
    payloadComDatas['dateTo'] = argv[1]
    payloadComDatas['dateToInic'] = argv[1] # Vem com o mesmo valor de data final
    return payloadComDatas

def findFile(page, urlPrefix):
    tree = html.fromstring(page.text)
    fileName = tree.xpath("//tr/@onclick")[0]
    if (not fileName):
        logger.error('Erro ao acessar arquivo de download')
        raise
    fileName = fileName[19:-1] #formata a posição do filename
    urlPrefix.append(fileName)
    return ''.join(urlPrefix)

"Escreve os dados na saída a partir do leitor csv"
def fileWriter(data):
    with open('out.csv', 'w') as f:
        writer = csv.writer(f)
        reader = csv.reader(data.text.splitlines())
        for row in reader:
            writer.writerow(row)


if __name__ == "__main__":
    if (len(sys.argv) == 4):
        scrapeEstabelecimentos(sys.argv[1], sys.argv[2], sys.argv[3])
    elif (len(sys.argv) <= 1):
        scrapeEstabelecimentos()
    else:
        raise Exception("Erro nos parametros")