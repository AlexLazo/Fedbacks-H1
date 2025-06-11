import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
from streamlit_option_menu import option_menu
import calendar
import io
from io import BytesIO
import base64
import plotly.io as pio
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Seguimiento Feedbacks - DS00",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para un diseño profesional
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 0 1rem;
    }
    .kpi-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .analysis-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .top-performance {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos con cache
@st.cache_data
def load_data():
    """Carga los datos de los archivos Excel"""
    try:
        # Cargar Feedbacks
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        
        # Cargar BD_Rutas
        rutas_df = pd.read_excel('BD_Rutas.xlsx')
        
        # Limpiar y preparar datos
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        feedbacks_df['fecha_cierre'] = pd.to_datetime(feedbacks_df['fecha_cierre'])
        
        # Crear columnas adicionales para análisis
        feedbacks_df['mes'] = feedbacks_df['fecha_registro'].dt.month
        feedbacks_df['mes_nombre'] = feedbacks_df['fecha_registro'].dt.month_name()
        feedbacks_df['semana'] = feedbacks_df['fecha_registro'].dt.isocalendar().week
        feedbacks_df['dia_semana'] = feedbacks_df['fecha_registro'].dt.day_name()
        feedbacks_df['trimestre'] = feedbacks_df['fecha_registro'].dt.quarter
        feedbacks_df['año'] = feedbacks_df['fecha_registro'].dt.year
        feedbacks_df['hora'] = feedbacks_df['fecha_registro'].dt.hour
        
        # Mapear trimestres a nombres
        trimestre_map = {1: 'Q1 (Ene-Mar)', 2: 'Q2 (Abr-Jun)', 3: 'Q3 (Jul-Sep)', 4: 'Q4 (Oct-Dic)'}
        feedbacks_df['trimestre_nombre'] = feedbacks_df['trimestre'].map(trimestre_map)
        
        # Join con BD_Rutas
        merged_df = feedbacks_df.merge(
            rutas_df, 
            left_on='ruta', 
            right_on='RUTA', 
            how='left'
        )
        
        return feedbacks_df, rutas_df, merged_df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None, None, None

# Función para limpiar DataFrames antes de mostrar (soluciona errores de Arrow)
def clean_dataframe_for_display(df):
    """Limpia un DataFrame para prevenir errores de Arrow en Streamlit"""
    df_clean = df.copy()
    
    # Convertir todas las columnas a tipos seguros para Streamlit
    for col in df_clean.columns:
        try:
            if col == 'check_supervisor':
                # Manejo especial para la columna check_supervisor
                # Convertir todos los valores a numéricos primero, luego a int, luego a string
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int).astype(str)
            elif col in ['codigo_cliente', 'id_tema']:
                # Manejar códigos como strings para evitar formateo científico
                df_clean[col] = df_clean[col].astype(str)
            elif df_clean[col].dtype == 'object':
                # Convertir valores NaN a string antes de convertir toda la columna
                df_clean[col] = df_clean[col].fillna('').astype(str)
            elif pd.api.types.is_numeric_dtype(df_clean[col]):
                # Redondear números flotantes para mejor visualización
                if df_clean[col].dtype in ['float64', 'float32']:
                    df_clean[col] = df_clean[col].round(2)
                    # Convertir NaN a 0 para evitar problemas
                    df_clean[col] = df_clean[col].fillna(0)
            elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                # Convertir fechas a string
                df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                df_clean[col] = df_clean[col].fillna('')
        except Exception as e:
            # En caso de error, convertir toda la columna a string
            print(f"Warning: Error processing column {col}: {e}")
            df_clean[col] = df_clean[col].fillna('').astype(str)
    
    # Reemplazar cualquier valor NaN restante con strings vacíos
    df_clean = df_clean.fillna('')
    
    # Verificación final: asegurar que todas las columnas problemáticas sean strings
    problematic_columns = ['check_supervisor', 'codigo_cliente', 'id_tema']
    for col in problematic_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str)
    
    # Asegurar que todas las columnas de objeto sean strings
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str)
    
    return df_clean

