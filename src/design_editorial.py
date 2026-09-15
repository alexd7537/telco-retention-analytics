"""Identidad editorial RETAIN: violeta/lima, navegacion superior y jerarquia asimetrica.
Solo presentacion; no cambia el modelo, sus medidas o los datos.
"""
import json
import uuid
from pathlib import Path

INK='#251B36'; VIOLET='#6A43C2'; LIME='#CEF374'; PAPER='#F5F2FA'
MUTED='#756B83'; LINE='#DED6E8'; WHITE='#FFFFFF'; SOFT='#EAE2F6'
PALE='#BDB0D2'; ALT='#A65479'
BODY='Calibri'; DISPLAY='Georgia'
PAGES=['Panorama','Factores','Prioridades']
WIDTH,HEIGHT=1440,900
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def lit(value):
    raw=str(value).lower() if isinstance(value,bool) else str(value)+'D' if isinstance(value,(int,float)) else "'"+value.replace("'","''")+"'"
    return {'expr':{'Literal':{'Value':raw}}}
def color(value):return {'solid':{'color':lit(value)}}
def encode(values):return {k:color(v) if isinstance(v,str) and v.startswith('#') else lit(v) for k,v in values.items()}
def obj(properties,selector=None):
    value={'properties':properties}
    if selector:value['selector']={'id':selector}
    return [value]
def field(table,column,measure=False):
    return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':column}}

