import pandas as pd
from datetime import datetime
import calendar

def generar_flujo_consecuencias_mes(mes=5, año=2025):
    """
    Genera el flujo de consecuencias para un mes específico
    
    Args:
        mes (int): Número del mes (1-12)
        año (int): Año a analizar
    """
    mes_nombre = calendar.month_name[mes]
    
    print(f"📋 GENERANDO FLUJO DE CONSECUENCIAS: {mes_nombre.upper()} {año}")
    print("=" * 60)
    
    try:
        # Cargar datos
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        
        # Intentar cargar la base de rutas más apropiada
        archivos_rutas = [
            f'BD_Rutas_{mes_nombre}.xlsx',
            'BD_Rutas_Junio.xlsx',
            'BD_Rutas_Mayo.xlsx', 
            'BD_Rutas.xlsx'
        ]
        
        rutas_df = None
        archivo_usado = None
        
        for archivo in archivos_rutas:
            try:
                rutas_df = pd.read_excel(archivo)
                archivo_usado = archivo
                print(f"✅ Usando base de rutas: {archivo}")
                break
            except FileNotFoundError:
                continue
        
        if rutas_df is None:
            print("❌ No se encontró ninguna base de datos de rutas")
            return None
        
        # Convertir fechas
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        
        # Filtrar feedbacks del mes específico
        feedbacks_mes = feedbacks_df[
            (feedbacks_df['fecha_registro'].dt.month == mes) &
            (feedbacks_df['fecha_registro'].dt.year == año)
        ]
        
        print(f"📊 Feedbacks encontrados en {mes_nombre} {año}: {len(feedbacks_mes)}")
        
        # Obtener todas las rutas activas
        todas_las_rutas = set(rutas_df['RUTA'].dropna().unique())
        
        # Rutas que SÍ hicieron feedback
        rutas_con_feedback = set(feedbacks_mes['ruta'].dropna().unique())
        
        # Rutas que NO hicieron feedback (necesitan consecuencias)
        rutas_sin_feedback = todas_las_rutas - rutas_con_feedback
        
        print(f"📈 Total rutas activas: {len(todas_las_rutas)}")
        print(f"✅ Rutas que cumplieron: {len(rutas_con_feedback)}")
        print(f"❌ Rutas que NO cumplieron: {len(rutas_sin_feedback)}")
        
        # Crear lista de rutas para consecuencias
        rutas_consecuencias = []
        
        for ruta in sorted(rutas_sin_feedback):
            # Buscar información del vendedor
            info_ruta = rutas_df[rutas_df['RUTA'] == ruta]
            vendedor = 'No disponible'
            
            if not info_ruta.empty:
                if 'NOMBRE_VENDEDOR' in info_ruta.columns:
                    vendedor = info_ruta['NOMBRE_VENDEDOR'].iloc[0]
                elif 'VENDEDOR' in info_ruta.columns:
                    vendedor = info_ruta['VENDEDOR'].iloc[0]
            
            rutas_consecuencias.append({
                'RUTA': ruta,
                'VENDEDOR': vendedor,
                'MES_INCUMPLIMIENTO': f'{mes_nombre} {año}',
                'NIVEL_CONSECUENCIA': '',  # Para llenar manualmente
                'ACCION_REQUERIDA': '',    # Para llenar manualmente
                'RESPONSABLE': '',         # Para llenar manualmente
                'FECHA_LIMITE': '',        # Para llenar manualmente
                'FECHA_EJECUTADA': '',     # Para llenar al ejecutar
                'ESTADO': 'PENDIENTE',
                'OBSERVACIONES': '',
                'DOCUMENTO_EVIDENCIA': ''
            })
        
        # Crear DataFrame
        df_consecuencias = pd.DataFrame(rutas_consecuencias)
        
        # Crear hoja de guía rápida
        guia_rapida = [
            {'NIVEL': 'NIVEL 1', 'ACCION': 'Llamada atención verbal', 'RESPONSABLE': 'Supervisor', 'PLAZO': '2 días'},
            {'NIVEL': 'NIVEL 2', 'ACCION': 'Amonestación escrita', 'RESPONSABLE': 'Coordinador', 'PLAZO': '3 días'},
            {'NIVEL': 'NIVEL 3', 'ACCION': 'Suspensión 1 día', 'RESPONSABLE': 'Jefe Distribución', 'PLAZO': '5 días'},
            {'NIVEL': 'NIVEL 4', 'ACCION': 'Comité evaluación', 'RESPONSABLE': 'Gerente + Comité', 'PLAZO': '1 semana'}
        ]
        
        df_guia = pd.DataFrame(guia_rapida)
        
        # Crear resumen estadístico
        resumen = [{
            'MES': f'{mes_nombre} {año}',
            'TOTAL_RUTAS': len(todas_las_rutas),
            'CUMPLIERON': len(rutas_con_feedback),
            'NO_CUMPLIERON': len(rutas_sin_feedback),
            'PORCENTAJE_CUMPLIMIENTO': round((len(rutas_con_feedback) / len(todas_las_rutas)) * 100, 1),
            'ARCHIVO_RUTAS_USADO': archivo_usado,
            'FECHA_GENERACION': datetime.now().strftime('%Y-%m-%d %H:%M')
        }]
        
        df_resumen = pd.DataFrame(resumen)
        
        # Generar archivo Excel
        filename = f"Consecuencias_{mes_nombre}_{año}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Hoja principal: Rutas para consecuencias
            df_consecuencias.to_excel(writer, sheet_name='RUTAS_CONSECUENCIAS', index=False)
            
            # Hoja de guía
            df_guia.to_excel(writer, sheet_name='GUIA_RAPIDA', index=False)
            
            # Hoja de resumen
            df_resumen.to_excel(writer, sheet_name='RESUMEN', index=False)
            
            # Formateo básico
            workbook = writer.book
            
            # Formato de encabezado
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            
            # Formato para pendientes
            pendiente_format = workbook.add_format({
                'bg_color': '#FFEB9C',
                'border': 1
            })
            
            # Aplicar formato a la hoja principal
            worksheet = writer.sheets['RUTAS_CONSECUENCIAS']
            
            # Ajustar anchos de columna
            worksheet.set_column('A:A', 12)  # RUTA
            worksheet.set_column('B:B', 25)  # VENDEDOR
            worksheet.set_column('C:C', 18)  # MES_INCUMPLIMIENTO
            worksheet.set_column('D:K', 20)  # Resto de columnas
            
            # Aplicar formato de encabezado
            for col in range(11):
                worksheet.write(0, col, df_consecuencias.columns[col], header_format)
        
        print(f"✅ Archivo generado: {filename}")
        
        # Mostrar rutas críticas si hay pocas
        if len(rutas_sin_feedback) <= 10 and len(rutas_sin_feedback) > 0:
            print(f"\n🚨 RUTAS QUE REQUIEREN ACCIÓN:")
            for i, ruta in enumerate(sorted(rutas_sin_feedback), 1):
                info_ruta = rutas_df[rutas_df['RUTA'] == ruta]
                vendedor = 'No disponible'
                if not info_ruta.empty and 'NOMBRE_VENDEDOR' in info_ruta.columns:
                    vendedor = info_ruta['NOMBRE_VENDEDOR'].iloc[0]
                print(f"   {i}. {ruta} - {vendedor}")
        
        return filename, len(rutas_sin_feedback)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, 0

