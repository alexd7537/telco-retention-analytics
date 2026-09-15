"""Genera TELCO / RETAIN: PBIP editable, modelo y tres paginas PBIR nativas.
La carga y el render nativo requieren validacion posterior en Power BI Desktop.
"""
from pathlib import Path
import csv
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'powerbi'
DATA = ROOT/'data/processed'
BASE = 'https://developer.microsoft.com/json-schemas/fabric/'
MONEY = '#,##0.00 "UM"'
MEASURES = [
    ('Clientes', 'COUNTROWS(Customers)', '#,##0', 'Clientes incluidos en el contexto de filtro.'),
    ('Abandonos', 'SUM(Customers[ChurnFlag])', '#,##0', 'Registros Churn=Yes; no bajas futuras.'),
    ('Activos', 'CALCULATE([Clientes], KEEPFILTERS(Customers[ChurnFlag] = 0))', '#,##0', 'Activos segun la etiqueta de esta muestra.'),
    ('Tasa de abandono', 'DIVIDE([Abandonos], [Clientes])', '0.0%', 'Abandonos / clientes en el mismo contexto. No tasa temporal de cohortes.'),
    ('Cargos de abandonos', 'DIVIDE(CALCULATE(SUM(Customers[MonthlyChargesCents]), KEEPFILTERS(Customers[ChurnFlag] = 1)), 100)', MONEY, 'Suma de cargos mensuales de clientes que abandonaron. No ingreso futuro en riesgo ni perdida contable.'),
    ('Cargos de activos', 'DIVIDE(CALCULATE(SUM(Customers[MonthlyChargesCents]), KEEPFILTERS(Customers[ChurnFlag] = 0)), 100)', MONEY, 'Cargos mensuales asociados a clientes activos en la muestra.'),
    ('Antiguedad media', 'AVERAGE(Customers[tenure])', '0.0 "meses"', 'Promedio de antiguedad observada.'),
    ('Cargo mensual medio', 'DIVIDE(SUM(Customers[MonthlyChargesCents]), [Clientes] * 100)', MONEY, 'Promedio de cargo mensual, no ingreso acumulado.'),
    ('Clientes con internet', 'CALCULATE([Clientes], KEEPFILTERS(Customers[InternetService] <> "No"))', '#,##0', 'Excluye clientes sin internet para comparar soporte.'),
    ('Abandonos con internet', 'CALCULATE([Abandonos], KEEPFILTERS(Customers[InternetService] <> "No"))', '#,##0', 'Numerador de la tasa de soporte.'),
    ('Tasa con internet', 'DIVIDE([Abandonos con internet], [Clientes con internet])', '0.0%', 'Solo clientes con internet: No aplica no se confunde con Sin soporte.'),
    ('Candidatos activos', 'CALCULATE([Activos], KEEPFILTERS(Segments[PilotEligible] = 1))', '#,##0', 'Activos de segmentos elegibles; regla exploratoria, no prediccion individual.'),
    ('Cargos de candidatos', 'CALCULATE([Cargos de activos], KEEPFILTERS(Segments[PilotEligible] = 1))', MONEY, 'Volumen de cargos asociado a candidatos; NO monto que se vaya a perder.'),
    ('Base global', 'CALCULATE([Tasa de abandono], REMOVEFILTERS(Customers), REMOVEFILTERS(Segments))', '0.0%', 'Referencia de toda la muestra, ignora filtros.'),
    ('Totales faltantes', 'SUM(Customers[TotalChargesMissing])', '#,##0', 'TotalCharges vacio en la fuente, conservado como nulo.'),
    ('Nota de base', 'IF([Clientes] < 100, "Base pequena", "Base >= 100")', '', 'Umbral descriptivo de lectura, no prueba de significancia.'),
]

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    import sys
    if '--design-only' in sys.argv:
        model=json.loads((OUT/'TelcoRetention.SemanticModel/model.bim').read_text(encoding='utf-8'))
        types={t['name']:{c['name']:c['dataType'] for c in t['columns']} for t in model['model']['tables']}
        from design_editorial import build_design
        build_design(ROOT, model, types)
        return
    # Tipos explicitos: no se infieren claves numericas o cargos segun configuracion regional.
    integer = {'SeniorCitizen','tenure','ChurnFlag','MonthlyChargesCents','TotalChargesCents','TotalChargesMissing','TenureBandOrder','ChargeBandOrder','ServiceCount','ContractOrder','PilotEligible','PriorityOrder'}
    types = {}
    for name in ['Customers','Segments']:
        with (DATA/f'{name}.csv').open(encoding='utf-8', newline='') as stream: columns=next(csv.reader(stream))
        types[name]={c: 'int64' if c in integer else 'decimal' if c in ['MonthlyCharges','TotalCharges'] else 'string' for c in columns}
    tables=[]
    for name, columns in types.items():
        mtypes={'int64':'Int64.Type','decimal':'Currency.Type','string':'type text'}
        pairs=', '.join('{"'+c+'", '+mtypes[t]+'}' for c,t in columns.items())
        expression=['let', f'    Source = Csv.Document(File.Contents(DataFolder & "/{name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
            '    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),']
        if name=='Customers': expression+=['    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, {"TotalCharges", "TotalChargesCents"}),']
        expression += [f'    Typed = Table.TransformColumnTypes({"Nulls" if name=="Customers" else "Headers"}, {{{pairs}}}, "en-US")','in','    Typed']
        cols=[]
        hidden=integer-{'ServiceCount','tenure','SeniorCitizen'}
        for c,t in columns.items():
            col={'name':c,'dataType':t,'sourceColumn':c,'summarizeBy':'none','lineageTag':str(uuid.uuid5(uuid.NAMESPACE_URL,'telco/'+name+'/'+c))}
            if c in hidden or c=='SegmentID': col['isHidden']=True
            if t=='decimal': col['formatString']=MONEY
            if c in {'customerID','SegmentID'}: col['description']='Identificador de texto; no agregar. Unico en Customers para customerID y en Segments para SegmentID.'
            sort={'TenureBand':'TenureBandOrder','ChargeBand':'ChargeBandOrder','ContractLabel':'ContractOrder','SegmentName':'PriorityOrder','PriorityLabel':'PriorityOrder'}
            # PriorityLabel=Seguimiento corresponde a varias posiciones, por eso no se ordena por columna.
            if c in sort and c!='PriorityLabel': col['sortByColumn']=sort[c]
            cols.append(col)
        table={'name':name,'lineageTag':str(uuid.uuid5(uuid.NAMESPACE_URL,'telco/'+name)), 'columns':cols,
            'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':expression}}]}
        if name=='Customers': table['measures']=[{'name':n,'expression':e,'formatString':fmt,'description':desc,'displayFolder':'Retencion'} for n,e,fmt,desc in MEASURES]
        tables.append(table)
    model={'name':'TelcoRetention','compatibilityLevel':1567,'model':{'culture':'es-ES','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-US','tables':tables,
        'relationships':[{'name':'customers_segments','fromTable':'Customers','fromColumn':'SegmentID','toTable':'Segments','toColumn':'SegmentID','fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'}],
        'expressions':[{'name':'DataFolder','kind':'m','expression':f'"{DATA.as_posix()}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}],
        'annotations':[{'name':'PBI_QueryOrder','value':json.dumps(['DataFolder','Customers','Segments'])}]}}
    write(OUT/'TelcoRetention.SemanticModel/model.bim', model)
    write(OUT/'TelcoRetention.SemanticModel/definition.pbism', {'$schema':BASE+'item/semanticModel/definitionProperties/1.0.0/schema.json','version':'1.0','settings':{'qnaEnabled':False}})
    write(OUT/'TelcoRetention.pbip', {'$schema':BASE+'pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'TelcoRetention.Report'}}],'settings':{'enableAutoRecovery':True}})
    report=OUT/'TelcoRetention.Report'; definition=report/'definition'
    write(report/'definition.pbir', {'$schema':BASE+'item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../TelcoRetention.SemanticModel'}}})
    (OUT/'Medidas.dax').write_text('\n\n'.join('// '+desc+'\n'+n+' =\n'+e for n,e,_,desc in MEASURES), encoding='utf-8')
    from design_editorial import build_design
    build_design(ROOT, model, types)

if __name__=='__main__': main()
