import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import warnings
warnings.filterwarnings('ignore')

def analyze_route_compliance():
    """
    Analiza el cumplimiento de feedbacks por ruta y genera flujo de consecuencias
    """
    print("📊 ANÁLISIS DE CUMPLIMIENTO DE FEEDBACKS POR RUTA")
    print("=" * 60)
    
    try:
        # Cargar datos de feedbacks
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        print(f"✅ Datos cargados: {len(feedbacks_df)} registros de feedbacks")
        
        # Intentar cargar base de datos de rutas más reciente
        rutas_files = ['BD_Rutas_Junio.xlsx', 'BD_Rutas_Mayo.xlsx', 'BD_Rutas.xlsx']
        rutas_df = None
        
        for file in rutas_files:
            try:
                rutas_df = pd.read_excel(file)
                print(f"✅ Base de rutas cargada: {file}")
                break
            except FileNotFoundError:
                continue
        
        if rutas_df is None:
            print("❌ No se pudo cargar ninguna base de datos de rutas")
            return None
            
        return feedbacks_df, rutas_df
        
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None

def create_consequence_flow(feedbacks_df, rutas_df):
    """
    Crea el flujo de consecuencias para rutas que no cumplen con feedbacks
    """
    print("\n🔍 GENERANDO FLUJO DE CONSECUENCIAS...")
    
    # Convertir fechas
    feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
    
    # Obtener el mes actual y anterior para análisis
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Analizar por mes
    monthly_analysis = []
    
    for month_offset in range(6):  # Analizar últimos 6 meses
        target_date = current_date - timedelta(days=30 * month_offset)
        target_month = target_date.month
        target_year = target_date.year
        month_name = calendar.month_name[target_month]
        
        # Filtrar feedbacks del mes
        month_feedbacks = feedbacks_df[
            (feedbacks_df['fecha_registro'].dt.month == target_month) &
            (feedbacks_df['fecha_registro'].dt.year == target_year)
        ]
        
        # Obtener rutas únicas del mes
        rutas_con_feedback = set(month_feedbacks['ruta'].dropna().unique())
        
        # Obtener todas las rutas que deberían tener feedback
        if 'RUTA' in rutas_df.columns:
            todas_las_rutas = set(rutas_df['RUTA'].dropna().unique())
        elif 'ruta' in rutas_df.columns:
            todas_las_rutas = set(rutas_df['ruta'].dropna().unique())
        else:
            # Si no hay columna de rutas clara, usar las rutas de feedbacks
            todas_las_rutas = set(feedbacks_df['ruta'].dropna().unique())
        
        # Rutas que NO realizaron feedback
        rutas_sin_feedback = todas_las_rutas - rutas_con_feedback
        
        # Calcular estadísticas
        total_rutas = len(todas_las_rutas)
        rutas_cumplieron = len(rutas_con_feedback)
        rutas_no_cumplieron = len(rutas_sin_feedback)
        porcentaje_cumplimiento = (rutas_cumplieron / total_rutas * 100) if total_rutas > 0 else 0
        
        monthly_analysis.append({
            'Año': target_year,
            'Mes': month_name,
            'Mes_Num': target_month,
            'Total_Rutas': total_rutas,
            'Rutas_Con_Feedback': rutas_cumplieron,
            'Rutas_Sin_Feedback': rutas_no_cumplieron,
            'Porcentaje_Cumplimiento': round(porcentaje_cumplimiento, 2),
            'Rutas_Incumplidas': list(rutas_sin_feedback)
        })
        
        print(f"\n📅 {month_name} {target_year}:")
        print(f"   • Total rutas: {total_rutas}")
        print(f"   • Rutas con feedback: {rutas_cumplieron}")
        print(f"   • Rutas sin feedback: {rutas_no_cumplieron}")
        print(f"   • % Cumplimiento: {porcentaje_cumplimiento:.1f}%")
    
    return monthly_analysis

