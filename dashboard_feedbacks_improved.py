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

# Función para limpiar DataFrames antes de mostrar (soluciona errores de Arrow)
def clean_dataframe_for_display(df):
    """Limpia un DataFrame para prevenir errores de Arrow en Streamlit"""
    df_clean = df.copy()
    
    # Convertir todas las columnas a tipos seguros para Streamlit
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str)
        elif pd.api.types.is_numeric_dtype(df_clean[col]):
            # Redondear números flotantes para mejor visualización
            if df_clean[col].dtype in ['float64', 'float32']:
                df_clean[col] = df_clean[col].round(2)
    
    # Reemplazar valores NaN con strings vacíos
    df_clean = df_clean.fillna('')
    
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
    
    # Filtrar merged_df también
    merged_df_filtrado = merged_df[
        (merged_df['fecha_registro'].dt.date >= fecha_inicio) &
        (merged_df['fecha_registro'].dt.date <= fecha_fin)
    ]
    
    # Aplicar filtros de mes y semana a merged_df también
    if mes_seleccionado != 'Todos':
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['mes_nombre'] == mes_seleccionado]
    
    if semana_seleccionada != 'Todas':
        semana_numero = int(semana_seleccionada.split()[1])
        merged_df_filtrado = merged_df_filtrado[merged_df_filtrado['semana'] == semana_numero]
    
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
    
    # Análisis por mes
    registros_mes = df.groupby(['mes_nombre', 'mes']).size().reset_index()
    registros_mes.columns = ['mes_nombre', 'mes_num', 'cantidad']
    registros_mes = registros_mes.sort_values('mes_num')
    
    fig_temporal = px.line(
        registros_mes,
        x='mes_nombre',
        y='cantidad',
        title="📈 Evolución Mensual de Registros",
        markers=True,
        line_shape='spline',
        height=700
    )   
    fig_temporal.update_traces(
        line=dict(width=6), 
        marker=dict(size=12),
        texttemplate='%{y}',
        textposition='top center'
    )
    fig_temporal.update_layout(
        showlegend=False
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
            title="Tasa de Cierre (%)",
            titleside="right"
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
            yaxis={'categoryorder': 'total ascending'},
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
        text='total_casos',
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
        margin=dict(l=200, r=50, t=80, b=50),
        xaxis_title="<b>Número de Casos</b>",
        yaxis_title="<b>Motivo de Retroalimentación</b>"
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
        text='total_casos',
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
        margin=dict(l=200, r=50, t=80, b=50),
        xaxis_title="<b>Número de Casos</b>",
        yaxis_title="<b>Tipo de Respuesta</b>"
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
            texttemplate='%{text} reportes',
            textposition='outside',
            marker_line_width=0
        )
        fig_clientes_repetitivos.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickformat': '',
                'type': 'category'
            },
            margin=dict(l=150, r=50, t=80, b=50),
            xaxis_title="<b>Número de Reportes</b>",
            yaxis_title="<b>Cliente</b>"
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
            color_continuous_scale='RdYlBu_r',
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
        st.info("✅ No se encontraron clientes con 3+ reportes del mismo motivo real")

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
    
    # Segunda fila - Análisis de usuarios con menos registros (Top Offenders)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⚠️ Top 15 Usuarios con Menor Cantidad de Feedbacks</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Obtener usuarios con menor cantidad de feedbacks (excluyendo usuarios con 0 registros)
    bottom_users = user_performance[user_performance['Total_Registros'] > 0].sort_values('Total_Registros', ascending=True).head(15)
    
    fig_offenders = px.bar(
        bottom_users,
        x='Total_Registros',
        y='usuario',
        orientation='h',
        title="⚠️ Top 15 Usuarios con Menor Cantidad de Feedbacks",
        color='Puntos_Promedio',
        color_continuous_scale='Reds',
        height=800,
        text='Total_Registros'
    )
    fig_offenders.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_offenders.update_layout(
        yaxis={'categoryorder': 'total descending'},
        margin=dict(l=150, r=50, t=80, b=50),
        xaxis_title="Número de Registros",
        yaxis_title="Usuario"
    )
    st.plotly_chart(fig_offenders, use_container_width=True)
    
    # Mostrar tabla adicional con detalles de los Top Offenders
    st.markdown("#### 📋 Detalles de Top Offenders")
    offenders_details = bottom_users[['usuario', 'Total_Registros', 'Puntos_Promedio', 'Rutas_Trabajadas', 'Tasa_Cierre']].copy()
    offenders_details.columns = ['Usuario', 'Total Registros', 'Puntos Promedio', 'Rutas Trabajadas', 'Tasa Cierre (%)']
    st.dataframe(clean_dataframe_for_display(offenders_details), use_container_width=True)

