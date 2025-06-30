import pandas as pd
from datetime import datetime, timedelta
import calendar

def create_simple_monthly_consequences_flow():
    """
    Crea un Excel simple y escalable para el flujo de consecuencias mensual
    """
    print("📋 CREANDO FLUJO DE CONSECUENCIAS MENSUAL SIMPLIFICADO")
    print("=" * 60)
    
    try:
        # Cargar datos de feedbacks
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        rutas_df = pd.read_excel('BD_Rutas_Mayo.xlsx')  # Usar Mayo como base
        
        print(f"✅ Datos cargados: {len(feedbacks_df)} feedbacks")
        print(f"✅ Base de rutas Mayo: {len(rutas_df)} rutas")
        
        # Convertir fechas
        feedbacks_df['fecha_registro'] = pd.to_datetime(feedbacks_df['fecha_registro'])
        
        # Filtrar feedbacks de Mayo 2025
        mayo_feedbacks = feedbacks_df[
            (feedbacks_df['fecha_registro'].dt.month == 5) &
            (feedbacks_df['fecha_registro'].dt.year == 2025)
        ]
        
        print(f"📊 Feedbacks de Mayo 2025: {len(mayo_feedbacks)}")
        
        # Obtener todas las rutas que deberían haber hecho feedback en Mayo
        todas_las_rutas_mayo = set(rutas_df['RUTA'].dropna().unique())
        
        # Rutas que SÍ hicieron feedback en Mayo
        rutas_con_feedback_mayo = set(mayo_feedbacks['ruta'].dropna().unique())
        
        # Rutas que NO hicieron feedback en Mayo (estas necesitan consecuencias)
        rutas_sin_feedback_mayo = todas_las_rutas_mayo - rutas_con_feedback_mayo
        
        print(f"📈 Total rutas esperadas en Mayo: {len(todas_las_rutas_mayo)}")
        print(f"✅ Rutas que sí cumplieron: {len(rutas_con_feedback_mayo)}")
        print(f"❌ Rutas que NO cumplieron: {len(rutas_sin_feedback_mayo)}")
        
        # Crear DataFrame principal con las rutas que necesitan consecuencias
        consecuencias_data = []
        
        for ruta in rutas_sin_feedback_mayo:
            # Buscar información del vendedor en la base de rutas
            ruta_info = rutas_df[rutas_df['RUTA'] == ruta]
            vendedor = ruta_info['NOMBRE_VENDEDOR'].iloc[0] if not ruta_info.empty and 'NOMBRE_VENDEDOR' in ruta_info.columns else 'No disponible'
            
            consecuencias_data.append({
                'RUTA': ruta,
                'VENDEDOR/CONDUCTOR': vendedor,
                'MES_INCUMPLIMIENTO': 'Mayo 2025',
                'FECHA_DETECCION': datetime.now().strftime('%Y-%m-%d'),
                'NIVEL_CONSECUENCIA': 'PENDIENTE EVALUAR',
                'ACCION_REQUERIDA': 'PENDIENTE ASIGNAR',
                'RESPONSABLE': 'PENDIENTE ASIGNAR',
                'FECHA_LIMITE_ACCION': '',
                'FECHA_EJECUCION': '',
                'ESTADO': 'PENDIENTE',
                'OBSERVACIONES': '',
                'EVIDENCIA_DOCUMENTO': ''
            })
        
        # Crear DataFrame
        consecuencias_df = pd.DataFrame(consecuencias_data)
        
        # Crear plantilla de niveles de consecuencias
        niveles_data = [
            {
                'NIVEL': 'NIVEL 1',
                'TIPO_ACCION': 'Llamada de Atención Verbal',
                'PARA_CUANDO': 'Primer incumplimiento mensual',
                'RESPONSABLE': 'Supervisor de Ruta',
                'PLAZO_MAXIMO': '48 horas desde detección',
                'DOCUMENTACION': 'Registro verbal en sistema',
                'SE_ARCHIVA': 'No'
            },
            {
                'NIVEL': 'NIVEL 2',
                'TIPO_ACCION': 'Amonestación Escrita',
                'PARA_CUANDO': 'Segundo incumplimiento mensual',
                'RESPONSABLE': 'Coordinador de Distribución',
                'PLAZO_MAXIMO': '3 días desde detección',
                'DOCUMENTACION': 'Memorándum escrito',
                'SE_ARCHIVA': 'Sí - Expediente personal'
            },
            {
                'NIVEL': 'NIVEL 3',
                'TIPO_ACCION': 'Suspensión 1 día sin sueldo',
                'PARA_CUANDO': 'Tercer incumplimiento mensual',
                'RESPONSABLE': 'Jefe de Distribución',
                'PLAZO_MAXIMO': '5 días desde detección',
                'DOCUMENTACION': 'Acta de suspensión',
                'SE_ARCHIVA': 'Sí - Expediente + RRHH'
            },
            {
                'NIVEL': 'NIVEL 4',
                'TIPO_ACCION': 'Evaluación por Comité',
                'PARA_CUANDO': 'Cuarto incumplimiento o más',
                'RESPONSABLE': 'Gerente CD + Comité',
                'PLAZO_MAXIMO': '1 semana desde detección',
                'DOCUMENTACION': 'Acta de evaluación y decisión',
                'SE_ARCHIVA': 'Sí - Todos los archivos'
            }
        ]
        
        niveles_df = pd.DataFrame(niveles_data)
        
        # Crear plantilla de seguimiento mensual
        seguimiento_mensual = [
            {
                'MES': 'Mayo 2025',
                'TOTAL_RUTAS': len(todas_las_rutas_mayo),
                'RUTAS_CUMPLIERON': len(rutas_con_feedback_mayo),
                'RUTAS_NO_CUMPLIERON': len(rutas_sin_feedback_mayo),
                'PORCENTAJE_CUMPLIMIENTO': round((len(rutas_con_feedback_mayo) / len(todas_las_rutas_mayo)) * 100, 1),
                'ACCIONES_NIVEL_1': 0,
                'ACCIONES_NIVEL_2': 0,
                'ACCIONES_NIVEL_3': 0,
                'ACCIONES_NIVEL_4': 0,
                'FECHA_REVISION': datetime.now().strftime('%Y-%m-%d'),
                'RESPONSABLE_REVISION': 'Coordinador de Distribución'
            }
        ]
        
        seguimiento_df = pd.DataFrame(seguimiento_mensual)
        
        # Crear plantilla para próximos meses (formato reutilizable)
        meses_template = []
        for i in range(1, 13):  # 12 meses
            mes_nombre = calendar.month_name[i]
            meses_template.append({
                'MES': f'{mes_nombre} 2025',
                'TOTAL_RUTAS': 'Actualizar según BD_Rutas del mes',
                'RUTAS_CUMPLIERON': 'Contar automáticamente',
                'RUTAS_NO_CUMPLIERON': 'Contar automáticamente',
                'PORCENTAJE_CUMPLIMIENTO': 'Calcular automáticamente',
                'ACCIONES_NIVEL_1': 'Llenar según acciones tomadas',
                'ACCIONES_NIVEL_2': 'Llenar según acciones tomadas',
                'ACCIONES_NIVEL_3': 'Llenar según acciones tomadas',
                'ACCIONES_NIVEL_4': 'Llenar según acciones tomadas',
                'FECHA_REVISION': 'Llenar al final del mes',
                'RESPONSABLE_REVISION': 'Coordinador de Distribución'
            })
        
        template_df = pd.DataFrame(meses_template)
        
        # Crear archivo Excel simplificado
        filename = f"Flujo_Consecuencias_MENSUAL_Mayo2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Hoja 1: Rutas para consecuencias (Mayo 2025)
            consecuencias_df.to_excel(writer, sheet_name='Mayo_2025_Consecuencias', index=False)
            
            # Hoja 2: Niveles de consecuencias (guía)
            niveles_df.to_excel(writer, sheet_name='Guia_Niveles', index=False)
            
            # Hoja 3: Seguimiento mensual
            seguimiento_df.to_excel(writer, sheet_name='Seguimiento_Mensual', index=False)
            
            # Hoja 4: Template para otros meses
            template_df.to_excel(writer, sheet_name='Template_Otros_Meses', index=False)
            
            # Obtener workbook para formateo
            workbook = writer.book
            
            # Formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            
            pendiente_format = workbook.add_format({
                'bg_color': '#FFEB9C',
                'border': 1
            })
            
            critico_format = workbook.add_format({
                'bg_color': '#FFC7CE',
                'border': 1
            })
            
            # Aplicar formato a las hojas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                
                # Ajustar ancho de columnas
                worksheet.set_column('A:A', 12)  # RUTA
                worksheet.set_column('B:B', 25)  # VENDEDOR
                worksheet.set_column('C:C', 15)  # MES
                worksheet.set_column('D:F', 18)  # FECHAS Y NIVELES
                worksheet.set_column('G:L', 20)  # RESTO DE COLUMNAS
                
                # Formato de encabezados (primera fila)
                for col in range(15):
                    worksheet.set_row(0, None, header_format)
        
        print(f"✅ Archivo generado: {filename}")
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN PARA MAYO 2025:")
        print(f"   • Total rutas: {len(todas_las_rutas_mayo)}")
        print(f"   • Rutas que cumplieron: {len(rutas_con_feedback_mayo)}")
        print(f"   • Rutas para consecuencias: {len(rutas_sin_feedback_mayo)}")
        print(f"   • % Cumplimiento: {round((len(rutas_con_feedback_mayo) / len(todas_las_rutas_mayo)) * 100, 1)}%")
        
        if len(rutas_sin_feedback_mayo) > 0:
            print(f"\n🚨 RUTAS QUE REQUIEREN ACCIÓN (Mayo 2025):")
            for i, ruta in enumerate(sorted(list(rutas_sin_feedback_mayo))[:10], 1):
                print(f"   {i}. {ruta}")
            if len(rutas_sin_feedback_mayo) > 10:
                print(f"   ... y {len(rutas_sin_feedback_mayo) - 10} rutas más")
        
        return filename, len(rutas_sin_feedback_mayo)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, 0