def generate_consequence_flow_excel(monthly_analysis):
    """
    Genera el archivo Excel con el flujo de consecuencias
    """
    print("\n📋 GENERANDO ARCHIVO DE CONSECUENCIAS...")
    
    # Crear DataFrames para diferentes hojas
    
    # 1. Resumen mensual
    resumen_df = pd.DataFrame([
        {
            'Año': item['Año'],
            'Mes': item['Mes'],
            'Total_Rutas': item['Total_Rutas'],
            'Rutas_Con_Feedback': item['Rutas_Con_Feedback'],
            'Rutas_Sin_Feedback': item['Rutas_Sin_Feedback'],
            'Porcentaje_Cumplimiento': item['Porcentaje_Cumplimiento']
        }
        for item in monthly_analysis
    ])
    
    # 2. Detalle de rutas incumplidas por mes
    rutas_incumplidas = []
    for item in monthly_analysis:
        for ruta in item['Rutas_Incumplidas']:
            rutas_incumplidas.append({
                'Año': item['Año'],
                'Mes': item['Mes'],
                'Ruta': ruta,
                'Estado': 'INCUMPLIMIENTO',
                'Fecha_Deteccion': datetime.now().strftime('%Y-%m-%d')
            })
    
    rutas_incumplidas_df = pd.DataFrame(rutas_incumplidas)
    
    # 3. Flujo de consecuencias progresivas
    flujo_consecuencias = []
    
    # Contar incumplimientos por ruta
    ruta_incumplimientos = {}
    for item in monthly_analysis:
        for ruta in item['Rutas_Incumplidas']:
            if ruta not in ruta_incumplimientos:
                ruta_incumplimientos[ruta] = 0
            ruta_incumplimientos[ruta] += 1
    
    # Definir consecuencias según el número de incumplimientos
    for ruta, incumplimientos in ruta_incumplimientos.items():
        if incumplimientos == 1:
            consecuencia = "LLAMADA DE ATENCIÓN VERBAL"
            nivel = "NIVEL 1"
        elif incumplimientos == 2:
            consecuencia = "AMONESTACIÓN ESCRITA"
            nivel = "NIVEL 2"
        elif incumplimientos == 3:
            consecuencia = "SUSPENSIÓN DE 1 DÍA"
            nivel = "NIVEL 3"
        elif incumplimientos >= 4:
            consecuencia = "EVALUACIÓN PARA SUSPENSIÓN EXTENDIDA"
            nivel = "NIVEL 4"
        else:
            consecuencia = "SIN CONSECUENCIAS"
            nivel = "NIVEL 0"
        
        flujo_consecuencias.append({
            'Ruta': ruta,
            'Incumplimientos_Totales': incumplimientos,
            'Nivel_Consecuencia': nivel,
            'Accion_Requerida': consecuencia,
            'Fecha_Evaluacion': datetime.now().strftime('%Y-%m-%d'),
            'Estado': 'PENDIENTE',
            'Responsable': 'Coordinador de Distribución',
            'Fecha_Limite_Accion': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        })
    
    flujo_df = pd.DataFrame(flujo_consecuencias)
    
    # 4. Hoja de seguimiento de acciones
    seguimiento_df = pd.DataFrame([
        {
            'Ruta': row['Ruta'],
            'Nivel': row['Nivel_Consecuencia'],
            'Accion': row['Accion_Requerida'],
            'Fecha_Programada': row['Fecha_Limite_Accion'],
            'Fecha_Ejecutada': '',
            'Responsable_Ejecucion': '',
            'Observaciones': '',
            'Estado': 'PENDIENTE',
            'Evidencia': ''
        }
        for _, row in flujo_df.iterrows()
    ])
    
    # Crear archivo Excel con múltiples hojas
    filename = f"Flujo_Consecuencias_Feedbacks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Hoja 1: Resumen ejecutivo
        resumen_df.to_excel(writer, sheet_name='Resumen_Mensual', index=False)
        
        # Hoja 2: Rutas incumplidas detallado
        rutas_incumplidas_df.to_excel(writer, sheet_name='Rutas_Incumplidas', index=False)
        
        # Hoja 3: Flujo de consecuencias
        flujo_df.to_excel(writer, sheet_name='Flujo_Consecuencias', index=False)
        
        # Hoja 4: Seguimiento de acciones
        seguimiento_df.to_excel(writer, sheet_name='Seguimiento_Acciones', index=False)
        
        # Acceder al workbook para formato
        workbook = writer.book
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#366092',
            'font_color': 'white',
            'border': 1
        })
        
        nivel1_format = workbook.add_format({
            'bg_color': '#FFEB9C',
            'border': 1
        })
        
        nivel2_format = workbook.add_format({
            'bg_color': '#FFCC99',
            'border': 1
        })
        
        nivel3_format = workbook.add_format({
            'bg_color': '#FF9999',
            'border': 1
        })
        
        nivel4_format = workbook.add_format({
            'bg_color': '#FF6666',
            'border': 1
        })
          # Aplicar formato a las hojas
        for sheet_name in ['Resumen_Mensual', 'Rutas_Incumplidas', 'Flujo_Consecuencias', 'Seguimiento_Acciones']:
            worksheet = writer.sheets[sheet_name]
            
            # Ajustar ancho de columnas
            worksheet.set_column('A:Z', 20)
            
            # Aplicar formato de encabezado a la primera fila
            for col_num in range(20):  # Aplicar a las primeras 20 columnas
                worksheet.set_row(0, None, header_format)
    
    print(f"✅ Archivo generado: {filename}")
    return filename

