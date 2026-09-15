# Diccionario de datos

Grano: un cliente por fila. Los 21 campos de la fuente conservan sus nombres. Los cargos se expresan en UM porque la copia recibida no especifica moneda. No se infiere país, fecha de corte ni periodo de facturación acumulada a partir del ID.

## Campos originales en Customers / customers

| Campo | Tipo limpio | Descripción / dominio |
|---|---|---|
| customerID | Texto, clave primaria | Identificador; no sumar ni convertir a número |
| gender | Texto categórico | Female / Male según fuente; descriptivo, no criterio de piloto |
| SeniorCitizen | Entero categórico | 0 / 1; no se infiere la edad exacta ni un umbral a partir del CSV |
| Partner | Texto categórico | Yes / No: pareja según fuente |
| Dependents | Texto categórico | Yes / No: dependientes según fuente |
| tenure | Entero | Antigüedad en meses; observada de 0 a 72 |
| PhoneService | Texto categórico | Yes / No: servicio telefónico |
| MultipleLines | Texto categórico | Yes / No / No phone service |
| InternetService | Texto categórico | DSL / Fiber optic / No |
| OnlineSecurity | Texto categórico | Yes / No / No internet service |
| OnlineBackup | Texto categórico | Yes / No / No internet service |
| DeviceProtection | Texto categórico | Yes / No / No internet service |
| TechSupport | Texto categórico | Yes / No / No internet service |
| StreamingTV | Texto categórico | Yes / No / No internet service |
| StreamingMovies | Texto categórico | Yes / No / No internet service |
| Contract | Texto categórico | Month-to-month / One year / Two year |
| PaperlessBilling | Texto categórico | Yes / No: facturación sin papel |
| PaymentMethod | Texto categórico | Electronic check / Mailed check / Bank transfer (automatic) / Credit card (automatic) |
| MonthlyCharges | Decimal no negativo | Cargo mensual; no confundir con ingreso acumulado o beneficio |
| TotalCharges | Decimal nullable | Cargo total según fuente; 11 vacíos conservados como nulos |
| Churn | Texto categórico | Yes / No: etiqueta de abandono observada |

`No internet service` y `No phone service` significan que el complemento no aplica por ausencia del servicio base; no son valores faltantes.

## Campos derivados

| Campo | Tipo | Regla |
|---|---|---|
| MonthlyChargesCents | Entero | MonthlyCharges ×100, conversión exacta con Decimal |
| TotalChargesCents | Entero nullable | TotalCharges ×100; nulo si no existe total |
| TotalChargesMissing | 0 / 1 | Indicador de total faltante |
| ChurnFlag | 0 / 1 | 1 si Churn=Yes; 0 si No |
| TenureBandOrder | Entero 1-5 | Orden de los cinco tramos de antigüedad |
| TenureBand | Texto | 0-6 / 7-12 / 13-24 / 25-48 / 49+ meses |
| ChargeBandOrder | Entero 1-3 | Orden de los tramos de cargo |
| ChargeBand | Texto | Bajo <35 / Medio >=35 y <80 / Alto >=80 UM |
| ServiceCount | Entero 0-9 | Teléfono + líneas extra + internet + seis complementos presentes |
| PaymentType | Texto | Automatico para transferencia/tarjeta automáticas; Manual para cheques |
| SegmentID | Texto S1-S6 | Segmento excluyente definido en metodología |
| ContractLabel | Texto | Etiqueta de lectura: Mensual / Un ano / Dos anos |
| ContractOrder | Entero 1-3 | Orden de presentación de contratos |
| InternetLabel | Texto | DSL / Fibra optica / Sin internet |
| SupportLabel | Texto | Con soporte / Sin soporte / No aplica |
| PaymentLabel | Texto | Etiqueta de lectura del método de pago |
| ChurnLabel | Texto | Abandono / Activo en la muestra |

El CSV limpio contiene 38 columnas: 21 de origen y 17 derivadas. Las etiquetas no cambian los valores originales de las columnas de fuente.

## Segments y resultados de segmentación

`data/processed/Segments.csv` es una dimensión de seis filas que importa Power BI. Su clave única es SegmentID. Contiene SegmentName, Rule, Action, PilotEligible, PriorityOrder y PriorityLabel. No contiene las métricas precalculadas para evitar tasas estáticas en el dashboard: estas se calculan con Customers y DAX.

`analysis/priority_segments.csv` y la tabla SQLite `segments` sí incluyen métricas de la muestra completa:

| Campo | Significado |
|---|---|
| Customers | Clientes totales del segmento |
| Churned | Clientes con abandono |
| Active | Clientes sin abandono observado |
| ChurnRate | Churned / Customers |
| MonthlyChargesChurned | Suma de cargos mensuales de abandonos del segmento |
| MonthlyChargesActive | Suma de cargos mensuales de activos del segmento |
| AvgMonthlyChargesActive | Media del cargo mensual de activos |
| PilotEligible | 1 si cumple umbrales de base/activos/tasa; 0 si no |
| PriorityOrder | Orden global exploratorio |
| PriorityLabel | Piloto 1/2/3 o Seguimiento |

## Otros archivos de análisis

- `metrics.json`: indicadores globales con precisión completa.
- `data_quality.json`: recuentos y controles de calidad.
- `source_manifest.json`: tamaño, SHA-256, referencia de fuente y versiones del entorno.
- `sql_results/`: resultado tabular de cada consulta SQL.
- `pilot_candidates.csv`: candidatos activos por regla; no lista de personas contactadas.
- `missing_total_charges.csv`: registros de total faltante para revisión.
- `scenarios.csv`: contactos, mejora supuesta, cargo medio, coste y resultado ilustrativo. Cada fila es un escenario alternativo, no una observación de campaña.
- `powerbi_validation.json`: pruebas estructurales y estado de validación nativa.

Los CSV usan coma como delimitador, punto decimal y UTF-8. Al abrirlos en una aplicación configurada en español, importar con esos ajustes si se muestran en una sola columna. Power BI ya declara cultura en-US para convertir los números.
