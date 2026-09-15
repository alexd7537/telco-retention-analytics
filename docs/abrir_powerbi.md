# Abrir y comprobar Power BI

## Archivo correcto

Abre `powerbi/TelcoRetention.pbip`. Ese archivo apunta a las dos carpetas que lo acompañan: `.Report` (páginas y visuales) y `.SemanticModel` (tablas, relaciones y medidas). No subas o muevas solo el `.pbip`.

Este es un proyecto editable, **no un archivo PBIX generado y probado en Desktop**. Microsoft documenta que PBIP almacena definiciones de texto y que se puede abrir desde el `.pbip` o `definition.pbir`. Ver [documentación oficial](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

## Apertura

1. Guarda cualquier otro trabajo de Power BI antes de empezar.
2. Abre `TelcoRetention.pbip` con Power BI Desktop compatible con proyectos PBIP/PBIR. Si tu versión solicita habilitar las opciones preliminares de proyecto o formato de informe, sigue el aviso y reinicia Desktop si lo requiere. Referencia: [formato del informe](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report).
3. Si aparece un aviso para convertir el modelo a TMDL, conserva una copia antes. No necesitas convertirlo para corregir los datos; este generador entrega `model.bim`. Si conviertes y editas, no vuelvas a ejecutar el generador sobre esa misma copia sin revisar el cambio de formato.
4. Revisa `Transformar datos > Administrar parámetros > DataFolder`. Debe apuntar a la carpeta `data/processed` del proyecto. La copia pública contiene la ruta de ejemplo `C:/TELCO_RETAIN/data/processed`: debes sustituirla por tu ubicación real. Alternativamente, con Desktop cerrado ejecuta `python src/configure_data.py --folder "RUTA/telco-retention-analytics/data/processed"` desde la raíz extraída; solo modifica este parámetro.
5. Aplica los cambios y pulsa Actualizar. La primera carga crea la caché local del modelo.
6. Si quieres un `.pbix`, después de validar usa Guardar como en Desktop. No se fabrica ni se convierte el binario PBIX con el script.

## Si mueves la carpeta

Actualiza `DataFolder` a la nueva ubicación. Usa la ruta hasta `data/processed`, sin añadir `Customers.csv`. La importación espera `Customers.csv` y `Segments.csv` juntos. No apunta al CSV raw del Escritorio ni al proyecto de ventas.

## Qué debes ver al abrir sin filtros

| Página / indicador | Resultado esperado |
|---|---:|
| Panorama: Clientes | 7.043 |
| Panorama: Abandonos | 1.869 |
| Panorama: Tasa de abandono | 26,5 % (26,536987 % antes de redondear) |
| Panorama: Cargos de abandonos, total de la tabla de detalle | 139.130,85 UM |
| Prioridades: Candidatos activos | 1.442 |
| Prioridades: Cargos de candidatos | 101.526,50 UM |
| Prioridades: Activos | 5.174 |
| Prioridades: Base global | 26,5 % |

## Checklist de aceptación manual pendiente

- [ ] El PBIP abre sin errores de modelo o visuales.
- [ ] Actualizar carga 7.043 clientes y 6 segmentos.
- [ ] Los 11 `TotalCharges` nulos no producen errores de conversión.
- [ ] `Segments[SegmentID]` es único; relación uno-a-muchos con `Customers[SegmentID]`.
- [ ] Las cifras anteriores coinciden con SQL sin filtros.
- [ ] Al filtrar contrato Mensual se ven 3.875 clientes y 1.655 abandonos: 42,7 %.
- [ ] El filtro de antigüedad ordena 0-6, 7-12, 13-24, 25-48, 49+.
- [ ] En Factores, soporte usa solo clientes con internet; no se confunde No aplica con Sin soporte.
- [ ] Los botones de navegación llevan a la página correcta (en modo edición puede requerirse Ctrl+clic).
- [ ] El menú está en la franja superior; no aparece la antigua barra lateral izquierda.
- [ ] Los filtros de cada página funcionan. No están sincronizados entre páginas.
- [ ] En Prioridades, las métricas cambian con filtros; la prioridad global no cambia.
- [ ] Las etiquetas, tablas, tarjetas y títulos se leen sin recortes a tamaño de página.
- [ ] Se han tomado capturas reales de las tres páginas antes de anunciarlas como dashboard validado.

## Qué sí se validó automáticamente

CSV y SQL conciliados, IDs únicos, tipos declarados, reemplazo de vacíos antes de conversión de cargos en M, referencias de campos, roles de consulta, límites del lienzo y destinos de navegación. El estado se guarda en `analysis/powerbi_validation.json`.

**Qué falta:** ejecutar M y DAX en el motor nativo, actualizar, revisar filtros y ver el resultado real en Desktop. El PDF y las imágenes son un resumen editorial aparte y no sustituyen esa prueba.

## Regeneración segura

`src/build_powerbi.py` vuelve a escribir el PBIP desde código. No debe ejecutarse sobre ediciones manuales sin respaldo. Para actualizar los análisis sin tocar el diseño usa `python src/run_project.py --skip-powerbi`, y después Actualizar en Desktop. Si has convertido a TMDL, conserva ese proyecto aparte del destino del generador.

Para regenerar únicamente la presentación sin escribir el modelo semántico: `python src/build_powerbi.py --design-only`. Esto sustituye los visuales del informe según `src/design_editorial.py`; respaldar antes las ediciones manuales del diseño.
