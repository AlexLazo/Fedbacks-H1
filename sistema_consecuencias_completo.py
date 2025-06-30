import pandas as pd
from datetime import datetime, timedelta
import os

def create_disciplinary_templates():
    """
    Crea plantillas de documentos disciplinarios para diferentes niveles de incumplimiento
    """
    print("📋 CREANDO PLANTILLAS DISCIPLINARIAS...")
    
    # Plantilla para Nivel 1 - Llamada de Atención Verbal
    nivel1_template = {
        'Documento': 'ACTA DE LLAMADA DE ATENCIÓN VERBAL',
        'Nivel': 'NIVEL 1',
        'Fecha': '{fecha}',
        'Ruta': '{ruta}',
        'Conductor': '{conductor}',
        'Motivo': 'Incumplimiento en la realización de Feedback semanal',
        'Descripcion': 'El conductor de la ruta {ruta} no realizó el feedback correspondiente en el período {periodo}.',
        'Accion': 'Se realiza llamada de atención verbal sobre la importancia de cumplir con los feedbacks semanales.',
        'Compromiso': 'El conductor se compromete a realizar todos los feedbacks en tiempo y forma.',
        'Supervisor': '{supervisor}',
        'Firma_Conductor': '_____________________',
        'Firma_Supervisor': '_____________________',
        'Observaciones': ''
    }
    
    # Plantilla para Nivel 2 - Amonestación Escrita
    nivel2_template = {
        'Documento': 'AMONESTACIÓN ESCRITA',
        'Nivel': 'NIVEL 2',
        'Fecha': '{fecha}',
        'Ruta': '{ruta}',
        'Conductor': '{conductor}',
        'Motivo': 'Segundo incumplimiento en la realización de Feedback semanal',
        'Descripcion': 'El conductor de la ruta {ruta} ha incumplido por segunda vez con la realización del feedback semanal.',
        'Accion': 'Se emite amonestación escrita y se archiva en expediente personal.',
        'Consecuencias': 'El próximo incumplimiento resultará en suspensión de un día sin goce de sueldo.',
        'Supervisor': '{supervisor}',
        'Firma_Conductor': '_____________________',
        'Firma_Supervisor': '_____________________',
        'Firma_RRHH': '_____________________',
        'Observaciones': ''
    }
    
    # Plantilla para Nivel 3 - Suspensión
    nivel3_template = {
        'Documento': 'ACTA DE SUSPENSIÓN',
        'Nivel': 'NIVEL 3',
        'Fecha': '{fecha}',
        'Ruta': '{ruta}',
        'Conductor': '{conductor}',
        'Motivo': 'Tercer incumplimiento en la realización de Feedback semanal',
        'Descripcion': 'El conductor de la ruta {ruta} ha incumplido por tercera vez con la realización del feedback semanal.',
        'Accion': 'Suspensión de un (1) día sin goce de sueldo.',
        'Fecha_Suspension': '{fecha_suspension}',
        'Fecha_Reintegro': '{fecha_reintegro}',
        'Consecuencias': 'El próximo incumplimiento será evaluado para suspensión extendida o medidas adicionales.',
        'Supervisor': '{supervisor}',
        'Gerente': '{gerente}',
        'Firma_Conductor': '_____________________',
        'Firma_Supervisor': '_____________________',
        'Firma_Gerente': '_____________________',
        'Firma_RRHH': '_____________________',
        'Observaciones': ''
    }
    
    # Plantilla para Nivel 4 - Evaluación Extendida
    nivel4_template = {
        'Documento': 'EVALUACIÓN PARA MEDIDAS DISCIPLINARIAS EXTENDIDAS',
        'Nivel': 'NIVEL 4',
        'Fecha': '{fecha}',
        'Ruta': '{ruta}',
        'Conductor': '{conductor}',
        'Motivo': 'Cuarto incumplimiento en la realización de Feedback semanal',
        'Descripcion': 'El conductor de la ruta {ruta} ha incumplido repetidamente con la realización del feedback semanal.',
        'Historial': 'Llamada atención verbal, amonestación escrita, suspensión de 1 día.',
        'Evaluacion': 'Se requiere evaluación por comité disciplinario para determinar medidas adicionales.',
        'Opciones': [
            'Suspensión extendida (3-5 días)',
            'Capacitación obligatoria',
            'Cambio de ruta',
            'Otras medidas según evaluación'
        ],
        'Comite': [
            'Gerente CD Soyapango',
            'Jefe de Distribución',
            'Coordinador de Distribución',
            'Recursos Humanos'
        ],
        'Fecha_Evaluacion': '{fecha_evaluacion}',
        'Decision': '___________________',
        'Firma_Comite': '_____________________',
        'Observaciones': ''
    }
    
    return {
        'Nivel_1': nivel1_template,
        'Nivel_2': nivel2_template,
        'Nivel_3': nivel3_template,
        'Nivel_4': nivel4_template
    }

