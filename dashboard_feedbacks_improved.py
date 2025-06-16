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
import os
import glob
from io import BytesIO
import base64
import plotly.io as pio
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
# NUEVA IMPORTACIÓN PARA XLSX
import xlsxwriter
# IMPORTAR VISUALIZACIONES MEJORADAS
from enhanced_visualizations import add_day_hour_heatmap, add_recurrence_analysis, add_comparative_time_analysis, add_problem_resolution_analysis
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Seguimiento Feedbacks - DS00",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para un diseño profesional mejorado
st.markdown("""
<style>
    /* Header principal */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Tarjetas de métricas mejoradas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar mejorado */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 0 20px 20px 0;    }      /* Tabs completamente fijos - Sin movimiento ni cambio de tamaño */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        background: rgba(0,0,0,0.4) !important;
        padding: 6px !important;
        border-radius: 15px !important;
        margin-bottom: 2rem !important;
        justify-content: center !important;
        align-items: center !important;
        height: 70px !important;
        min-height: 70px !important;
        max-height: 70px !important;
        position: relative !important;
        display: flex !important;
        width: 100% !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 58px !important;
        min-height: 58px !important;
        max-height: 58px !important;
        width: calc(14.28% - 2px) !important;
        min-width: calc(14.28% - 2px) !important;
        max-width: calc(14.28% - 2px) !important;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
        border-radius: 12px !important;
        padding: 8px 4px !important;
        font-weight: 700 !important;
        font-size: 0.7rem !important;
        border: 2px solid rgba(255, 255, 255, 0.4) !important;
        color: #2d3748 !important;
        transition: none !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        flex: none !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        position: relative !important;
        transform: none !important;
        box-sizing: border-box !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        border-color: rgba(255, 255, 255, 0.8) !important;
        transform: none !important;
        z-index: 2 !important;
        height: 58px !important;
        width: calc(14.28% - 2px) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        transform: none !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
        height: 58px !important;
        width: calc(14.28% - 2px) !important;
    }
      /* Asegurar que el contenido de las pestañas también sea fijo */
    .stTabs [data-baseweb="tab"] > div {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Bloquear completamente cualquier animación o movimiento */
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] > div,
    .stTabs [data-baseweb="tab"] > div > div,
    .stTabs [data-baseweb="tab"] * {
        transition: none !important;
        animation: none !important;
        transform: none !important;
        will-change: auto !important;
    }
      /* Forzar posición exacta */
    .stTabs [data-baseweb="tab"]:nth-child(1) { left: 0% !important; }
    .stTabs [data-baseweb="tab"]:nth-child(2) { left: 14.28% !important; }
    .stTabs [data-baseweb="tab"]:nth-child(3) { left: 28.56% !important; }
    .stTabs [data-baseweb="tab"]:nth-child(4) { left: 42.84% !important; }
    .stTabs [data-baseweb="tab"]:nth-child(5) { left: 57.12% !important; }
    .stTabs [data-baseweb="tab"]:nth-child(6) { left: 71.4% !important; }
    .stTabs [data-baseweb="tab"]:nth-child(7) { left: 85.68% !important; }
    
    /* Forza el mismo ancho para todas las pestañas */
    .stTabs [data-baseweb="tab"]:nth-child(1),
    .stTabs [data-baseweb="tab"]:nth-child(2),
    .stTabs [data-baseweb="tab"]:nth-child(3),
    .stTabs [data-baseweb="tab"]:nth-child(4),
    .stTabs [data-baseweb="tab"]:nth-child(5),
    .stTabs [data-baseweb="tab"]:nth-child(6),
    .stTabs [data-baseweb="tab"]:nth-child(7) {
        width: calc(14.28% - 2px) !important;
        min-width: calc(14.28% - 2px) !important;
        max-width: calc(14.28% - 2px) !important;
        height: 58px !important;
        min-height: 58px !important;
        max-height: 58px !important;
        flex: none !important;
        flex-shrink: 0 !important;
        flex-grow: 0 !important;
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
      /* Bloquear cualquier cambio de estilo en hover o selección */
    .stTabs [data-baseweb="tab"]:hover,
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        width: calc(14.28% - 2px) !important;
        min-width: calc(14.28% - 2px) !important;
        max-width: calc(14.28% - 2px) !important;
        height: 58px !important;
        min-height: 58px !important;
        max-height: 58px !important;
        flex: none !important;
        flex-shrink: 0 !important;
        flex-grow: 0 !important;
        transform: none !important;
        transition: none !important;
    }
    
    /* Regla universal para bloquear movimiento en tabs */
    .stTabs div[role="tablist"] > button {
        min-width: calc(14.28% - 2px) !important;
        max-width: calc(14.28% - 2px) !important;
        width: calc(14.28% - 2px) !important;
        flex: none !important;
        transition: none !important;
        transform: none !important;
        animation: none !important;
    }
    
    /* Forzar distribución uniforme */
    .stTabs div[role="tablist"] {
        display: flex !important;
        width: 100% !important;
        justify-content: space-evenly !important;
        gap: 2px !important;
    }/* KPIs rediseñados como cubos uniformes y coloridos */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 1.8rem !important;
        border-radius: 20px !important;
        margin: 0.8rem 0.3rem !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
        border: 3px solid rgba(255, 255, 255, 0.2) !important;
        text-align: center !important;
        min-height: 160px !important;
        max-height: 160px !important;
        min-width: 180px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.4s ease !important;
        transform: scale(1) !important;
    }
    
    .stMetric:hover {
        transform: scale(1.05) translateY(-8px) !important;
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.6) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
      /* Banda superior colorida única para cada KPI */
    .stMetric:nth-child(1)::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 6px !important;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4) !important;
    }
    
    .stMetric:nth-child(2)::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 6px !important;
        background: linear-gradient(90deg, #f093fb, #f5576c) !important;
    }
    
    .stMetric:nth-child(3)::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 6px !important;
        background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
    }
    
    .stMetric:nth-child(4)::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 6px !important;
        background: linear-gradient(90deg, #fa709a, #fee140) !important;
    }
    
    .stMetric:nth-child(5)::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 6px !important;
        background: linear-gradient(90deg, #4ecdc4, #44a08d) !important;
    }
    
    .stMetric [data-testid="metric-container"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        text-align: center !important;
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
        margin: 0 !important;
    }
    
    .stMetric [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        color: white !important;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.4) !important;
        margin-bottom: 0.8rem !important;
        line-height: 1 !important;
    }
    
    .stMetric [data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: rgba(255,255,255,0.95) !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        margin-top: 0.5rem !important;
        line-height: 1.2 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3) !important;
    }
    
    .stMetric [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: rgba(255,255,255,0.8) !important;
        margin-top: 0.3rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
    }
    
    /* Tarjetas de análisis rediseñadas */
    .analysis-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 25px;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 20px 40px rgba(79, 172, 254, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .analysis-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #ffa726, #42a5f5, #ab47bc);
    }
    
    /* Tarjetas de rendimiento superior */
    .top-performance {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 25px rgba(250, 112, 154, 0.3);
    }
    
    /* Insights mejorados */
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        border-left: 5px solid #ffa726;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    /* Alertas y notificaciones */
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8a80 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        border-left: 5px solid #ffab40;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.2);
    }    # Mejoras en gráficos - tamaños consistentes y texto negro
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        min-height: 500px;
    }
    
    .stPlotlyChart > div {
        border-radius: 15px;
    }
    
    /* Tablas mejoradas */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Efectos de hover para elementos interactivos */
    .metric-card:hover, .analysis-card:hover, .top-performance:hover {
        transform: translateY(-5px);
        transition: all 0.3s ease;
    }
    
    /* Títulos de secciones */
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Columnas más organizadas */
    .stColumns {
        gap: 1rem;
    }
    
    /* Responsividad mejorada */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .analysis-card, .kpi-container {
            padding: 1rem;
            margin: 1rem 0;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem !important;
            padding: 0 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar todas las BDs de rutas disponibles automáticamente
@st.cache_data
def load_all_rutas_databases():
    """Carga automáticamente todas las BDs de rutas disponibles en el directorio"""
    import glob
    
    # Diccionario para almacenar todas las BDs de rutas
    rutas_databases = {}
    
    # Cargar BD default
    try:
        default_df = pd.read_excel('BD_Rutas.xlsx')
        rutas_databases['default'] = default_df
        print("✅ BD_Rutas.xlsx (default) cargada")
    except Exception as e:
        print(f"❌ Error cargando BD_Rutas.xlsx: {e}")
        return None
    
    # Buscar automáticamente BDs por mes usando patrones de nombres
    meses_patrones = {
        'Enero': ['BD_Rutas_Enero.xlsx', 'BD_Rutas_enero.xlsx', 'BD_Rutas_ENERO.xlsx', 'BD_Rutas_Jan.xlsx'],
        'Febrero': ['BD_Rutas_Febrero.xlsx', 'BD_Rutas_febrero.xlsx', 'BD_Rutas_FEBRERO.xlsx', 'BD_Rutas_Feb.xlsx'],
        'Marzo': ['BD_Rutas_Marzo.xlsx', 'BD_Rutas_marzo.xlsx', 'BD_Rutas_MARZO.xlsx', 'BD_Rutas_Mar.xlsx'],
        'Abril': ['BD_Rutas_Abril.xlsx', 'BD_Rutas_abril.xlsx', 'BD_Rutas_ABRIL.xlsx', 'BD_Rutas_Apr.xlsx'],
        'Mayo': ['BD_Rutas_Mayo.xlsx', 'BD_Rutas_mayo.xlsx', 'BD_Rutas_MAYO.xlsx', 'BD_Rutas_May.xlsx'],
        'Junio': ['BD_Rutas_Junio.xlsx', 'BD_Rutas_junio.xlsx', 'BD_Rutas_JUNIO.xlsx', 'BD_Rutas_Jun.xlsx'],
        'Julio': ['BD_Rutas_Julio.xlsx', 'BD_Rutas_julio.xlsx', 'BD_Rutas_JULIO.xlsx', 'BD_Rutas_Jul.xlsx'],
        'Agosto': ['BD_Rutas_Agosto.xlsx', 'BD_Rutas_agosto.xlsx', 'BD_Rutas_AGOSTO.xlsx', 'BD_Rutas_Aug.xlsx'],
        'Septiembre': ['BD_Rutas_Septiembre.xlsx', 'BD_Rutas_septiembre.xlsx', 'BD_Rutas_SEPTIEMBRE.xlsx', 'BD_Rutas_Sep.xlsx'],
        'Octubre': ['BD_Rutas_Octubre.xlsx', 'BD_Rutas_octubre.xlsx', 'BD_Rutas_OCTUBRE.xlsx', 'BD_Rutas_Oct.xlsx'],
        'Noviembre': ['BD_Rutas_Noviembre.xlsx', 'BD_Rutas_noviembre.xlsx', 'BD_Rutas_NOVIEMBRE.xlsx', 'BD_Rutas_Nov.xlsx'],
        'Diciembre': ['BD_Rutas_Diciembre.xlsx', 'BD_Rutas_diciembre.xlsx', 'BD_Rutas_DICIEMBRE.xlsx', 'BD_Rutas_Dec.xlsx']
    }
    
    # Buscar archivos para cada mes
    for mes, patrones in meses_patrones.items():
        for patron in patrones:
            try:
                if os.path.exists(patron):
                    mes_df = pd.read_excel(patron)
                    
                    # Validar que tenga las columnas requeridas
                    required_cols = ['RUTA', 'SUPERVISOR', 'CONTRATISTA']
                    if all(col in mes_df.columns for col in required_cols):
                        rutas_databases[mes] = mes_df
                        print(f"✅ {patron} cargada para {mes}")
                        break  # Solo cargar el primer archivo encontrado para cada mes
                    else:
                        print(f"⚠️ {patron} no tiene las columnas requeridas: {required_cols}")
            except Exception as e:
                print(f"❌ Error cargando {patron}: {e}")
    
    # También buscar con patrones de wildcard para capturar variaciones adicionales
    additional_patterns = [
        'BD_Rutas_*.xlsx',
        'bd_rutas_*.xlsx',
        'BD_RUTAS_*.xlsx'
    ]
    
    for pattern in additional_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                # Extraer el mes del nombre del archivo
                filename = os.path.basename(file).lower()
                for mes in meses_patrones.keys():
                    if mes.lower() in filename and mes not in rutas_databases:
                        mes_df = pd.read_excel(file)
                        required_cols = ['RUTA', 'SUPERVISOR', 'CONTRATISTA']
                        if all(col in mes_df.columns for col in required_cols):
                            rutas_databases[mes] = mes_df
                            print(f"✅ {file} cargada automáticamente para {mes}")
                            break
            except Exception as e:
                print(f"❌ Error procesando {file}: {e}")
    
    return rutas_databases

# Función para cargar datos con cache
@st.cache_data
def load_data():
    """Carga los datos de los archivos Excel con manejo de duplicados y datos faltantes"""
    try:
        # Cargar Feedbacks
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        
        # Cargar todas las BDs de rutas disponibles automáticamente
        rutas_databases = load_all_rutas_databases()
        if rutas_databases is None:
            st.error("❌ No se pudo cargar ninguna BD de rutas")
            return None
        
        # Usar BD_Rutas default para el procesamiento inicial
        rutas_df = rutas_databases['default']
        
        # Guardar todas las BDs en session_state para uso posterior
        if 'rutas_databases_loaded' not in st.session_state:
            for mes, df in rutas_databases.items():
                if mes != 'default':
                    st.session_state[f'rutas_df_{mes}'] = df
            st.session_state['rutas_databases_loaded'] = True
            st.session_state['rutas_databases_info'] = {
                'available_months': list(rutas_databases.keys()),
                'total_databases': len(rutas_databases)
            }
        
        # ========== LIMPIEZA DE DATOS BD_RUTAS ==========        # Identificar y manejar duplicados en BD_Rutas
        duplicates = rutas_df[rutas_df['RUTA'].duplicated(keep=False)]
        if len(duplicates) > 0:
            # st.sidebar.warning(f"⚠️ Encontrados {len(duplicates)} registros duplicados en BD_Rutas")
            # Mantener solo el primer registro de cada ruta duplicada
            rutas_df = rutas_df.drop_duplicates(subset=['RUTA'], keep='first')
          # ========== PREPARACIÓN DE DATOS FEEDBACKS ==========
        # Limpiar y preparar datos
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        feedbacks_df['fecha_cierre'] = pd.to_datetime(feedbacks_df['fecha_cierre'])
        
        # CRITICAL: Calculate tiempo_cierre_dias column
        feedbacks_df['tiempo_cierre_dias'] = (
            feedbacks_df['fecha_cierre'] - feedbacks_df['fecha_registro']
        ).dt.days.fillna(0)  # Fill NaN with 0 for non-closed cases
        
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
          # ========== MERGE CON VALIDACIÓN ==========
        # Identificar rutas faltantes antes del merge
        rutas_feedbacks = set(feedbacks_df['ruta'].unique())
        rutas_bd = set(rutas_df['RUTA'].unique())
        rutas_faltantes = rutas_feedbacks - rutas_bd
        
        # Comentado para limpiar la interfaz
        # if rutas_faltantes:
        #     st.sidebar.warning(f"⚠️ {len(rutas_faltantes)} rutas en Feedbacks sin datos de supervisor: {list(rutas_faltantes)}")
        
        # Join con BD_Rutas
        merged_df = feedbacks_df.merge(
            rutas_df, 
            left_on='ruta', 
            right_on='RUTA', 
            how='left'
        )
          # ========== MANEJO DE DATOS FALTANTES ==========
        # Rellenar supervisores y contratistas faltantes
        merged_df['SUPERVISOR'] = merged_df['SUPERVISOR'].fillna('SIN ASIGNAR')
        merged_df['CONTRATISTA'] = merged_df['CONTRATISTA'].fillna('SIN ASIGNAR')
        
        # CRITICAL: Calculate tiempo_cierre_dias for merged_df as well
        merged_df['tiempo_cierre_dias'] = (
            merged_df['fecha_cierre'] - merged_df['fecha_registro']
        ).dt.days.fillna(0)  # Fill NaN with 0 for non-closed cases
        
        # Crear resumen de calidad de datos
        data_quality = {
            'total_feedbacks': len(feedbacks_df),
            'rutas_feedbacks': feedbacks_df['ruta'].nunique(),
            'total_rutas_bd': len(rutas_df),
            'rutas_unicas_bd': rutas_df['RUTA'].nunique(),
            'rutas_matched': len(rutas_feedbacks & rutas_bd),
            'rutas_sin_supervisor': len(rutas_faltantes),
            'duplicados_bd_rutas': len(duplicates)
        }
        
        return feedbacks_df, rutas_df, merged_df, data_quality
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None, None, None, None

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
    """Crea métricas KPI avanzadas con cubitos uniformes y coloridos"""
    st.markdown("### 📊 KPIs Principales del Sistema")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Definir gradientes de colores únicos para cada KPI
    kpi_colors = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",  # Azul-Púrpura
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",  # Rosa-Rojo
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",  # Azul-Cyan
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",  # Rosa-Amarillo
        "linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)"   # Verde-Turquesa
    ]
    
    with col1:
        total_registros = len(df)
        st.metric(
            "📊 Total Registros",
            f"{total_registros:,}",
            f"+{len(df[df['mes'] == df['mes'].max()])} este mes" if 'mes' in df.columns and not df.empty else ""
        )
    
    with col2:
        total_rutas = df['ruta'].nunique()
        st.metric(
            "🚚 Rutas Únicas", 
            f"{total_rutas}",
            "🗺️ Activas"
        )
    
    with col3:
        total_usuarios = df['usuario'].nunique()
        st.metric(
            "👥 Usuarios Activos",
            f"{total_usuarios}",
            "👤 Personal"
        )
    
    with col4:
        total_clientes = df['codigo_cliente'].nunique()
        st.metric(
            "🏢 Clientes Únicos",
            f"{total_clientes:,}",
            "🏪 Base"
        )
    
    with col5:
        tasa_cierre = (df['fecha_cierre'].notna().sum() / len(df)) * 100
        st.metric(
            "✅ Tasa de Cierre",
            f"{tasa_cierre:.1f}%",
            "📈 Eficiencia"
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
- Tiempo Promedio de Cierre: {df[df['fecha_cierre'].notna()]['tiempo_cierre_dias'].mean():.1f} días
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

## ANÁLISIS DE TIEMPOS DE CIERRE
### Distribución de Tiempos de Cierre (días):
{df[df['fecha_cierre'].notna()]['tiempo_cierre_dias'].value_counts().sort_index().to_string()}

### Análisis de Supervisores (si disponible):
"""
        if 'SUPERVISOR' in merged_df.columns:
            supervisor_analysis = merged_df.groupby('SUPERVISOR').agg({
                'id_tema': 'count',
                'tiempo_cierre_dias': 'mean'
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
- Tiempo Promedio de Cierre: {df[df['fecha_cierre'].notna()]['tiempo_cierre_dias'].mean():.1f} días
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
        story.append(Paragraph("📊 REPORTE FEEDBACKS - SOYAPANGO", title_style))
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
            ['Tiempo Promedio de Cierre', f"{df[df['fecha_cierre'].notna()]['tiempo_cierre_dias'].mean():.1f} días"],
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
            # Gráfica 2: Análisis de Tiempo de Cierre
            story.append(Paragraph("⏱️ ANÁLISIS DE TIEMPO DE CIERRE", heading_style))
            
            df_cerrados = df[df['fecha_cierre'].notna()].copy()
            if len(df_cerrados) > 0:
                fig_tiempo = px.histogram(
                    df_cerrados, x='tiempo_cierre_dias', 
                    title="Distribución de Tiempos de Cierre (días)",
                    labels={'tiempo_cierre_dias': 'Días para Cierre', 'count': 'Frecuencia'}
                )
                fig_tiempo.update_layout(height=400, width=700, showlegend=False)
                
                img_buffer2 = BytesIO()
                fig_tiempo.write_image(img_buffer2, format='png', engine='kaleido')
                img_buffer2.seek(0)
                
                img2 = Image(img_buffer2, width=5*inch, height=2.5*inch)
                story.append(img2)
                story.append(Spacer(1, 20))
            else:
                story.append(Paragraph("No hay datos de fechas de cierre disponibles.", styles['Normal']))
                story.append(Spacer(1, 10))
            
        except Exception as e:
            story.append(Paragraph(f"⚠️ Error generando gráfica de tiempo de cierre: {str(e)}", styles['Normal']))
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
                'tiempo_cierre_dias': 'mean'
            }).round(2).reset_index()
            
            supervisor_data = [['Supervisor', 'Total Casos', 'Tiempo Promedio Cierre (días)']]
            for _, row in supervisor_stats.head(10).iterrows():
                supervisor_data.append([
                    str(row['SUPERVISOR']), 
                    str(row['id_tema']), 
                    str(row['tiempo_cierre_dias']) if pd.notna(row['tiempo_cierre_dias']) else 'N/A'
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
        story.append(Paragraph("Reporte generado automáticamente por Dashboard SOYAPANGO", styles['Italic']))
        
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

def generate_excel_report(df, merged_df, filtros_aplicados=None):
    """Genera un reporte XLSX completo con múltiples hojas basado en los filtros aplicados"""
    try:
        # Crear buffer para el archivo Excel
        excel_buffer = BytesIO()
        
        # Crear workbook con xlsxwriter (sin options que pueden no ser compatibles)
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Definir formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BD',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'num_format': 'dd/mm/yyyy hh:mm',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '0.00',
                'border': 1
            })
            
            # HOJA 1: Datos filtrados principales
            try:
                df_export = clean_dataframe_for_display(df.copy())
                # Convertir fechas problemáticas a string
                for col in df_export.columns:
                    if 'fecha' in col.lower() and df_export[col].dtype == 'object':
                        df_export[col] = df_export[col].astype(str)
                
                df_export.to_excel(writer, sheet_name='Datos_Filtrados', index=False)
                worksheet1 = writer.sheets['Datos_Filtrados']
                
                # Aplicar formato a la hoja 1
                for col_num, value in enumerate(df_export.columns.values):
                    worksheet1.write(0, col_num, value, header_format)
                    
                # Ajustar ancho de columnas
                for i, col in enumerate(df_export.columns):
                    try:
                        max_len = max(df_export[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet1.set_column(i, i, min(max_len, 50))
                    except:
                        worksheet1.set_column(i, i, 15)
            except Exception as e:
                print(f"Error en Hoja 1: {e}")
              # HOJA 2: Análisis por Rutas
            try:
                rutas_analysis = df.groupby('ruta').agg({
                    'id_tema': 'count',
                    'tiempo_cierre_dias': ['mean', 'std', 'min', 'max'],
                    'fecha_cierre': lambda x: x.notna().sum(),
                    'codigo_cliente': 'nunique',
                    'usuario': 'nunique'
                }).round(2)
                
                # Aplanar columnas MultiIndex
                rutas_analysis.columns = ['Total_Registros', 'Tiempo_Cierre_Promedio', 'Tiempo_Cierre_Std', 'Tiempo_Cierre_Min', 'Tiempo_Cierre_Max', 'Registros_Cerrados', 'Clientes_Unicos', 'Usuarios_Activos']
                rutas_analysis = rutas_analysis.reset_index()
                rutas_analysis['Tasa_Cierre'] = (rutas_analysis['Registros_Cerrados'] / rutas_analysis['Total_Registros']) * 100
                rutas_analysis = rutas_analysis.sort_values('Total_Registros', ascending=False)
                
                rutas_analysis.to_excel(writer, sheet_name='Analisis_Rutas', index=False)
                worksheet2 = writer.sheets['Analisis_Rutas']
                
                # Aplicar formato a la hoja 2
                for col_num, value in enumerate(rutas_analysis.columns.values):
                    worksheet2.write(0, col_num, value, header_format)
            except Exception as e:
                print(f"Error en Hoja 2: {e}")
              # HOJA 3: Análisis por Usuarios
            try:
                usuarios_analysis = df.groupby('usuario').agg({
                    'id_tema': 'count',
                    'tiempo_cierre_dias': ['mean', 'std'],
                    'fecha_cierre': lambda x: x.notna().sum(),
                    'ruta': 'nunique',
                    'codigo_cliente': 'nunique'
                }).round(2)
                
                usuarios_analysis.columns = ['Total_Casos', 'Tiempo_Cierre_Promedio', 'Tiempo_Cierre_Std', 'Casos_Cerrados', 'Rutas_Trabajadas', 'Clientes_Atendidos']
                usuarios_analysis = usuarios_analysis.reset_index()
                usuarios_analysis['Tasa_Cierre'] = (usuarios_analysis['Casos_Cerrados'] / usuarios_analysis['Total_Casos']) * 100
                usuarios_analysis = usuarios_analysis.sort_values('Total_Casos', ascending=False)
                
                usuarios_analysis.to_excel(writer, sheet_name='Analisis_Usuarios', index=False)
                worksheet3 = writer.sheets['Analisis_Usuarios']
                
                # Aplicar formato a la hoja 3
                for col_num, value in enumerate(usuarios_analysis.columns.values):
                    worksheet3.write(0, col_num, value, header_format)
            except Exception as e:
                print(f"Error en Hoja 3: {e}")
            
            # HOJA 4: Top Clientes Problemáticos            try:
                df['codigo_cliente_display'] = df['codigo_cliente'].apply(lambda x: f"Cliente-{str(x).zfill(6)}")
                clientes_analysis = df.groupby(['codigo_cliente', 'codigo_cliente_display']).agg({
                    'id_tema': 'count',
                    'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
                    'tiempo_cierre_dias': 'mean',
                    'fecha_cierre': lambda x: x.notna().sum(),
                    'ruta': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
                    'usuario': 'nunique'
                }).round(2).reset_index()
                
                clientes_analysis.columns = ['codigo_cliente', 'codigo_cliente_display', 'total_reportes', 'motivo_principal', 'tiempo_promedio_cierre', 'casos_cerrados', 'ruta_principal', 'usuarios_involucrados']
                clientes_analysis['tasa_cierre'] = (clientes_analysis['casos_cerrados'] / clientes_analysis['total_reportes']) * 100
                clientes_analysis = clientes_analysis.sort_values('total_reportes', ascending=False).head(50)
                
                clientes_export = clientes_analysis[['codigo_cliente_display', 'total_reportes', 'motivo_principal', 'tiempo_promedio_cierre', 'tasa_cierre', 'ruta_principal', 'usuarios_involucrados']].copy()
                clientes_export.columns = ['Cliente', 'Total_Reportes', 'Motivo_Principal', 'Tiempo_Promedio_Cierre_Dias', 'Tasa_Cierre', 'Ruta_Principal', 'Usuarios_Involucrados']
                
                clientes_export.to_excel(writer, sheet_name='Top_Clientes_Problematicos', index=False)
                worksheet4 = writer.sheets['Top_Clientes_Problematicos']
                
                # Aplicar formato a la hoja 4
                for col_num, value in enumerate(clientes_export.columns.values):
                    worksheet4.write(0, col_num, value, header_format)
            except Exception as e:
                print(f"Error en Hoja 4: {e}")
              # HOJA 5: Resumen Ejecutivo
            try:
                resumen_data = {
                    'Metrica': [
                        'Total de Registros',
                        'Rutas Únicas',
                        'Usuarios Activos',
                        'Clientes Únicos',
                        'Tiempo Promedio de Cierre (días)',
                        'Tasa de Cierre Global (%)',
                        'Registros Cerrados',
                        'Fecha de Generación'
                    ],
                    'Valor': [
                        len(df),
                        df['ruta'].nunique(),
                        df['usuario'].nunique(),
                        df['codigo_cliente'].nunique(),
                        round(df[df['fecha_cierre'].notna()]['tiempo_cierre_dias'].mean(), 1) if len(df[df['fecha_cierre'].notna()]) > 0 else 'N/A',
                        round((df['fecha_cierre'].notna().sum() / len(df)) * 100, 1),
                        df['fecha_cierre'].notna().sum(),
                        datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    ]
                }
                
                if filtros_aplicados:
                    resumen_data['Metrica'].extend([
                        'Filtros Aplicados',
                        'Fecha Inicio Filtro',
                        'Fecha Fin Filtro',
                        'Ruta Filtrada',
                        'Usuario Filtrado'
                    ])
                    resumen_data['Valor'].extend([
                        'Sí',
                        str(filtros_aplicados.get('fecha_inicio', 'N/A')),
                        str(filtros_aplicados.get('fecha_fin', 'N/A')),
                        str(filtros_aplicados.get('ruta', 'Todas')),
                        str(filtros_aplicados.get('usuario', 'Todos'))
                    ])
                
                resumen_df = pd.DataFrame(resumen_data)
                resumen_df.to_excel(writer, sheet_name='Resumen_Ejecutivo', index=False)
                worksheet5 = writer.sheets['Resumen_Ejecutivo']
                
                # Aplicar formato a la hoja 5
                for col_num, value in enumerate(resumen_df.columns.values):
                    worksheet5.write(0, col_num, value, header_format)
            except Exception as e:
                print(f"Error en Hoja 5: {e}")
            
            # Ajustar ancho de columnas para todas las hojas
            try:
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.set_column('A:Z', 15)
            except Exception as e:
                print(f"Error ajustando columnas: {e}")
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue()
        
    except Exception as e:
        # Si hay error, crear un archivo simple con el error
        simple_buffer = BytesIO()
        error_df = pd.DataFrame({
            'Error': [f"Error generando archivo XLSX: {str(e)}"],
            'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Detalle': ['Por favor, verifique que xlsxwriter esté instalado correctamente']
        })
        
        try:
            with pd.ExcelWriter(simple_buffer, engine='xlsxwriter') as writer:
                error_df.to_excel(writer, sheet_name='Error', index=False)
        except:
            # Si incluso esto falla, usar openpyxl como fallback
            with pd.ExcelWriter(simple_buffer, engine='openpyxl') as writer:
                error_df.to_excel(writer, sheet_name='Error', index=False)
        
        simple_buffer.seek(0)
        return simple_buffer.getvalue()

# Función principal mejorada
def main():
    # Título principal
    st.markdown('<h1 class="main-header">Seguimiento Feedbacks - DS00</h1>', unsafe_allow_html=True)
      # Cargar datos
    with st.spinner('🔄 Cargando datos...'):
        load_result = load_data()
        
        if load_result is None or len(load_result) != 4:
            st.error("❌ No se pudieron cargar los datos. Verifica que los archivos Excel estén en el directorio correcto.")
            return
            
        feedbacks_df, rutas_df, merged_df, data_quality = load_result
    
    if feedbacks_df is None:
        st.error("❌ No se pudieron cargar los datos. Verifica que los archivos Excel estén en el directorio correcto.")
        return    # Se eliminó la sección de resumen de calidad de datos en sidebar
      # Sidebar con filtros mejorados
    st.sidebar.markdown("## 🔧 Centro de Control y Filtros")
      # === NUEVA SECCIÓN: GESTIÓN AUTOMÁTICA DE BASE DE DATOS DE RUTAS ===
    st.sidebar.markdown("### 📂 Sistema Automático de BD de Rutas")
    with st.sidebar.expander("🔍 BDs Cargadas Automáticamente", expanded=False):
        st.markdown("""
        **🚀 Sistema Inteligente:**
        El sistema detecta y carga automáticamente todas las BDs de rutas disponibles en el directorio.
        """)
        
        # Mostrar información de las BDs cargadas automáticamente
        if 'rutas_databases_info' in st.session_state:
            info = st.session_state['rutas_databases_info']
            st.metric("📊 Total BDs Detectadas", info['total_databases'])
            
            # Mostrar lista de BDs disponibles
            st.markdown("**📋 BDs Automáticamente Detectadas:**")
            available_months = info['available_months']
            
            # BD Default
            st.markdown("• ✅ **BD_Rutas.xlsx** (Default)")
            
            # BDs por mes detectadas automáticamente
            meses_spanish = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            for mes in meses_spanish:
                if mes in available_months:
                    st.markdown(f"• ✅ **{mes}** (Auto-detectada)")
                else:
                    st.markdown(f"• ❌ {mes} (No encontrada)")
        else:
            st.info("⏳ Cargando información de BDs...")
          # Información sobre patrones de búsqueda
        st.markdown("---")
        st.markdown("**ℹ️ Patrones de Archivos Soportados:**")
        st.markdown("""
        El sistema busca automáticamente archivos con estos nombres:
        
        • `BD_Rutas_Enero.xlsx`, `BD_Rutas_enero.xlsx`
        • `BD_Rutas_Febrero.xlsx`, `BD_Rutas_febrero.xlsx`
        • `BD_Rutas_Marzo.xlsx`, etc.
        • `BD_Rutas_Jan.xlsx`, `BD_Rutas_Feb.xlsx`, etc.
        • Cualquier variación en mayúsculas/minúsculas
        
        **Solo coloca los archivos en el directorio y el sistema los detectará automáticamente.**
        """)
        
        # Opción manual para casos especiales
        st.markdown("---")
        st.markdown("**🔧 Carga Manual (Opcional):**")
        mes_manual = st.selectbox(
            "Mes para carga manual:",
            ['Ninguno'] + ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            help="Solo usar si necesitas cargar una BD con nombre diferente"
        )
        
        if mes_manual != 'Ninguno':
            uploaded_rutas = st.file_uploader(
                f"📋 Subir BD Rutas para {mes_manual}",
                type=['xlsx', 'xls'],
                help=f"Carga manual de BD para {mes_manual} (sobrescribirá la auto-detectada)",
                key=f"upload_manual_{mes_manual}"
            )
            
            if uploaded_rutas is not None:
                try:
                    rutas_df_manual = pd.read_excel(uploaded_rutas)
                    required_cols = ['RUTA', 'SUPERVISOR', 'CONTRATISTA']
                    missing_cols = [col for col in required_cols if col not in rutas_df_manual.columns]
                    
                    if not missing_cols:
                        st.session_state[f'rutas_df_{mes_manual}'] = rutas_df_manual
                        st.success(f"✅ BD manual para {mes_manual} cargada exitosamente!")
                        st.info(f"📊 Rutas cargadas: {len(rutas_df_manual)}")
                        
                        # Actualizar info en session_state
                        if 'rutas_databases_info' in st.session_state:
                            if mes_manual not in st.session_state['rutas_databases_info']['available_months']:
                                st.session_state['rutas_databases_info']['available_months'].append(mes_manual)
                                st.session_state['rutas_databases_info']['total_databases'] += 1
                    else:
                        st.error(f"❌ Faltan columnas requeridas: {missing_cols}")
                except Exception as e:
                    st.error(f"❌ Error al procesar archivo: {str(e)}")
        
        # Botón para recargar BDs automáticamente
        if st.button("🔄 Recargar BDs Automáticamente"):
            # Limpiar cache y recargar
            st.cache_data.clear()
            if 'rutas_databases_loaded' in st.session_state:
                del st.session_state['rutas_databases_loaded']
            st.experimental_rerun()
        
        # Botón para limpiar todas las BDs personalizadas
        if st.button("🧹 Limpiar BDs Personalizadas"):
            keys_to_remove = [key for key in st.session_state.keys() if key.startswith('rutas_df_')]
            for key in keys_to_remove:
                del st.session_state[key]
            if 'rutas_databases_loaded' in st.session_state:
                del st.session_state['rutas_databases_loaded']
            if 'rutas_databases_info' in st.session_state:
                del st.session_state['rutas_databases_info']
            st.success("✅ BDs personalizadas eliminadas. Sistema volverá a cargar automáticamente.")
            st.experimental_rerun()
    
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
    
    # NUEVOS FILTROS: Mes y Semana - Ordenar meses cronológicamente
    meses_ordenados = feedbacks_df.groupby(['mes', 'mes_nombre']).size().reset_index().sort_values('mes')['mes_nombre'].tolist()
    meses_disponibles = ['Todos'] + meses_ordenados
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
    else:        contratista_seleccionado = 'Todos'
      # === SELECCIÓN AUTOMÁTICA DE BD DE RUTAS BASADA EN FILTROS (MEJORADA) ===
    def get_optimal_rutas_db(df_filtrado, mes_seleccionado):
        """
        Selecciona la BD de rutas más apropiada basada en los filtros aplicados
        Ahora usa el sistema automático de carga de BDs
        """
        # Si el usuario seleccionó un mes específico, usar esa BD si está disponible
        if mes_seleccionado != 'Todos':
            # Mapear nombres de meses a claves
            mes_map = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            
            mes_esp = mes_map.get(mes_seleccionado, mes_seleccionado)
            if f'rutas_df_{mes_esp}' in st.session_state:
                st.sidebar.info(f"🎯 Usando BD Rutas específica para {mes_esp}")
                return st.session_state[f'rutas_df_{mes_esp}'].copy()
        
        # Auto-detectar el mes predominante en los datos filtrados
        if not df_filtrado.empty:
            mes_predominante = df_filtrado['mes_nombre'].mode()
            if not mes_predominante.empty:
                mes_pred = mes_predominante.iloc[0]
                mes_map = {
                    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
                }
                mes_pred_esp = mes_map.get(mes_pred, mes_pred)
                
                if f'rutas_df_{mes_pred_esp}' in st.session_state:
                    st.sidebar.info(f"🔍 Auto-detectado: Usando BD Rutas para {mes_pred_esp}")
                    return st.session_state[f'rutas_df_{mes_pred_esp}'].copy()
        
        # Fallback a BD por defecto
        return rutas_df
    
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
      # ========== SELECCIÓN INTELIGENTE DE BD RUTAS ==========
    # Obtener la BD de rutas óptima basada en los filtros aplicados
    rutas_df_optimizada = get_optimal_rutas_db(df_filtrado, mes_seleccionado)
      # Mostrar información de la BD de rutas activa
    with st.sidebar.expander("📊 BD Rutas Activa", expanded=False):
        st.metric("🗂️ Total Rutas", rutas_df_optimizada['RUTA'].nunique())
        st.metric("👨‍💼 Supervisores", rutas_df_optimizada['SUPERVISOR'].nunique())
        st.metric("🏢 Contratistas", rutas_df_optimizada['CONTRATISTA'].nunique())
        
        # Rutas con contratistas reales (sin Dummy)
        rutas_reales = rutas_df_optimizada[
            (rutas_df_optimizada['CONTRATISTA'].notna()) & 
            (~rutas_df_optimizada['CONTRATISTA'].str.contains('Dummy', case=False, na=False))
        ]
        st.metric("✅ Rutas Activas", rutas_reales['RUTA'].nunique())
        
        # Detectar tipo de BD en uso
        bd_type_detected = False
        
        # Verificar si es una BD específica de mes
        meses_disponibles = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                           'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        for mes in meses_disponibles:
            if f'rutas_df_{mes}' in st.session_state:
                if st.session_state[f'rutas_df_{mes}'].equals(rutas_df_optimizada):
                    if mes in st.session_state.get('rutas_databases_info', {}).get('available_months', []):
                        st.success(f"🎯 BD Auto-detectada: {mes}")
                    else:
                        st.success(f"🔧 BD Manual: {mes}")
                    bd_type_detected = True
                    break
        
        if not bd_type_detected:
            st.info("📂 BD Default (BD_Rutas.xlsx)")
        
        # Exportar BD actual
        if st.button("📤 Exportar BD Activa"):
            try:
                csv_data = rutas_df_optimizada.to_csv(index=False)
                st.download_button(
                    label="💾 Descargar BD Activa (CSV)",
                    data=csv_data,
                    file_name=f"BD_Rutas_Activa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.success("✅ BD lista para descargar")
            except Exception as e:
                st.error(f"❌ Error al exportar: {str(e)}")
    
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
        with st.spinner("📊 Generando PDF con gráficas..."):
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
    
    # Botón para reporte XLSX con múltiples hojas
    if st.sidebar.button("📊 Generar Reporte XLSX"):
        with st.spinner("📊 Generando archivo XLSX con múltiples hojas..."):
            try:
                # Preparar información de filtros aplicados para incluir en el reporte
                filtros_info = {
                    'fecha_inicio': str(fecha_inicio),
                    'fecha_fin': str(fecha_fin),
                    'ruta': ruta_seleccionada,
                    'usuario': usuario_seleccionado,
                    'mes': mes_seleccionado,
                    'semana': semana_seleccionada,
                    'trimestre': trimestre_seleccionado,
                    'supervisor': supervisor_seleccionado,
                    'contratista': contratista_seleccionado
                }
                
                xlsx_data = generate_excel_report(df_filtrado, merged_df_filtrado, filtros_info)
                
                st.sidebar.download_button(
                    label="📋 Descargar Reporte XLSX",
                    data=xlsx_data,
                    file_name=f"reporte_feedbacks_XLSX_{tipo_reporte.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.sidebar.success("✅ Reporte XLSX generado exitosamente!")
            except Exception as e:
                st.sidebar.error(f"❌ Error generando XLSX: {str(e)}")
                st.sidebar.info("💡 Asegúrese de que xlsxwriter esté instalado correctamente.")
    
    # Información sobre los reportes
    with st.sidebar.expander("ℹ️ Información sobre Reportes"):
        st.write("""
        **Reporte TXT**: Archivo de texto plano con estadísticas y análisis detallado.
        
        **Reporte PDF**: Documento profesional con gráficas, tablas y análisis visual completo.
        
        **Reporte XLSX**: Archivo Excel con múltiples hojas de análisis:
        - Datos filtrados principales
        - Análisis por rutas
        - Análisis por usuarios
        - Top clientes problemáticos
        - Análisis temporal
        - Supervisores y contratistas
        - Resumen ejecutivo
        
        - Incluye gráficas de barras
        - Histogramas de distribución
        - Tablas con datos clave
        - Análisis de supervisores
        - Insights principales
        """)
    
    # Métricas KPI mejoradas
    create_advanced_kpi_metrics(df_filtrado, merged_df_filtrado)    # Menú de navegación principal
    selected = option_menu(
        menu_title=None,
        options=[
            "🏠 Resumen General", 
            "📈 Análisis Temporal", 
            "🚚 Análisis por Rutas", 
            "👨‍💼 Supervisores y Contratistas",
            "👥 Análisis de Personal", 
            "🎯 Análisis de Rendimiento", 
            "🏪 Análisis de Clientes",
            "📋 Datos Detallados"
        ],
        icons=["house", "graph-up", "truck", "person-badge", "people", "target", "shop", "table"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",    )    # Contenido según la selección    
    if selected == "🏠 Resumen General":
        show_general_overview(df_filtrado, merged_df_filtrado)
    elif selected == "📈 Análisis Temporal":
        show_temporal_analysis(df_filtrado, merged_df_filtrado, rutas_df_optimizada)
    elif selected == "🚚 Análisis por Rutas":
        show_routes_analysis(df_filtrado, merged_df_filtrado)    
    elif selected == "👨‍💼 Supervisores y Contratistas":
        show_supervisors_contractors_analysis(df_filtrado, merged_df_filtrado, rutas_df_optimizada)
    elif selected == "👥 Análisis de Personal":
        show_personnel_analysis(df_filtrado, merged_df_filtrado)
    elif selected == "🎯 Análisis de Rendimiento":
        show_performance_analysis(df_filtrado)
    elif selected == "🏪 Análisis de Clientes":
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
        'tiempo_cierre_dias': 'mean'
    }).round(2).reset_index()
    rutas_respuestas.columns = ['ruta', 'total_respuestas', 'tiempo_promedio_cierre']
    rutas_respuestas = rutas_respuestas.sort_values('total_respuestas', ascending=False).head(20)
    fig_rutas = px.scatter(
        rutas_respuestas,
        x='total_respuestas',
        y='tiempo_promedio_cierre',
        size='total_respuestas',
        hover_data=['ruta'],
        title="🚚 Rutas: Cantidad vs Tiempo de Cierre (Top 20)",
        color='tiempo_promedio_cierre',
        color_continuous_scale='RdYlBu_r',
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
        marker=dict(size=15, color='#1f77b4', line=dict(width=2, color='white')),        text=registros_mes['total_registros'],        texttemplate='<b>%{text}</b>',
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
        marker=dict(size=15, color='#ff7f0e', line=dict(width=2, color='white')),        text=registros_mes['total_cierres'],
        texttemplate='<b>%{text}</b>',        textposition='bottom center',
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
            y=1.02,            xanchor="right",
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
        'tiempo_cierre_dias': 'mean',
        'ruta': 'nunique'
    }).round(2).reset_index()
    usuarios_activos.columns = ['usuario', 'total_registros', 'tiempo_promedio_cierre', 'rutas_cubiertas']
    usuarios_activos = usuarios_activos.sort_values('total_registros', ascending=False).head(15)
    fig_usuarios = px.bar(
        usuarios_activos,
        x='total_registros',
        y='usuario',
        orientation='h',
        title="👥 Top 15 Usuarios Más Activos",
        color='tiempo_promedio_cierre',
        color_continuous_scale='plasma_r',
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
      # Quinta fila - Análisis de supervisores (si disponible)
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
            'tiempo_cierre_dias': 'mean',
            'ruta': 'nunique'
        }).round(2).reset_index()
        supervisores_data.columns = ['supervisor', 'total_casos', 'tiempo_promedio_cierre', 'rutas_supervisadas']
        supervisores_data = supervisores_data.sort_values('total_casos', ascending=False).head(15)
        fig_supervisores = px.scatter(
            supervisores_data,
            x='total_casos',
            y='tiempo_promedio_cierre',
            size='rutas_supervisadas',
            hover_data=['supervisor'],
            title="👨‍💼 Supervisores: Casos vs Tiempo de Cierre",
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
            'tiempo_cierre_dias': 'mean'
        }).round(2).reset_index()
        supervisor_cierres.columns = ['supervisor', 'total_cierres', 'tiempo_promedio_cierre']
        supervisor_cierres = supervisor_cierres.sort_values('total_cierres', ascending=False).head(10)
        fig_supervisor_cierres = px.bar(
            supervisor_cierres,
            x='total_cierres',
            y='supervisor',
            orientation='h',
            title="👨‍💼 Top 10 Supervisores con Más Cierres",
            color='tiempo_promedio_cierre',
            color_continuous_scale='viridis_r',
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

def show_temporal_analysis(df, merged_df, rutas_df):
    """Muestra análisis temporal mejorado y completo"""
    st.subheader("📅 Análisis Temporal Profundo y Detallado")
    
    # === SECCIÓN 1: EVOLUCIÓN TEMPORAL MULTI-NIVEL ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Evolución Temporal Multi-Nivel</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Análisis temporal por múltiples dimensiones
    temporal_analysis = df.groupby(['mes', 'mes_nombre']).agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'std', 'min', 'max'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique',
        'usuario': 'nunique',
        'ruta': 'nunique'
    }).round(2)
    
    temporal_analysis.columns = ['Total_Registros', 'Tiempo_Cierre_Promedio', 'Tiempo_Cierre_Std', 'Tiempo_Cierre_Min', 'Tiempo_Cierre_Max', 
                                'Total_Cierres', 'Clientes_Unicos', 'Usuarios_Activos', 'Rutas_Activas']
    temporal_analysis = temporal_analysis.reset_index()
    temporal_analysis['Tasa_Cierre'] = (temporal_analysis['Total_Cierres'] / temporal_analysis['Total_Registros']) * 100
    temporal_analysis = temporal_analysis.sort_values('mes')
    
    # Gráfico de líneas múltiples para evolución temporal
    fig_evolution = go.Figure()
    
    # Línea principal - Total de registros
    fig_evolution.add_trace(go.Scatter(
        x=temporal_analysis['mes_nombre'],
        y=temporal_analysis['Total_Registros'],
        mode='lines+markers+text',
        name='📊 Total Registros',
        line=dict(color='#FF6B6B', width=4),        marker=dict(size=10, color='#FF6B6B'),        text=temporal_analysis['Total_Registros'],
        textposition='top center',
        textfont=dict(size=12, color='white', family='Arial Black'),
        yaxis='y1'
    ))
      # Línea secundaria - Tasa de cierre
    fig_evolution.add_trace(go.Scatter(
        x=temporal_analysis['mes_nombre'],
        y=temporal_analysis['Tasa_Cierre'],
        mode='lines+markers+text',
        name='✅ Tasa Cierre (%)',
        line=dict(color='#4ECDC4', width=3, dash='dash'),
        marker=dict(size=8, color='#4ECDC4'),        text=temporal_analysis['Tasa_Cierre'].round(1),
        textposition='bottom center',
        textfont=dict(size=10, color='white')    ))
    
    # Línea terciaria - Clientes únicos (usando yaxis principal con escala normalizada)
    fig_evolution.add_trace(go.Scatter(
        x=temporal_analysis['mes_nombre'],
        y=temporal_analysis['Clientes_Unicos'],
        mode='lines+markers',
        name='👥 Clientes Únicos',
        line=dict(color='#FFA726', width=2),
        marker=dict(size=6, color='#FFA726')
    ))
    fig_evolution.update_layout(        
        title='📈 Evolución Temporal Multi-Dimensional de Registros',
        xaxis_title='<b>Mes</b>',
        yaxis_title='<b>Total de Registros</b>',
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # === SECCIÓN 2: ANÁLISIS DE PATRONES SEMANALES Y ESTACIONALES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🗓️ Análisis de Patrones Semanales y Estacionales</h3>
        </div>        """, 
        unsafe_allow_html=True
    )
    
    # Análisis por días de la semana
    df['fecha_parsed'] = pd.to_datetime(df['fecha_registro'], errors='coerce')
    df['dia_semana_num'] = df['fecha_parsed'].dt.dayofweek
    df['dia_semana_nombre'] = df['fecha_parsed'].dt.day_name()
    dias_analysis = df.groupby(['dia_semana_num', 'dia_semana_nombre']).agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': 'mean',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2).reset_index()
    dias_analysis.columns = ['dia_num', 'dia_nombre', 'total_registros', 'tiempo_promedio_cierre', 'total_cierres']
    dias_analysis['tasa_cierre'] = (dias_analysis['total_cierres'] / dias_analysis['total_registros']) * 100
    dias_analysis = dias_analysis.sort_values('dia_num')
    
    # Gráfico polar para días de la semana
    fig_polar = go.Figure()
    
    fig_polar.add_trace(go.Scatterpolar(
        r=dias_analysis['total_registros'],
        theta=dias_analysis['dia_nombre'],
        fill='toself',
        fillcolor='rgba(255, 107, 107, 0.3)',
        line=dict(color='#FF6B6B', width=3),        marker=dict(size=8, color='#FF6B6B'),        
        text=dias_analysis['total_registros'],
        textposition='middle center',        
        textfont=dict(size=12, color='white', family='Arial Black'),
        name='Registros por Día'
    ))    
    fig_polar.update_layout(
        title='🗓️ Distribución Polar de Registros por Día de la Semana',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    
    st.plotly_chart(fig_polar, use_container_width=True)
    
    # === SECCIÓN 3: ANÁLISIS DE VELOCIDAD DE RESOLUCIÓN ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⚡ Análisis de Velocidad de Resolución</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )    # Calcular tiempo de resolución cuando hay fecha de cierre
    df_cerrados = df[df['fecha_cierre'].notna()].copy()
    if not df_cerrados.empty:
        df_cerrados['fecha_registro_parsed'] = pd.to_datetime(df_cerrados['fecha_registro'], errors='coerce')
        df_cerrados['fecha_cierre_parsed'] = pd.to_datetime(df_cerrados['fecha_cierre'], errors='coerce')
        df_cerrados['dias_resolucion'] = (df_cerrados['fecha_cierre_parsed'] - df_cerrados['fecha_registro_parsed']).dt.days
        
        # Agregar columnas de mes para análisis temporal
        df_cerrados['mes'] = df_cerrados['fecha_registro_parsed'].dt.month
        df_cerrados['mes_nombre'] = df_cerrados['fecha_registro_parsed'].dt.month_name()
          # Filtrar valores razonables (entre 0 y 365 días)
        df_cerrados = df_cerrados[(df_cerrados['dias_resolucion'] >= 0) & (df_cerrados['dias_resolucion'] <= 365)]
        if not df_cerrados.empty:
            resolucion_analysis = df_cerrados.groupby(['mes', 'mes_nombre']).agg({
                'dias_resolucion': ['mean', 'median', 'std', 'min', 'max', 'count']
            }).round(2)
            
            resolucion_analysis.columns = ['Dias_Promedio', 'Dias_Mediana', 'Dias_Std', 'Dias_Min', 'Dias_Max', 'Total_Casos']
            resolucion_analysis = resolucion_analysis.reset_index()
            resolucion_analysis = resolucion_analysis.sort_values('mes')
            
            # Gráfico de cajas para mostrar distribución de tiempos
            fig_resolution = go.Figure()
            
            for mes in resolucion_analysis['mes_nombre']:
                datos_mes = df_cerrados[df_cerrados['mes_nombre'] == mes]['dias_resolucion']
                
                fig_resolution.add_trace(go.Box(
                    y=datos_mes,
                    name=mes,
                    boxpoints='outliers',
                    marker=dict(color='#4ECDC4'),
                    line=dict(color='#FF6B6B', width=2),
                    fillcolor='rgba(78, 205, 196, 0.3)'                ))
            
            fig_resolution.update_layout(
                title='⏱️ Distribución de Tiempos de Cierre por Mes',
                xaxis_title='<b>Mes</b>',
                yaxis_title='<b>Días para Cierre</b>',
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12)
            )
            
            st.plotly_chart(fig_resolution, use_container_width=True)
            
            # KPIs de tiempo de cierre
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                tiempo_promedio = df_cerrados['dias_resolucion'].mean()
                st.metric(
                    "⏱️ Tiempo Promedio",
                    f"{tiempo_promedio:.1f} días"
                )
            
            with col2:
                tiempo_mediana = df_cerrados['dias_resolucion'].median()
                st.metric(
                    "📊 Tiempo Mediana",
                    f"{tiempo_mediana:.1f} días"
                )
            
            with col3:
                casos_rapidos = len(df_cerrados[df_cerrados['dias_resolucion'] <= 7])
                porcentaje_rapidos = (casos_rapidos / len(df_cerrados)) * 100
                st.metric(
                    "🚀 Cierre Rápido",
                    f"{porcentaje_rapidos:.1f}%",
                    "≤ 7 días"
                )
            
            with col4:
                casos_lentos = len(df_cerrados[df_cerrados['dias_resolucion'] > 30])
                porcentaje_lentos = (casos_lentos / len(df_cerrados)) * 100
                st.metric(
                    "🐌 Cierre Lento",
                    f"{porcentaje_lentos:.1f}%",
                    "> 30 días"
                )
                
            # === NUEVA SECCIÓN: ANÁLISIS DE TIEMPO DE CIERRE POR SUPERVISOR ===
            if 'SUPERVISOR' in merged_df.columns:
                st.markdown(
                    """
                    <div class="analysis-card">
                        <h3 style="color: white; margin: 0;">👨‍💼 Tiempo Promedio de Cierre por Supervisor</h3>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Fusionar df_cerrados con merged_df para obtener supervisores
                df_cerrados_supervisor = df_cerrados.merge(
                    merged_df[['ruta', 'SUPERVISOR']].drop_duplicates(), 
                    on='ruta', 
                    how='left'
                )
                
                # Filtrar solo registros con supervisor asignado
                df_cerrados_supervisor = df_cerrados_supervisor[df_cerrados_supervisor['SUPERVISOR'].notna()]
                
                if not df_cerrados_supervisor.empty:
                    supervisor_cierre = df_cerrados_supervisor.groupby('SUPERVISOR').agg({
                        'dias_resolucion': ['mean', 'median', 'count']
                    }).round(2)
                    
                    supervisor_cierre.columns = ['Tiempo_Promedio', 'Tiempo_Mediana', 'Total_Casos_Cerrados']
                    supervisor_cierre = supervisor_cierre.reset_index()
                    supervisor_cierre = supervisor_cierre.sort_values('Tiempo_Promedio', ascending=True)
                    
                    # Gráfico de barras para tiempo promedio por supervisor
                    fig_supervisor_tiempo = px.bar(
                        supervisor_cierre.head(15),
                        x='Tiempo_Promedio',
                        y='SUPERVISOR',
                        orientation='h',
                        title='⏱️ Tiempo Promedio de Cierre por Supervisor (Top 15)',
                        color='Total_Casos_Cerrados',
                        color_continuous_scale='RdYlGn_r',
                        height=600,
                        text='Tiempo_Promedio'
                    )
                    
                    fig_supervisor_tiempo.update_traces(
                        texttemplate='<b>%{text:.1f} días</b>',
                        textposition='outside',
                        marker_line_width=1,
                        marker_line_color='white'
                    )                    
                    fig_supervisor_tiempo.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        margin=dict(l=200, r=50, t=80, b=50),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white', size=12),
                        xaxis_title="<b>Días Promedio para Cierre</b>",
                        yaxis_title="<b>Supervisor</b>"
                    )
                    
                    st.plotly_chart(fig_supervisor_tiempo, use_container_width=True)
                    
                    # Tabla detallada de supervisores
                    st.markdown("#### 📋 Detalle de Tiempo de Cierre por Supervisor")
                    supervisor_cierre_display = supervisor_cierre.copy()
                    supervisor_cierre_display.columns = ['Supervisor', 'Tiempo Promedio (días)', 'Tiempo Mediana (días)', 'Casos Cerrados']
                    st.dataframe(clean_dataframe_for_display(supervisor_cierre_display), use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ No hay datos suficientes para analizar tiempo de cierre por supervisor")
        else:
            st.warning("⚠️ No hay datos suficientes para calcular tiempos de cierre.")
    else:
        st.warning("⚠️ No hay casos cerrados para analizar tiempos de cierre.")
    
    # === SECCIÓN 4: INSIGHTS AUTOMÁTICOS ===
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h4 style="color: white; margin: 0;">🧠 Insights Temporales Automáticos</h4>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            📈 <strong>Mes más activo:</strong> {temporal_analysis.loc[temporal_analysis['Total_Registros'].idxmax(), 'mes_nombre']} 
            ({temporal_analysis['Total_Registros'].max()} registros)
        </p>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            ✅ <strong>Mejor tasa de cierre:</strong> {temporal_analysis.loc[temporal_analysis['Tasa_Cierre'].idxmax(), 'mes_nombre']} 
            ({temporal_analysis['Tasa_Cierre'].max():.1f}%)
        </p>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            👥 <strong>Mayor diversidad de clientes:</strong> {temporal_analysis.loc[temporal_analysis['Clientes_Unicos'].idxmax(), 'mes_nombre']} 
            ({temporal_analysis['Clientes_Unicos'].max()} clientes únicos)
        </p>
    </div>    """, unsafe_allow_html=True)
    
    # === SECCIÓN 5: ANÁLISIS DETALLADO MENSUAL ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Análisis Detallado Mensual</h3>
        </div>
    """, 
        unsafe_allow_html=True
    )
    monthly_detailed = df.groupby(['mes', 'mes_nombre']).agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'sum'],
        'usuario': 'nunique',
        'ruta': 'nunique',  # Rutas que tuvieron actividad ese mes
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2)
    
    monthly_detailed.columns = ['Total_Registros', 'Tiempo_Cierre_Promedio', 'Tiempo_Cierre_Total', 'Usuarios_Unicos', 'Rutas_Activas', 'Total_Cierres']
    monthly_detailed = monthly_detailed.reset_index()
    monthly_detailed = monthly_detailed.sort_values('mes')
    fig_monthly_bars = px.bar(
        monthly_detailed,
        x='mes_nombre',
        y='Total_Registros',
        title="📊 Registros Mensuales con Tiempo Promedio de Cierre",
        text='Total_Registros',
        color='Tiempo_Cierre_Promedio',
        color_continuous_scale='viridis_r',
        height=500
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
    
    # === SECCIÓN NUEVA: ANÁLISIS DE PICOS Y VALLES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📈 Análisis de Picos y Valles de Actividad</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Crear análisis de variabilidad
    temporal_analysis_sorted = temporal_analysis.sort_values('mes')
    temporal_analysis_sorted['cambio_mensual'] = temporal_analysis_sorted['Total_Registros'].pct_change() * 100
    temporal_analysis_sorted['categoria_cambio'] = temporal_analysis_sorted['cambio_mensual'].apply(
        lambda x: '📈 Aumento Significativo' if x > 20 else 
                  '📊 Aumento Moderado' if x > 0 else 
                  '📉 Disminución Moderada' if x > -20 else 
                  '⚠️ Disminución Significativa' if pd.notna(x) else '🔄 Primer Mes'
    )
    
    # Gráfico de cascada para mostrar cambios mensuales
    fig_waterfall = go.Figure()
    
    # Colores para diferentes tipos de cambio
    colores = []
    for cambio in temporal_analysis_sorted['cambio_mensual']:
        if pd.isna(cambio):
            colores.append('#4ECDC4')  # Primer mes
        elif cambio > 20:
            colores.append('#FF6B6B')  # Aumento significativo
        elif cambio > 0:
            colores.append('#FFA726')  # Aumento moderado
        elif cambio > -20:
            colores.append('#FFD54F')  # Disminución moderada
        else:
            colores.append('#FF5722')  # Disminución significativa
    
    fig_waterfall.add_trace(go.Bar(
        x=temporal_analysis_sorted['mes_nombre'],
        y=temporal_analysis_sorted['Total_Registros'],
        text=[f"<b>{val}</b><br>{cat}" for val, cat in zip(
            temporal_analysis_sorted['Total_Registros'],
        temporal_analysis_sorted['categoria_cambio']        )],        
        textposition='outside',
        textfont=dict(size=10, color='white'),
        marker=dict(color=colores, line=dict(width=2, color='white')),
        name='Registros Mensuales'
    ))    
    fig_waterfall.update_layout(
        title='📊 Análisis de Picos y Valles - Registros Mensuales con Categorización',
        xaxis_title='<b>Mes</b>',
        yaxis_title='<b>Total de Registros</b>',
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        showlegend=False
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Tabla de análisis de cambios
    cambios_df = temporal_analysis_sorted[['mes_nombre', 'Total_Registros', 'cambio_mensual', 'categoria_cambio']].copy()
    cambios_df['cambio_mensual'] = cambios_df['cambio_mensual'].fillna(0).round(1)
    cambios_df.columns = ['Mes', 'Total Registros', 'Cambio %', 'Categoría']
    
    st.markdown("#### 📊 Resumen de Cambios Mensuales")
    st.dataframe(clean_dataframe_for_display(cambios_df), use_container_width=True)
      # === SECCIÓN 6: ANÁLISIS DE EFICIENCIA TEMPORAL ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⚡ Análisis de Eficiencia Temporal</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )    # Crear métrica de eficiencia: Registros por Usuario por Mes
    eficiencia_temporal = monthly_detailed.copy()
    eficiencia_temporal['Eficiencia'] = eficiencia_temporal['Total_Registros'] / eficiencia_temporal['Usuarios_Unicos']
      # Calcular el número total de rutas disponibles en la base de datos
    total_rutas_disponibles = rutas_df['RUTA'].nunique()
    # Cobertura = % de rutas que tuvieron actividad vs total de rutas disponibles
    eficiencia_temporal['Cobertura'] = eficiencia_temporal['Rutas_Activas'] / total_rutas_disponibles * 100
    
    # Gráfico combinado de eficiencia
    fig_efficiency = go.Figure()
    
    # Barras de eficiencia (registros por usuario)
    fig_efficiency.add_trace(go.Bar(
        x=eficiencia_temporal['mes_nombre'],
        y=eficiencia_temporal['Eficiencia'],
        name='📊 Registros por Usuario',
        text=eficiencia_temporal['Eficiencia'].round(1),
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker=dict(color='#4ECDC4', line=dict(width=2, color='white')),
        yaxis='y'
    ))
      # Línea de cobertura de rutas
    fig_efficiency.add_trace(go.Scatter(
        x=eficiencia_temporal['mes_nombre'],
        y=eficiencia_temporal['Cobertura'],
        mode='lines+markers+text',
        name='📍 Cobertura de Rutas (%)',
        text=eficiencia_temporal['Cobertura'].round(1),
        texttemplate='%{text:.1f}%',
        textposition='top center',
        line=dict(color='#FF6B6B', width=4),
        marker=dict(size=10, color='#FF6B6B')
    ))      
    fig_efficiency.update_layout(
        title='⚡ Eficiencia Temporal: Productividad vs Cobertura',
        xaxis_title='<b>Mes</b>',
        yaxis_title='<b>Registros por Usuario</b>',
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    # KPIs de eficiencia
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        eficiencia_promedio = eficiencia_temporal['Eficiencia'].mean()
        st.metric(
            "📊 Eficiencia Promedio",
            f"{eficiencia_promedio:.1f}",
            "registros/usuario"
        )
    
    with col2:
        mejor_mes_eficiencia = eficiencia_temporal.loc[eficiencia_temporal['Eficiencia'].idxmax(), 'mes_nombre']
        mejor_eficiencia = eficiencia_temporal['Eficiencia'].max()
        st.metric(
            "🏆 Mejor Eficiencia",
            f"{mejor_eficiencia:.1f}",
            f"en {mejor_mes_eficiencia}"
        )
    
    with col3:
        cobertura_promedio = eficiencia_temporal['Cobertura'].mean()
        st.metric(
            "📍 Cobertura Promedio",
            f"{cobertura_promedio:.1f}%",
            "de rutas activas"
        )
    with col4:
        mejor_mes_cobertura = eficiencia_temporal.loc[eficiencia_temporal['Cobertura'].idxmax(), 'mes_nombre']
        mejor_cobertura = eficiencia_temporal['Cobertura'].max()
        st.metric(
            "🎯 Mejor Cobertura",
            f"{mejor_cobertura:.1f}%",
            f"en {mejor_mes_cobertura}"
        )    # === SECCIÓN 7: MAPA DE CALOR DE ACTIVIDAD POR DÍA Y HORA ===
    st.markdown("---")
    st.markdown("### ⏰ Patrones Temporales Avanzados")
    add_day_hour_heatmap(df)
      # === SECCIÓN 9: ANÁLISIS DE CLIENTES RECURRENTES ===
    st.markdown("---")
    st.markdown("### 🔄 Análisis de Patrones de Clientes")
    add_recurrence_analysis(df)
    
    # === SECCIÓN 10: ANÁLISIS DE PROBLEMAS Y RESOLUCIÓN ===
    st.markdown("---")
    st.markdown("### 🛠️ Análisis de Problemas Reportados y Tiempos de Resolución")
    add_problem_resolution_analysis(df)

def show_routes_analysis(df, merged_df):
    """Análisis completo por rutas con supervisores y contratistas"""
    st.subheader("🚚 Análisis Completo por Rutas, Supervisores y Contratistas")    # Primera fila - Top 3 rutas por contratista (fila completa)
    if 'CONTRATISTA' in merged_df.columns and 'SUPERVISOR' in merged_df.columns:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 20px; margin: 20px 0; color: white; box-shadow: 0 10px 25px rgba(250, 112, 154, 0.3);">
                <h3 style="color: white; margin: 0; text-align: center;">🏆 Top 3 Rutas por Contratista</h3>
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
            color_continuous_scale='Plasma'        )        
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
                'tickfont_color': 'white'  # Cambiado a blanco para mejor visibilidad
            },
            margin=dict(l=350, r=100, t=100, b=80),  # Más espacio para etiquetas descriptivas
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white'),  # Asegurar que todos los textos sean blancos
            title_font_size=16,
            xaxis_title="<b>Número de Registros</b>",
            yaxis_title="<b>Ruta</b>"
        )
    st.plotly_chart(fig_contratista_rutas, use_container_width=True)
          # Segunda fila - Top 3 rutas por supervisor (fila completa)        
    st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 20px; margin: 20px 0; color: white; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);">
                <h3 style="color: white; margin: 0; text-align: center;">🏆 Top 3 Rutas por Supervisor</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )      # Análisis por supervisor
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
            'tickfont_color': 'white'  # Cambiado a blanco para mejor visibilidad
        },
        margin=dict(l=350, r=100, t=100, b=80),  # Más espacio para etiquetas descriptivas
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='white'),
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
        font=dict(size=14, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
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
            <strong>• Eje Y (vertical):</strong> Tiempo promedio de cierre en días (menor es mejor)<br>
            <strong>• Tamaño de burbuja:</strong> Tasa de cierre (% de casos resueltos)<br>
            <strong>• Color:</strong> Intensidad de la tasa de cierre (Verde = alta, Rojo = baja)
        </p>
        <p style="color: white; margin: 10px 0; font-weight: bold;">
            🎯 <strong>Rutas ideales:</strong> Burbujas grandes y verdes en la parte inferior derecha (alto volumen + cierre rápido + alta tasa de cierre)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    ruta_eficiencia = df.groupby('ruta').agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': 'mean',
        'fecha_cierre': lambda x: x.notna().sum()
    }).round(2).reset_index()
    ruta_eficiencia.columns = ['ruta', 'total_registros', 'tiempo_promedio_cierre', 'total_cierres']
    ruta_eficiencia['tasa_cierre'] = (ruta_eficiencia['total_cierres'] / ruta_eficiencia['total_registros']) * 100
    
    # Filtrar rutas con al menos 1 registro para análisis más significativo
    ruta_eficiencia_filtrada = ruta_eficiencia[ruta_eficiencia['total_registros'] >= 1]
    
    # Añadir categorías de rendimiento para mejor interpretación
    def categorizar_rendimiento(row):
        if row['tiempo_promedio_cierre'] <= 5 and row['tasa_cierre'] >= 80:
            return "🟢 Excelente"
        elif row['tiempo_promedio_cierre'] <= 10 and row['tasa_cierre'] >= 60:
            return "🟡 Bueno"
        else:
            return "🔴 Necesita Mejora"
    
    ruta_eficiencia_filtrada['categoria_rendimiento'] = ruta_eficiencia_filtrada.apply(categorizar_rendimiento, axis=1)
    fig_eficiencia = px.scatter(
        ruta_eficiencia_filtrada,
        x='total_registros',
        y='tiempo_promedio_cierre',
        size='tasa_cierre',
        hover_data={
            'ruta': True,
            'tasa_cierre': ':.1f',
            'total_cierres': True,
            'categoria_rendimiento': True,
            'total_registros': True,
            'tiempo_promedio_cierre': ':.2f'
        },
        title="📊 Eficiencia Integral por Ruta: Volumen vs Tiempo de Cierre vs Tasa de Cierre",
        color='tasa_cierre',
        color_continuous_scale='RdYlGn',
        height=800,
        labels={
            'total_registros': 'Total de Registros de Feedback',
            'tiempo_promedio_cierre': 'Tiempo Promedio de Cierre (días)',
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
        yaxis_title="<b>Tiempo Promedio de Cierre (días)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    st.plotly_chart(fig_eficiencia, use_container_width=True)
    
    # Tabla resumen de las mejores y peores rutas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 5 Rutas Más Eficientes")
        top_eficientes = ruta_eficiencia_filtrada.nlargest(5, 'tasa_cierre')[['ruta', 'total_registros', 'tiempo_promedio_cierre', 'tasa_cierre', 'categoria_rendimiento']]
        top_eficientes.columns = ['Ruta', 'Registros', 'Tiempo Cierre (días)', 'Tasa Cierre %', 'Categoría']
        st.dataframe(top_eficientes, use_container_width=True)
    
    with col2:
        st.markdown("#### ⚠️ Top 5 Rutas que Necesitan Atención")
        menor_eficientes = ruta_eficiencia_filtrada.nsmallest(5, 'tasa_cierre')[['ruta', 'total_registros', 'tiempo_promedio_cierre', 'tasa_cierre', 'categoria_rendimiento']]        
        menor_eficientes.columns = ['Ruta', 'Registros', 'Tiempo Cierre (días)', 'Tasa Cierre %', 'Categoría']
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
            y='ruta',            orientation='h',
            title="⚠️ Top 15 Rutas con Menor Actividad (≤5 registros)",
            color='tiempo_promedio_cierre',
            color_continuous_scale='Reds_r',
            height=600,
            text='total_registros'
        )        
        fig_offenders_rutas.update_traces(
            texttemplate='%{text} registros',
            textposition='outside',
            marker_line_width=0,
            textfont=dict(size=12, color='white')
        )
        
        fig_offenders_rutas.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=150, r=50, t=80, b=50),
            xaxis_title="<b>Número de Registros</b>",
            yaxis_title="<b>Ruta</b>",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white')
        )
        
        st.plotly_chart(fig_offenders_rutas, use_container_width=True)
        
        # Tabla con detalles de rutas con baja actividad
        st.markdown("#### 📋 Detalles de Rutas con Baja Actividad")
        offenders_details = rutas_con_pocos_registros[['ruta', 'total_registros', 'tiempo_promedio_cierre', 'tasa_cierre']].copy()
        offenders_details.columns = ['Ruta', 'Total Registros', 'Tiempo Promedio Cierre (días)', 'Tasa Cierre (%)']
        st.dataframe(clean_dataframe_for_display(offenders_details), use_container_width=True)
    else:
        st.info("✅ No hay rutas con baja actividad (todas tienen más de 5 registros)")
    
    # Sexta fila - Análisis completo de supervisores y contratistas
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
            'tiempo_cierre_dias': 'mean',
            'fecha_cierre': lambda x: x.notna().sum(),
            'ruta': 'nunique',
            'codigo_cliente': 'nunique'
        }).round(2).reset_index()
        supervisor_analysis.columns = ['supervisor', 'total_casos', 'tiempo_promedio_cierre', 'casos_cerrados', 'rutas_supervisadas', 'clientes_unicos']
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
            text='value'        )
        
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
            legend_title="Estado del Caso",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white')
        )
        st.plotly_chart(fig_supervisor_comparison, use_container_width=True)
        
        # Gráfico de tasa de cierre por supervisor - Una línea completa
        fig_supervisor_cierre = px.bar(
            supervisor_analysis.head(10),
            x='tasa_cierre',            
            y='supervisor',
            orientation='h',
            title="📈 Tasa de Cierre por Supervisor (Top 10)",
            color='tiempo_promedio_cierre',
            color_continuous_scale='RdYlGn_r',
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
            yaxis_title="<b>Supervisor</b>",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white')
        )
        st.plotly_chart(fig_supervisor_cierre, use_container_width=True)
        
        # Tabla con análisis detallado de supervisores
        st.markdown("#### 📊 Análisis Completo de Supervisores")        
        supervisor_details = supervisor_analysis[['supervisor', 'total_casos', 'casos_cerrados', 'casos_pendientes', 'tasa_cierre', 'tiempo_promedio_cierre', 'rutas_supervisadas', 'clientes_unicos']].copy()
        supervisor_details.columns = ['Supervisor', 'Total Casos', 'Casos Cerrados', 'Casos Pendientes', 'Tasa Cierre (%)', 'Tiempo Promedio Cierre (días)', 'Rutas Supervisadas', 'Clientes Únicos']
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
            'tiempo_cierre_dias': 'mean',
            'fecha_cierre': lambda x: x.notna().sum(),
            'ruta': 'nunique',
            'motivo_retro': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
            'respuesta_sub': 'nunique'
        }).round(2).reset_index()
        contratista_analysis.columns = ['contratista', 'total_casos', 'tiempo_promedio_cierre', 'casos_cerrados', 'rutas_trabajadas', 'motivo_principal', 'tipos_respuesta']
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
            legend_title="Estado del Caso",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white')
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
            textfont_color='white'        )
        
        fig_motivos_contratista.update_layout(
            yaxis={
                'categoryorder': 'total ascending'
            },
            margin=dict(l=300, r=100, t=80, b=50),
            xaxis_title="<b>Número de Casos</b>",
            yaxis_title="<b>Motivo</b>",
            font=dict(color='white', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_motivos_contratista, use_container_width=True)
        
        # Tabla con análisis detallado de contratistas
        st.markdown("#### 📊 Análisis Completo de Contratistas")
        contratista_details = contratista_analysis[['contratista', 'total_casos', 'casos_cerrados', 'casos_pendientes', 'tasa_cierre', 'tiempo_promedio_cierre', 'rutas_trabajadas', 'motivo_principal', 'tipos_respuesta']].copy()
        contratista_details.columns = ['Contratista', 'Total Casos', 'Casos Cerrados', 'Casos Pendientes', 'Tasa Cierre (%)', 'Tiempo Promedio Cierre (días)', 'Rutas Trabajadas', 'Motivo Principal', 'Tipos de Respuesta']
        st.dataframe(clean_dataframe_for_display(contratista_details), use_container_width=True)
        
    # Séptima fila - Análisis de motivos específicos en lugar de números
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 20px; margin: 20px 0; color: white; box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);">
            <h3 style="color: white; margin: 0; text-align: center;">🎯 Análisis Detallado de Motivos Específicos</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Análisis detallado de motivos con nombres específicos
    motivos_analysis = df.groupby('motivo_retro').agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique'
    }).round(2)
    motivos_analysis.columns = ['total_casos', 'tiempo_promedio_cierre', 'desviacion_tiempo_cierre', 'casos_cerrados', 'clientes_afectados']
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
        color='tiempo_promedio_cierre',
        color_continuous_scale='RdYlBu_r',
        height=700,
        hover_data={
            'motivo_retro': True,
            'total_casos': True,
            'tiempo_promedio_cierre': ':.2f',
            'tasa_cierre': ':.1f',
            'clientes_afectados': True
        }
    )    
    fig_motivos.update_traces(
        texttemplate='%{text} casos',
        textposition='outside',
        marker_line_width=0,
        textfont=dict(size=12, color='white')
    )
    
    fig_motivos.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=200, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='white')
    )
    
    st.plotly_chart(fig_motivos, use_container_width=True)
    
    # Tabla detallada de motivos
    st.markdown("#### 📋 Detalles Completos de Motivos")
    motivos_details = motivos_analysis[['motivo_retro', 'total_casos', 'tiempo_promedio_cierre', 'tasa_cierre', 'clientes_afectados', 'desviacion_tiempo_cierre']].copy()
    motivos_details.columns = ['Motivo', 'Total Casos', 'Tiempo Promedio Cierre (días)', 'Tasa Cierre (%)', 'Clientes Afectados', 'Desviación Tiempo Cierre']
    st.dataframe(clean_dataframe_for_display(motivos_details), use_container_width=True)
    
    # Octava fila - Análisis de respuestas específicas
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 20px; margin: 20px 0; color: white; box-shadow: 0 10px 25px rgba(250, 112, 154, 0.3);">
            <h3 style="color: white; margin: 0; text-align: center;">💬 Análisis de Tipos de Respuesta Específicas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de respuestas específicas
    respuestas_analysis = df.groupby('respuesta_sub').agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique'    }).round(2)
    respuestas_analysis.columns = ['total_casos', 'tiempo_promedio_cierre', 'desviacion_tiempo_cierre', 'casos_cerrados', 'clientes_afectados']
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
        color='tiempo_promedio_cierre',
        color_continuous_scale='Viridis_r',
        height=700,
        hover_data={
            'respuesta_sub': True,
            'total_casos': True,            'tiempo_promedio_cierre': ':.2f',
            'tasa_cierre': ':.1f',
            'clientes_afectados': True
        }
    )      
    fig_respuestas.update_traces(
        texttemplate='<b>%{x}</b>',
        textposition='outside',
        marker_line_width=0,
        textfont=dict(size=10, color='white')
    )
    
    fig_respuestas.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=250, r=100, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        xaxis_title="<b>Total de Casos</b>",
        yaxis_title="<b>Tipo de Respuesta</b>"
    )
    
    st.plotly_chart(fig_respuestas, use_container_width=True)
    
    # Tabla detallada de respuestas
    st.markdown("#### 📋 Detalles Completos de Tipos de Respuesta")
    respuestas_details = respuestas_analysis[['respuesta_sub', 'total_casos', 'tiempo_promedio_cierre', 'tasa_cierre', 'clientes_afectados', 'desviacion_tiempo_cierre']].copy()
    respuestas_details.columns = ['Tipo de Respuesta', 'Total Casos', 'Tiempo Promedio Cierre (días)', 'Tasa Cierre (%)', 'Clientes Afectados', 'Desviación Tiempo Cierre']
    st.dataframe(clean_dataframe_for_display(respuestas_details), use_container_width=True)
    # Este análisis de cumplimiento de meta mensual se movió a la sección "Supervisores y Contratistas" para evitar duplicación

