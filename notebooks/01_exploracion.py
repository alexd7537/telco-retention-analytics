# %% [markdown]
# # TELCO / RETAIN: de la base a una decisión
# Caso de portafolio de análisis de abandono. Una fila representa un cliente;
# Churn es la etiqueta observada, no una probabilidad. Esta primera versión
# no entrena modelos predictivos ni estima efectos causales.
#
# El notebook se entrega con salidas ejecutadas mediante Python en un proceso
# local. Se puede volver a ejecutar en Jupyter con pandas instalado.
# %%
from pathlib import Path
import sys
import sqlite3
import json
import pandas as pd

locations = [Path.cwd(), *Path.cwd().parents]
ROOT = next((p for p in locations if (p/'data/raw/Telco-Customer-Churn.csv').is_file()), None)
if ROOT is None:
    ROOT = next((p/'outputs/proyecto_2_retencion' for p in locations
                 if (p/'outputs/proyecto_2_retencion/data/raw/Telco-Customer-Churn.csv').is_file()), None)
if ROOT is None:
    raise FileNotFoundError('Abre el notebook desde la carpeta del proyecto.')
sys.path.insert(0, str(ROOT/'src'))
from analyze import clean
raw = pd.read_csv(ROOT/'data/raw/Telco-Customer-Churn.csv', dtype=str, keep_default_na=False)
print('Dimensiones de la fuente:', raw.shape)
print('Columnas:', ', '.join(raw.columns))
# %% [markdown]
# ## 1. Auditar antes de transformar
# Los espacios de TotalCharges no equivalen a cero. Se inspeccionan los
# registros y se preservan todos los clientes. Las categorías estructurales
# 'No internet service' y 'No phone service' no significan lo mismo que 'No'.
# %%
blank_totals = raw.TotalCharges.str.strip().eq('')
print('IDs duplicados sin distinguir mayúsculas:', raw.customerID.str.upper().duplicated().sum())
print('Totales vacíos:', blank_totals.sum())
print(raw.loc[blank_totals, ['tenure', 'Churn']].value_counts().to_string())
print('\nCategorías estructurales de soporte:')
print(raw.TechSupport.value_counts().to_string())
# %% [markdown]
# ## 2. Limpiar sin alterar la fuente
# clean() valida el esquema y las categorías, convierte importes con Decimal,
# mantiene los nulos y crea los campos de análisis. Los centavos enteros
# permiten conciliar importes sin errores de representación binaria.
# %%
customers = clean(raw)
assert len(customers) == len(raw)
assert customers.customerID.is_unique
assert customers.TotalCharges.isna().sum() == blank_totals.sum()
print(customers[['tenure','MonthlyCharges','TotalCharges']].describe().round(2).to_string())
print('\nTramos de antigüedad:')
print(customers.TenureBand.value_counts().to_string())
# %% [markdown]
# ## 3. Definir el denominador
# La tasa descriptiva es clientes con Churn=Yes / todos los clientes del
# contexto. No existe una fecha de corte en este archivo para reconstruir
# una tasa mensual comparable entre periodos.
# %%
total = len(customers)
churned = int(customers.ChurnFlag.sum())
rate = churned / total
charges_churned = customers.loc[customers.ChurnFlag.eq(1), 'MonthlyChargesCents'].sum() / 100
print(f'Clientes: {total:,}; abandonos: {churned:,}; tasa: {rate:.2%}')
print(f'Cargos mensuales asociados a abandonos: {charges_churned:,.2f} UM')
print('Esta suma no es una pérdida contable ni ingreso futuro en riesgo.')
# %% [markdown]
# ## 4. Consultar una base real en SQLite
# La base se abre en modo de solo lectura. Cada consulta vive en sql/ y su
# resultado también se entrega como CSV. Así otra persona puede auditarlo.
# %%
connection = sqlite3.connect((ROOT/'database/telco_retention.sqlite').as_uri() + '?mode=ro', uri=True)
def query(filename):
    return pd.read_sql_query((ROOT/'sql'/filename).read_text(encoding='utf-8'), connection)
