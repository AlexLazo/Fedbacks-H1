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

# Define the required signatures for the report - exactly matching the example names
SIGNATURES = [
    {"name": "Roney Rivas", "title": "TL de Ventas"},
    {"name": "Félix Chávez", "title": "Gerente CD Soyapango"},
    {"name": "Óscar Portillo", "title": "Jefe de Distribución"},
    {"name": "Brian Lazo", "title": "Supervisor de Distribución"}
]

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
            
            return merged_df
            
        except Exception as e:
            print(f"Warning: Could not load routes database. Using only feedbacks data: {e}")
            return feedbacks_df
            
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

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
        client_data = issue_data[issue_data['codigo_numerico'] == client_code]
          # Generate a comprehensive action plan based on the specific issue and client data
        def generate_specific_action_plan(issue_type, client_feedback_data):
            """Generate specific action plan based on the issue type and actual client feedback"""
            
            # Get actual comments from client feedback for more context
            client_comments = client_feedback_data['comentarios'].dropna().tolist() if 'comentarios' in client_feedback_data.columns else []
            issue_lower = issue_type.lower()
            
            # Analyze specific patterns in the issue and comments
            if 'faltante' in issue_lower or 'producto' in issue_lower:
                if any('inventario' in str(comment).lower() for comment in client_comments):
                    return "Revisión de inventario en tiempo real y capacitación en control de stock"
                elif any('entrega' in str(comment).lower() for comment in client_comments):
                    return "Mejora en proceso de picking y verificación pre-despacho"
                else:
                    return "Implementar checklist de verificación de productos antes de salida"
                    
            elif 'envase' in issue_lower or 'canasta' in issue_lower:
                if any('sucio' in str(comment).lower() for comment in client_comments):
                    return "Protocolo de limpieza y desinfección de envases antes de entrega"
                elif any('roto' in str(comment).lower() or 'dañado' in str(comment).lower() for comment in client_comments):
                    return "Capacitación en manejo cuidadoso y revisión de envases antes de despacho"
                else:
                    return "Establecer proceso de inspección visual de envases y reposición inmediata"
                    
            elif 'pedido' in issue_lower or 'orden' in issue_lower:
                if any('cantidad' in str(comment).lower() for comment in client_comments):
                    return "Doble verificación de cantidades solicitadas vs. entregadas"
                elif any('producto' in str(comment).lower() for comment in client_comments):
                    return "Validación cruzada de códigos de producto antes de despacho"
                else:
                    return "Implementar sistema de confirmación de pedidos con el cliente"
                    
            elif 'entrega' in issue_lower or 'delivery' in issue_lower:
                if any('tarde' in str(comment).lower() or 'hora' in str(comment).lower() for comment in client_comments):
                    return "Reprogramación de ruta y comunicación proactiva de horarios"
                elif any('lugar' in str(comment).lower() or 'dirección' in str(comment).lower() for comment in client_comments):
                    return "Actualización de datos de ubicación y validación con cliente"
                else:
                    return "Coordinación previa con cliente para confirmar disponibilidad"
                    
            elif 'factura' in issue_lower or 'documento' in issue_lower:
                if any('precio' in str(comment).lower() for comment in client_comments):
                    return "Verificación de lista de precios actualizada y capacitación en facturación"
                elif any('dato' in str(comment).lower() for comment in client_comments):
                    return "Actualización de base de datos del cliente y validación de información"
                else:
                    return "Revisión completa del proceso de facturación y documentación"
            elif 'calidad' in issue_lower or 'caducidad' in issue_lower:
                if any('fecha' in str(comment).lower() for comment in client_comments):
                    return "Implementar rotación FIFO estricta y verificación de fechas de vencimiento"
                elif any('sabor' in str(comment).lower() or 'olor' in str(comment).lower() for comment in client_comments):
                    return "Protocolo de control de calidad sensorial antes de despacho"
                else:
                    return "Inspección completa de calidad del producto y condiciones de almacenamiento"
                    
            elif 'servicio' in issue_lower or 'atención' in issue_lower:
                return "Capacitación en servicio al cliente y protocolo de atención cordial"
                
            elif 'ruta' in issue_lower or 'vendedor' in issue_lower:
                return "Revisión de procedimientos de ruta y capacitación del personal de ventas"
                
            else:
                # For any other issue, provide a general but useful action plan                
                return "Seguimiento personalizado, análisis de causa raíz y plan de mejora específico"
        
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
    buffer = io.BytesIO()    # Create the PDF document with adjusted margins to fit everything on one page
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.5*inch,  # Reduce top margin
        bottomMargin=0.5*inch,  # Reduce bottom margin
        title="Reporte de Clientes Ofensores",
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
    
    # Main title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=1,  # Center
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=0.1*inch
    )
    
    # Subtitle style for week and problem
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=1,  # Center
        spaceAfter=0.2*inch
    )
    
    # Normal text style with better line spacing
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,  # Line spacing
        spaceBefore=6,
        spaceAfter=6
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
    story.append(Spacer(1, 0.1*inch))  # Reduce spacing

    # Add the date on the right side - positioned at the top right like in the example
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        alignment=2,  # Right-aligned
        fontSize=10
    )
    date_paragraph = Paragraph(tuesday_str, date_style)
    story.append(date_paragraph)
    story.append(Spacer(1, 0.2*inch))  # Reduce spacing    # Add title - centered and bold with reduced spacing
    most_reported_issue = offenders_data.iloc[0]['most_reported_issue']
    story.append(Paragraph("Reporte de clientes más reportados ", title_style))
    story.append(Spacer(1, 0.05*inch))  # Reduce spacing
    story.append(Paragraph(f"Semana {week} del {year} - Problema: {most_reported_issue}", subtitle_style))
    story.append(Spacer(1, 0.15*inch))  # Reduce spacing    # Introduction paragraph - automatically adapted to the specific issue
    def generate_intro_text(issue_type, week_num):
        """Generate specific introduction text based on the issue type"""
        issue_lower = issue_type.lower()
        
        if 'faltante' in issue_lower or 'producto' in issue_lower:
            specific_action = "capacitación en control de inventario y verificación de productos"
            objective = "asegurar la disponibilidad completa de productos solicitados"
            conclusion = "optimizando el control de inventario y previniendo faltantes"
            
        elif 'envase' in issue_lower or 'canasta' in issue_lower:
            specific_action = "capacitación en manejo adecuado y cuidado de envases"
            objective = "garantizar la entrega de envases en perfecto estado"
            conclusion = "previniendo quejas sobre condición de envases"
            
        elif 'pedido' in issue_lower or 'orden' in issue_lower:
            specific_action = "capacitación en verificación y confirmación de pedidos"
            objective = "asegurar la precisión en la toma y entrega de pedidos"
            conclusion = "reduciendo errores en los pedidos y devoluciones"
            
        elif 'entrega' in issue_lower or 'delivery' in issue_lower:
            specific_action = "capacitación en coordinación de horarios y rutas de entrega"
            objective = "optimizar los tiempos de entrega y la satisfacción del cliente"
            conclusion = "mejorando la puntualidad y efectividad en la distribución"
            
        elif 'factura' in issue_lower or 'documento' in issue_lower:
            specific_action = "capacitación en procesos de facturación y documentación"
            objective = "garantizar la exactitud en la documentación y facturación"
            conclusion = "evitando reprocesos administrativos y financieros"
            
        elif 'calidad' in issue_lower or 'caducidad' in issue_lower:
            specific_action = "capacitación en control de calidad y manejo de fechas de vencimiento"
            objective = "asegurar la entrega de productos con calidad óptima"
            conclusion = "eliminando reclamos por producto en mal estado"
            
        elif 'safety' in issue_lower or 'seguridad' in issue_lower or 'crítico' in issue_lower:
            specific_action = "evaluación de seguridad y protocolo de visita especializada"
            objective = "garantizar condiciones seguras para la operación comercial"
            conclusion = "protegiendo a nuestro personal y activos durante la visita"
            
        elif 'servicio' in issue_lower or 'atención' in issue_lower:
            specific_action = "capacitación en servicio al cliente y protocolo de atención"
            objective = "mejorar la experiencia y satisfacción del cliente"
            conclusion = "fidelizando a nuestros clientes a largo plazo"
            
        else:
            specific_action = "capacitación especializada según la naturaleza del problema"
            objective = "resolver la problemática específica identificada"
            conclusion = "mejorando nuestros procesos de atención al cliente"
        
        # Texto personalizado para cada tipo de motivo de feedback
        if 'faltante' in issue_lower or 'producto' in issue_lower:
            return f"""Por medio de la presente, el equipo de distribución del CD Soyapango, damos a conocer los clientes los cuales en la semana {week_num} nos presentaron problemas relacionados al tema de <b>{issue_type}</b>. Como equipo de distribución se solicita su valiosa ayuda en el tema de <b>{specific_action}</b>, esto para asegurar la disponibilidad completa de productos solicitados, optimizando el control de inventario y previniendo faltantes y para que la ruta cumpla eficientemente con su JL. Los detalles se presentan en la siguiente tabla:"""
        
        elif 'envase' in issue_lower or 'canasta' in issue_lower:
            return f"""Por medio de la presente, el equipo de distribución del CD Soyapango, damos a conocer los clientes los cuales en la semana {week_num} nos presentaron problemas relacionados al tema de <b>{issue_type}</b>. Como equipo de distribución se solicita su valiosa ayuda en el tema de <b>{specific_action}</b>, esto para garantizar la entrega de envases en perfecto estado, evitando quejas por esta causa y para que la ruta realice sus entregas sin contratiempos. Los detalles se presentan en la siguiente tabla:"""
        
        elif 'safety' in issue_lower or 'crítico' in issue_lower or 'crítico' in issue_lower:
            return f"""Por medio de la presente, el equipo de distribución del CD Soyapango, damos a conocer los clientes los cuales en la semana {week_num} nos presentaron problemas relacionados al tema de <b>{issue_type}</b>. Como equipo de distribución se solicita su valiosa ayuda en el tema de <b>evaluación de seguridad y protocolo de visita especializada</b>, esto para garantizar condiciones seguras para la operación comercial y garantizar que el cliente tenga de forma ordenada los procesos, para que la ruta no se exceda en el PDV ordenando y afectando la JL. Los detalles se presentan en la siguiente tabla:"""
        
        elif 'servicio' in issue_lower or 'atención' in issue_lower:
            return f"""Por medio de la presente, el equipo de distribución del CD Soyapango, damos a conocer los clientes los cuales en la semana {week_num} nos presentaron problemas relacionados al tema de <b>{issue_type}</b>. Como equipo de distribución se solicita su valiosa ayuda en el tema de <b>capacitación en servicio al cliente y protocolo de atención cordial</b>, esto para mejorar la experiencia del cliente y evitar reclamaciones futuras, asegurando que la ruta pueda completar sus tareas eficientemente. Los detalles se presentan en la siguiente tabla:"""
            
        # Texto genérico para otros casos
        else:
            return f"""Por medio de la presente, el equipo de distribución del CD Soyapango, damos a conocer los clientes los cuales en la semana {week_num} nos presentaron problemas relacionados al tema de <b>{issue_type}</b>. Como equipo de distribución se solicita su valiosa ayuda en el tema de <b>{specific_action}</b>, esto para {objective} y para que la ruta pueda completar su jornada laboral de manera eficiente. Los detalles se presentan en la siguiente tabla:"""
    
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
    ]
    
    # Function to force simple text wrapping
    def wrap_text(text, max_chars=35):
        """Simple text wrapping for table cells"""
        if len(text) <= max_chars:
            return text
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)        
            return "\n".join(lines)

    def wrap_routes(routes_text, max_chars=8):
        """Specialized wrapping for routes - force each route on separate line"""
        # Split by commas and put each route on its own line
        routes = [route.strip() for route in routes_text.split(',')]
        return "\n".join(routes)
    
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
              # Wrap the action plan text
            wrapped_action_plan = wrap_text(client['action_plan'], max_chars=35)
              # Wrap the routes text - simple approach: each route on new line
            routes_text = ", ".join(client['routes'])
            # Force each route on separate line by replacing commas with <br/>
            routes_html = routes_text.replace(", ", "<br/>")
            
            # Create Paragraph objects for cells that need wrapping  
            routes_paragraph = Paragraph(routes_html, centered_cell_style)
            action_plan_paragraph = Paragraph(wrapped_action_plan.replace('\n', '<br/>'), cell_style)
            
            # Use current date for consistency with header
            current_report_date = datetime.now().strftime("%d/%m/%Y")
            
            action_plan_data.append([
                client_display,
                routes_paragraph,
                action_plan_paragraph,
                tuesday_of_week.strftime("%d/%m/%Y")
            ])
            
            clients_added += 1# Create simple table without complex formatting
    if len(action_plan_data) > 1:  # Only if we have data rows        # Simple table con anchos de columna optimizados - aumentar ancho de rutas
        action_table = Table(action_plan_data, colWidths=[1.5*inch, 0.6*inch, 2.6*inch, 0.7*inch]) # Reducir rutas, aumentar plan
        action_table.setStyle(TableStyle([
            # Headers - simple and clean
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),  # Reducir tamaño de fuente
            
            # Data cells - formatting ultra compacto para ahorrar espacio
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),            ('FONTSIZE', (0, 1), (-1, -1), 7),  # Tamaño de fuente más legible 
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Cliente - left
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Rutas - center
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),      # Plan de Acción - left
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),    # Fecha - center
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),     # All content to top
              # Grid completo como en el ejemplo original
            ('GRID', (0, 0), (-1, -1), 0.75, colors.black),  # Líneas de rejilla completa
            
            # Mínimo padding posible
            ('LEFTPADDING', (0, 0), (-1, -1), 1),    # Padding mínimo
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),   # Padding mínimo
            ('TOPPADDING', (0, 0), (-1, -1), 1),     # Padding mínimo
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),  # Padding mínimo
        ]))
    else:
        # Simple placeholder when no data
        action_table = Table([['No se encontraron clientes']], colWidths=[5.7*inch])
        action_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
        ]))
    
    story.append(action_table)
    story.append(Spacer(1, 0.2*inch))  # Reduce spacing for signatures# Add signature section
    signature_style = ParagraphStyle(
        'SignatureHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        spaceBefore=12,        
        spaceAfter=14
    )
    story.append(Paragraph("Firma de enterados:", signature_style))
    story.append(Spacer(1, 0.15*inch))  # Reduce space for signatures
      # Create signatures table - matching the example layout exactly with more space
    sig_data = []
    
    # Create rows with 2 signatures per row, with more space for actual signatures
    for i in range(0, len(SIGNATURES), 2):
        row = []
        for j in range(2):
            idx = i + j
            if idx < len(SIGNATURES):
                sig = SIGNATURES[idx]                # Más espacio entre firmas pero menos entre línea de firma y nombre
                sig_cell = f"F.________________________________\n\n{sig['name']} - {sig['title']}"
            else:
                sig_cell = ""
            row.append(sig_cell)
        sig_data.append(row)
    
    # Create signature table with reduced spacing to fit on one page
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch], rowHeights=[0.5*inch]*len(sig_data))  # Altura aún más reducida
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align to top for better spacing
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Tamaño de letra más pequeño
        ('LEADING', (0, 0), (-1, -1), 8),  # Espacio entre líneas mínimo
        ('TOPPADDING', (0, 0), (-1, -1), 5),  # Reducir padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)  # Reducir padding
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
    data = load_data()
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

if __name__ == "__main__":
    import argparse
    
    # Create argument parser
    parser = argparse.ArgumentParser(description='Generate weekly offender reports')
    parser.add_argument('-w', '--week', type=int, help='Specific week number to generate report for')
    parser.add_argument('-y', '--year', type=int, help='Specific year to generate report for')
    parser.add_argument('-o', '--output', type=str, help='Directory to save the report')
    parser.add_argument('--all', action='store_true', help='Generate reports for all weeks with data')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.all:
        # Generate reports for all weeks
        generate_all_weekly_reports(year=args.year, output_dir=args.output)
    else:
        # Run the main function with the specified arguments
        main(specific_week=args.week, specific_year=args.year, output_dir=args.output)
