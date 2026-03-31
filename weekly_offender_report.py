import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import calendar
import os
import re
import io

# Define function to get signatures based on date
def get_signatures_for_date(week, year):
    """Return appropriate signatures based on the date"""
    # Calcular la fecha aproximada de la semana
    # Usar el primer día de la semana para determinar el período
    date_obj = datetime.strptime(f'{year}-W{week:02d}-1', "%Y-W%W-%w")
    
    # 14 de marzo como fecha de cambio (asumiendo 2025)
    cutoff_date = datetime(2025, 3, 14)
    
    if date_obj < cutoff_date:
        # Firmas antes del 14 de marzo
        return [
            {"name": "Roney Rivas", "title": "TL de Ventas"},
            {"name": "Rafael Osorio", "title": "Gerente CD Soyapango"},
            {"name": "Manuel Elías", "title": "Coordinador de Distribución"},
            {"name": "Elías Montesinos", "title": "Supervisor de Distribución"}
        ]
    else:
        # Firmas después del 14 de marzo (actuales)
        return [
            {"name": "Roney Rivas", "title": "TL de Ventas"},
            {"name": "Félix Chávez", "title": "Gerente CD Soyapango"},
            {"name": "Óscar Portillo", "title": "Jefe de Distribución"},
            {"name": "Óscar Cuellar", "title": "Coordinador de Distribución"}
        ]

# Define the default signatures for backward compatibility
SIGNATURES = [
    {"name": "Roney Rivas", "title": "TL de Ventas"},
    {"name": "Félix Chávez", "title": "Gerente CD Soyapango"},
    {"name": "Óscar Portillo", "title": "Jefe de Distribución"},
    {"name": "Óscar Cuellar", "title": "Supervisor de Distribución"}
]

# Planes de acción simplificados y escalables
MOTIVO_ACTION_PLANS = {
    # Top 1: Cliente demorado en recibir o pagar (30.2% de casos)
    'Cliente demorado en recibir o pagar': {
        'plan': 'Coordinación previa con cliente y ventana horaria específica',
        'intro': 'demoras en recepción y pago',
        'accion_especifica': 'coordinación previa y ventanas horarias',
        'objetivo': 'reducir demoras en la ruta',
        'conclusion': 'mejorando la eficiencia operativa'
    },
    
    # Top 2: Cliente crítico en atención (Safety) (25.4% de casos)
    'Cliente critico en atención (ubicación y/o acceso) - Requiere visita de Safety': {
        'plan': 'Evaluación de seguridad y protocolo de entrega segura',
        'intro': 'situaciones críticas de seguridad',
        'accion_especifica': 'evaluación de seguridad especializada',
        'objetivo': 'garantizar la seguridad del personal',
        'conclusion': 'protegiendo al equipo'
    },
    
    # Top 3: Cliente con novedad en envase (5.9% de casos)
    'Cliente con novedad en envase': {
        'plan': 'Inspección de envases y protocolo de limpieza',
        'intro': 'problemas con envases',
        'accion_especifica': 'inspección y limpieza de envases',
        'objetivo': 'entregar envases en buen estado',
        'conclusion': 'eliminando reclamos'
    },
    
    # Top 4: Cliente reiterativo en rechazo (5.6% de casos)
    'Cliente reiterativo en rechazo': {
        'plan': 'Análisis de causas y ajuste de pedidos',
        'intro': 'rechazos repetitivos',
        'accion_especifica': 'análisis de causas y ajuste según histórico',
        'objetivo': 'reducir rechazos',
        'conclusion': 'mejorando la aceptación'
    },
    
    # Top 5: Cliente problemático o grosero (4.9% de casos)
    'Cliente problemático o grosero': {
        'plan': 'Capacitación en manejo de clientes difíciles',
        'intro': 'clientes problemáticos',
        'accion_especifica': 'capacitación especializada',
        'objetivo': 'mantener ambiente profesional',
        'conclusion': 'asegurando calidad del servicio'
    },
    
    # Otros motivos identificados en el análisis
    'Faltante de producto': {
        'plan': 'Checklist de verificación y control de inventario',
        'intro': 'faltantes de productos',
        'accion_especifica': 'checklist de verificación',
        'objetivo': 'asegurar disponibilidad completa',
        'conclusion': 'eliminando faltantes'
    },
    
    'Calidad del producto (avería, rotura, mal olor, mala presentación)': {
        'plan': 'Control de calidad pre-despacho',
        'intro': 'problemas de calidad',
        'accion_especifica': 'control de calidad previo',
        'objetivo': 'asegurar calidad óptima',
        'conclusion': 'eliminando reclamos'
    }
}

