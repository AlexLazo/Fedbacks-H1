import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class FeedbackAnalyzer:
    """
    Clase para análisis avanzado de feedbacks
    """
    
    def __init__(self, feedbacks_path="Feedbacks H1.xlsx", rutas_path="BD_Rutas.xlsx"):
        """
        Inicializa el analizador con los archivos de datos
        """
        self.load_data(feedbacks_path, rutas_path)
        self.prepare_data()
    
    def load_data(self, feedbacks_path, rutas_path):
        """Carga los datos de los archivos Excel"""
        try:
            print("Cargando datos...")
            self.feedbacks_df = pd.read_excel(feedbacks_path)
            self.rutas_df = pd.read_excel(rutas_path)
            print(f"✅ Datos cargados: {len(self.feedbacks_df)} feedbacks, {len(self.rutas_df)} rutas")
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
            raise
    
    def prepare_data(self):
        """Prepara y limpia los datos para análisis"""
        # Conversión de fechas
        self.feedbacks_df['fecha_registro'] = pd.to_datetime(self.feedbacks_df['fecha_registro'])
        self.feedbacks_df['fecha_cierre'] = pd.to_datetime(self.feedbacks_df['fecha_cierre'])
        
        # Crear columnas adicionales
        self.feedbacks_df['mes'] = self.feedbacks_df['fecha_registro'].dt.month
        self.feedbacks_df['mes_nombre'] = self.feedbacks_df['fecha_registro'].dt.month_name()
        self.feedbacks_df['semana'] = self.feedbacks_df['fecha_registro'].dt.isocalendar().week
        self.feedbacks_df['dia_semana'] = self.feedbacks_df['fecha_registro'].dt.day_name()
        self.feedbacks_df['trimestre'] = self.feedbacks_df['fecha_registro'].dt.quarter
        self.feedbacks_df['año'] = self.feedbacks_df['fecha_registro'].dt.year
        self.feedbacks_df['hora'] = self.feedbacks_df['fecha_registro'].dt.hour
        
        # Tiempo de resolución
        self.feedbacks_df['tiempo_resolucion'] = (
            self.feedbacks_df['fecha_cierre'] - self.feedbacks_df['fecha_registro']
        ).dt.days
        
        # Merge con rutas
        self.merged_df = self.feedbacks_df.merge(
            self.rutas_df, 
            left_on='ruta', 
            right_on='RUTA', 
            how='left'
        )
        
        print("✅ Datos preparados para análisis")
    
    def generate_executive_summary(self):
        """Genera un resumen ejecutivo completo"""
        print("\n" + "="*60)
        print("📊 RESUMEN EJECUTIVO - FEEDBACKS H1")
        print("="*60)
        
        # Métricas principales
        total_registros = len(self.feedbacks_df)
        total_rutas = self.feedbacks_df['ruta'].nunique()
        total_usuarios = self.feedbacks_df['usuario'].nunique()
        total_clientes = self.feedbacks_df['codigo_cliente'].nunique()
        promedio_puntos = self.feedbacks_df['puntos'].mean()
        
        print(f"📈 Total de Registros: {total_registros:,}")
        print(f"🚚 Rutas Únicas: {total_rutas}")
        print(f"👥 Usuarios Activos: {total_usuarios}")
        print(f"🏢 Clientes Únicos: {total_clientes}")
        print(f"⭐ Promedio de Puntos: {promedio_puntos:.2f}")
        
        # Análisis temporal
        fecha_inicio = self.feedbacks_df['fecha_registro'].min()
        fecha_fin = self.feedbacks_df['fecha_registro'].max()
        periodo_dias = (fecha_fin - fecha_inicio).days
        
        print(f"\n📅 PERÍODO DE ANÁLISIS:")
        print(f"   Desde: {fecha_inicio.strftime('%d/%m/%Y')}")
        print(f"   Hasta: {fecha_fin.strftime('%d/%m/%Y')}")
        print(f"   Total días: {periodo_dias}")
        
        # Tasa de cierre
        registros_cerrados = self.feedbacks_df['fecha_cierre'].notna().sum()
        tasa_cierre = (registros_cerrados / total_registros) * 100
        
        print(f"\n📋 GESTIÓN DE CIERRE:")
        print(f"   Registros cerrados: {registros_cerrados:,}")
        print(f"   Tasa de cierre: {tasa_cierre:.1f}%")
        
        if registros_cerrados > 0:
            tiempo_promedio = self.feedbacks_df['tiempo_resolucion'].mean()
            print(f"   Tiempo promedio de resolución: {tiempo_promedio:.1f} días")
        
        return {
            'total_registros': total_registros,
            'total_rutas': total_rutas,
            'total_usuarios': total_usuarios,
            'promedio_puntos': promedio_puntos,
            'tasa_cierre': tasa_cierre
        }
    
    def analyze_top_performers(self, top_n=10):
        """Analiza los mejores performers por diferentes categorías"""
        print(f"\n🏆 TOP {top_n} PERFORMERS")
        print("="*50)
        
        # Top rutas por volumen
        print(f"\n🚚 TOP {top_n} RUTAS POR VOLUMEN:")
        top_rutas = self.feedbacks_df['ruta'].value_counts().head(top_n)
        for i, (ruta, count) in enumerate(top_rutas.items(), 1):
            print(f"   {i:2d}. {ruta}: {count:,} registros")
        
        # Top usuarios más activos
        print(f"\n👤 TOP {top_n} USUARIOS MÁS ACTIVOS:")
        top_usuarios = self.feedbacks_df['usuario'].value_counts().head(top_n)
        for i, (usuario, count) in enumerate(top_usuarios.items(), 1):
            print(f"   {i:2d}. {usuario}: {count:,} registros")
        
        # Top vendedores
        print(f"\n💼 TOP {top_n} VENDEDORES:")
        top_vendedores = self.feedbacks_df['vendedor'].value_counts().head(top_n)
        for i, (vendedor, count) in enumerate(top_vendedores.items(), 1):
            print(f"   {i:2d}. {vendedor}: {count:,} registros")
        
        # Análisis con datos de supervisores si disponible
        if 'SUPERVISOR' in self.merged_df.columns:
            print(f"\n👨‍💼 TOP {top_n} SUPERVISORES:")
            top_supervisores = self.merged_df['SUPERVISOR'].value_counts().head(top_n)
            for i, (supervisor, count) in enumerate(top_supervisores.items(), 1):
                print(f"   {i:2d}. {supervisor}: {count:,} registros")
    
    def analyze_trends(self):
        """Analiza tendencias temporales"""
        print("\n📈 ANÁLISIS DE TENDENCIAS")
        print("="*50)
        
        # Tendencia mensual
        monthly_trend = self.feedbacks_df.groupby('mes_nombre').size()
        print("\n📊 REGISTROS POR MES:")
        for mes, count in monthly_trend.items():
            print(f"   {mes}: {count:,} registros")
        
        # Tendencia por día de la semana
        weekly_trend = self.feedbacks_df.groupby('dia_semana').size()
        print("\n📅 REGISTROS POR DÍA DE LA SEMANA:")
        dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for dia in dias_orden:
            if dia in weekly_trend.index:
                count = weekly_trend[dia]
                print(f"   {dia}: {count:,} registros")
        
        # Análisis por trimestre
        quarterly_analysis = self.feedbacks_df.groupby('trimestre').agg({
            'id_tema': 'count',
            'puntos': ['mean', 'sum'],
            'check_supervisor': 'mean'
        }).round(2)
        
        print("\n📊 ANÁLISIS TRIMESTRAL:")
        print(quarterly_analysis)
    
    def analyze_quality_metrics(self):
        """Analiza métricas de calidad"""
        print("\n⭐ ANÁLISIS DE CALIDAD")
        print("="*50)
        
        # Distribución de puntos
        puntos_dist = self.feedbacks_df['puntos'].value_counts().sort_index()
        print("\n📊 DISTRIBUCIÓN DE PUNTOS:")
        for puntos, count in puntos_dist.items():
            percentage = (count / len(self.feedbacks_df)) * 100
            print(f"   {puntos} puntos: {count:,} registros ({percentage:.1f}%)")
        
        # Análisis de motivos
        print("\n🎯 TOP 10 MOTIVOS DE RETROALIMENTACIÓN:")
        top_motivos = self.feedbacks_df['motivo_retro'].value_counts().head(10)
        for i, (motivo, count) in enumerate(top_motivos.items(), 1):
            percentage = (count / len(self.feedbacks_df)) * 100
            print(f"   {i:2d}. {motivo}: {count:,} ({percentage:.1f}%)")
        
        # Análisis de respuestas
        print("\n💬 TOP 10 TIPOS DE RESPUESTAS:")
        top_respuestas = self.feedbacks_df['respuesta_sub'].value_counts().head(10)
        for i, (respuesta, count) in enumerate(top_respuestas.items(), 1):
            percentage = (count / len(self.feedbacks_df)) * 100
            print(f"   {i:2d}. {respuesta}: {count:,} ({percentage:.1f}%)")
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        print("\n💡 RECOMENDACIONES ESTRATÉGICAS")
        print("="*50)
        
        # Análisis de eficiencia
        tasa_cierre = (self.feedbacks_df['fecha_cierre'].notna().sum() / len(self.feedbacks_df)) * 100
        
        if tasa_cierre < 80:
            print("🔴 CRÍTICO: Baja tasa de cierre ({:.1f}%)".format(tasa_cierre))
            print("   → Implementar seguimiento más estricto de casos abiertos")
            print("   → Establecer SLAs para resolución de casos")
        
        # Análisis de distribución de carga
        coef_variacion_rutas = (self.feedbacks_df['ruta'].value_counts().std() / 
                               self.feedbacks_df['ruta'].value_counts().mean())
        
        if coef_variacion_rutas > 1:
            print("🟡 ATENCIÓN: Alta variabilidad en carga de trabajo por rutas")
            print("   → Considerar redistribución de rutas")
            print("   → Analizar capacidad y recursos por ruta")
        
        # Análisis de calidad
        puntos_promedio = self.feedbacks_df['puntos'].mean()
        if puntos_promedio < 3:
            print("🔴 CRÍTICO: Baja calificación promedio ({:.1f})".format(puntos_promedio))
            print("   → Implementar programa de mejora de calidad")
            print("   → Capacitación adicional al personal")
        
        # Análisis temporal
        registros_por_dia = len(self.feedbacks_df) / ((self.feedbacks_df['fecha_registro'].max() - 
                                                     self.feedbacks_df['fecha_registro'].min()).days)
        
        print(f"\n📊 MÉTRICAS DE PRODUCTIVIDAD:")
        print(f"   Promedio diario de registros: {registros_por_dia:.1f}")
        print(f"   Registros por ruta promedio: {len(self.feedbacks_df) / self.feedbacks_df['ruta'].nunique():.1f}")
    
    def export_summary_report(self, filename=None):
        """Exporta un reporte completo"""
        if filename is None:
            filename = f"reporte_feedbacks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Redirigir print a archivo
        import sys
        original_stdout = sys.stdout
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                sys.stdout = f
                
                print("REPORTE COMPLETO DE ANÁLISIS - FEEDBACKS H1")
                print("=" * 80)
                print(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                print()
                
                self.generate_executive_summary()
                self.analyze_top_performers()
                self.analyze_trends()
                self.analyze_quality_metrics()
                self.generate_recommendations()
                
        finally:
            sys.stdout = original_stdout
        
        print(f"✅ Reporte exportado: {filename}")
        return filename

# Función principal para ejecutar análisis completo
def main():
    print("🚀 Iniciando análisis completo de Feedbacks H1...")
    
    try:
        # Crear analizador
        analyzer = FeedbackAnalyzer()
        
        # Ejecutar análisis completo
        analyzer.generate_executive_summary()
        analyzer.analyze_top_performers()
        analyzer.analyze_trends()
        analyzer.analyze_quality_metrics()
        analyzer.generate_recommendations()
        
        # Exportar reporte
        report_file = analyzer.export_summary_report()
        print(f"\n✅ Análisis completo finalizado. Reporte guardado en: {report_file}")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")

if __name__ == "__main__":
    main()
