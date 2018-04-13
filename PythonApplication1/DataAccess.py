import pyodbc
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read('simple.ini')

def connection():
    connectionString = "Driver=%s;Server=%s;Database=%s;Trusted_Connection=%s;" % \
                          (parser.get('connection', 'Driver'), parser.get('connection', 'Server'), \
                          parser.get('connection', 'Database'), \
                          parser.get('connection', 'Trusted_Connection'))
                          
    return pyodbc.connect(connectionString)

def getById(refoPr_estab):
    result = []
    cnxn = connection()

    cursor = cnxn.cursor()
    cursor.execute("""SELECT  rpm.RPM_USER,
        rpm.RPM_PASSWD,
        refop.REFOPR_ESTABELECIMENTO
		FROM    dbo.REFOPR_PAGAR_ME AS rpm
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA_PR AS refop ON refop.REFOPR_ID = rpm.REFOPR_ID
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA AS refo ON refo.REFO_ID = refop.REFO_ID
		JOIN    dbo.CAD_EMPRESA_FILIAL AS cef ON cef.CEF_ID = refo.CEF_ID
		WHERE   cef.CEF_ATIVO = 1
		AND     refop.REFOPR_ATIVO = 1
		AND     refop.CO_ID = 43
		AND		refop.REFOPR_ESTABELECIMENTO = ?;""", str(refoPr_estab))

    for row in cursor:
        result.append(row)

    return result

def getAll():
    result = []
    cnxn = connection()

    cursor = cnxn.cursor()
    cursor.execute("""SELECT  rpm.RPM_USER,
        rpm.RPM_PASSWD,
        refop.REFOPR_ESTABELECIMENTO
		FROM    dbo.REFOPR_PAGAR_ME AS rpm
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA_PR AS refop ON refop.REFOPR_ID = rpm.REFOPR_ID
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA AS refo ON refo.REFO_ID = refop.REFO_ID
		JOIN    dbo.CAD_EMPRESA_FILIAL AS cef ON cef.CEF_ID = refo.CEF_ID
		WHERE   cef.CEF_ATIVO = 1
		AND     refop.REFOPR_ATIVO = 1
		AND     refop.CO_ID = 43;""")

    for row in cursor:
        result.append(row)

    return result


def getAllWithAuth(co_id):
    result = []
    cnxn = connection()

    cursor = cnxn.cursor()
    cursor.execute("""SELECT refop.REFOPR_ESTABELECIMENTO,
        refop.REFOPR_AUTORIZACAO
		FROM    dbo.REL_EMPRESA_FILIAL_OPERADORA_PR AS refop
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA AS refo ON refo.REFO_ID = refop.REFO_ID
		JOIN    dbo.CAD_EMPRESA_FILIAL AS cef ON cef.CEF_ID = refo.CEF_ID
		WHERE   cef.CEF_ATIVO = 1
		AND     refop.REFOPR_ATIVO = 1
		AND     refop.CO_ID = ?;""", co_id)
        

    for row in cursor:
        result.append(row)

    return result

def getCoId(op):
    result = []
    cnxn = connection()

    cursor = cnxn.cursor()
    cursor.execute("""SELECT [CO_ID] from [DEV_CONCILIADORA].[dbo].[CAD_OPERADORA] WHERE [CO_DESCRICAO] = ? ;""", str(op))

    for row in cursor:
        result.append(row)

    return result