# Función para crear métricas KPI mejoradas
def create_advanced_kpi_metrics(df, merged_df):
    """Crea métricas KPI avanzadas"""
    st.markdown("### 📊 KPIs Principales del Sistema")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        total_registros = len(df)
        st.markdown(
            f"""
            <div class="kpi-container">
                <h3 style="color: white; margin: 0;">📊 Total Registros</h3>
                <h2 style="color: white; margin: 0;">{total_registros:,}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        total_rutas = df['ruta'].nunique()
        st.markdown(
            f"""
            <div class="kpi-container">
                <h3 style="color: white; margin: 0;">🚚 Rutas Únicas</h3>
                <h2 style="color: white; margin: 0;">{total_rutas}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        total_usuarios = df['usuario'].nunique()
        st.markdown(
            f"""
            <div class="kpi-container">
                <h3 style="color: white; margin: 0;">👥 Usuarios</h3>
                <h2 style="color: white; margin: 0;">{total_usuarios}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        promedio_puntos = df['puntos'].mean()
        st.markdown(
            f"""
            <div class="kpi-container">
                <h3 style="color: white; margin: 0;">⭐ Puntos Promedio</h3>
                <h2 style="color: white; margin: 0;">{promedio_puntos:.1f}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col5:
        total_clientes = df['codigo_cliente'].nunique()
        st.markdown(
            f"""
            <div class="kpi-container">
                <h3 style="color: white; margin: 0;">🏢 Clientes</h3>
                <h2 style="color: white; margin: 0;">{total_clientes}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col6:
        tasa_cierre = (df['fecha_cierre'].notna().sum() / len(df)) * 100
        st.markdown(
            f"""
            <div class="kpi-container">
                <h3 style="color: white; margin: 0;">✅ Tasa Cierre</h3>
                <h2 style="color: white; margin: 0;">{tasa_cierre:.1f}%</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Función para generar reportes
def generate_report(df, merged_df, report_type="completo"):
    """Genera reportes en diferentes formatos"""
    
    if report_type == "completo":
        report_content = f"""
# REPORTE COMPLETO DE ANÁLISIS - FEEDBACKS H1
Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## RESUMEN EJECUTIVO
- Total de Registros: {len(df):,}
- Rutas Únicas: {df['ruta'].nunique()}
- Usuarios Activos: {df['usuario'].nunique()}
- Clientes Únicos: {df['codigo_cliente'].nunique()}
- Promedio de Puntos: {df['puntos'].mean():.2f}
- Tasa de Cierre: {(df['fecha_cierre'].notna().sum() / len(df)) * 100:.1f}%

## TOP PERFORMERS
### Top 10 Rutas por Volumen:
{df['ruta'].value_counts().head(10).to_string()}

### Top 10 Usuarios Más Activos:
{df['usuario'].value_counts().head(10).to_string()}

### Top 10 Respuestas de Retroalimentación:
{df['respuesta_sub'].value_counts().head(10).to_string()}

## ANÁLISIS TEMPORAL
### Registros por Mes:
{df.groupby('mes_nombre').size().to_string()}

### Registros por Trimestre:
{df.groupby('trimestre_nombre').size().to_string()}

## ANÁLISIS DE CALIDAD
### Distribución de Puntos:
{df['puntos'].value_counts().sort_index().to_string()}

### Análisis de Supervisores (si disponible):
"""
        
        if 'SUPERVISOR' in merged_df.columns:
            supervisor_analysis = merged_df.groupby('SUPERVISOR').agg({
                'id_tema': 'count',
                'puntos': 'mean'
            }).round(2)
            report_content += f"\n{supervisor_analysis.to_string()}\n"
        
        return report_content
    
    elif report_type == "ejecutivo":
        return f"""
# REPORTE EJECUTIVO - FEEDBACKS H1
Fecha: {datetime.now().strftime('%d/%m/%Y')}

## MÉTRICAS CLAVE
- Total Registros: {len(df):,}
- Tasa de Cierre: {(df['fecha_cierre'].notna().sum() / len(df)) * 100:.1f}%
- Puntos Promedio: {df['puntos'].mean():.2f}
- Período: {df['fecha_registro'].min().strftime('%d/%m/%Y')} - {df['fecha_registro'].max().strftime('%d/%m/%Y')}

## PRINCIPALES HALLAZGOS
- Ruta más activa: {df['ruta'].value_counts().index[0]} ({df['ruta'].value_counts().iloc[0]} registros)
- Usuario más activo: {df['usuario'].value_counts().index[0]} ({df['usuario'].value_counts().iloc[0]} registros)
- Respuesta principal: {df['respuesta_sub'].value_counts().index[0]} ({df['respuesta_sub'].value_counts().iloc[0]} casos)
"""

def generate_pdf_report(df, merged_df, report_type="completo"):
    """Genera un reporte PDF profesional con gráficas"""
    try:
        # Crear buffer para PDF
        pdf_buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.blue,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Lista de elementos para el PDF
        story = []
        
        # Título principal
        story.append(Paragraph("📊 REPORTE FEEDBACKS H1 - ANÁLISIS COMPLETO", title_style))
        story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resumen ejecutivo
        story.append(Paragraph("📋 RESUMEN EJECUTIVO", heading_style))
        
        # Crear tabla de métricas principales
        metrics_data = [
            ['Métrica', 'Valor'],
            ['Total de Registros', f"{len(df):,}"],
            ['Rutas Únicas', f"{df['ruta'].nunique()}"],
            ['Usuarios Activos', f"{df['usuario'].nunique()}"],
            ['Clientes Únicos', f"{df['codigo_cliente'].nunique()}"],
            ['Promedio de Puntos', f"{df['puntos'].mean():.2f}"],
            ['Tasa de Cierre', f"{(df['fecha_cierre'].notna().sum() / len(df)) * 100:.1f}%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Generar gráficas como imágenes
        try:
            # Gráfica 1: Top 10 Rutas
            story.append(Paragraph("🚚 TOP 10 RUTAS MÁS ACTIVAS", heading_style))
            
            top_rutas = df['ruta'].value_counts().head(10)
            fig_rutas = px.bar(
                x=top_rutas.values, 
                y=top_rutas.index, 
                orientation='h',
                title="Top 10 Rutas por Número de Registros",
                labels={'x': 'Número de Registros', 'y': 'Ruta'}
            )
            fig_rutas.update_layout(height=500, width=700, showlegend=False)
            
            # Convertir gráfica a imagen
            img_buffer = BytesIO()
            fig_rutas.write_image(img_buffer, format='png', engine='kaleido')
            img_buffer.seek(0)
            
            # Agregar imagen al PDF
            img = Image(img_buffer, width=5*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            story.append(Paragraph(f"⚠️ Error generando gráfica de rutas: {str(e)}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        try:
            # Gráfica 2: Distribución de Puntos
            story.append(Paragraph("⭐ DISTRIBUCIÓN DE PUNTUACIONES", heading_style))
            
            fig_puntos = px.histogram(
                df, x='puntos', 
                title="Distribución de Puntuaciones",
                labels={'puntos': 'Puntuación', 'count': 'Frecuencia'}
            )
            fig_puntos.update_layout(height=400, width=700, showlegend=False)
            
            img_buffer2 = BytesIO()
            fig_puntos.write_image(img_buffer2, format='png', engine='kaleido')
            img_buffer2.seek(0)
            
            img2 = Image(img_buffer2, width=5*inch, height=2.5*inch)
            story.append(img2)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            story.append(Paragraph(f"⚠️ Error generando gráfica de puntos: {str(e)}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Top Usuarios
        story.append(Paragraph("👥 TOP 10 USUARIOS MÁS ACTIVOS", heading_style))
        
        top_usuarios_data = [['Usuario', 'Registros']]
        for usuario, count in df['usuario'].value_counts().head(10).items():
            top_usuarios_data.append([str(usuario), str(count)])
        
        usuarios_table = Table(top_usuarios_data, colWidths=[3*inch, 1.5*inch])
        usuarios_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(usuarios_table)
        story.append(Spacer(1, 20))
        
        # Análisis de Supervisores (si existe)
        if 'SUPERVISOR' in merged_df.columns:
            story.append(Paragraph("👨‍💼 ANÁLISIS DE SUPERVISORES", heading_style))
            
            supervisor_stats = merged_df.groupby('SUPERVISOR').agg({
                'id_tema': 'count',
                'puntos': 'mean'
            }).round(2).reset_index()
            
            supervisor_data = [['Supervisor', 'Total Casos', 'Puntos Promedio']]
            for _, row in supervisor_stats.head(10).iterrows():
                supervisor_data.append([
                    str(row['SUPERVISOR']), 
                    str(row['id_tema']), 
                    str(row['puntos'])
                ])
            
            supervisor_table = Table(supervisor_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            supervisor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(supervisor_table)
            story.append(Spacer(1, 20))
        
        # Información adicional
        story.append(Paragraph("📈 INSIGHTS PRINCIPALES", heading_style))
        
        insights = [
            f"• Ruta más activa: {df['ruta'].value_counts().index[0]} ({df['ruta'].value_counts().iloc[0]} registros)",
            f"• Usuario más activo: {df['usuario'].value_counts().index[0]} ({df['usuario'].value_counts().iloc[0]} registros)",
            f"• Respuesta más común: {df['respuesta_sub'].value_counts().index[0]} ({df['respuesta_sub'].value_counts().iloc[0]} casos)",
            f"• Período de análisis: {df['fecha_registro'].min().strftime('%d/%m/%Y')} - {df['fecha_registro'].max().strftime('%d/%m/%Y')}"
        ]
        
        for insight in insights:
            story.append(Paragraph(insight, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph("Reporte generado automáticamente por Dashboard Feedbacks H1", styles['Italic']))
        
        # Construir PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
        
    except Exception as e:
        # Si hay error, crear un PDF simple con el error
        simple_buffer = BytesIO()
        simple_doc = SimpleDocTemplate(simple_buffer, pagesize=A4)
        simple_story = []
        
        styles = getSampleStyleSheet()
        simple_story.append(Paragraph("Error en la generación del PDF", styles['Title']))
        simple_story.append(Paragraph(f"Error: {str(e)}", styles['Normal']))
        simple_story.append(Paragraph("Por favor, verifique que todas las dependencias estén instaladas correctamente.", styles['Normal']))
        
        simple_doc.build(simple_story)
        simple_buffer.seek(0)
        
        return simple_buffer.getvalue()

# Función principal mejorada
def main():
    # Título principal
    st.markdown('<h1 class="main-header">Seguimiento Feedbacks - DS00</h1>', unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner('🔄 Cargando datos...'):
        feedbacks_df, rutas_df, merged_df = load_data()
    
    if feedbacks_df is None:
        st.error("❌ No se pudieron cargar los datos. Verifica que los archivos Excel estén en el directorio correcto.")
        return
    
    # Sidebar con filtros mejorados
    st.sidebar.markdown("## 🔧 Centro de Control y Filtros")
    
    # Filtro de fechas mejorado
    st.sidebar.markdown("### 📅 Filtros Temporales")
    fecha_min = feedbacks_df['fecha_registro'].min().date()
    fecha_max = feedbacks_df['fecha_registro'].max().date()
    
    # Opciones rápidas de fecha
    opciones_fecha = st.sidebar.selectbox(
        "🚀 Filtros Rápidos de Fecha",
        ["Personalizado", "Último Mes", "Últimos 3 Meses", "Todo el Período"]
    )
    
    if opciones_fecha == "Último Mes":
        fecha_inicio = fecha_max - timedelta(days=30)
        fecha_fin = fecha_max
    elif opciones_fecha == "Últimos 3 Meses":
        fecha_inicio = fecha_max - timedelta(days=90)
        fecha_fin = fecha_max
    elif opciones_fecha == "Todo el Período":
        fecha_inicio = fecha_min
        fecha_fin = fecha_max
    else:
        fecha_inicio, fecha_fin = st.sidebar.date_input(
            "📅 Rango de Fechas Personalizado",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )
      # Más filtros en sidebar
    st.sidebar.markdown("### 🎯 Filtros de Datos")
    
    rutas_disponibles = ['Todas'] + sorted(feedbacks_df['ruta'].unique().tolist())
    ruta_seleccionada = st.sidebar.selectbox("🚚 Seleccionar Ruta", rutas_disponibles)
    
    usuarios_disponibles = ['Todos'] + sorted(feedbacks_df['usuario'].unique().tolist())
    usuario_seleccionado = st.sidebar.selectbox("👤 Seleccionar Usuario", usuarios_disponibles)
    
    # NUEVOS FILTROS: Mes y Semana
    meses_disponibles = ['Todos'] + sorted(feedbacks_df['mes_nombre'].unique().tolist())
    mes_seleccionado = st.sidebar.selectbox("📆 Filtrar por Mes", meses_disponibles)
    
    semanas_disponibles = ['Todas'] + sorted([f"Semana {s}" for s in feedbacks_df['semana'].unique()])
    semana_seleccionada = st.sidebar.selectbox("📅 Filtrar por Semana", semanas_disponibles)
    
    trimestres_disponibles = ['Todos'] + sorted(feedbacks_df['trimestre_nombre'].unique().tolist())
    trimestre_seleccionado = st.sidebar.selectbox("📊 Seleccionar Trimestre", trimestres_disponibles)
    
    # Supervisores y Contratistas si están disponibles
    if 'SUPERVISOR' in merged_df.columns:
        supervisores_disponibles = ['Todos'] + sorted([str(s) for s in merged_df['SUPERVISOR'].dropna().unique()])
        supervisor_seleccionado = st.sidebar.selectbox("👨‍💼 Seleccionar Supervisor", supervisores_disponibles)
    else:
        supervisor_seleccionado = 'Todos'
    
    if 'CONTRATISTA' in merged_df.columns:
        contratistas_disponibles = ['Todos'] + sorted([str(c) for c in merged_df['CONTRATISTA'].dropna().unique()])
        contratista_seleccionado = st.sidebar.selectbox("🏢 Seleccionar Contratista", contratistas_disponibles)
    else:
        contratista_seleccionado = 'Todos'
    
    # Aplicar filtros
    df_filtrado = feedbacks_df[
        (feedbacks_df['fecha_registro'].dt.date >= fecha_inicio) &
        (feedbacks_df['fecha_registro'].dt.date <= fecha_fin)
    ]
    if ruta_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['ruta'] == ruta_seleccionada]
    
    if usuario_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['usuario'] == usuario_seleccionado]
    
    # APLICAR NUEVOS FILTROS
    if mes_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['mes_nombre'] == mes_seleccionado]
    
    if semana_seleccionada != 'Todas':
        semana_numero = int(semana_seleccionada.split()[1])  # Extraer número de "Semana X"
        df_filtrado = df_filtrado[df_filtrado['semana'] == semana_numero]
    
    if trimestre_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['trimestre_nombre'] == trimestre_seleccionado]
      # Filtrar merged_df también con los mismos criterios de df_filtrado
    merged_df_filtrado = merged_df[
        (merged_df['fecha_registro'].dt.date >= fecha_inicio) &
        (merged_df['fecha_registro'].dt.date <= fecha_fin)
    ]
    
    # Aplicar TODOS los filtros a merged_df_filtrado también
    if ruta_seleccionada != 'Todas':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['ruta'] == ruta_seleccionada]
    
    if usuario_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['usuario'] == usuario_seleccionado]
        # También aplicar al df_filtrado principal si hay SUPERVISOR o CONTRATISTA seleccionados
        
    # Aplicar filtros de mes y semana a merged_df también
    if mes_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['mes_nombre'] == mes_seleccionado]
    
    if semana_seleccionada != 'Todas':
        semana_numero = int(semana_seleccionada.split()[1])
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['semana'] == semana_numero]
    
    if trimestre_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['trimestre_nombre'] == trimestre_seleccionado]
    
    # FILTROS CRÍTICOS: Aplicar filtros de supervisor y contratista a AMBOS DataFrames
    if supervisor_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['SUPERVISOR'] == supervisor_seleccionado]
        # También filtrar df_filtrado basado en las rutas que tienen ese supervisor
        rutas_supervisor = merged_df_filtrado['ruta'].unique()
        df_filtrado = df_filtrado[df_filtrado['ruta'].isin(rutas_supervisor)]
    
    if contratista_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['CONTRATISTA'] == contratista_seleccionado]
        # También filtrar df_filtrado basado en las rutas que tienen ese contratista
        rutas_contratista = merged_df_filtrado['ruta'].unique()
        df_filtrado = df_filtrado[df_filtrado['ruta'].isin(rutas_contratista)]
      # Sección de reportes en sidebar
    st.sidebar.markdown("### 📄 Generación de Reportes")
    
    tipo_reporte = st.sidebar.selectbox(
        "📋 Tipo de Reporte",
        ["Completo", "Ejecutivo", "Por Supervisor", "Por Contratista"]
    )
    
    # Botón para reporte de texto
    if st.sidebar.button("📥 Generar Reporte TXT"):
        if tipo_reporte == "Completo":
            reporte = generate_report(df_filtrado, merged_df_filtrado, "completo")
        else:
            reporte = generate_report(df_filtrado, merged_df_filtrado, "ejecutivo")
        
        st.sidebar.download_button(
            label="💾 Descargar Reporte TXT",
            data=reporte,
            file_name=f"reporte_feedbacks_{tipo_reporte.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        st.sidebar.success("✅ Reporte TXT generado exitosamente!")
    
    # Botón para reporte PDF con gráficas
    if st.sidebar.button("📊 Generar Reporte PDF"):
        with st.sidebar.spinner("📊 Generando PDF con gráficas..."):
            try:
                pdf_data = generate_pdf_report(df_filtrado, merged_df_filtrado, tipo_reporte.lower())
                
                st.sidebar.download_button(
                    label="📄 Descargar Reporte PDF",
                    data=pdf_data,
                    file_name=f"reporte_feedbacks_PDF_{tipo_reporte.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                st.sidebar.success("✅ Reporte PDF generado exitosamente!")
            except Exception as e:
                st.sidebar.error(f"❌ Error generando PDF: {str(e)}")
                st.sidebar.info("💡 Asegúrese de que todas las dependencias estén instaladas.")
    
    # Información sobre los reportes
    with st.sidebar.expander("ℹ️ Información sobre Reportes"):
        st.write("""
        **Reporte TXT**: Archivo de texto plano con estadísticas y análisis detallado.
        
        **Reporte PDF**: Documento profesional con gráficas, tablas y análisis visual completo.
        
        - Incluye gráficas de barras
        - Histogramas de distribución
        - Tablas con datos clave
        - Análisis de supervisores
        - Insights principales
        """)
    
    # Métricas KPI mejoradas
    create_advanced_kpi_metrics(df_filtrado, merged_df_filtrado)
      # Menú de navegación principal
    selected = option_menu(
        menu_title=None,
        options=[
            "🏠 Resumen General", 
            "📈 Análisis Temporal", 
            "🚚 Análisis por Rutas", 
            "👨‍💼 Supervisores y Contratistas",
            "👥 Análisis de Personal", 
            "🎯 Análisis de Rendimiento", 
            "📊 Análisis Avanzado",
            "📋 Datos Detallados"
        ],
        icons=["house", "graph-up", "truck", "person-badge", "people", "target", "bar-chart", "table"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )
      # Contenido según la selección
    if selected == "🏠 Resumen General":
        show_general_overview(df_filtrado, merged_df_filtrado)
    elif selected == "📈 Análisis Temporal":
        show_temporal_analysis(df_filtrado)
    elif selected == "🚚 Análisis por Rutas":
        show_routes_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "👨‍💼 Supervisores y Contratistas":
        show_supervisors_contractors_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "👥 Análisis de Personal":
        show_personnel_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "🎯 Análisis de Rendimiento":
        show_performance_analysis(df_filtrado)
    elif selected == "📊 Análisis Avanzado":
        show_advanced_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "📋 Datos Detallados":
        show_detailed_data(df_filtrado, merged_df_filtrado)

def show_general_overview(df, merged_df):
    """Muestra el resumen general mejorado con disposición vertical"""
    st.subheader("📊 Resumen General del Sistema")
    
    # Primera fila - Respuestas más reportadas (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Análisis de Respuestas Más Reportadas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    respuestas_data = df['respuesta_sub'].value_counts().head(15).reset_index()
    respuestas_data.columns = ['respuesta', 'cantidad']
    fig_respuestas = px.bar(
        respuestas_data,
        x='cantidad',
        y='respuesta',
        orientation='h',
        title="🎯 Top 15 Respuestas de Retroalimentación",
        color='cantidad',
        color_continuous_scale='viridis',
        height=700,
        text='cantidad'
    )
    fig_respuestas.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_respuestas.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=200, r=50, t=50, b=50)
    )
    st.plotly_chart(fig_respuestas, use_container_width=True)
    
    # Segunda fila - Rutas vs Calidad (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🚚 Análisis Completo de Rutas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    rutas_respuestas = df.groupby('ruta').agg({
        'respuesta_sub': 'count',
        'puntos': 'mean'
    }).round(2).reset_index()
    rutas_respuestas.columns = ['ruta', 'total_respuestas', 'puntos_promedio']
    rutas_respuestas = rutas_respuestas.sort_values('total_respuestas', ascending=False).head(20)
    fig_rutas = px.scatter(
        rutas_respuestas,
        x='total_respuestas',
        y='puntos_promedio',
        size='total_respuestas',
        hover_data=['ruta'],
        title="🚚 Rutas: Cantidad vs Calidad (Top 20)",
        color='puntos_promedio',
        color_continuous_scale='RdYlBu',
        height=700
    )
    fig_rutas.update_traces(
        marker=dict(
            sizemode='diameter',
            line_width=0
        )
    )
    st.plotly_chart(fig_rutas, use_container_width=True)
    
    # Tercera fila - Distribución temporal (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📅 Distribución Temporal de Registros</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Análisis por mes - Registros y Cierres
    registros_mes = df.groupby(['mes_nombre', 'mes']).agg({
        'id_tema': 'count',
        'fecha_cierre': lambda x: x.notna().sum()
    }).reset_index()
    registros_mes.columns = ['mes_nombre', 'mes_num', 'total_registros', 'total_cierres']
    registros_mes = registros_mes.sort_values('mes_num')
    
    # Crear gráfico con dos líneas usando go.Figure
    fig_temporal = go.Figure()
    
    # Línea de registros totales
    fig_temporal.add_trace(go.Scatter(
        x=registros_mes['mes_nombre'],
        y=registros_mes['total_registros'],
        mode='lines+markers+text',
        name='Total Registros',
        line=dict(color='#1f77b4', width=6),
        marker=dict(size=15, color='#1f77b4', line=dict(width=2, color='white')),
        text=registros_mes['total_registros'],
        texttemplate='<b>%{text}</b>',
        textposition='top center',
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='<b>%{x}</b><br>Registros: %{y}<extra></extra>'
    ))
    
    # Línea de cierres totales
    fig_temporal.add_trace(go.Scatter(
        x=registros_mes['mes_nombre'],
        y=registros_mes['total_cierres'],
        mode='lines+markers+text',
        name='Total Cierres',
        line=dict(color='#ff7f0e', width=6),
        marker=dict(size=15, color='#ff7f0e', line=dict(width=2, color='white')),
        text=registros_mes['total_cierres'],
        texttemplate='<b>%{text}</b>',
        textposition='bottom center',
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='<b>%{x}</b><br>Cierres: %{y}<extra></extra>'
    ))
    
    fig_temporal.update_layout(
        title="📈 Evolución Mensual: Registros vs Cierres",
        xaxis_title="<b>Mes</b>",
        yaxis_title="<b>Número de Casos</b>",
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14, color='white', family='Arial Black')
        ),
        height=700
    )
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Cuarta fila - Análisis de usuarios más activos (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">👥 Usuarios Más Activos del Sistema</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    usuarios_activos = df.groupby('usuario').agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'ruta': 'nunique'
    }).round(2).reset_index()
    usuarios_activos.columns = ['usuario', 'total_registros', 'puntos_promedio', 'rutas_cubiertas']
    usuarios_activos = usuarios_activos.sort_values('total_registros', ascending=False).head(15)
    fig_usuarios = px.bar(
        usuarios_activos,
        x='total_registros',
        y='usuario',
        orientation='h',
        title="👥 Top 15 Usuarios Más Activos",
        color='puntos_promedio',
        color_continuous_scale='plasma',
        height=700,
        text='total_registros'
    )
    fig_usuarios.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_usuarios.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=150, r=50, t=50, b=50)
    )
    st.plotly_chart(fig_usuarios, use_container_width=True)
    
    # Quinta fila - Análisis de puntuación (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⭐ Distribución de Puntuaciones</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    fig_puntos = px.histogram(
        df,
        x='puntos',
        nbins=20,
        title="⭐ Distribución de Puntuaciones en el Sistema",
        color_discrete_sequence=['#ff6b6b'],
        height=700
    )
    fig_puntos.update_traces(
        marker_line_width=0
    )
    fig_puntos.update_layout(
        xaxis_title="Puntuación",
        yaxis_title="Frecuencia",
        bargap=0.1
    )
    st.plotly_chart(fig_puntos, use_container_width=True)
    
    # Sexta fila - Análisis de supervisores (si disponible)
    if 'SUPERVISOR' in merged_df.columns:
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">👨‍💼 Análisis de Supervisores</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        supervisores_data = merged_df.groupby('SUPERVISOR').agg({
            'id_tema': 'count',
            'puntos': 'mean',
            'ruta': 'nunique'
        }).round(2).reset_index()
        supervisores_data.columns = ['supervisor', 'total_casos', 'puntos_promedio', 'rutas_supervisadas']
        supervisores_data = supervisores_data.sort_values('total_casos', ascending=False).head(15)
        fig_supervisores = px.scatter(
            supervisores_data,
            x='total_casos',
            y='puntos_promedio',
            size='rutas_supervisadas',
            hover_data=['supervisor'],
            title="👨‍💼 Supervisores: Casos vs Calidad",
            color='total_casos',
            color_continuous_scale='viridis',
            height=700
        )        
        fig_supervisores.update_traces(
            marker=dict(
                sizemode='diameter',
                line_width=0
            )
        )
        st.plotly_chart(fig_supervisores, use_container_width=True)
        
        supervisor_cierres = merged_df[merged_df['fecha_cierre'].notna()].groupby('SUPERVISOR').agg({
            'id_tema': 'count',
            'puntos': 'mean'
        }).round(2).reset_index()
        supervisor_cierres.columns = ['supervisor', 'total_cierres', 'puntos_promedio']
        supervisor_cierres = supervisor_cierres.sort_values('total_cierres', ascending=False).head(10)
        fig_supervisor_cierres = px.bar(
            supervisor_cierres,
            x='total_cierres',
            y='supervisor',
            orientation='h',
            title="👨‍💼 Top 10 Supervisores con Más Cierres",
            color='puntos_promedio',
            color_continuous_scale='viridis',
            text='total_cierres'
        )
        fig_supervisor_cierres.update_traces(
            texttemplate='<b>%{text}</b>', 
            textposition='outside',
            marker_line_width=0
        )
        fig_supervisor_cierres.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=150, r=50, t=50, b=50)
        )        
        st.plotly_chart(fig_supervisor_cierres, use_container_width=True)

