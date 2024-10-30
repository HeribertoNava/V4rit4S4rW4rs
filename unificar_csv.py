import pandas as pd

def load_and_label_csv(filename, label):
    data = pd.read_csv(filename)
    data['label'] = label
    return data

# Cargar y etiquetar los datos
c_data = load_and_label_csv('datos_C.csv', 'C')
diagonal_data = load_and_label_csv('datos_diagonal.csv', 'diagonal')
ele_data = load_and_label_csv('datos_ele.csv', 'ele')
equis_data = load_and_label_csv('datos_equis.csv', 'equis')
infinito_data = load_and_label_csv('datos_infinito.csv', 'infinito')



# Unir todos los datasets
all_data = pd.concat([c_data, diagonal_data, ele_data, equis_data, infinito_data], ignore_index=True)

# Guardar el dataset unificado
all_data.to_csv('figuras.csv', index=False)
