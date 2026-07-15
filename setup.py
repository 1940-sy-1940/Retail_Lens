from setuptools import setup, find_packages

setup(
    name="retail_analytics",
    version="1.0.0",
    description="全球零售运营数据分析与可视化决策看板",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "openpyxl>=3.0.0",
        "streamlit>=1.36.0",
        "plotly>=5.15.0",
    ],
)
