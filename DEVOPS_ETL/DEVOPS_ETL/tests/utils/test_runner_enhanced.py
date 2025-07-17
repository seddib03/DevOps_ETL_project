"""
Utilitaire d'exécution des tests avec conventions améliorées.

Ce module fournit des utilitaires pour exécuter les tests
de manière structurée et avec des rapports détaillés.
"""
import pytest
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import subprocess
from datetime import datetime

# Ajouter le répertoire racine au path pour permettre les imports relatifs
project_root_directory = Path(__file__).parent.parent.parent
sys.path.append(str(project_root_directory))

from src.core.constants import (
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    TEST_CATEGORIES,
    TEST_REPORT_FORMATS
)

import logging
logger = logging.getLogger(__name__)


class TestRunnerEnhanced:
    """
    Exécuteur de tests amélioré avec conventions de nomenclature.
    
    Cette classe fournit des méthodes pour exécuter différents types
    de tests avec des rapports détaillés et une gestion d'erreurs robuste.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialise l'exécuteur de tests.
        
        Args:
            project_root: Chemin racine du projet
        """
        self._project_root = project_root
        self._tests_directory = project_root / "tests"
        self._logger = logging.getLogger(__name__)
        
        # Vérification de la structure des tests
        self._validate_test_structure()
    
    def run_gitlab_connection_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute les tests de connexion GitLab.
        
        Args:
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution des tests
        """
        test_file_path = self._tests_directory / "unit" / "test_gitlab_connection.py"
        
        return self._execute_test_file(
            test_file_path=test_file_path,
            test_category="GitLab Connection",
            verbose=verbose
        )
    
    def run_secrets_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute les tests du gestionnaire de secrets.
        
        Args:
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution des tests
        """
        test_file_path = self._tests_directory / "unit" / "test_secrets_enhanced.py"
        
        return self._execute_test_file(
            test_file_path=test_file_path,
            test_category="Secrets Manager",
            verbose=verbose
        )
    
    def run_sonarqube_connection_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute les tests de connexion SonarQube.
        
        Args:
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution des tests
        """
        test_file_path = self._tests_directory / "unit" / "test_sonarqube_connection_enhanced.py"
        
        return self._execute_test_file(
            test_file_path=test_file_path,
            test_category="SonarQube Connection",
            verbose=verbose
        )
    
    def run_all_unit_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute tous les tests unitaires.
        
        Args:
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution de tous les tests
        """
        unit_tests_directory = self._tests_directory / "unit"
        
        return self._execute_test_directory(
            test_directory=unit_tests_directory,
            test_category="All Unit Tests",
            verbose=verbose
        )
    
    def run_integration_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute les tests d'intégration.
        
        Args:
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution des tests d'intégration
        """
        integration_tests_directory = self._tests_directory / "integration"
        
        return self._execute_test_directory(
            test_directory=integration_tests_directory,
            test_category="Integration Tests",
            verbose=verbose
        )
    
    def generate_test_report(self, output_format: str = "console") -> Dict[str, Any]:
        """
        Génère un rapport de tests complet.
        
        Args:
            output_format: Format du rapport (console, html, json)
            
        Returns:
            Résultat de la génération du rapport
        """
        report_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if output_format == "html":
            report_file = self._project_root / f"test_report_{report_timestamp}.html"
            pytest_args = [
                "--html", str(report_file),
                "--self-contained-html",
                str(self._tests_directory)
            ]
        elif output_format == "json":
            report_file = self._project_root / f"test_report_{report_timestamp}.json"
            pytest_args = [
                "--json-report",
                "--json-report-file", str(report_file),
                str(self._tests_directory)
            ]
        else:
            pytest_args = ["-v", str(self._tests_directory)]
        
        try:
            exit_code = pytest.main(pytest_args)
            
            return {
                "report_successful": exit_code == 0,
                "report_format": output_format,
                "report_file": str(report_file) if output_format != "console" else None,
                "execution_timestamp": report_timestamp
            }
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {
                "report_successful": False,
                "error_message": str(e),
                "execution_timestamp": report_timestamp
            }
    
    def _execute_test_file(self, test_file_path: Path, test_category: str, 
                          verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute un fichier de test spécifique.
        
        Args:
            test_file_path: Chemin du fichier de test
            test_category: Catégorie du test
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution du test
        """
        if not test_file_path.exists():
            error_message = f"Fichier de test non trouvé: {test_file_path}"
            self._logger.error(error_message)
            return {
                "test_successful": False,
                "error_message": error_message,
                "test_category": test_category
            }
        
        if verbose:
            print(f"\\n=== Exécution des tests {test_category} ===\\n")
        
        try:
            pytest_args = ["-v"] if verbose else []
            pytest_args.append(str(test_file_path))
            
            exit_code = pytest.main(pytest_args)
            
            test_result = {
                "test_successful": exit_code == 0,
                "test_category": test_category,
                "test_file": str(test_file_path),
                "exit_code": exit_code
            }
            
            if verbose:
                if exit_code == 0:
                    print(f"\\n✅ Tests {test_category} réussis!")
                else:
                    print(f"\\n❌ Tests {test_category} échoués.")
            
            return test_result
            
        except Exception as e:
            error_message = f"Erreur lors de l'exécution des tests {test_category}: {e}"
            self._logger.error(error_message)
            return {
                "test_successful": False,
                "error_message": error_message,
                "test_category": test_category
            }
    
    def _execute_test_directory(self, test_directory: Path, test_category: str, 
                               verbose: bool = True) -> Dict[str, Any]:
        """
        Exécute tous les tests d'un répertoire.
        
        Args:
            test_directory: Répertoire des tests
            test_category: Catégorie des tests
            verbose: Si True, affiche des informations détaillées
            
        Returns:
            Résultat de l'exécution des tests
        """
        if not test_directory.exists():
            error_message = f"Répertoire de tests non trouvé: {test_directory}"
            self._logger.error(error_message)
            return {
                "test_successful": False,
                "error_message": error_message,
                "test_category": test_category
            }
        
        if verbose:
            print(f"\\n=== Exécution des tests {test_category} ===\\n")
        
        try:
            pytest_args = ["-v"] if verbose else []
            pytest_args.append(str(test_directory))
            
            exit_code = pytest.main(pytest_args)
            
            test_result = {
                "test_successful": exit_code == 0,
                "test_category": test_category,
                "test_directory": str(test_directory),
                "exit_code": exit_code
            }
            
            if verbose:
                if exit_code == 0:
                    print(f"\\n✅ Tests {test_category} réussis!")
                else:
                    print(f"\\n❌ Tests {test_category} échoués.")
            
            return test_result
            
        except Exception as e:
            error_message = f"Erreur lors de l'exécution des tests {test_category}: {e}"
            self._logger.error(error_message)
            return {
                "test_successful": False,
                "error_message": error_message,
                "test_category": test_category
            }
    
    def _validate_test_structure(self) -> None:
        """
        Valide la structure des répertoires de tests.
        
        Raises:
            FileNotFoundError: Si la structure des tests est incorrecte
        """
        if not self._tests_directory.exists():
            raise FileNotFoundError(f"Répertoire de tests non trouvé: {self._tests_directory}")
        
        expected_directories = ["unit", "integration", "fixtures"]
        for directory_name in expected_directories:
            directory_path = self._tests_directory / directory_name
            if not directory_path.exists():
                self._logger.warning(f"Répertoire de tests manquant: {directory_path}")


