# Proyecto ML 202510 Pregrado
## Análisis y Clustering de Cooperativas del Segmento 1 en Ecuador

### Descripción general

El objetivo de este proyecto es aplicar técnicas de machine learning tanto no supervisado (clustering) como semisupervisado para analizar y clasificar las cooperativas de ahorro y crédito del Segmento 1 en Ecuador según sus características financieras.

Cada cooperativa cuenta con una **calificación de riesgo (rating)** otorgada por agencias externas (A, B, C, etc.).

- En la **primera parte**, se aplicarán algoritmos de clustering para identificar grupos naturales de cooperativas con perfiles financieros similares, evaluando qué tan coherentes son estos clusters con respecto a los ratings reales.
- En la **segunda parte**, se entrenarán modelos de aprendizaje semisupervisado que aprovechen tanto datos etiquetados como no etiquetados para predecir los ratings, explorando cómo la información estructural del conjunto completo puede mejorar el desempeño en escenarios de etiquetado limitado.

Este proyecto integra conceptos de análisis exploratorio, selección y normalización de variables financieras, algoritmos de clustering, y métodos de aprendizaje semisupervisado, proporcionando una visión integral del análisis de datos financieros mediante machine learning.

---

### Objetivos específicos

1. Construir un dataset consolidado con los principales indicadores financieros de todas las cooperativas del Segmento 1, usando el corte más reciente disponible, mediante un pipeline automatizado de extracción desde PDFs.
2. Aplicar técnicas de preprocesamiento y normalización a los datos (manejo de valores faltantes, escalado, selección de variables) que servirán como base común para ambas partes del proyecto.
3. Implementar y evaluar modelos de clustering para identificar grupos naturales de cooperativas con comportamientos financieros similares, y comparar estos clusters con los ratings reales mediante métricas de evaluación no supervisadas.
4. Desarrollar modelos de aprendizaje semisupervisado (self-training y label propagation) que aprovechen datos sin etiqueta para mejorar la clasificación de ratings bajo diferentes escenarios de disponibilidad de datos etiquetados (5%, 10%, 20%, 40%).
5. Evaluar y comparar el desempeño de los modelos semisupervisados versus un baseline supervisado mediante métricas de clasificación (macro F1, balanced accuracy, AUC), analizando el impacto de los hiperparámetros y la fracción de datos etiquetados.
6. Analizar e interpretar los resultados desde una perspectiva financiera y técnica, identificando patrones en los clusters, errores de clasificación por clase de rating, e importancia de variables financieras en las predicciones.

---

## Metodología

### PARTE 1: CLUSTERING

1. **Obtención y limpieza de datos**

   - Recopilar indicadores financieros del último corte disponible de forma **automática**, a partir de una lista de enlaces a los archivos PDF de los indicadores financieros **o usando fuentes tabulares oficiales**.
   - Una fuente concreta es el portal de estadísticas de la SEPS:
     https://estadisticas.seps.gob.ec/index.php/estadisticas-sfps/
     donde se puede encontrar el **reporte financiero mensual de 2025**, que descarga un archivo `.zip` dentro del cual hay un Excel llamado:

     - `Boletin Financiero Segmento 1_oct_2025.xlsx` (nombre aproximado)
       - Hoja "Indicadores financieros"
       - Hoja "Ranking"

     Con estas hojas se pueden obtener directamente los indicadores y el ranking/rating necesarios para la actividad sin tener que extraerlos manualmente de PDFs.

   - Para **automatizar la obtención de estos datos** se puede:
     - Implementar **web scraping** sobre el portal de la SEPS (navegar al año/mes correspondiente, localizar el link al zip y descargarlo).
     - Usar un **agente** basado en SDK de OpenAI junto con **Playwright MCP**
       (https://github.com/microsoft/playwright-mcp)
       para que, de forma autónoma, navegue al sitio, descargue el `.zip`, lo descomprima y lea el Excel para construir la tabla consolidada de indicadores. De la misma página de SEPS está el PDF de la calificación de riesgo, que es otro insumo relevante.

   - Limpiar y unificar los datos (manejo de valores faltantes, escalado, etc.).

2. **Análisis exploratorio (EDA)**
   - Examinar la distribución de los indicadores.
   - Detectar correlaciones y redundancias.
   - Utilizar TSNE para facilitar visualización.

3. **Modelado**
   - Aplicar al menos tres algoritmos de **clustering**, de los cuales uno deberá ser K-Means como modelo base (**baseline**).
   - Justificar la elección del número de clusters.

4. **Evaluación y validación**
   - Evaluar la cohesión y separación de los clusters.
   - Comparar con las calificaciones de riesgo utilizando al menos **dos métricas** de evaluación investigadas por el grupo, justificadas y referenciadas en el informe final.

5. **Conclusiones**
   - Analizar similitudes y discrepancias entre clusters y ratings.
   - Proponer hipótesis sobre los patrones financieros observados.

---

### PARTE 2: APRENDIZAJE SEMISUPERVISADO

Usaremos el mismo conjunto de variables financieras. Los labels serán los ratings oficiales de cada cooperativa.

- **Objetivo:** entrenar modelos que aprovechen datos sin etiqueta para mejorar la clasificación de rating.
- **Supuestos:** el preprocesamiento y la selección de variables son exactamente los mismos que en la PARTE 1.

#### 2.1 Configuración y protocolo

- **División de datos:**
  - Conjunto total T con N instancias.
  - Fracción etiquetada p ∈ {5%, 10%, 20%, 40%, 60%, 80%}. El resto (1-p) se trata como no etiquetado.
  - Estratificar por rating en el subconjunto etiquetado.

- **Hiperparámetro principal:**
  - `ratio_labeled = p`. Reportar desempeño por cada p y su variabilidad.

- **Preprocesamiento:**
  - Reutilizar escalado, imputación y selección de variables definidos en la PARTE 1.
  - Semilla aleatoria fija para reproducibilidad.

- **Validación:**
  - 10 repeticiones por cada p con particiones aleatorias estratificadas de la porción etiquetada.

#### 2.2 Modelos a implementar

- **Baseline supervisado:**
  - Random Forest entrenado solo con el conjunto etiquetado.

- **Semisupervisados:**
  - **Self-training:** clasificador base = Random Forest. Pseudolabels con umbral de confianza τ ∈ {0.6, 0.7, 0.8, 0.9, otros}.
  - **Label Propagation/Label Spreading** sobre grafo k-NN:
    - k ∈ {5, 10, 20, otros}.
    - Métrica de distancia: euclidiana en el espacio escalado.

#### 2.3 Métricas de evaluación

- Macro F1 y Balanced Accuracy por clase y promedio macro.
- Matriz de confusión por p.
- Curva ROC y AUC.
- **Ganancia vs baseline:**
  - ΔMacro-F1 y ΔBalanced-Acc respecto al baseline supervisado para cada p.

#### 2.4 Análisis y reporte

- Curvas desempeño vs `ratio_labeled p` para cada método.
- Test estadístico con baseline como pivote.
- Efecto del umbral de confianza τ y de k en propagación de etiquetas.
- Discusión de errores frecuentes por clase de rating.
- **Interpretabilidad:**
  - Importancia de variables del clasificador base.
  - TSNE de los features que entran al clasificador, coloreado por label.

---

## Estructura del repositorio

```
data/
  raw/
  processed/
notebooks/
src/
  custom_agents/
  tools/
  main.py
README.md
requirements.txt
```

---

## Requisitos, instalación y ejecución

- Requisitos:
  - Python 3.13 (el Makefile es estricto y fallará si no está disponible).
  - Playwright (se instala con el Makefile).
  - Credenciales para LLM vía `OPENAI_API_KEY`.

1) Instalación automática (recomendada):

