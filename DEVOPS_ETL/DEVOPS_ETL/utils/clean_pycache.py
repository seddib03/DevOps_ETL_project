"""
Script pour nettoyer les fichiers __pycache__ et autres fichiers Python compilés (.pyc, .pyo).
"""
import os
import shutil
from pathlib import Path

def clean_pycache(root_dir):
    """
    Nettoie tous les dossiers __pycache__ et fichiers .pyc/.pyo dans le répertoire donné.
    
    Args:
        root_dir: Chemin racine du projet
    
    Returns:
        tuple: (nombre de dossiers supprimés, nombre de fichiers supprimés)
    """
    dirs_removed = 0
    files_removed = 0
    
    # Conversion en objet Path
    root = Path(root_dir)
    
    # Recherche de tous les dossiers __pycache__
    for pycache_dir in root.glob("**/__pycache__"):
        if pycache_dir.is_dir():
            print(f"Suppression du dossier: {pycache_dir}")
            try:
                shutil.rmtree(pycache_dir)
                dirs_removed += 1
            except Exception as e:
                print(f"Erreur lors de la suppression de {pycache_dir}: {e}")
    
    # Recherche de tous les fichiers .pyc et .pyo
    for py_cache_file in list(root.glob("**/*.pyc")) + list(root.glob("**/*.pyo")):
        if py_cache_file.is_file():
            print(f"Suppression du fichier: {py_cache_file}")
            try:
                os.remove(py_cache_file)
                files_removed += 1
            except Exception as e:
                print(f"Erreur lors de la suppression de {py_cache_file}: {e}")
    
    return dirs_removed, files_removed

def main():
    """Fonction principale."""
    # Chemin racine du projet
    project_root = Path(__file__).parent
    
    print("=== Nettoyage des fichiers de cache Python ===")
    print(f"Chemin racine: {project_root}")
    
    # Exécution du nettoyage
    dirs_removed, files_removed = clean_pycache(project_root)
    
    print("\n=== Résumé du nettoyage ===")
    print(f"Dossiers __pycache__ supprimés: {dirs_removed}")
    print(f"Fichiers .pyc/.pyo supprimés: {files_removed}")
    print(f"Total des éléments supprimés: {dirs_removed + files_removed}")

if __name__ == "__main__":
    main()
