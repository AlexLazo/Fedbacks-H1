import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def add_day_hour_heatmap(df):
    """Agrega un análisis avanzado de patrones temporales mediante mapa de calor interactivo"""
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">⏰ Análisis Avanzado de Patrones Temporales</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if not df.empty:
        # Verificar que tenemos datos de fecha
        if 'fecha_registro' in df.columns:
            # Crear copias para no modificar el dataframe original
            df_analisis = df.copy()
            df_analisis['fecha_parsed'] = pd.to_datetime(df_analisis['fecha_registro'], errors='coerce')
            
            # Extraer día de la semana y mes para análisis simplificado (sin horas)
            df_analisis['dia_semana'] = df_analisis['fecha_parsed'].dt.day_name()
            df_analisis['mes'] = df_analisis['fecha_parsed'].dt.month_name()
            df_analisis['semana_año'] = df_analisis['fecha_parsed'].dt.isocalendar().week
            
            # Agregar columna para período del día (por turno en vez de hora exacta)
            df_analisis['periodo_dia'] = 'Jornada Completa'  # Valor por defecto
            
            # UI para opciones de visualización
            col1, col2 = st.columns([1, 1])
            with col1:
                color_scale = st.selectbox(
                    "🎨 Paleta de colores:", 
                    ['Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis', 'Turbo', 'YlOrRd', 'YlGnBu', 'RdBu'],
                    index=0,
                    key="heatmap_color"
                )
            with col2:
                normalizar = st.checkbox("📊 Normalizar por día", value=False, key="normalize_heatmap")
            
            # Vista principal: Mapa de calor por día (sin desglose por hora)
            # Contar registros por día 
            heatmap_data = df_analisis.groupby(['dia_semana']).size().reset_index()
            heatmap_data.columns = ['Día', 'Cantidad']
            
            # Ordenar días de la semana
            dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dias_spanish = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            dias_map = dict(zip(dias_orden, dias_spanish))
            
            # Traducir nombres de días
            heatmap_data['Día_ES'] = heatmap_data['Día'].map(dias_map)
            heatmap_data['Orden'] = heatmap_data['Día'].apply(lambda x: dias_orden.index(x) if x in dias_orden else 7)
            heatmap_data = heatmap_data.sort_values('Orden')
              # Crear gráfico de barras por día
            if normalizar:
                total = heatmap_data['Cantidad'].sum()
                if total > 0:
                    heatmap_data['Porcentaje'] = (heatmap_data['Cantidad'] / total) * 100
                    y_value = 'Porcentaje'
                    titulo = "⏰ Distribución Porcentual de Actividad por Día"
                    escala = "% del Total"
                    formato = ".1f"
                else:
                    y_value = 'Cantidad'
                    titulo = "⏰ Cantidad de Actividad por Día"
                    escala = "Cantidad de Registros"
                    formato = ".0f"
            else:
                y_value = 'Cantidad'
                titulo = "⏰ Cantidad de Actividad por Día"
                escala = "Cantidad de Registros"
                formato = ".0f"
            
            # Crear gráfico de barras
            fig_heatmap = px.bar(
                heatmap_data,
                x='Día_ES',
                y=y_value,
                color=y_value,
                color_continuous_scale=color_scale,
                title=titulo,
                text_auto=True
            )
            fig_heatmap.update_layout(
                xaxis_title="<b>Día de la Semana</b>",
                yaxis_title=f"<b>{escala}</b>",
                height=600,  # Aumentamos la altura para mejor visualización
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=14),
                margin=dict(l=50, r=50, t=80, b=50),  # Márgenes optimizados
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1                )
            )
            
            # Añadir anotaciones con los valores
            fig_heatmap.update_traces(
                texttemplate='%{y:.0f}',
                textposition='outside',
                textfont=dict(size=14, color='white')
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Pestañas para análisis adicionales
            tab1, tab2 = st.tabs(["📊 Insights", "📅 Tendencias Semanales"])
            
            with tab1:
                # Insights automáticos mejorados
                dia_data = heatmap_data.set_index('Día_ES')
                dia_pico = dia_data['Cantidad'].idxmax() if not dia_data.empty else "N/A"
                max_registros = dia_data['Cantidad'].max() if not dia_data.empty else 0
                
                # Días laborables vs fin de semana
                dias_laborables = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                dias_finde = ['Sábado', 'Domingo']
                
                registros_laborables = dia_data.loc[dia_data.index.isin(dias_laborables), 'Cantidad'].sum() if not dia_data.empty else 0
                registros_finde = dia_data.loc[dia_data.index.isin(dias_finde), 'Cantidad'].sum() if not dia_data.empty else 0
                total_registros = registros_laborables + registros_finde
                
                porcentaje_laborable = (registros_laborables / total_registros * 100) if total_registros > 0 else 0
                porcentaje_finde = (registros_finde / total_registros * 100) if total_registros > 0 else 0
                
                # Calcular variabilidad entre días
                if not dia_data.empty and len(dia_data) > 1:
                    coef_variacion = (dia_data['Cantidad'].std() / dia_data['Cantidad'].mean()) * 100 if dia_data['Cantidad'].mean() > 0 else 0
                else:
                    coef_variacion = 0
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
                    <h4 style="color: white; margin: 0;">⏰ Insights Avanzados de Patrones Temporales</h4>
                    <p style="color: white; margin: 10px 0; font-size: 14px;">
                        📅 <strong>Día más activo:</strong> {dia_pico} ({max_registros:.0f} registros)<br>
                        💼 <strong>Actividad en días laborables (L-V):</strong> {registros_laborables:.0f} registros ({porcentaje_laborable:.1f}%)<br>
                        🏖️ <strong>Actividad en fin de semana (S-D):</strong> {registros_finde:.0f} registros ({porcentaje_finde:.1f}%)<br>
                        🔄 <strong>Variabilidad entre días:</strong> {coef_variacion:.1f}% (un valor alto indica patrones diarios inconsistentes)<br>
                        💡 <strong>Recomendaciones:</strong><br>
                        → Planificar mayor personal durante {dia_pico}<br>
                        → {f"Distribuir recursos considerando mayor carga en días laborables" if porcentaje_laborable > porcentaje_finde else "Considerar reforzar personal en fines de semana"}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with tab2:
                # Análisis de tendencia semanal
                if 'semana_año' in df_analisis.columns:
                    df_semanal = df_analisis.groupby('semana_año').size().reset_index()
                    df_semanal.columns = ['Semana', 'Cantidad']
                    
                    # Crear gráfico de línea con tendencia
                    fig_semanal = px.line(
                        df_semanal,
                        x='Semana',
                        y='Cantidad',
                        title='📅 Tendencia de Actividad por Semana',
                        markers=True
                    )
                    
                    # Añadir línea de tendencia
                    fig_semanal.add_trace(
                        go.Scatter(
                            x=df_semanal['Semana'],
                            y=df_semanal['Cantidad'].rolling(window=3, min_periods=1).mean(),
                            name='Tendencia',
                            line=dict(color='rgba(255, 255, 255, 0.5)', width=3, dash='dot')
                        )
                    )
                    
                    fig_semanal.update_layout(
                        xaxis_title='Número de Semana',
                        yaxis_title='Cantidad de Registros',
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        hovermode='x unified',
                        legend=dict(orientation='h', y=1.1)
                    )
                    
                    st.plotly_chart(fig_semanal, use_container_width=True)
                    
                    # Detectar patrones cíclicos
                    if len(df_semanal) > 4:
                        try:
                            # Calcular autocorrelación para detectar patrones cíclicos
                            from statsmodels.tsa.stattools import acf
                            
                            autocorr = acf(df_semanal['Cantidad'].values, nlags=min(10, len(df_semanal)-1))
                            max_lag = np.argmax(autocorr[1:]) + 1
                            
                            if max_lag < len(autocorr):
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #118AB2 0%, #073B4C 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
                                    <h4 style="color: white; margin: 0;">📊 Patrón Cíclico Detectado</h4>
                                    <p style="color: white; margin: 10px 0; font-size: 14px;">
                                        Se detecta un posible patrón cíclico cada {max_lag} semanas con una correlación de {autocorr[max_lag]:.2f}.<br>
                                        <strong>Recomendación:</strong> Planificar recursos considerando ciclos de {max_lag} semanas.
                                    </p>                                </div>
                                """, unsafe_allow_html=True)
                        except:
                            pass
                else:
                    st.warning("No hay suficientes datos para el análisis de tendencias semanales")
        else:
            st.info("No se encontraron datos de fecha para analizar patrones por hora")
    else:
        st.warning("No hay datos suficientes para el análisis por hora y día")


def add_recurrence_analysis(df):
    """Añade análisis de reincidencia de clientes"""
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🔄 Análisis de Clientes Recurrentes</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if 'codigo_cliente' in df.columns and not df.empty:
        # Calcular frecuencia por cliente
        client_recurrence = df.groupby('codigo_cliente').agg({
            'id_tema': 'count',
            'fecha_registro': ['min', 'max']
        })
        
        client_recurrence.columns = ['total_reportes', 'primera_fecha', 'ultima_fecha']
        client_recurrence = client_recurrence.reset_index()
        
        # Calcular días entre primer y último reporte
        client_recurrence['dias_actividad'] = (client_recurrence['ultima_fecha'] - client_recurrence['primera_fecha']).dt.days
        client_recurrence['dias_actividad'] = client_recurrence['dias_actividad'].fillna(0).astype(int)
        
        # Calcular reportes por día de actividad
        client_recurrence['reportes_por_dia'] = client_recurrence.apply(
            lambda x: x['total_reportes'] / max(x['dias_actividad'], 1), axis=1
        ).round(2)
        
        # Clasificar clientes
        client_recurrence['categoria'] = client_recurrence.apply(
            lambda x: '🔴 Alta Reincidencia' if x['reportes_por_dia'] > 0.5 and x['total_reportes'] >= 5 else
                     '🟠 Reincidencia Media' if x['reportes_por_dia'] > 0.2 and x['total_reportes'] >= 3 else
                     '🟢 Esporádico', axis=1
        )
        
        # Mostrar conteo por categoría
        categories_count = client_recurrence['categoria'].value_counts().reset_index()
        categories_count.columns = ['Categoría', 'Cantidad']
        
        # Crear gráfico de barras
        fig_categories = px.bar(
            categories_count,
            x='Categoría',
            y='Cantidad',
            color='Categoría',
            color_discrete_map={
                '🔴 Alta Reincidencia': '#FF5252',
                '🟠 Reincidencia Media': '#FFA726',
                '🟢 Esporádico': '#66BB6A'
            },
            title='🔄 Distribución de Clientes por Patrón de Reincidencia',
            text='Cantidad'
        )
        
        fig_categories.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=2,
            marker_line_color='white'
        )
        
        fig_categories.update_layout(
            xaxis_title="<b>Categoría</b>",
            yaxis_title="<b>Cantidad de Clientes</b>",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12)
        )
        
        st.plotly_chart(fig_categories, use_container_width=True)
        
        # Top clientes recurrentes
        top_recurrent = client_recurrence[client_recurrence['categoria'] == '🔴 Alta Reincidencia'].sort_values('reportes_por_dia', ascending=False).head(10)
        
        if not top_recurrent.empty:
            st.markdown("#### 🚨 Top Clientes con Alta Reincidencia")
            
            # Preparar datos para mostrar
            top_display = top_recurrent[['codigo_cliente', 'total_reportes', 'dias_actividad', 'reportes_por_dia']].copy()
            top_display.columns = ['Cliente', 'Total Reportes', 'Días de Actividad', 'Reportes por Día']
            
            st.dataframe(top_display, use_container_width=True)
            
            # Insights
            total_clientes = len(client_recurrence)
            alta_reincidencia = len(client_recurrence[client_recurrence['categoria'] == '🔴 Alta Reincidencia'])
            media_reincidencia = len(client_recurrence[client_recurrence['categoria'] == '🟠 Reincidencia Media'])
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h4 style="color: white; margin: 0;">💡 Insights de Reincidencia</h4>
                <p style="color: white; margin: 10px 0; font-size: 14px;">
                    🚨 <strong>{alta_reincidencia} clientes</strong> ({(alta_reincidencia/total_clientes*100):.1f}%) muestran patrones de alta reincidencia<br>
                    ⚠️ <strong>{media_reincidencia} clientes</strong> ({(media_reincidencia/total_clientes*100):.1f}%) tienen reincidencia media<br>
                    💡 <strong>Recomendación:</strong> Implementar programa de seguimiento especial para los {alta_reincidencia} clientes identificados con alta reincidencia
                </p>
            </div>
            """, unsafe_allow_html=True)        
        else:
            st.success("✅ No se han identificado clientes con alta reincidencia")
    else:
        st.warning("No hay datos suficientes para el análisis de reincidencia")