def main():
    """Fonction principale pour exécuter les tests."""
    parser = argparse.ArgumentParser(description="Exécuteur de tests amélioré")
    parser.add_argument("--category", choices=["gitlab", "secrets", "sonarqube", "unit", "integration", "all"], 
                       default="all", help="Catégorie de tests à exécuter")
    parser.add_argument("--verbose", action="store_true", help="Affichage détaillé")
    parser.add_argument("--report", choices=["console", "html", "json"], default="console", 
                       help="Format du rapport de tests")
    
    args = parser.parse_args()
    
    # Initialisation de l'exécuteur de tests
    test_runner = TestRunnerEnhanced(project_root_directory)
    
    # Exécution des tests selon la catégorie
    if args.category == "gitlab":
        result = test_runner.run_gitlab_connection_tests(args.verbose)
    elif args.category == "secrets":
        result = test_runner.run_secrets_tests(args.verbose)
    elif args.category == "sonarqube":
        result = test_runner.run_sonarqube_connection_tests(args.verbose)
    elif args.category == "unit":
        result = test_runner.run_all_unit_tests(args.verbose)
    elif args.category == "integration":
        result = test_runner.run_integration_tests(args.verbose)
    elif args.category == "all":
        if args.report != "console":
            result = test_runner.generate_test_report(args.report)
        else:
            result = test_runner.run_all_unit_tests(args.verbose)
    
    # Affichage du résultat
    if result.get("test_successful", False) or result.get("report_successful", False):
        print("\\n🎉 Exécution terminée avec succès!")
        sys.exit(0)
    else:
        print("\\n❌ Exécution échouée.")
        sys.exit(1)


if __name__ == "__main__":
    main()
