import pandas as pd

# Cargar datos y verificar columnas
print("=== VERIFICACIÓN DE COLUMNAS ===")
feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
rutas_df = pd.read_excel('BD_Rutas.xlsx')

print("\nColumnas en Feedbacks H1.xlsx:")
for i, col in enumerate(feedbacks_df.columns):
    print(f"{i+1}. '{col}'")

print(f"\nPrimeras filas de Feedbacks:")
print(feedbacks_df.head())

print(f"\nColumnas en BD_Rutas.xlsx:")
for i, col in enumerate(rutas_df.columns):
    print(f"{i+1}. '{col}'")

print(f"\nPrimeras filas de BD_Rutas:")
print(rutas_df.head())

print(f"\nTotal feedbacks: {len(feedbacks_df)}")
print(f"Total rutas: {len(rutas_df)}")