def create_tracking_system():
    """
    Crea sistema de seguimiento de acciones disciplinarias
    """
    tracking_data = [
        {
            'Campo': 'ID_Accion',
            'Descripcion': 'Identificador único de la acción disciplinaria',
            'Tipo': 'Autoincremento',
            'Ejemplo': 'DISC-2024-001'
        },
        {
            'Campo': 'Fecha_Accion',
            'Descripcion': 'Fecha en que se ejecutó la acción',
            'Tipo': 'Fecha',
            'Ejemplo': '2024-06-19'
        },
        {
            'Campo': 'Ruta',
            'Descripcion': 'Código de la ruta involucrada',
            'Tipo': 'Texto',
            'Ejemplo': 'R001'
        },
        {
            'Campo': 'Conductor',
            'Descripcion': 'Nombre del conductor',
            'Tipo': 'Texto',
            'Ejemplo': 'Juan Pérez'
        },
        {
            'Campo': 'Nivel_Consecuencia',
            'Descripcion': 'Nivel de la consecuencia aplicada',
            'Tipo': 'Lista',
            'Ejemplo': 'NIVEL 1, NIVEL 2, NIVEL 3, NIVEL 4'
        },
        {
            'Campo': 'Tipo_Accion',
            'Descripcion': 'Tipo específico de acción tomada',
            'Tipo': 'Lista',
            'Ejemplo': 'Verbal, Escrita, Suspensión, Evaluación'
        },
        {
            'Campo': 'Responsable_Ejecucion',
            'Descripcion': 'Quien ejecutó la acción',
            'Tipo': 'Texto',
            'Ejemplo': 'Óscar Cuellar'
        },
        {
            'Campo': 'Estado',
            'Descripcion': 'Estado actual de la acción',
            'Tipo': 'Lista',
            'Ejemplo': 'Pendiente, Ejecutada, Documentada'
        },
        {
            'Campo': 'Evidencia_Documento',
            'Descripcion': 'Referencia al documento de evidencia',
            'Tipo': 'Texto',
            'Ejemplo': 'AMON-R001-20240619.pdf'
        },
        {
            'Campo': 'Fecha_Seguimiento',
            'Descripcion': 'Fecha de próximo seguimiento',
            'Tipo': 'Fecha',
            'Ejemplo': '2024-06-26'
        },
        {
            'Campo': 'Observaciones',
            'Descripcion': 'Notas adicionales sobre la acción',
            'Tipo': 'Texto largo',
            'Ejemplo': 'Conductor mostró disposición a mejorar'
        }
    ]
    
    tracking_df = pd.DataFrame(tracking_data)
    return tracking_df

def create_escalation_matrix():
    """
    Crea matriz de escalamiento para diferentes escenarios
    """
    escalation_data = [
        {
            'Incumplimientos': 1,
            'Nivel': 'NIVEL 1',
            'Accion': 'Llamada de Atención Verbal',
            'Responsable': 'Supervisor de Ruta',
            'Tiempo_Limite': '24 horas',
            'Documentacion': 'Acta verbal',
            'Archivo': 'No'
        },
        {
            'Incumplimientos': 2,
            'Nivel': 'NIVEL 2',
            'Accion': 'Amonestación Escrita',
            'Responsable': 'Coordinador de Distribución',
            'Tiempo_Limite': '48 horas',
            'Documentacion': 'Memorándum escrito',
            'Archivo': 'Expediente personal'
        },
        {
            'Incumplimientos': 3,
            'Nivel': 'NIVEL 3',
            'Accion': 'Suspensión 1 día',
            'Responsable': 'Jefe de Distribución',
            'Tiempo_Limite': '72 horas',
            'Documentacion': 'Acta de suspensión',
            'Archivo': 'Expediente + RRHH'
        },
        {
            'Incumplimientos': '4+',
            'Nivel': 'NIVEL 4',
            'Accion': 'Evaluación por Comité',
            'Responsable': 'Gerente CD + Comité',
            'Tiempo_Limite': '1 semana',
            'Documentacion': 'Acta de evaluación',
            'Archivo': 'Expediente + RRHH + Gerencia'
        }
    ]
    
    escalation_df = pd.DataFrame(escalation_data)
    return escalation_df

