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
import base64
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Dashboard Feedbacks H1 - Análisis Profesional Completo",
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

### Top 10 Motivos de Retroalimentación:
{df['motivo_retro'].value_counts().head(10).to_string()}

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
- Motivo principal: {df['motivo_retro'].value_counts().index[0]} ({df['motivo_retro'].value_counts().iloc[0]} casos)
"""

# Función principal mejorada
def main():
    # Título principal
    st.markdown('<h1 class="main-header">🎯 Dashboard Feedbacks H1 - Análisis Profesional Completo</h1>', unsafe_allow_html=True)
    
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
    
    if trimestre_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['trimestre_nombre'] == trimestre_seleccionado]
    
    # Filtrar merged_df también
    merged_df_filtrado = merged_df[
        (merged_df['fecha_registro'].dt.date >= fecha_inicio) &
        (merged_df['fecha_registro'].dt.date <= fecha_fin)
    ]
    
    if supervisor_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['SUPERVISOR'] == supervisor_seleccionado]
    
    if contratista_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['CONTRATISTA'] == contratista_seleccionado]
    
    # Sección de reportes en sidebar
    st.sidebar.markdown("### 📄 Generación de Reportes")
    
    tipo_reporte = st.sidebar.selectbox(
        "📋 Tipo de Reporte",
        ["Completo", "Ejecutivo", "Por Supervisor", "Por Contratista"]
    )
    
    if st.sidebar.button("📥 Generar Reporte"):
        if tipo_reporte == "Completo":
            reporte = generate_report(df_filtrado, merged_df_filtrado, "completo")
        else:
            reporte = generate_report(df_filtrado, merged_df_filtrado, "ejecutivo")
        
        st.sidebar.download_button(
            label="💾 Descargar Reporte",
            data=reporte,
            file_name=f"reporte_feedbacks_{tipo_reporte.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        st.sidebar.success("✅ Reporte generado exitosamente!")
    
    # Métricas KPI mejoradas
    create_advanced_kpi_metrics(df_filtrado, merged_df_filtrado)
    
    # Menú de navegación principal
    selected = option_menu(
        menu_title=None,
        options=[
            "🏠 Resumen General", 
            "📈 Análisis Temporal", 
            "🚚 Análisis por Rutas", 
            "👥 Análisis de Personal", 
            "🎯 Análisis de Rendimiento", 
            "📊 Análisis Avanzado",
            "📋 Datos Detallados"
        ],
        icons=["house", "graph-up", "truck", "people", "target", "bar-chart", "table"],
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
    elif selected == "👥 Análisis de Personal":
        show_personnel_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "🎯 Análisis de Rendimiento":
        show_performance_analysis(df_filtrado)
    elif selected == "📊 Análisis Avanzado":
        show_advanced_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "📋 Datos Detallados":
        show_detailed_data(df_filtrado, merged_df_filtrado)

def show_general_overview(df, merged_df):
    """Muestra el resumen general mejorado"""
    st.subheader("📊 Resumen General del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 15 motivos más reportados
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">🎯 Análisis de Motivos Más Reportados</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        motivos_data = df['motivo_retro'].value_counts().head(15).reset_index()
        motivos_data.columns = ['motivo', 'cantidad']
        
        fig_motivos = px.bar(
            motivos_data,
            x='cantidad',
            y='motivo',
            orientation='h',
            title="🎯 Top 15 Motivos de Retroalimentación",
            color='cantidad',
            color_continuous_scale='viridis',
            height=600
        )
        fig_motivos.update_layout(
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_motivos, use_container_width=True)
    
    with col2:
        # Rutas que han ingresado más motivos
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">🚚 Rutas con Más Registros</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        rutas_motivos = df.groupby('ruta').agg({
            'motivo_retro': 'count',
            'puntos': 'mean'
        }).round(2).reset_index()
        rutas_motivos.columns = ['ruta', 'total_motivos', 'puntos_promedio']
        rutas_motivos = rutas_motivos.sort_values('total_motivos', ascending=False).head(15)
        
        fig_rutas = px.scatter(
            rutas_motivos,
            x='total_motivos',
            y='puntos_promedio',
            size='total_motivos',
            hover_data=['ruta'],
            title="🚚 Rutas: Cantidad vs Calidad",
            color='puntos_promedio',
            color_continuous_scale='RdYlBu',
            height=600
        )
        st.plotly_chart(fig_rutas, use_container_width=True)
    
    # Análisis de supervisores con más cierres (si disponible)
    if 'SUPERVISOR' in merged_df.columns:
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">👨‍💼 Análisis de Supervisores con Más Cierres</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
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
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_supervisor_cierres, use_container_width=True)

def show_temporal_analysis(df):
    """Muestra análisis temporal mejorado"""
    st.subheader("📅 Análisis Temporal Profundo y Detallado")
    
    # Filtro por trimestre mejorado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Análisis por Trimestres")
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
            title="📊 Registros por Trimestre",
            color='Puntos_Promedio',
            color_continuous_scale='viridis',
            text='Total_Registros'
        )
        fig_trimestre.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_trimestre, use_container_width=True)
        
        # Mostrar tabla de detalles trimestrales
        st.dataframe(trimestre_data, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Análisis Detallado por Días")
        
        # Análisis por día de la semana con más detalles
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
            title="📈 Registros por Día de la Semana",
            color='puntos_promedio',
            color_continuous_scale='plasma',
            text='total_registros'
        )
        fig_dias.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_dias, use_container_width=True)
    
    # Análisis mensual detallado
    st.markdown("### 📆 Análisis Mensual Completo")
    
    monthly_detailed = df.groupby(['mes', 'mes_nombre']).agg({
        'id_tema': 'count',
        'puntos': ['mean', 'sum'],
        'usuario': 'nunique',
        'ruta': 'nunique',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2)
    
    monthly_detailed.columns = ['Total_Registros', 'Puntos_Promedio', 'Puntos_Totales', 'Usuarios_Unicos', 'Rutas_Activas', 'Total_Cierres']
    monthly_detailed = monthly_detailed.reset_index()
    
    # Gráfico de múltiples métricas mensuales
    fig_monthly = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Registros Mensuales', 'Puntos Promedio', 'Usuarios Únicos', 'Rutas Activas'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Registros mensuales
    fig_monthly.add_trace(
        go.Bar(x=monthly_detailed['mes_nombre'], y=monthly_detailed['Total_Registros'], name='Registros'),
        row=1, col=1
    )
    
    # Puntos promedio
    fig_monthly.add_trace(
        go.Scatter(x=monthly_detailed['mes_nombre'], y=monthly_detailed['Puntos_Promedio'], 
                  mode='lines+markers', name='Puntos Promedio'),
        row=1, col=2
    )
    
    # Usuarios únicos
    fig_monthly.add_trace(
        go.Bar(x=monthly_detailed['mes_nombre'], y=monthly_detailed['Usuarios_Unicos'], name='Usuarios'),
        row=2, col=1
    )
    
    # Rutas activas
    fig_monthly.add_trace(
        go.Bar(x=monthly_detailed['mes_nombre'], y=monthly_detailed['Rutas_Activas'], name='Rutas'),
        row=2, col=2
    )
    
    fig_monthly.update_layout(height=600, title_text="📊 Análisis Mensual Multidimensional")
    st.plotly_chart(fig_monthly, use_container_width=True)

def show_routes_analysis(df, merged_df):
    """Análisis completo por rutas con supervisores y contratistas"""
    st.subheader("🚚 Análisis Completo por Rutas, Supervisores y Contratistas")
    
    # Top 3 rutas por contratista y Top 5 por supervisor
    if 'CONTRATISTA' in merged_df.columns and 'SUPERVISOR' in merged_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
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
            
            # Top 3 rutas por cada contratista
            top_rutas_contratista = contratista_rutas.groupby('contratista').apply(
                lambda x: x.nlargest(3, 'registros')
            ).reset_index(drop=True)
            
            fig_contratista_rutas = px.bar(
                top_rutas_contratista,
                x='registros',
                y='ruta',
                color='contratista',
                title="🏢 Top 3 Rutas por Contratista",
                orientation='h',
                height=500
            )
            st.plotly_chart(fig_contratista_rutas, use_container_width=True)
        
        with col2:
            st.markdown(
                """
                <div class="top-performance">
                    <h3 style="color: white; margin: 0;">🏆 Top 5 Rutas por Supervisor</h3>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Análisis por supervisor
            supervisor_rutas = merged_df.groupby(['SUPERVISOR', 'ruta']).size().reset_index()
            supervisor_rutas.columns = ['supervisor', 'ruta', 'registros']
            
            # Top 5 rutas por cada supervisor
            top_rutas_supervisor = supervisor_rutas.groupby('supervisor').apply(
                lambda x: x.nlargest(5, 'registros')
            ).reset_index(drop=True)
            
            fig_supervisor_rutas = px.bar(
                top_rutas_supervisor,
                x='registros',
                y='ruta',
                color='supervisor',
                title="👨‍💼 Top 5 Rutas por Supervisor",
                orientation='h',
                height=500
            )
            st.plotly_chart(fig_supervisor_rutas, use_container_width=True)
    
    # Top 5 rutas con más registros generales
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🚚 Análisis Detallado de Rutas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Top 15 rutas con más registros
        top_rutas_general = df['ruta'].value_counts().head(15).reset_index()
        top_rutas_general.columns = ['ruta', 'total_registros']
        
        fig_top_rutas = px.bar(
            top_rutas_general,
            x='total_registros',
            y='ruta',
            orientation='h',
            title="🏆 Top 15 Rutas con Más Registros",
            color='total_registros',
            color_continuous_scale='viridis',
            height=600
        )
        fig_top_rutas.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top_rutas, use_container_width=True)
    
    with col4:
        # Análisis de eficiencia por ruta (registros vs puntos promedio)
        ruta_eficiencia = df.groupby('ruta').agg({
            'id_tema': 'count',
            'puntos': 'mean',
            'fecha_cierre': lambda x: x.notna().sum()
        }).round(2).reset_index()
        ruta_eficiencia.columns = ['ruta', 'total_registros', 'puntos_promedio', 'total_cierres']
        ruta_eficiencia['tasa_cierre'] = (ruta_eficiencia['total_cierres'] / ruta_eficiencia['total_registros']) * 100
        
        # Filtrar rutas con al menos 10 registros para análisis más significativo
        ruta_eficiencia_filtrada = ruta_eficiencia[ruta_eficiencia['total_registros'] >= 10]
        
        fig_eficiencia = px.scatter(
            ruta_eficiencia_filtrada,
            x='total_registros',
            y='puntos_promedio',
            size='tasa_cierre',
            hover_data=['ruta', 'tasa_cierre'],
            title="📊 Eficiencia de Rutas: Volumen vs Calidad",
            color='tasa_cierre',
            color_continuous_scale='RdYlGn',
            height=600
        )
        st.plotly_chart(fig_eficiencia, use_container_width=True)

