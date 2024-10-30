import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import joblib

# Cargar y limpiar el archivo CSV
def load_and_clean_csv(filename):
    data = pd.read_csv(filename)
    numeric_columns = data.columns[:-1]  
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
    data = data.dropna()
    return data

data = load_and_clean_csv('figuras.csv')

# Normalizar los datos
scaler = StandardScaler()
data_scaled = pd.DataFrame(scaler.fit_transform(data.iloc[:, :-1]), columns=data.columns[:-1])
data_scaled['label'] = data['label']

# Guardar el scaler
joblib.dump(scaler, 'scaler_figuras.pkl')

# Segmentación y extracción de características
def segment_data(data, segment_size=60):  # Cambié el tamaño de segmento a 60 como mencionaste
    segments = []
    labels = []
    for i in range(0, len(data) - segment_size, segment_size):
        segment = data.iloc[i:i+segment_size, :-1].values
        segments.append(segment)
        labels.append(data['label'].iloc[i])
    return np.array(segments), np.array(labels)

segments, labels = segment_data(data_scaled)

def extract_features(segments):
    features = []
    for segment in segments:
        means = np.mean(segment, axis=0) 
        stds = np.std(segment, axis=0)
        maxs = np.max(segment, axis=0)
        mins = np.min(segment, axis=0)
        feature_vector = np.concatenate([means, stds, maxs, mins])
        features.append(feature_vector)
    return np.array(features)

X = extract_features(segments)
y = labels

# Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar el modelo
model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
model.fit(X_train, y_train)

# Guardar el modelo
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)
print(f"Train accuracy: {train_accuracy}")
print(f"Test accuracy: {test_accuracy}")

# Guardar el modelo y el scaler
joblib.dump(model, 'modelo_figuras_mlp.pkl')
joblib.dump(scaler, 'scaler_figuras_mlp.pkl')