def main():
    """
    Función principal - CAMBIAR AQUÍ EL MES Y AÑO
    """
    # 🔧 CONFIGURACIÓN - Cambiar estos valores según necesites:
    MES = 5      # 1=Enero, 2=Febrero, ..., 5=Mayo, 6=Junio, etc.
    AÑO = 2025   # Año a analizar
    
    print("🎯 GENERADOR SIMPLE DE FLUJO DE CONSECUENCIAS")
    print("=" * 60)
    
    archivo, total_rutas = generar_flujo_consecuencias_mes(MES, AÑO)
    
    if archivo:
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO")
        print(f"📁 Archivo: {archivo}")
        print(f"📊 Rutas para acción: {total_rutas}")
        
        print(f"\n📋 INSTRUCCIONES RÁPIDAS:")
        print(f"1. Abrir el Excel generado")
        print(f"2. En la hoja 'RUTAS_CONSECUENCIAS':")
        print(f"   - Llenar columna 'NIVEL_CONSECUENCIA' (1, 2, 3 o 4)")
        print(f"   - Llenar 'ACCION_REQUERIDA' según la guía")
        print(f"   - Asignar 'RESPONSABLE'")
        print(f"   - Poner 'FECHA_LIMITE' (max 5 días)")
        print(f"3. Ejecutar las acciones")
        print(f"4. Documentar en las columnas finales")
        
        print(f"\n💡 Para otro mes: Cambiar MES y AÑO en líneas 130-131")

if __name__ == "__main__":
    main()
