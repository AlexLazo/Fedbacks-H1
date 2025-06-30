import pandas as pd
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

def create_all_level_examples():
    """
    Crea ejemplos de cartas para todos los niveles usando las rutas reales
    """
    print("📋 GENERANDO EJEMPLOS DE CARTAS PARA TODOS LOS NIVELES")
    print("=" * 60)
    
    # Crear directorio
    if not os.path.exists('Ejemplos_Cartas_Todos_Niveles'):
        os.makedirs('Ejemplos_Cartas_Todos_Niveles')
    
    # Datos de las rutas reales
    rutas_data = [
        {'ruta': 'DS004H', 'vendedor': 'VENDEDOR RUTA DS004H'},
        {'ruta': 'DS00U2', 'vendedor': 'VENDEDOR RUTA DS00U2'}
    ]
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    supervisores = {
        'coordinador': {'nombre': 'Óscar Cuellar', 'cargo': 'Coordinador de Distribución'},
        'jefe': {'nombre': 'Óscar Portillo', 'cargo': 'Jefe de Distribución'},
        'gerente': {'nombre': 'Félix Chávez', 'cargo': 'Gerente CD Soyapango'}
    }
    
    cartas_generadas = []
    
    for ruta_info in rutas_data:
        ruta = ruta_info['ruta']
        vendedor = ruta_info['vendedor']
        
        # NIVEL 1 - Llamada de Atención Verbal
        carta_n1 = f"""
═══════════════════════════════════════════════════════════════════════════════
                         CONSTANCIA DE LLAMADA DE ATENCIÓN VERBAL
═══════════════════════════════════════════════════════════════════════════════

FECHA: {fecha_actual}
RUTA: {ruta}
VENDEDOR/CONDUCTOR: {vendedor}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MOTIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Incumplimiento en la realización del Feedback MENSUAL correspondiente a MAYO 2025.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESCRIPCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El vendedor de la ruta {ruta} no realizó el feedback mensual requerido durante 
Mayo 2025, incumpliendo con los procedimientos establecidos por la empresa para 
el seguimiento y mejora continua del servicio al cliente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACCIÓN TOMADA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se realiza LLAMADA DE ATENCIÓN VERBAL al vendedor sobre la importancia crítica 
de cumplir con los feedbacks mensuales como parte fundamental de sus 
responsabilidades laborales y compromiso con la empresa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPROMISOS DEL VENDEDOR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Realizar TODOS los feedbacks mensuales en tiempo y forma
✓ Comunicar cualquier impedimento que pueda afectar el cumplimiento
✓ Mantener al día sus reportes y documentación requerida
✓ Mejorar su compromiso y responsabilidad laboral

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  ADVERTENCIA IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este es su PRIMER incumplimiento registrado. El próximo incumplimiento mensual 
resultará en AMONESTACIÓN ESCRITA que será archivada en su expediente personal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRMAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_________________________________              _________________________________
{vendedor}                                       {supervisores['coordinador']['nombre']}
Vendedor/Conductor                              {supervisores['coordinador']['cargo']}

Fecha: ___________________                      Fecha: ___________________

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBSERVACIONES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________

═══════════════════════════════════════════════════════════════════════════════
                              ARCHIVO: NO SE ARCHIVA
═══════════════════════════════════════════════════════════════════════════════
"""

        # NIVEL 2 - Amonestación Escrita
        carta_n2 = f"""
═══════════════════════════════════════════════════════════════════════════════
                                AMONESTACIÓN ESCRITA
═══════════════════════════════════════════════════════════════════════════════

FECHA: {fecha_actual}
RUTA: {ruta}
VENDEDOR/CONDUCTOR: {vendedor}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 MOTIVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SEGUNDO incumplimiento en la realización del Feedback MENSUAL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ANTECEDENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El vendedor ya recibió LLAMADA DE ATENCIÓN VERBAL por incumplimiento previo 
en la realización de feedbacks mensuales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 DESCRIPCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El vendedor de la ruta {ruta} ha incumplido por SEGUNDA vez con la realización 
del feedback mensual requerido, demostrando falta de compromiso con los 
procedimientos establecidos y desatención a la llamada de atención previa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️  ACCIÓN DISCIPLINARIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se emite AMONESTACIÓN ESCRITA FORMAL que será archivada PERMANENTEMENTE 
en el expediente personal del empleado.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  ADVERTENCIA SEVERA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Esta amonestación escrita constituye una medida disciplinaria FORMAL. El vendedor 
debe entender que su comportamiento laboral NO está cumpliendo con los estándares 
requeridos por la empresa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 COMPROMISOS EXIGIDOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Cumplimiento INMEDIATO y sostenido de todos los feedbacks mensuales
✓ Mejora URGENTE en la responsabilidad y compromiso laboral
✓ Comunicación proactiva con supervisión ante cualquier situación
✓ Demostrar cambio de actitud en el desempeño laboral

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 CONSECUENCIAS DEL PRÓXIMO INCUMPLIMIENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUSPENSIÓN DE UN DÍA SIN GOCE DE SUELDO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRMAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_________________________________              _________________________________
{vendedor}                                       {supervisores['coordinador']['nombre']}
Vendedor/Conductor                              {supervisores['coordinador']['cargo']}

Fecha: ___________________                      Fecha: ___________________

═══════════════════════════════════════════════════════════════════════════════
🗂️  ARCHIVO: SÍ - EXPEDIENTE PERSONAL PERMANENTE
═══════════════════════════════════════════════════════════════════════════════
"""

        # NIVEL 3 - Suspensión
        fecha_suspension = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        fecha_reintegro = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
        
        carta_n3 = f"""
═══════════════════════════════════════════════════════════════════════════════
                                  ACTA DE SUSPENSIÓN
═══════════════════════════════════════════════════════════════════════════════

FECHA: {fecha_actual}
RUTA: {ruta}
VENDEDOR/CONDUCTOR: {vendedor}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 MOTIVO GRAVE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TERCER incumplimiento en la realización del Feedback MENSUAL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HISTORIAL DISCIPLINARIO COMPLETO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PRIMER incumplimiento: Llamada de atención verbal ✓
2. SEGUNDO incumplimiento: Amonestación escrita ✓  
3. TERCER incumplimiento: PRESENTE ACTA DE SUSPENSIÓN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 DESCRIPCIÓN DE LA FALTA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El vendedor de la ruta {ruta} ha incumplido por TERCERA vez consecutiva con la 
realización del feedback mensual, demostrando una actitud REINCIDENTE de 
incumplimiento a pesar de las medidas disciplinarias previas aplicadas.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️  MEDIDA DISCIPLINARIA APLICADA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUSPENSIÓN DE UN (1) DÍA SIN GOCE DE SUELDO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 FECHAS DE SUSPENSIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• FECHA DE SUSPENSIÓN: {fecha_suspension}
• FECHA DE REINTEGRO: {fecha_reintegro}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CONDICIONES PARA REINTEGRO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Compromiso escrito de cumplimiento futuro
✓ Reunión obligatoria con {supervisores['jefe']['nombre']} antes del reintegro  
✓ Plan de mejora personalizado acordado
✓ Demostrar cambio de actitud y compromiso

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ADVERTENCIA FINAL SEVERA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cualquier incumplimiento adicional será evaluado directamente por el 
GERENTE CD SOYAPANGO para determinar medidas disciplinarias más severas, 
incluyendo posible evaluación de continuidad laboral.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRMAS REQUERIDAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_________________________________              _________________________________
{vendedor}                                       {supervisores['jefe']['nombre']}
Vendedor/Conductor                              {supervisores['jefe']['cargo']}

_________________________________              
{supervisores['coordinador']['nombre']}                                       
{supervisores['coordinador']['cargo']}

Fecha: ___________________                      

═══════════════════════════════════════════════════════════════════════════════
🗂️  ARCHIVO: EXPEDIENTE PERSONAL + COORDINACIÓN + JEFATURA
═══════════════════════════════════════════════════════════════════════════════
"""

        # NIVEL 4 - Evaluación Gerencial
        fecha_evaluacion = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        
        carta_n4 = f"""
═══════════════════════════════════════════════════════════════════════════════
                          CITACIÓN PARA EVALUACIÓN GERENCIAL
═══════════════════════════════════════════════════════════════════════════════

FECHA: {fecha_actual}
RUTA: {ruta}
VENDEDOR/CONDUCTOR: {vendedor}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 MOTIVO CRÍTICO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CUARTO incumplimiento o más en la realización de Feedbacks mensuales.
CASO CRÍTICO que requiere evaluación gerencial inmediata.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 HISTORIAL DISCIPLINARIO COMPLETO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PRIMER incumplimiento: Llamada de atención verbal ✓
2. SEGUNDO incumplimiento: Amonestación escrita ✓  
3. TERCER incumplimiento: Suspensión 1 día ✓
4. INCUMPLIMIENTOS ADICIONALES: EVALUACIÓN GERENCIAL OBLIGATORIA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 SITUACIÓN CRÍTICA ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El vendedor de la ruta {ruta} presenta un patrón REINCIDENTE GRAVE de 
incumplimiento en la realización de feedbacks mensuales, habiendo agotado 
TODAS las medidas disciplinarias progresivas sin mostrar mejora en su 
comportamiento laboral.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 CITACIÓN OBLIGATORIA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se CITA OBLIGATORIAMENTE al vendedor a reunión de evaluación gerencial para 
determinar las medidas disciplinarias correspondientes según la gravedad del caso.

• FECHA DE EVALUACIÓN: {fecha_evaluacion}
• HORA: 8:00 AM (PUNTUAL)
• LUGAR: Oficina de Gerencia CD Soyapango

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 COMITÉ DE EVALUACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• {supervisores['gerente']['nombre']} - {supervisores['gerente']['cargo']} (PRESIDENTE)
• {supervisores['jefe']['nombre']} - {supervisores['jefe']['cargo']}
• {supervisores['coordinador']['nombre']} - {supervisores['coordinador']['cargo']}
• {vendedor} - Vendedor/Conductor (EVALUADO)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️  OPCIONES DISCIPLINARIAS A EVALUAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

□ Suspensión extendida (3-5 días sin goce de sueldo)
□ Capacitación obligatoria intensiva
□ Cambio de ruta con período de prueba estricto
□ Plan de mejora con seguimiento semanal obligatorio
□ Medidas disciplinarias adicionales según evaluación gerencial
□ Evaluación de continuidad laboral

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  ADVERTENCIA CRÍTICA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

La asistencia a esta evaluación es OBLIGATORIA e INELUDIBLE. 
La ausencia injustificada constituirá falta GRAVE ADICIONAL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRMAS DE NOTIFICACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_________________________________              _________________________________
{vendedor}                                       {supervisores['gerente']['nombre']}
Vendedor/Conductor                              {supervisores['gerente']['cargo']}

_________________________________              _________________________________
{supervisores['jefe']['nombre']}                              {supervisores['coordinador']['nombre']}
{supervisores['jefe']['cargo']}                               {supervisores['coordinador']['cargo']}

Fecha: ___________________                      

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 RESULTADO DE LA EVALUACIÓN (llenar después de la reunión):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANÁLISIS DEL CASO: ____________________________________________________________

_____________________________________________________________________________

DECISIÓN ADOPTADA: ____________________________________________________________

_____________________________________________________________________________

MEDIDAS APLICADAS: ____________________________________________________________

_____________________________________________________________________________

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DECISIÓN FINAL GERENCIA: _____________________________________________________

FIRMA GERENCIA: ___________________________  FECHA: _______________________

═══════════════════════════════════════════════════════════════════════════════
🗂️  ARCHIVO: EXPEDIENTE + GERENCIA + JEFATURA + COORDINACIÓN + SEGUIMIENTO
═══════════════════════════════════════════════════════════════════════════════
"""

        # Guardar las cartas
        niveles = [
            ('NIVEL1_Atencion_Verbal', carta_n1),
            ('NIVEL2_Amonestacion_Escrita', carta_n2),
            ('NIVEL3_Suspension', carta_n3),
            ('NIVEL4_Evaluacion_Gerencial', carta_n4)
        ]
        
        for nivel_nombre, contenido in niveles:
            filename = f"Ejemplos_Cartas_Todos_Niveles/EJEMPLO_{nivel_nombre}_Ruta_{ruta}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            cartas_generadas.append({
                'Ruta': ruta,
                'Nivel': nivel_nombre,
                'Archivo': filename
            })
    
    # Crear resumen
    resumen_df = pd.DataFrame(cartas_generadas)
    resumen_filename = f"Ejemplos_Cartas_Todos_Niveles/RESUMEN_Ejemplos_Todas_Cartas.xlsx"
    resumen_df.to_excel(resumen_filename, index=False)
    
    print(f"✅ Ejemplos generados para todos los niveles")
    print(f"📁 Directorio: Ejemplos_Cartas_Todos_Niveles/")
    print(f"📊 Total archivos: {len(cartas_generadas)}")
    print(f"📄 Resumen: {resumen_filename}")
    
    return cartas_generadas