def show_temporal_analysis(df):
    """Muestra análisis temporal mejorado en disposición vertical"""
    st.subheader("📅 Análisis Temporal Profundo y Detallado")
    
    # Primera fila - Análisis por Trimestres
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Análisis Detallado por Trimestres</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    trimestre_data = df.groupby('trimestre_nombre').agg({
        'id_tema': 'count',
        'puntos': ['mean', 'sum'],
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2)
    
    trimestre_data.columns = ['Total_Registros', 'Puntos_Promedio', 'Puntos_Totales', 'Total_Cierres']
    trimestre_data = trimestre_data.reset_index()
    
    fig_trimestre = px.bar(
        trimestre_data,
        x='trimestre_nombre',
        y='Total_Registros',
        title="📊 Registros y Análisis por Trimestre",
        color='Puntos_Promedio',
        color_continuous_scale='viridis',
        text='Total_Registros',
        height=800
    )
    fig_trimestre.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_trimestre.update_layout(
        xaxis_title="Trimestre",
        yaxis_title="Total de Registros",
        margin=dict(l=20, r=20, t=80, b=20)
    )
    st.plotly_chart(fig_trimestre, use_container_width=True)
    
    # Segunda fila - Análisis por Días de la Semana
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📅 Análisis Detallado por Días de la Semana</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    dias_data = df.groupby('dia_semana').agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2).reset_index()
    dias_data.columns = ['dia_semana', 'total_registros', 'puntos_promedio', 'total_cierres']
    
    # Ordenar días de la semana
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_data['dia_semana'] = pd.Categorical(dias_data['dia_semana'], categories=dias_orden)
    dias_data = dias_data.sort_values('dia_semana')
    
    fig_dias = px.bar(
        dias_data,
        x='dia_semana',
        y='total_registros',
        title="📈 Registros por Día de la Semana con Promedio de Puntos",
        color='puntos_promedio',
        color_continuous_scale='plasma',
        text='total_registros',
        height=800
    )
    fig_dias.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_dias.update_layout(
        xaxis_title="Día de la Semana",
        yaxis_title="Total de Registros",
        margin=dict(l=20, r=20, t=80, b=20)
    )
    st.plotly_chart(fig_dias, use_container_width=True)
    
    # Tercera fila - Análisis Mensual Completo
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📆 Análisis Mensual Completo y Detallado</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    monthly_detailed = df.groupby(['mes', 'mes_nombre']).agg({
        'id_tema': 'count',
        'puntos': ['mean', 'sum'],
        'usuario': 'nunique',
        'ruta': 'nunique',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2)
    
    monthly_detailed.columns = ['Total_Registros', 'Puntos_Promedio', 'Puntos_Totales', 'Usuarios_Unicos', 'Rutas_Activas', 'Total_Cierres']
    monthly_detailed = monthly_detailed.reset_index()
    
    fig_monthly_bars = px.bar(
        monthly_detailed,
        x='mes_nombre',
        y='Total_Registros',
        title="📊 Registros Mensuales con Puntos Promedio",
        text='Total_Registros',
        color='Puntos_Promedio',
        color_continuous_scale='viridis',
        height=800
    )
    fig_monthly_bars.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_monthly_bars.update_layout(
        xaxis_title="Mes",
        yaxis_title="Total de Registros",
        margin=dict(l=20, r=20, t=80, b=20)
    )
    st.plotly_chart(fig_monthly_bars, use_container_width=True)
    
    # Cuarta fila - Tendencia de Puntos Promedio Mensual
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📈 Tendencia de Puntos Promedio Mensual</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    fig_trend = px.line(
        monthly_detailed,
        x='mes_nombre',
        y='Puntos_Promedio',
        title="📈 Tendencia de Calidad - Puntos Promedio por Mes",
        markers=True,
        text='Puntos_Promedio',
        height=800
    )
    fig_trend.update_traces(
        line_width=6,
        marker_size=12,
        texttemplate='%{text:.2f}',
        textposition='top center'
    )
    fig_trend.update_layout(
        xaxis_title="Mes",
        yaxis_title="Puntos Promedio",
        margin=dict(l=20, r=20, t=80, b=20)
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Quinta fila - Análisis de Usuarios Únicos y Rutas Activas
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">👥 Análisis de Actividad: Usuarios y Rutas por Mes</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    fig_activity = go.Figure()
    fig_activity.add_trace(go.Bar(
        x=monthly_detailed['mes_nombre'],
        y=monthly_detailed['Usuarios_Unicos'],
        name='Usuarios Únicos',
        text=monthly_detailed['Usuarios_Unicos'],
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker_color='lightblue',
        marker_line_width=0
    ))
    fig_activity.add_trace(go.Bar(
        x=monthly_detailed['mes_nombre'],
        y=monthly_detailed['Rutas_Activas'],
        name='Rutas Activas',
        text=monthly_detailed['Rutas_Activas'],
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker_color='orange',
        marker_line_width=0
    ))
    fig_activity.update_layout(
        title="👥 Usuarios Únicos y Rutas Activas por Mes",
        xaxis_title="Mes",
        yaxis_title="Cantidad",
        height=800,
        barmode='group',
        margin=dict(l=20, r=20, t=80, b=20)
    )
    st.plotly_chart(fig_activity, use_container_width=True)

def show_routes_analysis(df, merged_df):
    """Análisis completo por rutas con supervisores y contratistas"""
    st.subheader("🚚 Análisis Completo por Rutas, Supervisores y Contratistas")
      # Primera fila - Top 3 rutas por contratista (fila completa)
    if 'CONTRATISTA' in merged_df.columns and 'SUPERVISOR' in merged_df.columns:
        st.markdown(
            """
            <div class="top-performance">
                <h3 style="color: white; margin: 0;">🏆 Top 3 Rutas por Contratista</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Análisis por contratista
        contratista_rutas = merged_df.groupby(['CONTRATISTA', 'ruta']).size().reset_index()
        contratista_rutas.columns = ['contratista', 'ruta', 'registros']
        
        # Mejor ruta por cada contratista
        top_rutas_contratista = contratista_rutas.groupby('contratista').apply(
            lambda x: x.nlargest(1, 'registros')
        ).reset_index(drop=True)
        
        # Ordenar por contratista para mejor visualización
        top_rutas_contratista = top_rutas_contratista.sort_values(['contratista', 'registros'], ascending=[True, False])
        
        # Crear etiquetas más descriptivas para mejor organización
        top_rutas_contratista['etiqueta_completa'] = (
            top_rutas_contratista['contratista'].astype(str) + ' → ' + 
            top_rutas_contratista['ruta'].astype(str)
        )        
        fig_contratista_rutas = px.bar(
            top_rutas_contratista,
            x='registros',
            y='etiqueta_completa',
            title="🏢 Mejor Ruta por Contratista - Análisis Detallado",
            orientation='h',
            height=900,  # Aumentar altura
            text='registros',
            color='registros',
            color_continuous_scale='Plasma'
        )
        
        fig_contratista_rutas.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=0,
            textfont_size=14,
            textfont_color='white',
            textfont_family='Arial Black'
        )
        
        fig_contratista_rutas.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont_size': 12,
                'tickfont_color': 'white'
            },
            margin=dict(l=350, r=100, t=100, b=80),  # Más espacio para etiquetas descriptivas
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font_size=16,
            xaxis_title="<b>Número de Registros</b>",
            yaxis_title="<b>Ruta</b>"
        )
        st.plotly_chart(fig_contratista_rutas, use_container_width=True)
          # Segunda fila - Top 3 rutas por supervisor (fila completa)
        st.markdown(
            """
            <div class="top-performance">
                <h3 style="color: white; margin: 0;">🏆 Top 3 Rutas por Supervisor</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
          # Análisis por supervisor
        supervisor_rutas = merged_df.groupby(['SUPERVISOR', 'ruta']).size().reset_index()
        supervisor_rutas.columns = ['supervisor', 'ruta', 'registros']
        
        # Top 3 rutas por cada supervisor
        top_rutas_supervisor = supervisor_rutas.groupby('supervisor').apply(
            lambda x: x.nlargest(3, 'registros')
        ).reset_index(drop=True)
        
        # Ordenar por supervisor para mejor visualización
        top_rutas_supervisor = top_rutas_supervisor.sort_values(['supervisor', 'registros'], ascending=[True, False])
        
        # Crear etiquetas más descriptivas para mejor organización
        top_rutas_supervisor['etiqueta_completa'] = (
            top_rutas_supervisor['supervisor'].astype(str) + ' → ' + 
            top_rutas_supervisor['ruta'].astype(str)
        )        
        fig_supervisor_rutas = px.bar(
            top_rutas_supervisor,
            x='registros',
            y='etiqueta_completa',
            title="👨‍💼 Top 3 Rutas por Supervisor - Análisis Detallado",
            orientation='h',
            height=900,  # Aumentar altura
            text='registros',
            color='registros',
            color_continuous_scale='Plasma'
        )
        
        fig_supervisor_rutas.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=0,
            textfont_size=14,
            textfont_color='white',
            textfont_family='Arial Black'
        )
        
        fig_supervisor_rutas.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont_size': 12,
                'tickfont_color': 'white'
            },
            margin=dict(l=350, r=100, t=100, b=80),  # Más espacio para etiquetas descriptivas
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font_size=16,
            xaxis_title="<b>Número de Registros</b>",
            yaxis_title="<b>Ruta</b>"
        )
        st.plotly_chart(fig_supervisor_rutas, use_container_width=True)      
    # Cuarta fila - Top rutas con más registros generales (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🚚 Top 20 Rutas con Más Registros Totales</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    top_rutas_general = df['ruta'].value_counts().head(20).reset_index()
    top_rutas_general.columns = ['ruta', 'total_registros']
    fig_top_rutas = px.bar(
        top_rutas_general,
        x='total_registros',
        y='ruta',
        orientation='h',
        title="🏆 Top 20 Rutas con Más Registros",
        color='total_registros',
        color_continuous_scale='Plasma',
        height=800,
        text='total_registros'
    )
    fig_top_rutas.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0,
        textfont_size=14,
        textfont_color='white',
        textfont_family='Arial Black'
    )
    fig_top_rutas.update_layout(
        yaxis={
            'categoryorder': 'total ascending',
            'tickfont_size': 14,
            'tickfont_color': 'white'
        },
        margin=dict(l=150, r=100, t=80, b=50),
        xaxis_title="<b>Total de Registros</b>",
        yaxis_title="<b>Ruta</b>",
        font=dict(size=14)
    )
    st.plotly_chart(fig_top_rutas, use_container_width=True)
      # Tercera fila - Análisis de eficiencia por ruta (fila completa)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Análisis de Eficiencia por Rutas: ¿Qué nos dice esta gráfica?</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Explicación detallada de la gráfica
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h4 style="color: white; margin: 0;">💡 ¿Cómo interpretar esta gráfica de burbujas?</h4>
        <p style="color: white; margin: 10px 0;">
            <strong>• Eje X (horizontal):</strong> Total de registros de feedbacks por ruta<br>
            <strong>• Eje Y (vertical):</strong> Puntos promedio de calidad (1-10)<br>
            <strong>• Tamaño de burbuja:</strong> Tasa de cierre (% de casos resueltos)<br>
            <strong>• Color:</strong> Intensidad de la tasa de cierre (Verde = alta, Rojo = baja)
        </p>
        <p style="color: white; margin: 10px 0; font-weight: bold;">
            🎯 <strong>Rutas ideales:</strong> Burbujas grandes y verdes en la parte superior derecha (alto volumen + alta calidad + alta tasa de cierre)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    ruta_eficiencia = df.groupby('ruta').agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2).reset_index()
    ruta_eficiencia.columns = ['ruta', 'total_registros', 'puntos_promedio', 'total_cierres']
    ruta_eficiencia['tasa_cierre'] = (ruta_eficiencia['total_cierres'] / ruta_eficiencia['total_registros']) * 100
    
    # Filtrar rutas con al menos 10 registros para análisis más significativo
    ruta_eficiencia_filtrada = ruta_eficiencia[ruta_eficiencia['total_registros'] >= 1]
    
    # Añadir categorías de rendimiento para mejor interpretación
    def categorizar_rendimiento(row):
        if row['puntos_promedio'] >= 7 and row['tasa_cierre'] >= 80:
            return "🟢 Excelente"
        elif row['puntos_promedio'] >= 5 and row['tasa_cierre'] >= 60:
            return "🟡 Bueno"
        else:
            return "🔴 Necesita Mejora"
    
    ruta_eficiencia_filtrada['categoria_rendimiento'] = ruta_eficiencia_filtrada.apply(categorizar_rendimiento, axis=1)
    
    fig_eficiencia = px.scatter(
        ruta_eficiencia_filtrada,
        x='total_registros',
        y='puntos_promedio',
        size='tasa_cierre',
        hover_data={
            'ruta': True,
            'tasa_cierre': ':.1f',
            'total_cierres': True,
            'categoria_rendimiento': True,
            'total_registros': True,
            'puntos_promedio': ':.2f'
        },        title="📊 Eficiencia Integral por Ruta: Volumen vs Calidad vs Tasa de Cierre",
        color='tasa_cierre',
        color_continuous_scale='RdYlGn',
        height=800,
        labels={
            'total_registros': 'Total de Registros de Feedback',
            'puntos_promedio': 'Calidad Promedio (Puntos 1-10)',
            'tasa_cierre': 'Tasa de Cierre (%)',
            'ruta': 'Ruta'
        }
    )
    fig_eficiencia.update_traces(
        marker=dict(
            sizemode='diameter',
            sizemin=8,
            size=20,
            line_width=0
        )
    )    
    fig_eficiencia.update_layout(
        margin=dict(l=20, r=20, t=80, b=20),
        xaxis_title="<b>Total de Registros de Feedback</b>",
        yaxis_title="<b>Calidad Promedio (Puntos 1-10)</b>",        
        coloraxis_colorbar=dict(
            title="Tasa de Cierre (%)"
        )
    )
    st.plotly_chart(fig_eficiencia, use_container_width=True)
    
    # Tabla resumen de las mejores y peores rutas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 5 Rutas Más Eficientes")
        top_eficientes = ruta_eficiencia_filtrada.nlargest(5, 'tasa_cierre')[['ruta', 'total_registros', 'puntos_promedio', 'tasa_cierre', 'categoria_rendimiento']]
        top_eficientes.columns = ['Ruta', 'Registros', 'Calidad', 'Tasa Cierre %', 'Categoría']
        st.dataframe(top_eficientes, use_container_width=True)
    
    with col2:
        st.markdown("#### ⚠️ Top 5 Rutas que Necesitan Atención")
        menor_eficientes = ruta_eficiencia_filtrada.nsmallest(5, 'tasa_cierre')[['ruta', 'total_registros', 'puntos_promedio', 'tasa_cierre', 'categoria_rendimiento']]
        menor_eficientes.columns = ['Ruta', 'Registros', 'Calidad', 'Tasa Cierre %', 'Categoría']
        st.dataframe(menor_eficientes, use_container_width=True)

    # Quinta fila - Top Offenders: Rutas con pocos o ningún registro
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⚠️ Top Offenders - Rutas con Baja Actividad</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de rutas con pocos registros
    rutas_con_pocos_registros = ruta_eficiencia[ruta_eficiencia['total_registros'] <= 5].sort_values('total_registros', ascending=True)
    
    if not rutas_con_pocos_registros.empty:
        fig_offenders_rutas = px.bar(
            rutas_con_pocos_registros.head(15),
            x='total_registros',
            y='ruta',
            orientation='h',
            title="⚠️ Top 15 Rutas con Menor Actividad (≤5 registros)",
            color='puntos_promedio',
            color_continuous_scale='Reds',
            height=600,
            text='total_registros'
        )
        fig_offenders_rutas.update_traces(
            texttemplate='%{text} registros',
            textposition='outside',
            marker_line_width=0
        )
        fig_offenders_rutas.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=150, r=50, t=80, b=50),
            xaxis_title="<b>Número de Registros</b>",
            yaxis_title="<b>Ruta</b>"
        )
        st.plotly_chart(fig_offenders_rutas, use_container_width=True)
          # Tabla con detalles de rutas con baja actividad
        st.markdown("#### 📋 Detalles de Rutas con Baja Actividad")
        offenders_details = rutas_con_pocos_registros[['ruta', 'total_registros', 'puntos_promedio', 'tasa_cierre']].copy()
        offenders_details.columns = ['Ruta', 'Total Registros', 'Puntos Promedio', 'Tasa Cierre (%)']
        st.dataframe(clean_dataframe_for_display(offenders_details), use_container_width=True)
    else:
        st.info("✅ No hay rutas con baja actividad (todas tienen más de 5 registros)")    # Sexta fila - Análisis completo de supervisores y contratistas
    if 'SUPERVISOR' in merged_df.columns:
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">👨‍💼 Análisis Completo de Supervisores - Total vs Cerrados</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Análisis detallado de supervisores
        supervisor_analysis = merged_df.groupby('SUPERVISOR').agg({
            'id_tema': 'count',
            'puntos': 'mean',
            'fecha_cierre': lambda x: x.notna().sum(),
            'ruta': 'nunique',
            'codigo_cliente': 'nunique'
        }).round(2).reset_index()
        supervisor_analysis.columns = ['supervisor', 'total_casos', 'puntos_promedio', 'casos_cerrados', 'rutas_supervisadas', 'clientes_unicos']
        supervisor_analysis['tasa_cierre'] = (supervisor_analysis['casos_cerrados'] / supervisor_analysis['total_casos']) * 100
        supervisor_analysis['casos_pendientes'] = supervisor_analysis['total_casos'] - supervisor_analysis['casos_cerrados']
        supervisor_analysis = supervisor_analysis.sort_values('total_casos', ascending=False)
          # Gráfico de casos totales vs cerrados - Una línea completa
        supervisor_top = supervisor_analysis.head(10)
        fig_supervisor_comparison = px.bar(
            supervisor_top,
            x=['casos_cerrados', 'casos_pendientes'],
            y='supervisor',
            orientation='h',
            title="📊 Casos Cerrados vs Pendientes por Supervisor (Top 10)",
            labels={'value': 'Número de Casos', 'variable': 'Estado', 'supervisor': 'Supervisor'},
            color_discrete_map={'casos_cerrados': '#32CD32', 'casos_pendientes': '#FF6347'},
            height=700,
            text='value'
        )
        fig_supervisor_comparison.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=0,
            textfont_size=12,
            textfont_color='white'
        )
        fig_supervisor_comparison.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=200, r=100, t=80, b=50),
            xaxis_title="<b>Número de Casos</b>",
            yaxis_title="<b>Supervisor</b>",
            legend_title="Estado del Caso"
        )
        st.plotly_chart(fig_supervisor_comparison, use_container_width=True)
        
        # Gráfico de tasa de cierre por supervisor - Una línea completa
        fig_supervisor_cierre = px.bar(
            supervisor_analysis.head(10),
            x='tasa_cierre',
            y='supervisor',
            orientation='h',
            title="📈 Tasa de Cierre por Supervisor (Top 10)",
            color='puntos_promedio',
            color_continuous_scale='RdYlGn',
            height=700,
            text='tasa_cierre'
        )
        fig_supervisor_cierre.update_traces(
            texttemplate='<b>%{text:.1f}%</b>',
            textposition='outside',
            marker_line_width=0,
            textfont_size=12,
           
            textfont_color='white'
        )
        fig_supervisor_cierre.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=200, r=100, t=80, b=50),
            xaxis_title="<b>Tasa de Cierre (%)</b>",
            yaxis_title="<b>Supervisor</b>"
        )
        st.plotly_chart(fig_supervisor_cierre, use_container_width=True)
        
        # Tabla con análisis detallado de supervisores
        st.markdown("#### 📊 Análisis Completo de Supervisores")
        supervisor_details = supervisor_analysis[['supervisor', 'total_casos', 'casos_cerrados', 'casos_pendientes', 'tasa_cierre', 'puntos_promedio', 'rutas_supervisadas', 'clientes_unicos']].copy()
        supervisor_details.columns = ['Supervisor', 'Total Casos', 'Casos Cerrados', 'Casos Pendientes', 'Tasa Cierre (%)', 'Puntos Promedio', 'Rutas Supervisadas', 'Clientes Únicos']
        st.dataframe(clean_dataframe_for_display(supervisor_details), use_container_width=True)

    # Análisis completo de contratistas
    if 'CONTRATISTA' in merged_df.columns:
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">🏢 Análisis Detallado de Contratistas - Tipos de Casos</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Análisis detallado de contratistas
        contratista_analysis = merged_df.groupby('CONTRATISTA').agg({
            'id_tema': 'count',
            'puntos': 'mean',
            'fecha_cierre': lambda x: x.notna().sum(),
            'ruta': 'nunique',
            'motivo_retro': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
            'respuesta_sub': 'nunique'
        }).round(2).reset_index()
        contratista_analysis.columns = ['contratista', 'total_casos', 'puntos_promedio', 'casos_cerrados', 'rutas_trabajadas', 'motivo_principal', 'tipos_respuesta']
        contratista_analysis['tasa_cierre'] = (contratista_analysis['casos_cerrados'] / contratista_analysis['total_casos']) * 100
        contratista_analysis['casos_pendientes'] = contratista_analysis['total_casos'] - contratista_analysis['casos_cerrados']
        contratista_analysis = contratista_analysis.sort_values('total_casos', ascending=False)
        
        # Análisis de tipos de casos por contratista
        contratista_motivos = merged_df.groupby(['CONTRATISTA', 'motivo_retro']).size().reset_index()
        contratista_motivos.columns = ['contratista', 'motivo_retro', 'cantidad']
        
        # Top 3 motivos por contratista
        top_motivos_contratista = contratista_motivos.groupby('contratista').apply(
            lambda x: x.nlargest(3, 'cantidad')
        ).reset_index(drop=True)
          # Gráfico de casos por contratista - Una línea completa
        fig_contratista_casos = px.bar(
            contratista_analysis.head(10),
            x=['casos_cerrados', 'casos_pendientes'],
            y='contratista',
            orientation='h',
            title="📊 Casos Cerrados vs Pendientes por Contratista (Top 10)",
            labels={'value': 'Número de Casos', 'variable': 'Estado', 'contratista': 'Contratista'},
            color_discrete_map={'casos_cerrados': '#1E90FF', 'casos_pendientes': '#FFD700'},
            height=700,
            text='value'
        )
        fig_contratista_casos.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=0,
            textfont_size=12,
            textfont_color='white'
        )
        fig_contratista_casos.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=250, r=100, t=80, b=50),
            xaxis_title="<b>Número de Casos</b>",
            yaxis_title="<b>Contratista</b>",
            legend_title="Estado del Caso"
        )
        st.plotly_chart(fig_contratista_casos, use_container_width=True)
        
        # Gráfico de tipos de motivos por contratista - Una línea completa
        fig_motivos_contratista = px.bar(
            top_motivos_contratista.head(15),
            x='cantidad',
            y='motivo_retro',
            color='contratista',
            orientation='h',
            title="🎯 Top Motivos por Contratista",
            height=700,
            text='cantidad'
        )
        fig_motivos_contratista.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=0,
            textfont_size=12,
            textfont_color='white'
        )
        fig_motivos_contratista.update_layout(
            yaxis={
            'categoryorder': 'total ascending'},
            margin=dict(l=300, r=100, t=80, b=50),
            xaxis_title="<b>Número de Casos</b>",
            yaxis_title="<b>Motivo</b>"
        )
        st.plotly_chart(fig_motivos_contratista, use_container_width=True)
        
        # Tabla con análisis detallado de contratistas
        st.markdown("#### 📊 Análisis Completo de Contratistas")
        contratista_details = contratista_analysis[['contratista', 'total_casos', 'casos_cerrados', 'casos_pendientes', 'tasa_cierre', 'puntos_promedio', 'rutas_trabajadas', 'motivo_principal', 'tipos_respuesta']].copy()
        contratista_details.columns = ['Contratista', 'Total Casos', 'Casos Cerrados', 'Casos Pendientes', 'Tasa Cierre (%)', 'Puntos Promedio', 'Rutas Trabajadas', 'Motivo Principal', 'Tipos de Respuesta']
        st.dataframe(clean_dataframe_for_display(contratista_details), use_container_width=True)

    # Séptima fila - Análisis de motivos específicos en lugar de números
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Análisis Detallado de Motivos Específicos</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis detallado de motivos con nombres específicos
    motivos_analysis = df.groupby('motivo_retro').agg({
        'id_tema': 'count',
        'puntos': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique'
    }).round(2)
    motivos_analysis.columns = ['total_casos', 'puntos_promedio', 'desviacion_puntos', 'casos_cerrados', 'clientes_afectados']
    motivos_analysis = motivos_analysis.reset_index()
    motivos_analysis['tasa_cierre'] = (motivos_analysis['casos_cerrados'] / motivos_analysis['total_casos']) * 100
    motivos_analysis = motivos_analysis.sort_values('total_casos', ascending=False)
    
    # Gráfico de motivos más comunes con información detallada
    fig_motivos = px.bar(
        motivos_analysis.head(15),
        x='total_casos',
        y='motivo_retro',
        orientation='h',
        title="🎯 Top 15 Motivos Específicos de Retroalimentación",
        color='puntos_promedio',
        color_continuous_scale='RdYlBu',
        height=700,
        hover_data={
            'motivo_retro': True,
            'total_casos': True,
            'puntos_promedio': ':.2f',
            'tasa_cierre': ':.1f',
            'clientes_afectados': True
        }
    )
    fig_motivos.update_traces(
        texttemplate='%{text} casos',
        textposition='outside',
        marker_line_width=0
    )
    fig_motivos.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=200, r=50, t=80, b=50)
    )
    st.plotly_chart(fig_motivos, use_container_width=True)
    
    # Tabla detallada de motivos
    st.markdown("#### 📋 Detalles Completos de Motivos")
    motivos_details = motivos_analysis[['motivo_retro', 'total_casos', 'puntos_promedio', 'tasa_cierre', 'clientes_afectados', 'desviacion_puntos']].copy()
    motivos_details.columns = ['Motivo', 'Total Casos', 'Puntos Promedio', 'Tasa Cierre (%)', 'Clientes Afectados', 'Desviación Puntos']
    st.dataframe(clean_dataframe_for_display(motivos_details), use_container_width=True)

    # Octava fila - Análisis de respuestas específicas
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💬 Análisis de Tipos de Respuesta Específicas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de respuestas específicas
    respuestas_analysis = df.groupby('respuesta_sub').agg({
        'id_tema': 'count',
        'puntos': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique'
    }).round(2)
    respuestas_analysis.columns = ['total_casos', 'puntos_promedio', 'desviacion_puntos', 'casos_cerrados', 'clientes_afectados']
    respuestas_analysis = respuestas_analysis.reset_index()
    respuestas_analysis['tasa_cierre'] = (respuestas_analysis['casos_cerrados'] / respuestas_analysis['total_casos']) * 100
    respuestas_analysis = respuestas_analysis.sort_values('total_casos', ascending=False)
    
    # Gráfico de respuestas más comunes
    fig_respuestas = px.bar(
        respuestas_analysis.head(15),
        x='total_casos',
        y='respuesta_sub',
        orientation='h',
        title="💬 Top 15 Tipos de Respuesta Específicas",
        color='puntos_promedio',
        color_continuous_scale='Viridis',
        height=700,
        hover_data={
            'respuesta_sub': True,
            'total_casos': True,
            'puntos_promedio': ':.2f',
            'tasa_cierre': ':.1f',
            'clientes_afectados': True
        }
    )
    fig_respuestas.update_traces(
        texttemplate='%{text} casos',
        textposition='outside',
        marker_line_width=0
    )
    fig_respuestas.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=200, r=50, t=80, b=50)
    )
    st.plotly_chart(fig_respuestas, use_container_width=True)
    
    # Tabla detallada de respuestas    st.markdown("#### 📋 Detalles Completos de Tipos de Respuesta")
    respuestas_details = respuestas_analysis[['respuesta_sub', 'total_casos', 'puntos_promedio', 'tasa_cierre', 'clientes_afectados', 'desviacion_puntos']].copy()
    respuestas_details.columns = ['Tipo de Respuesta', 'Total Casos', 'Puntos Promedio', 'Tasa Cierre (%)', 'Clientes Afectados', 'Desviación Puntos']
    st.dataframe(clean_dataframe_for_display(respuestas_details), use_container_width=True)    # Novena fila - Análisis específico de clientes con múltiples reportes del mismo motivo (usando respuesta_sub)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🔍 Análisis de Clientes con Múltiples Reportes del Mismo Motivo Real</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Convertir codigo_cliente a string para mejor manejo
    df['codigo_cliente_str'] = df['codigo_cliente'].astype(str)
    
    # Analizar clientes que tienen múltiples reportes del mismo motivo real (respuesta_sub)
    cliente_motivo_analysis = df.groupby(['codigo_cliente_str', 'respuesta_sub']).agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2).reset_index()
    cliente_motivo_analysis.columns = ['codigo_cliente', 'motivo_real', 'total_reportes', 'puntos_promedio', 'casos_cerrados']
    
    # Filtrar clientes con más de 3 reportes del mismo motivo real
    clientes_repetitivos = cliente_motivo_analysis[cliente_motivo_analysis['total_reportes'] >= 3].sort_values('total_reportes', ascending=False)
    
    if not clientes_repetitivos.empty:
        st.markdown(f"##### 🎯 Se encontraron {len(clientes_repetitivos)} clientes con 3+ reportes del mismo motivo real")
        fig_clientes_repetitivos = px.bar(
            clientes_repetitivos.head(20),
            x='total_reportes',
            y='codigo_cliente',
            orientation='h',
            title="🚨 Top 20 Clientes con Más Reportes del Mismo Motivo Real",
            color='motivo_real',
            height=800,
            text='total_reportes',
            hover_data={
                'codigo_cliente': True,
                'motivo_real': True,
                'total_reportes': True,
                'puntos_promedio': ':.2f',
                'casos_cerrados': True
            }
        )
        fig_clientes_repetitivos.update_traces(
            texttemplate='<b>%{text} reportes</b>',
            textposition='outside',
            marker_line_width=0,
            textfont=dict(size=14, color='white', family='Arial Black')
        )
        fig_clientes_repetitivos.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickformat': '',
                'type': 'category',
                'tickfont': dict(size=12, color='white')
            },
            margin=dict(l=150, r=100, t=80, b=50),
            xaxis_title="<b>Número de Reportes</b>",
            yaxis_title="<b>Código Cliente</b>",
            font=dict(size=12)
        )
        st.plotly_chart(fig_clientes_repetitivos, use_container_width=True)
        
        # Tabla detallada
        st.markdown("##### 📋 Detalles de Clientes con Reportes Repetitivos del Mismo Motivo")
        clientes_details = clientes_repetitivos[['codigo_cliente', 'motivo_real', 'total_reportes', 'puntos_promedio', 'casos_cerrados']].copy()
        clientes_details.columns = ['Cliente', 'Motivo Real', 'Total Reportes', 'Puntos Promedio', 'Casos Cerrados']
        st.dataframe(clean_dataframe_for_display(clientes_details), use_container_width=True)
        
        # Análisis de los motivos más problemáticos
        st.markdown("##### 🎯 Top 10 Motivos Reales Más Problemáticos")
        motivos_problematicos = clientes_repetitivos.groupby('motivo_real').agg({
            'codigo_cliente': 'count',
            'total_reportes': 'sum',
            'puntos_promedio': 'mean'
        }).round(2).reset_index()
        motivos_problematicos.columns = ['motivo_real', 'clientes_afectados', 'total_reportes_acumulados', 'puntos_promedio']
        motivos_problematicos = motivos_problematicos.sort_values('clientes_afectados', ascending=False).head(10)
        
        fig_motivos_problematicos = px.bar(
            motivos_problematicos,
            x='clientes_afectados',
            y='motivo_real',
            orientation='h',
            title="🎯 Top 10 Motivos Reales con Más Clientes con Reportes Repetitivos",
            color='puntos_promedio',
            color_continuous_scale='RdYlGn',
            height=600,
            text='clientes_afectados'
        )
        fig_motivos_problematicos.update_traces(
            texttemplate='%{text} clientes',
            textposition='outside'
        )
        fig_motivos_problematicos.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=250, r=50, t=80, b=50)
        )
        st.plotly_chart(fig_motivos_problematicos, use_container_width=True)
        
        st.markdown("##### 📋 Detalles de Motivos Problemáticos")
        motivos_problematicos_details = motivos_problematicos[['motivo_real', 'clientes_afectados', 'total_reportes_acumulados', 'puntos_promedio']].copy()
        motivos_problematicos_details.columns = ['Motivo Real', 'Clientes Afectados', 'Total Reportes', 'Puntos Promedio']        
        st.dataframe(clean_dataframe_for_display(motivos_problematicos_details), use_container_width=True)
    else:
        st.info("✅ No se encontraron clientes con 3+ reportes del mismo motivo real")    # --- NUEVA SECCIÓN: Cumplimiento de Meta Mensual por Ruta, Supervisor y Contratista ---
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">📅 Cumplimiento de Meta Mensual (10 registros/ruta)</h3>
            </div>
            """,
            unsafe_allow_html=True
    )
    
    # Filtros dinámicos mejorados
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        meses_disponibles = sorted(df['mes_nombre'].unique().tolist())
        mes_meta = st.selectbox("📅 Selecciona el mes:", meses_disponibles, key="meta_mes")
    
    with col_filtro2:
        if 'SUPERVISOR' in merged_df.columns:
            supervisores_disp = ['Todos'] + sorted(merged_df['SUPERVISOR'].dropna().unique().tolist())
            supervisor_meta = st.selectbox("👨‍💼 Filtrar por Supervisor:", supervisores_disp, key="meta_supervisor")
        else:
            supervisor_meta = 'Todos'
    
    with col_filtro3:
        if 'CONTRATISTA' in merged_df.columns:
            contratistas_disp = ['Todos'] + sorted(merged_df['CONTRATISTA'].dropna().unique().tolist())
            contratista_meta = st.selectbox("🏢 Filtrar por Contratista:", contratistas_disp, key="meta_contratista")
        else:
            contratista_meta = 'Todos'
    
    # Aplicar filtros
    df_meta = merged_df[merged_df['mes_nombre'] == mes_meta].copy()
    
    if supervisor_meta != 'Todos' and 'SUPERVISOR' in df_meta.columns:
        df_meta = df_meta[df_meta['SUPERVISOR'] == supervisor_meta]
    
    if contratista_meta != 'Todos' and 'CONTRATISTA' in df_meta.columns:
        df_meta = df_meta[df_meta['CONTRATISTA'] == contratista_meta]
    
    # --- Análisis por SUPERVISOR ---
    if 'SUPERVISOR' in df_meta.columns:
        st.markdown("### 👨‍💼 Análisis por Supervisores")
        
        # Calcular métricas por supervisor y ruta
        supervisor_rutas = df_meta.groupby(['SUPERVISOR', 'ruta']).agg({'id_tema':'count'}).reset_index()
        supervisor_rutas['Meta Cumplida'] = supervisor_rutas['id_tema'] >= 10
        supervisor_rutas['Estado'] = supervisor_rutas['Meta Cumplida'].map(lambda x: '✅ Cumple' if x else '❌ No Cumple')
        supervisor_rutas = supervisor_rutas.rename(columns={'id_tema':'Registros'})
        
        # Tabla detallada
        st.dataframe(
            clean_dataframe_for_display(supervisor_rutas[['SUPERVISOR', 'ruta', 'Registros', 'Estado']]), 
            use_container_width=True
        )
        
        # KPIs por supervisor
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        with col_kpi1:
            total_rutas_sup = supervisor_rutas.shape[0]
            rutas_cumplen_sup = supervisor_rutas['Meta Cumplida'].sum()
            porcentaje_cumple_sup = (rutas_cumplen_sup/total_rutas_sup*100) if total_rutas_sup > 0 else 0
            st.metric("📊 % Rutas que Cumplen Meta", f"{porcentaje_cumple_sup:.1f}%")
        
        with col_kpi2:
            st.metric("📈 Rutas que Cumplen", f"{rutas_cumplen_sup}/{total_rutas_sup}")
        
        with col_kpi3:
            rutas_no_cumplen_sup = total_rutas_sup - rutas_cumplen_sup
            st.metric("⚠️ Rutas que NO Cumplen", f"{rutas_no_cumplen_sup}")
        
        # Ranking de supervisores
        ranking_supervisores = supervisor_rutas.groupby('SUPERVISOR').agg({
            'Meta Cumplida': ['count', 'sum'],
            'Registros': 'mean'
        }).round(2)
        ranking_supervisores.columns = ['Total_Rutas', 'Rutas_Cumplen', 'Registros_Promedio']
        ranking_supervisores = ranking_supervisores.reset_index()
        ranking_supervisores['Porcentaje_Cumplimiento'] = (ranking_supervisores['Rutas_Cumplen'] / ranking_supervisores['Total_Rutas'] * 100).round(1)
        ranking_supervisores = ranking_supervisores.sort_values('Porcentaje_Cumplimiento', ascending=False)
        
        # Gráfica de ranking de supervisores
        fig_ranking_sup = px.bar(
            ranking_supervisores, 
            x='SUPERVISOR', 
            y='Porcentaje_Cumplimiento',
            color='Porcentaje_Cumplimiento',
            color_continuous_scale='RdYlGn',
            title='🏆 Ranking de Supervisores por % de Cumplimiento de Meta',
            text='Porcentaje_Cumplimiento'
        )
        fig_ranking_sup.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_ranking_sup.update_layout(
            xaxis_title="<b>Supervisor</b>",
            yaxis_title="<b>% de Cumplimiento</b>",
            height=500
        )
        st.plotly_chart(fig_ranking_sup, use_container_width=True)
    
    # --- Análisis por CONTRATISTA ---
    if 'CONTRATISTA' in df_meta.columns:
        st.markdown("### 🏢 Análisis por Contratistas")
        
        # Calcular métricas por contratista y ruta
        contratista_rutas = df_meta.groupby(['CONTRATISTA', 'ruta']).agg({'id_tema':'count'}).reset_index()
        contratista_rutas['Meta Cumplida'] = contratista_rutas['id_tema'] >= 10
        contratista_rutas['Estado'] = contratista_rutas['Meta Cumplida'].map(lambda x: '✅ Cumple' if x else '❌ No Cumple')
        contratista_rutas = contratista_rutas.rename(columns={'id_tema':'Registros'})
        
        # Tabla detallada
        st.dataframe(
            clean_dataframe_for_display(contratista_rutas[['CONTRATISTA', 'ruta', 'Registros', 'Estado']]), 
            use_container_width=True
        )
        
        # KPIs por contratista
        col_kpi4, col_kpi5, col_kpi6 = st.columns(3)
        
        with col_kpi4:
            total_rutas_con = contratista_rutas.shape[0]
            rutas_cumplen_con = contratista_rutas['Meta Cumplida'].sum()
            porcentaje_cumple_con = (rutas_cumplen_con/total_rutas_con*100) if total_rutas_con > 0 else 0
            st.metric("📊 % Rutas que Cumplen Meta", f"{porcentaje_cumple_con:.1f}%")
        
        with col_kpi5:
            st.metric("📈 Rutas que Cumplen", f"{rutas_cumplen_con}/{total_rutas_con}")
        
        with col_kpi6:
            rutas_no_cumplen_con = total_rutas_con - rutas_cumplen_con
            st.metric("⚠️ Rutas que NO Cumplen", f"{rutas_no_cumplen_con}")
        
        # Ranking de contratistas
        ranking_contratistas = contratista_rutas.groupby('CONTRATISTA').agg({
            'Meta Cumplida': ['count', 'sum'],
            'Registros': 'mean'
        }).round(2)
        ranking_contratistas.columns = ['Total_Rutas', 'Rutas_Cumplen', 'Registros_Promedio']
        ranking_contratistas = ranking_contratistas.reset_index()
        ranking_contratistas['Porcentaje_Cumplimiento'] = (ranking_contratistas['Rutas_Cumplen'] / ranking_contratistas['Total_Rutas'] * 100).round(1)
        ranking_contratistas = ranking_contratistas.sort_values('Porcentaje_Cumplimiento', ascending=False)
        
        # Gráfica de ranking de contratistas
        fig_ranking_con = px.bar(
            ranking_contratistas, 
            x='CONTRATISTA', 
            y='Porcentaje_Cumplimiento',
            color='Porcentaje_Cumplimiento',
            color_continuous_scale='RdYlGn',
            title='🏆 Ranking de Contratistas por % de Cumplimiento de Meta',
            text='Porcentaje_Cumplimiento'
        )
        fig_ranking_con.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_ranking_con.update_layout(
            xaxis_title="<b>Contratista</b>",
            yaxis_title="<b>% de Cumplimiento</b>",
            height=500
        )
        st.plotly_chart(fig_ranking_con, use_container_width=True)
    
    # --- SECCIÓN 2: Top Performers y Offenders ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🏅 Top Performers vs Top Offenders por Mes</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Top Offenders y Best por rutas
    rutas_mes = df_meta.groupby('ruta').agg({'id_tema':'count'}).reset_index()
    rutas_mes = rutas_mes.rename(columns={'id_tema':'Registros'})
    top_offenders = rutas_mes.nsmallest(10, 'Registros')
    top_performers = rutas_mes.nlargest(10, 'Registros')
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.markdown("##### ⚠️ Top 10 Offenders (Menos registros)")
        fig_offenders = px.bar(
            top_offenders, 
            x='Registros', 
            y='ruta', 
            orientation='h',
            color='Registros',
            color_continuous_scale='Reds',
            title='⚠️ Rutas con Menos Registros',
            text='Registros'
        )
        fig_offenders.update_traces(texttemplate='%{text}', textposition='outside')
        fig_offenders.update_layout(height=400)
        st.plotly_chart(fig_offenders, use_container_width=True)
    
    with col_top2:
        st.markdown("##### 🏆 Top 10 Performers (Más registros)")
        fig_performers = px.bar(
            top_performers, 
            x='Registros', 
            y='ruta', 
            orientation='h',
            color='Registros',
            color_continuous_scale='Greens',
            title='🏆 Rutas con Más Registros',
            text='Registros'
        )
        fig_performers.update_traces(texttemplate='%{text}', textposition='outside')
        fig_performers.update_layout(height=400)
        st.plotly_chart(fig_performers, use_container_width=True)
    
    # --- SECCIÓN 3: Análisis de Impacto ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🔥 Análisis de Impacto y Focos de Atención</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_impacto1, col_impacto2 = st.columns(2)
    
    # Impacto por supervisores
    if 'SUPERVISOR' in df_meta.columns:
        with col_impacto1:
            st.markdown("##### 👨‍💼 Supervisores con Rutas Sin Meta")
            supervisor_sin_meta = supervisor_rutas[~supervisor_rutas['Meta Cumplida']].groupby('SUPERVISOR').size().reset_index(name='Rutas_Sin_Meta')
            supervisor_sin_meta = supervisor_sin_meta.sort_values('Rutas_Sin_Meta', ascending=False)
            
            if not supervisor_sin_meta.empty:
                fig_impacto_sup = px.bar(
                    supervisor_sin_meta.head(10),
                    x='Rutas_Sin_Meta',
                    y='SUPERVISOR',
                    orientation='h',
                    color='Rutas_Sin_Meta',
                    color_continuous_scale='Reds',
                    title='🚨 Supervisores con Más Rutas Sin Meta',
                    text='Rutas_Sin_Meta'
                )
                fig_impacto_sup.update_traces(texttemplate='%{text}', textposition='outside')
                fig_impacto_sup.update_layout(height=400)
                st.plotly_chart(fig_impacto_sup, use_container_width=True)
            else:
                st.success("✅ Todos los supervisores tienen rutas que cumplen la meta!")
    
    # Impacto por contratistas
    if 'CONTRATISTA' in df_meta.columns:
        with col_impacto2:
            st.markdown("##### 🏢 Contratistas con Rutas Sin Meta")
            contratista_sin_meta = contratista_rutas[~contratista_rutas['Meta Cumplida']].groupby('CONTRATISTA').size().reset_index(name='Rutas_Sin_Meta')
            contratista_sin_meta = contratista_sin_meta.sort_values('Rutas_Sin_Meta', ascending=False)
            
            if not contratista_sin_meta.empty:
                fig_impacto_con = px.bar(
                    contratista_sin_meta.head(10),
                    x='Rutas_Sin_Meta',
                    y='CONTRATISTA',
                    orientation='h',
                    color='Rutas_Sin_Meta',
                    color_continuous_scale='Reds',
                    title='🚨 Contratistas con Más Rutas Sin Meta',
                    text='Rutas_Sin_Meta'
                )
                fig_impacto_con.update_traces(texttemplate='%{text}', textposition='outside')
                fig_impacto_con.update_layout(height=400)
                st.plotly_chart(fig_impacto_con, use_container_width=True)
            else:
                st.success("✅ Todos los contratistas tienen rutas que cumplen la meta!")
    
    # --- SECCIÓN 4: Recomendaciones y Acciones ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💡 Recomendaciones y Plan de Acción</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Generar recomendaciones automáticas
    recomendaciones = []
    
    if 'SUPERVISOR' in df_meta.columns and 'supervisor_sin_meta' in locals() and not supervisor_sin_meta.empty:
        peor_supervisor = supervisor_sin_meta.iloc[0]
        recomendaciones.append(f"🎯 **Supervisor {peor_supervisor['SUPERVISOR']}** requiere atención inmediata: {peor_supervisor['Rutas_Sin_Meta']} rutas sin meta.")
    
    if 'CONTRATISTA' in df_meta.columns and 'contratista_sin_meta' in locals() and not contratista_sin_meta.empty:
        peor_contratista = contratista_sin_meta.iloc[0]
        recomendaciones.append(f"🎯 **Contratista {peor_contratista['CONTRATISTA']}** requiere atención inmediata: {peor_contratista['Rutas_Sin_Meta']} rutas sin meta.")
    
    if not top_offenders.empty:
        peor_ruta = top_offenders.iloc[0]
        recomendaciones.append(f"🚨 **Ruta {peor_ruta['ruta']}** es la menos activa con solo {peor_ruta['Registros']} registros.")
    
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.success("🎉 **¡Excelente!** Todos los indicadores están dentro de los parámetros esperados.")
    
    # Botón para exportar datos
    st.markdown("---")
    st.markdown("### 📤 Exportar Análisis")
    if st.button("💾 Generar Reporte de Supervisores y Contratistas", key="export_supervisores"):
        # Crear datos para exportar
        export_data = {
            'Mes_Analizado': mes_meta,
            'Supervisor_Filtro': supervisor_meta,
            'Contratista_Filtro': contratista_meta,
            'Total_Rutas_Analizadas': total_rutas_sup if 'SUPERVISOR' in df_meta.columns else (total_rutas_con if 'CONTRATISTA' in df_meta.columns else 0)
        }
        
        st.json(export_data)
        st.success("📊 Datos exportados exitosamente para análisis adicional.")

def show_supervisors_contractors_analysis(df, merged_df):
    """Análisis integral dedicado a Supervisores y Contratistas"""
    st.subheader("👨‍💼 Análisis Integral por Supervisores y Contratistas")
    
    # Verificar que tenemos los datos necesarios
    if 'SUPERVISOR' not in merged_df.columns and 'CONTRATISTA' not in merged_df.columns:
        st.warning("⚠️ No hay datos de Supervisores o Contratistas disponibles en el dataset.")
        return
    
    # --- NUEVA SECCIÓN: Cumplimiento de Meta Mensual por Ruta, Supervisor y Contratista ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📅 Cumplimiento de Meta Mensual (10 registros/ruta)</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Filtros dinámicos mejorados
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        meses_disponibles = sorted(df['mes_nombre'].unique().tolist())
        mes_meta = st.selectbox("📅 Selecciona el mes:", meses_disponibles, key="meta_mes")
    
    with col_filtro2:
        if 'SUPERVISOR' in merged_df.columns:
            supervisores_disp = ['Todos'] + sorted(merged_df['SUPERVISOR'].dropna().unique().tolist())
            supervisor_meta = st.selectbox("👨‍💼 Filtrar por Supervisor:", supervisores_disp, key="meta_supervisor")
        else:
            supervisor_meta = 'Todos'
    
    with col_filtro3:
        if 'CONTRATISTA' in merged_df.columns:
            contratistas_disp = ['Todos'] + sorted(merged_df['CONTRATISTA'].dropna().unique().tolist())
            contratista_meta = st.selectbox("🏢 Filtrar por Contratista:", contratistas_disp, key="meta_contratista")
        else:
            contratista_meta = 'Todos'
    
    # Aplicar filtros
    df_meta = merged_df[merged_df['mes_nombre'] == mes_meta].copy()
    
    if supervisor_meta != 'Todos' and 'SUPERVISOR' in df_meta.columns:
        df_meta = df_meta[df_meta['SUPERVISOR'] == supervisor_meta]
    
    if contratista_meta != 'Todos' and 'CONTRATISTA' in df_meta.columns:
        df_meta = df_meta[df_meta['CONTRATISTA'] == contratista_meta]
    
    # --- Análisis por SUPERVISOR ---
    if 'SUPERVISOR' in df_meta.columns:
        st.markdown("### 👨‍💼 Análisis por Supervisores")
        
        # Calcular métricas por supervisor y ruta
        supervisor_rutas = df_meta.groupby(['SUPERVISOR', 'ruta']).agg({'id_tema':'count'}).reset_index()
        supervisor_rutas['Meta Cumplida'] = supervisor_rutas['id_tema'] >= 10
        supervisor_rutas['Estado'] = supervisor_rutas['Meta Cumplida'].map(lambda x: '✅ Cumple' if x else '❌ No Cumple')
        supervisor_rutas = supervisor_rutas.rename(columns={'id_tema':'Registros'})
        
        # Tabla detallada
        st.dataframe(
            clean_dataframe_for_display(supervisor_rutas[['SUPERVISOR', 'ruta', 'Registros', 'Estado']]), 
            use_container_width=True
        )
        
        # KPIs por supervisor
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        with col_kpi1:
            total_rutas_sup = supervisor_rutas.shape[0]
            rutas_cumplen_sup = supervisor_rutas['Meta Cumplida'].sum()
            porcentaje_cumple_sup = (rutas_cumplen_sup/total_rutas_sup*100) if total_rutas_sup > 0 else 0
            st.metric("📊 % Rutas que Cumplen Meta", f"{porcentaje_cumple_sup:.1f}%")
        
        with col_kpi2:
            st.metric("📈 Rutas que Cumplen", f"{rutas_cumplen_sup}/{total_rutas_sup}")
        
        with col_kpi3:
            rutas_no_cumplen_sup = total_rutas_sup - rutas_cumplen_sup
            st.metric("⚠️ Rutas que NO Cumplen", f"{rutas_no_cumplen_sup}")
        
        # Ranking de supervisores
        ranking_supervisores = supervisor_rutas.groupby('SUPERVISOR').agg({
            'Meta Cumplida': ['count', 'sum'],
            'Registros': 'mean'
        }).round(2)
        ranking_supervisores.columns = ['Total_Rutas', 'Rutas_Cumplen', 'Registros_Promedio']
        ranking_supervisores = ranking_supervisores.reset_index()
        ranking_supervisores['Porcentaje_Cumplimiento'] = (ranking_supervisores['Rutas_Cumplen'] / ranking_supervisores['Total_Rutas'] * 100).round(1)
        ranking_supervisores = ranking_supervisores.sort_values('Porcentaje_Cumplimiento', ascending=False)
        
        # Gráfica de ranking de supervisores
        fig_ranking_sup = px.bar(
            ranking_supervisores, 
            x='SUPERVISOR', 
            y='Porcentaje_Cumplimiento',
            color='Porcentaje_Cumplimiento',
            color_continuous_scale='RdYlGn',
            title='🏆 Ranking de Supervisores por % de Cumplimiento de Meta',
            text='Porcentaje_Cumplimiento'
        )
        fig_ranking_sup.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_ranking_sup.update_layout(
            xaxis_title="<b>Supervisor</b>",
            yaxis_title="<b>% de Cumplimiento</b>",
            height=500
        )
        st.plotly_chart(fig_ranking_sup, use_container_width=True)
    
    # --- Análisis por CONTRATISTA ---
    if 'CONTRATISTA' in df_meta.columns:
        st.markdown("### 🏢 Análisis por Contratistas")
        
        # Calcular métricas por contratista y ruta
        contratista_rutas = df_meta.groupby(['CONTRATISTA', 'ruta']).agg({'id_tema':'count'}).reset_index()
        contratista_rutas['Meta Cumplida'] = contratista_rutas['id_tema'] >= 10
        contratista_rutas['Estado'] = contratista_rutas['Meta Cumplida'].map(lambda x: '✅ Cumple' if x else '❌ No Cumple')
        contratista_rutas = contratista_rutas.rename(columns={'id_tema':'Registros'})
        
        # Tabla detallada
        st.dataframe(
            clean_dataframe_for_display(contratista_rutas[['CONTRATISTA', 'ruta', 'Registros', 'Estado']]), 
            use_container_width=True
        )
        
        # KPIs por contratista
        col_kpi4, col_kpi5, col_kpi6 = st.columns(3)
        
        with col_kpi4:
            total_rutas_con = contratista_rutas.shape[0]
            rutas_cumplen_con = contratista_rutas['Meta Cumplida'].sum()
            porcentaje_cumple_con = (rutas_cumplen_con/total_rutas_con*100) if total_rutas_con > 0 else 0
            st.metric("📊 % Rutas que Cumplen Meta", f"{porcentaje_cumple_con:.1f}%")
        
        with col_kpi5:
            st.metric("📈 Rutas que Cumplen", f"{rutas_cumplen_con}/{total_rutas_con}")
        
        with col_kpi6:
            rutas_no_cumplen_con = total_rutas_con - rutas_cumplen_con
            st.metric("⚠️ Rutas que NO Cumplen", f"{rutas_no_cumplen_con}")
        
        # Ranking de contratistas
        ranking_contratistas = contratista_rutas.groupby('CONTRATISTA').agg({
            'Meta Cumplida': ['count', 'sum'],
            'Registros': 'mean'
        }).round(2)
        ranking_contratistas.columns = ['Total_Rutas', 'Rutas_Cumplen', 'Registros_Promedio']
        ranking_contratistas = ranking_contratistas.reset_index()
        ranking_contratistas['Porcentaje_Cumplimiento'] = (ranking_contratistas['Rutas_Cumplen'] / ranking_contratistas['Total_Rutas'] * 100).round(1)
        ranking_contratistas = ranking_contratistas.sort_values('Porcentaje_Cumplimiento', ascending=False)
        
        # Gráfica de ranking de contratistas
        fig_ranking_con = px.bar(
            ranking_contratistas, 
            x='CONTRATISTA', 
            y='Porcentaje_Cumplimiento',
            color='Porcentaje_Cumplimiento',
            color_continuous_scale='RdYlGn',
            title='🏆 Ranking de Contratistas por % de Cumplimiento de Meta',
            text='Porcentaje_Cumplimiento'
        )
        fig_ranking_con.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_ranking_con.update_layout(
            xaxis_title="<b>Contratista</b>",
            yaxis_title="<b>% de Cumplimiento</b>",
            height=500
        )
        st.plotly_chart(fig_ranking_con, use_container_width=True)
    
    # --- SECCIÓN 2: Top Performers y Offenders ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🏅 Top Performers vs Top Offenders por Mes</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Top Offenders y Best por rutas
    rutas_mes = df_meta.groupby('ruta').agg({'id_tema':'count'}).reset_index()
    rutas_mes = rutas_mes.rename(columns={'id_tema':'Registros'})
    top_offenders = rutas_mes.nsmallest(10, 'Registros')
    top_performers = rutas_mes.nlargest(10, 'Registros')
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.markdown("##### ⚠️ Top 10 Offenders (Menos registros)")
        fig_offenders = px.bar(
            top_offenders, 
            x='Registros', 
            y='ruta', 
            orientation='h',
            color='Registros',
            color_continuous_scale='Reds',
            title='⚠️ Rutas con Menos Registros',
            text='Registros'
        )
        fig_offenders.update_traces(texttemplate='%{text}', textposition='outside')
        fig_offenders.update_layout(height=400)
        st.plotly_chart(fig_offenders, use_container_width=True)
    
    with col_top2:
        st.markdown("##### 🏆 Top 10 Performers (Más registros)")
        fig_performers = px.bar(
            top_performers, 
            x='Registros', 
            y='ruta', 
            orientation='h',
            color='Registros',
            color_continuous_scale='Greens',
            title='🏆 Rutas con Más Registros',
            text='Registros'
        )
        fig_performers.update_traces(texttemplate='%{text}', textposition='outside')
        fig_performers.update_layout(height=400)
        st.plotly_chart(fig_performers, use_container_width=True)
    
    # --- SECCIÓN 3: Análisis de Impacto ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🔥 Análisis de Impacto y Focos de Atención</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_impacto1, col_impacto2 = st.columns(2)
    
    # Impacto por supervisores
    if 'SUPERVISOR' in df_meta.columns and 'supervisor_rutas' in locals():
        with col_impacto1:
            st.markdown("##### 👨‍💼 Supervisores con Rutas Sin Meta")
            supervisor_sin_meta = supervisor_rutas[~supervisor_rutas['Meta Cumplida']].groupby('SUPERVISOR').size().reset_index(name='Rutas_Sin_Meta')
            supervisor_sin_meta = supervisor_sin_meta.sort_values('Rutas_Sin_Meta', ascending=False)
            
            if not supervisor_sin_meta.empty:
                st.dataframe(clean_dataframe_for_display(supervisor_sin_meta), use_container_width=True)
            else:
                st.success("🎉 Todos los supervisores tienen rutas que cumplen la meta!")
    
    # Impacto por contratistas
    if 'CONTRATISTA' in df_meta.columns and 'contratista_rutas' in locals():
        with col_impacto2:
            st.markdown("##### 🏢 Contratistas con Rutas Sin Meta")
            contratista_sin_meta = contratista_rutas[~contratista_rutas['Meta Cumplida']].groupby('CONTRATISTA').size().reset_index(name='Rutas_Sin_Meta')
            contratista_sin_meta = contratista_sin_meta.sort_values('Rutas_Sin_Meta', ascending=False)
            
            if not contratista_sin_meta.empty:
                st.dataframe(clean_dataframe_for_display(contratista_sin_meta), use_container_width=True)
            else:
                st.success("🎉 Todos los contratistas tienen rutas que cumplen la meta!")
    
    # --- SECCIÓN 4: Recomendaciones y Acciones ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💡 Recomendaciones y Plan de Acción</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Generar recomendaciones automáticas
    recomendaciones = []
    
    if 'SUPERVISOR' in df_meta.columns and 'supervisor_sin_meta' in locals() and not supervisor_sin_meta.empty:
        peor_supervisor = supervisor_sin_meta.iloc[0]
        recomendaciones.append(f"🎯 **Supervisor {peor_supervisor['SUPERVISOR']}** requiere atención inmediata: {peor_supervisor['Rutas_Sin_Meta']} rutas sin meta.")
    
    if 'CONTRATISTA' in df_meta.columns and 'contratista_sin_meta' in locals() and not contratista_sin_meta.empty:
        peor_contratista = contratista_sin_meta.iloc[0]
        recomendaciones.append(f"🎯 **Contratista {peor_contratista['CONTRATISTA']}** requiere atención inmediata: {peor_contratista['Rutas_Sin_Meta']} rutas sin meta.")
    
    if not top_offenders.empty:
        peor_ruta = top_offenders.iloc[0]
        recomendaciones.append(f"🚨 **Ruta {peor_ruta['ruta']}** es la menos activa con solo {peor_ruta['Registros']} registros.")
    
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.success("🎉 **¡Excelente!** Todos los indicadores están dentro de los parámetros esperados.")
    
    # Botón para exportar datos
    st.markdown("---")
    st.markdown("### 📤 Exportar Análisis")
    if st.button("💾 Generar Reporte de Supervisores y Contratistas", key="export_supervisores"):
        # Crear datos para exportar
        export_data = {
            'Mes_Analizado': mes_meta,
            'Supervisor_Filtro': supervisor_meta,
            'Contratista_Filtro': contratista_meta,
            'Total_Rutas_Analizadas': total_rutas_sup if 'SUPERVISOR' in df_meta.columns else (total_rutas_con if 'CONTRATISTA' in df_meta.columns else 0)
        }
        
        st.json(export_data)
        st.success("📊 Datos exportados exitosamente para análisis adicional.")

def show_personnel_analysis(df, merged_df):
    """Análisis completo del personal con múltiples métricas"""
    st.subheader("👥 Análisis Detallado del Personal y Rendimiento")
    
    # Primera fila - Análisis de usuarios más activos
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">👤 Rendimiento Completo de Usuarios</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    user_performance = df.groupby('usuario').agg({
        'id_tema': 'count',
        'puntos': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'ruta': 'nunique'
    }).round(2)
    user_performance.columns = ['Total_Registros', 'Puntos_Promedio', 'Desviacion_Puntos', 'Registros_Cerrados', 'Rutas_Trabajadas']
    user_performance = user_performance.reset_index()
    user_performance['Tasa_Cierre'] = (user_performance['Registros_Cerrados'] / user_performance['Total_Registros']) * 100
    user_performance = user_performance.sort_values('Total_Registros', ascending=False)
    
    # Gráfico de rendimiento de usuarios
    fig_user_performance = px.bar(
        user_performance.head(15),
        x='Total_Registros',
        y='usuario',
        orientation='h',
        title="👤 Top 15 Usuarios por Volumen de Registros",
        color='Puntos_Promedio',
        color_continuous_scale='Blues',
        height=800,
        text='Total_Registros'
    )
    fig_user_performance.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_user_performance.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=150, r=50, t=50, b=50)
    )
    st.plotly_chart(fig_user_performance, use_container_width=True)

def show_performance_analysis(df):
    """Análisis de rendimiento completo con múltiples gráficas"""
    st.subheader("🎯 Análisis Detallado de Rendimiento y Calidad")
    
    # Primera fila - Top clientes más reportados
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🏪 Top 20 Clientes Más Reportados</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Convertir codigo_cliente a string para evitar problemas de formato
    df['codigo_cliente_str'] = df['codigo_cliente'].astype(str)
    clientes_reportados = df.groupby('codigo_cliente_str').agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'fecha_cierre': lambda x: x.notna().sum(),
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A'
    }).round(2).reset_index()
    clientes_reportados.columns = ['codigo_cliente', 'total_reportes', 'puntos_promedio', 'reportes_cerrados', 'motivo_principal']
    clientes_reportados['tasa_cierre'] = (clientes_reportados['reportes_cerrados'] / clientes_reportados['total_reportes']) * 100    
    clientes_reportados = clientes_reportados.sort_values('total_reportes', ascending=False).head(20)
    
    fig_clientes = px.bar(
        clientes_reportados,
        x='total_reportes',
        y='codigo_cliente',
        orientation='h',
        title="🏪 Top 20 Clientes Más Reportados",
        color='motivo_principal',
        height=800,
        text='total_reportes'
    )    
    fig_clientes.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_clientes.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=200, r=50, t=50, b=50)
    )
    st.plotly_chart(fig_clientes, use_container_width=True)

def show_advanced_analysis(df, merged_df):
    """Análisis avanzado con gráficas especializadas"""
    st.subheader("📊 Análisis Avanzado y Insights Profundos")
    
    # Primera fila - Análisis de clientes problemáticos
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Top 20 Clientes con Más Reportes</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Convertir codigo_cliente a string para evitar problemas de formato
    df['codigo_cliente_str'] = df['codigo_cliente'].astype(str)
    
    # Análisis de clientes usando respuesta_sub como motivo real
    clientes_analysis = df.groupby('codigo_cliente_str').agg({
        'id_tema': 'count',
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
        'puntos': 'mean',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2).reset_index()
    clientes_analysis.columns = ['codigo_cliente', 'total_reportes', 'motivo_principal', 'puntos_promedio', 'casos_cerrados']
    clientes_analysis['tasa_cierre'] = (clientes_analysis['casos_cerrados'] / clientes_analysis['total_reportes']) * 100
    clientes_analysis = clientes_analysis.sort_values('total_reportes', ascending=False).head(20)
    
    fig_clientes_problematicos = px.bar(
        clientes_analysis,
        x='total_reportes',
        y='codigo_cliente',
        orientation='h',
        title="🎯 Top 20 Clientes con Más Reportes",
        color='motivo_principal',
        height=800,
        text='total_reportes'
    )
    fig_clientes_problematicos.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker_line_width=0
    )
    fig_clientes_problematicos.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=150, r=50, t=80, b=50)
    )
    st.plotly_chart(fig_clientes_problematicos, use_container_width=True)

def show_detailed_data(df, merged_df):
    """Muestra los datos detallados con filtros avanzados"""
    st.subheader("📋 Datos Detallados con Filtros Avanzados")
    
    # Verificar si hay datos disponibles
    if df.empty:
        st.warning("⚠️ No hay datos disponibles para mostrar con los filtros actuales.")
        return
    
    # Filtros básicos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        motivos_unicos = ['Todos'] + sorted([str(m) for m in df['motivo_retro'].dropna().unique().tolist()])
        motivo_filtro = st.selectbox("🎯 Filtrar por Motivo", motivos_unicos, key="detailed_motivo_filtro")
    
    with col2:
        min_puntos = int(df['puntos'].min()) if not df.empty else 0
        max_puntos = int(df['puntos'].max()) if not df.empty else 5
        puntos_filtro = st.slider("⭐ Rango de Puntos", min_puntos, max_puntos, (min_puntos, max_puntos), key="detailed_puntos_filtro")
    
    with col3:
        solo_cerrados = st.checkbox("📋 Solo mostrar registros cerrados", key="detailed_solo_cerrados")
    
    # Aplicar filtros
    df_tabla = df.copy()
    
    if motivo_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['motivo_retro'] == motivo_filtro]
    
    df_tabla = df_tabla[
        (df_tabla['puntos'] >= puntos_filtro[0]) & 
        (df_tabla['puntos'] <= puntos_filtro[1])
    ]
    
    if solo_cerrados:
        df_tabla = df_tabla[df_tabla['fecha_cierre'].notna()]
    
    # Mostrar estadísticas
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("📊 Total de Registros", len(df_tabla))
    
    with col_stats2:
        st.metric("⭐ Puntos Promedio", f"{df_tabla['puntos'].mean():.2f}" if not df_tabla.empty else "0.00")
    
    with col_stats3:
        tasa_cierre = (df_tabla['fecha_cierre'].notna().sum() / len(df_tabla) * 100) if not df_tabla.empty else 0
        st.metric("📋 Tasa de Cierre", f"{tasa_cierre:.1f}%")
    
    # Mostrar tabla
    if not df_tabla.empty:
        st.dataframe(clean_dataframe_for_display(df_tabla), use_container_width=True)
    else:
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")

if __name__ == "__main__":
    main()
