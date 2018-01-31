from urllib import request, parse
from datetime import date
import re, requests, csv, time, sys, DataAccess
from lxml import html
from selenium import webdriver

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


def file_download(url):
    csv = request.urlopen(url).read()
    with open('file.csv', 'wb') as f:
        f.write(csv)       

def scrapeLogIn(*argv):
    """Realiza o scrape no log in da pagina inicial"""

    """Payload com os parâmetros de entrada para o log in"""
    payload = {'user': '<USERNAME>', 
               'pass': '<PASSWORD>',
               'dest' : 'REDIR|https://pagseguro.uol.com.br/hub.jhtml',
               'skin' : 'ps',
               'acsrfToken' : ''}

    payload['user'] = argv[0]
    payload['pass'] = argv[1]
    """Sessão iniciada e encarrega de fechá-la ao final com o with"""
    with requests.session() as session_request:
        url="https://pagseguro.uol.com.br/login.jhtml"
        urlPrefix = ['https://pagseguro.uol.com.br']

        "Início da requisição GET na página de log in"
        result = session_request.get(url)
        tree = html.fromstring(result.text)
                   
        authenticity_token = list(set(tree.xpath("//input[@name='acsrfToken']/@value")))[0]
        payload['acsrfToken'] = authenticity_token

        result = session_request.post(url, payload)

        """Requisição GET ao painel de extrato"""
        url2 = "https://pagseguro.uol.com.br/transaction/search.jhtml"
        result2 = session_request.get(url2)

        """ Payload com as datas e filtros"""
        payloadComDatas = {'page': '1', 'pageCmd' : '', 'exibirFiltro' : 'false', 'exibirHora' : 'false', 'interval' : '3', 
                           'dateFrom' : '', 'dateTo' : '', 'dateToInic' : '', 'timeFrom' : '00:00', 'timeTo' : '23:59',
                          'status' : '3', 'status' : '1', 'status' : '4', 'status' : '2', 'status' : '5', 'status' : '6', 
                          'paymentMethod' : '', 'type' : '', 'operationType' : 'T', 'selectedFilter' : 'all', 'filterText' : '', 'fileType' : ''}
        payloadComDatas['dateFrom'] = argv[2]
        payloadComDatas['dateTo'] = argv[3]
        payloadComDatas['dateToInic'] = argv[3] # Vem com o mesmo valor de data final

        "Codifica o payload para inserir na URL"
        params = parse.urlencode(payloadComDatas)
        url4 = "https://pagseguro.uol.com.br/transaction/find.jhtml"

        "Requisicao GET para exibir o extrato com as datas"
        result4 = session_request.get(url4, params = params)

        "Requisicao GET para acessar o histórico gerado"
        url5 = "https://pagseguro.uol.com.br/transaction/hist.jhtml"
        result5 = session_request.get(url5)

        """Recupera o nome do primeiro arquivo gerado no histórico"""
        tree = html.fromstring(result5.text)
        fileName = tree.xpath("//tr/@onclick")[0]
        fileName = fileName[19:-1] #formata a posição do filename
        urlPrefix.append(fileName)
        urlFile = ''.join(urlPrefix)
    
        """Download do arquivo gerado no histórico"""
        data = session_request.get(urlFile)
    
        "Escreve os dados na saída a partir do leitor csv"
        with open('out.csv', 'w') as f:
            writer = csv.writer(f)
            reader = csv.reader(data.text.splitlines())
            for row in reader:
                writer.writerow(row)

        """Faz log out da página"""
        session_request.get("https://pagseguro.uol.com.br/logout.jhtml")
        time.sleep(5)

def scrapeEstabelecimentos(*argv):
    """Realiza scrape para cada estabelecimento no banco de dados"""
    if(argv):
        "Dados de um usuario do banco"
        codigo = '1234567890'
        result = DataAccess.getById(codigo)[0]
        user = result[0]
        passw = result[1]
        scrapeLogIn(user, passw, argv[2], argv[3])

    else:
        estabs = DataAccess.getAll()
        for estab in estabs:
            user = estab[0]
            passw = estab[1]
            today = date.today()
            dataFrom = date(today.year, today.month, today.day-1)
            args = [user, passw, dataFrom, dataFrom]
            scrapeLogIn(args)

def fileReading():
    result = ""
    with open('dict_payload', 'r') as f:
        s = f.read()
        result = ast.literal_eval(s)
    return result

if __name__ == "__main__":
    scrapeEstabelecimentos()

    #if (sys.argv):
    #    scrapeEstabelecimentos(sys.argv)
    #else:
    #    scrapeEstabelecimentos()