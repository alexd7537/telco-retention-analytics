# Plan de retención: propuesta para validar

No se ha ejecutado ninguna campaña ni se afirma una reducción de abandono. Este documento convierte observaciones en hipótesis y define cómo comprobarlas.

## Prioridades iniciales

| Orden | Segmento | Base | Abandonos | Tasa observada | Activos candidatos | Primera hipótesis |
|---|---|---:|---:|---:|---:|---|
| 1 | Mensual, hasta 6 meses | 1.413 | 780 | 55,20 % | 633 | La bienvenida puede resolver fricciones tempranas |
| 2 | Mensual, >6 meses, fibra sin soporte | 1.227 | 607 | 49,47 % | 620 | Hay problemas técnicos o de experiencia que conviene investigar |
| 3 | Mensual restante, cargo >=80 UM | 281 | 92 | 32,74 % | 189 | Puede existir desajuste entre plan, uso y valor percibido |

Los segmentos son excluyentes. La base incluye activos y abandonos; el piloto solo considera activos. En conjunto hay 1.442 candidatos. El listado `analysis/pilot_candidates.csv` contiene IDs del dataset de muestra y la regla aplicable, no datos de contacto ni probabilidades.

## Qué haría en cada grupo

### 1. Bienvenida mensual

Comprobar si la instalación terminó correctamente, explicar la primera factura, facilitar canales de ayuda y resolver incidencias detectadas. Evitar dar descuentos generales sin entender el problema. Responsable sugerido: experiencia de cliente, con apoyo de operaciones.

Validar antes: motivo de contacto, tickets recientes, antigüedad real al asignar y disponibilidad de un canal consentido. La muestra no contiene esas variables.

### 2. Fibra sin soporte

Revisar incidencias y calidad percibida, ofrecer diagnóstico y probar soporte opcional. La diferencia entre clientes con y sin soporte podría reflejar selección de clientes y tipos de contrato; no demuestra que añadir soporte causará retención. Responsable sugerido: soporte técnico.

### 3. Revisión de tarifa

Comparar uso real y necesidades con el plan vigente; explicar el coste y ofrecer una alternativa cuando aporte valor. Cualquier incentivo necesita estimar costes y margen antes de aprobarse. Responsable sugerido: gestión comercial.

### Grupos en seguimiento

Mensual restante: seguimiento de experiencia y educación de pago; si se propone domiciliación, que sea voluntaria y con condiciones claras. Anuales y bianuales: recordatorios de renovación y seguimiento de satisfacción. Una tasa menor no equivale a ausencia de problemas.

## Diseño de un primer piloto

1. Empezar por S1, no por los tres grupos al mismo tiempo. Confirmar elegibilidad en una base operativa actual y respetar las preferencias de contacto.
2. Definir de antemano intervención, canal, coste, fecha de asignación, abandono y ventana de evaluación. No utilizar el 55,20 % del CSV como tasa base a 30 días.
3. Estimar tamaño necesario con una tasa base real, efecto mínimo relevante, potencia y nivel de error; 200 es solo la cantidad ilustrativa de los escenarios. Si 633 candidatos no alcanzan, ampliar captación o ventana, no prometer significancia.
4. Asignar aleatoriamente tratamiento y control dentro de S1, con reparto equilibrado y semilla registrada. El control recibe la atención habitual; no se le niega soporte esencial.
5. Medir abandono a 30 días desde la asignación y hacer seguimiento adicional a 60/90 días. Analizar por intención de tratar, incluyendo a quienes no respondieron al contacto.
6. Informar diferencia absoluta de tasas con intervalo de confianza, volumen, cobertura de seguimiento y costes. Revisar quejas, satisfacción y carga operativa como salvaguardas.
7. Escalar solo si la evidencia y la economía justifican el cambio. Un resultado no concluyente también debe documentarse.

## Datos adicionales requeridos

Fecha de alta, fecha de baja, estado activo actual, motivo de baja, facturación por periodo, tickets, quejas, uso del servicio, coste de atención, incentivos, margen y registro de asignación/contacto/resultados. No es necesario ampliar atributos personales sensibles para probar estas acciones.

## Escenarios ilustrativos

Los supuestos están en `config/scenarios.json`. Cada fila de `analysis/scenarios.csv` es un escenario alternativo de un segmento. No se suman escenarios de distintas mejoras ni se confunden cargos con utilidad.

Para S1 y 200 contactos, el cargo mensual medio de activos es aproximadamente 46,25 UM. Con una mejora incremental supuesta de 3 puntos porcentuales, los cargos mensuales asociados serían 277,47 UM. Un coste supuesto de contacto de 200 UM deja una diferencia de 77,47 UM, **antes de considerar margen, costes del servicio e incentivos**. No es un retorno medido ni una promesa.

## Cómo explicarlo al cliente

“La muestra señala dónde investigar. Mi recomendación no es asumir que todos estos clientes se irán, sino probar una intervención concreta en un grupo definido, compararla con un control y medir el resultado con costes reales.”
