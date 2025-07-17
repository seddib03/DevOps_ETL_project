"""
Script de nettoyage du projet DevOps ETL.

Ce script supprime les fichiers temporaires, caches et anciens fichiers de test
pour maintenir un environnement de développement propre.
"""
import os
import shutil
from pathlib import Path
from typing import List

def clean_pycache(base_path: Path) -> int:
    """
    Supprime tous les dossiers __pycache__ récursivement.
    
    Args:
        base_path: Chemin de base pour la recherche
        
    Returns:
        Nombre de dossiers supprimés
    """
    count = 0
    for pycache_dir in base_path.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            count += 1
            print(f"✅ Supprimé: {pycache_dir}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de {pycache_dir}: {e}")
    
    return count

def clean_test_files(base_path: Path) -> int:
    """
    Supprime les fichiers de test temporaires.
    
    Args:
        base_path: Chemin de base pour la recherche
        
    Returns:
        Nombre de fichiers supprimés
    """
    count = 0
    
    # Fichiers de test à supprimer
    test_patterns = [
        "test_*.py",
        "*_test.py",
        "*_debug.py",
        "debug_*.py",
        "temp_*.py",
        "tmp_*.py"
    ]
    
    # Dossiers spécifiques à nettoyer
    scripts_dir = base_path / "scripts"
    
    for pattern in test_patterns:
        for file_path in scripts_dir.glob(pattern):
            # Garder les fichiers de test légitimes
            if file_path.name in ["test_secrets.py", "test_sonarqube_connection.py"]:
                continue
            
            try:
                file_path.unlink()
                count += 1
                print(f"✅ Supprimé: {file_path}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
    
    return count

def clean_output_files(base_path: Path) -> int:
    """
    Supprime les fichiers de sortie temporaires.
    
    Args:
        base_path: Chemin de base pour la recherche
        
    Returns:
        Nombre de fichiers supprimés
    """
    count = 0
    
    # Patterns de fichiers temporaires
    temp_patterns = [
        "*_output.txt",
        "*.tmp",
        "*.temp",
        "debug_*",
        "temp_*"
    ]
    
    for pattern in temp_patterns:
        for file_path in base_path.glob(pattern):
            try:
                file_path.unlink()
                count += 1
                print(f"✅ Supprimé: {file_path}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
    
    return count

def clean_old_exports(base_path: Path, keep_recent: int = 5) -> int:
    """
    Supprime les anciens fichiers d'export Excel.
    
    Args:
        base_path: Chemin de base pour la recherche
        keep_recent: Nombre de fichiers récents à conserver
        
    Returns:
        Nombre de fichiers supprimés
    """
    count = 0
    
    # Dossier des exports
    output_dir = base_path / "data" / "output"
    
    if not output_dir.exists():
        return count
    
    # Trouver tous les fichiers Excel
    excel_files = []
    for excel_file in output_dir.rglob("*.xlsx"):
        excel_files.append(excel_file)
    
    # Trier par date de modification (plus récent en premier)
    excel_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Supprimer les anciens fichiers
    for file_path in excel_files[keep_recent:]:
        try:
            file_path.unlink()
            count += 1
            print(f"✅ Supprimé: {file_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
    
    return count

def clean_logs(base_path: Path, keep_recent: int = 10) -> int:
    """
    Supprime les anciens fichiers de logs.
    
    Args:
        base_path: Chemin de base pour la recherche
        keep_recent: Nombre de fichiers récents à conserver
        
    Returns:
        Nombre de fichiers supprimés
    """
    count = 0
    
    logs_dir = base_path / "logs"
    
    if not logs_dir.exists():
        return count
    
    # Trouver tous les fichiers de logs
    log_files = []
    for log_file in logs_dir.glob("*.log*"):
        log_files.append(log_file)
    
    # Trier par date de modification
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Supprimer les anciens fichiers
    for file_path in log_files[keep_recent:]:
        try:
            file_path.unlink()
            count += 1
            print(f"✅ Supprimé: {file_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
    
    return count

def clean_empty_directories(base_path: Path) -> int:
    """
    Supprime les dossiers vides.
    
    Args:
        base_path: Chemin de base pour la recherche
        
    Returns:
        Nombre de dossiers supprimés
    """
    count = 0
    
    # Dossiers à ignorer
    ignore_dirs = {".git", ".venv", "node_modules", "__pycache__"}
    
    for dir_path in base_path.rglob("*"):
        if dir_path.is_dir() and dir_path.name not in ignore_dirs:
            try:
                # Vérifier si le dossier est vide
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    count += 1
                    print(f"✅ Dossier vide supprimé: {dir_path}")
            except Exception as e:
                # Le dossier n'est pas vide ou erreur
                pass
    
    return count

def main():
    """
    Fonction principale de nettoyage.
    """
    print("🧹 Nettoyage du projet DevOps ETL")
    print("=" * 50)
    
    # Chemin de base du projet
    base_path = Path(__file__).parent.parent
    
    total_cleaned = 0
    
    # Nettoyage des caches Python
    print("\\n📁 Nettoyage des caches Python...")
    cache_count = clean_pycache(base_path)
    total_cleaned += cache_count
    print(f"   {cache_count} dossiers __pycache__ supprimés")
    
    # Nettoyage des fichiers de test
    print("\\n🧪 Nettoyage des fichiers de test temporaires...")
    test_count = clean_test_files(base_path)
    total_cleaned += test_count
    print(f"   {test_count} fichiers de test supprimés")
    
    # Nettoyage des fichiers de sortie temporaires
    print("\\n📄 Nettoyage des fichiers temporaires...")
    output_count = clean_output_files(base_path)
    total_cleaned += output_count
    print(f"   {output_count} fichiers temporaires supprimés")
    
    # Nettoyage des anciens exports
    print("\\n📊 Nettoyage des anciens exports Excel...")
    export_count = clean_old_exports(base_path)
    total_cleaned += export_count
    print(f"   {export_count} anciens exports supprimés")
    
    # Nettoyage des logs
    print("\\n📋 Nettoyage des anciens logs...")
    log_count = clean_logs(base_path)
    total_cleaned += log_count
    print(f"   {log_count} anciens logs supprimés")
    
    # Nettoyage des dossiers vides
    print("\\n📁 Nettoyage des dossiers vides...")
    empty_count = clean_empty_directories(base_path)
    total_cleaned += empty_count
    print(f"   {empty_count} dossiers vides supprimés")
    
    print("\\n" + "=" * 50)
    print(f"🎉 Nettoyage terminé! {total_cleaned} éléments supprimés au total.")
    
    # Afficher l'espace libéré (approximatif)
    print("\\n💾 Espace de stockage libéré.")
    print("\\n✅ Projet nettoyé avec succès!")

if __name__ == "__main__":
    main()
