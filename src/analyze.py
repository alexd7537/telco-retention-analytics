"""Pipeline descriptivo reproducible. No modifica la fuente ni entrena predictores."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_COLUMNS = 'customerID gender SeniorCitizen Partner Dependents tenure PhoneService MultipleLines InternetService OnlineSecurity OnlineBackup DeviceProtection TechSupport StreamingTV StreamingMovies Contract PaperlessBilling PaymentMethod MonthlyCharges TotalCharges Churn'.split()
ADDONS = 'OnlineSecurity OnlineBackup DeviceProtection TechSupport StreamingTV StreamingMovies'.split()
SEGMENTS = {
    'S1': ('01 | Bienvenida mensual', 'Mensual y antiguedad de 0 a 6 meses.', 'Bienvenida y revision temprana de fricciones'),
    'S2': ('02 | Fibra sin soporte', 'Mensual, mas de 6 meses, fibra y sin soporte.', 'Diagnostico tecnico y oferta de soporte opcional'),
    'S3': ('03 | Revision de tarifa', 'Mensual restante con cargo mensual >= 80 UM.', 'Revisar adecuacion del plan y valor percibido'),
    'S4': ('04 | Mensual restante', 'Resto de contratos mensuales.', 'Seguimiento de experiencia y pago voluntario'),
    'S5': ('05 | Contrato anual', 'Contrato de un ano.', 'Recordatorio de renovacion y seguimiento'),
    'S6': ('06 | Contrato bianual', 'Contrato de dos anos.', 'Seguimiento de satisfaccion y renovacion'),
}

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def cents(value: str, allow_missing=False):
    value = str(value).strip()
    if not value and allow_missing:
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f'Importe no numerico: {value!r}') from error
    if not amount.is_finite() or amount < 0 or amount * 100 != (amount * 100).to_integral_value():
        raise ValueError(f'Importe negativo, no finito o con mas de dos decimales: {value}')
    return int(amount * 100)

def assign_segment(row):
    if row['Contract'] == 'One year': return 'S5'
    if row['Contract'] == 'Two year': return 'S6'
    if row['tenure'] <= 6: return 'S1'
    if row['InternetService'] == 'Fiber optic' and row['TechSupport'] == 'No': return 'S2'
    if row['MonthlyChargesCents'] >= 8000: return 'S3'
    return 'S4'

def clean(raw):
    if list(raw.columns) != ORIGINAL_COLUMNS:
        raise ValueError('El esquema del archivo no coincide con las 21 columnas esperadas.')
    d = raw.copy()
    for c in d: d[c] = d[c].str.strip()
    if d.customerID.eq('').any() or d.customerID.str.upper().duplicated().any():
        raise ValueError('ID vacio o duplicado (sin distinguir mayusculas): no se eliminan filas silenciosamente.')
    categories = {c: {'Yes', 'No'} for c in ['Partner','Dependents','PhoneService','PaperlessBilling','Churn']}
    categories.update({c: {'Yes','No','No internet service'} for c in ADDONS})
    categories.update({'gender': {'Female','Male'}, 'SeniorCitizen': {'0','1'},
        'MultipleLines': {'Yes','No','No phone service'}, 'InternetService': {'DSL','Fiber optic','No'},
        'Contract': {'Month-to-month','One year','Two year'},
        'PaymentMethod': {'Electronic check','Mailed check','Bank transfer (automatic)','Credit card (automatic)'}})
    for c, allowed in categories.items():
        unexpected = set(d[c]) - allowed
        if unexpected: raise ValueError(f'Categorias inesperadas en {c}: {unexpected}')
    tenure = pd.to_numeric(d.tenure, errors='raise')
    if ((tenure < 0) | (tenure % 1 != 0)).any(): raise ValueError('Antiguedad invalida')
    d['tenure'] = tenure.astype('int64')
    d['SeniorCitizen'] = d.SeniorCitizen.astype('int64')
    d['MonthlyChargesCents'] = d.MonthlyCharges.map(cents).astype('int64')
    d['TotalChargesCents'] = pd.array([cents(x, True) for x in d.TotalCharges], dtype='Int64')
    d['MonthlyCharges'] = d.MonthlyChargesCents / 100
    d['TotalCharges'] = d.TotalChargesCents.astype('Float64') / 100
    d['TotalChargesMissing'] = d.TotalCharges.isna().astype('int64')
    d['ChurnFlag'] = d.Churn.eq('Yes').astype('int64')
    for c in ADDONS:
        if not d[c].eq('No internet service').equals(d.InternetService.eq('No')):
            raise ValueError(f'Inconsistencia entre InternetService y {c}')
    if not d.MultipleLines.eq('No phone service').equals(d.PhoneService.eq('No')):
        raise ValueError('Inconsistencia de telefono y lineas adicionales')
    d['TenureBandOrder'] = d.tenure.map(lambda n: 1 if n<=6 else 2 if n<=12 else 3 if n<=24 else 4 if n<=48 else 5)
    d['TenureBand'] = d.TenureBandOrder.map({1:'0-6 meses',2:'7-12 meses',3:'13-24 meses',4:'25-48 meses',5:'49+ meses'})
    d['ChargeBandOrder'] = d.MonthlyChargesCents.map(lambda n: 1 if n<3500 else 2 if n<8000 else 3)
    d['ChargeBand'] = d.ChargeBandOrder.map({1:'Bajo: <35 UM',2:'Medio: 35 a <80 UM',3:'Alto: >=80 UM'})
    d['ServiceCount'] = (d.PhoneService.eq('Yes').astype(int) + d.MultipleLines.eq('Yes').astype(int)
        + d.InternetService.ne('No').astype(int) + d[ADDONS].eq('Yes').sum(axis=1))
    d['PaymentType'] = d.PaymentMethod.map(lambda x:'Automatico' if '(automatic)' in x else 'Manual')
    d['SegmentID'] = d.apply(assign_segment, axis=1)
    d['ContractLabel'] = d.Contract.map({'Month-to-month':'Mensual','One year':'Un ano','Two year':'Dos anos'})
    d['ContractOrder'] = d.Contract.map({'Month-to-month':1,'One year':2,'Two year':3})
    d['InternetLabel'] = d.InternetService.map({'DSL':'DSL','Fiber optic':'Fibra optica','No':'Sin internet'})
    d['SupportLabel'] = d.TechSupport.map({'Yes':'Con soporte','No':'Sin soporte','No internet service':'No aplica'})
    d['PaymentLabel'] = d.PaymentMethod.map({'Electronic check':'Cheque electronico','Mailed check':'Cheque por correo','Bank transfer (automatic)':'Transferencia automatica','Credit card (automatic)':'Tarjeta automatica'})
    d['ChurnLabel'] = d.Churn.map({'Yes':'Abandono','No':'Activo en la muestra'})
    # Orden estable: fuente primero, luego campos derivados. Identidad original preservada.
    return d[ORIGINAL_COLUMNS + [c for c in d if c not in ORIGINAL_COLUMNS]]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, default=ROOT/'data/raw/Telco-Customer-Churn.csv')
    args = parser.parse_args()
    source = args.raw.resolve()
    if not source.is_file(): raise FileNotFoundError(source)
    for p in ['data/processed','database','analysis/sql_results','reports','images','notebooks','powerbi']:
        (ROOT/p).mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(source, dtype=str, keep_default_na=False)
    d = clean(raw)
    d.to_csv(ROOT/'data/processed/Customers.csv', index=False, encoding='utf-8', float_format='%.2f')
    config = json.loads((ROOT/'config/scenarios.json').read_text(encoding='utf-8'))
    conn = sqlite3.connect(ROOT/'database/telco_retention.sqlite')
    conn.executescript((ROOT/'sql/00_schema.sql').read_text(encoding='utf-8'))
    # Reemplaza solo tablas derivadas de este proyecto al regenerar; la fuente no se toca.
    with conn:
        conn.execute('DELETE FROM customers')
        names = ','.join('"'+c+'"' for c in d.columns)
        values = [tuple(None if pd.isna(v) else v for v in row) for row in d.itertuples(index=False, name=None)]
        conn.executemany(f'INSERT INTO customers ({names}) VALUES ({",".join("?" for _ in d.columns)})', values)
    overview = pd.read_sql_query((ROOT/'sql/01_overview.sql').read_text(encoding='utf-8'), conn).iloc[0].to_dict()
    for k in ['Customers','Churned','Active','MissingTotalCharges']: overview[k] = int(overview[k])
    seg = pd.read_sql_query((ROOT/'sql/06_segments.sql').read_text(encoding='utf-8'), conn)
    seg['SegmentName'] = seg.SegmentID.map(lambda x: SEGMENTS[x][0])
    seg['Rule'] = seg.SegmentID.map(lambda x: SEGMENTS[x][1])
    seg['Action'] = seg.SegmentID.map(lambda x: SEGMENTS[x][2])
    seg['PilotEligible'] = ((seg.Customers>=config['minimum_segment_customers']) & (seg.Active>=config['minimum_active_customers']) & (seg.ChurnRate>overview['ChurnRate'])).astype(int)
    ranking = seg.sort_values(['PilotEligible','Churned','MonthlyChargesActive','SegmentID'], ascending=[False,False,False,True]).SegmentID.tolist()
    seg['PriorityOrder'] = seg.SegmentID.map({s:i+1 for i,s in enumerate(ranking)})
    seg['PriorityLabel'] = seg.apply(lambda r:f"Piloto {r.PriorityOrder}" if r.PilotEligible else 'Seguimiento', axis=1)
    seg.to_sql('segments', conn, if_exists='replace', index=False)
    conn.execute('CREATE UNIQUE INDEX idx_segment_id ON segments(SegmentID)')
    seg.to_csv(ROOT/'analysis/priority_segments.csv', index=False, float_format='%.6f')
    seg[['SegmentID','SegmentName','Rule','Action','PilotEligible','PriorityOrder','PriorityLabel']].to_csv(ROOT/'data/processed/Segments.csv', index=False)
    results = {}
    for sql in sorted((ROOT/'sql').glob('*.sql')):
        if sql.name.startswith('00_'): continue
        result = pd.read_sql_query(sql.read_text(encoding='utf-8'), conn)
        result.to_csv(ROOT/'analysis/sql_results'/f'{sql.stem}.csv', index=False, float_format='%.6f')
        results[sql.stem] = len(result)
    candidates = pd.read_sql_query((ROOT/'sql/07_campaign_candidates.sql').read_text(encoding='utf-8'), conn)
    candidates.to_csv(ROOT/'analysis/pilot_candidates.csv', index=False, float_format='%.2f')
    scenarios = []
    for row in seg[seg.PilotEligible.eq(1)].sort_values('PriorityOrder').itertuples():
        targets = min(int(config['campaign_target_cap']), row.Active)
        for uplift in config['incremental_retention_assumptions']:
            gross = targets * uplift * row.AvgMonthlyChargesActive
            cost = targets * config['cost_per_contact_um']
            scenarios.append({'SegmentID':row.SegmentID,'SegmentName':row.SegmentName,'Targets':targets,
                'AssumedIncrementalRetention':uplift,'AvgMonthlyChargeActive':row.AvgMonthlyChargesActive,
                'IllustrativeGrossMonthlyCharges':gross,'IllustrativeContactCost':cost,
                'GrossLessContactCostOnly':gross-cost,'Label':'Simulacion; no beneficio neto ni impacto demostrado'})
    pd.DataFrame(scenarios).to_csv(ROOT/'analysis/scenarios.csv', index=False, float_format='%.6f')
    nulls = d[d.TotalChargesMissing.eq(1)][['customerID','tenure','MonthlyCharges','TotalChargesMissing']]
    nulls.to_csv(ROOT/'analysis/missing_total_charges.csv', index=False)
    quality = {
        'source_rows':len(raw), 'source_columns':len(raw.columns), 'clean_rows':len(d),
        'duplicate_ids_case_insensitive':int(d.customerID.str.upper().duplicated().sum()),
        'missing_total_charges':int(d.TotalChargesMissing.sum()),
        'missing_totals_with_nonzero_tenure':int((d.TotalCharges.isna() & d.tenure.ne(0)).sum()),
        'zero_tenure_customers':int(d.tenure.eq(0).sum()), 'negative_monthly_charges':int(d.MonthlyCharges.lt(0).sum()),
        'zero_monthly_charges':int(d.MonthlyCharges.eq(0).sum()),
        'total_less_than_monthly_nonmissing':int((d.TotalCharges<d.MonthlyCharges).fillna(False).sum()),
        'max_tenure_months':int(d.tenure.max()), 'monthly_min':float(d.MonthlyCharges.min()),
        'monthly_max':float(d.MonthlyCharges.max()), 'total_charges_imputed':False,
        'rows_removed':0, 'sql_integrity':conn.execute('PRAGMA integrity_check').fetchone()[0],
        'sql_query_rows':results,
        'notes':['Los totales menores al cargo mensual se conservan: sin historial de facturacion no se prueba un error.',
                 'No se exige TotalCharges = tenure * MonthlyCharges: los cargos pueden variar.']}
    assert seg.Customers.sum()==len(d) and seg.Churned.sum()==d.ChurnFlag.sum()
    assert candidates.customerID.is_unique
    assert set(candidates.customerID).issubset(set(d.loc[d.ChurnFlag.eq(0),'customerID']))
    assert overview['MonthlyChargesChurned'] == int(d.loc[d.ChurnFlag.eq(1),'MonthlyChargesCents'].sum())/100
    save_json(ROOT/'analysis/metrics.json', overview)
    save_json(ROOT/'analysis/data_quality.json', quality)
    save_json(ROOT/'analysis/source_manifest.json', {'filename':source.name,
        'sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes':source.stat().st_size,
        'reference_url':'https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv',
        'source_note':'Archivo aportado por el usuario. Referencia de esquema: IBM. No se verifico identidad byte a byte con la copia remota.',
        'currency':'UM: unidad monetaria no especificada en el archivo',
        'temporal_scope':'Sin fecha de corte ni fechas individuales en el CSV; Churn es la etiqueta observada.',
        'python':platform.python_version(), 'pandas':pd.__version__, 'sqlite':sqlite3.sqlite_version})
    conn.commit(); conn.close()
    print(json.dumps(overview, ensure_ascii=False, indent=2))
    print(seg[['SegmentName','Customers','ChurnRate','Active','PriorityLabel']].to_string(index=False))
    print(f'Candidatos operativos (no prediccion): {len(candidates)}')

if __name__ == '__main__': main()