def load_data():
    """Load and preprocess the feedback data"""
    try:
        # Load the feedbacks data
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        
        # Convert date columns
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        feedbacks_df['fecha_cierre'] = pd.to_datetime(feedbacks_df['fecha_cierre'])
        
        # Create time-based columns for analysis
        feedbacks_df['year'] = feedbacks_df['fecha_registro'].dt.year
        feedbacks_df['month'] = feedbacks_df['fecha_registro'].dt.month
        feedbacks_df['week'] = feedbacks_df['fecha_registro'].dt.isocalendar().week
        feedbacks_df['weekday'] = feedbacks_df['fecha_registro'].dt.day_name()
        
        # Calculate resolution time in days for closed issues
        feedbacks_df['tiempo_cierre_dias'] = (
            feedbacks_df['fecha_cierre'] - feedbacks_df['fecha_registro']
        ).dt.days.fillna(0)
        
        # Try to load the routes database
        try:
            # First try to load the most recent month-specific database
            current_month = datetime.now().strftime("%B")
            month_map = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            month_esp = month_map.get(current_month, current_month)
            
            month_file = f'BD_Rutas_{month_esp}.xlsx'
            if os.path.exists(month_file):
                rutas_df = pd.read_excel(month_file)
            else:
                rutas_df = pd.read_excel('BD_Rutas.xlsx')
                
            # Merge with the routes data
            merged_df = feedbacks_df.merge(
                rutas_df,
                left_on='ruta',
                right_on='RUTA',
                how='left'
            )
            
            return merged_df, rutas_df
            
        except Exception as e:
            print(f"Warning: Could not load routes database. Using only feedbacks data: {e}")
            return feedbacks_df, None
            
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def is_valid_client(client_code, client_name):
    """
    Check if a client code and name are valid based on requirements
    Invalid examples: 'Cliente-0 Bodega', 'Cliente-00 000', 'Cliente-0001', points, commas, etc.
    """
    # Check for invalid patterns in code
    if not isinstance(client_code, str):
        client_code = str(client_code)
        
    invalid_code_patterns = [
        r'^0+$',                  # All zeros
        r'^0+\s*[Bb]odega$',      # Zeros followed by "Bodega"
        r'^[0]+\s*$',             # Just zeros with spaces
        r'^[.,]+$',               # Just dots or commas
        r'^\s*$',                 # Empty or just spaces
        r'^0001\.*$'              # "0001" pattern possibly followed by dots
    ]
    
    # Check for invalid patterns in name
    if not isinstance(client_name, str):
        client_name = str(client_name)
        
    invalid_name_patterns = [
        r'^[.,]+$',               # Just dots or commas
        r'^\s*$',                 # Empty or just spaces
        r'^[Bb]odega$',           # Just "Bodega"
        r'^[0-9,.\s]+$'           # Just numbers, commas, dots and/or spaces
    ]
    
    # Check if any invalid pattern matches
    for pattern in invalid_code_patterns:
        if re.match(pattern, client_code):
            return False
    
    for pattern in invalid_name_patterns:
        if re.match(pattern, client_name):
            return False
    
    return True

