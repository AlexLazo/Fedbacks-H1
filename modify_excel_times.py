import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def modify_excel_with_realistic_times():
    """
    Modifica el archivo Excel agregando columnas de tiempo de cierre variados (1-10 días)
    """
    
    try:
        # Cargar el archivo Excel
        print("📂 Cargando archivo Feedbacks H1.xlsx...")
        df = pd.read_excel('Feedbacks H1.xlsx')
        
        print(f"✅ Archivo cargado exitosamente. Registros: {len(df)}")
        print(f"📋 Columnas actuales: {list(df.columns)}")
        
        # Convertir fecha_registro a datetime
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], errors='coerce')
        
        # Generar tiempo de cierre realista (1-10 días con distribución variada)
        print("⏱️ Generando tiempos de cierre variados (1-10 días)...")
        
        # Crear tiempos de cierre más variados y realistas
        np.random.seed(42)  # Para resultados reproducibles
        
        # Usar diferentes tipos de distribución para hacer más realista
        tiempos = []
        for i in range(len(df)):
            rand = random.random()
            if rand < 0.3:  # 30% - casos rápidos (1-3 días)
                tiempo = np.random.uniform(1, 3)
            elif rand < 0.6:  # 30% - casos normales (3-6 días)
                tiempo = np.random.uniform(3, 6)
            elif rand < 0.85:  # 25% - casos que toman más tiempo (6-8 días)
                tiempo = np.random.uniform(6, 8)
            else:  # 15% - casos complejos (8-10 días)
                tiempo = np.random.uniform(8, 10)
            
            tiempos.append(round(tiempo, 1))
        
        df['tiempo_cierre_dias'] = tiempos
        
        # Crear fecha de cierre basada en fecha_registro + tiempo_cierre_dias
        df['fecha_cierre'] = df['fecha_registro'] + pd.to_timedelta(df['tiempo_cierre_dias'], unit='days')
        
        # Agregar algo de variación: 85% tienen cierre, 15% están pendientes
        indices_pendientes = np.random.choice(df.index, size=int(len(df) * 0.15), replace=False)
        df.loc[indices_pendientes, 'fecha_cierre'] = pd.NaT
        df.loc[indices_pendientes, 'tiempo_cierre_dias'] = np.nan
        
        # Estadísticas de lo generado
        casos_cerrados = df['fecha_cierre'].notna().sum()
        casos_pendientes = df['fecha_cierre'].isna().sum()
        tiempo_promedio = df['tiempo_cierre_dias'].mean()
        
        print(f"📊 Estadísticas generadas:")
        print(f"   • Casos cerrados: {casos_cerrados} ({casos_cerrados/len(df)*100:.1f}%)")
        print(f"   • Casos pendientes: {casos_pendientes} ({casos_pendientes/len(df)*100:.1f}%)")
        print(f"   • Tiempo promedio de cierre: {tiempo_promedio:.1f} días")
        print(f"   • Tiempo mínimo: {df['tiempo_cierre_dias'].min():.1f} días")
        print(f"   • Tiempo máximo: {df['tiempo_cierre_dias'].max():.1f} días")
        
        # Crear backup del archivo original
        backup_name = f"Feedbacks H1_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        print(f"💾 Creando backup: {backup_name}")
        df_original = pd.read_excel('Feedbacks H1.xlsx')
        df_original.to_excel(backup_name, index=False)
        
        # Guardar el archivo modificado
        print("💾 Guardando archivo modificado...")
        df.to_excel('Feedbacks H1.xlsx', index=False)
        
        print("✅ ¡Archivo modificado exitosamente!")
        print(f"📋 Columnas finales: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al modificar el archivo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando modificación del archivo Excel...")
    print("=" * 50)
    
    success = modify_excel_with_realistic_times()
    
    print("=" * 50)
    if success:
        print("✅ ¡Proceso completado exitosamente!")
        print("🔄 Ahora puedes ejecutar el dashboard y verás:")
        print("   • Tiempos de cierre variados (1-10 días)")
        print("   • 30% casos rápidos (1-3 días)")
        print("   • 30% casos normales (3-6 días)")
        print("   • 25% casos lentos (6-8 días)")
        print("   • 15% casos complejos (8-10 días)")
        print("   • 85% de casos cerrados, 15% pendientes")
        print("   • Métricas de eficiencia más variadas y realistas")
    else:
        print("❌ El proceso falló. Revisa los errores arriba.")
