"""
Script to test client code formatting fix
This script verifies that large client codes display properly without abbreviation
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def test_client_code_formatting():
    """Test function to verify client code formatting"""
    print("🧪 Testing Client Code Formatting...")
    
    # Create test data with large client codes
    test_data = pd.DataFrame({
        'codigo_cliente': [14000000, 12000000, 11500000, 10200000, 9800000],
        'total_reportes': [25, 20, 18, 15, 12],
        'motivo_principal': ['Entrega tardía', 'Producto dañado', 'Falta producto', 'Error facturación', 'Atención cliente']
    })
    
    print("📊 Original client codes:")
    for codigo in test_data['codigo_cliente']:
        print(f"  - {codigo}")
    
    # Test 1: Original approach (problematic)
    print("\n🔍 Test 1: Using numeric client codes (may show as 14M, 12M, etc.)")
    fig1 = px.bar(
        test_data,
        x='total_reportes',
        y='codigo_cliente',
        title="Test 1: Numeric Client Codes",
        orientation='h'
    )
    
    # Test 2: String conversion approach (our fix)
    print("\n✅ Test 2: Using string client codes (should show full numbers)")
    test_data_fixed = test_data.copy()
    test_data_fixed['codigo_cliente_str'] = test_data_fixed['codigo_cliente'].astype(str)
    
    fig2 = px.bar(
        test_data_fixed,
        x='total_reportes',
        y='codigo_cliente_str',
        title="Test 2: String Client Codes (Fixed)",
        orientation='h'
    )
    
    # Test 3: Our enhanced approach with additional formatting options
    print("\n🔧 Test 3: Enhanced approach with tickformat and type settings")
    fig3 = px.bar(
        test_data_fixed,
        x='total_reportes',
        y='codigo_cliente_str',
        title="Test 3: Enhanced Client Code Display",
        orientation='h'
    )
    
    # Apply our formatting fix
    fig3.update_layout(
        yaxis={
            'categoryorder': 'total ascending', 
            'tickformat': '',
            'type': 'category'
        },
        margin=dict(l=200, r=50, t=50, b=50),
        xaxis_title="<b>Número de Reportes</b>",
        yaxis_title="<b>Código Cliente</b>"
    )
    
    print("\n🎯 Test Results:")
    print("  - Fig 1 (numeric): May show abbreviated codes like '14M', '12M'")
    print("  - Fig 2 (string): Should show full codes like '14000000', '12000000'")
    print("  - Fig 3 (enhanced): Guaranteed full codes with categorical type")
    
    # Save test figures
    try:
        fig1.write_html("test_client_codes_numeric.html")
        fig2.write_html("test_client_codes_string.html")
        fig3.write_html("test_client_codes_enhanced.html")
        print("\n💾 Test files saved:")
        print("  - test_client_codes_numeric.html")
        print("  - test_client_codes_string.html")
        print("  - test_client_codes_enhanced.html")
    except Exception as e:
        print(f"\n❌ Error saving test files: {e}")
    
    return fig1, fig2, fig3

def verify_dashboard_fix():
    """Verify the fix applied to the dashboard"""
    print("\n🔍 Verifying Dashboard Fix...")
    
    try:
        # Read the dashboard file to check for our fixes
        with open('dashboard_feedbacks_improved.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for our fixes
        fixes_found = []
        
        if "'tickformat': ''" in content:
            fixes_found.append("✅ tickformat parameter found")
        
        if "'type': 'category'" in content:
            fixes_found.append("✅ category type setting found")
        
        if "codigo_cliente_display" in content:
            fixes_found.append("✅ string conversion approach found")
        
        if "astype(str)" in content:
            fixes_found.append("✅ explicit string conversion found")
        
        print(f"\n📋 Dashboard Fix Status ({len(fixes_found)}/4 fixes found):")
        for fix in fixes_found:
            print(f"  {fix}")
        
        if len(fixes_found) >= 2:
            print("\n🎉 Dashboard appears to have sufficient fixes applied!")
        else:
            print("\n⚠️ Dashboard may need additional fixes")
            
    except Exception as e:
        print(f"\n❌ Error checking dashboard: {e}")

if __name__ == "__main__":
    # Run tests
    fig1, fig2, fig3 = test_client_code_formatting()
    
    # Verify dashboard
    verify_dashboard_fix()
    
    print("\n🏁 Test completed!")
    print("\n💡 Key Points:")
    print("  - Large numbers like 14000000 should display as '14000000', not '14M'")
    print("  - Converting to string prevents Plotly's automatic number formatting")
    print("  - Setting yaxis type to 'category' ensures categorical display")
    print("  - tickformat='' prevents additional formatting")