def get_weekly_offenders(data, week=None, year=None, top_n=5):
    """
    Get the top N clients with the most reported issues for a specific week
    """
    # If week is not provided, use the current week
    if week is None:
        today = datetime.now()
        week = today.isocalendar()[1]
    
    # If year is not provided, use the current year
    if year is None:
        year = datetime.now().year
    
    # Filter by week and year
    weekly_data = data[
        (data['week'] == week) &
        (data['year'] == year)
    ]
    
    # If there's no data for the specified week, return empty dataframe
    if weekly_data.empty:
        return pd.DataFrame()
    
    # Find the most reported issue for the week
    issue_counts = weekly_data['respuesta_sub'].value_counts()
    if issue_counts.empty:
        return pd.DataFrame()
    
    most_reported_issue = issue_counts.idxmax()    # Filter by the most reported issue
    issue_data = weekly_data[weekly_data['respuesta_sub'] == most_reported_issue]
    
    # PRIMERO: Limpiar nombres duplicados en los datos originales
    def clean_name_universal(name):
        """Limpiar nombres duplicados universalmente"""
        clean_name = str(name).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name.strip())
        
        # Método 1: División de palabras para detectar duplicaciones
        words = clean_name.split()
        total_words = len(words)
        
        if total_words >= 2:
            for split_point in range(1, total_words):
                first_part = words[:split_point]
                remaining_words = words[split_point:]
                
                if len(remaining_words) == len(first_part):
                    if [w.lower() for w in first_part] == [w.lower() for w in remaining_words]:
                        clean_name = " ".join(first_part)
                        break
        
        # Método 2: Regex para duplicaciones
        iteration = 0
        max_iterations = 10
        
        while iteration < max_iterations:
            prev_name = clean_name
            clean_name = re.sub(r'(.+?)\s+\1$', r'\1', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'^(.+?)\s+\1\s*$', r'\1', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'^(.{2,})\1$', r'\1', clean_name, flags=re.IGNORECASE)
            
            if clean_name == prev_name:
                break
            iteration += 1
        
        # Método 3: Verificación de caracteres sin espacios
        if len(clean_name) > 4:
            text_no_spaces = clean_name.replace(' ', '')
            text_length = len(text_no_spaces)
            
            if text_length % 2 == 0:
                mid = text_length // 2
                first_half = text_no_spaces[:mid]
                second_half = text_no_spaces[mid:]
                
                if first_half.lower() == second_half.lower():
                    original_words = clean_name.split()
                    if len(original_words) % 2 == 0:
                        half_words = len(original_words) // 2
                        clean_name = " ".join(original_words[:half_words])
        
        # Método 4: Eliminar palabras duplicadas consecutivas
        final_words = []
        words = clean_name.split()
        prev_word = ""
        
        for word in words:
            if word.lower() != prev_word.lower():
                final_words.append(word)
                prev_word = word
        
        if final_words:
            clean_name = " ".join(final_words)
            
        return clean_name    # Aplicar limpieza de nombres ANTES del groupby (corregir warning de pandas)
    issue_data = issue_data.copy()  # Crear una copia para evitar el warning
    issue_data['nombre_cliente_clean'] = issue_data['nombre_cliente'].apply(clean_name_universal)
    
    # Extraer solo el código numérico del inicio de codigo_cliente
    issue_data['codigo_numerico'] = issue_data['codigo_cliente'].str.extract(r'^(\d+)')[0]
    
    # Group by NUMERIC client CODE only and count occurrences
    # Esto evita que el mismo cliente aparezca múltiples veces con nombres diferentes
    client_counts = issue_data.groupby('codigo_numerico').agg({
        'nombre_cliente_clean': 'first',  # Tomar el primer nombre limpio
        'codigo_numerico': 'size'          # Contar ocurrencias
    }).rename(columns={'codigo_numerico': 'count'}).reset_index()
    
    # Renombrar la columna para que el resto del código funcione
    client_counts = client_counts.rename(columns={'nombre_cliente_clean': 'nombre_cliente', 'codigo_numerico': 'codigo_cliente'})
    client_counts = client_counts.sort_values('count', ascending=False)
      # Filter out invalid clients 
    valid_clients = client_counts[client_counts.apply(lambda x: is_valid_client(x['codigo_cliente'], x['nombre_cliente']), axis=1)]
    
    # Remove duplicates by client code only - keep first occurrence
    valid_clients = valid_clients.drop_duplicates(subset=['codigo_cliente'], keep='first')
      # Get top N valid clients (limit to requested number)
    top_clients = valid_clients.head(top_n)
    
    # Add details for each client
    results = []
    for _, client in top_clients.iterrows():
        client_code = client['codigo_cliente']
        client_name = client['nombre_cliente']
        client_issue_count = client['count']
          # Get the client's specific data using numeric code
        client_data = issue_data[issue_data['codigo_numerico'] == client_code]        # Generate a comprehensive action plan based on the specific issue and client data
        def generate_specific_action_plan(issue_type, client_feedback_data):
            """Generate specific action plan based on the issue type and historical analysis"""
            
            # Buscar el plan específico en nuestro diccionario de motivos
            if issue_type in MOTIVO_ACTION_PLANS:
                return MOTIVO_ACTION_PLANS[issue_type]['plan']
            
            # Si no encuentra el motivo exacto, buscar por palabras clave
            issue_lower = issue_type.lower()
            
            # Buscar coincidencias parciales para motivos similares
            for motivo_key, motivo_data in MOTIVO_ACTION_PLANS.items():
                motivo_key_lower = motivo_key.lower()
                
                # Coincidencias específicas por palabras clave
                if ('demorado' in issue_lower or 'demora' in issue_lower or 'espera' in issue_lower) and 'demorado' in motivo_key_lower:
                    return motivo_data['plan']
                elif ('safety' in issue_lower or 'critico' in issue_lower or 'acceso' in issue_lower) and 'critico' in motivo_key_lower:
                    return motivo_data['plan']
                elif ('envase' in issue_lower or 'canasta' in issue_lower) and 'envase' in motivo_key_lower:
                    return motivo_data['plan']
                elif ('rechazo' in issue_lower or 'rechaza' in issue_lower) and 'rechazo' in motivo_key_lower:
                    return motivo_data['plan']
                elif ('problemático' in issue_lower or 'grosero' in issue_lower) and 'problemático' in motivo_key_lower:
                    return motivo_data['plan']
                elif ('faltante' in issue_lower or 'falta' in issue_lower) and 'faltante' in motivo_key_lower:
                    return motivo_data['plan']
                elif ('calidad' in issue_lower or 'rotura' in issue_lower or 'avería' in issue_lower) and 'calidad' in motivo_key_lower:
                    return motivo_data['plan']
            
            # Plan genérico si no encuentra coincidencia específica
            return "Análisis personalizado de la situación, identificación de causa raíz y implementación de plan de mejora específico"
        
        action_plan = generate_specific_action_plan(most_reported_issue, client_data)
        
        # Add to results - el nombre ya está limpio del groupby
        results.append({
            'codigo_cliente': client_code,
            'nombre_cliente': client_name,  # Ya está limpio
            'count': client_issue_count,
            'most_reported_issue': most_reported_issue,
            'action_plan': action_plan,
            'routes': client_data['ruta'].unique().tolist(),
            'last_date': client_data['fecha_registro'].max().strftime('%d/%m/%Y')
        })
    
    return pd.DataFrame(results)

