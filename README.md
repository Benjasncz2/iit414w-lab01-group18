# iit414w-lab01-group18
Aquí tienes el **README (Reproducibility Runbook)** estructurado para tu Lab 1, siguiendo el formato profesional solicitado y adaptado a los problemas y herramientas específicos que hemos trabajado (FastF1, Jolpica y el análisis de 2022-2024).

---

# Reproducibility Runbook - Lab 1

### (a) Header

* **Members:** Alonso Cárdenas, Benjamín Sánchez
* **Date:** 15 March 2026

### (b) System Info

* **Operating System:** Windows 10 / 11
* **Python Version:** 3.11.x
* **Conda/Pip Version:** Pip 24.0 / Conda 24.x

### (c) Setup Instructions

Para recrear el entorno exacto utilizado en este análisis, siga estos pasos:

1. **Clonar el repositorio y navegar al directorio:**
```bash
git clone [URL_DE_TU_REPOSITORIO]
cd [NOMBRE_DE_TU_CARPETA]

```


2. **Si utiliza Conda (Recomendado):** Cree el entorno desde el archivo `environment.yml` provisto:
```bash
conda env create -f environment.yml
conda activate iit414w_lab1

```


3. **Lanzar Jupyter Lab:**
```bash
jupyter lab

```



*(Alternativa usando venv estándar)*:

```bash
python -m venv f1_env
f1_env\Scripts\activate
pip install pandas seaborn matplotlib fastf1 requests scikit-learn

```

### (d) How to run

1. **Orden de ejecución:** Ejecute el notebook principal de arriba hacia abajo (`Kernel -> Restart & Run All Cells`).
2. **Configuración de Cache:** Asegúrese de que la celda que habilita `fastf1.Cache` tenga permisos de escritura en el directorio local.
3. **Dependencias:** No ignore las celdas iniciales de importación de librerías, ya que configuran los estilos de `seaborn` necesarios para visualizar correctamente los gráficos KDE y los histogramas de la Sección 3.3.

### (e) Problems encountered

Aquí se detallan dos problemas técnicos encontrados durante el EDA y su solución:

1. **Inconsistencia en tipos de datos al unir (Merge) fuentes:**
* **Problema:** Al intentar cruzar datos de la API de Jolpica con FastF1, el `DriverNumber` se cargaba como `float` en un set y como `object` (string) en otro, causando que el merge resultara en un DataFrame vacío.
* **Solución:** Utilicé `.astype(int)` en ambas columnas antes del merge para asegurar la integridad referencial.


2. **Sesgo por Abandonos (DNF) en el cálculo de IsTop10:**
* **Problema:** Inicialmente, los pilotos que no terminaron la carrera aparecían con valores nulos en la posición final, lo que hacía que no fueran contabilizados ni como éxito ni como fracaso.
* **Solución:** Implementé una lógica de limpieza donde cualquier `Status` distinto de 'Finished' o '+n Laps' (indicando DNF o DSQ) se mapea automáticamente a `IsTop10 = 0`, evitando el sesgo de supervivencia en los datos.



### (f) Expected outputs

Al ejecutar el notebook exitosamente, debería observar lo siguiente:

1. **Análisis de Balance (3.2):** Un gráfico de barras mostrando una distribución casi perfecta de 50% (680) para la clase `1` y 50% (679) para la clase `0`.
2. **Patrón Temporal (3.3):** Un gráfico de densidad (KDE) que compare 2022 vs 2024, mostrando que en 2024 la densidad de éxito se concentra más fuertemente en el Top 5 de la parrilla.
3. **Matriz de Correlación (3.4):** Un Heatmap donde `GridPosition` muestre una correlación negativa fuerte (aprox. $-0.82$) con `IsTop10`.
4. **Resumen 1-3-1 (3.8):** Una celda de Markdown final con la estructura "1 Most Important Finding, 3 Key Insights, 1 Recommendation".

---

**¿Hay algún otro detalle de tu configuración que te gustaría agregar o estamos listos para cerrar el Lab?**
