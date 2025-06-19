import pandas as pd

# Cargar los datos
feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
bd_rutas_df = pd.read_excel('BD_Rutas.xlsx')

print("=== ANÁLISIS DE JUAN SIBRIAN ===")

# Ver cómo aparece Juan en feedbacks
juan_feedbacks = feedbacks_df[feedbacks_df['SUPERVISOR'].str.contains('JUAN', case=False, na=False)]
print(f"\nNombres de Juan en feedbacks ({len(juan_feedbacks)} registros):")
print(juan_feedbacks['SUPERVISOR'].unique())

# Ver cómo aparece Juan en BD_Rutas
juan_rutas = bd_rutas_df[bd_rutas_df['SUPERVISOR'].str.contains('JUAN', case=False, na=False)]
print(f"\nNombres de Juan en BD_Rutas ({len(juan_rutas)} rutas):")
print(juan_rutas['SUPERVISOR'].unique())

print("\n=== COMPARACIÓN DETALLADA ===")
print("Feedbacks - nombres exactos:")
for nombre in juan_feedbacks['SUPERVISOR'].unique():
    print(f"'{nombre}' - len: {len(nombre)}")

print("\nBD_Rutas - nombres exactos:")
for nombre in juan_rutas['SUPERVISOR'].unique():
    print(f"'{nombre}' - len: {len(nombre)}")

# Ver si hay espacios o caracteres especiales
print("\n=== ANÁLISIS DE CARACTERES ===")
if len(juan_feedbacks['SUPERVISOR'].unique()) > 0:
    nombre_fb = juan_feedbacks['SUPERVISOR'].unique()[0]
    print(f"Feedbacks - primer nombre: '{nombre_fb}'")
    print(f"Bytes: {[ord(c) for c in nombre_fb]}")

if len(juan_rutas['SUPERVISOR'].unique()) > 0:
    nombre_rt = juan_rutas['SUPERVISOR'].unique()[0]
    print(f"BD_Rutas - primer nombre: '{nombre_rt}'")
    print(f"Bytes: {[ord(c) for c in nombre_rt]}")

# Test de limpieza
print("\n=== TEST DE LIMPIEZA ===")
if len(juan_feedbacks['SUPERVISOR'].unique()) > 0 and len(juan_rutas['SUPERVISOR'].unique()) > 0:
    nombre_fb_clean = juan_feedbacks['SUPERVISOR'].unique()[0].strip().upper()
    nombre_rt_clean = juan_rutas['SUPERVISOR'].unique()[0].strip().upper()
    print(f"Feedbacks limpio: '{nombre_fb_clean}'")
    print(f"BD_Rutas limpio: '{nombre_rt_clean}'")
    print(f"¿Son iguales?: {nombre_fb_clean == nombre_rt_clean}")

# Ver las rutas de Juan
print(f"\n=== RUTAS DE JUAN ===")
print("Rutas en BD_Rutas:")
print(juan_rutas[['RUTA', 'SUPERVISOR']].to_string())

print(f"\nFeedbacks de Juan por ruta:")
if len(juan_feedbacks) > 0:
    juan_por_ruta = juan_feedbacks.groupby('RUTA').size()
    print(juan_por_ruta)