def build_design(root,model,types):
    root=Path(root).resolve();report=root/'powerbi/TelcoRetention.Report';definition=report/'definition'
    existing=set((definition/'pages').glob('*/visuals/*/visual.json'))
    written=set();records=[]
    theme_name='TelcoRetain.json'
    theme={'$schema':'https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.157.json',
        'name':theme_name,'dataColors':[VIOLET,ALT,'#9E83D1','#766289','#BEAA63',INK],
        'background':WHITE,'foreground':INK,'foregroundNeutralSecondary':MUTED,'backgroundLight':LINE,'tableAccent':VIOLET,
        'textClasses':{'title':{'fontFace':BODY,'fontSize':13,'color':INK},'label':{'fontFace':BODY,'fontSize':11,'color':MUTED}},
        'visualStyles':{'*':{'*':{
            'title':[{'show':True,'fontFamily':BODY,'fontSize':13,'fontColor':{'solid':{'color':INK}}}],
            'background':[{'show':True,'color':{'solid':{'color':WHITE}},'transparency':0}],
            'border':[{'show':False,'radius':0}]}},
            'tableEx':{'*':{'columnHeaders':[{'fontColor':{'solid':{'color':INK}},'backColor':{'solid':{'color':SOFT}},'fontFamily':BODY,'fontSize':10,'bold':True,'autoSizeColumnWidth':True,'columnAdjustment':'growToFit'}],
                'values':[{'fontFamily':BODY,'fontSize':11,'fontColorPrimary':{'solid':{'color':INK}},'fontColorSecondary':{'solid':{'color':INK}},'backColorPrimary':{'solid':{'color':WHITE}},'backColorSecondary':{'solid':{'color':'#F8F5FC'}}}],
                'grid':[{'gridVertical':False,'gridHorizontal':False,'rowPadding':9}]}}}}
    write(report/'StaticResources/RegisteredResources'/theme_name,theme)
    write(definition/'report.json',{'$schema':SCHEMA+'report/3.0.0/schema.json',
        'themeCollection':{'customTheme':{'name':theme_name,'type':'RegisteredResources','reportVersionAtImport':{'visual':'2.4.0','report':'3.0.0','page':'2.0.0'}}},
        'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':theme_name,'path':theme_name,'type':'CustomTheme'}]}]})
    write(definition/'version.json',{'$schema':SCHEMA+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
    write(definition/'pages/pages.json',{'$schema':SCHEMA+'pagesMetadata/1.0.0/schema.json','pageOrder':PAGES,'activePageName':'Panorama'})
    def container(title='',bg=WHITE,padding=16):
        return {'title':obj(encode({'show':bool(title),'text':title,'fontSize':13,'fontFamily':BODY,'fontColor':INK})),
            'background':obj(encode({'show':bg is not None,'color':bg or WHITE,'transparency':0})),
            'border':obj(encode({'show':False,'radius':0})),
            'padding':obj(encode(dict.fromkeys(['top','bottom','left','right'],padding)))}
    def add(page,kind,key,x,y,w,h,roles=None,title='',objects=None,vco=None,sort=None):
        name=uuid.uuid5(uuid.NAMESPACE_URL,'telco-retain/'+page+'/'+key).hex[:20]
        v={'$schema':SCHEMA+'visualContainer/2.4.0/schema.json','name':name,
            'position':{'x':x,'y':y,'z':(len(records)+1)*1000,'width':w,'height':h,'tabOrder':(len(records)+1)*1000},
            'visual':{'visualType':kind,'visualContainerObjects':vco or container(title),'drillFilterOtherVisuals':True}}
        if objects:v['visual']['objects']=objects
        if roles:
            query={'queryState':{r:{'projections':[{'field':field(*f),'queryRef':f[0]+'.'+f[1],'nativeQueryRef':f[1]} for f in fs]} for r,fs in roles.items()}}
            if sort:query['sortDefinition']={'sort':[{'field':field(*sort[:3]),'direction':sort[3]}],'isDefaultSort':True}
            v['visual']['query']=query
        path=definition/f'pages/{page}/visuals/{name}/visual.json'
        write(path,v);written.add(path);records.append((page,key,v))
    def text(page,key,value,x,y,w,h,size=12,fg=MUTED,bold=False,bg=None,display=False):
        paragraphs=[{'textRuns':[{'value':line,'textStyle':{'fontFamily':DISPLAY if display else BODY,'fontSize':f'{size}px','color':fg,'fontWeight':'bold' if bold else 'normal'}}],'horizontalTextAlignment':'left'} for line in value.split('\n')]
        add(page,'textbox',key,x,y,w,h,objects={'general':obj({'paragraphs':paragraphs})},vco=container(bg=bg,padding=0))
    def nav(page,target,i):
        selected=page==target;fg=INK if selected else WHITE;bg=LIME if selected else INK
        styles={'text':encode({'show':True,'text':f'0{i+1}  {target}','fontSize':12,'fontColor':fg,'fontFamily':BODY,'horizontalAlignment':'center'}),
            'fill':encode({'show':True,'fillColor':bg,'transparency':0}),'outline':encode({'show':False})}
        objects={k:obj(v)+obj(v,'default') for k,v in styles.items()}
        objects['fill']+=obj(encode({'show':True,'fillColor':VIOLET,'transparency':0}),'hover')
        objects['text']+=obj(encode({'show':True,'text':f'0{i+1}  {target}','fontColor':WHITE,'fontFamily':BODY,'fontSize':12}),'hover')
        vco=container(bg=None,padding=0)
        vco['visualLink']=obj(encode({'show':True,'type':'PageNavigation','navigationSection':target,'tooltip':'Ir a '+target}))
        add(page,'actionButton','nav-'+target,908+164*i,15,156,42,objects=objects,vco=vco)
    headings={
        'Panorama':('La primera señal: quién se va.','Un retrato de clientes, contratos y cargos. Sin confundir la fotografía con una predicción.'),
        'Factores':('Leer las diferencias con contexto.','Explora las asociaciones; al pasar el cursor verás clientes y abandonos de cada grupo.'),
        'Prioridades':('Elegir dónde empezar.','De seis segmentos excluyentes a un piloto que se pueda medir con un grupo de control.')}
    for i,page in enumerate(PAGES):
        write(definition/f'pages/{page}/page.json',{'$schema':SCHEMA+'page/2.0.0/schema.json','name':page,'displayName':f'0{i+1} · {page}','displayOption':'FitToPage','width':WIDTH,'height':HEIGHT,
            'objects':{'background':obj(encode({'color':PAPER,'transparency':0})),'outspace':obj(encode({'color':LINE,'transparency':0}))}})
        text(page,'rail','',0,0,1440,72,bg=INK)
        text(page,'brand','RETAIN.',36,14,170,43,29,WHITE,display=True)
        text(page,'brand-sub','TELCO  /  CUSTOMER ANALYTICS',232,28,340,24,11,PALE)
        for j,target in enumerate(PAGES):nav(page,target,j)
        text(page,'chapter',f'ESTUDIO 02    /    {page.upper()}',36,93,720,20,11,VIOLET,True)
        text(page,'heading',headings[page][0],36,119,1350,49,34,INK,display=True)
        text(page,'subtitle',headings[page][1],36,174,1350,26,14,MUTED)
        for j,(label,t,col) in enumerate([('Contrato','Customers','ContractLabel'),('Antigüedad','Customers','TenureBand'),('Segmento','Segments','SegmentName')]):
            add(page,'slicer','filter-'+col,36+342*j,216,320,62,{'Values':[(t,col,False)]},objects={
                'data':obj(encode({'mode':'Dropdown'})),
                'header':obj(encode({'show':True,'text':label,'fontColor':MUTED,'fontFamily':BODY,'textSize':10})),
                'items':obj(encode({'fontColor':INK,'fontFamily':BODY,'textSize':11}))},vco=container(bg=WHITE,padding=6))
        text(page,'filter-scope','FILTROS DE ESTA PÁGINA\nSin fecha de corte · importes en UM',1075,222,329,51,11,MUTED)
        text(page,'footer-rule','',36,863,1368,1,bg=LINE)
        text(page,'footer','IBM Telco (referencia)   /   CSV aportado   /   UM: moneda no especificada   /   Asociación no implica causalidad',36,873,1280,21,10,MUTED)
    def card(page,metric,x,y,w,h,size=32,bg=WHITE,fg=INK,precision=0,label=None):
        objects={'value':obj(encode({'fontFamily':DISPLAY,'fontSize':size,'fontColor':fg,'labelDisplayUnits':1,'labelPrecision':precision,'horizontalAlignment':'left'}),'default'),
            'label':obj(encode({'show':True,'text':label or metric,'fontFamily':BODY,'fontSize':11,'fontColor':PALE if bg==INK else MUTED,'position':'aboveValue','horizontalAlignment':'left'}),'default'),
            'fillCustom':obj(encode({'show':True,'fillColor':bg,'transparency':0}),'default'),
            'outline':obj(encode({'show':False}),'default'),
            'layout':obj(encode({'paddingUniform':0,'backgroundShow':False}),'default'),
            'padding':obj(encode({'paddingUniform':8}),'default')}
        add(page,'cardVisual','kpi-'+metric,x,y,w,h,{'Data':[('Customers',metric,True)]},objects=objects,vco=container(bg=bg,padding=8))
    def chart(page,key,title,x,y,w,h,category,metric='Tasa de abandono',sort_category=False,accent=False,kind='barChart'):
        objects={'legend':obj(encode({'show':False})), 'dataPoint':obj({'defaultColor':color(ALT if accent else VIOLET)}),
            'categoryAxis':obj(encode({'showAxisTitle':False,'fontSize':11,'fontFamily':BODY,'labelColor':MUTED})),
            'valueAxis':obj(encode({'showAxisTitle':False,'fontSize':10,'fontFamily':BODY,'labelColor':MUTED,'gridlineShow':True,'gridlineColor':LINE}))}
        tooltip=['Clientes con internet','Abandonos con internet'] if metric=='Tasa con internet' else ['Clientes','Abandonos']
        add(page,kind,key,x,y,w,h,{'Category':[('Customers',category,False)],'Y':[('Customers',metric,True)],'Tooltips':[('Customers',m,True) for m in tooltip]},title,objects,
            sort=('Customers',category,False,'Ascending') if sort_category else ('Customers',metric,True,'Descending'))
    def table(page,key,title,fields,x,y,w,h):add(page,'tableEx',key,x,y,w,h,{'Values':fields},title)
    ms=lambda names:[('Customers',name,True) for name in names]
    # Panorama: un foco dominante; no fila de cuatro tarjetas equivalentes.
    text('Panorama','hero-bg','',36,306,376,282,bg=INK)
    card('Panorama','Tasa de abandono',55,324,336,141,58,INK,LIME,1,'ABANDONO OBSERVADO')
    card('Panorama','Clientes',55,482,155,86,25,INK,WHITE)
    card('Panorama','Abandonos',220,482,173,86,25,INK,WHITE)
    chart('Panorama','contract','01   /   Tasa por contrato',440,306,964,282,'ContractLabel',sort_category=True)
    chart('Panorama','tenure','02   /   Tasa por antigüedad',36,612,655,226,'TenureBand',sort_category=True,accent=True,kind='columnChart')
    table('Panorama','contract-detail','03   /   Volumen, duración y cargos',
        [('Customers','ContractLabel',False)]+ms(['Clientes','Abandonos','Antiguedad media','Cargos de abandonos']),719,612,685,226)
    text('Panorama','scope','Cargos de abandonos: suma de MonthlyCharges. No es pérdida contable ni riesgo futuro.',36,843,1368,18,10,MUTED)
    # Factores: bloque de comparaciones y foco de lectura a la derecha.
    chart('Factores','payment','01   /   Método de pago',36,306,674,253,'PaymentLabel')
    chart('Factores','internet','02   /   Servicio de internet',36,583,674,255,'InternetLabel')
    text('Factores','focus-bg','',738,306,666,532,bg=SOFT)
    text('Factores','focus-label','COMPARAR DONDE APLICA',762,323,615,24,12,VIOLET,True)
    chart('Factores','support','03   /   Soporte · solo clientes con internet',762,361,618,202,'SupportLabel','Tasa con internet',accent=True)
    chart('Factores','charge-band','04   /   Cargo mensual · cortes exploratorios',762,580,618,201,'ChargeBand',sort_category=True,kind='columnChart')
    text('Factores','confounding','Contrato, antigüedad y servicios están relacionados.\nEstas diferencias no aíslan un efecto causal.',762,793,618,41,11,MUTED)
    # Prioridades: columna de contexto y dos tablas anchas para decidir.
    text('Prioridades','priority-bg','',36,306,286,532,bg=INK)
    card('Prioridades','Candidatos activos',50,320,258,155,47,INK,LIME)
    card('Prioridades','Cargos de candidatos',50,490,258,93,24,INK,WHITE,2)
    card('Prioridades','Activos',50,592,258,93,29,INK,WHITE)
    card('Prioridades','Base global',50,697,258,93,29,INK,WHITE,1)
    text('Prioridades','candidate-note','Regla exploratoria, no predicción.',58,800,240,26,10,PALE)
    table('Prioridades','segment-detail','01   /   Seis segmentos excluyentes',
        [('Segments','SegmentName',False),('Segments','PriorityLabel',False)]+ms(['Clientes','Abandonos','Tasa de abandono','Activos','Cargos de activos']),350,306,1054,285)
    table('Prioridades','actions','02   /   Acciones a probar, no impactos demostrados',
        [('Segments','SegmentName',False),('Segments','Action',False)],350,615,1054,181)
    text('Prioridades','priority-note','Piloto: base >=100, activos >=50 y tasa mayor a la global. Orden por abandonos observados.\nLas métricas responden a filtros; la elegibilidad y el orden global no se recalculan.',366,806,1022,44,11,MUTED)
    lookup={t['name']:set(types[t['name']])|{m['name'] for m in t.get('measures',[])} for t in model['model']['tables']}
    for page,key,v in records:
        p=v['position']
        assert p['x']>=0 and p['y']>=0 and p['x']+p['width']<=WIDTH and p['y']+p['height']<=HEIGHT,(page,key)
        for role in v['visual'].get('query',{}).get('queryState',{}).values():
            for projection in role['projections']:
                f=next(iter(projection['field'].values()))
                assert f['Property'] in lookup[f['Expression']['SourceRef']['Entity']]
    # Quitar solo definiciones visuales obsoletas dentro del informe objetivo.
    # La primera sustitucion esta respaldada en work/proyecto_2_retencion/redesign/.
    removed=0
    for path in existing-written:
        absolute=path.resolve()
        if definition.resolve() not in absolute.parents or absolute.name!='visual.json':raise ValueError('Ruta de visual fuera del informe')
        absolute.unlink();removed+=1
        if not any(absolute.parent.iterdir()):absolute.parent.rmdir()
    write(root/'analysis/powerbi_validation.json',{'pages':3,'visuals':len(records),'tables':2,'relationships':1,
        'design':'Editorial violet / lime; horizontal navigation; asymmetrical hierarchy',
        'field_references':'passed','canvas_bounds':'passed','native_desktop_refresh':'not_executed','native_dax_execution':'not_executed','native_visual_review':'not_executed',
        'note':'PDF y PNG son un resumen editorial independiente, no capturas de Power BI.'})
    print(f'RETAIN editorial: {len(records)} visuales; {removed} definiciones obsoletas sustituidas. Modelo sin cambios en modo --design-only.')
