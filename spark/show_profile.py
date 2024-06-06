from IPython.display import display, HTML

def show_spark_ui():
    display(HTML('<a href="http://localhost:4040" target="_blank">Spark UI</a>'))

show_spark_ui()
