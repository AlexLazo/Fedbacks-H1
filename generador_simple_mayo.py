import pandas as pd
from datetime import datetime
import calendar

def load_headcount_data_fixed():
    """
    Carga la base de datos de HEADCOUNT con manejo mejorado de columnas
    """
    try:
        # Intentar cargar el archivo HEADCOUNT con diferentes métodos
        headcount_file = "BASE HEADCOUNT JUNIO - 2025.xlsm"
        
        # Leer con skiprows para omitir encabezados problemáticos
        headcount_df = pd.read_excel(headcount_file, engine='openpyxl', skiprows=1)
        
        print(f"✅ BASE HEADCOUNT cargada: {len(headcount_df)} empleados")
        
        # Intentar encontrar la columna de nombres completos
        name_columns = []
        supervisor_columns = []
        
        for col in headcount_df.columns:
            col_str = str(col).lower()
            if any(word in col_str for word in ['nombre', 'completo', 'name']):
                name_columns.append(col)
            if any(word in col_str for word in ['supervisor', 'jefe', 'boss']):
                supervisor_columns.append(col)
        
        print(f"📋 Columnas de nombres encontradas: {name_columns}")
        print(f"📋 Columnas de supervisores encontradas: {supervisor_columns}")
        
        # Si encontramos columnas apropiadas, renombrar para uso estándar
        if name_columns:
            headcount_df['NOMBRE_COMPLETO'] = headcount_df[name_columns[0]]
        if supervisor_columns:
            headcount_df['SUPERVISOR'] = headcount_df[supervisor_columns[0]]
        
        return headcount_df
        
    except Exception as e:
        print(f"❌ Error cargando BASE HEADCOUNT: {e}")
        return None

