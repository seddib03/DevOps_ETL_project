"""
Script pour exécuter les tests unitaires et écrire les résultats dans un fichier.
"""
import sys
import os
import subprocess
from pathlib import Path

# Définir le répertoire racine du projet
ROOT_DIR = Path(__file__).parent
OUTPUT_FILE = ROOT_DIR / "test_results.txt"

# Commandes de test à exécuter
TEST_COMMANDS = [
    ["pytest", "tests/unit/extractors/gitlab", "-v"],
    ["pytest", "tests/unit/extractors/test_gitlab_users.py", "-v"],
    ["pytest", "tests/unit/test_gitlab_client.py", "-v"],
    ["pytest", "tests/unit/test_gitlab_connection.py", "-v"]
]

def run_tests():
    """Exécute les tests et écrit les résultats dans un fichier."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Résultats des tests unitaires\n\n")
        
        for cmd in TEST_COMMANDS:
            test_name = " ".join(cmd)
            f.write(f"\n## Test: {test_name}\n\n```\n")
            
            try:
                # Exécuter la commande et capturer la sortie
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                # Écrire la sortie dans le fichier
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nERREURS:\n")
                    f.write(result.stderr)
                
                # Afficher le statut sur la console
                if result.returncode == 0:
                    print(f"✅ {test_name} - Tests réussis")
                else:
                    print(f"❌ {test_name} - Échec des tests")
                    
            except Exception as e:
                f.write(f"Erreur lors de l'exécution des tests: {str(e)}\n")
                print(f"❌ {test_name} - Erreur: {str(e)}")
            
            f.write("```\n")
    
    print(f"\nTous les résultats des tests ont été écrits dans {OUTPUT_FILE}")

if __name__ == "__main__":
    run_tests()
