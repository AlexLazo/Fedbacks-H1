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
        # Cargar el archivo HEADCOUNT de Octubre - HOJA BASE con datos individuales
        headcount_file = "BASE HEADCOUNT OCTUBRE - 2025.xlsm"
        headcount_df = pd.read_excel(headcount_file, sheet_name='BASE', header=0, engine='openpyxl')
        
        # Limpiar nombres de columnas (quitar espacios extra)
        headcount_df.columns = headcount_df.columns.str.strip()
        
        print(f"✅ BASE HEADCOUNT OCTUBRE cargada: {len(headcount_df)} registros")
        
        # Mostrar las columnas disponibles para verificar
        print(f"📋 Columnas disponibles: {list(headcount_df.columns)}")
        
        # Mostrar una muestra de datos para verificar
        print("📋 Muestra de datos HEADCOUNT:")
        if len(headcount_df) > 0:
            cols_to_show = []
            if 'RUTA' in headcount_df.columns:
                cols_to_show.append('RUTA')
            if 'NOMBRE COMPLETO EMPLEADO' in headcount_df.columns:
                cols_to_show.append('NOMBRE COMPLETO EMPLEADO')
            if 'NOMBRE - SUPERVISOR' in headcount_df.columns:
                cols_to_show.append('NOMBRE - SUPERVISOR')
            if 'CONTRATISTA' in headcount_df.columns:
                cols_to_show.append('CONTRATISTA')
            if 'PUESTO' in headcount_df.columns:
                cols_to_show.append('PUESTO')
            
            if cols_to_show:
                print(headcount_df[cols_to_show].head(3))
        
        return headcount_df
        
    except Exception as e:
        print(f"❌ Error cargando BASE HEADCOUNT: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_signatures_for_date():
    """Return current signatures"""
    return [
        {"name": "Roney Rivas", "title": "TL de Ventas"},
        {"name": "Félix Chávez", "title": "Gerente CD Soyapango"},
        {"name": "Óscar Portillo", "title": "Jefe de Distribución"},
        {"name": "Óscar Cuellar", "title": "Coordinador de Distribución"}
    ]

def generar_flujo_consecuencias_con_cartas(mes=5, año=2025):
    """
    Genera el flujo de consecuencias mensual con cartas PDF personalizadas
    """
    # Nombres de meses en español
    meses_español = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    mes_nombre = meses_español[mes]
    
    print(f"📋 GENERANDO FLUJO DE CONSECUENCIAS CON CARTAS PDF: {mes_nombre.upper()} {año}")
    print("=" * 80)
    
    try:
        # Cargar datos principales
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        headcount_df = load_headcount_data()
        
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
        
        # Calcular fecha de detección (primer día del mes siguiente)
        if mes == 12:  # Si es diciembre, siguiente mes es enero del año siguiente
            fecha_deteccion = datetime(año + 1, 1, 1)
        else:
            fecha_deteccion = datetime(año, mes + 1, 1)
        
        def fecha_en_español(fecha_dt):
            """Convierte una fecha a formato español"""
            meses_es = [
                '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
            ]
            dia = fecha_dt.day
            mes = meses_es[fecha_dt.month]
            año = fecha_dt.year
            return f"{dia} de {mes} de {año}"
        
        fecha_deteccion_str = fecha_en_español(fecha_deteccion)
        
        # Crear lista de rutas para consecuencias con datos completos
        rutas_consecuencias = []
        rutas_sin_datos_headcount = []
        
        for ruta in sorted(rutas_sin_feedback):
            # Buscar información en la base de rutas
            info_ruta = rutas_df[rutas_df['RUTA'] == ruta]
            
            reparto_nombre = None
            supervisor_nombre = None
            contratista_nombre = None
            datos_encontrados = False
            
            # Buscar en HEADCOUNT para obtener datos completos
            if headcount_df is not None and 'RUTA' in headcount_df.columns:
                try:
                    # Buscar por ruta exacta
                    headcount_match = headcount_df[headcount_df['RUTA'] == ruta]
                    
                    if not headcount_match.empty:
                        # Tomar el primer empleado de la ruta (CONDUCTOR, que es el principal)
                        # Filtrar por CONDUCTOR si es posible
                        conductores = headcount_match[headcount_match['PUESTO'].str.contains('CONDUCTOR', case=False, na=False)]
                        if not conductores.empty:
                            empleado_principal = conductores.iloc[0]
                        else:
                            empleado_principal = headcount_match.iloc[0]
                        
                        # Obtener nombre completo del empleado
                        if 'NOMBRE COMPLETO EMPLEADO' in headcount_match.columns and pd.notna(empleado_principal['NOMBRE COMPLETO EMPLEADO']):
                            reparto_nombre = str(empleado_principal['NOMBRE COMPLETO EMPLEADO']).strip()
                        
                        # Obtener supervisor del nombre
                        if 'NOMBRE - SUPERVISOR' in headcount_match.columns and pd.notna(empleado_principal['NOMBRE - SUPERVISOR']):
                            supervisor_nombre = str(empleado_principal['NOMBRE - SUPERVISOR']).strip()
                        
                        # Obtener contratista
                        if 'CONTRATISTA' in headcount_match.columns and pd.notna(empleado_principal['CONTRATISTA']):
                            contratista_nombre = str(empleado_principal['CONTRATISTA']).strip()
                        
                        # Verificar que al menos tengamos el nombre del reparto
                        if reparto_nombre:
                            datos_encontrados = True
                            print(f"✅ Datos encontrados para {ruta}: {reparto_nombre} - Supervisor: {supervisor_nombre} - Contratista: {contratista_nombre}")
                        else:
                            print(f"⚠️ Datos incompletos en HEADCOUNT para ruta {ruta} - No se generará carta")
                            rutas_sin_datos_headcount.append(ruta)
                    else:
                        print(f"⚠️ Ruta {ruta} no encontrada en HEADCOUNT - No se generará carta")
                        rutas_sin_datos_headcount.append(ruta)
                        
                except Exception as e:
                    print(f"❌ Error buscando en HEADCOUNT para {ruta}: {e}")
                    rutas_sin_datos_headcount.append(ruta)
            else:
                print(f"❌ HEADCOUNT no disponible para ruta {ruta} - No se generará carta")
                rutas_sin_datos_headcount.append(ruta)
            
            # Solo agregar a la lista si se encontraron datos válidos
            if datos_encontrados and reparto_nombre:
                rutas_consecuencias.append({
                    'RUTA': ruta,
                    'REPARTO': reparto_nombre,
                    'SUPERVISOR': supervisor_nombre if supervisor_nombre else 'No especificado',
                    'CONTRATISTA': contratista_nombre if contratista_nombre else 'No especificado',
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
        
        # Mostrar resumen de rutas sin datos
        if rutas_sin_datos_headcount:
            print(f"\n⚠️ RUTAS SIN DATOS EN HEADCOUNT (no se generarán cartas): {len(rutas_sin_datos_headcount)}")
            print(f"   Rutas: {', '.join(sorted(rutas_sin_datos_headcount))}")
        
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
            'CON_DATOS_HEADCOUNT': len(rutas_consecuencias),
            'SIN_DATOS_HEADCOUNT': len(rutas_sin_datos_headcount),
            'CARTAS_GENERADAS': len(rutas_consecuencias),
            'PORCENTAJE_CUMPLIMIENTO': round((len(rutas_con_feedback) / len(todas_las_rutas)) * 100, 1),
            'ARCHIVO_RUTAS_USADO': archivo_usado,
            'FECHA_GENERACION': datetime.now().strftime('%Y-%m-%d %H:%M')
        }]
        
        df_resumen = pd.DataFrame(resumen)
        
        # Generar archivo Excel
        excel_filename = f"Consecuencias_COMPLETO_{mes_nombre}_{año}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
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
            worksheet.set_column('D:D', 20)  # CONTRATISTA
            worksheet.set_column('E:M', 18)  # Resto de columnas
        
        print(f"✅ Archivo Excel generado: {excel_filename}")
        
        # Generar cartas PDF para cada ruta
        if len(rutas_sin_feedback) > 0:
            generar_cartas_pdf(df_consecuencias, mes_nombre, año, fecha_deteccion_str)
        
        # Generar PDF del flujo completo
        generar_pdf_flujo_completo(df_guia, mes_nombre, año, df_resumen)
        
        return excel_filename, len(rutas_sin_feedback)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, 0

def generar_cartas_pdf(df_consecuencias, mes_nombre, año, fecha_deteccion_str):
    """
    Genera cartas PDF individuales para cada ruta usando el formato del weekly report
    """
    print(f"\n📄 GENERANDO CARTAS PDF PARA {len(df_consecuencias)} RUTAS...")
    
    # Crear directorio para las cartas
    cartas_dir = f"Cartas_{mes_nombre}_{año}"
    if not os.path.exists(cartas_dir):
        os.makedirs(cartas_dir)
    
    for _, row in df_consecuencias.iterrows():
        ruta = row['RUTA']
        reparto = row['REPARTO']
        supervisor = row['SUPERVISOR']
        contratista = row['CONTRATISTA']
        
        # Crear carta PDF
        filename = f"{cartas_dir}/Carta_Incumplimiento_{ruta}_{mes_nombre}_{año}.pdf"
        
        crear_carta_individual_pdf(filename, ruta, reparto, supervisor, contratista, mes_nombre, año, fecha_deteccion_str)
    
    print(f"✅ {len(df_consecuencias)} cartas PDF generadas en directorio: {cartas_dir}")

def crear_carta_individual_pdf(filename, ruta, reparto, supervisor, contratista, mes_nombre, año, fecha_deteccion_str):
    """
    Crea una carta PDF individual usando el formato del weekly report
    """
    # Crear documento PDF
    doc = SimpleDocTemplate(
        filename, 
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        title=f"Carta Incumplimiento {ruta}",
        author="CD Soyapango",
        subject=f"Incumplimiento Feedback {mes_nombre} {año}"
    )
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=1,  # Center
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=0.2*inch,
        spaceBefore=0
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=6,
        alignment=4  # Justified
    )
    
    # Construir el contenido
    story = []
    
    # Logo de la empresa
    try:
        logo_path = "LogoConst.png"
        logo_img = Image(logo_path, width=2*inch, height=0.8*inch)
        logo_table = Table([[logo_img]], colWidths=[6*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        story.append(logo_table)
    except Exception as e:
        # Fallback a texto si no hay logo
        company_name = "LA CONSTANCIA"
        subtitle = "ABInBev"
        header_data = [[company_name], [subtitle]]
        header_table = Table(header_data, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, 1), 12),
        ]))
        story.append(header_table)
    
    story.append(Spacer(1, 0.2*inch))
    
    # Usar fecha de detección (primer día del mes siguiente) en lugar de fecha actual
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        alignment=2,  # Right-aligned
        fontSize=10
    )
    story.append(Paragraph(fecha_deteccion_str, date_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Título
    story.append(Paragraph("NOTIFICACIÓN DE INCUMPLIMIENTO", title_style))
    story.append(Paragraph("FEEDBACK MENSUAL DE RUTA", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Contenido de la carta
    contenido = f"""
Estimado(a) <b>{reparto}</b>,<br/><br/>

Por medio de la presente le notificamos que se ha detectado el incumplimiento en la realización del 
feedback mensual correspondiente al mes de <b>{mes_nombre} {año}</b> para la ruta <b>{ruta}</b> 
bajo su responsabilidad.<br/><br/>

Como es de su conocimiento, los feedbacks mensuales son una herramienta fundamental para el 
mejoramiento continuo de nuestros procesos de distribución y la calidad del servicio que 
brindamos a nuestros clientes. El incumplimiento de esta responsabilidad afecta directamente 
nuestros objetivos de excelencia operacional.<br/><br/>

<b>DETALLE DEL INCUMPLIMIENTO:</b><br/>
• Ruta: {ruta}<br/>
• Reparto responsable: {reparto}<br/>
• Supervisor inmediato: {supervisor}<br/>
• Contratista: {contratista}<br/>
• Mes de incumplimiento: {mes_nombre} {año}<br/>
• Fecha de detección: {fecha_deteccion_str}<br/><br/>

Solicitamos de manera urgente que se presente con su supervisor inmediato <b>{supervisor}</b> 
para recibir la instrucción correspondiente y establecer las medidas necesarias para evitar 
futuros incumplimientos.<br/><br/>

Recordamos que el cumplimiento puntual de los feedbacks mensuales es una responsabilidad 
inherente a su posición y forma parte de los estándares de desempeño establecidos por la empresa 
y su contratista <b>{contratista}</b>.<br/><br/>

Sin otro particular, y esperando su pronta respuesta y mejora en el cumplimiento de sus 
responsabilidades, nos despedimos cordialmente.
"""
    
    story.append(Paragraph(contenido, normal_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Firmas simplificadas: Solo Reparto y Supervisor
    firma_data = [
        ["_____________________", "_____________________"],
        [f"{reparto}", f"{supervisor}"],
        ["Reparto Responsable", "Supervisor Inmediato"]
    ]
    
    sig_table = Table(firma_data, colWidths=[3*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(sig_table)
    
    # Construir PDF
    doc.build(story)

def generar_pdf_flujo_completo(df_guia, mes_nombre, año, df_resumen):
    """
    Genera un PDF explicando todo el flujo de consecuencias y sus etapas
    """
    filename = f"Manual_Flujo_Consecuencias_{mes_nombre}_{año}.pdf"
    
    doc = SimpleDocTemplate(
        filename, 
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        title="Manual de Flujo de Consecuencias",
        author="CD Soyapango",
        subject=f"Flujo de Consecuencias {mes_nombre} {año}"
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=16,
        fontName='Helvetica-Bold',
        spaceAfter=0.3*inch,
        spaceBefore=0
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=13,
        fontName='Helvetica-Bold',
        spaceAfter=0.15*inch,
        spaceBefore=0.2*inch
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceBefore=6,
        spaceAfter=6,
        alignment=4
    )
    
    story = []
    
    # Logo y encabezado
    try:
        logo_path = "LogoConst.png"
        logo_img = Image(logo_path, width=2*inch, height=0.8*inch)
        logo_table = Table([[logo_img]], colWidths=[6*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        story.append(logo_table)
    except:
        story.append(Paragraph("LA CONSTANCIA - ABInBev", heading_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Título principal
    story.append(Paragraph("MANUAL DE FLUJO DE CONSECUENCIAS", title_style))
    story.append(Paragraph("INCUMPLIMIENTO DE FEEDBACKS MENSUALES", title_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Introducción
    story.append(Paragraph("1. INTRODUCCIÓN", heading_style))
    intro_text = """
El presente manual establece el flujo de consecuencias progresivas para el personal de repartos 
que incumplan con la realización de los feedbacks mensuales. Este sistema busca garantizar el 
cumplimiento de los estándares de calidad y mejora continua en nuestros procesos de distribución.
"""
    story.append(Paragraph(intro_text, normal_style))
    
    # Objetivos
    story.append(Paragraph("2. OBJETIVOS", heading_style))
    objetivos_text = """
• Establecer un sistema claro y progresivo de consecuencias disciplinarias<br/>
• Promover el cumplimiento puntual de los feedbacks mensuales<br/>
• Mejorar la calidad de los procesos de distribución<br/>
• Mantener estándares de excelencia operacional<br/>
• Documentar adecuadamente todas las acciones disciplinarias
"""
    story.append(Paragraph(objetivos_text, normal_style))
    
    # Niveles de consecuencias
    story.append(Paragraph("3. NIVELES DE CONSECUENCIAS", heading_style))
    
    for _, nivel in df_guia.iterrows():
        story.append(Paragraph(f"<b>{nivel['NIVEL']}:</b> {nivel['ACCION']}", normal_style))
        story.append(Paragraph(f"Responsable: {nivel['RESPONSABLE']}", normal_style))
        story.append(Paragraph(f"Plazo máximo: {nivel['PLAZO']}", normal_style))
        story.append(Paragraph(f"Aplica para: {nivel['DESCRIPCION']}", normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Jerarquía corregida
    story.append(Paragraph("4. JERARQUÍA DE RESPONSABLES", heading_style))
    jerarquia_text = """
<b>NIVEL 1 - Supervisor de Distribución:</b><br/>
• Primera instancia de control<br/>
• Aplicación de llamadas de atención verbales<br/>
• Seguimiento directo con los repartos<br/><br/>

<b>NIVEL 2 - Coordinador de Distribución:</b><br/>
• Aplicación de amonestaciones escritas<br/>
• Supervisión del cumplimiento general<br/>
• Generación de reportes mensuales<br/><br/>

<b>NIVEL 3 - Jefe de Distribución:</b><br/>
• Autorización de suspensiones<br/>
• Revisión de casos complejos<br/>
• Toma de decisiones disciplinarias importantes<br/><br/>

<b>NIVEL 4 - Gerente CD Soyapango:</b><br/>
• Casos extremos y evaluaciones finales<br/>
• Decisiones de impacto mayor<br/>
• Supervisión general del sistema
"""
    story.append(Paragraph(jerarquia_text, normal_style))
    
    # Proceso
    story.append(Paragraph("5. PROCESO DE APLICACIÓN", heading_style))
    proceso_text = """
<b>5.1 Detección del Incumplimiento</b><br/>
Al final de cada mes, se genera automáticamente el reporte que identifica las rutas 
que no realizaron su feedback mensual.<br/><br/>

<b>5.2 Notificación</b><br/>
Se genera una carta PDF personalizada para cada ruta incumplida, con datos completos 
del reparto y supervisor obtenidos de la BASE HEADCOUNT.<br/><br/>

<b>5.3 Aplicación de Consecuencias</b><br/>
Según el historial de incumplimientos, se aplica el nivel correspondiente respetando 
la jerarquía establecida.<br/><br/>

<b>5.4 Documentación</b><br/>
Todas las acciones se documentan en el sistema Excel y se archivan las cartas PDF 
generadas como evidencia.<br/><br/>

<b>5.5 Seguimiento</b><br/>
Monitoreo mensual para verificar efectividad y ajustar el sistema según resultados.
"""
    story.append(Paragraph(proceso_text, normal_style))
    
    # Construir PDF
    doc.build(story)
    
    print(f"✅ Manual PDF generado: {filename}")

def main():
    """
    Función principal - Genera cartas para múltiples meses
    """
    # 🔧 CONFIGURACIÓN - Cambiar estos valores según necesites:
    MESES = [5, 6, 7, 8, 9]  # Mayo a Septiembre
    AÑO = 2025   # Año a analizar
    
    print("🎯 GENERADOR DE FLUJO DE CONSECUENCIAS CON CARTAS PDF")
    print("=" * 80)
    print("📋 CORREGIDO: Repartos, sin Comité, con Supervisor de Distribución")
    print("📄 Cartas PDF + Manual PDF + Excel completo")
    print("📅 FECHA EN CARTAS: Primer día del mes siguiente al incumplimiento")
    print(f"📅 GENERANDO PARA MESES: {MESES} del año {AÑO}")
    print("=" * 80)
    
    # Contador de resultados
    total_archivos = 0
    total_rutas_accion = 0
    resultados = []
    
    # Generar para cada mes
    for mes in MESES:
        meses_nombres = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        print(f"\n{'='*80}")
        print(f"📅 PROCESANDO: {meses_nombres[mes]} {AÑO}")
        print(f"{'='*80}")
        
        archivo, total_rutas = generar_flujo_consecuencias_con_cartas(mes, AÑO)
        
        if archivo:
            total_archivos += 1
            total_rutas_accion += total_rutas
            resultados.append({
                'mes': meses_nombres[mes],
                'archivo': archivo,
                'rutas': total_rutas
            })
            print(f"✅ {meses_nombres[mes]}: {total_rutas} rutas procesadas")
        else:
            print(f"❌ {meses_nombres[mes]}: Error al procesar")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO PARA TODOS LOS MESES")
    print("=" * 80)
    print(f"� RESUMEN GENERAL:")
    print(f"   • Meses procesados: {total_archivos}/{len(MESES)}")
    print(f"   • Total de rutas para acción: {total_rutas_accion}")
    print(f"\n� ARCHIVOS GENERADOS POR MES:")
    
    for resultado in resultados:
        print(f"\n   📅 {resultado['mes']}:")
        print(f"      • Excel: {resultado['archivo']}")
        print(f"      • Cartas PDF: {resultado['rutas']} archivos")
        print(f"      • Directorio: Cartas_{resultado['mes']}_{AÑO}/")
    
    print(f"\n🎯 ARCHIVOS GENERADOS PARA CADA MES:")
    print(f"   • Excel completo con datos HEADCOUNT")
    print(f"   • Cartas PDF personalizadas por ruta")
    print(f"   • Manual PDF explicativo del flujo")
    
    print(f"\n📋 SIGUIENTES PASOS:")
    print(f"1. Revisar los Excel de cada mes con datos completos")
    print(f"2. Asignar niveles según historial de cada ruta")
    print(f"3. Entregar cartas PDF a supervisores correspondientes")
    print(f"4. Aplicar acciones según jerarquía corregida")
    print(f"5. Documentar ejecución en los Excel")
    
    print(f"\n✅ SISTEMA LISTO PARA IMPLEMENTACIÓN")

if __name__ == "__main__":
    main()