def generate_weekly_report(offenders_data, week, year, output_file="weekly_offender_report.pdf"):
    """
    Generate a PDF report with the weekly offenders and action plans
    """
    if offenders_data.empty:
        print(f"No data available for week {week}, year {year}")
        return None
    
    # Create a buffer for PDF
    buffer = io.BytesIO()    # Create the PDF document with optimized margins to fit everything on one page
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=0.5*inch,     # Reduce left margin
        rightMargin=0.5*inch,    # Reduce right margin
        topMargin=0.4*inch,      # Reduce top margin further
        bottomMargin=0.3*inch,   # Reduce bottom margin further
        title="Reporte de clientes más reportados",
        author="CD Soyapango",
        subject=f"Reporte Semana {week} del {year}"
    )
      # Get styles - refined to match the example
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    # Define styles for table cells with proper wrapping
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=normal_style,
        fontSize=7,
        leading=9,  # line spacing
        alignment=0  # left aligned
    )
    
    centered_cell_style = ParagraphStyle(
        'CenteredCellStyle',
        parent=normal_style,
        fontSize=7,
        leading=9,
        alignment=1  # center aligned
    )
      # Main title style with reduced spacing
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=1,  # Center
        fontSize=13,  # Slightly smaller font
        fontName='Helvetica-Bold',
        spaceAfter=0.05*inch,  # Reduce space after title
        spaceBefore=0
    )
      # Subtitle style for week and problem with reduced spacing
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=11,  # Slightly smaller
        fontName='Helvetica-Bold',
        alignment=1,  # Center
        spaceAfter=0.1*inch,  # Reduce space after
        spaceBefore=0
    )
      # Normal text style with compact line spacing
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,   # Smaller font size
        leading=13,   # Tighter line spacing
        spaceBefore=3,  # Reduce space before
        spaceAfter=3    # Reduce space after
    )
    
    # Heading style for section headers
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=11,
        fontName='Helvetica-Bold'
    )
    
    # Current date string
    current_date = datetime.now().strftime("%d de %B de %Y")
    # Convert English month names to Spanish if needed
    month_map = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo',
        'April': 'abril', 'May': 'mayo', 'June': 'junio',
        'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
        'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    for eng_month, es_month in month_map.items():
        current_date = current_date.replace(eng_month, es_month)
      # Calcular el martes de la semana evaluada
    # ISO: lunes=1, martes=2, ...
    tuesday_of_week = datetime.strptime(f'{year}-W{int(week)}-2', "%Y-W%W-%w")
    tuesday_str = tuesday_of_week.strftime("%d de %B de %Y")
    # Convertir el mes a español
    for eng_month, es_month in month_map.items():
        tuesday_str = tuesday_str.replace(eng_month, es_month)
    
    # Start building the document
    story = []    # Add the LA CONSTANCIA logo - smaller and left-aligned like in the example
    try:
        logo_path = "LogoConst.png"
        logo_img = Image(logo_path, width=2*inch, height=0.8*inch)
        logo_table = Table([[logo_img]], colWidths=[6*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Left-aligned like the example
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        story.append(logo_table)
    except Exception as e:
        print(f"Warning: Could not load logo image: {e}")
        # Fallback to text if image fails
        company_name = "LA CONSTANCIA"
        subtitle = "ABInBev"
        header_data = [[company_name], [subtitle]]
        header_table = Table(header_data, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left-aligned to match logo
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, 1), 12),
        ]))
        story.append(header_table)
    story.append(Spacer(1, 0.05*inch))  # Minimal spacing after logo

    # Add the date on the right side - positioned at the top right like in the example
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        alignment=2,  # Right-aligned
        fontSize=10
    )
    date_paragraph = Paragraph(tuesday_str, date_style)    
    story.append(date_paragraph)
    story.append(Spacer(1, 0.1*inch))  # Minimal spacing after date
    
    # Add title - centered and bold with reduced spacing
    most_reported_issue = offenders_data.iloc[0]['most_reported_issue']
    story.append(Paragraph("REPORTE DE CLIENTES TOP OFFENDER", title_style))
    story.append(Spacer(1, 0.03*inch))  # Minimal spacing
    story.append(Paragraph(f"Semana {week} del {year} - Problema: {most_reported_issue}", subtitle_style))
    story.append(Spacer(1, 0.15*inch))  # Reduce spacing
    
    # Introduction paragraph - automatically adapted to the specific issue
    intro_text = generate_intro_text(most_reported_issue, week)
    
    # Create justified paragraph
    justified_style = ParagraphStyle(
        'Justified',
        parent=normal_style,
        alignment=4,  # 4 = justified
        spaceBefore=6,
        spaceAfter=6
    )
    story.append(Paragraph(intro_text, justified_style))
    story.append(Spacer(1, 0.2*inch))  # Add space before the table
    
    # Add action plans table - prevent ALL duplicated entries with forced text wrapping
    action_plan_data = [
        ['Cliente', 'Rutas', 'Plan de Acción', 'Fecha']
    ]    # Function to create wrapped text as Paragraph
    def wrap_text_paragraph(text, max_width=1.8*inch, style_name='Normal'):
        """Create a Paragraph object with proper wrapping"""
        if not text:
            return Paragraph("", styles[style_name])
        
        # Clean the text
        clean_text = str(text).strip()
        
        # Create paragraph with automatic wrapping
        return Paragraph(clean_text, styles[style_name])

    def wrap_routes_paragraph(routes_text, max_width=0.8*inch):
        """Create a Paragraph for routes with line breaks"""
        if not routes_text:
            return Paragraph("", styles['Normal'])
        
        # Split by commas and create HTML line breaks
        routes = [route.strip() for route in str(routes_text).split(',')]
        formatted_routes = '<br/>'.join(routes)
        
        return Paragraph(formatted_routes, styles['Normal'])
      # Use a set to track unique clients and limit to top 5
    seen_clients = set()
    clients_added = 0
    max_clients = 3  # Limitar a solo 3 clientes para asegurar que quepa en una sola página
    
    for _, client in offenders_data.iterrows():
        if clients_added >= max_clients:
            break
        client_key = f"{client['codigo_cliente']}-{client['nombre_cliente']}".strip().lower()
        if client_key not in seen_clients:
            seen_clients.add(client_key)
              # El nombre ya está limpio del groupby, solo combinar con código
            client_display = f"{client['codigo_cliente']} {client['nombre_cliente']}"
            
            # Create wrapped paragraphs for table cells
            client_paragraph = wrap_text_paragraph(client_display, max_width=2.0*inch)
            action_plan_paragraph = wrap_text_paragraph(client['action_plan'], max_width=2.5*inch)
            
            # Wrap the routes text with line breaks
            routes_text = ", ".join(client['routes'])
            routes_paragraph = wrap_routes_paragraph(routes_text, max_width=0.8*inch)
            
            # Use current date for consistency with header
            current_report_date = datetime.now().strftime("%d/%m/%Y")
            
            action_plan_data.append([
                client_paragraph,
                routes_paragraph,
                action_plan_paragraph,
                tuesday_of_week.strftime("%d/%m/%Y")
            ])
            
            clients_added += 1
              # Create simple table without complex formatting
    if len(action_plan_data) > 1:  # Only if we have data rows
        # Simple table con anchos de columna optimizados
        action_table = Table(action_plan_data, colWidths=[2.0*inch, 0.8*inch, 2.5*inch, 0.8*inch])
        action_table.setStyle(TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Data cells
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Cliente
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Rutas
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),      # Plan de Acción
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),    # Fecha
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # Grid y padding
            ('GRID', (0, 0), (-1, -1), 0.75, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
    else:
        # Simple placeholder when no data
        action_table = Table([['No se encontraron clientes']], colWidths=[5.7*inch])
        action_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, 0), 10),        ]))
    
    story.append(action_table)
    story.append(Spacer(1, 0.2*inch))  # Minimal spacing before signatures
    
    # Add signature section    
    signature_style = ParagraphStyle(        'SignatureHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,    # Smaller font
        leading=10,    # Tighter spacing
        spaceBefore=6,  # Reduce space before        
        spaceAfter=8   # Reduce space after
    )
    
    story.append(Paragraph("Firma de enterados:", signature_style))
    story.append(Spacer(1, 0.15*inch))  # Reduce space for signatures
    
    # Get appropriate signatures based on the week/year
    current_signatures = get_signatures_for_date(week, year)
    
    # Create signatures table - matching the example layout exactly with more space
    sig_data = []
    # Create rows with 2 signatures per row, with more space for actual signatures
    for i in range(0, len(current_signatures), 2):
        row = []
        for j in range(2):
            idx = i + j
            if idx < len(current_signatures):
                sig = current_signatures[idx]
                # Más espacio entre línea de firma y nombre para firmar adecuadamente
                sig_cell = f"F.________________________________\n{sig['name']} - {sig['title']}"
            else:
                sig_cell = ""
            row.append(sig_cell)
        sig_data.append(row)
    
    # Create signature table with increased spacing for proper signing
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch], rowHeights=[1.0*inch]*len(sig_data))  # Altura aumentada para más espacio
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align to top for better spacing
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Tamaño de letra
        ('LEADING', (0, 0), (-1, -1), 12),  # Más espacio entre líneas
        ('TOPPADDING', (0, 0), (-1, -1), 8),  # Más padding arriba
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)  # Más padding abajo para separar filas
    ]))
    
    story.append(sig_table)
    # Add footer with DPO logo - reduced spacing to fit on one page
    story.append(Spacer(1, 0.2*inch))  # Reducir más el espacio
    
    try:
        dpo_logo_path = "dpo.png"
        # Make DPO logo bigger and more visible like in the example
        dpo_img = Image(dpo_logo_path, width=1.2*inch, height=0.8*inch)
        dpo_table = Table([[dpo_img]], colWidths=[6*inch])
        dpo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))
        story.append(dpo_table)
    except Exception as e:
        print(f"Warning: Could not load DPO logo: {e}")
        # Fallback to text if image fails - make it more visible
        footer_table = Table([["DPO 2.0"]], colWidths=[6*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),  # Bigger font size
        ]))
        story.append(footer_table)
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    
    # Save to file
    with open(output_file, 'wb') as f:
        f.write(buffer.read())
    
    print(f"Report generated successfully: {output_file}")
    return output_file

