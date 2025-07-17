"""
Script pour créer un résumé des tests disponibles.
"""
import sys
import os
from pathlib import Path

# Définir le répertoire racine du projet
ROOT_DIR = Path(__file__).parent
TEST_DIR = ROOT_DIR / "tests"
OUTPUT_FILE = ROOT_DIR / "test_summary.txt"

def scan_tests():
    """Scan le répertoire de tests et liste les tests disponibles."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Résumé des tests disponibles\n\n")
        
        # Rechercher tous les fichiers de test Python
        test_files = list(TEST_DIR.glob("**/*test*.py"))
        
        # Écrire un résumé par catégorie
        categories = {}
        
        for test_file in test_files:
            # Calculer le chemin relatif
            rel_path = test_file.relative_to(ROOT_DIR)
            
            # Déterminer la catégorie (niveau supérieur dans tests/)
            if str(rel_path).startswith("tests/unit/"):
                category = "Unit Tests"
            elif str(rel_path).startswith("tests/integration/"):
                category = "Integration Tests"
            else:
                category = "Other Tests"
            
            # Ajouter à la catégorie
            if category not in categories:
                categories[category] = []
            categories[category].append(str(rel_path))
        
        # Écrire par catégorie
        for category, files in categories.items():
            f.write(f"## {category}\n\n")
            for file in sorted(files):
                f.write(f"- `{file}`\n")
            f.write("\n")
        
        # Ajouter des statistiques
        f.write(f"**Total des fichiers de test trouvés:** {len(test_files)}\n")
    
    print(f"Résumé des tests écrit dans {OUTPUT_FILE}")
    return len(test_files)

if __name__ == "__main__":
    num_tests = scan_tests()
    print(f"Trouvé {num_tests} fichiers de test au total.")