overview = query('01_overview.sql').iloc[0]
assert int(overview.Customers) == total
assert int(overview.Churned) == churned
assert abs(overview.MonthlyChargesChurned - charges_churned) < 0.000001
print(query('02_contract.sql').round(4).to_string(index=False))
print('\nAntigüedad:')
print(query('03_tenure.sql').round(4).to_string(index=False))
# %% [markdown]
# ## 5. Factores asociados y comparación válida
# El soporte se compara solo entre clientes con internet. Ver más abandono
# sin soporte no demuestra que ofrecer soporte evitará ese abandono.
# Contrato y antigüedad pueden explicar parte de la diferencia.
# %%
factors = query('04_factors.sql')
print(factors[factors.Factor.isin(['Internet','Soporte (solo internet)','Metodo de pago'])].round(4).to_string(index=False))
print('\nSoporte dentro de cada contrato (también descriptivo):')
print(query('10_support_within_contract.sql').round(4).to_string(index=False))
# %% [markdown]
# ## 6. Cruces, importe y tamaño de muestra
# Los cruces pequeños no deben liderar un ranking por una tasa extrema.
# Los tramos de cargos (<35, 35 a <80 y >=80 UM) son cortes exploratorios
# documentados, no umbrales validados del negocio.
# %%
print(query('05_contract_tenure.sql').round(4).to_string(index=False))
print('\nDistribución por tramo de cargo y abandono:')
print(query('08_charges.sql').round(2).to_string(index=False))
# %% [markdown]
# ## 7. Seis segmentos excluyentes
# En contratos mensuales se aplica una jerarquía: primero <=6 meses;
# luego fibra sin soporte; luego cargo >=80 UM; finalmente el resto.
# Los contratos anual y bianual forman otros dos grupos. Un cliente
# pertenece a un solo segmento. Los datos demográficos no deciden elegibilidad.
# %%
segments = pd.read_csv(ROOT/'analysis/priority_segments.csv')
assert int(segments.Customers.sum()) == total
assert int(segments.Churned.sum()) == churned
print(segments[['SegmentName','Customers','Churned','ChurnRate','Active','PriorityLabel']].round(4).to_string(index=False))
print('\nReglas:')
print(segments[['SegmentID','Rule']].to_string(index=False))
# %% [markdown]
# ## 8. Candidatos activos, no probabilidades de abandono
# La elegibilidad de piloto exige base >=100, activos >=50 y tasa observada
# superior a la global. El orden usa abandonos observados. Es una heurística
# exploratoria que debe validarse; no es un modelo predictivo.
# %%
candidates = query('07_campaign_candidates.sql')
assert candidates.customerID.is_unique
assert set(candidates.customerID).issubset(set(customers.loc[customers.ChurnFlag.eq(0),'customerID']))
print('Clientes activos candidatos:', len(candidates))
print(candidates.groupby('SegmentName').size().to_string())
print('\nLos IDs son del dataset de muestra. No hay datos de contacto ni campaña enviada.')
# %% [markdown]
# ## 9. Sensibilidad: supuestos separados de resultados
# Contactos x mejora incremental supuesta x cargo mensual medio del segmento.
# La diferencia resta solo coste de contacto: no es beneficio neto, pues faltan
# margen, coste de servicio e incentivos. El tamaño 200 es ilustrativo,
# no un cálculo de potencia estadística.
# %%
scenarios = pd.read_csv(ROOT/'analysis/scenarios.csv')
print(scenarios[scenarios.SegmentID.eq('S1')].round(2).to_string(index=False))
connection.close()
# %% [markdown]
# ## 10. Recomendación y siguiente validación
# Empezar por un piloto de bienvenida en clientes mensuales nuevos, con
# asignación aleatoria y control, previa verificación de consentimiento y
# capacidad. Recoger fechas y resultados a 30/60/90 días. Separar efectos
# medidos de asociaciones de esta muestra. Antes de entrenar un modelo,
# definir horizonte, disponibilidad temporal de variables y validación.
#
# Fuente de referencia: [IBM Telco Customer Churn](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv).
# La copia utilizada es la aportada por el usuario, identificada por SHA-256
# en analysis/source_manifest.json; no se comprobó identidad con el remoto.