def main():
    """
    Función principal para generar ejemplos de todos los niveles
    """
    print("🎯 GENERADOR DE EJEMPLOS COMPLETOS PARA TODOS LOS NIVELES")
    print("=" * 70)
    
    # Generar ejemplos de cartas para todos los niveles
    ejemplos = create_all_level_examples()
    
    print("\n" + "=" * 70)
    print("✅ EJEMPLOS COMPLETOS GENERADOS")
    print(f"📁 Total ejemplos: {len(ejemplos)}")
    print(f"📂 Directorio: Ejemplos_Cartas_Todos_Niveles/")
    
    print(f"\n📋 CONTENIDO GENERADO:")
    print(f"   • NIVEL 1: Llamada de Atención Verbal (2 ejemplos)")
    print(f"   • NIVEL 2: Amonestación Escrita (2 ejemplos)")  
    print(f"   • NIVEL 3: Suspensión (2 ejemplos)")
    print(f"   • NIVEL 4: Evaluación Gerencial (2 ejemplos)")
    print(f"   • Resumen Excel con todos los archivos")
    
    print(f"\n⚡ CARACTERÍSTICAS:")
    print(f"   ✓ Cartas con datos reales de las rutas")
    print(f"   ✓ Formato profesional y detallado")
    print(f"   ✓ Jerarquía correcta de responsables")
    print(f"   ✓ Sin participación de RRHH")
    print(f"   ✓ Fechas y plazos específicos")
    print(f"   ✓ Espacios para firmas y observaciones")
    
    print(f"\n📋 CÓMO USAR:")
    print(f"   1. Determinar el nivel según historial del vendedor")
    print(f"   2. Usar la carta correspondiente como plantilla")
    print(f"   3. Ajustar datos específicos si es necesario")
    print(f"   4. Imprimir y aplicar la medida disciplinaria")
    print(f"   5. Archivar según indicaciones en cada carta")

if __name__ == "__main__":
    main()
