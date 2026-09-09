import pickle
from pathlib import Path


BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "model" / "knn_boost_model.pkl"


# Load the trained model
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


print("\nMODEL LOADED SUCCESSFULLY!\n")

print("Model type:")
print(type(model))

print("\nModel:")
print(model)