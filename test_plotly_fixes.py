#!/usr/bin/env python3
"""
Test script to verify plotly configuration fixes
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def test_scatter_with_colorbar():
    """Test the scatter plot with colorbar configuration that was causing issues"""
    print("🧪 Testing scatter plot with colorbar configuration...")
    
    # Create sample data similar to the dashboard
    sample_data = {
        'total_registros': [10, 20, 30, 40, 50],
        'puntos_promedio': [5.5, 6.0, 7.2, 8.1, 9.0],
        'tasa_cierre': [60, 70, 80, 85, 90],
        'ruta': ['R001', 'R002', 'R003', 'R004', 'R005']
    }
    
    df = pd.DataFrame(sample_data)
    
    try:
        # Test the exact configuration from the dashboard
        fig_eficiencia = px.scatter(
            df,
            x='total_registros',
            y='puntos_promedio',
            size='tasa_cierre',
            hover_data=['ruta', 'total_registros', 'puntos_promedio', 'tasa_cierre'],
            title="📊 Test: Eficiencia Integral por Ruta",
            color='tasa_cierre',
            color_continuous_scale='RdYlGn',
            height=400,
            labels={
                'total_registros': 'Total de Registros de Feedback',
                'puntos_promedio': 'Calidad Promedio (Puntos 1-10)',
                'tasa_cierre': 'Tasa de Cierre (%)',
                'ruta': 'Ruta'
            }
        )
        
        fig_eficiencia.update_traces(
            marker=dict(
                sizemode='diameter',
                sizemin=8,
                size=20,
                line_width=0
            )
        )    
        
        fig_eficiencia.update_layout(
            margin=dict(l=20, r=20, t=80, b=20),
            xaxis_title="<b>Total de Registros de Feedback</b>",
            yaxis_title="<b>Calidad Promedio (Puntos 1-10)</b>",        
            coloraxis_colorbar=dict(
                title="Tasa de Cierre (%)"
            )
        )
        print("✅ Scatter plot with colorbar created successfully!")
        print(f"   - Figure type: {type(fig_eficiencia)}")
        print(f"   - Has coloraxis: {'coloraxis' in fig_eficiencia.layout}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating scatter plot: {e}")
        return False

def test_bar_chart_with_continuous_color():
    """Test bar charts with continuous color scale"""
    print("\n🧪 Testing bar chart with continuous color scale...")
    
    sample_data = {
        'ruta': ['DS0033', 'DS0045', 'DS0040', 'DS0050'],
        'registros': [15, 25, 18, 22],
        'supervisor': ['FLAVIO', 'FLAVIO', 'CARLOS', 'CARLOS']
    }
    
    df = pd.DataFrame(sample_data)
    
    try:
        fig_bar = px.bar(
            df,
            x='registros',
            y='ruta',
            orientation='h',
            title="🏆 Test: Top Rutas por Registros",
            color='registros',
            color_continuous_scale='Plasma',
            height=400,
            text='registros'
        )
        
        fig_bar.update_traces(
            texttemplate='<b>%{text}</b>',
            textposition='outside',
            marker_line_width=0
        )
        
        print("✅ Bar chart with continuous color created successfully!")
        print(f"   - Figure type: {type(fig_bar)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating bar chart: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Plotly Configuration Fixes")
    print("=" * 50)
    
    test1_passed = test_scatter_with_colorbar()
    test2_passed = test_bar_chart_with_continuous_color()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"   Scatter plot test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Bar chart test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The plotly fixes are working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    main()
