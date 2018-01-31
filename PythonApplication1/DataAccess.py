import pyodbc

def connection():
    return pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                          "Server=SQL2012;"
                          "Database=DEV_CONCILIADORA;"
                          "Trusted_Connection=yes;")

def getById(refoPr_id):
    result = []
    cnxn = connection()

    cursor = cnxn.cursor()
    cursor.execute("""SELECT  rpm.RPM_USER,
        rpm.RPM_PASSWD
		FROM    dbo.REFOPR_PAGAR_ME AS rpm
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA_PR AS refop ON refop.REFOPR_ID = rpm.REFOPR_ID
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA AS refo ON refo.REFO_ID = refop.REFO_ID
		JOIN    dbo.CAD_EMPRESA_FILIAL AS cef ON cef.CEF_ID = refo.CEF_ID
		WHERE   cef.CEF_ATIVO = 1
		AND     refop.REFOPR_ATIVO = 1
		AND     refop.CO_ID = 35
		AND		refop.REFOPR_ESTABELECIMENTO = ?;""", str(refoPr_id))

    for row in cursor:
        result.append(row)

    return result

def getAll():
    result = []
    cnxn = connection()

    cursor = cnxn.cursor()
    cursor.execute("""SELECT  rpm.RPM_USER,
        rpm.RPM_PASSWD
		FROM    dbo.REFOPR_PAGAR_ME AS rpm
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA_PR AS refop ON refop.REFOPR_ID = rpm.REFOPR_ID
		JOIN    dbo.REL_EMPRESA_FILIAL_OPERADORA AS refo ON refo.REFO_ID = refop.REFO_ID
		JOIN    dbo.CAD_EMPRESA_FILIAL AS cef ON cef.CEF_ID = refo.CEF_ID
		WHERE   cef.CEF_ATIVO = 1
		AND     refop.REFOPR_ATIVO = 1
		AND     refop.CO_ID = 35;""")

    for row in cursor:
        result.append(row)

    return result

