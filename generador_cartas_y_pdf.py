import pandas as pd
from datetime import datetime, timedelta
import calendar
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import io

def load_headcount_data():
    """
    Carga la base de datos de HEADCOUNT para obtener nombres completos y supervisores
    """
    try:
        # Intentar cargar el archivo HEADCOUNT
        headcount_file = "BASE HEADCOUNT JUNIO - 2025.xlsm"
        headcount_df = pd.read_excel(headcount_file, engine='openpyxl')
        
        print(f"✅ BASE HEADCOUNT cargada: {len(headcount_df)} empleados")
        
        # Mostrar las columnas disponibles para verificar
        print(f"📋 Columnas disponibles: {list(headcount_df.columns)}")
        
        return headcount_df
        
    except Exception as e:
        print(f"❌ Error cargando BASE HEADCOUNT: {e}")
        return None

def get_signatures_for_date():
    """Return current signatures"""
    return [
        {"name": "Roney Rivas", "title": "TL de Ventas"},
        {"name": "Félix Chávez", "title": "Gerente CD Soyapango"},
        {"name": "Óscar Portillo", "title": "Jefe de Distribución"},
        {"name": "Óscar Cuellar", "title": "Coordinador de Distribución"}
    ]

def get_supervisor_info():
    """
    Retorna información de supervisores según la jerarquía CORREGIDA
    """
    return {
        'supervisor_distribucion': {
            'nombre': 'Supervisor de Distribución',
            'cargo': 'Supervisor de Distribución'
        },
        'coordinador': {
            'nombre': 'Óscar Cuellar',
            'cargo': 'Coordinador de Distribución'
        },
        'jefe': {
            'nombre': 'Óscar Portillo', 
            'cargo': 'Jefe de Distribución'
        },
        'gerente': {
            'nombre': 'Félix Chávez',
            'cargo': 'Gerente CD Soyapango'
        }
    }

