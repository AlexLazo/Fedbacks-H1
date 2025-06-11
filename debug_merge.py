import pandas as pd
import numpy as np

print('=== ANÁLISIS DETALLADO DEL MERGE ===')

# Cargar datasets
try:
    feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
    rutas_df = pd.read_excel('BD_Rutas.xlsx')
    
    print(f'Feedbacks dataset: {len(feedbacks_df)} registros, {feedbacks_df["ruta"].nunique()} rutas únicas')
    print(f'BD_Rutas dataset: {len(rutas_df)} registros, {rutas_df["RUTA"].nunique()} rutas únicas')
    
    # Mostrar columnas
    print('\nColumnas Feedbacks:', list(feedbacks_df.columns))
    print('\nColumnas BD_Rutas:', list(rutas_df.columns))
    
    # Análisis de rutas
    rutas_feedbacks = set(feedbacks_df['ruta'].unique())
    rutas_bd = set(rutas_df['RUTA'].unique())
    
    print(f'\nRutas en común: {len(rutas_feedbacks.intersection(rutas_bd))}')
    print(f'Rutas solo en Feedbacks: {len(rutas_feedbacks - rutas_bd)}')
    print(f'Rutas solo en BD_Rutas: {len(rutas_bd - rutas_feedbacks)}')
    
    # Hacer el merge como en el código
    merged_df = feedbacks_df.merge(rutas_df, left_on='ruta', right_on='RUTA', how='left')
    print(f'\nDespués del merge: {len(merged_df)} registros, {merged_df["ruta"].nunique()} rutas únicas')
    
    # Verificar duplicados en BD_Rutas
    print(f'\nDuplicados en BD_Rutas por RUTA: {rutas_df["RUTA"].duplicated().sum()}')
    if rutas_df["RUTA"].duplicated().sum() > 0:
        print("Rutas duplicadas en BD_Rutas:")
        duplicated_routes = rutas_df[rutas_df["RUTA"].duplicated(keep=False)].sort_values('RUTA')
        print(duplicated_routes[['RUTA', 'SUPERVISOR', 'CONTRATISTA']])
    
    # Verificar nulos después del merge
    print(f'\nRegistros con supervisor nulo después del merge: {merged_df["SUPERVISOR"].isnull().sum()}')
    print(f'Registros con contratista nulo después del merge: {merged_df["CONTRATISTA"].isnull().sum()}')
    
    # Análisis de rutas únicas después del merge
    merged_routes = merged_df.groupby('ruta').agg({
        'SUPERVISOR': 'first',
        'CONTRATISTA': 'first'
    }).reset_index()
    
    print(f'\nRutas únicas con supervisor asignado: {merged_routes["SUPERVISOR"].notna().sum()}')
    print(f'Rutas sin supervisor después del merge: {merged_routes["SUPERVISOR"].isna().sum()}')
    
    # Mostrar algunas rutas sin supervisor
    routes_without_supervisor = merged_routes[merged_routes['SUPERVISOR'].isna()]
    if len(routes_without_supervisor) > 0:
        print(f'\nPrimeras 10 rutas sin supervisor:')
        print(routes_without_supervisor['ruta'].head(10).tolist())
    
    # Contar registros por mes y ruta para meta analysis
    feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
    feedbacks_df['mes'] = feedbacks_df['fecha_registro'].dt.month
    
    monthly_route_counts = feedbacks_df.groupby(['mes', 'ruta']).size().reset_index(name='count')
    print(f'\nTotal de combinaciones mes-ruta: {len(monthly_route_counts)}')
    print(f'Rutas con 10+ registros por mes: {(monthly_route_counts["count"] >= 10).sum()}')
    
except Exception as e:
    print(f"Error: {e}")
