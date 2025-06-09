#!/usr/bin/env python3
"""
Script para eliminar todos los bordes blancos y aplicar estilo consistente a las gráficas
"""

import re

def fix_chart_styles():
    file_path = "dashboard_feedbacks_improved.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar todos los marker_line_width=3 y cambiarlos a 0
    content = re.sub(r'marker_line_width=3', 'marker_line_width=0', content)
    
    # Eliminar todos los marker_line_width=4 y cambiarlos a 0 (para consistencia)
    content = re.sub(r'marker_line_width=4', 'marker_line_width=0', content)
    
    # También asegurar que todos los marker_line_color sean transparentes o no existan
    content = re.sub(r',\s*marker_line_color=[\'"][^\'\"]*[\'"]', '', content)
    
    # Hacer los textos más consistentes - todos en negrita
    content = re.sub(r'texttemplate=\'%\{text\}\'', 'texttemplate=\'<b>%{text}</b>\'', content)
    content = re.sub(r'texttemplate="%\{text\}"', 'texttemplate="<b>%{text}</b>"', content)
    
    # Hacer los textos de números más consistentes
    content = re.sub(r'textfont_size=12', 'textfont_size=14', content)
    content = re.sub(r'textfont_size=16', 'textfont_size=14', content)
    
    # Aplicar colores de texto más consistentes
    content = re.sub(r'textfont_color=[\'"]black[\'"]', 'textfont_color="white"', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Estilos de gráficas actualizados:")
    print("- ❌ Eliminados todos los bordes de barras")
    print("- 🎨 Colores de texto unificados a blanco")
    print("- 📝 Tamaños de fuente unificados a 14px")
    print("- ✨ Textos en negrita consistentes")

if __name__ == "__main__":
    fix_chart_styles()