def main(specific_week=None, specific_year=None, output_dir=None):
    """Main function to generate the weekly offender report
    
    Args:
        specific_week: Optional specific week number to generate report for
        specific_year: Optional specific year to generate report for
        output_dir: Optional directory to save the report
    """
    # Get current week number and year if not specified
    today = datetime.now()
    current_week = specific_week if specific_week else today.isocalendar()[1]
    current_year = specific_year if specific_year else today.year
    
    print(f"Generating report for week {current_week}, year {current_year}")
      # Load the data
    data, routes_df = load_data()
    if data is None:
        print("Error: Could not load data. Verify that 'Feedbacks H1.xlsx' exists.")
        return None
    
    # Get the weekly offenders
    offenders = get_weekly_offenders(data, week=current_week, year=current_year)
    week_used = current_week
    year_used = current_year
    
    # If no offenders found, try the previous week
    if offenders.empty and not specific_week:
        print(f"No data found for week {current_week}. Trying previous week...")
        prev_week = current_week - 1
        prev_year = current_year
        if prev_week < 1:
            prev_week = 52  # Last week of previous year
            prev_year -= 1
        
        offenders = get_weekly_offenders(data, week=prev_week, year=prev_year)
        
        if not offenders.empty:
            week_used = prev_week
            year_used = prev_year
            print(f"Using data from week {week_used}, year {year_used}")
    
    # Generate the report
    if not offenders.empty:
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"weekly_offender_report_w{week_used}_{year_used}.pdf")
        else:
            output_path = f"weekly_offender_report_w{week_used}_{year_used}.pdf"
            
        report_path = generate_weekly_report(offenders, week_used, year_used, output_path)
        
        if report_path:
            print(f"Report generated successfully at: {report_path}")
            return report_path
        else:
            print("Error: Failed to generate report")
            return None
    else:
        msg = f"No offenders found for week {current_week}, year {current_year}"
        if not specific_week:
            msg += " or the previous week"
        print(msg)
        return None

