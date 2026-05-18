# Análise de Dados - E-commerce Performance Insights

Este projeto realiza uma Análise Exploratória de Dados (EDA) detalhada sobre o desempenho de um e-commerce, utilizando Python e bibliotecas de visualização para transformar dados brutos em inteligência de negócio.

## 📌 Objetivos do Projeto

O objetivo principal é identificar padrões de consumo, eficiência de marcas e sensibilidade de preço para orientar decisões estratégicas de estoque e marketing.

## 📊 Gráficos e Insights Gerados para um E-commerce

O projeto abrange 7 visualizações fundamentais:

1.  **Histograma:** Distribuição de avaliações dos produtos.
2.  **Gráfico de Dispersão:** Relação entre Preço e Nota (Percepção de Valor).
3.  **Mapa de Calor (Heatmap):** Correlação entre variáveis (Desconto, Vendas, Notas).
4.  **Gráfico de Barras Agrupadas:** Comparação entre Presença de Catálogo vs. Giro de Vendas por Marca.
5.  **Gráfico de Pizza:** Segmentação de produtos por Categoria/Gênero.
6.  **Gráfico de Densidade (KDE):** Concentração e faixas de preço dominantes.
7.  **Gráfico de Regressão:** Modelagem estatística do impacto do preço no volume de vendas.

## 🚀 Principais Insights Estratégicos

* **Prova Social como Motor de Vendas:** Identificamos que o número de avaliações tem uma correlação de **0.91** com o volume de vendas, sendo um driver mais forte que o próprio desconto.
* **Eficiência de Nicho (Zorba):** Marcas específicas dominam o giro de vendas com poucos anúncios, enquanto outras possuem catálogos inflados e baixo retorno.
* **Independência de Preço e Qualidade:** A satisfação do cliente (nota) mantém-se estável independentemente da faixa de preço, permitindo estratégias de precificação premium.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Bibliotecas:** Pandas, Matplotlib, Seaborn e Scipy (Stats).
* **Ambiente:** PyCharm / Jupyter Notebook (.ipynb).

## 📂 Como Executar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/seu-usuario/ecommerce-data-insights.git](https://github.com/seu-usuario/ecommerce-data-insights.git)```

2. Certifique-se de ter o arquivo ecommerce_estatistica.csv no mesmo diretório.

3. Execute o arquivo Graficos_Ecommerce_Estatistica.ipynb.