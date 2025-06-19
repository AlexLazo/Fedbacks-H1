import pandas as pd
import numpy as np

def limpiar_nombre(nombre):
    """Función de limpieza de nombres igual que en el dashboard"""
    if pd.isna(nombre):
        return ""
    return str(nombre).strip().upper()

# Cargar datos
print("=== DIAGNÓSTICO ESPECÍFICO JUAN SIBRIAN ===")
feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
rutas_df = pd.read_excel('BD_Rutas.xlsx')

print(f"Total feedbacks: {len(feedbacks_df)}")
print(f"Total rutas: {len(rutas_df)}")

# Verificar nombres de supervisores únicos en feedbacks
print("\n=== SUPERVISORES EN FEEDBACKS ===")
supervisores_feedbacks = feedbacks_df['Supervisor'].dropna().unique()
print("Supervisores únicos en feedbacks:")
for sup in sorted(supervisores_feedbacks):
    count = len(feedbacks_df[feedbacks_df['Supervisor'] == sup])
    print(f"  '{sup}' -> {count} registros")

# Verificar nombres de supervisores únicos en rutas
print("\n=== SUPERVISORES EN BD_RUTAS ===")
supervisores_rutas = rutas_df['Supervisor'].dropna().unique()
print("Supervisores únicos en BD_Rutas:")
for sup in sorted(supervisores_rutas):
    count = len(rutas_df[rutas_df['Supervisor'] == sup])
    print(f"  '{sup}' -> {count} rutas")

# Buscar variaciones de Juan específicamente
print("\n=== VARIACIONES DE JUAN ===")
juan_feedbacks = [s for s in supervisores_feedbacks if 'juan' in str(s).lower()]
juan_rutas = [s for s in supervisores_rutas if 'juan' in str(s).lower()]

print("En Feedbacks:")
for juan in juan_feedbacks:
    count = len(feedbacks_df[feedbacks_df['Supervisor'] == juan])
    print(f"  '{juan}' (len={len(juan)}) -> {count} registros")
    
print("En BD_Rutas:")
for juan in juan_rutas:
    count = len(rutas_df[rutas_df['Supervisor'] == juan])
    print(f"  '{juan}' (len={len(juan)}) -> {count} rutas")

# Aplicar limpieza y verificar match
print("\n=== DESPUÉS DE LIMPIEZA ===")
juan_feedbacks_clean = [limpiar_nombre(s) for s in juan_feedbacks]
juan_rutas_clean = [limpiar_nombre(s) for s in juan_rutas]

print("Juan en Feedbacks (limpio):", juan_feedbacks_clean)
print("Juan en BD_Rutas (limpio):", juan_rutas_clean)

# Verificar si hacen match después de limpieza
matches = set(juan_feedbacks_clean) & set(juan_rutas_clean)
print("Matches después de limpieza:", matches)

# Comparar con otro supervisor que sí funciona
print("\n=== COMPARACIÓN CON OTRO SUPERVISOR ===")
# Buscar un supervisor que tenga registros en ambos lados
supervisores_comunes = []
for sup_f in supervisores_feedbacks:
    sup_f_clean = limpiar_nombre(sup_f)
    for sup_r in supervisores_rutas:
        sup_r_clean = limpiar_nombre(sup_r)
        if sup_f_clean == sup_r_clean and sup_f_clean != "":
            supervisores_comunes.append((sup_f, sup_r, sup_f_clean))

print("Supervisores que hacen match correctamente:")
for orig_f, orig_r, clean in supervisores_comunes[:3]:  # Solo los primeros 3
    count_f = len(feedbacks_df[feedbacks_df['Supervisor'] == orig_f])
    count_r = len(rutas_df[rutas_df['Supervisor'] == orig_r])
    print(f"  '{orig_f}' -> '{orig_r}' = '{clean}' ({count_f} feedbacks, {count_r} rutas)")

# Test específico del merge como en el dashboard
print("\n=== TEST DEL MERGE ESPECÍFICO ===")
# Filtrar datos de Juan
juan_original_feedbacks = 'Juan Sibrian'  # El nombre exacto en feedbacks
juan_original_rutas = None

# Encontrar el nombre exacto en rutas
for sup in supervisores_rutas:
    if 'juan' in str(sup).lower() and 'sibrian' in str(sup).lower():
        juan_original_rutas = sup
        break

if juan_original_rutas:
    print(f"Juan en feedbacks: '{juan_original_feedbacks}'")
    print(f"Juan en rutas: '{juan_original_rutas}'")
    
    # Simular el proceso del dashboard
    rutas_df_copy = rutas_df.copy()
    feedbacks_df_copy = feedbacks_df.copy()
    
    # Limpiar nombres
    rutas_df_copy['Supervisor_clean'] = rutas_df_copy['Supervisor'].apply(limpiar_nombre)
    feedbacks_df_copy['Supervisor_clean'] = feedbacks_df_copy['Supervisor'].apply(limpiar_nombre)
    
    juan_clean = limpiar_nombre(juan_original_feedbacks)
    
    # Verificar registros antes del merge
    juan_feedbacks_count = len(feedbacks_df_copy[feedbacks_df_copy['Supervisor_clean'] == juan_clean])
    juan_rutas_count = len(rutas_df_copy[rutas_df_copy['Supervisor_clean'] == juan_clean])
    
    print(f"Después de limpieza - Juan: '{juan_clean}'")
    print(f"Feedbacks de Juan: {juan_feedbacks_count}")
    print(f"Rutas de Juan: {juan_rutas_count}")
    
    # Hacer el merge como en el dashboard
    supervisor_stats = (feedbacks_df_copy[feedbacks_df_copy['Supervisor_clean'] == juan_clean]
                       .groupby('Ruta')
                       .size()
                       .reset_index(name='feedbacks_count'))
    
    juan_rutas_filtered = rutas_df_copy[rutas_df_copy['Supervisor_clean'] == juan_clean]
    
    supervisor_merged = juan_rutas_filtered.merge(
        supervisor_stats, 
        on='Ruta', 
        how='left'
    )
    
    supervisor_merged['feedbacks_count'] = supervisor_merged['feedbacks_count'].fillna(0)
    
    print(f"Rutas de Juan después del merge: {len(supervisor_merged)}")
    print(f"Total feedbacks en rutas de Juan: {supervisor_merged['feedbacks_count'].sum()}")
    
    if len(supervisor_merged) > 0:
        print("Detalle de rutas de Juan:")
        for _, row in supervisor_merged.iterrows():
            print(f"  Ruta {row['Ruta']}: {row['feedbacks_count']} feedbacks")
else:
    print("No se encontró Juan en BD_Rutas")