def generate_all_weekly_reports(year=None, output_dir=None):
    """Generate reports for all weeks with data in the specified year
    
    Args:
        year: Year to generate reports for (default: current year)
        output_dir: Directory to save all reports
    """
    if year is None:
        year = datetime.now().year
    
    print(f"Generating reports for all weeks with data in {year}...")
    
    # Load the data
    data = load_data()
    if data is None:
        print("Error: Could not load data. Verify that 'Feedbacks H1.xlsx' exists.")
        return []
    
    # Find all weeks with data
    weekly_data = data[data['year'] == year]
    weeks_with_data = sorted(weekly_data['week'].unique())
    
    print(f"Found data for {len(weeks_with_data)} weeks: {weeks_with_data}")
    
    generated_reports = []
    
    for week in weeks_with_data:
        print(f"\n--- Generating report for week {week} ---")
        
        # Get offenders for this week
        offenders = get_weekly_offenders(data, week=week, year=year)
        
        if not offenders.empty:
            # Create output path
            if output_dir:
                import os
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"weekly_offender_report_w{week}_{year}.pdf")
            else:
                output_path = f"weekly_offender_report_w{week}_{year}.pdf"
            
            # Generate the report
            report_path = generate_weekly_report(offenders, week, year, output_path)
            
            if report_path:
                generated_reports.append(report_path)
                print(f"✅ Report generated: {report_path}")
            else:
                print(f"❌ Failed to generate report for week {week}")
        else:
            print(f"⚠️  No valid offenders found for week {week}")
    
    print(f"\n🎉 Generation completed! Created {len(generated_reports)} reports.")
    return generated_reports

def generate_weekly_report_for_any_week(week_num, year_num=None):
    """Generate report for any specified week and year"""
    if year_num is None:
        year_num = datetime.now().year
    
    print(f"Generating report for week {week_num}, year {year_num}")
    
    # Load data
    feedbacks_df, routes_df = load_data()
    
    # Get weekly offenders for the specified week/year
    offenders_data = get_weekly_offenders(feedbacks_df, week_num, year_num)
    
    if offenders_data.empty:
        print(f"No data available for week {week_num}, year {year_num}")
        return None
    
    # Generate the PDF report
    output_file = f"weekly_offender_report_w{week_num}_{year_num}.pdf"
    return generate_weekly_report(offenders_data, week_num, year_num, output_file)

def generate_all_weekly_reports(year=None):
    """Generate reports for all weeks with data from the beginning of the year until current week"""
    if year is None:
        year = datetime.now().year
    
    print(f"Generando reportes para todas las semanas con datos en el año {year}")
    
    # Load data to find the range of weeks with data
    data, routes_df = load_data()
    if data is None:
        print("Error: No se pudo cargar los datos")
        return 0, 1
    
    # Filter data for the specified year
    data_year = data[data['year'] == year].copy()
    if data_year.empty:
        print(f"No hay datos disponibles para el año {year}")
        return 0, 1
    
    # Get all unique weeks with data in the year
    weeks_with_data = sorted(data_year['week'].unique())
    
    # Get current week to avoid generating future reports
    current_week = datetime.now().isocalendar().week
    current_year = datetime.now().year
    
    # If we're looking at current year, limit to current week
    if year == current_year:
        weeks_with_data = [w for w in weeks_with_data if w <= current_week]
    
    print(f"Semanas con datos encontradas: {weeks_with_data}")
    print(f"Total de semanas a procesar: {len(weeks_with_data)}")
    
    generated_reports = []
    error_count = 0
    
    for i, week in enumerate(weeks_with_data, 1):
        print(f"\n--- Procesando Semana {week} ({i}/{len(weeks_with_data)}) ---")
        try:
            result = generate_weekly_report_for_any_week(week, year)
            if result:
                filename = f"weekly_offender_report_w{week}_{year}.pdf"
                generated_reports.append(filename)
                print(f"✅ Reporte generado: {filename}")
            else:
                print(f"⚠️ No se pudieron generar datos para la semana {week}")
                error_count += 1
        except Exception as e:
            print(f"❌ Error generando reporte para la semana {week}: {str(e)}")
            error_count += 1
    
    print(f"\n📋 Resumen final:")
    print(f"✅ Reportes generados exitosamente: {len(generated_reports)}")
    print(f"❌ Errores encontrados: {error_count}")
    
    if generated_reports:
        print(f"\n📁 Archivos generados:")
        for report in generated_reports:
            print(f"  - {report}")
    
    return len(generated_reports), error_count

def classify_issue_type(issue_text):
    """Classify the issue type for proper action plan assignment"""
    if not issue_text:
        return 'generic'
    
    issue_lower = str(issue_text).lower()
    
    # Clasificación específica por palabras clave
    if any(word in issue_lower for word in ['faltante', 'producto', 'inventario', 'stock']):
        return 'faltante_producto'
    elif any(word in issue_lower for word in ['envase', 'canasta', 'sucio', 'roto', 'dañado']):
        return 'envase_canasta'
    elif any(word in issue_lower for word in ['pedido', 'orden', 'cantidad', 'solicitud']):
        return 'pedido_orden'
    elif any(word in issue_lower for word in ['entrega', 'delivery', 'tarde', 'hora', 'puntual']):
        return 'entrega_delivery'
    elif any(word in issue_lower for word in ['factura', 'documento', 'precio', 'dato']):
        return 'factura_documento'
    elif any(word in issue_lower for word in ['calidad', 'caducidad', 'fecha', 'vencimiento', 'sabor', 'olor']):
        return 'calidad_caducidad'
    elif any(word in issue_lower for word in ['servicio', 'atención', 'cordial', 'trato']):
        return 'servicio_atencion'
    elif any(word in issue_lower for word in ['ruta', 'vendedor', 'personal', 'ventas']):
        return 'ruta_vendedor'
    elif any(word in issue_lower for word in ['demora', 'demorado', 'recibir', 'pagar', 'espera']):
        return 'cliente_demora'
    elif any(word in issue_lower for word in ['safety', 'seguridad', 'crítico', 'peligro', 'riesgo']):
        return 'safety_critico'
    else:
        return 'generic'