def show_performance_analysis(df):
    """Análisis de rendimiento completo con múltiples gráficas"""
    st.subheader("🎯 Análisis Detallado de Rendimiento y Calidad")
      # Primera fila - Top clientes más reportados (usando string para evitar formato de millones)
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
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A'  # Motivo real más común
    }).round(2).reset_index()
    clientes_reportados.columns = ['codigo_cliente', 'total_reportes', 'puntos_promedio', 'reportes_cerrados', 'motivo_principal']
    clientes_reportados['tasa_cierre'] = (clientes_reportados['reportes_cerrados'] / clientes_reportados['total_reportes']) * 100    
    clientes_reportados = clientes_reportados.sort_values('total_reportes', ascending=False).head(20)
    
    # Crear una copia con códigos formateados como strings para evitar formateo automático
    clientes_display = clientes_reportados.copy()
    clientes_display['codigo_cliente_display'] = clientes_display['codigo_cliente'].astype(str)
    
    fig_clientes = px.bar(
        clientes_display,
        x='total_reportes',
        y='codigo_cliente_display',
        orientation='h',
        title="🏪 Top 20 Clientes Más Reportados",
        color='motivo_principal',
        height=800,
        text='total_reportes',
        hover_data={
            'codigo_cliente': True,
            'total_reportes': True,
            'puntos_promedio': ':.2f',
            'tasa_cierre': ':.1f',
            'motivo_principal': True
        }
    )    
    fig_clientes.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=0
    )
    fig_clientes.update_layout(
        yaxis={
            'categoryorder': 'total ascending', 
            'tickformat': '',
            'type': 'category'
        },
        margin=dict(l=200, r=50, t=50, b=50),
        xaxis_title="<b>Número de Reportes</b>",
        yaxis_title="<b>Código Cliente</b>"
    )
    st.plotly_chart(fig_clientes, use_container_width=True)
    
    # Tabla detallada de clientes más reportados
    st.markdown("#### 📋 Detalles de Clientes Más Reportados")
    clientes_details = clientes_reportados[['codigo_cliente', 'total_reportes', 'puntos_promedio', 'motivo_principal', 'tasa_cierre']].copy()
    clientes_details.columns = ['Código Cliente', 'Total Reportes', 'Puntos Promedio', 'Motivo Principal', 'Tasa Cierre (%)']
    st.dataframe(clean_dataframe_for_display(clientes_details), use_container_width=True)
    
    # Segunda fila - Análisis de respuestas críticas
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🚨 Respuestas Más Críticas (Menor Puntuación)</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    respuestas_criticas = df.groupby('respuesta_sub').agg({
        'puntos': ['mean', 'count'],
        'codigo_cliente': 'nunique'
    }).round(2)
    respuestas_criticas.columns = ['puntos_promedio', 'total_casos', 'clientes_afectados']
    respuestas_criticas = respuestas_criticas.reset_index()
    respuestas_criticas = respuestas_criticas[respuestas_criticas['total_casos'] >= 5]  # Solo respuestas con al menos 5 casos
    respuestas_criticas = respuestas_criticas.sort_values('puntos_promedio', ascending=True).head(15)
    
    fig_criticas = px.bar(
        respuestas_criticas,
        x='puntos_promedio',
        y='respuesta_sub',
        orientation='h',
        title="🚨 Top 15 Respuestas Más Críticas (Menor Puntuación Promedio)",
        color='clientes_afectados',
        color_continuous_scale='Reds',
        height=800,
        text='puntos_promedio'
    )
    fig_criticas.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside',
        marker_line_width=0
    )
    fig_criticas.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=250, r=50, t=50, b=50),
        xaxis_title="Puntos Promedio",
        yaxis_title="Tipo de Respuesta"
    )
    st.plotly_chart(fig_criticas, use_container_width=True)