def add_comparative_time_analysis(df):
    """Agrega un análisis comparativo de patrones temporales entre períodos"""
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">📊 Análisis Comparativo de Períodos</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if not df.empty:
        # Verificar que tenemos datos de fecha
        if 'fecha_registro' in df.columns:
            # Crear copia para no modificar el dataframe original
            df_temp = df.copy()
            df_temp['fecha_parsed'] = pd.to_datetime(df_temp['fecha_registro'], errors='coerce')
            
            # Añadir columnas de tiempo
            df_temp['mes'] = df_temp['fecha_parsed'].dt.month
            df_temp['mes_nombre'] = df_temp['fecha_parsed'].dt.month_name()
            df_temp['año'] = df_temp['fecha_parsed'].dt.year
            df_temp['semana'] = df_temp['fecha_parsed'].dt.isocalendar().week
            df_temp['dia_semana'] = df_temp['fecha_parsed'].dt.day_name()
            df_temp['hora'] = df_temp['fecha_parsed'].dt.hour
            
            # UI para selección de períodos y tipo de comparación
            col1, col2 = st.columns(2)
            
            # Obtener lista de meses y años disponibles
            meses = sorted(df_temp['mes'].unique())
            años = sorted(df_temp['año'].unique())
            
            # Mapeo de nombres de meses
            meses_nombres = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            
            with col1:
                tipo_comparacion = st.selectbox(
                    "📈 Tipo de comparación:", 
                    ["Meses", "Trimestres", "Semanas"],
                    key="tipo_comparacion"
                )
            
            with col2:
                metrica_analisis = st.selectbox(
                    "🔍 Métrica a analizar:", 
                    ["Volumen de actividad", "Distribución semanal", "Patrones por hora"],
                    key="metrica_analisis"
                )
            
            # Comparación entre períodos
            if tipo_comparacion == "Meses":
                if len(meses) >= 2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(años) > 1:
                            año_1 = st.selectbox("Año (Período 1):", años, index=len(años)-1, key="año_1")
                            meses_año = sorted([m for m, a in zip(df_temp['mes'], df_temp['año']) if a == año_1])
                        else:
                            año_1 = años[0]
                            meses_año = meses
                        
                        mes_1 = st.selectbox(
                            "Mes (Período 1):", 
                            meses_año,
                            format_func=lambda x: meses_nombres.get(x, f"Mes {x}"),
                            index=len(meses_año)-1 if len(meses_año) > 0 else 0,
                            key="mes_1"
                        )
                    
                    with col2:
                        if len(años) > 1:
                            año_2 = st.selectbox("Año (Período 2):", años, index=len(años)-1, key="año_2")
                            meses_año = sorted([m for m, a in zip(df_temp['mes'], df_temp['año']) if a == año_2])
                        else:
                            año_2 = años[0]
                            meses_año = meses
                            
                        mes_anterior_idx = meses_año.index(mes_1) - 1 if mes_1 in meses_año and meses_año.index(mes_1) > 0 else 0
                        mes_anterior_idx = max(0, min(mes_anterior_idx, len(meses_año) - 1))
                        
                        mes_2 = st.selectbox(
                            "Mes (Período 2):", 
                            meses_año,
                            format_func=lambda x: meses_nombres.get(x, f"Mes {x}"),
                            index=mes_anterior_idx,
                            key="mes_2"
                        )
                    
                    # Filtrar datos por los períodos seleccionados
                    datos_periodo_1 = df_temp[(df_temp['mes'] == mes_1) & (df_temp['año'] == año_1)]
                    datos_periodo_2 = df_temp[(df_temp['mes'] == mes_2) & (df_temp['año'] == año_2)]
                    
                    periodo_1_label = f"{meses_nombres.get(mes_1, f'Mes {mes_1}')} {año_1}"
                    periodo_2_label = f"{meses_nombres.get(mes_2, f'Mes {mes_2}')} {año_2}"
                    
                else:
                    st.info("No hay suficientes meses para realizar una comparación")
                    return
                
            elif tipo_comparacion == "Trimestres":
                # Mapeo de trimestres
                df_temp['trimestre'] = ((df_temp['mes'] - 1) // 3) + 1
                
                trimestres = sorted(df_temp['trimestre'].unique())
                
                if len(trimestres) >= 2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(años) > 1:
                            año_1 = st.selectbox("Año (Período 1):", años, index=len(años)-1, key="año_tri_1")
                            trim_año = sorted([t for t, a in zip(df_temp['trimestre'], df_temp['año']) if a == año_1])
                        else:
                            año_1 = años[0]
                            trim_año = trimestres
                        
                        trim_1 = st.selectbox(
                            "Trimestre (Período 1):", 
                            trim_año,
                            format_func=lambda x: f"Q{x}",
                            index=len(trim_año)-1 if len(trim_año) > 0 else 0,
                            key="trim_1"
                        )
                    
                    with col2:
                        if len(años) > 1:
                            año_2 = st.selectbox("Año (Período 2):", años, index=len(años)-1, key="año_tri_2")
                            trim_año = sorted([t for t, a in zip(df_temp['trimestre'], df_temp['año']) if a == año_2])
                        else:
                            año_2 = años[0]
                            trim_año = trimestres
                            
                        trim_anterior_idx = trim_año.index(trim_1) - 1 if trim_1 in trim_año and trim_año.index(trim_1) > 0 else 0
                        trim_anterior_idx = max(0, min(trim_anterior_idx, len(trim_año) - 1))
                        
                        trim_2 = st.selectbox(
                            "Trimestre (Período 2):", 
                            trim_año,
                            format_func=lambda x: f"Q{x}",
                            index=trim_anterior_idx,
                            key="trim_2"
                        )
                    
                    # Filtrar datos por los períodos seleccionados
                    datos_periodo_1 = df_temp[(df_temp['trimestre'] == trim_1) & (df_temp['año'] == año_1)]
                    datos_periodo_2 = df_temp[(df_temp['trimestre'] == trim_2) & (df_temp['año'] == año_2)]
                    
                    periodo_1_label = f"Q{trim_1} {año_1}"
                    periodo_2_label = f"Q{trim_2} {año_2}"
                else:
                    st.info("No hay suficientes trimestres para realizar una comparación")
                    return
            
            elif tipo_comparacion == "Semanas":
                semanas = sorted(df_temp['semana'].unique())
                
                if len(semanas) >= 2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(años) > 1:
                            año_1 = st.selectbox("Año (Período 1):", años, index=len(años)-1, key="año_sem_1")
                            sem_año = sorted([s for s, a in zip(df_temp['semana'], df_temp['año']) if a == año_1])
                        else:
                            año_1 = años[0]
                            sem_año = semanas
                        
                        sem_1 = st.selectbox(
                            "Semana (Período 1):", 
                            sem_año,
                            format_func=lambda x: f"Semana {x}",
                            index=len(sem_año)-1 if len(sem_año) > 0 else 0,
                            key="sem_1"
                        )
                    
                    with col2:
                        if len(años) > 1:
                            año_2 = st.selectbox("Año (Período 2):", años, index=len(años)-1, key="año_sem_2")
                            sem_año = sorted([s for s, a in zip(df_temp['semana'], df_temp['año']) if a == año_2])
                        else:
                            año_2 = años[0]
                            sem_año = semanas
                        
                        sem_anterior_idx = sem_año.index(sem_1) - 1 if sem_1 in sem_año and sem_año.index(sem_1) > 0 else 0
                        sem_anterior_idx = max(0, min(sem_anterior_idx, len(sem_año) - 1))
                        
                        sem_2 = st.selectbox(
                            "Semana (Período 2):", 
                            sem_año,
                            format_func=lambda x: f"Semana {x}",
                            index=sem_anterior_idx,
                            key="sem_2"
                        )
                    
                    # Filtrar datos por los períodos seleccionados
                    datos_periodo_1 = df_temp[(df_temp['semana'] == sem_1) & (df_temp['año'] == año_1)]
                    datos_periodo_2 = df_temp[(df_temp['semana'] == sem_2) & (df_temp['año'] == año_2)]
                    
                    periodo_1_label = f"Semana {sem_1} {año_1}"
                    periodo_2_label = f"Semana {sem_2} {año_2}"
                else:
                    st.info("No hay suficientes semanas para realizar una comparación")
                    return
            
            # Verificar si tenemos datos en ambos períodos
            if len(datos_periodo_1) == 0 or len(datos_periodo_2) == 0:
                st.warning(f"No hay suficientes datos para uno o ambos períodos seleccionados")
                return
            
            # Realizar visualización según la métrica seleccionada
            if metrica_analisis == "Volumen de actividad":
                # Contador por período
                conteo_p1 = len(datos_periodo_1)
                conteo_p2 = len(datos_periodo_2)
                
                # Mostrar métricas comparativas
                col1, col2, col3 = st.columns([2, 2, 3])
                
                with col1:
                    st.metric(
                        label=f"📊 {periodo_1_label}",
                        value=f"{conteo_p1:,}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        label=f"📊 {periodo_2_label}",
                        value=f"{conteo_p2:,}",
                        delta=f"{((conteo_p1 - conteo_p2) / max(conteo_p2, 1) * 100):.1f}%" if conteo_p2 > 0 else "N/A"
                    )
                
                with col3:
                    variacion_porcentual = ((conteo_p1 - conteo_p2) / max(conteo_p2, 1) * 100)
                    
                    if variacion_porcentual > 20:
                        emoji = "🚀"
                        mensaje = f"¡Aumento significativo de {variacion_porcentual:.1f}% entre períodos!"
                    elif variacion_porcentual > 5:
                        emoji = "📈"
                        mensaje = f"Aumento moderado de {variacion_porcentual:.1f}% entre períodos"
                    elif variacion_porcentual > -5:
                        emoji = "⚖️"
                        mensaje = f"Niveles estables entre períodos ({variacion_porcentual:.1f}%)"
                    elif variacion_porcentual > -20:
                        emoji = "📉"
                        mensaje = f"Disminución moderada de {-variacion_porcentual:.1f}% entre períodos"
                    else:
                        emoji = "🔻"
                        mensaje = f"¡Caída significativa de {-variacion_porcentual:.1f}% entre períodos!"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); padding: 15px; border-radius: 10px; text-align: center;">
                        <h4 style="color: white; margin: 0;">{emoji} Análisis de Variación</h4>
                        <p style="color: white; font-size: 16px; margin-top: 10px;">{mensaje}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Gráfico de barras comparativas
                data_comp = pd.DataFrame({
                    'Período': [periodo_1_label, periodo_2_label],
                    'Cantidad': [conteo_p1, conteo_p2]
                })
                
                fig = px.bar(
                    data_comp,
                    x='Período',
                    y='Cantidad',
                    color='Período',
                    text='Cantidad',
                    title=f"📊 Comparación de Volumen: {periodo_1_label} vs {periodo_2_label}",
                    color_discrete_sequence=['#4e54c8', '#8f94fb']
                )
                
                fig.update_traces(
                    texttemplate='%{text:,}',
                    textposition='auto',
                    marker_line_width=2,
                    marker_line_color='white'
                )
                
                fig.update_layout(
                    xaxis_title="Período",
                    yaxis_title="Cantidad de Registros",
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            elif metrica_analisis == "Distribución semanal":
                # Distribución por día de semana
                dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dias_spanish = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                dias_map = dict(zip(dias_orden, dias_spanish))
                
                # Contar por día de la semana para cada período
                dist_p1 = datos_periodo_1.groupby('dia_semana').size().reset_index()
                dist_p1.columns = ['Día', 'Cantidad']
                dist_p1['Período'] = periodo_1_label
                
                dist_p2 = datos_periodo_2.groupby('dia_semana').size().reset_index()
                dist_p2.columns = ['Día', 'Cantidad']
                dist_p2['Período'] = periodo_2_label
                
                # Crear un DataFrame combinado
                dist_combinada = pd.concat([dist_p1, dist_p2])
                
                # Convertir los nombres de los días y ordenarlos
                dist_combinada['Día'] = dist_combinada['Día'].map(dias_map)
                dist_combinada['DiaCodigo'] = dist_combinada['Día'].map({dia: i for i, dia in enumerate(dias_spanish)})
                dist_combinada = dist_combinada.sort_values('DiaCodigo')
                
                # Normalizar datos para comparación más justa
                if st.checkbox("Normalizar datos por total de período", value=False, key="norm_day_dist"):
                    for periodo in [periodo_1_label, periodo_2_label]:
                        total = dist_combinada[dist_combinada['Período'] == periodo]['Cantidad'].sum()
                        if total > 0:
                            dist_combinada.loc[dist_combinada['Período'] == periodo, 'Cantidad'] = \
                                dist_combinada.loc[dist_combinada['Período'] == periodo, 'Cantidad'] / total * 100
                    titulo = f"📊 Distribución Porcentual por Día: {periodo_1_label} vs {periodo_2_label}"
                    y_label = "Porcentaje (%)"
                else:
                    titulo = f"📊 Cantidad por Día: {periodo_1_label} vs {periodo_2_label}"
                    y_label = "Cantidad de Registros"
                
                # Gráfico de barras agrupadas
                fig = px.bar(
                    dist_combinada,
                    x='Día',
                    y='Cantidad',
                    color='Período',
                    barmode='group',
                    title=titulo,
                    color_discrete_sequence=['#4e54c8', '#8f94fb'],
                    text_auto=True
                )
                
                fig.update_layout(
                    xaxis_title="Día de la Semana",
                    yaxis_title=y_label,
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Análisis de desplazamiento de picos
                dia_pico_p1 = dist_p1.loc[dist_p1['Cantidad'].idxmax(), 'Día']
                dia_pico_p1 = dias_map.get(dia_pico_p1, dia_pico_p1)
                
                dia_pico_p2 = dist_p2.loc[dist_p2['Cantidad'].idxmax(), 'Día']
                dia_pico_p2 = dias_map.get(dia_pico_p2, dia_pico_p2)
                
                if dia_pico_p1 != dia_pico_p2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); padding: 15px; border-radius: 10px; margin-top: 10px;">
                        <h4 style="color: white; margin: 0;">🔄 Desplazamiento de Día Pico</h4>
                        <p style="color: white; font-size: 16px; margin-top: 10px;">
                            Se detectó un cambio en el patrón semanal: el día con mayor actividad pasó de <strong>{dia_pico_p2}</strong> a <strong>{dia_pico_p1}</strong>
                        </p>
                        <p style="color: white; font-size: 14px; margin-top: 5px;">
                            Este cambio puede requerir ajustes en la programación del personal o en la gestión de recursos.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
            elif metrica_analisis == "Patrones por hora":
                # Distribución por hora del día
                # Contar por hora para cada período
                hora_p1 = datos_periodo_1.groupby('hora').size().reset_index()
                hora_p1.columns = ['Hora', 'Cantidad']
                hora_p1['Período'] = periodo_1_label
                
                hora_p2 = datos_periodo_2.groupby('hora').size().reset_index()
                hora_p2.columns = ['Hora', 'Cantidad']
                hora_p2['Período'] = periodo_2_label
                
                # Rellenar horas faltantes con ceros
                for periodo, df_hora in [(periodo_1_label, hora_p1), (periodo_2_label, hora_p2)]:
                    horas_faltantes = set(range(24)) - set(df_hora['Hora'])
                    if horas_faltantes:
                        df_horas_faltantes = pd.DataFrame({
                            'Hora': list(horas_faltantes),
                            'Cantidad': [0] * len(horas_faltantes),
                            'Período': [periodo] * len(horas_faltantes)
                        })
                        if periodo == periodo_1_label:
                            hora_p1 = pd.concat([hora_p1, df_horas_faltantes])
                        else:
                            hora_p2 = pd.concat([hora_p2, df_horas_faltantes])
                
                # Ordenar por hora
                hora_p1 = hora_p1.sort_values('Hora')
                hora_p2 = hora_p2.sort_values('Hora')
                
                # Combinar datos
                horas_combinadas = pd.concat([hora_p1, hora_p2])
                
                # Normalizar datos para comparación más justa
                if st.checkbox("Normalizar datos por total de período", value=True, key="norm_hour_dist"):
                    for periodo in [periodo_1_label, periodo_2_label]:
                        total = horas_combinadas[horas_combinadas['Período'] == periodo]['Cantidad'].sum()
                        if total > 0:
                            horas_combinadas.loc[horas_combinadas['Período'] == periodo, 'Cantidad'] = \
                                horas_combinadas.loc[horas_combinadas['Período'] == periodo, 'Cantidad'] / total * 100
                    titulo = f"⏰ Distribución Porcentual por Hora: {periodo_1_label} vs {periodo_2_label}"
                    y_label = "Porcentaje (%)"
                else:
                    titulo = f"⏰ Cantidad por Hora: {periodo_1_label} vs {periodo_2_label}"
                    y_label = "Cantidad de Registros"
                
                # Gráfico de líneas superpuestas
                fig = px.line(
                    horas_combinadas,
                    x='Hora',
                    y='Cantidad',
                    color='Período',
                    title=titulo,
                    color_discrete_sequence=['#4e54c8', '#8f94fb'],
                    markers=True,
                    line_shape='spline'
                )
                
                fig.update_layout(
                    xaxis_title="Hora del Día",
                    yaxis_title=y_label,
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    ),
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(0, 24)),
                        ticktext=[f"{h}:00" for h in range(0, 24)]
                    )
                )
                
                # Añadir área sombreada para destacar diferencias
                if not st.checkbox("Ocultar área de diferencia", value=False, key="hide_diff_area"):
                    # Crear DataFrames con todas las horas para ambos períodos
                    p1_completo = pd.DataFrame({'Hora': range(24)}).merge(hora_p1, on='Hora', how='left').fillna(0)
                    p2_completo = pd.DataFrame({'Hora': range(24)}).merge(hora_p2, on='Hora', how='left').fillna(0)
                    
                    # Calcular diferencia
                    if st.checkbox("Normalizar datos por total de período", value=True, key="norm_hour_dist2"):
                        # Ya están normalizados en horas_combinadas
                        p1_vals = horas_combinadas[horas_combinadas['Período'] == periodo_1_label].sort_values('Hora')['Cantidad'].values
                        p2_vals = horas_combinadas[horas_combinadas['Período'] == periodo_2_label].sort_values('Hora')['Cantidad'].values
                    else:
                        p1_vals = p1_completo['Cantidad'].values
                        p2_vals = p2_completo['Cantidad'].values
                    
                    fig.add_trace(
                        go.Scatter(
                            x=list(range(0, 24)) + list(range(23, -1, -1)),  # Ruta de ida y vuelta para crear polígono
                            y=list(p1_vals) + list(p2_vals[::-1]),
                            fill='toself',
                            fillcolor='rgba(140, 158, 255, 0.3)',
                            line=dict(color='rgba(0, 0, 0, 0)'),
                            hoverinfo='skip',
                            showlegend=False
                        )
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Análisis de desplazamiento de picos de hora
                hora_pico_p1 = int(hora_p1.loc[hora_p1['Cantidad'].idxmax(), 'Hora'])
                hora_pico_p2 = int(hora_p2.loc[hora_p2['Cantidad'].idxmax(), 'Hora'])
                
                # Detectar patrones cambiantes
                if abs(hora_pico_p1 - hora_pico_p2) >= 2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%); padding: 15px; border-radius: 10px; margin-top: 10px;">
                        <h4 style="color: white; margin: 0;">⏰ Desplazamiento de Hora Pico</h4>
                        <p style="color: white; font-size: 16px; margin-top: 10px;">
                            Se detectó un cambio significativo en el patrón horario: la hora con mayor actividad pasó de <strong>{hora_pico_p2}:00</strong> 
                            a <strong>{hora_pico_p1}:00</strong> (desplazamiento de {abs(hora_pico_p1 - hora_pico_p2)} horas)
                        </p>
                        <p style="color: white; font-size: 14px; margin-top: 5px;">
                            Este cambio puede indicar un cambio en los hábitos de los clientes o en la operativa. 
                            Considere ajustar los horarios del personal para adaptarse a este nuevo patrón.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Insights generales sobre el cambio
            st.markdown("### 🔍 Insights sobre la comparación de períodos")
            
            col1, col2 = st.columns(2)
            
            # Calcular variación total
            var_total = ((len(datos_periodo_1) - len(datos_periodo_2)) / max(len(datos_periodo_2), 1) * 100)
            
            # Calcular variación en promedios diarios
            dias_p1 = len(datos_periodo_1['fecha_parsed'].dt.date.unique())
            dias_p2 = len(datos_periodo_2['fecha_parsed'].dt.date.unique())
            
            prom_diario_p1 = len(datos_periodo_1) / max(dias_p1, 1)
            prom_diario_p2 = len(datos_periodo_2) / max(dias_p2, 1)
            
            var_prom_diario = ((prom_diario_p1 - prom_diario_p2) / max(prom_diario_p2, 1) * 100)
            
            with col1:
                st.metric(
                    label="📈 Variación Total",
                    value=f"{var_total:.1f}%",
                    delta=f"{len(datos_periodo_1) - len(datos_periodo_2)}"
                )
            
            with col2:
                st.metric(
                    label="📊 Variación Promedio Diario",
                    value=f"{var_prom_diario:.1f}%",
                    delta=f"{prom_diario_p1 - prom_diario_p2:.1f}"
                )
            
            # Presentar recomendaciones basadas en los cambios
            if var_total > 10 or var_prom_diario > 10:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #06D6A0 0%, #1B9AAA 100%); padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <h4 style="color: white; margin: 0;">📈 Aumento Significativo</h4>
                    <p style="color: white; margin: 10px 0;">
                        Se recomienda:<br>
                        ✅ Revisar si hay eventos especiales que expliquen el incremento<br>
                        ✅ Preparar recursos adicionales para mantener la calidad del servicio<br>
                        ✅ Analizar qué segmentos específicos están generando este aumento
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif var_total < -10 or var_prom_diario < -10:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #FF595E 0%, #D62246 100%); padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <h4 style="color: white; margin: 0;">📉 Disminución Significativa</h4>
                    <p style="color: white; margin: 10px 0;">
                        Se recomienda:<br>
                        ✅ Investigar posibles causas de la disminución<br>
                        ✅ Revisar si hay cambios en el proceso que afecten la recepción de feedbacks<br>
                        ✅ Implementar acciones para recuperar el volumen anterior si es necesario
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.info("No se encontraron datos de fecha para realizar el análisis comparativo")    
    else:
        st.warning("No hay datos suficientes para el análisis comparativo")