def generar_flujo_consecuencias_con_cartas(mes=5, año=2025):
    """
    Genera el flujo de consecuencias mensual con cartas PDF personalizadas
    """
    mes_nombre = calendar.month_name[mes]
    
    print(f"📋 GENERANDO FLUJO DE CONSECUENCIAS CON CARTAS PDF: {mes_nombre.upper()} {año}")
    print("=" * 80)
    
    try:
        # Cargar datos principales
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        headcount_df = load_headcount_data()
        
        if headcount_df is None:
            print("⚠️ Continuando sin base HEADCOUNT, usando datos disponibles")
        
        # Cargar base de rutas
        archivos_rutas = [
            f'BD_Rutas_{mes_nombre}.xlsx',
            'BD_Rutas_Junio.xlsx',
            'BD_Rutas_Mayo.xlsx', 
            'BD_Rutas.xlsx'
        ]
        
        rutas_df = None
        archivo_usado = None
        
        for archivo in archivos_rutas:
            try:
                rutas_df = pd.read_excel(archivo)
                archivo_usado = archivo
                print(f"✅ Usando base de rutas: {archivo}")
                break
            except FileNotFoundError:
                continue
        
        if rutas_df is None:
            print("❌ No se encontró ninguna base de datos de rutas")
            return None
        
        # Convertir fechas
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        
        # Filtrar feedbacks del mes específico
        feedbacks_mes = feedbacks_df[
            (feedbacks_df['fecha_registro'].dt.month == mes) &
            (feedbacks_df['fecha_registro'].dt.year == año)
        ]
        
        print(f"📊 Feedbacks encontrados en {mes_nombre} {año}: {len(feedbacks_mes)}")
        
        # Obtener todas las rutas activas
        todas_las_rutas = set(rutas_df['RUTA'].dropna().unique())
        
        # Rutas que SÍ hicieron feedback
        rutas_con_feedback = set(feedbacks_mes['ruta'].dropna().unique())
        
        # Rutas que NO hicieron feedback (necesitan consecuencias)
        rutas_sin_feedback = todas_las_rutas - rutas_con_feedback
        
        print(f"📈 Total rutas activas: {len(todas_las_rutas)}")
        print(f"✅ Rutas que cumplieron: {len(rutas_con_feedback)}")
        print(f"❌ Rutas que NO cumplieron: {len(rutas_sin_feedback)}")
        
        # Crear lista de rutas para consecuencias con datos completos
        rutas_consecuencias = []
        
        for ruta in sorted(rutas_sin_feedback):
            # Buscar información en la base de rutas
            info_ruta = rutas_df[rutas_df['RUTA'] == ruta]
            
            reparto_nombre = 'Reparto no identificado'
            supervisor_nombre = 'Supervisor no identificado'
            
            if not info_ruta.empty:
                # Intentar obtener el nombre del reparto de diferentes columnas posibles
                for col in ['NOMBRE_VENDEDOR', 'VENDEDOR', 'REPARTO', 'NOMBRE_REPARTO', 'NOMBRE']:
                    if col in info_ruta.columns and pd.notna(info_ruta[col].iloc[0]):
                        reparto_nombre = info_ruta[col].iloc[0]
                        break
                
                # Buscar en HEADCOUNT para obtener datos completos
                if headcount_df is not None:
                    # Buscar por nombre del reparto en HEADCOUNT
                    headcount_match = headcount_df[
                        headcount_df['NOMBRE COMPLETO'].str.contains(reparto_nombre, case=False, na=False)
                    ]
                    
                    if not headcount_match.empty:
                        reparto_nombre = headcount_match['NOMBRE COMPLETO'].iloc[0]
                        
                        # Obtener supervisor si existe la columna
                        for sup_col in ['POSICION - SUPERVISOR', 'SUPERVISOR', 'JEFE_INMEDIATO']:
                            if sup_col in headcount_match.columns and pd.notna(headcount_match[sup_col].iloc[0]):
                                supervisor_nombre = headcount_match[sup_col].iloc[0]
                                break
            
            rutas_consecuencias.append({
                'RUTA': ruta,
                'REPARTO': reparto_nombre,
                'SUPERVISOR': supervisor_nombre,
                'MES_INCUMPLIMIENTO': f'{mes_nombre} {año}',
                'NIVEL_CONSECUENCIA': '',  # Para llenar manualmente
                'ACCION_REQUERIDA': '',    # Para llenar manualmente
                'RESPONSABLE': '',         # Para llenar manualmente
                'FECHA_LIMITE': '',        # Para llenar manualmente
                'FECHA_EJECUTADA': '',     # Para llenar al ejecutar
                'ESTADO': 'PENDIENTE',
                'OBSERVACIONES': '',
                'DOCUMENTO_EVIDENCIA': ''
            })
        
        # Crear DataFrame
        df_consecuencias = pd.DataFrame(rutas_consecuencias)
        
        # Crear hoja de guía rápida CORREGIDA
        guia_rapida = [
            {
                'NIVEL': 'NIVEL 1', 
                'ACCION': 'Llamada atención verbal', 
                'RESPONSABLE': 'Supervisor de Distribución', 
                'PLAZO': '2 días',
                'DESCRIPCION': 'Primera falta mensual'
            },
            {
                'NIVEL': 'NIVEL 2', 
                'ACCION': 'Amonestación escrita', 
                'RESPONSABLE': 'Coordinador de Distribución', 
                'PLAZO': '3 días',
                'DESCRIPCION': 'Segunda falta mensual'
            },
            {
                'NIVEL': 'NIVEL 3', 
                'ACCION': 'Suspensión 1 día', 
                'RESPONSABLE': 'Jefe de Distribución', 
                'PLAZO': '5 días',
                'DESCRIPCION': 'Tercera falta mensual'
            },
            {
                'NIVEL': 'NIVEL 4', 
                'ACCION': 'Evaluación disciplinaria', 
                'RESPONSABLE': 'Gerente CD Soyapango', 
                'PLAZO': '1 semana',
                'DESCRIPCION': 'Cuarta falta o más'
            }
        ]
        
        df_guia = pd.DataFrame(guia_rapida)
        
        # Crear resumen estadístico
        resumen = [{
            'MES': f'{mes_nombre} {año}',
            'TOTAL_RUTAS': len(todas_las_rutas),
            'CUMPLIERON': len(rutas_con_feedback),
            'NO_CUMPLIERON': len(rutas_sin_feedback),
            'PORCENTAJE_CUMPLIMIENTO': round((len(rutas_con_feedback) / len(todas_las_rutas)) * 100, 1),
            'ARCHIVO_RUTAS_USADO': archivo_usado,
            'FECHA_GENERACION': datetime.now().strftime('%Y-%m-%d %H:%M')
        }]
        
        df_resumen = pd.DataFrame(resumen)
        
        # Generar archivo Excel
        excel_filename = f"Consecuencias_{mes_nombre}_{año}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
            # Hoja principal: Rutas para consecuencias
            df_consecuencias.to_excel(writer, sheet_name='RUTAS_CONSECUENCIAS', index=False)
            
            # Hoja de guía
            df_guia.to_excel(writer, sheet_name='GUIA_RAPIDA', index=False)
            
            # Hoja de resumen
            df_resumen.to_excel(writer, sheet_name='RESUMEN', index=False)
            
            # Formateo básico
            workbook = writer.book
            
            # Formato de encabezado
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            
            # Aplicar formato a la hoja principal
            worksheet = writer.sheets['RUTAS_CONSECUENCIAS']
            
            # Ajustar anchos de columna
            worksheet.set_column('A:A', 12)  # RUTA
            worksheet.set_column('B:B', 25)  # REPARTO
            worksheet.set_column('C:C', 25)  # SUPERVISOR
            worksheet.set_column('D:L', 20)  # Resto de columnas
        
        print(f"✅ Archivo Excel generado: {excel_filename}")
        
        # Generar cartas PDF para cada ruta
        if len(rutas_sin_feedback) > 0:
            generar_cartas_pdf(df_consecuencias, mes_nombre, año)
        
        # Generar PDF del flujo completo
        generar_pdf_flujo_completo(df_guia, mes_nombre, año, df_resumen)
        
        return excel_filename, len(rutas_sin_feedback)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, 0
