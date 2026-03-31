"""
set CMAKE_ARGS=-DLLAMA_CUBLAS=on

set FORCE_CMAKE=1

pip install -U 'webscout[local]'
pip install -U huggingface_hub
"""
from webscout.Local.utils import download_model
from webscout.Local.model import Model
from webscout.Local.thread import Thread
from webscout.Local import formats
# 1. Download the model
repo_id = "lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF"  # Replace with the desired Hugging Face repo
filename = "Mistral-7B-Instruct-v0.3-Q8_0.gguf" # Replace with the correct filename
model_path = download_model(repo_id, filename)

# 2. Load the model 
model = Model(model_path, n_gpu_layers=32)  

# 3. Create a Thread for conversation
thread = Thread(model, formats.mistral_instruct)

# 4. Start interacting with the model
thread.interact()
