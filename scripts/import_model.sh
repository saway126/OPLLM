#!/bin/bash
# import_model.sh
# Imports a model into Ollama from an offline file (GGUF or Modelfile).

set -e

MODEL_NAME=$1
MODEL_FILE_PATH=$2

if [ -z "$MODEL_NAME" ] || [ -z "$MODEL_FILE_PATH" ]; then
    echo "Usage: ./import_model.sh <model_name> <path_to_Modelfile_or_GGUF>"
    echo "Example: ./import_model.sh my-llama3 ./llama3.gguf"
    exit 1
fi

echo "Importing model '$MODEL_NAME' from '$MODEL_FILE_PATH'..."

# Check if file exists
if [ ! -f "$MODEL_FILE_PATH" ]; then
    echo "Error: File $MODEL_FILE_PATH not found."
    exit 1
fi

# Determine if it's a GGUF file or a Modelfile
if [[ "$MODEL_FILE_PATH" == *.gguf ]]; then
    echo "Detected GGUF file. Creating temporary Modelfile..."
    echo "FROM $MODEL_FILE_PATH" > Modelfile.temp
    ollama create "$MODEL_NAME" -f Modelfile.temp
    rm Modelfile.temp
else
    # Assume it's a Modelfile
    ollama create "$MODEL_NAME" -f "$MODEL_FILE_PATH"
fi

echo "Model '$MODEL_NAME' imported successfully."
ollama list