def generate_action_plan():
    """
    Genera un plan de acción complementario
    """
    print("\n📋 GENERANDO PLAN DE ACCIÓN...")
    
    plan_data = [
        {
            'Actividad': 'Revisión Semanal de Cumplimiento',
            'Responsable': 'Coordinador de Distribución',
            'Frecuencia': 'Semanal - Viernes',
            'Descripcion': 'Revisar que todas las rutas hayan completado sus feedbacks semanales',
            'Tiempo_Estimado': '30 minutos',
            'KPI': 'Porcentaje de rutas con feedback >= 95%'
        },
        {
            'Actividad': 'Notificación de Incumplimiento',
            'Responsable': 'Supervisor de Ruta',
            'Frecuencia': 'Inmediata al detectar',
            'Descripcion': 'Contactar inmediatamente a la ruta que no cumplió',
            'Tiempo_Estimado': '15 minutos',
            'KPI': 'Tiempo de respuesta < 24 horas'
        },
        {
            'Actividad': 'Aplicación de Consecuencias',
            'Responsable': 'Gerente CD / Jefe Distribución',
            'Frecuencia': 'Según flujo de consecuencias',
            'Descripcion': 'Ejecutar las acciones disciplinarias según el nivel',
            'Tiempo_Estimado': '60 minutos',
            'KPI': 'Reducción de reincidencia'
        },
        {
            'Actividad': 'Capacitación Preventiva',
            'Responsable': 'TL de Ventas',
            'Frecuencia': 'Mensual',
            'Descripcion': 'Reforzar la importancia de los feedbacks',
            'Tiempo_Estimado': '45 minutos',
            'KPI': 'Mejora en cumplimiento mes a mes'
        },
        {
            'Actividad': 'Reporte Ejecutivo',
            'Responsable': 'Coordinador de Distribución',
            'Frecuencia': 'Mensual',
            'Descripcion': 'Presentar resultados y tendencias a gerencia',
            'Tiempo_Estimado': '60 minutos',
            'KPI': 'Cumplimiento global de objetivos'
        }
    ]
    
    plan_df = pd.DataFrame(plan_data)
    
    # Guardar plan de acción
    plan_filename = f"Plan_Accion_Feedbacks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    plan_df.to_excel(plan_filename, index=False)
    
    print(f"✅ Plan de acción generado: {plan_filename}")
    return plan_filename

def main():
    """
    Función principal para ejecutar el análisis completo
    """
    print("🚀 INICIANDO ANÁLISIS DE FLUJO DE CONSECUENCIAS")
    print("=" * 70)
    
    # Cargar datos
    data = analyze_route_compliance()
    if data is None:
        return
    
    feedbacks_df, rutas_df = data
    
    # Crear análisis mensual
    monthly_analysis = create_consequence_flow(feedbacks_df, rutas_df)
    
    # Generar archivo de consecuencias
    consequence_file = generate_consequence_flow_excel(monthly_analysis)
    
    # Generar plan de acción
    action_plan_file = generate_action_plan()
    
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print(f"📁 Archivos generados:")
    print(f"   • {consequence_file}")
    print(f"   • {action_plan_file}")
    print("\n📋 PRÓXIMOS PASOS:")
    print("   1. Revisar las rutas con incumplimientos")
    print("   2. Contactar a los supervisores responsables")
    print("   3. Aplicar las consecuencias según el nivel")
    print("   4. Hacer seguimiento semanal del cumplimiento")
    print("   5. Documentar todas las acciones tomadas")

if __name__ == "__main__":
    main()
