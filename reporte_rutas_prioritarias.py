import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np

def generate_priority_offenders_report():
    """
    Genera un reporte específico de las rutas con mayor incumplimiento para priorizar acciones
    """
    print("🎯 GENERANDO REPORTE DE RUTAS PRIORITARIAS PARA ACCIÓN INMEDIATA")
    print("=" * 80)
    
    try:
        # Cargar datos
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        rutas_df = pd.read_excel('BD_Rutas_Junio.xlsx')
        
        # Convertir fechas
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        
        # Análisis de los últimos 6 meses
        current_date = datetime.now()
        six_months_ago = current_date - timedelta(days=180)
        
        # Filtrar feedbacks de los últimos 6 meses
        recent_feedbacks = feedbacks_df[feedbacks_df['fecha_registro'] >= six_months_ago]
        
        print(f"📊 Analizando feedbacks desde: {six_months_ago.strftime('%Y-%m-%d')}")
        print(f"📊 Total feedbacks en el período: {len(recent_feedbacks)}")
        
        # Obtener todas las rutas activas
        all_routes = set(rutas_df['RUTA'].unique())
        
        # Análisis mensual de cumplimiento por ruta
        monthly_compliance = []
        
        for month_offset in range(6):
            target_date = current_date - timedelta(days=30 * month_offset)
            target_month = target_date.month
            target_year = target_date.year
            
            # Feedbacks del mes
            month_feedbacks = recent_feedbacks[
                (recent_feedbacks['fecha_registro'].dt.month == target_month) &
                (recent_feedbacks['fecha_registro'].dt.year == target_year)
            ]
            
            # Rutas que SÍ hicieron feedback este mes
            routes_with_feedback = set(month_feedbacks['ruta'].dropna().unique())
            
            # Rutas que NO hicieron feedback
            routes_without_feedback = all_routes - routes_with_feedback
            
            # Registrar incumplimientos
            for route in routes_without_feedback:
                monthly_compliance.append({
                    'Ruta': route,
                    'Año': target_year,
                    'Mes': target_month,
                    'Cumplimiento': 0,
                    'Fecha': target_date.strftime('%Y-%m')
                })
            
            for route in routes_with_feedback:
                monthly_compliance.append({
                    'Ruta': route,
                    'Año': target_year,
                    'Mes': target_month,
                    'Cumplimiento': 1,
                    'Fecha': target_date.strftime('%Y-%m')
                })
        
        compliance_df = pd.DataFrame(monthly_compliance)
        
        # Calcular estadísticas por ruta
        route_stats = compliance_df.groupby('Ruta').agg({
            'Cumplimiento': ['count', 'sum', 'mean']
        }).round(3)
        
        route_stats.columns = ['Meses_Evaluados', 'Meses_Cumplidos', 'Porcentaje_Cumplimiento']
        route_stats['Meses_Incumplidos'] = route_stats['Meses_Evaluados'] - route_stats['Meses_Cumplidos']
        route_stats['Porcentaje_Cumplimiento'] = (route_stats['Porcentaje_Cumplimiento'] * 100).round(1)
        
        # Clasificar rutas por nivel de riesgo
        def classify_risk(row):
            incumplimientos = row['Meses_Incumplidos']
            porcentaje = row['Porcentaje_Cumplimiento']
            
            if incumplimientos >= 4 or porcentaje <= 33:
                return 'CRÍTICO'
            elif incumplimientos >= 3 or porcentaje <= 50:
                return 'ALTO'
            elif incumplimientos >= 2 or porcentaje <= 67:
                return 'MEDIO'
            elif incumplimientos >= 1 or porcentaje <= 83:
                return 'BAJO'
            else:
                return 'ÓPTIMO'
        
        route_stats['Nivel_Riesgo'] = route_stats.apply(classify_risk, axis=1)
        
        # Ordenar por prioridad (más incumplimientos primero)
        route_stats = route_stats.sort_values(['Meses_Incumplidos', 'Porcentaje_Cumplimiento'], 
                                            ascending=[False, True])
        
        # Agregar información de la ruta
        if 'NOMBRE_VENDEDOR' in rutas_df.columns:
            route_info = rutas_df[['RUTA', 'NOMBRE_VENDEDOR']].drop_duplicates()
            route_stats = route_stats.merge(route_info, left_index=True, right_on='RUTA', how='left')
            route_stats.set_index('RUTA', inplace=True)
        
        # Separar por nivel de riesgo
        rutas_criticas = route_stats[route_stats['Nivel_Riesgo'] == 'CRÍTICO']
        rutas_alto_riesgo = route_stats[route_stats['Nivel_Riesgo'] == 'ALTO']
        rutas_medio_riesgo = route_stats[route_stats['Nivel_Riesgo'] == 'MEDIO']
        
        print(f"\n🚨 RUTAS CRÍTICAS (Acción inmediata): {len(rutas_criticas)}")
        print(f"⚠️  RUTAS ALTO RIESGO: {len(rutas_alto_riesgo)}")
        print(f"📋 RUTAS MEDIO RIESGO: {len(rutas_medio_riesgo)}")
        
        # Crear plan de acción priorizado
        action_plan = []
        
        # Rutas críticas - Acción inmediata
        for ruta, data in rutas_criticas.head(10).iterrows():
            action_plan.append({
                'Ruta': ruta,
                'Vendedor': data.get('NOMBRE_VENDEDOR', 'No disponible'),
                'Incumplimientos': data['Meses_Incumplidos'],
                'Porcentaje_Cumplimiento': data['Porcentaje_Cumplimiento'],
                'Nivel_Riesgo': 'CRÍTICO',
                'Accion_Inmediata': 'Reunión urgente + Amonestación escrita',
                'Responsable': 'Jefe de Distribución',
                'Plazo': '24 horas',
                'Seguimiento': 'Semanal',
                'Prioridad': 1
            })
        
        # Rutas alto riesgo
        for ruta, data in rutas_alto_riesgo.head(15).iterrows():
            action_plan.append({
                'Ruta': ruta,
                'Vendedor': data.get('NOMBRE_VENDEDOR', 'No disponible'),
                'Incumplimientos': data['Meses_Incumplidos'],
                'Porcentaje_Cumplimiento': data['Porcentaje_Cumplimiento'],
                'Nivel_Riesgo': 'ALTO',
                'Accion_Inmediata': 'Llamada de atención + Capacitación',
                'Responsable': 'Coordinador de Distribución',
                'Plazo': '48 horas',
                'Seguimiento': 'Quincenal',
                'Prioridad': 2
            })
        
        # Rutas medio riesgo
        for ruta, data in rutas_medio_riesgo.head(20).iterrows():
            action_plan.append({
                'Ruta': ruta,
                'Vendedor': data.get('NOMBRE_VENDEDOR', 'No disponible'),
                'Incumplimientos': data['Meses_Incumplidos'],
                'Porcentaje_Cumplimiento': data['Porcentaje_Cumplimiento'],
                'Nivel_Riesgo': 'MEDIO',
                'Accion_Inmediata': 'Recordatorio + Monitoreo',
                'Responsable': 'Supervisor de Ruta',
                'Plazo': '1 semana',
                'Seguimiento': 'Mensual',
                'Prioridad': 3
            })
        
        action_plan_df = pd.DataFrame(action_plan)
        
        # Crear cronograma de acciones
        today = datetime.now()
        chronogram = []
        
        for _, action in action_plan_df.iterrows():
            if action['Plazo'] == '24 horas':
                fecha_limite = today + timedelta(hours=24)
            elif action['Plazo'] == '48 horas':
                fecha_limite = today + timedelta(hours=48)
            elif action['Plazo'] == '1 semana':
                fecha_limite = today + timedelta(days=7)
            else:
                fecha_limite = today + timedelta(days=3)
            
            chronogram.append({
                'Ruta': action['Ruta'],
                'Vendedor': action['Vendedor'],
                'Accion': action['Accion_Inmediata'],
                'Responsable': action['Responsable'],
                'Fecha_Limite': fecha_limite.strftime('%Y-%m-%d %H:%M'),
                'Estado': 'PENDIENTE',
                'Prioridad': action['Prioridad'],
                'Nivel_Riesgo': action['Nivel_Riesgo']
            })
        
        chronogram_df = pd.DataFrame(chronogram).sort_values(['Prioridad', 'Fecha_Limite'])
        
        # Generar archivo Excel con el reporte prioritario
        filename = f"Reporte_Rutas_Prioritarias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Hoja 1: Plan de acción priorizado
            action_plan_df.to_excel(writer, sheet_name='Plan_Accion_Prioritario', index=False)
            
            # Hoja 2: Cronograma de acciones
            chronogram_df.to_excel(writer, sheet_name='Cronograma_Acciones', index=False)
            
            # Hoja 3: Estadísticas completas por ruta
            route_stats.to_excel(writer, sheet_name='Estadisticas_Rutas')
            
            # Hoja 4: Rutas críticas detalle
            rutas_criticas.to_excel(writer, sheet_name='Rutas_Criticas')
            
            # Hoja 5: Dashboard resumen
            dashboard_data = {
                'Indicador': [
                    'Total Rutas Evaluadas',
                    'Rutas Críticas',
                    'Rutas Alto Riesgo',
                    'Rutas Medio Riesgo',
                    'Rutas Bajo Riesgo',
                    'Rutas Óptimas',
                    'Porcentaje Críticas',
                    'Acciones Inmediatas Requeridas'
                ],
                'Valor': [
                    len(route_stats),
                    len(rutas_criticas),
                    len(rutas_alto_riesgo),
                    len(rutas_medio_riesgo),
                    len(route_stats[route_stats['Nivel_Riesgo'] == 'BAJO']),
                    len(route_stats[route_stats['Nivel_Riesgo'] == 'ÓPTIMO']),
                    f"{(len(rutas_criticas) / len(route_stats) * 100):.1f}%",
                    len(action_plan_df[action_plan_df['Prioridad'] == 1])
                ]
            }
            dashboard_df = pd.DataFrame(dashboard_data)
            dashboard_df.to_excel(writer, sheet_name='Dashboard_Resumen', index=False)
            
            # Formateo
            workbook = writer.book
            
            # Formatos por nivel de riesgo
            critico_format = workbook.add_format({
                'bg_color': '#FF4444',
                'font_color': 'white',
                'bold': True,
                'border': 1
            })
            
            alto_format = workbook.add_format({
                'bg_color': '#FF8844',
                'border': 1
            })
            
            medio_format = workbook.add_format({
                'bg_color': '#FFAA44',
                'border': 1
            })
            
            # Aplicar formato condicional a las hojas principales
            for sheet_name in ['Plan_Accion_Prioritario', 'Cronograma_Acciones']:
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:Z', 18)
        
        print(f"\n✅ Reporte prioritario generado: {filename}")
        
        # Mostrar resumen en consola
        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"   • Total rutas evaluadas: {len(route_stats)}")
        print(f"   • Rutas críticas (acción inmediata): {len(rutas_criticas)}")
        print(f"   • Rutas alto riesgo: {len(rutas_alto_riesgo)}")
        print(f"   • Acciones programadas: {len(action_plan_df)}")
        
        if len(rutas_criticas) > 0:
            print(f"\n🚨 TOP 5 RUTAS CRÍTICAS:")
            for i, (ruta, data) in enumerate(rutas_criticas.head(5).iterrows(), 1):
                vendedor = data.get('NOMBRE_VENDEDOR', 'No disponible')
                print(f"   {i}. Ruta {ruta} - {vendedor} - {data['Meses_Incumplidos']} incumplimientos")
        
        return filename, route_stats, action_plan_df
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        return None, None, None

