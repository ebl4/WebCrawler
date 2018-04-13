from urllib import request, parse
from datetime import datetime, timedelta
import mercadopago, re, requests, csv, json, time, sys, DataAccess
import logging, logging.config
from lxml import html
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read('simple.ini')

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simpleExample')


class MPago(object):
    __codigo_cliente = None
    __begin_date = None
    __end_date = None
    __client_id = None
    __client_secret = None
    __refoEstabelecimento = None

    def __init__(self, *args):
        "Inicializando atributos da classe com os argumentos de entrada e chamada de procedimento"
        if (len(sys.argv) == 3):
            self.__codigo_cliente = args[0]
            self.__begin_date = args[1]
            self.__end_date = args[2]
            self.scrapePorCliente()
        elif (len(sys.argv) <= 1):
            self.__begin_date = self.__end_date = datetime.strftime(datetime.now() - timedelta(20), '%Y-%m-%dT%H:%M:%SZ')
            self.scrapeTodosClientes()
        else:
            raise Exception("Erro nos parametros")

    def scrapeLogIn(self, *argv):
        """Realiza o scrape no log in da pagina inicial"""

        access_token = self.get_acess_token(self.__client_id, self.__client_secret)

        urlPrefix = parser.get('MercadoPago', 'urlPrefix')
    
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        headersHist = {'accept': 'application/json'}
        url = ''.join((parser.get('MercadoPago', 'urlToken'), access_token))
        params = json.dumps({"begin_date": self.__begin_date,"end_date": self.__end_date})
        data = {'access_token':access_token}


        with requests.session() as session_req:
            response = session_req.post(url, data=params, headers=headers) # O sistema do MercadoPago leva um tempo para gerar o relatório
            resp = session_req.get(''.join((urlPrefix, "list")), headers=headersHist, data=data)
        
            """Download do arquivo"""
            if(resp.status_code is 200):
                jsonText = json.loads(resp.text)
                dateFrom = datetime.strptime(self.__begin_date, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d')
                filePrefix = ''.join(("MercadoPago_",''.join((str(self.__refoEstabelecimento), dateFrom))))
                fileName = jsonText[0]['file_name']
                path = ''.join((parser.get('MercadoPago', 'PathRecebimentoAdquirente'), ''.join((filePrefix, fileName))))
            
                urlSufix = ''.join((''.join((fileName, "?access_token=")), access_token))
                url = ''.join((urlPrefix, urlSufix))
                downloadResponse = session_req.get(url)
                if(downloadResponse.status_code is 200):
                    self.fileWriter(downloadResponse, path)
                else:
                    logger.error("Erro na geração do relatório")
                    raise


    def get_acess_token(self, clientId, clientSecret):
        mp = mercadopago.MP(clientId, clientSecret)
        accessToken = mp.get_access_token()
        return accessToken

    def index(req, **kwargs):
        mp = get_acess_token()
        paymentInfo = mp.get_payment (kwargs["id"])
    
        if paymentInfo["status"] == 200:
            return json.dumps(paymentInfo, indent=4)
        else:
            return None

    def BuscaPagamentos(req, **kwargs):
        filters = {
            "id": None,
            "site_id": None,
            "external_reference": None
        }
        searchResult = mp.search_payment(filters)
        return json.dumps(searchResult, indent=4)

    def scrapePorCliente(self):
        """Realiza scrape para um cliente específico"""
        result = DataAccess.getById(str(self.__codigo_cliente))
        if(not result):
            logger.error("usuário não encontrado")
            raise
        self.__client_id = result[0][0]
        self.__client_secret = result[0][1]
        self.__refoEstabelecimento = result[0][2]
        logger.info('usuario %s', self.__client_id)
        self.scrapeLogIn()

    def scrapeTodosClientes(self):
        estabs = DataAccess.getAll()
        for estab in estabs:
            self.__client_id = estab[0]
            self.__client_secret = estab[1]
            self.__refoEstabelecimento = estab[2]
            logger.info('usuario %s - data %s', self.__client_id, self.__begin_date)
            self.scrapeLogIn()

    """Escreve os dados na saída a partir do leitor csv"""
    def fileWriter(self, data, name):
        with open('%s' % name, 'w') as f:
            writer = csv.writer(f)
            reader = csv.reader(data.text.splitlines())
            for row in reader:
                writer.writerow(row)

if __name__ == "__main__": 
    MPago()