Se realiza llamada de atención VERBAL al reparto sobre la importancia de cumplir con los feedbacks 
mensuales como parte fundamental de sus responsabilidades laborales.

COMPROMISO:
El reparto se compromete a:
- Realizar todos los feedbacks mensuales en tiempo y forma
- Comunicar cualquier impedimento que pueda afectar el cumplimiento
- Mantener al día sus reportes y documentación requerida

CONSECUENCIAS:
Este es el PRIMER incumplimiento registrado. El próximo incumplimiento resultará en amonestación escrita 
que será archivada en su expediente personal.

FIRMAS:

_____________________________          _____________________________
{vendedor}                             {supervisores['coordinador']['nombre']}
Conductor                     {supervisores['coordinador']['cargo']}

Fecha: _________________               Fecha: _________________

OBSERVACIONES:
_________________________________________________________________________
_________________________________________________________________________
_________________________________________________________________________
"""
    return carta_content

def generate_carta_nivel2(ruta, vendedor, mes_año, fecha_actual):
    """
    Genera carta para NIVEL 2 - Amonestación Escrita
    """
    supervisores = get_supervisor_info()
    
    carta_content = f"""
AMONESTACIÓN ESCRITA

Fecha: {fecha_actual}
Ruta: {ruta}
Conductor: {vendedor}

MOTIVO:
SEGUNDO incumplimiento en la realización del Feedback mensual correspondiente a {mes_año}.

ANTECEDENTE:
El reparto ya recibió llamada de atención verbal por incumplimiento previo en la realización 
de feedbacks mensuales.

DESCRIPCIÓN:
El reparto de la ruta {ruta} ha incumplido por SEGUNDA vez con la realización del feedback 
mensual requerido durante el período de {mes_año}, demostrando falta de compromiso con los 
procedimientos establecidos.

ACCIÓN DISCIPLINARIA:
Se emite AMONESTACIÓN ESCRITA que será archivada en el expediente personal del empleado.

ADVERTENCIA:
Esta amonestación escrita constituye una medida disciplinaria formal. El reparto debe entender 
que su comportamiento laboral no está cumpliendo con los estándares requeridos.

COMPROMISOS EXIGIDOS:
- Cumplimiento INMEDIATO y sostenido de todos los feedbacks mensuales
- Mejora en la responsabilidad y compromiso laboral
- Comunicación proactiva con supervisión

CONSECUENCIAS:
El próximo incumplimiento resultará en SUSPENSIÓN DE UN DÍA SIN GOCE DE SUELDO.

FIRMAS:

_____________________________          _____________________________
{vendedor}                             {supervisores['coordinador']['nombre']}
Vendedor/Conductor                     {supervisores['coordinador']['cargo']}

Fecha: _________________               Fecha: _________________

COPIA PARA EXPEDIENTE PERSONAL: SÍ