def get_action_plan_for_issue(issue_type):
    """Get the appropriate action plan for the classified issue type"""
    action_plans = {
        'faltante_producto': 'Checklist de verificación y control de inventario',
        'envase_canasta': 'Inspección y limpieza de envases a ',
        'pedido_orden': 'Verificación dual de cantidades',
        'entrega_delivery': 'Optimización de rutas y comunicación',
        'factura_documento': 'Capacitación en facturación',
        'calidad_caducidad': 'Control de calidad y fechas',
        'servicio_atencion': 'Capacitación en servicio al cliente',
        'ruta_vendedor': 'Optimización de procedimientos',
        'cliente_demora': 'Coordinación previa con clientes y BDR',
        'safety_critico': 'Evaluación en RCOG con ventas de clientes criticos'
    }
    
    issue_key = classify_issue_type(issue_type)
    return action_plans.get(issue_key, "Análisis personalizado y plan de mejora específico")

def get_intro_text_for_issue(issue_type, week_num):
    """Get the appropriate intro text for the classified issue type"""
    intro_texts = {
        'faltante_producto': f"""El equipo de distribución del CD Soyapango informa sobre clientes con <b>faltante de productos</b> en la semana {week_num}. Se solicita implementar <b>checklist de verificación</b> para asegurar disponibilidad completa y optimizar la eficiencia de ruta. Detalles:""",
        
        'envase_canasta': f"""El equipo de distribución del CD Soyapango informa sobre problemas con <b>envases y canastas</b> en la semana {week_num}. Se solicita implementar <b>protocolo de inspección</b> para garantizar entrega en perfecto estado. Detalles:""",
        
        'pedido_orden': f"""El equipo de distribución del CD Soyapango informa sobre problemas en <b>toma de pedidos</b> en la semana {week_num}. Se solicita implementar <b>verificación dual</b> para asegurar precisión y evitar discrepancias. Detalles:""",
        
        'entrega_delivery': f"""El equipo de distribución del CD Soyapango informa sobre problemas de <b>puntualidad en entregas</b> en la semana {week_num}. Se solicita <b>optimización logística</b> para mejorar eficiencia y cumplir cronogramas. Detalles:""",
        
        'factura_documento': f"""El equipo de distribución del CD Soyapango informa sobre problemas de <b>documentación</b> en la semana {week_num}. Se solicita <b>mejora en procesos administrativos</b> para eliminar errores y reprocesos. Detalles:""",
        
        'calidad_caducidad': f"""El equipo de distribución del CD Soyapango informa sobre problemas de <b>calidad de productos</b> en la semana {week_num}. Se solicita implementar <b>controles de calidad</b> para asegurar productos óptimos. Detalles:""",
        
        'servicio_atencion': f"""El equipo de distribución del CD Soyapango informa sobre problemas de <b>servicio al cliente</b> en la semana {week_num}. Se solicita <b>capacitación en excelencia</b> para mejorar experiencia y satisfacción. Detalles:""",
        
        'ruta_vendedor': f"""El equipo de distribución del CD Soyapango informa sobre problemas en <b>procedimientos de ruta</b> en la semana {week_num}. Se solicita <b>optimización de procesos</b> para mejorar eficiencia operativa. Detalles:""",
        
        'cliente_demora': f"""El equipo de distribución del CD Soyapango informa sobre <b>demoras en recepción</b> en la semana {week_num}. Se solicita <b>mejora en comunicación</b> para minimizar tiempos de espera. Detalles:""",
        
        'safety_critico': f"""El equipo de distribución del CD Soyapango informa sobre <b>condiciones de seguridad</b> en la semana {week_num}. Se solicita implementar <b>protocolos de seguridad</b> para garantizar operación segura. Detalles:"""    }
    
    issue_key = classify_issue_type(issue_type)
    return intro_texts.get(issue_key, f"""El equipo de distribución del CD Soyapango informa sobre problemas diversos en la semana {week_num}. Se solicita <b>implementar mejoras específicas</b> para optimizar procesos y completar jornadas eficientemente. Detalles:""")

def generate_monthly_reports(month=None, year=None):
    """Generate reports for all weeks in a specified month that have data"""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    print(f"Generando reportes para todas las semanas con datos en {calendar.month_name[month]} {year}")
    
    # Load data to find the range of weeks with data
    data, routes_df = load_data()
    if data is None:
        print("Error: No se pudo cargar los datos")
        return 0, 1
    
    # Filter data for the specified month and year
    data_filtered = data[(data['year'] == year) & (data['month'] == month)].copy()
    if data_filtered.empty:
        print(f"No hay datos disponibles para {calendar.month_name[month]} {year}")
        return 0, 1
    
    # Get all unique weeks with data in the month
    weeks_with_data = sorted(data_filtered['week'].unique())
    
    print(f"Semanas con datos en {calendar.month_name[month]}: {weeks_with_data}")
    print(f"Total de semanas a procesar: {len(weeks_with_data)}")
    
    generated_reports = []
    error_count = 0
    
    for i, week in enumerate(weeks_with_data, 1):
        print(f"\n--- Procesando Semana {week} ({i}/{len(weeks_with_data)}) ---")
        try:
            result = generate_weekly_report_for_any_week(week, year)
            if result:
                filename = f"weekly_offender_report_w{week}_{year}.pdf"
                generated_reports.append(filename)
                print(f"✅ Reporte generado: {filename}")
            else:
                print(f"⚠️ No se pudieron generar datos para la semana {week}")
                error_count += 1
        except Exception as e:
            print(f"❌ Error generando reporte para la semana {week}: {str(e)}")
            error_count += 1
    
    print(f"\n📋 Resumen del mes:")
    print(f"✅ Reportes generados exitosamente: {len(generated_reports)}")
    print(f"❌ Errores encontrados: {error_count}")
    
    if generated_reports:
        print(f"\n📁 Archivos generados:")
        for report in generated_reports:
            print(f"  - {report}")
    
    return len(generated_reports), error_count