def show_advanced_analysis(df, merged_df):
    """Análisis avanzado con gráficas especializadas"""
    st.subheader("📊 Análisis Avanzado y Insights Profundos")
    
    # Primera fila - Análisis de clientes problemáticos (usando respuesta_sub como motivo real)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Top 20 Clientes con Más Reportes (Usando Motivos Reales)</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Convertir codigo_cliente a string para evitar problemas de formato
    df['codigo_cliente_str'] = df['codigo_cliente'].astype(str)    # Análisis de clientes usando respuesta_sub como motivo real
    clientes_analysis = df.groupby('codigo_cliente_str').agg({
        'id_tema': 'count',
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',  # Motivo más común
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
        title="🎯 Top 20 Clientes con Más Reportes (Motivos Reales)",
        color='motivo_principal',
        height=800,
        text='total_reportes',
        hover_data={
            'codigo_cliente': True,
            'motivo_principal': True,
            'total_reportes': True,
            'puntos_promedio': ':.2f',
            'tasa_cierre': ':.1f'
        }
    )    
    fig_clientes_problematicos.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker_line_width=2
    )
    fig_clientes_problematicos.update_layout(
        yaxis={
            'categoryorder': 'total ascending', 
            'tickformat': '',
            'type': 'category'
        },
        margin=dict(l=150, r=50, t=80, b=50),
        xaxis_title="<b>Número de Reportes</b>",
        yaxis_title="<b>Código Cliente</b>"
    )
    st.plotly_chart(fig_clientes_problematicos, use_container_width=True)
    
    # Tabla detallada de clientes problemáticos
    st.markdown("##### 📋 Detalles de Clientes con Más Reportes")
    clientes_details = clientes_analysis[['codigo_cliente', 'motivo_principal', 'total_reportes', 'puntos_promedio', 'tasa_cierre']].copy()
    clientes_details.columns = ['Código Cliente', 'Motivo Principal', 'Total Reportes', 'Puntos Promedio', 'Tasa Cierre (%)']
    st.dataframe(clean_dataframe_for_display(clientes_details), use_container_width=True)
    
    # Segunda fila - Rutas líderes por tipo de respuesta específica con información de supervisor/contratista
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🚚 Rutas Líderes por Tipo de Respuesta Específica</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Crear análisis de rutas con información adicional si está disponible
    if 'SUPERVISOR' in merged_df.columns:
        ruta_respuesta_analysis = merged_df.groupby(['respuesta_sub', 'ruta', 'SUPERVISOR']).size().reset_index()
        ruta_respuesta_analysis.columns = ['respuesta_sub', 'ruta', 'supervisor', 'cantidad']
        
        # Obtener la ruta líder para cada tipo de respuesta
        rutas_lideres_respuesta = ruta_respuesta_analysis.loc[
            ruta_respuesta_analysis.groupby('respuesta_sub')['cantidad'].idxmax()
        ]
        
        # Crear etiqueta combinada para mejor visualización
        rutas_lideres_respuesta['ruta_supervisor'] = rutas_lideres_respuesta['ruta'].astype(str) + ' (' + rutas_lideres_respuesta['supervisor'].astype(str) + ')'
        
        fig_rutas_respuesta = px.bar(
            rutas_lideres_respuesta.head(15),
            x='cantidad',
            y='respuesta_sub',
            color='supervisor',
            orientation='h',
            title="🚚 Ruta Líder por Cada Tipo de Respuesta (Con Supervisor)",
            height=800,
            text='cantidad',
            hover_data={
                'respuesta_sub': True,
                'ruta': True,
                'supervisor': True,
                'cantidad': True
            }
        )
    else:
        ruta_respuesta_analysis = df.groupby(['respuesta_sub', 'ruta']).size().reset_index()
        ruta_respuesta_analysis.columns = ['respuesta_sub', 'ruta', 'cantidad']
        
        rutas_lideres_respuesta = ruta_respuesta_analysis.loc[
            ruta_respuesta_analysis.groupby('respuesta_sub')['cantidad'].idxmax()
        ]
        
        fig_rutas_respuesta = px.bar(
            rutas_lideres_respuesta.head(15),
            x='cantidad',
            y='respuesta_sub',
            color='ruta',
            orientation='h',
            title="🚚 Ruta Líder por Cada Tipo de Respuesta",
            height=800,
            text='cantidad'
        )
    fig_rutas_respuesta.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker_line_width=0,
        textfont_size=14,
        textfont_color='white',
        textfont_family='Arial Black'
    )
    fig_rutas_respuesta.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=200, r=50, t=80, b=50),
        xaxis_title="<b>Número de Casos</b>",
        yaxis_title="<b>Tipo de Respuesta</b>"
    )
    st.plotly_chart(fig_rutas_respuesta, use_container_width=True)    
    # Tercera fila - Análisis de motivos específicos más reportados (usando respuesta_sub)
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💬 Análisis de Motivos Reales Más Reportados</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Análisis usando respuesta_sub como motivo real
    motivos_reales_analysis = df.groupby('respuesta_sub').agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'codigo_cliente_str': 'nunique',
        'fecha_cierre': lambda x: x.notna().sum() if not x.empty else 0
    }).round(2).reset_index()
    motivos_reales_analysis.columns = ['motivo_real', 'total_casos', 'puntos_promedio', 'clientes_afectados', 'casos_cerrados']
    motivos_reales_analysis['tasa_cierre'] = (motivos_reales_analysis['casos_cerrados'] / motivos_reales_analysis['total_casos']) * 100
    motivos_reales_analysis = motivos_reales_analysis.sort_values('total_casos', ascending=False).head(15)
    
    fig_motivos_reales = px.scatter(
        motivos_reales_analysis,
        x='total_casos',
        y='puntos_promedio',
        size='clientes_afectados',
        hover_data=['motivo_real', 'tasa_cierre'],
        title="💬 Motivos Reales: Frecuencia vs Calidad vs Clientes Afectados",
        color='tasa_cierre',
        color_continuous_scale='RdYlGn',
        height=800,
        labels={
            'total_casos': 'Total de Casos',
            'puntos_promedio': 'Puntos Promedio',
            'clientes_afectados': 'Clientes Afectados'
        }
    )
    fig_motivos_reales.update_traces(
        marker=dict(
            sizemode='diameter',
            sizemin=10,
            line_width=0
        )
    )
    fig_motivos_reales.update_layout(
        xaxis_title="<b>Total de Casos</b>",
        yaxis_title="<b>Puntos Promedio</b>",
        margin=dict(l=50, r=50, t=80, b=50)
    )
    st.plotly_chart(fig_motivos_reales, use_container_width=True)
      # Tabla detallada de motivos reales
    st.markdown("##### 📋 Detalles de Motivos Reales")
    motivos_reales_details = motivos_reales_analysis[['motivo_real', 'total_casos', 'puntos_promedio', 'clientes_afectados', 'tasa_cierre']].copy()
    motivos_reales_details.columns = ['Motivo Real', 'Total Casos', 'Puntos Promedio', 'Clientes Afectados', 'Tasa Cierre (%)']
    st.dataframe(clean_dataframe_for_display(motivos_reales_details), use_container_width=True)
    
    # Nueva sección - Análisis de Frecuencia de Temas por ID
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🔢 Análisis de Frecuencia por ID de Tema (Top Reportes)</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de frecuencia por id_tema
    tema_frequency_analysis = df.groupby('id_tema').agg({
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',  # Tipo más común
        'codigo_cliente_str': 'nunique',
        'puntos': 'mean',
        'fecha_cierre': lambda x: x.notna().sum(),
        'ruta': 'nunique'
    }).round(2).reset_index()
    
    # Contar frecuencia de cada id_tema
    tema_counts = df['id_tema'].value_counts().reset_index()
    tema_counts.columns = ['id_tema', 'frecuencia_reportes']
    
    # Merge para tener datos completos
    tema_frequency_analysis = tema_frequency_analysis.merge(tema_counts, on='id_tema', how='left')
    tema_frequency_analysis.columns = ['ID_Tema', 'Tipo_Principal', 'Clientes_Unicos', 'Puntos_Promedio', 'Casos_Cerrados', 'Rutas_Afectadas', 'Frecuencia_Reportes']
    
    # Calcular tasa de cierre
    tema_frequency_analysis['Tasa_Cierre'] = (tema_frequency_analysis['Casos_Cerrados'] / tema_frequency_analysis['Frecuencia_Reportes']) * 100
    
    # Ordenar por frecuencia de reportes descendente y tomar top 20
    tema_frequency_analysis = tema_frequency_analysis.sort_values('Frecuencia_Reportes', ascending=False).head(20)
      # Gráfico de frecuencia de temas
    fig_tema_frequency = px.bar(
        tema_frequency_analysis,
        x='Frecuencia_Reportes',
        y='ID_Tema',
        orientation='h',
        title="🔢 Top 20 IDs de Tema Más Reportados",
        color='Puntos_Promedio',
        color_continuous_scale='Plasma',
        height=800,
        text='Frecuencia_Reportes',
        hover_data={
            'ID_Tema': True,
            'Tipo_Principal': True,
            'Frecuencia_Reportes': True,
            'Clientes_Unicos': True,
            'Puntos_Promedio': ':.2f',
            'Tasa_Cierre': ':.1f',
            'Rutas_Afectadas': True        }
    )
    
    fig_tema_frequency.update_traces(
        texttemplate='<b>ID: %{y}</b><br><b>%{text} reportes</b>',
        textposition='outside',
        marker_line_width=0,
        textfont_size=14,
        textfont_color='white'
    )
    fig_tema_frequency.update_layout(
        yaxis={
            'categoryorder': 'total ascending',
            'tickformat': '',
            'type': 'category',
            'tickfont_size': 14,
            'tickfont_color': 'white'
        },
        margin=dict(l=150, r=100, t=80, b=50),
        xaxis_title="<b>Frecuencia de Reportes</b>",
        yaxis_title="<b>ID de Tema</b>",
        font=dict(size=14)
    )
    
    st.plotly_chart(fig_tema_frequency, use_container_width=True)
    
    # Tabla detallada de frecuencia por ID de tema
    st.markdown("##### 📋 Detalles de Frecuencia por ID de Tema")
    tema_details = tema_frequency_analysis[['ID_Tema', 'Tipo_Principal', 'Frecuencia_Reportes', 'Clientes_Unicos', 'Puntos_Promedio', 'Tasa_Cierre', 'Rutas_Afectadas']].copy()
    tema_details.columns = ['ID Tema', 'Tipo Principal', 'Frecuencia', 'Clientes Únicos', 'Puntos Promedio', 'Tasa Cierre (%)', 'Rutas Afectadas']
    st.dataframe(clean_dataframe_for_display(tema_details), use_container_width=True)
    
    # Cuarta fila - Distribución de Centros
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🏢 Distribución de Centros por Registros</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    centro_analysis = df.groupby('centro').agg({
        'id_tema': 'count',
        'puntos': 'mean',
        'usuario': 'nunique'
    }).round(2).reset_index()
    centro_analysis.columns = ['centro', 'total_registros', 'puntos_promedio', 'usuarios_unicos']
    centro_analysis = centro_analysis.sort_values('total_registros', ascending=False)
    
    fig_centros = px.treemap(
        centro_analysis,
        path=['centro'],
        values='total_registros',
        color='puntos_promedio',
        title="🏢 Distribución de Registros por Centro",
        color_continuous_scale='viridis',
        height=800
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
        motivo_filtro = st.selectbox("🎯 Filtrar por Motivo", motivos_unicos, key="detailed_motivo_filtro")
    
    with col2:
        min_puntos = int(df['puntos'].min()) if not df.empty else 0
        max_puntos = int(df['puntos'].max()) if not df.empty else 5
        
        if min_puntos == max_puntos:
            max_puntos = min_puntos + 1
        
        puntos_filtro = st.slider("⭐ Rango de Puntos", min_puntos, max_puntos, (min_puntos, max_puntos), key="detailed_puntos_filtro")
    
    with col3:
        vendedores_unicos = ['Todos'] + sorted([str(v) for v in df['vendedor'].dropna().unique().tolist()])
        vendedor_filtro = st.selectbox("💼 Filtrar por Vendedor", vendedores_unicos, key="detailed_vendedor_filtro")
    
    with col4:
        solo_cerrados = st.checkbox("📋 Solo mostrar registros cerrados", key="detailed_solo_cerrados")
    
    # Segunda fila de filtros - NUEVOS FILTROS
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        if 'SUPERVISOR' in merged_df.columns:
            supervisores_disponibles = merged_df['SUPERVISOR'].dropna().unique()
            supervisores_unicos = ['Todos'] + sorted([str(s) for s in supervisores_disponibles])
            supervisor_filtro = st.selectbox("👨‍💼 Filtrar por Supervisor", supervisores_unicos, key="detailed_supervisor_filtro")
        else:
            supervisor_filtro = 'Todos'
    
    with col6:
        if 'CONTRATISTA' in merged_df.columns:
            contratistas_disponibles = merged_df['CONTRATISTA'].dropna().unique()
            contratistas_unicos = ['Todos'] + sorted([str(c) for c in contratistas_disponibles])
            contratista_filtro = st.selectbox("🏢 Filtrar por Contratista", contratistas_unicos, key="detailed_contratista_filtro")
        else:
            contratista_filtro = 'Todos'
    
    with col7:
        respuestas_unicos = ['Todos'] + sorted([str(r) for r in df['respuesta_sub'].dropna().unique().tolist()])
        respuesta_filtro = st.selectbox("💬 Filtrar por Tipo Respuesta", respuestas_unicos, key="detailed_respuesta_filtro")
    
    with col8:
        trimestres = ['Todos'] + sorted([str(t) for t in df['trimestre_nombre'].dropna().unique().tolist()])
        trimestre_filtro = st.selectbox("📅 Filtrar por Trimestre", trimestres, key="detailed_trimestre_filtro")
    
    # Tercera fila de filtros
    col9, col10, col11, col12 = st.columns(4)
    
    with col9:
        meses_disponibles = ['Todos'] + sorted([str(m) for m in df['mes_nombre'].dropna().unique().tolist()])
        mes_filtro = st.selectbox("📆 Filtrar por Mes", meses_disponibles, key="detailed_mes_filtro")
    
    with col10:
        # Top 20 clientes más reportados para filtro rápido
        clientes_top = df['codigo_cliente'].value_counts().head(20).index.tolist()
        opciones_cliente = ['Todos', 'Top 20 más reportados'] + sorted([str(c) for c in df['codigo_cliente'].dropna().unique().tolist()])
        cliente_filtro = st.selectbox("🏪 Filtrar por Cliente", opciones_cliente, key="detailed_cliente_filtro")
    
    with col11:
        centros_unicos = ['Todos'] + sorted([str(c) for c in df['centro'].dropna().unique().tolist()])
        centro_filtro = st.selectbox("🏢 Filtrar por Centro", centros_unicos, key="detailed_centro_filtro")
    
    with col12:
        check_estados = ['Todos', 'Supervisado (1)', 'No Supervisado (0)']
        check_filtro = st.selectbox("✅ Estado Supervisión", check_estados, key="detailed_check_filtro")
    
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
            clean_dataframe_for_display(df_tabla[columnas_mostrar].sort_values('fecha_registro', ascending=False)),
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