OBSERVACIONES:
_________________________________________________________________________
_________________________________________________________________________
_________________________________________________________________________
"""
    return carta_content

def generate_carta_nivel3(ruta, vendedor, mes_año, fecha_actual):
    """
    Genera carta para NIVEL 3 - Suspensión
    """
    supervisores = get_supervisor_info()
    fecha_suspension = (datetime.strptime(fecha_actual, '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d')
    fecha_reintegro = (datetime.strptime(fecha_suspension, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    carta_content = f"""
ACTA DE SUSPENSIÓN

Fecha: {fecha_actual}
Ruta: {ruta}
Vendedor/Conductor: {vendedor}

MOTIVO:
TERCER incumplimiento en la realización del Feedback mensual correspondiente a {mes_año}.

HISTORIAL DISCIPLINARIO:
1. Primer incumplimiento: Llamada de atención verbal
2. Segundo incumplimiento: Amonestación escrita
3. Tercer incumplimiento: PRESENTE ACTA

DESCRIPCIÓN:
El vendedor de la ruta {ruta} ha incumplido por TERCERA vez con la realización del feedback 
mensual, demostrando una actitud reincidente de incumplimiento a pesar de las medidas 
disciplinarias previas aplicadas.

MEDIDA DISCIPLINARIA:
SUSPENSIÓN DE UN (1) DÍA SIN GOCE DE SUELDO

FECHAS:
- Fecha de suspensión: {fecha_suspension}
- Fecha de reintegro: {fecha_reintegro}

CONDICIONES DE REINTEGRO:
- Compromiso escrito de cumplimiento futuro
- Reunión con {supervisores['jefe']['nombre']} antes del reintegro
- Plan de mejora personalizado

ADVERTENCIA FINAL:
Cualquier incumplimiento adicional será evaluado por el Gerente para determinar medidas 
disciplinarias más severas, incluyendo posible evaluación de continuidad laboral.

FIRMAS:

_____________________________          _____________________________
{vendedor}                             {supervisores['jefe']['nombre']}
Vendedor/Conductor                     {supervisores['jefe']['cargo']}

_____________________________          
{supervisores['coordinador']['nombre']}                             
{supervisores['coordinador']['cargo']}

Fecha: _________________               

COPIA PARA: Expediente personal, Coordinación, Jefatura

OBSERVACIONES:
_________________________________________________________________________
_________________________________________________________________________
_________________________________________________________________________
"""
    return carta_content

def generate_carta_nivel4(ruta, vendedor, mes_año, fecha_actual):
    """
    Genera carta para NIVEL 4 - Evaluación Gerencial
    """
    supervisores = get_supervisor_info()
    fecha_evaluacion = (datetime.strptime(fecha_actual, '%Y-%m-%d') + timedelta(days=5)).strftime('%Y-%m-%d')
    
    carta_content = f"""
CITACIÓN PARA EVALUACIÓN GERENCIAL

Fecha: {fecha_actual}
Ruta: {ruta}
Vendedor/Conductor: {vendedor}

MOTIVO:
CUARTO incumplimiento o más en la realización de Feedbacks mensuales.

HISTORIAL DISCIPLINARIO:
1. Primer incumplimiento: Llamada de atención verbal
2. Segundo incumplimiento: Amonestación escrita  
3. Tercer incumplimiento: Suspensión 1 día
4. Incumplimientos adicionales: EVALUACIÓN GERENCIAL

SITUACIÓN ACTUAL:
El vendedor de la ruta {ruta} presenta un patrón reincidente de incumplimiento en la realización 
de feedbacks mensuales, habiendo agotado las medidas disciplinarias progresivas sin mostrar 
mejora en su comportamiento laboral.

CITACIÓN:
Se CITA al vendedor a reunión de evaluación con Gerencia para determinar las medidas 
disciplinarias correspondientes según la gravedad del caso.

FECHA DE EVALUACIÓN: {fecha_evaluacion}
HORA: 8:00 AM
LUGAR: Oficina de Gerencia CD Soyapango

PARTICIPANTES DE LA EVALUACIÓN:
- {supervisores['gerente']['nombre']} - {supervisores['gerente']['cargo']}
- {supervisores['jefe']['nombre']} - {supervisores['jefe']['cargo']}
- {supervisores['coordinador']['nombre']} - {supervisores['coordinador']['cargo']}
- {vendedor} - Vendedor/Conductor

OPCIONES A EVALUAR:
□ Suspensión extendida (3-5 días sin goce de sueldo)
□ Capacitación obligatoria intensiva
□ Cambio de ruta con período de prueba
□ Plan de mejora con seguimiento semanal
□ Otras medidas según evaluación gerencial