```bash
make install
```

Esto creará `venv`, instalará dependencias (`requirements.txt`) y los binarios de Playwright.

2) Activar el entorno:

```bash
source venv/bin/activate
```

3) Variables de entorno:

- Copiar o crear un archivo `.env` en la raíz con:

```
OPENAI_API_KEY=tu_api_key
```

4) Ejecutar el pipeline de agente (ingesta/ETL y consolidación):

```bash
python src/main.py
```

- El script `src/main.py` usa `OPENAI_API_KEY` y orquesta:
  - Un scraper (opcional) y un orquestador de consolidación.
  - Por defecto en el código actual `skip_scraper=True`; ajusta esa variable si deseas ejecutar el scraping automático del portal SEPS.
  - La salida esperada es una base de datos procesada en `data/processed/` (por ejemplo, `dataset.csv`).

---

## Datos de origen sugeridos (SEPS)

- Portal de estadísticas: https://estadisticas.seps.gob.ec/index.php/estadisticas-sfps/
- Reporte financiero mensual 2025 → descarga `.zip` → Excel con:
  - Hoja "Indicadores financieros"
  - Hoja "Ranking"
- El pipeline puede ampliar la ingesta incluyendo el PDF de calificación de riesgo.

---

## Notebook ejecutable y Colab

- Notebook parte 2: `notebooks/semisupervisado_rating_v2.ipynb`.
- Abrir en Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1via6trYSj1Gt8qJXlbEE5s5Tqlgg7Xjl?usp=sharing)

---

## Lineamientos de modelado (resumen operativo)

- Preprocesamiento único compartido entre PARTES 1 y 2: imputación, escalado y selección de variables.
- Clustering: al menos 3 métodos (incluye K-Means baseline). Justificar número de clusters.
- Semisupervisado: Self-training (RF, umbral τ) y Label Propagation/Spreading (k-NN, k en {5,10,20}).
- Validación: 10 repeticiones por p ∈ {5,10,20,40,60,80}.
- Métricas: Macro-F1, Balanced Accuracy, ROC/AUC; matrices de confusión; Δ vs baseline supervisado.
- Visualizaciones: TSNE para EDA e interpretabilidad; curvas de desempeño por p; importancia de variables.

---

## Reproducibilidad

- Fijar semillas aleatorias en todos los componentes utilizados.
- Documentar versiones de librerías en `requirements.txt`.
- Guardar artefactos de resultados y figuras bajo `figures/` (si aplica).

---

## Entregables

- **Repositorio en GitHub (privado)** con estructura indicada.
- **Notebook `.ipynb`** en `/notebooks` con botón "Open in Colab".
- **Pipeline de ingesta automática** en `/src` con scraping o agente (Playwright MCP opcional) y manejo de credenciales por variables de entorno.
- **Base de datos procesada** (`.csv` o `.xlsx`) en `/data/processed` generada por el pipeline.
- **Notebook ejecutable** como informe principal, con análisis, resultados y conclusiones.

---

## Licencia

Este proyecto puede incluir una licencia a elección en `LICENSE` (opcional).