def show_supervisors_contractors_analysis(df, merged_df, rutas_df):
    """Análisis integral dedicado a Supervisores y Contratistas
    
    Esta función muestra análisis de supervisores y contratistas, incluyendo rutas con cero feedbacks.
    Se ha corregido para usar rutas_df directamente para asegurar consistencia entre ambas tablas.
    """
    st.subheader("👨‍💼 Análisis Integral por Supervisores y Contratistas")
    
    # Verificar que tenemos los datos necesarios
    if 'SUPERVISOR' not in merged_df.columns and 'CONTRATISTA' not in merged_df.columns:
        st.warning("⚠️ No hay datos de Supervisores o Contratistas disponibles en el dataset.")
        return
      # ========== CALCULAMOS EL TOTAL DE RUTAS DISPONIBLES DESDE BD_RUTAS ==========
    # Filtrar rutas que tienen contratista real asignado (no "Dummy" o nulos)
    rutas_con_contratista_real = rutas_df[
        (rutas_df['CONTRATISTA'].notna()) & 
        (~rutas_df['CONTRATISTA'].str.contains('Dummy', case=False, na=False))
    ]
    total_rutas_disponibles = rutas_con_contratista_real['RUTA'].nunique()  # Total de rutas con contratistas reales
      # --- NUEVA SECCIÓN: Cumplimiento de Meta Mensual por Ruta, Supervisor y Contratista ---
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📅 Cumplimiento de Meta Mensual por Ruta</h3>  
        </div>
        """,
        unsafe_allow_html=True
    )
      # Filtros dinámicos mejorados en dos filas
    # Primera fila de filtros - Mes, Supervisor y Contratista
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    with col_filtro1:
        # Ordenar meses cronológicamente
        meses_ordenados = df.groupby(['mes', 'mes_nombre']).size().reset_index().sort_values('mes')['mes_nombre'].tolist()
        mes_meta = st.selectbox("📅 Selecciona el mes:", meses_ordenados, key="meta_mes")
    
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
      # Se removieron los filtros adicionales de Tipo de Reporte y Motivo según lo solicitado    # Aplicar filtros
    df_meta = merged_df[merged_df['mes_nombre'] == mes_meta].copy()
    
    if supervisor_meta != 'Todos' and 'SUPERVISOR' in df_meta.columns:
        df_meta = df_meta[df_meta['SUPERVISOR'] == supervisor_meta]
    
    if contratista_meta != 'Todos' and 'CONTRATISTA' in df_meta.columns:
        df_meta = df_meta[df_meta['CONTRATISTA'] == contratista_meta]
          # Crear mensaje descriptivo de filtros aplicados
    filtros_aplicados = []
    if supervisor_meta != 'Todos':
        filtros_aplicados.append(f"Supervisor: {supervisor_meta}")
    if contratista_meta != 'Todos':
        filtros_aplicados.append(f"Contratista: {contratista_meta}")
    
    filtros_mensaje = ", ".join(filtros_aplicados) if filtros_aplicados else "ninguno"
    st.info(f"🔍 Mostrando datos para el mes de {mes_meta}. Filtros aplicados: {filtros_mensaje}.")
    
    # --- Análisis por SUPERVISOR ---
    if 'SUPERVISOR' in df_meta.columns:
        st.markdown("### 👨‍💼 Análisis por Supervisores")
          # ========== MEJORA: Incluir rutas con 0 registros ==========
        # 1. Obtener todas las rutas asignadas a supervisores (de BD_Rutas completo)
        # Usar rutas_df en lugar de merged_df para asegurar todas las rutas estén incluidas
        todas_rutas_supervisor = rutas_df[['SUPERVISOR', 'RUTA']].drop_duplicates()
        todas_rutas_supervisor = todas_rutas_supervisor.rename(columns={'RUTA': 'ruta'})
        
        # 2. Calcular registros por supervisor-ruta para el período filtrado
        registros_activos = df_meta.groupby(['SUPERVISOR', 'ruta']).agg({'id_tema':'count'}).reset_index()
        
        # 3. Hacer merge completo para incluir rutas con 0 registros
        supervisor_rutas = todas_rutas_supervisor.merge(
            registros_activos, 
            on=['SUPERVISOR', 'ruta'], 
            how='left'
        )
        supervisor_rutas['id_tema'] = supervisor_rutas['id_tema'].fillna(0).astype(int)
        
        # 4. Filtrar por supervisor seleccionado si aplica
        if supervisor_meta != 'Todos':
            supervisor_rutas = supervisor_rutas[supervisor_rutas['SUPERVISOR'] == supervisor_meta]
          # 5. Calcular métricas finales con meta variable según el mes
        # Obtener el número de mes para determinar la meta
        meses_dict = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        mes_numero = meses_dict.get(mes_meta, 6)  # Default a junio si no se encuentra
        meta_mensual = 6 if mes_numero <= 5 else 10
        
        supervisor_rutas['Meta Cumplida'] = supervisor_rutas['id_tema'] >= meta_mensual
        supervisor_rutas['Estado'] = supervisor_rutas['Meta Cumplida'].map(lambda x: '✅ Cumple' if x else '❌ No Cumple')
        supervisor_rutas = supervisor_rutas.rename(columns={'id_tema':'Registros'})
        
        # Tabla detallada
        st.dataframe(
            clean_dataframe_for_display(supervisor_rutas[['SUPERVISOR', 'ruta', 'Registros', 'Estado']]), 
            use_container_width=True
        )
          # KPIs por supervisor
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:            # ========== CORREGIDO: Usar el número de rutas del dataframe de supervisores ==========
            total_rutas_sup = supervisor_rutas.shape[0]  # Usar el número real de rutas del supervisor
            rutas_cumplen_sup = supervisor_rutas['Meta Cumplida'].sum()
            porcentaje_cumple_sup = (rutas_cumplen_sup/total_rutas_sup*100) if total_rutas_sup > 0 else 0
            st.metric("📊 % Rutas que Cumplen Meta", f"{porcentaje_cumple_sup:.1f}%", f"Meta: {meta_mensual} reg/ruta")
        
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
          # ========== MEJORA: Incluir rutas con 0 registros ==========
        # 1. Obtener todas las rutas asignadas a contratistas (de BD_Rutas completo)
        # Usar rutas_df para mantener consistencia con la sección de supervisores
        todas_rutas_contratista = rutas_df[['CONTRATISTA', 'RUTA']].drop_duplicates()
        todas_rutas_contratista = todas_rutas_contratista.rename(columns={'RUTA': 'ruta'})
        
        # 2. Calcular registros por contratista-ruta para el período filtrado
        registros_activos_con = df_meta.groupby(['CONTRATISTA', 'ruta']).agg({'id_tema':'count'}).reset_index()
        
        # 3. Hacer merge completo para incluir rutas con 0 registros
        contratista_rutas = todas_rutas_contratista.merge(
            registros_activos_con, 
            on=['CONTRATISTA', 'ruta'], 
            how='left'
        )
        contratista_rutas['id_tema'] = contratista_rutas['id_tema'].fillna(0).astype(int)
        
        # 4. Filtrar por contratista seleccionado si aplica
        if contratista_meta != 'Todos':
            contratista_rutas = contratista_rutas[contratista_rutas['CONTRATISTA'] == contratista_meta]
          # 5. Calcular métricas finales con meta variable según el mes
        # Usar la misma meta calculada anteriormente
        contratista_rutas['Meta Cumplida'] = contratista_rutas['id_tema'] >= meta_mensual
        contratista_rutas['Estado'] = contratista_rutas['Meta Cumplida'].map(lambda x: '✅ Cumple' if x else '❌ No Cumple')
        contratista_rutas = contratista_rutas.rename(columns={'id_tema':'Registros'})
        
        # Tabla detallada
        st.dataframe(
            clean_dataframe_for_display(contratista_rutas[['CONTRATISTA', 'ruta', 'Registros', 'Estado']]), 
            use_container_width=True
        )
          # KPIs por contratista
        col_kpi4, col_kpi5, col_kpi6 = st.columns(3)
        with col_kpi4:            # ========== CORREGIDO: Usar el número de rutas del dataframe de contratistas ==========
            total_rutas_con = contratista_rutas.shape[0]  # Usar el número real de rutas del contratista
            rutas_cumplen_con = contratista_rutas['Meta Cumplida'].sum()
            porcentaje_cumple_con = (rutas_cumplen_con/total_rutas_con*100) if total_rutas_con > 0 else 0
            st.metric("📊 % Rutas que Cumplen Meta", f"{porcentaje_cumple_con:.1f}%", f"Meta: {meta_mensual} reg/ruta")
        
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
    
    # === SECCIÓN 1: ANÁLISIS DE USUARIOS ===
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
        'tiempo_cierre_dias': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'ruta': 'nunique',
        'codigo_cliente': 'nunique'
    }).round(2)
    user_performance.columns = ['Total_Registros', 'Tiempo_Promedio_Cierre', 'Desviacion_Tiempo_Cierre', 'Registros_Cerrados', 'Rutas_Trabajadas', 'Clientes_Atendidos']
    user_performance = user_performance.reset_index()
    user_performance['Tasa_Cierre'] = (user_performance['Registros_Cerrados'] / user_performance['Total_Registros']) * 100
    user_performance['Eficiencia'] = user_performance['Tasa_Cierre'] / (user_performance['Tiempo_Promedio_Cierre'] + 1)  # Eficiencia basada en rapidez de cierre
    user_performance = user_performance.sort_values('Total_Registros', ascending=False)
    
    # Gráfico 1: Top 15 usuarios por volumen
    fig_user_performance = px.bar(
        user_performance.head(15),        x='Total_Registros',
        y='usuario',
        orientation='h',
        title="👤 Top 15 Usuarios por Volumen de Registros",
        color='Tiempo_Promedio_Cierre',
        color_continuous_scale='Blues_r',
        height=700,
        text='Total_Registros'
    )
    fig_user_performance.update_traces(
        texttemplate='<b>%{text}</b>', 
        textposition='outside',
        marker_line_width=1,
        marker_line_color='white'
    )      
    fig_user_performance.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=150, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    st.plotly_chart(fig_user_performance, use_container_width=True)
    
    # === SECCIÓN 2: ANÁLISIS DE EFICIENCIA USUARIO vs CALIDAD ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⚡ Matriz de Eficiencia: Productividad vs Calidad</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Gráfico 2: Scatter plot de productividad vs tiempo de cierre
    fig_efficiency = px.scatter(
        user_performance.head(20),
        x='Total_Registros',
        y='Tiempo_Promedio_Cierre',
        size='Tasa_Cierre',
        color='Eficiencia',
        hover_data={
            'usuario': True,
            'Total_Registros': True,
            'Tiempo_Promedio_Cierre': ':.2f',
            'Tasa_Cierre': ':.1f',
            'Rutas_Trabajadas': True,
            'Clientes_Atendidos': True
        },
        title='⚡ Productividad vs Tiempo de Cierre (Tamaño = Tasa de Cierre)',
        color_continuous_scale='Viridis',
        height=600
    )
    
    fig_efficiency.update_traces(
        marker=dict(
            sizemode='diameter',
            sizemin=10,
            sizeref=2,
            line_width=2,
            line_color='white'
        )
    )
      # Agregar líneas de referencia
    promedio_registros = user_performance['Total_Registros'].mean()
    promedio_tiempo_cierre = user_performance['Tiempo_Promedio_Cierre'].mean()
    
    fig_efficiency.add_hline(y=promedio_tiempo_cierre, line_dash="dash", line_color="yellow", 
                           annotation_text="Promedio de Tiempo de Cierre")
    fig_efficiency.add_vline(x=promedio_registros, line_dash="dash", line_color="orange",
                           annotation_text="Promedio de Productividad")    
    fig_efficiency.update_layout(
        xaxis_title="<b>Total de Registros (Productividad)</b>",
        yaxis_title="<b>Tiempo Promedio de Cierre (días)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    # === SECCIÓN 3: ANÁLISIS DE VENDEDORES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💼 Análisis de Rendimiento de Vendedores</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if 'vendedor' in df.columns:
        vendedor_performance = df.groupby('vendedor').agg({
            'id_tema': 'count',
            'tiempo_cierre_dias': ['mean', 'std'],
            'codigo_cliente': 'nunique',
            'ruta': 'nunique',
            'fecha_cierre': lambda x: x.notna().sum()
        }).round(2)
        vendedor_performance.columns = ['Total_Casos', 'Tiempo_Promedio_Cierre', 'Desviacion_Tiempo_Cierre', 'Clientes_Unicos', 'Rutas_Cubiertas', 'Casos_Cerrados']
        vendedor_performance = vendedor_performance.reset_index()
        vendedor_performance['Tasa_Cierre'] = (vendedor_performance['Casos_Cerrados'] / vendedor_performance['Total_Casos']) * 100
        vendedor_performance = vendedor_performance.sort_values('Total_Casos', ascending=False).head(20)
        
        # Gráfico 3: Top vendedores
        fig_vendedores = px.bar(
            vendedor_performance,
            x='Total_Casos',
            y='vendedor',
            orientation='h',
            title="💼 Top 20 Vendedores por Volumen de Casos",
            color='Tiempo_Promedio_Cierre',
            color_continuous_scale='Plasma_r',
            height=700,
            text='Total_Casos'
        )
        fig_vendedores.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=1,
            marker_line_color='white'
        )          
        fig_vendedores.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=150, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12)
        )
        st.plotly_chart(fig_vendedores, use_container_width=True)
    else:
        st.info("ℹ️ No hay datos de vendedores disponibles para análisis")
    
    # === SECCIÓN 4: ANÁLISIS DE CARGA DE TRABAJO ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Distribución de Carga de Trabajo</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Gráfico 4: Histograma de distribución de casos
    fig_distribution = px.histogram(
        user_performance,
        x='Total_Registros',
        nbins=20,
        title='📊 Distribución de Casos por Usuario',
        color_discrete_sequence=['#4ECDC4'],
        height=500
    )
    
    fig_distribution.update_traces(
        marker_line_width=1,
        marker_line_color='white'
    )
    
    fig_distribution.update_layout(
        xaxis_title="<b>Número de Casos</b>",
        yaxis_title="<b>Número de Usuarios</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    st.plotly_chart(fig_distribution, use_container_width=True)
    
    # === SECCIÓN 5: ANÁLISIS COMPARATIVO DE EFICIENCIA POR RUTAS ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🗺️ Eficiencia de Usuarios por Rutas Trabajadas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Gráfico 5: Eficiencia vs Rutas trabajadas
    fig_rutas_efficiency = px.scatter(
        user_performance.head(25),
        x='Rutas_Trabajadas',
        y='Eficiencia',
        size='Total_Registros',
        color='Tasa_Cierre',
        hover_data={
            'usuario': True,
            'Rutas_Trabajadas': True,
            'Eficiencia': ':.2f',
            'Total_Registros': True,
            'Clientes_Atendidos': True
        },
        title='🗺️ Eficiencia vs Diversidad de Rutas',
        color_continuous_scale='RdYlGn',
        height=600
    )
    
    fig_rutas_efficiency.update_traces(
        marker=dict(
            sizemode='diameter',
            sizemin=8,
            sizeref=2,
            line_width=2,
            line_color='white'
        )
    )
    fig_rutas_efficiency.update_layout(
        xaxis_title="<b>Número de Rutas Trabajadas</b>",        
        yaxis_title="<b>Eficiencia (Calidad × Cierre)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    st.plotly_chart(fig_rutas_efficiency, use_container_width=True)
    
    # === SECCIÓN 6: ANÁLISIS DE TOP Y BOTTOM PERFORMERS ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🏆 Top & Bottom Performers</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:        st.markdown("##### 🏆 Top 5 Usuarios por Eficiencia")
    top_efficient = user_performance.nlargest(5, 'Eficiencia')[
            ['usuario', 'Total_Registros', 'Tiempo_Promedio_Cierre', 'Tasa_Cierre', 'Eficiencia']
        ].copy()
    top_efficient.columns = ['Usuario', 'Casos', 'Tiempo Cierre (días)', 'Cierre (%)', 'Eficiencia']
    st.dataframe(clean_dataframe_for_display(top_efficient), use_container_width=True, hide_index=True)
    with col2:
        st.markdown("##### ⚠️ Bottom 5 Usuarios (Necesitan Apoyo)")
        bottom_performers = user_performance[user_performance['Total_Registros'] >= 5].nsmallest(5, 'Eficiencia')[
            ['usuario', 'Total_Registros', 'Tiempo_Promedio_Cierre', 'Tasa_Cierre', 'Eficiencia']
        ].copy()
        if not bottom_performers.empty:
            bottom_performers.columns = ['Usuario', 'Casos', 'Tiempo Cierre (días)', 'Cierre (%)', 'Eficiencia']
            st.dataframe(clean_dataframe_for_display(bottom_performers), use_container_width=True, hide_index=True)
        else:
            st.success("✅ Todos los usuarios tienen buen rendimiento")
    
    # === SECCIÓN 7: INSIGHTS Y RECOMENDACIONES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💡 Insights de Personal y Recomendaciones</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Generar insights automáticos
    mejor_usuario = user_performance.loc[user_performance['Eficiencia'].idxmax(), 'usuario']
    mejor_eficiencia = user_performance['Eficiencia'].max()
    usuarios_alta_productividad = len(user_performance[user_performance['Total_Registros'] >= user_performance['Total_Registros'].quantile(0.8)])
    usuarios_baja_eficiencia = len(user_performance[user_performance['Eficiencia'] <= user_performance['Eficiencia'].quantile(0.2)])
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h4 style="color: white; margin: 0;">🧠 Insights del Personal</h4>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            🏆 <strong>Mejor usuario:</strong> {mejor_usuario} (Eficiencia: {mejor_eficiencia:.2f})
        </p>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            📈 <strong>Alta productividad:</strong> {usuarios_alta_productividad} usuarios en el top 20%
        </p>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            ⚠️ <strong>Necesitan apoyo:</strong> {usuarios_baja_eficiencia} usuarios en el bottom 20%
        </p>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            📊 <strong>Diversidad de rutas promedio:</strong> {user_performance['Rutas_Trabajadas'].mean():.1f} rutas por usuario
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recomendaciones
    st.markdown("##### 📋 Plan de Acción Recomendado")
    recomendaciones = [
        "🎓 **Programa de mentoring:** Los top performers pueden capacitar a usuarios con baja eficiencia",
        "📈 **Redistribución de carga:** Equilibrar casos entre usuarios de alta y baja productividad",
        "🗺️ **Especialización en rutas:** Usuarios con pocas rutas pueden especializarse para mejor eficiencia",
        "⚡ **Incentivos por eficiencia:** Reconocer usuarios que combinan alta productividad y calidad",
        "📊 **Monitoreo semanal:** Seguimiento de KPIs para identificar tendencias tempranas",
        "🎯 **Metas personalizadas:** Establecer objetivos específicos según perfil de cada usuario"
    ]
    
    for rec in recomendaciones:
        st.markdown(rec)

def show_performance_analysis(df):
    """Análisis de rendimiento completo y avanzado con múltiples métricas"""
    st.subheader("🎯 Análisis Detallado de Rendimiento y Calidad")
    
    # === SECCIÓN 1: OVERVIEW DE RENDIMIENTO GENERAL ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Dashboard de Rendimiento General</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # KPIs principales de rendimiento
    col1, col2, col3, col4 = st.columns(4)
    
    total_casos = len(df)
    casos_cerrados = df['fecha_cierre'].notna().sum()
    tasa_cierre_global = (casos_cerrados / total_casos) * 100 if total_casos > 0 else 0    
    tiempo_promedio_cierre_global = df[df['fecha_cierre'].notna()]['tiempo_cierre_dias'].mean() if len(df[df['fecha_cierre'].notna()]) > 0 else 0
    
    with col1:
        st.metric(
            "📈 Total de Casos",
            f"{total_casos:,}",
            f"+{len(df[df['mes'] == df['mes'].max()])} este mes" if not df.empty else ""
        )
    
    with col2:
        st.metric(
            "✅ Tasa de Cierre",
            f"{tasa_cierre_global:.1f}%",
            "📊 Global"
        )
    
    with col3:
        st.metric(
            "⏱️ Tiempo Promedio Cierre",
            f"{tiempo_promedio_cierre_global:.1f} días",
            "🎯 Promedio"
        )
    
    with col4:
        clientes_unicos = df['codigo_cliente'].nunique()
        st.metric(
            "👥 Clientes Activos",
            f"{clientes_unicos:,}",
            "🏪 Únicos"
        )
    
    # === SECCIÓN 2: ANÁLISIS DETALLADO DE CLIENTES POR RENDIMIENTO ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🏪 Matriz de Rendimiento de Clientes</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Formatear correctamente el código de cliente como ID
    df['codigo_cliente_display'] = df['codigo_cliente'].apply(lambda x: f"Cliente-{str(x).zfill(6)}")
      # Análisis avanzado de clientes
    clientes_performance = df.groupby(['codigo_cliente', 'codigo_cliente_display']).agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'std', 'min', 'max'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
        'ruta': 'nunique',
        'usuario': 'nunique'
    }).round(2).reset_index()
    
    # Aplanar columnas
    clientes_performance.columns = ['codigo_cliente', 'codigo_cliente_display', 'total_reportes', 
                                   'tiempo_promedio_cierre', 'tiempo_std_cierre', 'tiempo_min_cierre', 'tiempo_max_cierre',
                                   'reportes_cerrados', 'motivo_principal', 'rutas_afectadas', 'usuarios_involucrados']
    
    clientes_performance['tasa_cierre'] = (clientes_performance['reportes_cerrados'] / clientes_performance['total_reportes']) * 100
    clientes_performance['variabilidad_tiempo'] = clientes_performance['tiempo_std_cierre']
    
    # Clasificación de clientes por rendimiento
    clientes_performance['categoria_rendimiento'] = clientes_performance.apply(lambda x:
        '🔴 Crítico' if x['total_reportes'] >= 15 and x['tiempo_promedio_cierre'] >= 15 else
        '🟡 Atención' if x['total_reportes'] >= 10 and x['tiempo_promedio_cierre'] >= 10 else
        '🟢 Estable' if x['total_reportes'] >= 5 and x['tiempo_promedio_cierre'] <= 7 else
        '⚪ Monitoreando', axis=1
    )
    
    clientes_performance = clientes_performance.sort_values('total_reportes', ascending=False).head(25)
    
    # Gráfico de dispersión avanzado: Volumen vs Calidad    
    fig_scatter = px.scatter(
        clientes_performance,
        x='total_reportes',
        y='tiempo_promedio_cierre',
        size='tasa_cierre',
        color='categoria_rendimiento',
        hover_data={
            'codigo_cliente_display': True,
            'total_reportes': True,
            'tiempo_promedio_cierre': ':.2f',
            'tasa_cierre': ':.1f',
            'variabilidad_tiempo': ':.2f',
            'rutas_afectadas': True
        },
        title='🎯 Matriz de Rendimiento: Volumen vs Tiempo de Cierre vs Tasa de Cierre',
        color_discrete_map={
            '🔴 Crítico': '#FF4444',
            '🟡 Atención': '#FFA500',
            '🟢 Estable': '#32CD32',
            '⚪ Monitoreando': '#87CEEB'
        },
        height=700
    )
      # Añadir líneas de referencia
    fig_scatter.add_hline(y=tiempo_promedio_cierre_global, line_dash="dash", line_color="white", 
                         annotation_text="Promedio Global de Tiempo de Cierre")
    fig_scatter.add_vline(x=clientes_performance['total_reportes'].median(), line_dash="dash", line_color="yellow",
                         annotation_text="Mediana de Volumen")
    
    fig_scatter.update_traces(
        marker=dict(
            sizemode='diameter',
            sizemin=8,
            sizeref=2,
            line_width=2,
            line_color='white'
        )
    )    
    fig_scatter.update_layout(
        xaxis_title="<b>Total de Reportes</b>",        
        yaxis_title="<b>Tiempo Promedio de Cierre (días)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # === SECCIÓN 3: ANÁLISIS DE TENDENCIAS POR USUARIO ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">👤 Análisis de Rendimiento por Usuario</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de usuarios    
    usuarios_performance = df.groupby('usuario').agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique',
        'ruta': 'nunique'
    }).round(2).reset_index()
    
    usuarios_performance.columns = ['usuario', 'total_casos', 'tiempo_promedio_cierre', 'tiempo_std_cierre', 
                                   'casos_cerrados', 'clientes_atendidos', 'rutas_trabajadas']
    usuarios_performance['tasa_cierre'] = (usuarios_performance['casos_cerrados'] / usuarios_performance['total_casos']) * 100
    usuarios_performance['eficiencia'] = usuarios_performance['tasa_cierre'] / (usuarios_performance['tiempo_promedio_cierre'] + 1)
    usuarios_performance = usuarios_performance.sort_values('total_casos', ascending=False).head(20)
    
    # Gráfico de barras apiladas para usuarios
    fig_usuarios = go.Figure()
    
    # Barras de casos totales
    fig_usuarios.add_trace(go.Bar(
        name='📊 Casos Totales',
        x=usuarios_performance['usuario'],
        y=usuarios_performance['total_casos'],
        yaxis='y',
        offsetgroup=1,
        marker=dict(color='#FF6B6B'),        
        text=usuarios_performance['total_casos'],
        textposition='outside',
        textfont=dict(color='white', size=10)
    ))
      # Línea de eficiencia
    fig_usuarios.add_trace(go.Scatter(
        name='⚡ Eficiencia',
        x=usuarios_performance['usuario'],
        y=usuarios_performance['eficiencia'],
        mode='lines+markers',
        line=dict(color='#4ECDC4', width=3),        
        marker=dict(size=8, color='#4ECDC4'),        
        text=usuarios_performance['eficiencia'].round(2),
        textposition='top center',
        textfont=dict(color='white', size=10)
    ))    
    fig_usuarios.update_layout(
        title='👤 Rendimiento de Usuarios: Volumen vs Eficiencia',
        xaxis_title='<b>Usuario</b>',
        yaxis_title='<b>Total de Casos</b>',        
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_usuarios, use_container_width=True)
    
    # === SECCIÓN 4: ANÁLISIS DE MOTIVOS Y PATRONES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Análisis de Motivos y Patrones de Calidad</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Análisis de motivos vs tiempo de cierre
    motivos_analysis = df.groupby('respuesta_sub').agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': ['mean', 'std'],
        'fecha_cierre': lambda x: x.notna().sum(),
        'codigo_cliente': 'nunique'
    }).round(2).reset_index()
    
    motivos_analysis.columns = ['motivo', 'total_casos', 'tiempo_promedio_cierre', 'tiempo_cierre_std', 
                               'casos_cerrados', 'clientes_afectados']
    motivos_analysis['tasa_cierre'] = (motivos_analysis['casos_cerrados'] / motivos_analysis['total_casos']) * 100
    motivos_analysis = motivos_analysis.sort_values('total_casos', ascending=False).head(15)
      # Gráfico de burbujas para motivos
    fig_motivos = px.scatter(
        motivos_analysis,
        x='tiempo_promedio_cierre',
        y='tasa_cierre',
        size='total_casos',
        color='clientes_afectados',
        hover_data={
            'motivo': True,
            'total_casos': True,
            'tiempo_promedio_cierre': ':.2f',
            'tasa_cierre': ':.1f',
            'clientes_afectados': True
        },
        title='🎯 Matriz de Motivos: Tiempo de Cierre vs Tasa de Cierre vs Volumen',
        color_continuous_scale='Viridis',
        height=600
    )
    
    fig_motivos.update_traces(
        marker=dict(
            sizemode='diameter',
            sizemin=10,
            sizeref=2,
            line_width=2,
            line_color='white'
        )
    )    
    fig_motivos.update_layout(        
        xaxis_title="<b>Tiempo Promedio de Cierre (Días)</b>",
        yaxis_title="<b>Tasa de Cierre (%)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12)
    )
    
    st.plotly_chart(fig_motivos, use_container_width=True)
    
    # === SECCIÓN 5: TABLA RESUMEN DE RENDIMIENTO ===
    st.markdown("#### 📊 Resumen Ejecutivo de Rendimiento")
    
    # Top performers
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 🏆 Top 5 Clientes por Eficiencia")
        top_eficientes = clientes_performance.nsmallest(5, 'tiempo_promedio_cierre')[
            ['codigo_cliente_display', 'total_reportes', 'tiempo_promedio_cierre', 'tasa_cierre']
        ].copy()
        top_eficientes.columns = ['Cliente', 'Reportes', 'Tiempo Cierre (días)', 'Cierre (%)']
        st.dataframe(top_eficientes, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("##### ⚠️ Top 5 Clientes Críticos")
        top_criticos = clientes_performance[clientes_performance['categoria_rendimiento'] == '🔴 Crítico'].head(5)[
            ['codigo_cliente_display', 'total_reportes', 'tiempo_promedio_cierre', 'tasa_cierre']
        ].copy()
        if not top_criticos.empty:
            top_criticos.columns = ['Cliente', 'Reportes', 'Tiempo Cierre (días)', 'Cierre (%)']
            st.dataframe(top_criticos, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 No hay clientes en estado crítico!")
    
    # Insights automáticos
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h4 style="color: white; margin: 0;">🧠 Insights de Rendimiento</h4>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            🏆 <strong>Mejor usuario:</strong> {usuarios_performance.loc[usuarios_performance['eficiencia'].idxmax(), 'usuario']} 
            (Eficiencia: {usuarios_performance['eficiencia'].max():.2f})
        </p>        <p style="color: white; margin: 10px 0; font-size: 16px;">
            🎯 <strong>Motivo más eficiente:</strong> {motivos_analysis.loc[motivos_analysis['tiempo_promedio_cierre'].idxmin(), 'motivo']} 
            (Tiempo: {motivos_analysis['tiempo_promedio_cierre'].min():.2f} días)
        </p>
        <p style="color: white; margin: 10px 0; font-size: 16px;">
            📊 <strong>Clientes críticos:</strong> {len(clientes_performance[clientes_performance['categoria_rendimiento'] == '🔴 Crítico'])} 
            requieren atención inmediata
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_advanced_analysis(df, merged_df):
    """Análisis avanzado enfocado en Clientes y gráficas especializadas"""
    st.subheader("📊 Análisis Avanzado de Clientes e Insights Profundos")
    
    # Preparar datos de clientes - formatear correctamente el código de cliente
    df['codigo_cliente_display'] = df['codigo_cliente'].apply(lambda x: f"Cliente-{str(x).zfill(6)}")    # === FILTROS PARA ANÁLISIS DE CLIENTES ===
    st.markdown("#### 🔍 Filtros de Análisis")
    st.markdown("Utilice los siguientes filtros para refinar el análisis de clientes según sus necesidades.")
    # Cambiamos de 3 a 4 columnas para agregar el nuevo filtro
    col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
    
    with col_filtro1:
        # Filtro por Tipo de Reporte (antes llamado Motivo) - usa motivo_retro
        tipos_reporte_disp = ['Todos']
        if 'motivo_retro' in df.columns:
            tipos_reporte_disp += sorted([str(m) for m in df['motivo_retro'].dropna().unique().tolist()])
        tipo_reporte_filtro = st.selectbox("📋 Filtrar por Tipo de Reporte:", tipos_reporte_disp, key="cliente_tipo_reporte_filtro")
    
    with col_filtro2:
        # Filtro por Motivo (nuevo) - usa respuesta_sub
        motivos_disp = ['Todos']
        if 'respuesta_sub' in df.columns:
            motivos_disp += sorted([str(m) for m in df['respuesta_sub'].dropna().unique().tolist()])
        motivo_filtro = st.selectbox("🎯 Filtrar por Motivo:", motivos_disp, key="cliente_motivo_filtro")
    
    with col_filtro3:
        # Filtro por Cliente
        clientes_disp = ['Todos']
        clientes_disp += sorted([c for c in df['codigo_cliente_display'].dropna().unique().tolist()])
        cliente_filtro = st.selectbox("👥 Filtrar por Cliente:", clientes_disp, key="cliente_id_filtro")
    
    with col_filtro4:
        # Filtro por Frecuencia de reportes
        frecuencia_options = [
            'Todos',
            '1 reporte',
            '2-4 reportes',
            '5-10 reportes',
            'Más de 10 reportes'
        ]
        frecuencia_filtro = st.selectbox("📊 Filtrar por Frecuencia de Reportes:", 
                                         frecuencia_options, key="cliente_frecuencia_filtro")
      # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro por Tipo de Reporte (motivo_retro)
    if tipo_reporte_filtro != 'Todos' and 'motivo_retro' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['motivo_retro'] == tipo_reporte_filtro]
    
    # Filtro por Motivo (respuesta_sub)
    if motivo_filtro != 'Todos' and 'respuesta_sub' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['respuesta_sub'] == motivo_filtro]
    
    # Filtro por Cliente
    if cliente_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['codigo_cliente_display'] == cliente_filtro]
      # === SECCIÓN 1: TOP CLIENTES PROBLEMÁTICOS ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Top 20 Clientes con Más Reportes</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis completo de clientes con dataframe filtrado
    clientes_analysis = df_filtrado.groupby(['codigo_cliente', 'codigo_cliente_display']).agg({
        'id_tema': 'count',
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
        'tiempo_cierre_dias': 'mean',
        'fecha_cierre': lambda x: x.notna().sum(),
        'ruta': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A',
        'usuario': 'nunique'
    }).round(2).reset_index()    
    clientes_analysis.columns = ['codigo_cliente', 'codigo_cliente_display', 'total_reportes', 'motivo_principal', 'tiempo_promedio_cierre', 'casos_cerrados', 'ruta_principal', 'usuarios_involucrados']
    clientes_analysis['tasa_cierre'] = (clientes_analysis['casos_cerrados'] / clientes_analysis['total_reportes']) * 100
    
    # Aplicar filtro de frecuencia después de agrupar
    if frecuencia_filtro != 'Todos':
        if frecuencia_filtro == '1 reporte':
            clientes_analysis = clientes_analysis[clientes_analysis['total_reportes'] == 1]
        elif frecuencia_filtro == '2-4 reportes':
            clientes_analysis = clientes_analysis[(clientes_analysis['total_reportes'] >= 2) & 
                                               (clientes_analysis['total_reportes'] <= 4)]
        elif frecuencia_filtro == '5-10 reportes':
            clientes_analysis = clientes_analysis[(clientes_analysis['total_reportes'] >= 5) & 
                                               (clientes_analysis['total_reportes'] <= 10)]
        elif frecuencia_filtro == 'Más de 10 reportes':
            clientes_analysis = clientes_analysis[clientes_analysis['total_reportes'] > 10]
    
    clientes_analysis = clientes_analysis.sort_values('total_reportes', ascending=False)
      # Crear categorías de riesgo para TODOS los clientes
    clientes_analysis['categoria_riesgo'] = clientes_analysis.apply(lambda x: 
        'Alto Riesgo' if x['total_reportes'] >= 10 and x['tasa_cierre'] < 50 else
        'Riesgo Medio' if x['total_reportes'] >= 5 and x['tasa_cierre'] < 70 else
        'Bajo Riesgo', axis=1)      # Mostrar info de clientes en los filtros actuales
    total_clientes_filtrados = len(clientes_analysis)
    
    # Crear mensaje descriptivo de filtros aplicados
    filtros_aplicados = []
    if tipo_reporte_filtro != 'Todos':
        filtros_aplicados.append(f"Tipo de Reporte: {tipo_reporte_filtro}")
    if motivo_filtro != 'Todos':
        filtros_aplicados.append(f"Motivo: {motivo_filtro}")
    if cliente_filtro != 'Todos':
        filtros_aplicados.append(f"Cliente: {cliente_filtro}")
    if frecuencia_filtro != 'Todos':
        filtros_aplicados.append(f"Frecuencia: {frecuencia_filtro}")
    
    filtros_mensaje = ", ".join(filtros_aplicados) if filtros_aplicados else "ninguno"
    st.info(f"📊 Se encontraron {total_clientes_filtrados} clientes con los filtros seleccionados. Filtros aplicados: {filtros_mensaje}.")
    
    # Top 20 clientes problemáticos o todos si hay menos de 20
    if total_clientes_filtrados == 0:
        st.warning("⚠️ No hay clientes que cumplan con los criterios de filtrado seleccionados.")
        top_clientes = pd.DataFrame()  # DataFrame vacío para manejar el caso de no resultados
    else:
        top_clientes = clientes_analysis.head(20).copy()
      # Gráfico principal de barras horizontal con mejor diseño
    if not top_clientes.empty:
        fig_clientes_main = px.bar(
            top_clientes,
            x='total_reportes',
            y='codigo_cliente_display',
            orientation='h',
            title="🎯 Top 20 Clientes Problemáticos",
            color='categoria_riesgo',
            color_discrete_map={
                'Alto Riesgo': '#FF4B4B',
                'Riesgo Medio': '#FFA500', 
                'Bajo Riesgo': '#32CD32'
            },
            height=800,
        text='total_reportes',        
        hover_data={
            'codigo_cliente_display': True,
            'total_reportes': True,
            'tasa_cierre': ':.1f',
            'tiempo_promedio_cierre': ':.2f',
            'motivo_principal': True,
            'ruta_principal': True
        }
    )
    fig_clientes_main.update_traces(
        texttemplate='<b>%{text} reportes</b>',        
        textposition='outside',
        marker_line_width=2,
        marker_line_color='white',
        textfont=dict(size=12, color='white', family='Arial Black')
    )
    fig_clientes_main.update_layout(
        yaxis={
            'categoryorder': 'total ascending',
            'tickfont': dict(size=11, color='white'),
            'title': '<b>Código de Cliente</b>'
        },
        xaxis_title="<b>Número Total de Reportes</b>",
        margin=dict(l=200, r=100, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_clientes_main, use_container_width=True)    # === SECCIÓN 2: HEATMAP DE CLIENTES VS MESES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🌡️ Heatmap: Intensidad de Reportes por Cliente y Mes</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de intensidad temporal de los top 15 clientes más problemáticos
    top_15_clientes = clientes_analysis.head(15)['codigo_cliente'].tolist()
    
    # Filtrar datos temporales para estos clientes
    df_heatmap = df[df['codigo_cliente'].isin(top_15_clientes)].copy()
    
    if not df_heatmap.empty:
        # Crear matriz de clientes vs meses
        heatmap_data = df_heatmap.groupby(['codigo_cliente_display', 'mes_nombre']).agg({
            'id_tema': 'count'
        }).reset_index()
        heatmap_data.columns = ['Cliente', 'Mes', 'Reportes']
        
        # Crear pivot table para el heatmap
        heatmap_pivot = heatmap_data.pivot(index='Cliente', columns='Mes', values='Reportes').fillna(0)
        
        # Ordenar columnas cronológicamente
        meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        heatmap_pivot = heatmap_pivot.reindex(columns=[mes for mes in meses_orden if mes in heatmap_pivot.columns])
        
        # Crear heatmap
        fig_heatmap = px.imshow(
            heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            color_continuous_scale='Reds',
            title="🌡️ Intensidad de Reportes: Top 15 Clientes vs Meses",
            aspect='auto',
            height=700
        )        
        fig_heatmap.update_traces(
            text=heatmap_pivot.values,
            texttemplate='%{text}',
            textfont=dict(size=12, color='white')
        )
        fig_heatmap.update_layout(
            xaxis_title="<b>Mes</b>",
            yaxis_title="<b>Cliente</b>",
            margin=dict(l=200, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12)
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Insights del heatmap
        cliente_mas_activo = heatmap_pivot.sum(axis=1).idxmax()
        mes_mas_problematico = heatmap_pivot.sum(axis=0).idxmax()
        pico_maximo = heatmap_pivot.max().max()
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h4 style="color: white; margin: 0;">📊 Insights del Heatmap</h4>
            <p style="color: white; margin: 10px 0; font-size: 14px;">
                🔥 <strong>Cliente más activo:</strong> {cliente_mas_activo}<br>
                📅 <strong>Mes más problemático:</strong> {mes_mas_problematico}<br>
                ⚡ <strong>Pico máximo:</strong> {pico_maximo} reportes en un mes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("ℹ️ No hay suficientes datos temporales para mostrar el heatmap")
    
    # === SECCIÓN 2.1: DISTRIBUCIÓN POR MOTIVOS PRINCIPALES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🎯 Top 10 Motivos Principales</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Distribución por motivo principal
    if not clientes_analysis.empty:
        motivos_distribucion = clientes_analysis['motivo_principal'].value_counts().head(10).reset_index()
        motivos_distribucion.columns = ['motivo_principal', 'cantidad_clientes']
        
        fig_motivos_bar = px.bar(
            motivos_distribucion,
            x='cantidad_clientes',
            y='motivo_principal',
            orientation='h',
            title="🎯 Top 10 Motivos Principales por Cantidad de Clientes",
            color='cantidad_clientes',
            color_continuous_scale='Viridis',
            height=600,
            text='cantidad_clientes'
        )
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar la distribución de motivos con los filtros actuales.")
        motivos_distribucion = pd.DataFrame()    
        if not motivos_distribucion.empty:
            fig_motivos_bar.update_traces(
            texttemplate='<b>%{text} clientes</b>',
            textposition='outside',
            marker_line_width=1,
            marker_line_color='white',
            textfont=dict(size=12, color='white')
        )
        fig_motivos_bar.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': dict(size=11, color='white'),
                'title': '<b>Motivo del Reporte</b>'
            },
            xaxis_title="<b>Cantidad de Clientes</b>",
            margin=dict(l=200, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12)
        )
        
        st.plotly_chart(fig_motivos_bar, use_container_width=True)
    
    # === SECCIÓN 3.1: ANÁLISIS DE FRECUENCIA DE REPORTES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📈 Análisis de Frecuencia de Reportes por Cliente</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Análisis de distribución por frecuencia de reportes
    def clasificar_frecuencia(reportes):
        if reportes >= 15:
            return '15+ reportes (Crítico)'
        elif reportes >= 10:
            return '10-14 reportes (Alto)'
        elif reportes >= 5:
            return '5-9 reportes (Medio)'
        elif reportes >= 2:
            return '2-4 reportes (Bajo)'
        else:
            return '1 reporte (Mínimo)'
    if not clientes_analysis.empty:
        clientes_analysis['frecuencia_categoria'] = clientes_analysis['total_reportes'].apply(clasificar_frecuencia)
        
        # Contar clientes por frecuencia
        distribucion_frecuencia = clientes_analysis['frecuencia_categoria'].value_counts().reset_index()
        distribucion_frecuencia.columns = ['frecuencia_categoria', 'cantidad_clientes']
        
        # Ordenar de manera lógica
        orden_frecuencia = ['1 reporte (Mínimo)', '2-4 reportes (Bajo)', '5-9 reportes (Medio)', '10-14 reportes (Alto)', '15+ reportes (Crítico)']
        distribucion_frecuencia['frecuencia_categoria'] = pd.Categorical(distribucion_frecuencia['frecuencia_categoria'], categories=orden_frecuencia, ordered=True)
        distribucion_frecuencia = distribucion_frecuencia.sort_values('frecuencia_categoria')
          # Gráfico de distribución de frecuencia
        fig_frecuencia = px.bar(
            distribucion_frecuencia,
            x='frecuencia_categoria',
            y='cantidad_clientes',
            title="📈 Distribución de Clientes por Frecuencia de Reportes",
            color='cantidad_clientes',
            color_continuous_scale='Plasma',
            height=600,
            text='cantidad_clientes'
        )
        
        fig_frecuencia.update_traces(
            texttemplate='<b>%{text} clientes</b>',
            textposition='outside',
            marker_line_width=2,
            marker_line_color='white',
            textfont=dict(size=14, color='white', family='Arial Black')
        )
        
        fig_frecuencia.update_layout(
            xaxis_title="<b>Categoría de Frecuencia</b>",
            yaxis_title="<b>Cantidad de Clientes</b>",
            margin=dict(l=50, r=50, t=80, b=100),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig_frecuencia, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles para mostrar la distribución de frecuencia con los filtros actuales.")
      # Insight sobre la distribución
    if not clientes_analysis.empty:
        clientes_criticos = len(clientes_analysis[clientes_analysis['total_reportes'] >= 10])
        porcentaje_criticos = (clientes_criticos / len(clientes_analysis)) * 100 if len(clientes_analysis) > 0 else 0
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
            <h4 style="color: white; margin: 0;">🎯 Insights de Frecuencia</h4>
            <p style="color: white; margin: 10px 0; font-size: 16px;">
                📊 <strong>{clientes_criticos}</strong> clientes tienen 10+ reportes ({porcentaje_criticos:.1f}% del total)
            </p>
            <p style="color: white; margin: 10px 0; font-size: 14px;">
                💡 <strong>Recomendación:</strong> Estos clientes de alta frecuencia requieren atención prioritaria y seguimiento especializado.
            </p>
        </div>
        """, unsafe_allow_html=True)# === SECCIÓN 3: ANÁLISIS DE DISTRIBUCIÓN DE TIEMPO DE CIERRE ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Distribución de Tiempo de Cierre por Cliente</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Crear análisis de distribución de tiempo de cierre
    if not clientes_analysis.empty:
        # Clasificar clientes por rango de tiempo de cierre
        def clasificar_tiempo_cierre(tiempo):
            if tiempo <= 2:
                return 'Muy Rápido (≤2 días)'
            elif tiempo <= 5:
                return 'Rápido (3-5 días)'
            elif tiempo <= 10:
                return 'Moderado (6-10 días)'
            else:
                return 'Lento (>10 días)'
        
        clientes_analysis['rango_tiempo_cierre'] = clientes_analysis['tiempo_promedio_cierre'].apply(clasificar_tiempo_cierre)
        
        # Contar clientes por rango de tiempo de cierre
        distribucion_tiempo = clientes_analysis['rango_tiempo_cierre'].value_counts().reset_index()
        distribucion_tiempo.columns = ['rango_tiempo_cierre', 'cantidad_clientes']
        
        # Ordenar de manera lógica (mejor rendimiento primero)
        orden_rangos = ['Muy Rápido (≤2 días)', 'Rápido (3-5 días)', 'Moderado (6-10 días)', 'Lento (>10 días)']
        distribucion_tiempo['rango_tiempo_cierre'] = pd.Categorical(distribucion_tiempo['rango_tiempo_cierre'], categories=orden_rangos, ordered=True)
        distribucion_tiempo = distribucion_tiempo.sort_values('rango_tiempo_cierre')
        
        # Gráfico de barras de distribución
        fig_distribucion = px.bar(
            distribucion_tiempo,
            x='rango_tiempo_cierre',
            y='cantidad_clientes',
            title="📊 Distribución de Clientes por Tiempo de Cierre",
            color='cantidad_clientes',
            color_continuous_scale='RdYlGn',
            height=600,
            text='cantidad_clientes'
        )
        fig_distribucion.update_traces(
            texttemplate='<b>%{text} clientes</b>',
            textposition='outside',
            marker_line_width=2,
            marker_line_color='white',
            textfont=dict(size=14, color='white', family='Arial Black')
        )
        
        fig_distribucion.update_layout(
            xaxis_title="<b>Rango de Tiempo de Cierre</b>",
            yaxis_title="<b>Cantidad de Clientes</b>",
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig_distribucion, use_container_width=True)
        
        # Análisis adicional por categoría de riesgo y tiempo
        st.markdown("##### 📋 Análisis Cruzado: Riesgo vs Tiempo de Cierre")
        
        analisis_cruzado = clientes_analysis.groupby(['categoria_riesgo', 'rango_tiempo_cierre']).agg({
            'codigo_cliente': 'count',
            'total_reportes': 'sum'
        }).reset_index()
        analisis_cruzado.columns = ['Categoría de Riesgo', 'Rango de Tiempo', 'Cantidad de Clientes', 'Total Reportes']
        
        if not analisis_cruzado.empty:
            st.dataframe(clean_dataframe_for_display(analisis_cruzado), use_container_width=True)
            
            # Insights automáticos
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h4 style="color: white; margin: 0;">💡 Insights de Puntuación</h4>
                <ul style="color: white; margin: 10px 0;">
                    <li><strong>🎯 Objetivo:</strong> Identificar patrones entre satisfacción del cliente y frecuencia de reportes</li>
                    <li><strong>📈 Análisis:</strong> Clientes con puntuaciones bajas pero pocos reportes pueden necesitar seguimiento</li>
                    <li><strong>⚠️ Alertas:</strong> Clientes con puntuaciones altas pero muchos reportes requieren atención especial</li>
                    <li><strong>🎪 Acción:</strong> Priorizar clientes de alto riesgo con puntuaciones bajas</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No hay datos suficientes para mostrar la distribución de puntuaciones")
    
    # === SECCIÓN 4: ANÁLISIS DE REPORTES REPETITIVOS ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🔍 Clientes con Reportes Repetitivos del Mismo Motivo</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
      # Analizar clientes que tienen múltiples reportes del mismo motivo
    cliente_motivo_analysis = df.groupby(['codigo_cliente', 'codigo_cliente_display', 'respuesta_sub']).agg({
        'id_tema': 'count',
        'tiempo_cierre_dias': 'mean',
        'fecha_cierre': lambda x: x.notna().sum(),
        'ruta': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A'
    }).round(2).reset_index()
    cliente_motivo_analysis.columns = ['codigo_cliente', 'codigo_cliente_display', 'motivo_real', 'total_reportes', 'tiempo_promedio_cierre', 'casos_cerrados', 'ruta_principal']
    
    # Filtrar clientes con 3+ reportes del mismo motivo
    clientes_repetitivos = cliente_motivo_analysis[cliente_motivo_analysis['total_reportes'] >= 3].sort_values('total_reportes', ascending=False)
    if not clientes_repetitivos.empty:
        st.markdown(f"##### 🎯 Se encontraron {len(clientes_repetitivos)} casos de clientes con 3+ reportes del mismo motivo")
          # Gráfico de clientes repetitivos - FILA COMPLETA
        fig_repetitivos = px.bar(
            clientes_repetitivos.head(15),
            x='total_reportes',
            y='codigo_cliente_display',
            orientation='h',
            title="🚨 Top 15 Casos de Reportes Repetitivos",
            color='motivo_real',
            height=900,
            text='total_reportes',            hover_data={
                'codigo_cliente_display': True,
                'motivo_real': True,
                'tiempo_promedio_cierre': ':.2f',
                'casos_cerrados': True,
                'ruta_principal': True
            }
        )
        fig_repetitivos.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=2,
            marker_line_color='white',
            textfont=dict(size=14, color='white', family='Arial Black')
        )        
        fig_repetitivos.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': dict(size=12, color='white')
            },
            xaxis_title="<b>Reportes del Mismo Motivo</b>",
            yaxis_title="<b>Cliente</b>",
            margin=dict(l=250, r=100, t=100, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        st.plotly_chart(fig_repetitivos, use_container_width=True)
        
        # === ANÁLISIS DE MOTIVOS MÁS PROBLEMÁTICOS - FILA COMPLETA ===
        st.markdown(
            """
            <div class="analysis-card">
                <h3 style="color: white; margin: 0;">🎯 Análisis de Motivos Más Problemáticos</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
          # Análisis de motivos más problemáticos
        motivos_problematicos = clientes_repetitivos.groupby('motivo_real').agg({
            'codigo_cliente': 'count',
            'total_reportes': 'sum',
            'tiempo_promedio_cierre': 'mean',
            'casos_cerrados': 'sum'
        }).round(2).reset_index()
        motivos_problematicos.columns = ['motivo_real', 'clientes_afectados', 'total_reportes_acumulados', 'tiempo_promedio_cierre', 'casos_cerrados_total']
        motivos_problematicos['tasa_resolucion'] = (motivos_problematicos['casos_cerrados_total'] / motivos_problematicos['total_reportes_acumulados']) * 100
        motivos_problematicos = motivos_problematicos.sort_values('clientes_afectados', ascending=False).head(10)
        
        fig_motivos_problematicos = px.bar(
            motivos_problematicos,
            x='clientes_afectados',
            y='motivo_real',
            orientation='h',
            title="🎯 Top 10 Motivos Más Problemáticos",
            color='tasa_resolucion',
            color_continuous_scale='RdYlGn',
            height=700,
            text='clientes_afectados',
            hover_data={
                'motivo_real': True,
                'clientes_afectados': True,
                'total_reportes_acumulados': True,
                'tasa_resolucion': ':.1f'
            }
        )
        
        fig_motivos_problematicos.update_traces(
            texttemplate='%{text} clientes',
            textposition='outside',
            marker_line_width=1,
            marker_line_color='white',
            textfont=dict(size=11, color='white')
        )        
        fig_motivos_problematicos.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': dict(size=10, color='white')
            },
            xaxis_title="<b>Clientes Afectados</b>",
            yaxis_title="<b>Motivo del Reporte</b>",
            margin=dict(l=200, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=11)
        )
        
        st.plotly_chart(fig_motivos_problematicos, use_container_width=True)
          # Tabla resumen de clientes repetitivos críticos
        st.markdown("##### 📋 Clientes Críticos con Reportes Repetitivos")
        clientes_criticos = clientes_repetitivos[clientes_repetitivos['total_reportes'] >= 5].copy()
        
        if not clientes_criticos.empty:
            clientes_criticos_display = clientes_criticos[['codigo_cliente_display', 'motivo_real', 'total_reportes', 'tiempo_promedio_cierre', 'casos_cerrados', 'ruta_principal']].copy()
            clientes_criticos_display.columns = ['Cliente', 'Motivo Repetitivo', 'Total Reportes', 'Tiempo Promedio Cierre (días)', 'Casos Cerrados', 'Ruta Principal']
            st.dataframe(clean_dataframe_for_display(clientes_criticos_display), use_container_width=True)
        else:
            st.success("✅ No hay clientes con 5+ reportes repetitivos del mismo motivo")
    else:
        st.success("✅ No se encontraron clientes con reportes repetitivos significativos")      # === SECCIÓN 5: ANÁLISIS GEOGRÁFICO POR RUTAS ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🗺️ Análisis Geográfico por Rutas</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Distribución de clientes problemáticos por ruta
    clientes_rutas = df.groupby(['ruta', 'codigo_cliente', 'codigo_cliente_display']).agg({
        'id_tema': 'count',
        'respuesta_sub': lambda x: x.mode().iloc[0] if not x.empty and len(x.mode()) > 0 else 'N/A'
    }).reset_index()
    clientes_rutas.columns = ['ruta', 'codigo_cliente', 'codigo_cliente_display', 'reportes', 'motivo_principal']
    
    # Rutas con más clientes problemáticos (3+ reportes)
    clientes_problematicos_por_ruta = clientes_rutas[clientes_rutas['reportes'] >= 3].groupby('ruta').agg({
        'codigo_cliente': 'count',
        'reportes': 'sum'
    }).reset_index()
    clientes_problematicos_por_ruta.columns = ['ruta', 'clientes_problematicos', 'total_reportes']
    clientes_problematicos_por_ruta = clientes_problematicos_por_ruta.sort_values('clientes_problematicos', ascending=False).head(12)
    
    if not clientes_problematicos_por_ruta.empty:
        fig_rutas = px.bar(
            clientes_problematicos_por_ruta,
            x='clientes_problematicos',
            y='ruta',
            orientation='h',
            title="🗺️ Top 12 Rutas con Clientes Problemáticos",
            color='total_reportes',
            color_continuous_scale='Reds',
            height=600,
            text='clientes_problematicos',
            hover_data={
                'ruta': True,
                'clientes_problematicos': True,
                'total_reportes': True
            }
        )
        
        fig_rutas.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=1,
            marker_line_color='white',
            textfont=dict(size=11, color='white')
        )        
        fig_rutas.update_layout(
            yaxis={
                'categoryorder': 'total ascending',
                'tickfont': dict(size=10, color='white')
            },
            xaxis_title="<b>Clientes Problemáticos</b>",
            yaxis_title="<b>Ruta</b>",
            margin=dict(l=120, r=50, t=80, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=11)
        )
        
        st.plotly_chart(fig_rutas, use_container_width=True)
    else:
        st.success("✅ No se encontraron rutas con concentración alta de clientes problemáticos")
    
    # === HEATMAP DE RUTAS VS MOTIVOS ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🌡️ Heatmap: Rutas vs Motivos de Reporte</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Heatmap de rutas vs motivos
    if not clientes_rutas.empty:
        ruta_motivo_heatmap = df.groupby(['ruta', 'respuesta_sub']).size().reset_index(name='cantidad')
        # Tomar solo las rutas y motivos más comunes para mejor visualización
        top_rutas = ruta_motivo_heatmap.groupby('ruta')['cantidad'].sum().nlargest(10).index
        top_motivos = ruta_motivo_heatmap.groupby('respuesta_sub')['cantidad'].sum().nlargest(8).index
        
        heatmap_data = ruta_motivo_heatmap[
            (ruta_motivo_heatmap['ruta'].isin(top_rutas)) & 
            (ruta_motivo_heatmap['respuesta_sub'].isin(top_motivos))
        ]
        
        if not heatmap_data.empty:
            heatmap_pivot = heatmap_data.pivot(index='ruta', columns='respuesta_sub', values='cantidad').fillna(0)
            
            fig_heatmap = px.imshow(
                heatmap_pivot.values,
                x=heatmap_pivot.columns,
                y=heatmap_pivot.index,
                color_continuous_scale='Reds',
                title="🌡️ Heatmap: Rutas vs Motivos de Reporte",
                height=600,
                aspect='auto'
            )
            
            fig_heatmap.update_layout(
                xaxis_title="<b>Motivo del Reporte</b>",
                yaxis_title="<b>Ruta</b>",
                margin=dict(l=100, r=50, t=80, b=120),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=10),
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("ℹ️ No hay suficientes datos para mostrar el heatmap")
    else:
        st.info("ℹ️ No hay datos de rutas disponibles para el heatmap")
      # === SECCIÓN 6: EVOLUCIÓN TEMPORAL ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📅 Evolución Temporal de Clientes Problemáticos</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    top_5_clientes = clientes_analysis.head(5)['codigo_cliente'].tolist()
    top_5_display = clientes_analysis.head(5)['codigo_cliente_display'].tolist()
    
    if 'mes_nombre' in df.columns and top_5_clientes:
        # Crear mapping de meses con su número para ordenamiento correcto
        evolucion_clientes = df[df['codigo_cliente'].isin(top_5_clientes)].groupby(['mes', 'mes_nombre', 'codigo_cliente_display']).agg({
            'id_tema': 'count',
            'fecha_cierre': lambda x: x.notna().sum()
        }).reset_index()
        evolucion_clientes.columns = ['mes_num', 'mes', 'cliente', 'reportes', 'casos_cerrados']
        evolucion_clientes['tasa_cierre_mes'] = (evolucion_clientes['casos_cerrados'] / evolucion_clientes['reportes']) * 100
        
        # Ordenar correctamente por número de mes
        evolucion_clientes = evolucion_clientes.sort_values(['mes_num', 'cliente'])
        
        if not evolucion_clientes.empty:
            # Evolución de reportes - FILA COMPLETA
            fig_evolucion_reportes = px.line(
                evolucion_clientes,
                x='mes',
                y='reportes',
                color='cliente',
                title="📈 Evolución Mensual de Reportes - Top 5 Clientes",
                markers=True,
                height=600,
                category_orders={'mes': evolucion_clientes.sort_values('mes_num')['mes'].unique()}
            )
            
            fig_evolucion_reportes.update_traces(
                line_width=3, 
                marker_size=8,
                marker_line_width=2,
                marker_line_color='white'
            )
            
            fig_evolucion_reportes.update_layout(
                xaxis_title="<b>Mes</b>",
                yaxis_title="<b>Número de Reportes</b>",
                margin=dict(l=20, r=20, t=80, b=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                legend=dict(title="<b>Cliente</b>")
            )
            
            st.plotly_chart(fig_evolucion_reportes, use_container_width=True)
              # Evolución de tasa de cierre - FILA COMPLETA
            fig_evolucion_cierre = px.line(
                evolucion_clientes,
                x='mes',
                y='tasa_cierre_mes',
                color='cliente',
                title="📊 Evolución de Tasa de Cierre - Top 5 Clientes",
                markers=True,
                height=600,
                category_orders={'mes': evolucion_clientes.sort_values('mes_num')['mes'].unique()}
            )
            
            fig_evolucion_cierre.update_traces(
                line_width=3, 
                marker_size=8,
                marker_line_width=2,
                marker_line_color='white'
            )
            
            fig_evolucion_cierre.add_hline(
                y=70, 
                line_dash="dash", 
                line_color="yellow", 
                annotation_text="Meta 70%"
            )
            
            fig_evolucion_cierre.update_layout(
                xaxis_title="<b>Mes</b>",
                yaxis_title="<b>Tasa de Cierre (%)</b>",
                margin=dict(l=20, r=20, t=80, b=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                legend=dict(title="<b>Cliente</b>")
            )
            
            st.plotly_chart(fig_evolucion_cierre, use_container_width=True)
        else:
            st.info("ℹ️ No hay datos suficientes para mostrar evolución temporal")
      # === SECCIÓN 7: INSIGHTS Y RECOMENDACIONES ===
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">💡 Insights Inteligentes y Plan de Acción</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Generar insights automáticos
    insights_avanzados = []
    
    if not clientes_analysis.empty:
        # Estadísticas generales
        total_clientes = len(clientes_analysis)
        clientes_alto_riesgo = len(clientes_analysis[clientes_analysis['categoria_riesgo'] == 'Alto Riesgo'])
        cliente_mas_reportes = clientes_analysis.iloc[0]
        tasa_cierre_promedio = clientes_analysis['tasa_cierre'].mean()
        
        insights_avanzados.extend([
            f"📊 **Total de clientes analizados:** {total_clientes:,}",
            f"🚨 **Clientes de alto riesgo:** {clientes_alto_riesgo} ({(clientes_alto_riesgo/total_clientes)*100:.1f}%)",
            f"🥇 **Cliente más problemático:** {cliente_mas_reportes['codigo_cliente_display']} ({cliente_mas_reportes['total_reportes']} reportes)",
            f"📈 **Tasa de cierre promedio:** {tasa_cierre_promedio:.1f}%"
        ])
        
        if 'motivo_principal' in cliente_mas_reportes:
            insights_avanzados.append(f"🎯 **Motivo principal del cliente más problemático:** {cliente_mas_reportes['motivo_principal']}")
        
        # Análisis de eficiencia
        clientes_eficientes = clientes_analysis[clientes_analysis['tasa_cierre'] >= 80]
        if not clientes_eficientes.empty:
            insights_avanzados.append(f"✅ **Clientes con alta eficiencia (≥80% cierre):** {len(clientes_eficientes)}")
        
        clientes_criticos = clientes_analysis[
            (clientes_analysis['total_reportes'] >= 10) & 
            (clientes_analysis['tasa_cierre'] < 50)
        ]
        if not clientes_criticos.empty:
            insights_avanzados.append(f"⚠️ **Clientes críticos (10+ reportes, <50% cierre):** {len(clientes_criticos)}")
      # Mostrar insights y recomendaciones en dos columnas para ahorrar espacio
    col_insights, col_recomendaciones = st.columns(2)
    
    with col_insights:
        st.markdown("#### 📊 Insights Clave")
        for i, insight in enumerate(insights_avanzados, 1):
            st.markdown(f"{i}. {insight}")
    
    with col_recomendaciones:
        st.markdown("#### 🎯 Recomendaciones Estratégicas")
        recomendaciones_avanzadas = [
            "🔄 **Implementar programa de seguimiento personalizado** para clientes de alto riesgo",
            "📞 **Establecer contacto proactivo mensual** con top 10 clientes problemáticos",
            "📋 **Crear protocolo especial** para casos con 3+ reportes del mismo motivo",
            "⚡ **Priorizar resolución** de clientes críticos (alto volumen + baja eficiencia)",
            "📈 **Monitorear métricas semanales** de tasa de cierre por cliente",
            "🗺️ **Analizar rutas con concentración** de clientes problemáticos",
            "🎓 **Capacitar equipos** en motivos más frecuentes identificados",
            "📊 **Implementar dashboard de alerta temprana** para nuevos casos críticos"
        ]
        
        for rec in recomendaciones_avanzadas:
            st.markdown(rec)
    
    # === SECCIÓN 8: EXPORTAR ANÁLISIS ===
    st.markdown("---")
    st.markdown("### 📤 Exportar Análisis Completo")
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("💾 Exportar Top Clientes Problemáticos", key="export_top_clientes"):
            try:                
                export_data = clientes_analysis[['codigo_cliente_display', 'total_reportes', 'motivo_principal', 
                                               'tiempo_promedio_cierre', 'tasa_cierre', 'categoria_riesgo']].copy()
                export_data.columns = ['Cliente', 'Total Reportes', 'Motivo Principal', 'Tiempo Promedio Cierre (días)', 'Tasa Cierre (%)', 'Categoría Riesgo']
                
                csv = export_data.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"top_clientes_problematicos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
                st.success("✅ Datos preparados para exportar")
            except Exception as e:
                st.error(f"❌ Error al preparar exportación: {str(e)}")
    
    with col_export2:
        if st.button("📊 Exportar Análisis de Repetitivos", key="export_repetitivos"):
            try:
                if not clientes_repetitivos.empty:                    
                    export_repetitivos = clientes_repetitivos[['codigo_cliente_display', 'motivo_real', 'total_reportes', 
                                                             'tiempo_promedio_cierre', 'casos_cerrados', 'ruta_principal']].copy()
                    export_repetitivos.columns = ['Cliente', 'Motivo Repetitivo', 'Total Reportes', 'Tiempo Promedio Cierre (días)', 'Casos Cerrados', 'Ruta Principal']
                    
                    csv = export_repetitivos.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"clientes_repetitivos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                    st.success("✅ Datos preparados para exportar")
                else:
                    st.info("ℹ️ No hay datos de clientes repetitivos para exportar")
            except Exception as e:
                st.error(f"❌ Error al preparar exportación: {str(e)}")
    
    with col_export3:
        if st.button("🗺️ Exportar Análisis por Rutas", key="export_rutas"):
            try:
                if not clientes_problematicos_por_ruta.empty:
                    export_rutas = clientes_problematicos_por_ruta.copy()
                    export_rutas.columns = ['Ruta', 'Clientes Problemáticos', 'Total Reportes']
                    
                    csv = export_rutas.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"analisis_rutas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                    st.success("✅ Datos preparados para exportar")
                else:
                    st.info("ℹ️ No hay datos de rutas para exportar")
            except Exception as e:
                st.error(f"❌ Error al preparar exportación: {str(e)}")

def show_detailed_data(df, merged_df):
    """Muestra los datos detallados con filtros avanzados"""
    st.subheader("📋 Datos Detallados con Filtros Avanzados")
    
    # Verificar si hay datos disponibles
    if df.empty:
        st.warning("⚠️ No hay datos disponibles para mostrar con los filtros actuales.")
        return
    
    # Filtros básicos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tipos_reporte_unicos = ['Todos'] + sorted([str(m) for m in df['motivo_retro'].dropna().unique().tolist()])
        tipo_reporte_filtro = st.selectbox("📋 Filtrar por Tipo de Reporte", tipos_reporte_unicos, key="detailed_tipo_reporte_filtro")
    
    with col2:
        motivos_unicos = ['Todos'] + sorted([str(m) for m in df['respuesta_sub'].dropna().unique().tolist()])
        motivo_filtro = st.selectbox("🎯 Filtrar por Motivo", motivos_unicos, key="detailed_motivo_filtro")
    with col3:
        min_tiempo = int(df['tiempo_cierre_dias'].min()) if not df.empty and not df['tiempo_cierre_dias'].isna().all() else 0
        max_tiempo = int(df['tiempo_cierre_dias'].max()) if not df.empty and not df['tiempo_cierre_dias'].isna().all() else 30
        
        # Asegurar que min_value < max_value para el slider
        if min_tiempo >= max_tiempo:
            max_tiempo = min_tiempo + 30
        
        tiempo_filtro = st.slider("⏱️ Rango de Tiempo de Cierre (días)", min_tiempo, max_tiempo, (min_tiempo, max_tiempo), key="detailed_tiempo_filtro")
    with col4:
        solo_cerrados = st.checkbox("📋 Solo mostrar registros cerrados", key="detailed_solo_cerrados")
      # Aplicar filtros
    df_tabla = df.copy()
    
    if tipo_reporte_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['motivo_retro'] == tipo_reporte_filtro]
        
    if motivo_filtro != 'Todos':
        df_tabla = df_tabla[df_tabla['respuesta_sub'] == motivo_filtro]
    
    # Filtrar por tiempo de cierre solo si hay datos disponibles
    if not df_tabla['tiempo_cierre_dias'].isna().all():
        df_tabla = df_tabla[
            (df_tabla['tiempo_cierre_dias'] >= tiempo_filtro[0]) & 
            (df_tabla['tiempo_cierre_dias'] <= tiempo_filtro[1])
        ]
    
    if solo_cerrados:
        df_tabla = df_tabla[df_tabla['fecha_cierre'].notna()]
      # Crear mensaje descriptivo de filtros aplicados
    filtros_aplicados = []
    if tipo_reporte_filtro != 'Todos':
        filtros_aplicados.append(f"Tipo de Reporte: {tipo_reporte_filtro}")
    if motivo_filtro != 'Todos':
        filtros_aplicados.append(f"Motivo: {motivo_filtro}")
    if tiempo_filtro != (min_tiempo, max_tiempo):
        filtros_aplicados.append(f"Tiempo de cierre: entre {tiempo_filtro[0]} y {tiempo_filtro[1]} días")
    if solo_cerrados:
        filtros_aplicados.append("Solo registros cerrados")
    
    filtros_mensaje = ", ".join(filtros_aplicados) if filtros_aplicados else "ninguno"
    st.info(f"🔍 Filtros aplicados: {filtros_mensaje}")
    
    # Mostrar estadísticas
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("📊 Total de Registros", len(df_tabla))
    with col_stats2:
        tiempo_promedio = df_tabla['tiempo_cierre_dias'].mean() if not df_tabla.empty and not df_tabla['tiempo_cierre_dias'].isna().all() else 0
        st.metric("⏱️ Tiempo Promedio Cierre", f"{tiempo_promedio:.2f} días")
    
    with col_stats3:
        tasa_cierre = (df_tabla['fecha_cierre'].notna().sum() / len(df_tabla) * 100) if not df_tabla.empty else 0
        st.metric("📋 Tasa de Cierre", f"{tasa_cierre:.1f}%")
    
    # Sección de descarga de datos filtrados
    if not df_tabla.empty:
        st.markdown("---")
        st.markdown("### 📥 Descargar Datos Filtrados")
        
        col_download1, col_download2, col_download3 = st.columns(3)
        
        with col_download1:
            # Descarga CSV
            csv_data = df_tabla.to_csv(index=False)
            st.download_button(
                label="📄 Descargar CSV",
                data=csv_data,
                file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="download_csv_detailed"
            )
        
        with col_download2:
            # Descarga XLSX con análisis básico
            try:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    # Hoja principal con datos filtrados
                    df_export = clean_dataframe_for_display(df_tabla.copy())
                    df_export.to_excel(writer, sheet_name='Datos_Filtrados', index=False)
                    
                    # Hoja con resumen estadístico
                    if len(df_tabla) > 0:                        
                        resumen_stats = pd.DataFrame({
                            'Métrica': [
                                'Total de Registros',
                                'Tiempo Promedio Cierre (días)',
                                'Tasa de Cierre (%)',
                                'Rutas Únicas',
                                'Usuarios Únicos',
                                'Clientes Únicos',
                                'Registros Cerrados',
                                'Fecha de Exportación'
                            ],
                            'Valor': [
                                len(df_tabla),
                                round(df_tabla['tiempo_cierre_dias'].mean(), 2) if not df_tabla['tiempo_cierre_dias'].isna().all() else 0,
                                round(tasa_cierre, 1),
                                df_tabla['ruta'].nunique(),
                                df_tabla['usuario'].nunique(),
                                df_tabla['codigo_cliente'].nunique(),
                                df_tabla['fecha_cierre'].notna().sum(),
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            ]
                        })
                        resumen_stats.to_excel(writer, sheet_name='Resumen_Estadistico', index=False)
                    
                    # Aplicar formato
                    workbook = writer.book
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#D7E4BD',
                        'border': 1
                    })
                    
                    # Aplicar formato a las hojas
                    for sheet_name in writer.sheets:
                        worksheet = writer.sheets[sheet_name]
                        # Obtener las columnas del DataFrame correspondiente
                        if sheet_name == 'Datos_Filtrados':
                            columns = df_export.columns
                        elif sheet_name == 'Resumen_Estadistico' and len(df_tabla) > 0:
                            columns = resumen_stats.columns
                        else:
                            continue
                            
                        # Aplicar formato a los headers
                        for col_num, col_name in enumerate(columns):
                            worksheet.write(0, col_num, col_name, header_format)
                        
                        # Ajustar ancho de columnas
                        for i, col in enumerate(columns):
                            worksheet.set_column(i, i, 20)
                
                excel_buffer.seek(0)
                
                st.download_button(
                    label="📊 Descargar XLSX",
                    data=excel_buffer.getvalue(),
                    file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_xlsx_detailed"
                )
            except Exception as e:
                st.error(f"❌ Error generando XLSX: {str(e)}")
        
        with col_download3:
            # Información sobre los archivos
            with st.expander("ℹ️ Información de Descarga"):
                st.write("""
                **CSV**: Archivo de texto separado por comas, compatible con Excel y otros programas.
                
                **XLSX**: Archivo Excel con:
                - Hoja 1: Datos filtrados completos
                - Hoja 2: Resumen estadístico
                - Formato profesional con encabezados
                """)
    
    # Mostrar tabla
    if not df_tabla.empty:
        st.dataframe(clean_dataframe_for_display(df_tabla), use_container_width=True)
    else:
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")

if __name__ == "__main__":
    main()