def create_instructions():
    """
    Crea un archivo de instrucciones para usar el sistema
    """
    instructions = """
# 📋 INSTRUCCIONES - FLUJO DE CONSECUENCIAS MENSUAL

## 🎯 USO DEL EXCEL GENERADO

### HOJA 1: "Mayo_2025_Consecuencias"
Esta hoja contiene todas las rutas que NO hicieron feedback en Mayo 2025.

**PASOS A SEGUIR:**
1. Para cada ruta, completar la columna "NIVEL_CONSECUENCIA":
   - NIVEL 1: Si es primera vez que no cumple
   - NIVEL 2: Si es segunda vez que no cumple  
   - NIVEL 3: Si es tercera vez que no cumple
   - NIVEL 4: Si es cuarta vez o más que no cumple

2. Completar "ACCION_REQUERIDA" según el nivel:
   - NIVEL 1: "Llamada de atención verbal"
   - NIVEL 2: "Amonestación escrita"
   - NIVEL 3: "Suspensión 1 día sin sueldo"
   - NIVEL 4: "Evaluación por comité"

3. Asignar "RESPONSABLE" según el nivel:
   - NIVEL 1: Supervisor de Ruta
   - NIVEL 2: Coordinador de Distribución
   - NIVEL 3: Jefe de Distribución
   - NIVEL 4: Gerente CD + Comité

4. Establecer "FECHA_LIMITE_ACCION" (máximo 5 días desde hoy)

5. Una vez ejecutada la acción, llenar:
   - FECHA_EJECUCION
   - ESTADO (cambiar a "EJECUTADA")
   - OBSERVACIONES
   - EVIDENCIA_DOCUMENTO

### HOJA 2: "Guia_Niveles"
Referencia rápida de qué acción tomar según el nivel.

### HOJA 3: "Seguimiento_Mensual"
Actualizar las estadísticas conforme se ejecuten las acciones.

### HOJA 4: "Template_Otros_Meses"
Copiar para crear el seguimiento de otros meses.

## 🔄 PROCESO MENSUAL

### AL FINAL DE CADA MES:
1. Correr este script cambiando el mes en el código
2. Revisar las rutas que no cumplieron
3. Asignar niveles de consecuencia
4. Ejecutar las acciones dentro de los plazos
5. Documentar todo en el Excel
6. Archivar el archivo completado

### ESCALAMIENTO:
- Si una ruta ya tiene historial de incumplimientos, aplicar el siguiente nivel
- Mantener registro histórico para referencia
- Revisar efectividad del sistema cada trimestre

## ⚠️ IMPORTANTE:
- Este sistema es MENSUAL, no semanal
- Cada mes generar un nuevo Excel
- Mantener archivos históricos
- Seguir siempre los plazos establecidos
"""
    
    instructions_file = f"INSTRUCCIONES_Flujo_Consecuencias_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Instrucciones creadas: {instructions_file}")
    return instructions_file

def main():
    """
    Función principal simplificada
    """
    print("🎯 SISTEMA SIMPLIFICADO DE CONSECUENCIAS MENSUAL")
    print("=" * 60)
    print("Base: MAYO 2025")
    print("=" * 60)
    
    # Generar Excel simplificado
    excel_file, rutas_pendientes = create_simple_monthly_consequences_flow()
    
    if excel_file:
        # Crear instrucciones
        instructions_file = create_instructions()
        
        print("\n" + "=" * 60)
        print("✅ SISTEMA SIMPLIFICADO GENERADO")
        print(f"📁 Archivos creados:")
        print(f"   • {excel_file}")
        print(f"   • {instructions_file}")
        
        print(f"\n📋 PRÓXIMOS PASOS:")
        print(f"   1. Abrir el Excel: {excel_file}")
        print(f"   2. Completar las columnas según las instrucciones")
        print(f"   3. Asignar responsables y fechas límite")
        print(f"   4. Ejecutar las acciones disciplinarias")
        print(f"   5. Documentar todo en el mismo Excel")
        
        print(f"\n🚨 URGENTE: {rutas_pendientes} rutas necesitan acción inmediata")

if __name__ == "__main__":
    main()