def generar_flujo_simple_mayo():
    """
    Versión simplificada para Mayo con manejo mejorado de datos
    """
    print("🎯 GENERADOR SIMPLIFICADO PARA MAYO 2025")
    print("=" * 60)
    
    try:
        # Cargar datos básicos
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        rutas_df = pd.read_excel('BD_Rutas_Junio.xlsx')
        headcount_df = load_headcount_data_fixed()
        
        # Convertir fechas
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        
        # Filtrar Mayo 2025
        mayo_feedbacks = feedbacks_df[
            (feedbacks_df['fecha_registro'].dt.month == 5) &
            (feedbacks_df['fecha_registro'].dt.year == 2025)
        ]
        
        print(f"📊 Feedbacks de Mayo 2025: {len(mayo_feedbacks)}")
        
        # Analizar rutas
        todas_las_rutas = set(rutas_df['RUTA'].dropna().unique())
        rutas_con_feedback = set(mayo_feedbacks['ruta'].dropna().unique())
        rutas_sin_feedback = todas_las_rutas - rutas_con_feedback
        
        print(f"📈 Total rutas: {len(todas_las_rutas)}")
        print(f"✅ Rutas que cumplieron: {len(rutas_con_feedback)}")
        print(f"❌ Rutas que NO cumplieron: {len(rutas_sin_feedback)}")
        
        # Crear Excel simple para las rutas que necesitan acción
        rutas_para_accion = []
        
        for ruta in sorted(rutas_sin_feedback):
            # Buscar datos básicos
            info_ruta = rutas_df[rutas_df['RUTA'] == ruta]
            reparto = 'No identificado'
            supervisor = 'No identificado'
            
            if not info_ruta.empty:
                # Obtener nombre del reparto
                for col in ['NOMBRE_VENDEDOR', 'VENDEDOR', 'NOMBRE']:
                    if col in info_ruta.columns and pd.notna(info_ruta[col].iloc[0]):
                        reparto = info_ruta[col].iloc[0]
                        break
                
                # Buscar supervisor en HEADCOUNT si está disponible
                if headcount_df is not None and 'NOMBRE_COMPLETO' in headcount_df.columns:
                    match = headcount_df[
                        headcount_df['NOMBRE_COMPLETO'].str.contains(reparto, case=False, na=False)
                    ]
                    if not match.empty and 'SUPERVISOR' in headcount_df.columns:
                        supervisor = match['SUPERVISOR'].iloc[0] if pd.notna(match['SUPERVISOR'].iloc[0]) else supervisor
            
            rutas_para_accion.append({
                'RUTA': ruta,
                'REPARTO': reparto,
                'SUPERVISOR_INMEDIATO': supervisor,
                'MES_INCUMPLIMIENTO': 'Mayo 2025',
                'NIVEL_CONSECUENCIA': '[LLENAR: 1, 2, 3 o 4]',
                'ACCION_REQUERIDA': '[LLENAR SEGÚN NIVEL]',
                'RESPONSABLE_EJECUCION': '[LLENAR SEGÚN NIVEL]',
                'FECHA_LIMITE': '[LLENAR: YYYY-MM-DD]',
                'FECHA_EJECUTADA': '',
                'ESTADO': 'PENDIENTE',
                'OBSERVACIONES': '',
                'EVIDENCIA': ''
            })
        
        # Crear DataFrame y Excel
        df_rutas = pd.DataFrame(rutas_para_accion)
        
        # Crear guía rápida corregida
        guia_data = [
            {
                'NIVEL': 'NIVEL 1',
                'ACCION': 'Llamada de atención verbal',
                'RESPONSABLE': 'Supervisor de Distribución',
                'PLAZO': '2 días',
                'PARA': 'Primera falta mensual'
            },
            {
                'NIVEL': 'NIVEL 2',
                'ACCION': 'Amonestación escrita',
                'RESPONSABLE': 'Coordinador de Distribución',
                'PLAZO': '3 días',
                'PARA': 'Segunda falta mensual'
            },
            {
                'NIVEL': 'NIVEL 3',
                'ACCION': 'Suspensión 1 día sin sueldo',
                'RESPONSABLE': 'Jefe de Distribución',
                'PLAZO': '5 días',
                'PARA': 'Tercera falta mensual'
            },
            {
                'NIVEL': 'NIVEL 4',
                'ACCION': 'Evaluación disciplinaria especial',
                'RESPONSABLE': 'Gerente CD Soyapango',
                'PLAZO': '1 semana',
                'PARA': 'Cuarta falta o más'
            }
        ]
        
        df_guia = pd.DataFrame(guia_data)
        
        # Generar Excel
        filename = f"FLUJO_CONSECUENCIAS_Mayo_2025_FINAL_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Hoja principal
            df_rutas.to_excel(writer, sheet_name='RUTAS_MAYO_2025', index=False)
            
            # Hoja de guía
            df_guia.to_excel(writer, sheet_name='GUIA_NIVELES', index=False)
            
            # Formateo
            workbook = writer.book
            
            # Formato de encabezado
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#366092',
                'font_color': 'white',
                'border': 1,
                'text_wrap': True
            })
            
            # Formato para pendientes
            pendiente_format = workbook.add_format({
                'bg_color': '#FFEB9C',
                'border': 1
            })
            
            # Aplicar formato
            worksheet = writer.sheets['RUTAS_MAYO_2025']
            worksheet.set_column('A:A', 12)  # RUTA
            worksheet.set_column('B:B', 25)  # REPARTO
            worksheet.set_column('C:C', 25)  # SUPERVISOR
            worksheet.set_column('D:L', 18)  # Resto
            
            # Encabezados
            for col_num, value in enumerate(df_rutas.columns):
                worksheet.write(0, col_num, value, header_format)
        
        print(f"✅ Excel generado: {filename}")
        
        # Mostrar resumen final
        print(f"\n📊 RESUMEN FINAL MAYO 2025:")
        print(f"   • Total rutas: {len(todas_las_rutas)}")
        print(f"   • Rutas que cumplieron: {len(rutas_con_feedback)} ({len(rutas_con_feedback)/len(todas_las_rutas)*100:.1f}%)")
        print(f"   • Rutas que NO cumplieron: {len(rutas_sin_feedback)}")
        
        if len(rutas_sin_feedback) > 0:
            print(f"\n🚨 RUTAS QUE REQUIEREN ACCIÓN INMEDIATA:")
            for i, ruta_data in enumerate(rutas_para_accion, 1):
                print(f"   {i}. {ruta_data['RUTA']} - {ruta_data['REPARTO']}")
        
        print(f"\n📋 INSTRUCCIONES:")
        print(f"1. Abrir: {filename}")
        print(f"2. Completar columnas según historial de cada ruta")
        print(f"3. Usar la hoja GUIA_NIVELES como referencia")
        print(f"4. Aplicar acciones según la jerarquía correcta")
        print(f"5. Documentar todo en el mismo Excel")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    generar_flujo_simple_mayo()

if __name__ == "__main__":
    main()
