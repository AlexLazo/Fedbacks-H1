#!/usr/bin/env python3
"""
Script de prueba para verificar el dashboard mejorado
"""

import sys
import pandas as pd
import numpy as np

def test_basic_imports():
    """Prueba las importaciones básicas"""
    try:
        print("🔄 Probando importaciones...")
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Importaciones básicas exitosas")
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_data_loading():
    """Prueba si los archivos de datos existen"""
    try:
        print("🔄 Verificando archivos de datos...")
        import os
        
        feedbacks_exists = os.path.exists('Feedbacks H1.xlsx')
        rutas_exists = os.path.exists('BD_Rutas.xlsx')
        
        print(f"📊 Feedbacks H1.xlsx: {'✅ Existe' if feedbacks_exists else '❌ No encontrado'}")
        print(f"🚚 BD_Rutas.xlsx: {'✅ Existe' if rutas_exists else '❌ No encontrado'}")
        
        return feedbacks_exists and rutas_exists
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")
        return False

def test_dashboard_functions():
    """Prueba las funciones principales del dashboard"""
    try:
        print("🔄 Probando funciones del dashboard...")
        
        # Importar dashboard
        import dashboard_feedbacks_improved as dash
        
        # Verificar que las funciones principales existen
        functions_to_test = [
            'load_data',
            'create_advanced_kpi_metrics', 
            'show_general_overview',
            'show_temporal_analysis',
            'show_routes_analysis',
            'show_personnel_analysis',
            'show_performance_analysis',
            'show_advanced_analysis',
            'show_detailed_data',
            'clean_dataframe_for_display'
        ]
        
        for func_name in functions_to_test:
            if hasattr(dash, func_name):
                print(f"  ✅ {func_name}")
            else:
                print(f"  ❌ {func_name} - No encontrada")
                return False
        
        print("✅ Todas las funciones principales encontradas")
        return True
        
    except Exception as e:
        print(f"❌ Error probando funciones: {e}")
        return False

def test_pandas_categorical_fix():
    """Prueba la corrección de datos categóricos"""
    try:
        print("🔄 Probando corrección de datos categóricos...")
        
        # Crear datos de prueba con categorical
        df_test = pd.DataFrame({
            'col_categorical': pd.Categorical(['A', 'B', 'C', None]),
            'col_normal': [1, 2, 3, 4],
            'col_float': [1.1, 2.2, 3.3, np.nan]
        })
        
        # Importar función de limpieza
        from dashboard_feedbacks_improved import clean_dataframe_for_display
        
        # Probar limpieza
        df_clean = clean_dataframe_for_display(df_test)
        
        print("✅ Corrección de datos categóricos exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error en corrección categórica: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del Dashboard Feedbacks H1 Mejorado")
    print("=" * 60)
    
    tests = [
        ("Importaciones Básicas", test_basic_imports),
        ("Archivos de Datos", test_data_loading),
        ("Funciones del Dashboard", test_dashboard_functions),
        ("Corrección Categórica", test_pandas_categorical_fix)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El dashboard está listo.")
        print("💡 Para ejecutar el dashboard, usa: streamlit run dashboard_feedbacks_improved.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores anteriores.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
