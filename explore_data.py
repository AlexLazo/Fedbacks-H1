import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Función para cargar y explorar los datos
def load_and_explore_data():
    """Carga y explora los archivos Excel"""
    try:
        # Cargar Feedbacks H1
        print("Cargando archivo Feedbacks H1.xlsx...")
        feedbacks_df = pd.read_excel('Feedbacks H1.xlsx')
        print(f"Dimensiones de Feedbacks: {feedbacks_df.shape}")
        print(f"Columnas de Feedbacks: {list(feedbacks_df.columns)}")
        print("\nPrimeras 5 filas de Feedbacks:")
        print(feedbacks_df.head())
        print("\nInformación del DataFrame Feedbacks:")
        print(feedbacks_df.info())
        print("\nEstadísticas descriptivas de Feedbacks:")
        print(feedbacks_df.describe())
        
        # Cargar BD_Rutas
        print("\n" + "="*50)
        print("Cargando archivo BD_Rutas.xlsx...")
        rutas_df = pd.read_excel('BD_Rutas.xlsx')
        print(f"Dimensiones de BD_Rutas: {rutas_df.shape}")
        print(f"Columnas de BD_Rutas: {list(rutas_df.columns)}")
        print("\nPrimeras 5 filas de BD_Rutas:")
        print(rutas_df.head())
        print("\nInformación del DataFrame BD_Rutas:")
        print(rutas_df.info())
        
        return feedbacks_df, rutas_df
        
    except Exception as e:
        print(f"Error al cargar los archivos: {e}")
        return None, None

if __name__ == "__main__":
    feedbacks_df, rutas_df = load_and_explore_data()