def generate_comprehensive_consequence_system():
    """
    Genera el sistema completo de consecuencias con todas las plantillas
    """
    print("\n🏗️  GENERANDO SISTEMA COMPLETO DE CONSECUENCIAS...")
    
    # Crear plantillas
    templates = create_disciplinary_templates()
    
    # Crear sistema de seguimiento
    tracking_system = create_tracking_system()
    
    # Crear matriz de escalamiento
    escalation_matrix = create_escalation_matrix()
    
    # Crear archivo Excel comprehensivo
    filename = f"Sistema_Consecuencias_Completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Hoja 1: Matriz de escalamiento
        escalation_matrix.to_excel(writer, sheet_name='Matriz_Escalamiento', index=False)
        
        # Hoja 2: Sistema de seguimiento
        tracking_system.to_excel(writer, sheet_name='Sistema_Seguimiento', index=False)
        
        # Hojas 3-6: Plantillas por nivel
        for nivel, template in templates.items():
            template_df = pd.DataFrame([template]).T
            template_df.columns = ['Campo']
            template_df.to_excel(writer, sheet_name=f'Plantilla_{nivel}')
        
        # Hoja 7: Registro de acciones (plantilla vacía)
        registro_columns = [
            'ID_Accion', 'Fecha_Accion', 'Ruta', 'Conductor', 'Nivel_Consecuencia',
            'Tipo_Accion', 'Responsable_Ejecucion', 'Estado', 'Evidencia_Documento',
            'Fecha_Seguimiento', 'Observaciones'
        ]
        registro_df = pd.DataFrame(columns=registro_columns)
        registro_df.to_excel(writer, sheet_name='Registro_Acciones', index=False)
        
        # Formateo
        workbook = writer.book
        
        # Formato de encabezado
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#366092',
            'font_color': 'white',
            'border': 1
        })
        
        # Formato de alerta
        alert_format = workbook.add_format({
            'bg_color': '#FF6666',
            'font_color': 'white',
            'bold': True,
            'border': 1
        })
        
        # Aplicar formatos a todas las hojas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:Z', 25)
    
    print(f"✅ Sistema completo generado: {filename}")
    return filename

def create_monthly_report_template():
    """
    Crea plantilla para reportes mensuales de cumplimiento
    """
    report_data = {
        'Seccion': [
            'RESUMEN EJECUTIVO',
            'ESTADÍSTICAS DEL MES',
            'RUTAS CON INCUMPLIMIENTOS',
            'ACCIONES DISCIPLINARIAS APLICADAS',
            'TENDENCIAS Y ANÁLISIS',
            'RECOMENDACIONES',
            'PLAN DE MEJORA'
        ],
        'Contenido': [
            'Porcentaje general de cumplimiento, rutas críticas, acciones tomadas',
            'Total rutas, feedbacks realizados, incumplimientos por nivel',
            'Listado detallado de rutas que no cumplieron y sus historiales',
            'Acciones ejecutadas por nivel, documentación generada',
            'Comparación con meses anteriores, identificación de patrones',
            'Propuestas de mejora, ajustes al proceso',
            'Acciones específicas para el próximo mes'
        ],
        'Responsable': [
            'Coordinador de Distribución',
            'Coordinador de Distribución',
            'Supervisor de Rutas',
            'Jefe de Distribución',
            'Coordinador de Distribución',
            'Jefe de Distribución',
            'Gerente CD Soyapango'
        ],
        'Frecuencia': [
            'Mensual',
            'Mensual',
            'Mensual',
            'Mensual',
            'Mensual',
            'Mensual',
            'Mensual'
        ]
    }
    
    report_df = pd.DataFrame(report_data)
    
    # Guardar plantilla de reporte
    report_filename = f"Plantilla_Reporte_Mensual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    report_df.to_excel(report_filename, index=False)
    
    print(f"✅ Plantilla de reporte mensual: {report_filename}")
    return report_filename

def main():
    """
    Función principal para generar todo el sistema de consecuencias
    """
    print("🎯 GENERANDO SISTEMA COMPLETO DE CONSECUENCIAS PARA FEEDBACKS")
    print("=" * 80)
    
    # Generar sistema completo
    system_file = generate_comprehensive_consequence_system()
    
    # Generar plantilla de reporte mensual
    report_template = create_monthly_report_template()
    
    print("\n" + "=" * 80)
    print("✅ SISTEMA DE CONSECUENCIAS GENERADO EXITOSAMENTE")
    print(f"📁 Archivos del sistema:")
    print(f"   • {system_file}")
    print(f"   • {report_template}")
    
    print("\n📋 COMPONENTES DEL SISTEMA:")
    print("   1. Matriz de escalamiento por niveles")
    print("   2. Plantillas de documentos disciplinarios")
    print("   3. Sistema de seguimiento y tracking")
    print("   4. Registro de acciones tomadas")
    print("   5. Plantilla de reportes mensuales")
    
    print("\n⚡ IMPLEMENTACIÓN RECOMENDADA:")
    print("   1. Capacitar al equipo en el uso del sistema")
    print("   2. Establecer responsables por nivel")
    print("   3. Configurar alertas automáticas")
    print("   4. Revisar mensualmente la efectividad")
    print("   5. Ajustar según resultados obtenidos")

if __name__ == "__main__":
    main()