def create_weekly_monitoring_checklist():
    """
    Crea una checklist semanal para monitoreo
    """
    checklist_data = [
        {
            'Día': 'Lunes',
            'Actividad': 'Verificar feedbacks de la semana anterior',
            'Responsable': 'Coordinador de Distribución',
            'Tiempo': '30 min',
            'Output': 'Lista de rutas faltantes'
        },
        {
            'Día': 'Martes',
            'Actividad': 'Contactar rutas que no cumplieron',
            'Responsable': 'Supervisor de Rutas',
            'Tiempo': '45 min',
            'Output': 'Registro de contactos realizados'
        },
        {
            'Día': 'Miércoles',
            'Actividad': 'Aplicar consecuencias nivel 1 y 2',
            'Responsable': 'Coordinador de Distribución',
            'Tiempo': '60 min',
            'Output': 'Documentos disciplinarios'
        },
        {
            'Día': 'Jueves',
            'Actividad': 'Revisar casos escalados (nivel 3+)',
            'Responsable': 'Jefe de Distribución',
            'Tiempo': '45 min',
            'Output': 'Plan de acciones especiales'
        },
        {
            'Día': 'Viernes',
            'Actividad': 'Reporte semanal a gerencia',
            'Responsable': 'Coordinador de Distribución',
            'Tiempo': '30 min',
            'Output': 'Reporte ejecutivo semanal'
        }
    ]
    
    checklist_df = pd.DataFrame(checklist_data)
    
    # Guardar checklist
    checklist_filename = f"Checklist_Semanal_Monitoreo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    checklist_df.to_excel(checklist_filename, index=False)
    
    print(f"✅ Checklist semanal generada: {checklist_filename}")
    return checklist_filename

def main():
    """
    Función principal
    """
    # Generar reporte prioritario
    priority_file, stats, actions = generate_priority_offenders_report()
    
    if priority_file:
        # Generar checklist semanal
        checklist_file = create_weekly_monitoring_checklist()
        
        print(f"\n🎯 ARCHIVOS GENERADOS PARA ACCIÓN INMEDIATA:")
        print(f"   • {priority_file}")
        print(f"   • {checklist_file}")
        
        print(f"\n⚡ ACCIONES INMEDIATAS RECOMENDADAS:")
        print(f"   1. Revisar rutas críticas identificadas")
        print(f"   2. Contactar inmediatamente a supervisores responsables")
        print(f"   3. Programar reuniones urgentes con rutas críticas")
        print(f"   4. Implementar el cronograma de acciones")
        print(f"   5. Iniciar monitoreo semanal sistemático")

if __name__ == "__main__":
    main()