def show_personnel_analysis(df, merged_df):
    """Análisis completo del personal"""
    st.subheader("👥 Análisis Detallado del Personal y Rendimiento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análisis de usuarios más activos con métricas adicionales
        user_performance = df.groupby('usuario').agg({
            'id_tema': 'count',
            'puntos': ['mean', 'sum'],
            'ruta': 'nunique',
            'codigo_cliente': 'nunique',
            'fecha_cierre': lambda x: x.notna().sum()
        }).round(2)
        
        user_performance.columns = ['Total_Registros', 'Puntos_Promedio', 'Puntos_Totales', 'Rutas_Trabajadas', 'Clientes_Atendidos', 'Cierres_Realizados']
        user_performance = user_performance.reset_index()
        user_performance['Tasa_Cierre'] = (user_performance['Cierres_Realizados'] / user_performance['Total_Registros']) * 100
        user_performance = user_performance.sort_values('Total_Registros', ascending=False).head(15)
        
        fig_user_perf = px.scatter(
            user_performance,
            x='Total_Registros',
            y='Puntos_Promedio',
            size='Clientes_Atendidos',
            color='Tasa_Cierre',
            hover_data=['usuario', 'Rutas_Trabajadas'],
            title="👤 Rendimiento de Usuarios: Productividad vs Calidad",
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_user_perf, use_container_width=True)
    
    with col2:
        # Análisis de vendedores con métricas de ventas
        vendedor_performance = df.groupby('vendedor').agg({
            'id_tema': 'count',
            'puntos': ['mean', 'sum'],
            'codigo_cliente': 'nunique',
            'ruta': 'nunique'
        }).round(2)
        
        vendedor_performance.columns = ['Total_Registros', 'Puntos_Promedio', 'Puntos_Totales', 'Clientes_Unicos', 'Rutas_Cubiertas']
        vendedor_performance = vendedor_performance.reset_index()
        vendedor_performance = vendedor_performance.sort_values('Total_Registros', ascending=False).head(15)
        
        fig_vendedor_perf = px.bar(
            vendedor_performance,
            x='Total_Registros',
            y='vendedor',
            orientation='h',
            title="💼 Top 15 Vendedores por Volumen",
            color='Puntos_Promedio',
            color_continuous_scale='plasma'
        )
        fig_vendedor_perf.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_vendedor_perf, use_container_width=True)

