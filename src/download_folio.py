"""
Script para descargar el dataset FOLIO desde HuggingFace.

El dataset FOLIO es privado y requiere autenticación mediante token de HuggingFace.
El token debe estar configurado en el archivo .env como HF_TOKEN.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datasets import load_dataset

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener token de HuggingFace
HF_TOKEN = os.getenv('HF_TOKEN')

if not HF_TOKEN or HF_TOKEN == 'your_huggingface_token_here':
    raise ValueError(
        "HF_TOKEN no está configurado. Por favor, edita el archivo .env y "
        "configura tu token de HuggingFace. Obtén tu token en: "
        "https://huggingface.co/settings/tokens"
    )


def download_folio_dataset(save_path=None, split='train'):
    """
    Descarga el dataset FOLIO desde HuggingFace.
    
    Args:
        save_path: Ruta donde guardar el dataset localmente (opcional).
                  Si es None, se usa el cache de HuggingFace.
        split: Split del dataset a descargar ('train', 'validation', 'test').
    
    Returns:
        Dataset de HuggingFace
    """
    print(f"Descargando dataset FOLIO (split: {split})...")
    
    try:
        dataset = load_dataset(
            'yale-nlp/FOLIO',
            split=split,
            use_auth_token=HF_TOKEN
        )
        print(f"Dataset descargado exitosamente. Número de registros: {len(dataset)}")
        
        # Guardar localmente si se especifica una ruta
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir a formato JSON para fácil acceso
            data = [dict(record) for record in dataset]
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Dataset guardado en: {save_path}")
        
        return dataset
    
    except Exception as e:
        print(f"Error al descargar el dataset: {e}")
        raise


if __name__ == '__main__':
    # Descargar dataset de entrenamiento
    dataset = download_folio_dataset(save_path='data/folio_train.json', split='train')
    
    # Mostrar ejemplo del primer registro
    if len(dataset) > 0:
        print("\nEjemplo del primer registro:")
        print(f"Premisas: {dataset[0].get('premises', [])}")
        print(f"Conclusión: {dataset[0].get('conclusion', '')}")

