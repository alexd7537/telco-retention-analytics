"""Resumen editorial RETAIN. Solo presentacion; no es captura de Power BI."""
from pathlib import Path
import json
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
W,H=1440,900
INK='#251B36'; VIOLET='#6A43C2'; LIME='#CEF374'; PAPER='#F5F2FA'
MUTED='#756B83'; LINE='#DED6E8'; WHITE='#FFFFFF'; SOFT='#EAE2F6'
PALE='#C2B5D5'; ALT='#A65479'

def num(x,dec=0):return f'{x:,.{dec}f}'.replace(',','_').replace('.',',').replace('_','.')
def pct(x):return num(x*100,1)+' %'

def main():
    fontdir=Path('C:/Windows/Fonts')
    fonts={'Body':('calibri.ttf','Helvetica'),'Bold':('calibrib.ttf','Helvetica-Bold'),
           'Display':('georgia.ttf','Times-Roman'),'DisplayBold':('georgiab.ttf','Times-Bold')}
    from reportlab.pdfbase.pdfmetrics import Font
    for name,(filename,fallback) in fonts.items():
        if (fontdir/filename).exists():pdfmetrics.registerFont(TTFont(name,str(fontdir/filename)))
        else:pdfmetrics.registerFont(Font(name,fallback,'WinAnsiEncoding'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
    pdfmetrics.registerFontFamily('Display',normal='Display',bold='DisplayBold',italic='Display',boldItalic='DisplayBold')
    m=json.loads((ROOT/'analysis/metrics.json').read_text(encoding='utf-8'))
    q=json.loads((ROOT/'analysis/data_quality.json').read_text(encoding='utf-8'))
    contract=pd.read_csv(ROOT/'analysis/sql_results/02_contract.csv')
    tenure=pd.read_csv(ROOT/'analysis/sql_results/03_tenure.csv')
    factors=pd.read_csv(ROOT/'analysis/sql_results/04_factors.csv')
    segments=pd.read_csv(ROOT/'analysis/priority_segments.csv').sort_values('PriorityOrder')
    scenarios=pd.read_csv(ROOT/'analysis/scenarios.csv')
    s1=segments.loc[segments.SegmentID.eq('S1')].iloc[0]
    active_candidates=int(segments.loc[segments.PilotEligible.eq(1),'Active'].sum())
    output=ROOT/'reports/Resumen_ejecutivo_retencion.pdf'
    output.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(output),pagesize=(W,H),pageCompression=1)
    c.setTitle('RETAIN. - Estudio de abandono y retencion')
    c.setAuthor('Alexander Cordova | Caso de portafolio')
    def rect(x,y,w,h,fill):
        c.setFillColor(HexColor(fill));c.rect(x,H-y-h,w,h,stroke=0,fill=1)
    def rule(x,y,w,color=LINE):rect(x,y,w,1,color)
    def text(value,x,y,size=16,color=INK,bold=False,display=False):
        c.setFillColor(HexColor(color));c.setFont(('DisplayBold' if bold else 'Display') if display else ('Bold' if bold else 'Body'),size)
        c.drawString(x,H-y-size,value)
    def para(value,x,y,w,size=16,color=MUTED,display=False,leading=None):
        style=ParagraphStyle('p',fontName='Display' if display else 'Body',fontSize=size,leading=leading or size*1.32,textColor=HexColor(color))
        p=Paragraph(value,style);_,height=p.wrap(w,H)
        p.drawOn(c,x,H-y-height)
        return height
    def footer(n,dark=False):
        fg=PALE if dark else MUTED
        rule(48,848,1344,'#4C3C60' if dark else LINE)
        text('TELCO / RETAIN   |   Caso de portafolio   |   UM: moneda no especificada en el CSV',48,863,11,fg)
        text(f'0{n} / 05',1320,861,12,fg)
    def header(n,section,title,subtitle):
        rect(0,0,W,H,PAPER)
        text('RETAIN.',48,25,28,INK,display=True)
        text('ESTUDIO 02  /  CLIENTES Y RETENCIÓN',245,40,11,MUTED)
        text('ALEXANDER CORDOVA',1204,40,11,MUTED)
        rule(48,80,1344,INK)
        text(f'0{n}   /   {section}',48,107,11,VIOLET,True)
        text(title,48,137,38,INK,display=True)
        para(subtitle,48,192,1344,16,MUTED)
        footer(n)
    def stacked_bars(frame,label,x,y,w,row=82,dark=False,maxrate=.6,color=VIOLET):
        fg=WHITE if dark else INK;muted=PALE if dark else MUTED
        for i,r in enumerate(frame.itertuples(index=False)):
            yy=y+i*row
            labeltext=str(getattr(r,label)).replace('Un ano','Un año').replace('Dos anos','Dos años').replace('optica','óptica')
            text(labeltext,x,yy,16,fg)
            text(f'n = {num(r.Customers)}',x,yy+23,11,muted)
            text(pct(r.ChurnRate),x+w-76,yy,18,LIME if dark else color,True)
            rect(x,yy+46,w,8,'#4E3E63' if dark else LINE)
            rect(x,yy+46,w*r.ChurnRate/maxrate,8,LIME if dark else color)
    # 1. Portada editorial, con gran cifra y comparacion de contratos.
    rect(0,0,W,H,INK)
    text('RETAIN.',48,29,32,WHITE,display=True)
    text('TELCO  /  CUSTOMER ANALYTICS',252,44,12,PALE)
    text('PORTAFOLIO DE ALEXANDER CORDOVA',1080,44,11,PALE)
    rule(48,93,1344,'#4C3C60')
    text('ESTUDIO 02    /    ABANDONO Y RETENCIÓN',48,126,12,LIME,True)
    text('Entender la salida.',48,169,49,WHITE,display=True)
    text('Diseñar el siguiente paso.',48,229,49,WHITE,display=True)
    text(pct(m['ChurnRate']),48,307,106,LIME,display=True)
    text('TASA DE ABANDONO OBSERVADA',56,438,13,PALE,True)
    para('Una fotografía de la muestra, no una probabilidad de abandono futuro.',56,472,540,19,WHITE)
    text('El contrato cambia la lectura',821,143,24,WHITE,display=True)
    text('Tasas por grupo. Escala de barras: 0 % a 60 %.',821,182,13,PALE)
    stacked_bars(contract,'ContractLabel',821,228,550,row=99,dark=True)
    rule(48,560,1344,'#4C3C60')
    for xx,label,value,size in [(48,'CLIENTES ANALIZADOS',num(m['Customers']),32),
                               (422,'ABANDONOS OBSERVADOS',num(m['Churned']),32),
                               (821,'CARGOS MENSUALES DE ABANDONOS',num(m['MonthlyChargesChurned'],2)+' UM',29)]:
        text(label,xx,587,11,PALE,True);text(value,xx,613,size,WHITE,display=True)
    rect(0,689,W,151,LIME)
    text(pct(s1.ChurnRate),48,705,54,INK,display=True)
    text('EL FOCO INICIAL',353,712,12,INK,True)
    para(f'Contratos mensuales con hasta 6 meses: {num(s1.Churned)} abandonos de {num(s1.Customers)} clientes. '
         f'Quedan {num(s1.Active)} activos en ese segmento para evaluar una bienvenida reforzada.',353,739,1018,18,INK)
    text('Los cargos de abandonos son una suma descriptiva; no una pérdida contable ni un pronóstico.',48,817,11,INK)
    footer(1,True);c.showPage()
    # 2. Columnas editoriales en lugar de cuadricula de tarjetas.
    header(2,'EXPLORAR','Las diferencias necesitan contexto.',
        'Contrato, antigüedad y servicios pueden estar relacionados. Una asociación observada no identifica la causa del abandono.')
    left=48;middle=495;right=967
    text('01',left,265,28,VIOLET,display=True);text('Servicio de internet',left,312,23,INK,display=True)
    text('Abandonos / clientes de cada categoría.',left,351,13,MUTED)
    stacked_bars(factors[factors.Factor.eq('Internet')],'Category',left,402,393,row=104)
    rect(468,272,1,511,LINE)
    text('02',middle,265,28,VIOLET,display=True);text('Método de pago',middle,312,23,INK,display=True)
    text('Pago manual no equivale a causa.',middle,351,13,MUTED)
    pay=factors[factors.Factor.eq('Metodo de pago')].copy()
    pay['Category']=pay.Category.replace({'Transferencia automatica':'Transferencia automática','Tarjeta automatica':'Tarjeta automática','Cheque electronico':'Cheque electrónico'})
    stacked_bars(pay,'Category',middle,402,393,row=87,color=ALT)
    rect(943,264,449,521,INK)
    text('03 / COMPARAR DONDE APLICA',right,286,12,LIME,True)
    text('Soporte técnico',right,327,27,WHITE,display=True)
    para('Solo clientes con internet. No se mezcla ausencia de soporte con ausencia de internet.',right,375,400,15,PALE)
    stacked_bars(factors[factors.Factor.eq('Soporte (solo internet)')],'Category',right,455,400,row=106,dark=True)
    para('Investigar tickets, quejas y experiencia antes de proponer una solución.',right,690,395,19,WHITE,display=True)
    text('Todas las barras comparten una escala de 0 % a 60 %. Los tamaños de muestra se muestran junto a cada grupo.',48,810,13,MUTED)
    c.showPage()
    # 3. Segmentos: cifra lateral y matriz de decision.
    header(3,'PRIORIZAR','Un cliente. Un segmento. Una primera acción.',
        'Seis grupos excluyentes: la base incluye activos y abandonos; los candidatos a piloto son únicamente clientes activos de la muestra.')
    rect(48,269,256,308,LIME)
    text('ACTIVOS CANDIDATOS',68,296,12,INK,True)
    text(num(active_candidates),68,340,53,INK,display=True)
    para('En tres segmentos elegibles. La regla orienta un piloto; no predice quién se irá.',68,428,210,18,INK)
    text('La decisión, con volumen y tasa',337,267,24,INK,display=True)
    xcols=[337,596,693,797,918,1020,1190]
    headers=['SEGMENTO','CLIENTES','ABANDONOS','TASA','ACTIVOS','CARGOS ACTIVOS*','PRIORIDAD']
    rule(337,308,1055,INK)
    for xx,hd in zip(xcols,headers):text(hd,xx,321,10,MUTED,True)
    for i,r in enumerate(segments.itertuples(index=False)):
        yy=356+i*35
        if i<3:rect(329,yy-1,1063,33,SOFT)
        vals=[r.SegmentName.split(' | ')[1],num(r.Customers),num(r.Churned),pct(r.ChurnRate),num(r.Active),num(r.MonthlyChargesActive,2),r.PriorityLabel]
        for j,(xx,val) in enumerate(zip(xcols,vals)):text(val,xx,yy+5,12,VIOLET if j==6 and r.PilotEligible else INK,j==6)
        rule(337,yy+33,1055,LINE)
    text('* UM mensuales asociadas a activos; no ingreso en riesgo ni beneficio recuperable.',337,583,12,MUTED)
    actions=[('01','Bienvenida','Mensual, hasta 6 meses.','Comprobar instalación, explicar la factura y resolver fricciones tempranas.'),
             ('02','Experiencia técnica','Mensual, >6 meses, fibra sin soporte.','Revisar incidencias y probar soporte opcional; no asumir que todo es precio.'),
             ('03','Valor del plan','Mensual restante, cargo >=80 UM.','Revisar uso y adecuación de tarifa, sin ofrecer descuentos generales.')]
    rule(48,635,1344,INK)
    for i,(n,title,sub,body) in enumerate(actions):
        xx=48+i*462
        text(n,xx,657,28,VIOLET,display=True)
        text(title,xx+58,658,22,INK,display=True)
        text(sub,xx+58,697,13,MUTED)
        para(body,xx+58,731,356,15,INK)
    text('Elegibilidad: n >=100, activos >=50 y tasa mayor a la global. Orden por abandonos; desempate por cargos activos.',48,812,12,MUTED)
    c.showPage()
    # 4. Experimento: linea de proceso y sensibilidad.
    header(4,'VALIDAR','Probar primero. Escalar después.',
        'Propuesta de experimento, no campaña ejecutada. Empezar por la bienvenida mensual y comparar contra la atención habitual.')
    steps=[('1','Elegibilidad','Clientes activos de S1. Confirmar contacto, consentimiento y capacidad operativa.'),
           ('2','Asignación','Aleatorizar tratamiento y control. Calcular el tamaño necesario antes de lanzar.'),
           ('3','Intervención','Bienvenida y ayuda con instalación o factura; atención habitual en el control.'),
           ('4','Evaluación','Abandono a 30 días por intención de tratar; seguimiento adicional a 60/90 días.')]
    rule(73,300,1070,VIOLET)
    for i,(n,title,body) in enumerate(steps):
        xx=48+i*347
        rect(xx,277,46,46,LIME if i==0 else SOFT)
        text(n,xx+15,283,23,INK,display=True)
        text(title,xx,347,23,INK,display=True)
        para(body,xx,390,300,16,MUTED)
    rule(48,483,1344,INK)
    text('¿Qué cambiaría bajo distintos supuestos?',48,508,26,INK,display=True)
    text('S1: 200 contactos · 1 UM por contacto · horizonte de un mes',48,551,14,MUTED)
    xcols=[48,233,441,650]
    for xx,hd in zip(xcols,['MEJORA ABSOLUTA','CARGOS ASOCIADOS','COSTE CONTACTO','DIFERENCIA*']):text(hd,xx,594,11,MUTED,True)
    for i,r in enumerate(scenarios[scenarios.SegmentID.eq('S1')].itertuples(index=False)):
        yy=631+i*39
        vals=[num(r.AssumedIncrementalRetention*100,1)+' pp',num(r.IllustrativeGrossMonthlyCharges,2),num(r.IllustrativeContactCost,2),num(r.GrossLessContactCostOnly,2)]
        for j,(xx,val) in enumerate(zip(xcols,vals)):text(val,xx,yy,17,ALT if j==3 and r.GrossLessContactCostOnly<0 else INK,j==3)
        rule(48,yy+32,760)
    para('* Solo resta contacto: faltan costes de servicio, incentivos y margen. No es beneficio neto. pp = puntos porcentuales adicionales de retención frente al control.',48,770,760,12,MUTED)
    rect(857,508,535,311,INK)
    text('NO ES UNA PREVISIÓN',881,531,12,LIME,True)
    para('Para decidir hacen falta fechas reales, seguimiento, costes y un grupo de control.',881,575,483,26,WHITE,display=True)
    para('La tasa histórica de S1 no es su riesgo futuro a 30 días. Las mejoras de 1, 3 y 5 puntos son supuestos, no resultados logrados.',881,704,483,16,PALE)
    c.showPage()
    # 5. Controles y limites.
    header(5,'DOCUMENTAR','El criterio también forma parte del trabajo.',
        'Lo que se limpió, lo que se conservó y lo que todavía debe comprobarse antes de presentar el dashboard como validado.')
    text('01 / CONTROLES',48,270,12,VIOLET,True)
    text('Datos sin maquillaje.',48,308,30,INK,display=True)
    rows=[('Filas conservadas',f"{num(q['clean_rows'])} de {num(q['source_rows'])}"),
          ('Identificadores duplicados',str(q['duplicate_ids_case_insensitive'])),
          ('TotalCharges vacíos','11; todos con tenure = 0'),
          ('Tratamiento de vacíos','Nulo, sin imputar a cero'),
          ('Importes negativos','0'),('Integridad SQLite',q['sql_integrity'])]
    for i,(label,value) in enumerate(rows):
        yy=374+i*35
        text(label,48,yy,15,MUTED);text(value,349,yy,15,INK,True);rule(48,yy+29,607)
    rect(704,269,688,329,SOFT)
    text('02 / LÍMITES',732,292,12,VIOLET,True)
    para('Sin fechas, sin moneda definida,<br/>sin impacto comercial demostrado.',732,333,628,26,INK,display=True)
    para('No se pueden reconstruir cohortes ni tendencias con este CSV. No hay costes, margen ni resultados de campañas.<br/><br/>El análisis es descriptivo. El modelo predictivo queda para una ampliación posterior.',732,442,628,17,INK)
    rule(48,633,1344,INK)
    text('03 / ENTREGA',48,656,12,VIOLET,True)
    para('<b>Python + SQLite + SQL:</b> limpieza reproducible, consultas y controles.<br/>'
         '<b>Notebook y documentación:</b> exploración ejecutada en Python, diccionario y plan.',48,699,633,16,INK,leading=25)
    para('<b>Power BI:</b> tres páginas editables; prueba nativa de carga y visuales pendiente.<br/>'
         '<b>Este PDF:</b> resumen editorial, no captura de Power BI ni encargo de un cliente real.',732,699,660,16,INK,leading=25)
    link='https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv'
    c.linkURL(link,(48,H-830,1392,H-809),relative=0)
    text('Referencia: IBM / telco-customer-churn-on-icp4d   |   Archivo local y SHA-256: analysis/source_manifest.json',48,813,12,VIOLET)
    c.showPage();c.save()
    print(output)

if __name__=='__main__':main()