def show_performance_analysis(df):
    """Análisis de rendimiento completo"""
    st.subheader("🎯 Análisis de Rendimiento y Métricas Avanzadas")
    
    # Análisis de clientes más reportados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏪 Clientes Más Reportados")
        
        clientes_reportados = df.groupby(['codigo_cliente', 'nombre_cliente']).agg({
            'id_tema': 'count',
            'motivo_retro': lambda x: x.mode().iloc[0] if not x.empty else 'N/A',
            'puntos': 'mean'
        }).round(2).reset_index()
        clientes_reportados.columns = ['codigo_cliente', 'nombre_cliente', 'total_reportes', 'motivo_principal', 'puntos_promedio']
        clientes_reportados = clientes_reportados.sort_values('total_reportes', ascending=False).head(15)
        
        fig_clientes = px.bar(
            clientes_reportados,
            x='total_reportes',
            y='nombre_cliente',
            orientation='h',
            title="🏪 Top 15 Clientes Más Reportados",
            color='puntos_promedio',
            color_continuous_scale='RdYlBu',
            height=600
        )
        fig_clientes.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_clientes, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Análisis de Motivos por Cliente")
        
        # Análisis de motivos más comunes por cliente
        cliente_motivos = df.groupby(['codigo_cliente', 'motivo_retro']).size().reset_index()
        cliente_motivos.columns = ['codigo_cliente', 'motivo', 'cantidad']
        
        # Top clientes y sus motivos principales
        top_clientes = df['codigo_cliente'].value_counts().head(10).index
        cliente_motivos_top = cliente_motivos[cliente_motivos['codigo_cliente'].isin(top_clientes)]
        
        fig_motivos_cliente = px.sunburst(
            cliente_motivos_top,
            path=['codigo_cliente', 'motivo'],
            values='cantidad',
            title="🌅 Distribución de Motivos por Cliente",
            height=600
        )
        st.plotly_chart(fig_motivos_cliente, use_container_width=True)