ADVERTENCIA:
La asistencia a esta evaluación es OBLIGATORIA. La ausencia injustificada constituirá 
falta grave adicional.

FIRMAS:

_____________________________          _____________________________
{vendedor}                             {supervisores['gerente']['nombre']}
Vendedor/Conductor                     {supervisores['gerente']['cargo']}

_____________________________          _____________________________
{supervisores['jefe']['nombre']}                             {supervisores['coordinador']['nombre']}
{supervisores['jefe']['cargo']}                              {supervisores['coordinador']['cargo']}

Fecha: _________________               

COPIA PARA: Expediente personal, Gerencia, Jefatura, Coordinación

OBSERVACIONES:
_________________________________________________________________________
_________________________________________________________________________
_________________________________________________________________________

RESULTADO DE LA EVALUACIÓN (llenar después de la reunión):
_________________________________________________________________________
_________________________________________________________________________
_________________________________________________________________________

DECISIÓN FINAL: ___________________________________________________________

FIRMA GERENCIA: _________________________ FECHA: _____________________
"""
    return carta_content

def generate_cartas_for_routes():
    """
    Genera cartas para las rutas que necesitan consecuencias
    """
    print("📋 GENERANDO CARTAS DISCIPLINARIAS PARA RUTAS")
    print("=" * 60)
    
    try:
        # Cargar datos
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        rutas_df = pd.read_excel('BD_Rutas_Mayo.xlsx')
        
        # Convertir fechas
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        
        # Filtrar Mayo 2025
        mayo_feedbacks = feedbacks_df[
            (feedbacks_df['fecha_registro'].dt.month == 5) &
            (feedbacks_df['fecha_registro'].dt.year == 2025)
        ]
        
        # Identificar rutas sin feedback
        todas_las_rutas = set(rutas_df['RUTA'].dropna().unique())
        rutas_con_feedback = set(mayo_feedbacks['ruta'].dropna().unique())
        rutas_sin_feedback = todas_las_rutas - rutas_con_feedback
        
        print(f"📊 Rutas que necesitan cartas: {len(rutas_sin_feedback)}")
        
        # Crear directorio para cartas
        if not os.path.exists('Cartas_Disciplinarias'):
            os.makedirs('Cartas_Disciplinarias')
        
        cartas_generadas = []
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        
        for ruta in sorted(rutas_sin_feedback):
            # Buscar información del vendedor
            info_ruta = rutas_df[rutas_df['RUTA'] == ruta]
            vendedor = 'VENDEDOR NO IDENTIFICADO'
            
            if not info_ruta.empty and 'NOMBRE_VENDEDOR' in info_ruta.columns:
                vendedor = info_ruta['NOMBRE_VENDEDOR'].iloc[0]
            
            # Para este ejemplo, generar cartas de diferentes niveles
            # En la práctica, deberías determinar el nivel según el historial
            nivel = 1  # Por defecto NIVEL 1 para nuevos incumplimientos
            
            # Generar carta según el nivel
            if nivel == 1:
                carta_content = generate_carta_nivel1(ruta, vendedor, "Mayo 2025", fecha_actual)
                nivel_nombre = "NIVEL1_Atencion_Verbal"
            elif nivel == 2:
                carta_content = generate_carta_nivel2(ruta, vendedor, "Mayo 2025", fecha_actual)
                nivel_nombre = "NIVEL2_Amonestacion_Escrita"
            elif nivel == 3:
                carta_content = generate_carta_nivel3(ruta, vendedor, "Mayo 2025", fecha_actual)
                nivel_nombre = "NIVEL3_Suspension"
            else:
                carta_content = generate_carta_nivel4(ruta, vendedor, "Mayo 2025", fecha_actual)
                nivel_nombre = "NIVEL4_Evaluacion_Gerencial"
            
            # Guardar carta
            filename = f"Cartas_Disciplinarias/Carta_{nivel_nombre}_Ruta_{ruta}_{fecha_actual.replace('-', '')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(carta_content)
            
            cartas_generadas.append({
                'Ruta': ruta,
                'Vendedor': vendedor,
                'Nivel': nivel_nombre,
                'Archivo': filename
            })
            
            print(f"✅ Carta generada: {ruta} - {vendedor} - {nivel_nombre}")
        
        # Crear resumen de cartas generadas
        resumen_df = pd.DataFrame(cartas_generadas)
        resumen_filename = f"Cartas_Disciplinarias/RESUMEN_Cartas_Generadas_{fecha_actual.replace('-', '')}.xlsx"
        resumen_df.to_excel(resumen_filename, index=False)
        
        print(f"\n✅ Total cartas generadas: {len(cartas_generadas)}")
        print(f"📁 Directorio: Cartas_Disciplinarias/")
        print(f"📊 Resumen: {resumen_filename}")
        
        return cartas_generadas
        
    except Exception as e:
        print(f"❌ Error generando cartas: {e}")
        return []

def create_flow_explanation_pdf():
    """
    Crea un PDF explicativo del flujo de consecuencias
    """
    print("\n📄 GENERANDO PDF EXPLICATIVO DEL FLUJO")
    print("=" * 60)
    
    filename = f"FLUJO_CONSECUENCIAS_EXPLICATIVO_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.darkblue
    )
    
    story.append(Paragraph("FLUJO DE CONSECUENCIAS DISCIPLINARIAS", title_style))
    story.append(Paragraph("SISTEMA MENSUAL DE FEEDBACKS", title_style))
    story.append(Spacer(1, 20))
    
    # Introducción
    intro_style = ParagraphStyle(
        'Intro',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        alignment=4  # Justify
    )
    
    intro_text = """
    Este documento establece el flujo de consecuencias disciplinarias para vendedores/conductores 
    que no cumplan con la realización de feedbacks mensuales. El sistema implementa medidas 
    progresivas que buscan corregir el comportamiento y asegurar el cumplimiento de los 
    procedimientos establecidos.
    """
    
    story.append(Paragraph(intro_text, intro_style))
    story.append(Spacer(1, 20))
    
    # Jerarquía de responsables
    story.append(Paragraph("JERARQUÍA DE RESPONSABLES", styles['Heading2']))
    
    jerarquia_data = [
        ['NIVEL', 'RESPONSABLE', 'CARGO'],
        ['1', 'Óscar Cuellar', 'Coordinador de Distribución'],
        ['2', 'Óscar Cuellar', 'Coordinador de Distribución'],
        ['3', 'Óscar Portillo', 'Jefe de Distribución'],
        ['4', 'Félix Chávez', 'Gerente CD Soyapango']
    ]
    
    jerarquia_table = Table(jerarquia_data, colWidths=[1*inch, 2.5*inch, 2.5*inch])
    jerarquia_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(jerarquia_table)
    story.append(Spacer(1, 20))
    
    # Niveles de consecuencias
    story.append(Paragraph("NIVELES DE CONSECUENCIAS", styles['Heading2']))
    
    # NIVEL 1
    story.append(Paragraph("NIVEL 1 - LLAMADA DE ATENCIÓN VERBAL", styles['Heading3']))
    nivel1_text = """
    <b>Aplicación:</b> Primer incumplimiento mensual<br/>
    <b>Responsable:</b> Coordinador de Distribución<br/>
    <b>Plazo máximo:</b> 48 horas desde detección<br/>
    <b>Documentación:</b> Constancia de llamada de atención verbal<br/>
    <b>Archivo:</b> No se archiva en expediente<br/>
    <b>Consecuencia del próximo incumplimiento:</b> Amonestación escrita
    """
    story.append(Paragraph(nivel1_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # NIVEL 2
    story.append(Paragraph("NIVEL 2 - AMONESTACIÓN ESCRITA", styles['Heading3']))
    nivel2_text = """
    <b>Aplicación:</b> Segundo incumplimiento mensual<br/>
    <b>Responsable:</b> Coordinador de Distribución<br/>
    <b>Plazo máximo:</b> 3 días desde detección<br/>
    <b>Documentación:</b> Amonestación escrita formal<br/>
    <b>Archivo:</b> SÍ - Expediente personal<br/>
    <b>Consecuencia del próximo incumplimiento:</b> Suspensión de 1 día
    """
    story.append(Paragraph(nivel2_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # NIVEL 3
    story.append(Paragraph("NIVEL 3 - SUSPENSIÓN", styles['Heading3']))
    nivel3_text = """
    <b>Aplicación:</b> Tercer incumplimiento mensual<br/>
    <b>Responsable:</b> Jefe de Distribución<br/>
    <b>Plazo máximo:</b> 5 días desde detección<br/>
    <b>Documentación:</b> Acta de suspensión<br/>
    <b>Archivo:</b> SÍ - Expediente personal + Jefatura<br/>
    <b>Sanción:</b> 1 día sin goce de sueldo<br/>
    <b>Consecuencia del próximo incumplimiento:</b> Evaluación gerencial
    """
    story.append(Paragraph(nivel3_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # NIVEL 4
    story.append(Paragraph("NIVEL 4 - EVALUACIÓN GERENCIAL", styles['Heading3']))
    nivel4_text = """
    <b>Aplicación:</b> Cuarto incumplimiento o más<br/>
    <b>Responsable:</b> Gerente CD Soyapango + Comité<br/>
    <b>Plazo máximo:</b> 1 semana desde detección<br/>
    <b>Documentación:</b> Citación y acta de evaluación<br/>
    <b>Archivo:</b> SÍ - Todos los niveles organizacionales<br/>
    <b>Opciones de sanción:</b> Suspensión extendida, capacitación obligatoria, 
    cambio de ruta, o medidas según evaluación
    """
    story.append(Paragraph(nivel4_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Proceso mensual
    story.append(Paragraph("PROCESO MENSUAL", styles['Heading2']))
    
    proceso_data = [
        ['PASO', 'ACTIVIDAD', 'RESPONSABLE', 'PLAZO'],
        ['1', 'Identificar rutas sin feedback', 'Coordinador', 'Día 1 del mes siguiente'],
        ['2', 'Generar cartas disciplinarias', 'Coordinador', 'Día 2'],
        ['3', 'Notificar a vendedores', 'Coordinador/Jefe', 'Día 3'],
        ['4', 'Ejecutar consecuencias', 'Según nivel', 'Máximo día 8'],
        ['5', 'Documentar en expedientes', 'Coordinador', 'Día 10'],
        ['6', 'Seguimiento y monitoreo', 'Jefe/Gerente', 'Continuo']
    ]
    
    proceso_table = Table(proceso_data, colWidths=[0.8*inch, 2.2*inch, 1.5*inch, 1.5*inch])
    proceso_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(proceso_table)
    story.append(Spacer(1, 20))
    
    # Notas importantes
    story.append(Paragraph("NOTAS IMPORTANTES", styles['Heading2']))
    
    notas_text = """
    • Este sistema es de aplicación MENSUAL, no semanal o quincenal<br/>
    • Cada incumplimiento debe ser documentado apropiadamente<br/>
    • Los plazos son máximos y deben respetarse estrictamente<br/>
    • El sistema busca la corrección, no la sanción excesiva<br/>
    • Recursos Humanos NO participa en este proceso disciplinario<br/>
    • Mantener confidencialidad en el manejo de expedientes<br/>
    • Revisar efectividad del sistema trimestralmente
    """
    
    story.append(Paragraph(notas_text, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Footer
    footer_text = f"""
    <b>Documento generado:</b> {datetime.now().strftime('%d de %B de %Y')}<br/>
    <b>Sistema:</b> Flujo de Consecuencias Mensual v1.0<br/>
    <b>Vigencia:</b> A partir de la fecha de implementación
    """
    
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    
    print(f"✅ PDF generado: {filename}")
    return filename

def main():
    """
    Función principal para generar cartas y PDF explicativo
    """
    print("🎯 GENERADOR DE CARTAS DISCIPLINARIAS Y PDF EXPLICATIVO")
    print("=" * 70)
    
    # Generar cartas para rutas
    cartas = generate_cartas_for_routes()
    
    # Generar PDF explicativo
    pdf_file = create_flow_explanation_pdf()
    
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print(f"📁 Cartas generadas: {len(cartas)}")
    print(f"📄 PDF explicativo: {pdf_file}")
    print(f"📂 Directorio cartas: Cartas_Disciplinarias/")
    
    print(f"\n📋 ARCHIVOS LISTOS PARA USAR:")
    print(f"   • Cartas individuales por ruta y nivel")
    print(f"   • PDF explicativo completo del sistema")
    print(f"   • Resumen Excel de cartas generadas")
    
    print(f"\n⚡ PRÓXIMOS PASOS:")
    print(f"   1. Revisar cartas generadas en el directorio")
    print(f"   2. Imprimir cartas según el nivel correspondiente")
    print(f"   3. Aplicar las medidas disciplinarias")
    print(f"   4. Documentar la ejecución en el sistema")

if __name__ == "__main__":
    main()
