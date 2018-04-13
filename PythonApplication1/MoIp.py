from urllib import request, parse
from datetime import datetime, timedelta
import re, requests, json, time, sys, DataAccess
import logging, logging.config
from lxml import html
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read('simple.ini')

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('simpleExample')

class Moip(object):
    __begin_date = None
    __end_date = None
    __access_token = None
    __refoEstabelecimento = None

    def __init__(self, *args):
        "Inicializando atributos da classe com os argumentos de entrada e chamada de procedimento"
        if (len(sys.argv) == 3):
            self.__refoEstabelecimento = args[0]
            self.__begin_date = args[1]
            self.__end_date = args[2]
            self.scrapePorCliente()
        elif (len(sys.argv) <= 1):
            self.__begin_date = "2017-03-01T14:20:54.00Z"
            self.__end_date = "2017-03-25T13:08.00Z"
            self.scrapeTodosClientes()
        else:
            raise Exception("Erro nos parametros")

    def scrapeLogIn(self, *argv):
        """Realiza o scrape no log in da pagina inicial"""

        headers = {'content-type': 'application/json', 'Authorization':''.join(('OAuth ', self.__access_token))}
        urlOrdem = parser.get('Moip', 'urlOrdens')
        dataInterval = ''.join((''.join((self.__begin_date, ",")), self.__end_date))
        filters = ''.join((''.join(("?filters=createdAt::bt(", dataInterval)), ")"))

        with requests.session() as session_req:
            #response = session_req.post(url, data=filters, headers=headers) 
            resp = session_req.get(''.join((urlOrdem[:-1], filters)), headers=headers)
        
            """Obtendo as ordens no período indicado. Download do arquivo"""
            if(resp.status_code is 200):
                jsonText = json.loads(resp.text)
                dateFrom = datetime.strptime(self.__begin_date, '%Y-%m-%dT%H:%M:%S.00Z').strftime('%Y%m%d')
                filePrefix = ''.join(("Moip_",''.join((str(self.__refoEstabelecimento), dateFrom))))
                resultPayments = []

                for ordem in jsonText['orders']:
                    urlSufix = ''.join((ordem["id"],"/payments"))
                    payments = session_req.get(''.join((urlOrdem, urlSufix)), headers=headers)
                    path = ''.join((parser.get('Moip', 'PathRecebimentoAdquirente'), filePrefix))
                    if(payments.status_code is 200):
                        resultPayments.append(json.loads(payments.text))
                    else:
                        logger.error("Erro na geração do relatório")
                self.fileWriter(resultPayments, path)

    """Realiza scrape para estabelecimentos no banco de dados"""
    def scrapeTodosClientes(self):
        co_id = DataAccess.getCoId('Moip')
        estabs = DataAccess.getAllWithAuth(co_id[0][0])
        for estab in estabs:
            self.__refoEstabelecimento = estab[0]
            self.__access_token = estab[1]
            logger.info('estabelecimento %s - data %s', self.__refoEstabelecimento, self.__begin_date)
            self.scrapeLogIn()


    """Escreve os dados na saída a partir do leitor json"""
    def fileWriter(self, data, name):
        with open('%s.json' % name, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__": 
    Moip()