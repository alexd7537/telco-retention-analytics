# Metodología y límites

## Pregunta y unidad de análisis

Una fila por cliente. Objetivo: describir el abandono de la muestra y proponer segmentos para una intervención que deberá validarse. `Churn=Yes` define el abandono observado; `Churn=No` se denomina activo **en esta muestra**, no necesariamente activo hoy.

No hay fechas individuales, fecha de corte, historial de cargos ni resultados de campañas. Por ello no se construyen tendencias mensuales, cohortes temporales, valor de vida del cliente, supervivencia, rentabilidad o causalidad. Aunque el campo `MonthlyCharges` sea mensual, la tasa calculada no se presenta como una serie de tasas mensuales.

## Fuente y conservación

Se analiza la copia aportada por el usuario. El archivo raw se conserva byte a byte y se registra su SHA-256. No se eliminan filas; no se reemplaza la fuente. Datos y resultados permanecen locales.

## Transformaciones

1. Exigir exactamente las 21 columnas originales y su orden. Cambios de esquema detienen el proceso.
2. Recortar espacios exteriores; conservar el texto del ID. Validar unicidad sin distinguir mayúsculas, también por compatibilidad con Power BI.
3. Validar dominios cerrados de categorías. Una categoría nueva provoca un error explícito, no una recodificación silenciosa.
4. Convertir `tenure` a entero no negativo. Tratar `SeniorCitizen` como categoría binaria, aunque su almacenamiento sea entero.
5. Convertir cargos mediante `Decimal`; rechazar negativos, valores no finitos y más de dos decimales. Generar enteros de centavos para conciliación.
6. Reemplazar únicamente `TotalCharges` vacío por nulo. Los 11 casos tienen antigüedad cero, pero no se asume que el cargo total sea cero.
7. Validar que `No internet service` coincida con ausencia de internet en los seis complementos; que `No phone service` coincida con ausencia de teléfono.
8. Crear campos derivados y etiquetas de lectura. No sobreescribir el significado de las categorías originales.

No se exige `TotalCharges = tenure × MonthlyCharges`: un cargo mensual actual no reconstruye toda la historia. Tampoco se eliminan valores altos automáticamente como outliers.

## Campos derivados

- `ChurnFlag`: 1 si Churn=Yes, 0 si No.
- `TenureBand`: 0-6, 7-12, 13-24, 25-48, 49 o más meses. Incluye tenure=0 en el primer grupo.
- `ChargeBand`: bajo <35 UM; medio >=35 y <80 UM; alto >=80 UM. Son cortes exploratorios fijos para facilitar lectura, no segmentos tarifarios validados.
- `ServiceCount`: suma de teléfono, líneas adicionales, internet (DSL o fibra cuenta una sola vez), seguridad, backup, protección de dispositivo, soporte, TV y películas. Rango teórico 0-9. Las categorías no aplicables aportan 0. No representa cantidad de dispositivos, uso o rentabilidad.
- `PaymentType`: automático para transferencia o tarjeta automáticas; manual para los dos tipos de cheque. No se infiere morosidad.
- `TotalChargesMissing`: 1 cuando falta el total; nunca confundir con importe cero.

## Indicadores

| Nombre | Definición | Precaución |
|---|---|---|
| Clientes | Número de filas del contexto | Un ID por fila |
| Abandonos | Suma de ChurnFlag | Etiqueta observada |
| Tasa de abandono | Abandonos / Clientes | El denominador cambia con el filtro |
| Activos | Clientes con ChurnFlag=0 | Activos en la muestra |
| Cargos de abandonos | Suma de MonthlyChargesCents de ChurnFlag=1 / 100 | No pérdida contable ni riesgo futuro |
| Cargos de activos | Suma equivalente de ChurnFlag=0 | No beneficio o margen |
| Antigüedad media | Media de tenure | No tiempo esperado hasta abandono |
| Tasa con internet | Abandonos con internet / clientes con internet | Para comparar soporte donde aplica |
| Base global | Tasa del conjunto completo | En Power BI ignora filtros |
| Candidatos activos | Activos en segmentos elegibles | Heurística, no probabilidad individual |

La tasa global se calcula con conteos, **no como promedio simple de tasas de segmentos**. Los importes SQL se suman en centavos. Los CSV de resultados muestran hasta seis decimales; SQLite y las medidas se calculan desde los datos de clientes, no desde tasas redondeadas.

## Segmentación excluyente

Para contratos mensuales, aplicar en este orden:

1. S1: tenure <=6.
2. S2: resto mensual, fibra y TechSupport=No.
3. S3: resto mensual con MonthlyCharges >=80 UM.
4. S4: resto mensual.
5. S5: todos los contratos de un año.
6. S6: todos los contratos de dos años.

Así un cliente nuevo de fibra con cargo alto solo cae en S1. La suma de clientes, activos y abandonos de los seis segmentos coincide con el total.

Elegibilidad de piloto: >=100 clientes, >=50 activos y tasa superior a la global. Los elegibles se ordenan por número de abandonos observado, con desempate por cargos de activos y SegmentID. Los umbrales se configuran en `config/scenarios.json` y son una decisión exploratoria, no un contraste estadístico.

La prioridad se fija al construir los segmentos con toda la muestra. Los filtros de Power BI recalculan métricas, pero no ese orden ni la elegibilidad. No se usan género, SeniorCitizen, pareja o dependientes para seleccionar candidatos.

## Arquitectura

```text
CSV raw -> Python validado -> Customers.csv + Segments.csv -> Power BI
                         -> SQLite -> consultas SQL -> análisis y conciliación
                                                    -> notebook y PDF
```

Power BI importa CSV, no necesita un driver SQLite. `Segments[SegmentID]` es el lado uno; `Customers[SegmentID]`, el lado muchos. Filtro unidireccional desde segmentos a clientes. No se crean dimensiones de producto ni relaciones muchos-a-muchos.

## Escenarios y experimento

Se simulan, separadamente por segmento, hasta 200 contactos, mejoras absolutas de retención de 1/3/5 puntos porcentuales respecto a control y 1 UM por contacto. Se usa el cargo mensual medio de activos del segmento. Los valores se guardan junto a cada resultado; no se presentan como hechos.

`Cargos ilustrativos = contactos × mejora incremental supuesta × cargo mensual medio`.

`Diferencia = cargos ilustrativos - coste de contacto`.

La diferencia **no es beneficio neto**: faltan margen, costes de servicio e incentivos. No se multiplica por 12 ni por TotalCharges. No se usa la tasa histórica de esta muestra como riesgo futuro del candidato. Los tres escenarios son alternativas, no sumables entre sí.

## Validación y límites pendientes

20 pruebas cubren snapshot, identidad, nulos, dinero exacto, categorías, servicios, límites de tramos, segmentos, integridad SQL, conciliación SQL/Python, candidatos, fórmulas, referencias y estructura del PBIP, ejecución del notebook, navegación horizontal y paleta del rediseño.

El notebook se ejecutó secuencialmente mediante Python, capturando salidas reales; no se probó un kernel Jupyter. Las medidas DAX y consultas M no se ejecutaron en el motor de Power BI. Los controles JSON y de layout no prueban la carga nativa. Completar `docs/abrir_powerbi.md` antes de presentar el dashboard como verificado.