# Nueva función para generar el texto introductorio específico
def generate_intro_text(issue_type, week_num):
    """Generate specific introduction text based on the issue type and historical analysis"""
    
    # Buscar el texto específico en nuestro diccionario de motivos
    if issue_type in MOTIVO_ACTION_PLANS:
        motivo_data = MOTIVO_ACTION_PLANS[issue_type]
        intro = motivo_data['intro']
        accion_especifica = motivo_data['accion_especifica'] 
        objetivo = motivo_data['objetivo']
        conclusion = motivo_data['conclusion']
    else:
        # Buscar coincidencias parciales para motivos similares
        issue_lower = issue_type.lower()
        motivo_data = None
        
        for motivo_key, data in MOTIVO_ACTION_PLANS.items():
            motivo_key_lower = motivo_key.lower()
            
            if ('demorado' in issue_lower or 'demora' in issue_lower) and 'demorado' in motivo_key_lower:
                motivo_data = data
                break
            elif ('safety' in issue_lower or 'critico' in issue_lower) and 'critico' in motivo_key_lower:
                motivo_data = data
                break
            elif ('envase' in issue_lower) and 'envase' in motivo_key_lower:
                motivo_data = data
                break
            elif ('rechazo' in issue_lower) and 'rechazo' in motivo_key_lower:
                motivo_data = data
                break
            elif ('problemático' in issue_lower or 'grosero' in issue_lower) and 'problemático' in motivo_key_lower:
                motivo_data = data
                break
            elif ('faltante' in issue_lower) and 'faltante' in motivo_key_lower:
                motivo_data = data
                break
            elif ('calidad' in issue_lower) and 'calidad' in motivo_key_lower:
                motivo_data = data
                break
        
        if motivo_data:
            intro = motivo_data['intro']
            accion_especifica = motivo_data['accion_especifica']
            objetivo = motivo_data['objetivo']
            conclusion = motivo_data['conclusion']
        else:
            # Texto genérico si no encuentra coincidencia
            intro = "diversos problemas operativos"
            accion_especifica = "análisis personalizado y plan de mejora"
            objetivo = "resolver las problemáticas identificadas"
            conclusion = "mejorando procesos"
        
    # Generar el texto completo simplificado
    return f"""El equipo de distribución del CD Soyapango informa sobre clientes con {intro} en la semana {week_num}. Se solicita apoyo en <b>{accion_especifica}</b> para {objetivo}, {conclusion}. Detalles en la tabla:"""

if __name__ == "__main__":
    import sys
    import argparse
      # Setup argument parser
    parser = argparse.ArgumentParser(description='Generate weekly offender reports')
    parser.add_argument('--all', action='store_true', 
                        help='Generate reports for all weeks with data in the year')
    parser.add_argument('--week', type=int, 
                        help='Generate report for specific week number')
    parser.add_argument('--year', type=int, 
                        help='Year for the report (default: current year)')
    parser.add_argument('--month', type=int, 
                        help='Generate reports for all weeks of specified month')
    parser.add_argument('--output-dir', type=str, 
                        help='Output directory for generated reports')
    
    args = parser.parse_args()
    
    try:
        if args.all:
            print("🔄 Generando reportes para todas las semanas del año con datos...")
            current_year = args.year or datetime.now().year
            
            print(f"📅 Procesando todas las semanas del año {current_year}")
            success_count, error_count = generate_all_weekly_reports(year=current_year)
            
            print(f"\n✅ Proceso completado:")
            print(f"   - Reportes generados exitosamente: {success_count}")
            print(f"   - Errores encontrados: {error_count}")
            
            if success_count > 0:
                print(f"\n📁 Reportes guardados en el directorio actual")
            
        elif args.month:
            print(f"🔄 Generando reportes para todas las semanas del mes {args.month}...")
            year = args.year or datetime.now().year
            
            success_count, error_count = generate_monthly_reports(
                month=args.month, 
                year=year
            )
            
            print(f"\n✅ Proceso completado:")
            print(f"   - Reportes generados exitosamente: {success_count}")
            print(f"   - Errores encontrados: {error_count}")
            
        elif args.week:
            print(f"🔄 Generando reporte para la semana {args.week}...")
            year = args.year or datetime.now().year
            
            success = generate_weekly_report_for_any_week(args.week, year)
            if success:
                print(f"✅ Reporte generado exitosamente para la semana {args.week} del {year}")
            else:
                print(f"❌ Error al generar el reporte para la semana {args.week}")
            
        else:
            # Default behavior: generate report for current week
            print("🔄 Generando reporte para la semana actual...")
            main(output_dir=args.output_dir)
            print("✅ Reporte generado exitosamente")
            
    except Exception as e:
        print(f"❌ Error al generar el reporte: {str(e)}")
        sys.exit(1)