def add_problem_resolution_analysis(df):
    """Añade análisis de problemas reportados y resolución"""
    st.markdown(
        """
        <div class="analysis-card">
            <h3 style="color: white; margin: 0;">🛠️ Análisis de Problemas y Resolución</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if not df.empty:
        # Crear copia para no modificar el dataframe original
        df_prob = df.copy()
        
        # Verificar las columnas disponibles
        columnas_necesarias = ['fecha_registro', 'fecha_cierre', 'motivo_cierre', 'observacion', 'respuesta_sub']
        if all(col in df_prob.columns for col in columnas_necesarias):
            # Convertir fechas
            df_prob['fecha_registro'] = pd.to_datetime(df_prob['fecha_registro'], errors='coerce')
            df_prob['fecha_cierre'] = pd.to_datetime(df_prob['fecha_cierre'], errors='coerce')
            
            # Calcular tiempo de resolución en horas
            df_prob['tiempo_resolucion'] = (df_prob['fecha_cierre'] - df_prob['fecha_registro']).dt.total_seconds() / 3600
            df_prob = df_prob[df_prob['tiempo_resolucion'] > 0]  # Filtrar tiempos negativos
            
            # Pestañas para diferentes análisis
            tab1, tab2, tab3 = st.tabs(["🔍 Tipos de Problemas", "⏱️ Tiempos de Resolución", "👥 Análisis de Vendedores"])
            
            with tab1:
                st.markdown("### 📊 Distribución de Tipos de Problemas")
                
                # Verificar si la columna respuesta_sub tiene valores no nulos
                if 'respuesta_sub' in df_prob.columns and df_prob['respuesta_sub'].notna().any():
                    # Contar los tipos de problemas más comunes
                    problema_counts = df_prob['respuesta_sub'].value_counts().reset_index()
                    problema_counts.columns = ['Tipo de Problema', 'Cantidad']
                    
                    # Mostrar solo los top 10
                    top_problemas = problema_counts.head(10)
                    
                    # Crear gráfico de barras horizontales
                    fig = px.bar(
                        top_problemas,
                        y='Tipo de Problema',
                        x='Cantidad',
                        orientation='h',
                        title='Top 10 Tipos de Problemas Reportados',
                        color='Cantidad',
                        color_continuous_scale='YlOrRd',
                        text='Cantidad'
                    )
                    
                    fig.update_layout(
                        xaxis_title="Cantidad de Reportes",
                        yaxis_title="",
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        yaxis={'categoryorder':'total ascending'}
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text}',
                        textposition='outside',
                        marker_line_width=1,
                        marker_line_color='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Análisis de la tendencia de problemas en el tiempo (mensual)
                    st.markdown("### 📈 Tendencia Mensual por Tipo de Problema")
                    
                    # Agregar mes a los datos
                    df_prob['mes'] = df_prob['fecha_registro'].dt.month
                    df_prob['mes_nombre'] = df_prob['fecha_registro'].dt.month_name()
                    
                    # Elegir los problemas para visualizar
                    top_5_problemas = problema_counts.head(5)['Tipo de Problema'].tolist()
                    problema_seleccionado = st.selectbox(
                        "Seleccionar tipo de problema:",
                        options=['Todos'] + top_5_problemas,
                        key="problema_tendencia"
                    )
                    
                    if problema_seleccionado != 'Todos':
                        df_tendencia = df_prob[df_prob['respuesta_sub'] == problema_seleccionado]
                    else:
                        df_tendencia = df_prob.copy()
                    
                    # Agrupar por mes
                    tendencia_mensual = df_tendencia.groupby('mes_nombre').size().reset_index()
                    tendencia_mensual.columns = ['Mes', 'Cantidad']
                    
                    # Ordenar por mes
                    meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 
                                  'July', 'August', 'September', 'October', 'November', 'December']
                    tendencia_mensual['mes_num'] = tendencia_mensual['Mes'].apply(lambda x: meses_orden.index(x) if x in meses_orden else 0)
                    tendencia_mensual = tendencia_mensual.sort_values('mes_num')
                    
                    # Crear gráfico de línea
                    fig = px.line(
                        tendencia_mensual,
                        x='Mes',
                        y='Cantidad',
                        title=f"Tendencia Mensual: {'Todos los Problemas' if problema_seleccionado == 'Todos' else problema_seleccionado}",
                        markers=True,
                        line_shape='spline'
                    )
                    
                    fig.update_traces(
                        line=dict(width=3, color='#4e54c8'),
                        marker=dict(size=8, color='#4e54c8')
                    )
                    
                    fig.update_layout(
                        xaxis_title="Mes",
                        yaxis_title="Cantidad de Reportes",
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Añadir un mapa de calor para la correlación entre problemas
                    st.markdown("### 🔄 Correlación entre Tipos de Problemas")
                    
                    # Crear matriz de coincidencia de problemas por ruta
                    if 'ruta' in df_prob.columns:
                        # Obtener las top rutas
                        top_rutas = df_prob['ruta'].value_counts().head(20).index.tolist()
                        
                        # Filtrar para incluir solo las principales rutas
                        df_top = df_prob[df_prob['ruta'].isin(top_rutas)]
                        
                        # Crear un pivot table que cuente problemas por ruta
                        problema_pivot = pd.crosstab(
                            df_top['ruta'], 
                            df_top['respuesta_sub']
                        )
                        
                        # Calcular correlación entre tipos de problemas
                        corr_problemas = problema_pivot.corr(method='pearson')
                          # Filtrar y mantener solo los top problemas
                        if len(corr_problemas) > 5:
                            top_prob_correlation = top_5_problemas
                            corr_problemas = corr_problemas.loc[top_prob_correlation, top_prob_correlation]
                        
                        # Visualizar la correlación como un heatmap
                        fig = px.imshow(
                            corr_problemas,
                            text_auto='.2f',  # Formato exacto con 2 decimales
                            color_continuous_scale='RdBu_r',
                            title='Correlación Entre Tipos de Problemas (por Ruta)'
                        )
                        
                        fig.update_layout(
                            height=900,  # Tamaño aumentado significativamente
                            width=900,   # Ancho aumentado
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white', size=16),  # Texto más grande y color blanco
                            margin=dict(l=100, r=100, b=100, t=100)  # Márgenes aumentados para textos largos
                        )
                        
                        # Asegurar que el texto en la visualización sea visible (color blanco)
                        fig.update_traces(
                            textfont=dict(color='white', size=14),
                            hoverinfo='all'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.info("📊 **Interpretación:** Valores cercanos a 1 indican que los problemas tienden a ocurrir en las mismas rutas, mientras que valores cercanos a -1 indican que cuando un problema ocurre, el otro tiende a no ocurrir en esa ruta.")
                    
                else:
                    st.info("No hay datos suficientes sobre los tipos de problemas reportados.")
            
            with tab2:
                st.markdown("### ⏱️ Tiempos de Resolución por Tipo de Problema")
                
                if 'respuesta_sub' in df_prob.columns and 'tiempo_resolucion' in df_prob.columns:
                    # Calcular estadísticas de tiempo de resolución por tipo de problema
                    tiempo_por_problema = df_prob.groupby('respuesta_sub')['tiempo_resolucion'].agg(['mean', 'median', 'count']).reset_index()
                    tiempo_por_problema.columns = ['Tipo de Problema', 'Promedio (horas)', 'Mediana (horas)', 'Cantidad']
                    tiempo_por_problema = tiempo_por_problema.sort_values('Promedio (horas)', ascending=False)
                    
                    # Filtrar para mostrar solo problemas con suficientes datos
                    tiempo_por_problema = tiempo_por_problema[tiempo_por_problema['Cantidad'] >= 5].head(10)
                    
                    # Crear gráfico de barras
                    fig = px.bar(
                        tiempo_por_problema,
                        y='Tipo de Problema',
                        x='Promedio (horas)',
                        orientation='h',
                        title='Tiempo Promedio de Resolución por Tipo de Problema',
                        color='Promedio (horas)',
                        color_continuous_scale='Sunset',
                        text='Promedio (horas)'
                    )
                    
                    fig.update_layout(
                        xaxis_title="Tiempo Promedio (horas)",
                        yaxis_title="",
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        yaxis={'categoryorder':'total ascending'}
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text:.1f} h',
                        textposition='outside',
                        marker_line_width=1,
                        marker_line_color='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Crear histograma con distribución de tiempos
                    st.markdown("### 📊 Distribución de Tiempos de Resolución")
                    
                    # Eliminar outliers para mejor visualización
                    q1 = df_prob['tiempo_resolucion'].quantile(0.05)
                    q3 = df_prob['tiempo_resolucion'].quantile(0.95)
                    df_filtrado = df_prob[(df_prob['tiempo_resolucion'] >= q1) & (df_prob['tiempo_resolucion'] <= q3)]
                    
                    fig = px.histogram(
                        df_filtrado,
                        x='tiempo_resolucion',
                        nbins=30,
                        title='Distribución de Tiempos de Resolución (5%-95% para mejor visualización)',
                        labels={'tiempo_resolucion': 'Tiempo de Resolución (horas)'},
                        color_discrete_sequence=['#4e54c8']
                    )
                    
                    fig.update_layout(
                        xaxis_title="Tiempo de Resolución (horas)",
                        yaxis_title="Frecuencia",
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        bargap=0.05
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Añadir tiempo promedio por día de la semana
                    st.markdown("### 📅 Tiempo Promedio de Resolución por Día de la Semana")
                    
                    # Agregar día de la semana
                    df_prob['dia_semana'] = df_prob['fecha_registro'].dt.day_name()
                    
                    # Calcular tiempo promedio por día
                    tiempo_por_dia = df_prob.groupby('dia_semana')['tiempo_resolucion'].mean().reset_index()
                    tiempo_por_dia.columns = ['Día', 'Promedio (horas)']
                    
                    # Ordenar días
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dias_spanish = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    map_dias = dict(zip(dias_orden, dias_spanish))
                    
                    tiempo_por_dia['Día_ES'] = tiempo_por_dia['Día'].map(map_dias)
                    tiempo_por_dia['Orden'] = tiempo_por_dia['Día'].apply(lambda x: dias_orden.index(x) if x in dias_orden else 7)
                    tiempo_por_dia = tiempo_por_dia.sort_values('Orden')
                    
                    # Crear gráfico de barras
                    fig = px.bar(
                        tiempo_por_dia,
                        x='Día_ES',
                        y='Promedio (horas)',
                        title='Tiempo Promedio de Resolución por Día de la Semana',
                        color='Promedio (horas)',
                        color_continuous_scale='Viridis',
                        text='Promedio (horas)'
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text:.1f} h',
                        textposition='outside',
                        marker_line_width=1,
                        marker_line_color='white'
                    )
                    
                    fig.update_layout(
                        xaxis_title="Día de la Semana",
                        yaxis_title="Tiempo Promedio (horas)",
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.info("No hay datos suficientes sobre los tiempos de resolución.")
            
            with tab3:
                st.markdown("### 👥 Análisis de Vendedores y Problemas Reportados")
                
                if 'vendedor' in df_prob.columns:
                    # Contar problemas por vendedor
                    problemas_vendedor = df_prob.groupby('vendedor').size().reset_index()
                    problemas_vendedor.columns = ['Vendedor', 'Cantidad de Problemas']
                    problemas_vendedor = problemas_vendedor.sort_values('Cantidad de Problemas', ascending=False).head(15)
                    
                    # Crear gráfico de barras horizontal
                    fig = px.bar(
                        problemas_vendedor,
                        y='Vendedor',
                        x='Cantidad de Problemas',
                        orientation='h',
                        title='Top 15 Vendedores por Cantidad de Problemas Reportados',
                        color='Cantidad de Problemas',
                        color_continuous_scale='Blues',
                        text='Cantidad de Problemas'
                    )
                    
                    fig.update_layout(
                        xaxis_title="Cantidad de Problemas",
                        yaxis_title="",
                        height=600,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        yaxis={'categoryorder':'total ascending'}
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text}',
                        textposition='outside',
                        marker_line_width=1,
                        marker_line_color='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Análisis de tipos de problemas por vendedor
                    st.markdown("### 🔍 Tipos de Problemas por Vendedor")
                    
                    # Permitir seleccionar un vendedor
                    top_vendedores = df_prob['vendedor'].value_counts().head(10).index.tolist()
                    vendedor_seleccionado = st.selectbox(
                        "Seleccionar vendedor:",
                        options=top_vendedores,
                        key="vendedor_analisis"
                    )
                    
                    # Filtrar datos para el vendedor seleccionado
                    df_vendedor = df_prob[df_prob['vendedor'] == vendedor_seleccionado]
                    
                    # Contar tipos de problemas para el vendedor
                    problemas_del_vendedor = df_vendedor['respuesta_sub'].value_counts().reset_index()
                    problemas_del_vendedor.columns = ['Tipo de Problema', 'Cantidad']
                    problemas_del_vendedor = problemas_del_vendedor.sort_values('Cantidad', ascending=False).head(8)
                    
                    # Crear gráfico de sectores
                    fig = px.pie(
                        problemas_del_vendedor,
                        values='Cantidad',
                        names='Tipo de Problema',
                        title=f'Distribución de Problemas para {vendedor_seleccionado}',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        marker=dict(line=dict(color='#000000', width=1))
                    )
                    
                    fig.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparación con otros vendedores
                    if 'ruta' in df_prob.columns:
                        st.markdown("### 🔄 Comparación con Otros Vendedores de la Misma Ruta")
                        
                        # Obtener rutas del vendedor seleccionado
                        rutas_vendedor = df_prob[df_prob['vendedor'] == vendedor_seleccionado]['ruta'].unique()
                        
                        if len(rutas_vendedor) > 0:
                            # Selección de ruta para comparar
                            ruta_comparar = st.selectbox(
                                "Seleccionar ruta para comparar:",
                                options=rutas_vendedor,
                                key="ruta_comparacion"
                            )
                            
                            # Obtener vendedores de la misma ruta
                            df_ruta = df_prob[df_prob['ruta'] == ruta_comparar]
                            vendedores_ruta = df_ruta['vendedor'].unique()
                            
                            # Contar problemas por vendedor en la ruta
                            problemas_ruta = df_ruta.groupby(['vendedor', 'respuesta_sub']).size().reset_index()
                            problemas_ruta.columns = ['Vendedor', 'Tipo de Problema', 'Cantidad']
                            
                            # Graficar comparativa
                            fig = px.bar(
                                problemas_ruta,
                                x='Vendedor',
                                y='Cantidad',
                                color='Tipo de Problema',
                                title=f'Comparación de Problemas en Ruta {ruta_comparar}',
                                barmode='stack'
                            )
                            
                            fig.update_layout(
                                xaxis_title="Vendedor",
                                yaxis_title="Cantidad de Problemas",
                                height=500,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='white'),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.3,
                                    xanchor="center",
                                    x=0.5
                                )
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(f"No hay información de rutas para {vendedor_seleccionado}")
                    
                else:
                    st.info("No hay datos suficientes sobre vendedores.")
                
            # Insights generales
            st.markdown("### 💡 Insights Generales de Problemas y Resolución")
            
            # Calcular estadísticas relevantes
            if 'tiempo_resolucion' in df_prob.columns and 'respuesta_sub' in df_prob.columns:
                tiempo_promedio = df_prob['tiempo_resolucion'].mean()
                problema_mas_comun = df_prob['respuesta_sub'].value_counts().index[0] if len(df_prob['respuesta_sub'].value_counts()) > 0 else "No disponible"
                problema_mas_lento = tiempo_por_problema.sort_values('Promedio (horas)', ascending=False).iloc[0]['Tipo de Problema'] if not tiempo_por_problema.empty else "No disponible"
                tiempo_mas_lento = tiempo_por_problema.sort_values('Promedio (horas)', ascending=False).iloc[0]['Promedio (horas)'] if not tiempo_por_problema.empty else 0
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <h4 style="color: white; margin: 0;">📊 Estadísticas Clave</h4>
                        <p style="color: white; margin: 10px 0; font-size: 14px;">
                            ⏱️ <strong>Tiempo promedio de resolución:</strong> {tiempo_promedio:.1f} horas<br>
                            🔍 <strong>Problema más común:</strong> {problema_mas_comun}<br>
                            ⚠️ <strong>Problema con resolución más lenta:</strong> {problema_mas_lento} ({tiempo_mas_lento:.1f} horas)<br>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Generar recomendaciones automáticas
                    recomendaciones = []
                    
                    if tiempo_promedio > 300:  # Si el tiempo promedio es mayor a 300 horas
                        recomendaciones.append("⚡ Implementar un sistema de priorización de problemas para reducir tiempos de resolución")
                    
                    if 'vendedor' in df_prob.columns:
                        vendor_counts = df_prob['vendedor'].value_counts()
                        if vendor_counts.max() > 50:  # Si hay vendedores con muchos problemas
                            recomendaciones.append("👥 Proporcionar capacitación adicional a los vendedores con mayor número de problemas reportados")
                    
                    if len(recomendaciones) == 0:
                        recomendaciones.append("✅ Los tiempos de resolución y la distribución de problemas están dentro de los rangos esperados")
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #06D6A0 0%, #1B9AAA 100%); padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <h4 style="color: white; margin: 0;">💡 Recomendaciones</h4>
                        <p style="color: white; margin: 10px 0; font-size: 14px;">
                            {'<br>'.join(recomendaciones)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
        else:
            st.info("No se encontraron todas las columnas necesarias para este análisis.")
    
    else:
        st.warning("No hay datos suficientes para el análisis de problemas y resolución")
