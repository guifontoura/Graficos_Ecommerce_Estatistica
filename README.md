# Análise de Dados - E-commerce Performance Insights

Este projeto realiza uma Análise Exploratória de Dados (EDA) detalhada sobre o desempenho de um e-commerce real, utilizando Python, bibliotecas de visualização para transformar dados brutos em inteligência de negócio e evoluindo de visualizações estáticas em Jupyter até um dashboard interativo construído em Dash/Plotly.

**Analista:** Guilherme Fontoura · EBAC — Analista de Dados · 2026

---

## 📌 Objetivos do Projeto

O objetivo principal é identificar padrões de consumo, eficiência de marcas e sensibilidade de preço para orientar decisões estratégicas de estoque e marketing.

---
## 🗂️ Estrutura do Projeto

```
├── Graficos_Ecommerce_Estatistica.ipynb   # Análise estática — 7 gráficos com Matplotlib/Seaborn
├── ecommerce_dashboard.py                 # Dashboard interativo — Dash com tema dark
├── ecommerce_estatistica.csv              # Dataset
├── requirements.txt                       # Dependências
└── README.md
```

---
## 📊 Gráficos e Insights Gerados para um E-commerce

O projeto abrange 7 visualizações fundamentais:

| # | Gráfico | Pergunta respondida |
|---|---------|---------------------|
| 1 | Histograma | As avaliações estão concentradas em qual faixa? |
| 2 | Dispersão | Produtos mais caros são melhor avaliados? |
| 3 | Mapa de calor | Quais variáveis se correlacionam? |
| 4 | Barras duplas | Quais marcas têm melhor giro de vendas? |
| 5 | Pizza | Para qual público o catálogo está direcionado? |
| 6 | Densidade | Em quais faixas de preço há mais produtos? |
| 7 | Regressão | Preço impacta o volume de vendas? |

---
## 🚀 Principais Insights Estratégicos

* **Prova Social como Motor de Vendas:** Identificamos que o número de avaliações tem uma correlação de **0.91** com o volume de vendas, sendo um driver mais forte que o próprio desconto.
* **Eficiência de Nicho (Zorba):** Marcas específicas dominam o giro de vendas com poucos anúncios, enquanto outras possuem catálogos inflados e baixo retorno.
* **Independência de Preço e Qualidade:** A satisfação do cliente (nota) mantém-se estável independentemente da faixa de preço, permitindo estratégias de precificação premium.
* **Oportunidade de Expansão:** Público infantil e unissex representam menos de 10% do catálogo — baixa concorrência interna.

---
## ▶️ Como Executar

**Instalar dependências:**
```bash
pip install -r requirements.txt
```

**Rodar o dashboard interativo:**
```bash
python ecommerce_dashboard.py
```
Acesse em: `http://127.0.0.1:8050`

**Abrir a análise estática:**
```
Graficos_Ecommerce_Estatistica.ipynb
```

> O arquivo `ecommerce_estatistica.csv` deve estar na mesma pasta do script.

---
## 🎛️ Filtros Interativos

O dashboard possui dois filtros que afetam em tempo real os gráficos 1, 2, 5, 6 e 7:

- **Gênero** — selecione um ou mais públicos para segmentar a análise
- **Faixa de Preço** — arraste o slider para focar em uma faixa específica (R$25 – R$327)

---
## 🛠️ Tecnologias

| Etapa | Ferramentas                                  |
|-------|----------------------------------------------|
| Análise estática | Python · Pandas · Matplotlib · Seaborn · Scipy |
| Dashboard interativo | Dash · Plotly · Statsmodels |
| Ambiente | Jupyter Notebook · PyCharm |
