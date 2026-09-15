# Fuentes y atribución

## Datos utilizados

Se trabajó sobre el archivo `Telco-Customer-Churn.csv` aportado por el usuario. Se conserva una copia en `data/raw/`, con tamaño y SHA-256 en `analysis/source_manifest.json`. La fuente original no se modificó.

Referencia pública del dataset de 21 columnas: [archivo de IBM](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv). Su [README](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/README.md) incluye ese CSV como dato de ejemplo para un caso de abandono. El 14 de septiembre de 2026 se descargó esa copia pública y se comprobó igualdad byte a byte mediante SHA-256: `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`, 970.457 bytes. No se atribuye al archivo una fecha de corte, moneda o información de otras versiones ampliadas de Telco.

El repositorio de referencia publica una [licencia Apache 2.0](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/LICENSE), conservada íntegramente en [IBM-DATA-LICENSE.txt](IBM-DATA-LICENSE.txt). Se atribuye el CSV a ese repositorio y se conserva sin modificar en `data/raw/`. Las tablas limpias, la base SQLite, los agregados y los candidatos son derivados producidos por el código de este proyecto; sus transformaciones se describen en `metodologia.md`. La licencia del repositorio fuente no se presenta como licencia del código original de este portafolio; no se ha elegido una licencia abierta para ese código. No existe afiliación ni respaldo de IBM.

El manifiesto inicial registra el estado anterior a esta comprobación. La evidencia de publicación se encuentra en `analysis/publication_source_verification.json`.

## Implementación de Power BI

- [Microsoft: proyectos Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).
- [Microsoft: carpeta del informe y formato PBIR](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report).
- [Microsoft: esquemas JSON](https://github.com/microsoft/json-schemas).

Consulta de las referencias: 13 de septiembre de 2026. Los archivos se entregan en un formato de proyecto de texto, con validación nativa pendiente.

## Autoría y presentación

Caso de portafolio preparado para Alexander Cordova con asistencia de Codex. No corresponde a un trabajo remunerado ni a una campaña real. El código transforma y analiza la base; el PDF resume resultados calculados. No se copiaron resultados de un caso ajeno ni se inventaron mejoras comerciales.