def show_advanced_analysis(df, merged_df):
    """Análisis avanzado con gráficas especializadas"""
    st.subheader("📊 Análisis Avanzado y Insights Profundos")
    
    # Ruta con más registros de cada motivo
    st.markdown("### 🎯 Rutas Líderes por Tipo de Motivo")
    
    motivo_ruta_analysis = df.groupby(['motivo_retro', 'ruta']).size().reset_index()
    motivo_ruta_analysis.columns = ['motivo', 'ruta', 'cantidad']
    
    # Obtener la ruta líder para cada motivo
    rutas_lideres_por_motivo = motivo_ruta_analysis.loc[
        motivo_ruta_analysis.groupby('motivo')['cantidad'].idxmax()
    ]
    
    fig_rutas_motivo = px.bar(
        rutas_lideres_por_motivo.head(15),
        x='cantidad',
        y='motivo',
        color='ruta',
        orientation='h',
        title="🚚 Ruta Líder por Cada Tipo de Motivo",
        height=600
    )
    fig_rutas_motivo.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_rutas_motivo, use_container_width=True)
    
    # Análisis de tipos de respuesta
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Análisis de Tipos de Respuesta")
        
        respuesta_analysis = df.groupby('respuesta_sub').agg({
            'id_tema': 'count',
            'puntos': 'mean'
        }).round(2).reset_index()
        respuesta_analysis.columns = ['tipo_respuesta', 'total_casos', 'puntos_promedio']
        respuesta_analysis = respuesta_analysis.sort_values('total_casos', ascending=False).head(10)
        
        fig_respuestas = px.scatter(
            respuesta_analysis,
            x='total_casos',
            y='puntos_promedio',
            size='total_casos',
            hover_data=['tipo_respuesta'],
            title="💬 Tipos de Respuesta: Frecuencia vs Calidad",
            color='puntos_promedio',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_respuestas, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Distribución de Centros")
        
        centro_analysis = df.groupby('centro').agg({
            'id_tema': 'count',
            'puntos': 'mean',
            'usuario': 'nunique'
        }).round(2).reset_index()
        centro_analysis.columns = ['centro', 'total_registros', 'puntos_promedio', 'usuarios_unicos']
        
        fig_centros = px.treemap(
            centro_analysis,
            path=['centro'],
            values='total_registros',
            color='puntos_promedio',
            title="🏢 Distribución de Registros por Centro",
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_centros, use_container_width=True)

def show_detailed_data(df, merged_df):
    """Muestra los datos detallados con filtros avanzados mejorados"""
    st.subheader("📋 Datos Detallados con Filtros Avanzados Completos")
    
    # Verificar si hay datos disponibles
    if df.empty:
        st.warning("⚠️ No hay datos disponibles para mostrar con los filtros actuales.")
        return
    
    # Filtros avanzados mejorados
    st.markdown("### 🔍 Centro de Filtros Avanzados")
    
    # Primera fila de filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        motivos_unicos = ['Todos'] + sorted([str(m) for m in df['motivo_retro'].dropna().unique().tolist()])
        motivo_filtro = st.selectbox("🎯 Filtrar por Motivo", motivos_unicos)
    
    with col2:
        min_puntos = int(df['puntos'].min()) if not df.empty else 0
        max_puntos = int(df['puntos'].max()) if not df.empty else 5
        
        if min_puntos == max_puntos:
            max_puntos = min_puntos + 1
        
        puntos_filtro = st.slider("⭐ Rango de Puntos", min_puntos, max_puntos, (min_puntos, max_puntos))
    
    with col3:
        vendedores_unicos = ['Todos'] + sorted([str(v) for v in df['vendedor'].dropna().unique().tolist()])
        vendedor_filtro = st.selectbox("💼 Filtrar por Vendedor", vendedores_unicos)
    
    with col4:
        solo_cerrados = st.checkbox("📋 Solo mostrar registros cerrados")
    
    # Segunda fila de filtros - NUEVOS FILTROS
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        if 'SUPERVISOR' in merged_df.columns:
            supervisores_disponibles = merged_df['SUPERVISOR'].dropna().unique()
            supervisores_unicos = ['Todos'] + sorted([str(s) for s in supervisores_disponibles])
            supervisor_filtro = st.selectbox("👨‍💼 Filtrar por Supervisor", supervisores_unicos)
        else:
            supervisor_filtro = 'Todos'
    
    with col6:
        if 'CONTRATISTA' in merged_df.columns:
            contratistas_disponibles = merged_df['CONTRATISTA'].dropna().unique()
            contratistas_unicos = ['Todos'] + sorted([str(c) for c in contratistas_disponibles])
            contratista_filtro = st.selectbox("🏢 Filtrar por Contratista", contratistas_unicos)
        else:
            contratista_filtro = 'Todos'
    
    with col7:
        respuestas_unicos = ['Todos'] + sorted([str(r) for r in df['respuesta_sub'].dropna().unique().tolist()])
        respuesta_filtro = st.selectbox("💬 Filtrar por Tipo Respuesta", respuestas_unicos)
    
    with col8:
        trimestres = ['Todos'] + sorted([str(t) for t in df['trimestre_nombre'].dropna().unique().tolist()])
        trimestre_filtro = st.selectbox("📅 Filtrar por Trimestre", trimestres)
    
    # Tercera fila de filtros
    col9, col10, col11, col12 = st.columns(4)
    
    with col9:
        meses_disponibles = ['Todos'] + sorted([str(m) for m in df['mes_nombre'].dropna().unique().tolist()])
        mes_filtro = st.selectbox("📆 Filtrar por Mes", meses_disponibles)
    
    with col10:
        # Top 20 clientes más reportados para filtro rápido
        clientes_top = df['codigo_cliente'].value_counts().head(20).index.tolist()
        opciones_cliente = ['Todos', 'Top 20 más reportados'] + sorted([str(c) for c in df['codigo_cliente'].dropna().unique().tolist()])
        cliente_filtro = st.selectbox("🏪 Filtrar por Cliente", opciones_cliente)
    
    with col11:
        centros_unicos = ['Todos'] + sorted([str(c) for c in df['centro'].dropna().unique().tolist()])
        centro_filtro = st.selectbox("🏢 Filtrar por Centro", centros_unicos)
    
    with col12:
        check_estados = ['Todos', 'Supervisado (1)', 'No Supervisado (0)']
        check_filtro = st.selectbox("✅ Estado Supervisión", check_estados)
    
    # Aplicar todos los filtros
    df_tabla = df.copy()
    
    if motivo_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['motivo_retro'] == motivo_filtro]
    
    df_tabla = df_tabla[
        (df_tabla['puntos'] >= puntos_filtro[0]) & 
        (df_tabla['puntos'] <= puntos_filtro[1])
    ]
    
    if vendedor_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['vendedor'].astype(str) == vendedor_filtro]
    
    if solo_cerrados:
        df_tabla = df_tabla[df_tabla['fecha_cierre'].notna()]
    
    if respuesta_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['respuesta_sub'].astype(str) == respuesta_filtro]
    
    if trimestre_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['trimestre_nombre'] == trimestre_filtro]
    
    if mes_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['mes_nombre'] == mes_filtro]
    
    if cliente_filtro == 'Top 20 más reportados':
        df_tabla = df_tabla[df_tabla['codigo_cliente'].isin(clientes_top)]
    elif cliente_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['codigo_cliente'].astype(str) == cliente_filtro]
    
    if centro_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['centro'] == centro_filtro]
    
    if check_filtro == 'Supervisado (1)':
        df_tabla = df_tabla[df_tabla['check_supervisor'] == 1]
    elif check_filtro == 'No Supervisado (0)':
        df_tabla = df_tabla[df_tabla['check_supervisor'] == 0]
    
    # Mostrar estadísticas de la tabla filtrada
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        st.metric("📊 Registros Mostrados", f"{len(df_tabla):,}")
    
    with col_stats2:
        if len(df_tabla) > 0:
            promedio_puntos_filtrado = df_tabla['puntos'].mean()
            st.metric("⭐ Puntos Promedio", f"{promedio_puntos_filtrado:.2f}")
        else:
            st.metric("⭐ Puntos Promedio", "N/A")
    
    with col_stats3:
        if len(df_tabla) > 0:
            rutas_unicas_filtrado = df_tabla['ruta'].nunique()
            st.metric("🚚 Rutas Únicas", f"{rutas_unicas_filtrado}")
        else:
            st.metric("🚚 Rutas Únicas", "0")
    
    with col_stats4:
        if len(df_tabla) > 0:
            tasa_cierre_filtrado = (df_tabla['fecha_cierre'].notna().sum() / len(df_tabla)) * 100
            st.metric("✅ Tasa de Cierre", f"{tasa_cierre_filtrado:.1f}%")
        else:
            st.metric("✅ Tasa de Cierre", "0%")
    
    # Columnas a mostrar en la tabla
    columnas_mostrar = [
        'fecha_registro', 'usuario', 'ruta', 'codigo_cliente', 'nombre_cliente',
        'motivo_retro', 'puntos', 'vendedor', 'observacion', 'respuesta_sub',
        'centro', 'check_supervisor', 'fecha_cierre'
    ]
    
    # Mostrar la tabla
    if len(df_tabla) > 0:
        st.dataframe(
            df_tabla[columnas_mostrar].sort_values('fecha_registro', ascending=False),
            use_container_width=True,
            height=500
        )
        
        # Opciones de descarga mejoradas
        col_download1, col_download2, col_download3 = st.columns(3)
        
        with col_download1:
            if st.button("📥 Descargar CSV"):
                csv = df_tabla.to_csv(index=False)
                st.download_button(
                    label="💾 Descargar Datos Filtrados (CSV)",
                    data=csv,
                    file_name=f"feedbacks_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
        
        with col_download2:
            if st.button("📊 Generar Reporte Filtrado"):
                reporte_filtrado = generate_report(df_tabla, merged_df, "completo")
                st.download_button(
                    label="📄 Descargar Reporte",
                    data=reporte_filtrado,
                    file_name=f"reporte_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col_download3:
            # Estadísticas rápidas de los datos filtrados
            if st.button("📈 Ver Estadísticas Rápidas"):
                st.markdown("### 📊 Estadísticas de Datos Filtrados")
                
                stats_col1, stats_col2 = st.columns(2)
                
                with stats_col1:
                    st.markdown("**Top 5 Motivos:**")
                    top_motivos = df_tabla['motivo_retro'].value_counts().head(5)
                    for motivo, count in top_motivos.items():
                        st.write(f"• {motivo}: {count}")
                
                with stats_col2:
                    st.markdown("**Top 5 Rutas:**")
                    top_rutas = df_tabla['ruta'].value_counts().head(5)
                    for ruta, count in top_rutas.items():
                        st.write(f"• {ruta}: {count}")
    else:
        st.warning("⚠️ No hay registros que coincidan con los filtros seleccionados.")
        st.info("💡 Intenta ajustar los filtros para ver más datos.")

if __name__ == "__main__":
    main()
