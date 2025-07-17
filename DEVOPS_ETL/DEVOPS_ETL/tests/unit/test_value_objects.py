"""
Tests unitaires pour les objets de valeur (Value Objects) du domaine.

Ce module contient des tests spécifiques pour chaque classe de value object,
assurant que les fonctionnalités, validations et règles métier sont correctement implémentées.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from freezegun import freeze_time

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.domain.value_objects import (
    DateRange, CommitActivity, MetricValue, CodeCoverage,
    TechnicalDebt, ProjectIdentifier
)


class TestDateRange(unittest.TestCase):
    """Tests unitaires pour la classe DateRange."""
    
    def test_valid_date_range(self):
        """Test qu'une DateRange avec start < end est valide."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 15)
        date_range = DateRange(start, end)
        self.assertEqual(date_range.start_date, start)
        self.assertEqual(date_range.end_date, end)
    
    def test_invalid_date_range(self):
        """Test qu'une DateRange avec start > end lève une exception."""
        start = datetime(2025, 1, 15)
        end = datetime(2025, 1, 1)
        with self.assertRaises(ValueError):
            DateRange(start, end)
    
    def test_duration_property(self):
        """Test que la propriété duration retourne la bonne durée."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 15)
        date_range = DateRange(start, end)
        self.assertEqual(date_range.duration, timedelta(days=14))
    
    def test_contains_method(self):
        """Test que la méthode contains fonctionne correctement."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 15)
        date_range = DateRange(start, end)
        
        # Test avec date à l'intérieur
        self.assertTrue(date_range.contains(datetime(2025, 1, 7)))
        # Test avec date au début
        self.assertTrue(date_range.contains(start))
        # Test avec date à la fin
        self.assertTrue(date_range.contains(end))
        # Test avec date avant
        self.assertFalse(date_range.contains(datetime(2024, 12, 31)))
        # Test avec date après
        self.assertFalse(date_range.contains(datetime(2025, 1, 16)))
    
    @freeze_time("2025-07-15")
    def test_last_n_days(self):
        """Test que la méthode de classe last_n_days fonctionne correctement."""
        # Test avec date de fin par défaut (aujourd'hui)
        date_range = DateRange.last_n_days(7)
        expected_start = datetime(2025, 7, 8)
        expected_end = datetime(2025, 7, 15)
        
        # Comparaison de dates sans heures/minutes/secondes pour simplifier
        self.assertEqual(date_range.start_date.date(), expected_start.date())
        self.assertEqual(date_range.end_date.date(), expected_end.date())
        
        # Test avec date de fin spécifiée
        end_date = datetime(2025, 1, 15)
        date_range = DateRange.last_n_days(7, end_date)
        expected_start = datetime(2025, 1, 8)
        
        self.assertEqual(date_range.start_date.date(), expected_start.date())
        self.assertEqual(date_range.end_date.date(), end_date.date())


class TestCommitActivity(unittest.TestCase):
    """Tests unitaires pour la classe CommitActivity."""
    
    def setUp(self):
        """Initialise les données de test communes."""
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 1, 15)
        self.date_range = DateRange(self.start_date, self.end_date)
    
    def test_basic_properties(self):
        """Test des propriétés de base."""
        activity = CommitActivity(
            period=self.date_range,
            count=10,
            authors=frozenset(['dev1', 'dev2', 'dev3']),
            additions=100,
            deletions=50,
            file_count=20
        )
        
        self.assertEqual(activity.count, 10)
        self.assertEqual(activity.author_count, 3)
        self.assertEqual(activity.additions, 100)
        self.assertEqual(activity.deletions, 50)
        self.assertEqual(activity.file_count, 20)
    
    def test_derived_metrics(self):
        """Test des métriques dérivées."""
        activity = CommitActivity(
            period=self.date_range,
            count=10,
            authors=frozenset(['dev1', 'dev2']),
            additions=100,
            deletions=50,
            file_count=20
        )
        
        # Test net_changes (additions - deletions)
        self.assertEqual(activity.net_changes, 50)
        
        # Test total_changes (additions + deletions)
        self.assertEqual(activity.total_changes, 150)
        
        # Test average_changes_per_commit
        self.assertEqual(activity.average_changes_per_commit, 15.0)
        
        # Test average_changes_per_file
        self.assertEqual(activity.average_changes_per_file, 7.5)
    
    def test_edge_cases(self):
        """Test des cas limites (division par zéro, etc.)."""
        # Test avec count=0
        activity = CommitActivity(
            period=self.date_range,
            count=0,
            additions=100,
            deletions=50,
            file_count=20
        )
        self.assertEqual(activity.average_changes_per_commit, 0.0)
        
        # Test avec file_count=0
        activity = CommitActivity(
            period=self.date_range,
            count=10,
            additions=100,
            deletions=50,
            file_count=0
        )
        self.assertEqual(activity.average_changes_per_file, 0.0)
        
        # Test sans additions ni deletions
        activity = CommitActivity(
            period=self.date_range,
            count=10,
            file_count=20
        )
        self.assertEqual(activity.net_changes, 0)
        self.assertEqual(activity.total_changes, 0)


class TestMetricValue(unittest.TestCase):
    """Tests unitaires pour la classe MetricValue."""
    
    def test_basic_properties(self):
        """Test des propriétés de base."""
        metric = MetricValue(
            name="test_coverage",
            value=85.5,
            unit="%",
            timestamp=datetime(2025, 7, 15),
            source="sonarqube"
        )
        
        self.assertEqual(metric.name, "test_coverage")
        self.assertEqual(metric.value, 85.5)
        self.assertEqual(metric.unit, "%")
        self.assertEqual(metric.timestamp, datetime(2025, 7, 15))
        self.assertEqual(metric.source, "sonarqube")
    
    def test_string_representation(self):
        """Test de la représentation en chaîne."""
        # Avec unité
        metric = MetricValue(name="coverage", value=85.5, unit="%")
        self.assertEqual(str(metric), "85.5 %")
        
        # Sans unité
        metric = MetricValue(name="score", value=42)
        self.assertEqual(str(metric), "42")
    
    def test_validation(self):
        """Test de la validation des métriques."""
        # Pourcentage valide
        metric = MetricValue(name="coverage", value=85.5, unit="%")
        self.assertTrue(metric.is_valid())
        
        # Pourcentage invalide (> 100%)
        metric = MetricValue(name="coverage", value=120, unit="%")
        self.assertFalse(metric.is_valid())
        
        # Pourcentage invalide (négatif)
        metric = MetricValue(name="coverage", value=-5, unit="%")
        self.assertFalse(metric.is_valid())
        
        # Compteur valide
        metric = MetricValue(name="issues", value=42, unit="count")
        self.assertTrue(metric.is_valid())
        
        # Compteur invalide (négatif)
        metric = MetricValue(name="issues", value=-3, unit="count")
        self.assertFalse(metric.is_valid())
        
        # Ratio valide
        metric = MetricValue(name="ratio", value=0.75, unit="ratio")
        self.assertTrue(metric.is_valid())
        
        # Ratio invalide (négatif)
        metric = MetricValue(name="ratio", value=-0.5, unit="ratio")
        self.assertFalse(metric.is_valid())
        
        # Unité sans règle spécifique (toujours valide)
        metric = MetricValue(name="score", value=-10, unit="points")
        self.assertTrue(metric.is_valid())


class TestCodeCoverage(unittest.TestCase):
    """Tests unitaires pour la classe CodeCoverage."""
    
    def test_basic_properties(self):
        """Test des propriétés de base."""
        coverage = CodeCoverage(
            line_coverage=75.5,
            branch_coverage=65.2,
            covered_lines=1500,
            total_lines=2000,
            covered_branches=300,
            total_branches=450
        )
        
        self.assertEqual(coverage.line_coverage, 75.5)
        self.assertEqual(coverage.branch_coverage, 65.2)
        self.assertEqual(coverage.covered_lines, 1500)
        self.assertEqual(coverage.total_lines, 2000)
        self.assertEqual(coverage.covered_branches, 300)
        self.assertEqual(coverage.total_branches, 450)
        self.assertEqual(coverage.source, "sonarqube")  # valeur par défaut
    
    def test_value_clamping(self):
        """Test que les valeurs de couverture sont limitées entre 0 et 100."""
        # Test avec valeur > 100%
        coverage = CodeCoverage(
            line_coverage=120,
            branch_coverage=110,
            covered_lines=1500,
            total_lines=2000
        )
        
        self.assertEqual(coverage.line_coverage, 100)
        self.assertEqual(coverage.branch_coverage, 100)
        
        # Test avec valeur < 0%
        coverage = CodeCoverage(
            line_coverage=-10,
            branch_coverage=-20,
            covered_lines=1500,
            total_lines=2000
        )
        
        self.assertEqual(coverage.line_coverage, 0)
        self.assertEqual(coverage.branch_coverage, 0)
    
    def test_overall_coverage(self):
        """Test du calcul de la couverture globale."""
        # Avec branches
        coverage = CodeCoverage(
            line_coverage=80,
            branch_coverage=60,
            covered_lines=1600,
            total_lines=2000,
            covered_branches=300,
            total_branches=500
        )
        
        # 80% * 0.7 + 60% * 0.3 = 74%
        expected_overall = 0.7 * 80 + 0.3 * 60
        self.assertEqual(coverage.overall_coverage, expected_overall)
        
        # Sans branches (devrait être égal à line_coverage)
        coverage = CodeCoverage(
            line_coverage=80,
            branch_coverage=60,
            covered_lines=1600,
            total_lines=2000,
            covered_branches=0,
            total_branches=0
        )
        
        self.assertEqual(coverage.overall_coverage, 80)
    
    def test_coverage_rating(self):
        """Test de la notation de la couverture."""
        # Test note A (>= 80%)
        coverage = CodeCoverage(
            line_coverage=85,
            branch_coverage=85,
            covered_lines=1700,
            total_lines=2000
        )
        self.assertEqual(coverage.coverage_rating, "A")
        
        # Test note B (>= 70%)
        coverage = CodeCoverage(
            line_coverage=75,
            branch_coverage=75,
            covered_lines=1500,
            total_lines=2000
        )
        self.assertEqual(coverage.coverage_rating, "B")
        
        # Test note C (>= 50%)
        coverage = CodeCoverage(
            line_coverage=60,
            branch_coverage=60,
            covered_lines=1200,
            total_lines=2000
        )
        self.assertEqual(coverage.coverage_rating, "C")
        
        # Test note D (>= 30%)
        coverage = CodeCoverage(
            line_coverage=40,
            branch_coverage=40,
            covered_lines=800,
            total_lines=2000
        )
        self.assertEqual(coverage.coverage_rating, "D")
        
        # Test note E (< 30%)
        coverage = CodeCoverage(
            line_coverage=20,
            branch_coverage=20,
            covered_lines=400,
            total_lines=2000
        )
        self.assertEqual(coverage.coverage_rating, "E")


class TestTechnicalDebt(unittest.TestCase):
    """Tests unitaires pour la classe TechnicalDebt."""
    
    def test_basic_properties(self):
        """Test des propriétés de base."""
        debt = TechnicalDebt(
            effort_days=15.5,
            issues_count=120,
            blocker_issues=2,
            critical_issues=8,
            major_issues=25,
            minor_issues=65,
            info_issues=20,
            code_smells=95
        )
        
        self.assertEqual(debt.effort_days, 15.5)
        self.assertEqual(debt.issues_count, 120)
        self.assertEqual(debt.blocker_issues, 2)
        self.assertEqual(debt.critical_issues, 8)
        self.assertEqual(debt.major_issues, 25)
        self.assertEqual(debt.minor_issues, 65)
        self.assertEqual(debt.info_issues, 20)
        self.assertEqual(debt.code_smells, 95)
        self.assertEqual(debt.source, "sonarqube")  # valeur par défaut
    
    def test_weighted_issues(self):
        """Test du calcul des problèmes pondérés."""
        debt = TechnicalDebt(
            effort_days=15.5,
            issues_count=120,
            blocker_issues=2,   # 2 * 10 = 20
            critical_issues=8,  # 8 * 5 = 40
            major_issues=25,    # 25 * 3 = 75
            minor_issues=65,    # 65 * 1 = 65
            info_issues=20      # 20 * 0.1 = 2
        )
        
        # 20 + 40 + 75 + 65 + 2 = 202
        expected_weighted = 2 * 10 + 8 * 5 + 25 * 3 + 65 * 1 + 20 * 0.1
        self.assertEqual(debt.weighted_issues, expected_weighted)
    
    def test_technical_debt_ratio(self):
        """Test du calcul du ratio de dette technique."""
        debt = TechnicalDebt(
            effort_days=15.5,
            issues_count=120,
            blocker_issues=2,
            critical_issues=8,
            major_issues=25,
            minor_issues=65,
            info_issues=20
        )
        
        # weighted_issues / issues_count
        expected_ratio = debt.weighted_issues / 120
        self.assertEqual(debt.technical_debt_ratio, expected_ratio)
        
        # Test avec issues_count=0
        debt = TechnicalDebt(
            effort_days=0,
            issues_count=0
        )
        self.assertEqual(debt.technical_debt_ratio, 0.0)
    
    def test_debt_rating(self):
        """Test de la notation de la dette technique."""
        # Test note A (< 5 jours)
        debt = TechnicalDebt(effort_days=3, issues_count=50)
        self.assertEqual(debt.debt_rating, "A")
        
        # Test note B (< 10 jours)
        debt = TechnicalDebt(effort_days=8, issues_count=50)
        self.assertEqual(debt.debt_rating, "B")
        
        # Test note C (< 20 jours)
        debt = TechnicalDebt(effort_days=15, issues_count=50)
        self.assertEqual(debt.debt_rating, "C")
        
        # Test note D (< 40 jours)
        debt = TechnicalDebt(effort_days=30, issues_count=50)
        self.assertEqual(debt.debt_rating, "D")
        
        # Test note E (>= 40 jours)
        debt = TechnicalDebt(effort_days=50, issues_count=50)
        self.assertEqual(debt.debt_rating, "E")


class TestProjectIdentifier(unittest.TestCase):
    """Tests unitaires pour la classe ProjectIdentifier."""
    
    def test_basic_properties(self):
        """Test des propriétés de base."""
        project_id = ProjectIdentifier(
            name="test-project",
            gitlab_id="123",
            sonarqube_key="test-project:main",
            defect_dojo_id="456",
            dependency_track_id="789",
            jira_key="PROJ",
            organization="acme"
        )
        
        self.assertEqual(project_id.name, "test-project")
        self.assertEqual(project_id.gitlab_id, "123")
        self.assertEqual(project_id.sonarqube_key, "test-project:main")
        self.assertEqual(project_id.defect_dojo_id, "456")
        self.assertEqual(project_id.dependency_track_id, "789")
        self.assertEqual(project_id.jira_key, "PROJ")
        self.assertEqual(project_id.organization, "acme")
    
    def test_string_representation(self):
        """Test de la représentation en chaîne."""
        project_id = ProjectIdentifier(name="test-project")
        self.assertEqual(str(project_id), "test-project")
    
    def test_tracking_methods(self):
        """Test des méthodes de vérification du suivi."""
        # Projet avec suivi qualité et sécurité
        project_id = ProjectIdentifier(
            name="complete-project",
            sonarqube_key="complete-project:main",
            defect_dojo_id="456"
        )
        self.assertTrue(project_id.has_quality_tracking())
        self.assertTrue(project_id.has_security_tracking())
        
        # Projet avec suivi qualité uniquement
        project_id = ProjectIdentifier(
            name="quality-only",
            sonarqube_key="quality-only:main"
        )
        self.assertTrue(project_id.has_quality_tracking())
        self.assertFalse(project_id.has_security_tracking())
        
        # Projet avec suivi sécurité uniquement (DefectDojo)
        project_id = ProjectIdentifier(
            name="defect-dojo-only",
            defect_dojo_id="456"
        )
        self.assertFalse(project_id.has_quality_tracking())
        self.assertTrue(project_id.has_security_tracking())
        
        # Projet avec suivi sécurité uniquement (Dependency Track)
        project_id = ProjectIdentifier(
            name="dependency-track-only",
            dependency_track_id="789"
        )
        self.assertFalse(project_id.has_quality_tracking())
        self.assertTrue(project_id.has_security_tracking())
        
        # Projet sans suivi
        project_id = ProjectIdentifier(name="no-tracking")
        self.assertFalse(project_id.has_quality_tracking())
        self.assertFalse(project_id.has_security_tracking())
    
    def test_from_gitlab_project(self):
        """Test de la méthode de fabrique from_gitlab_project."""
        # Cas normal
        gitlab_data = {
            'id': 123,
            'path_with_namespace': 'acme/test-project',
            'namespace': {'name': 'acme'}
        }
        project_id = ProjectIdentifier.from_gitlab_project(gitlab_data)
        
        self.assertEqual(project_id.name, "test-project")
        self.assertEqual(project_id.gitlab_id, "123")
        self.assertEqual(project_id.organization, "acme")
        
        # Cas avec données partielles
        gitlab_data = {
            'id': 456,
            'path_with_namespace': 'test-project-2'
        }
        project_id = ProjectIdentifier.from_gitlab_project(gitlab_data)
        
        self.assertEqual(project_id.name, "test-project-2")
        self.assertEqual(project_id.gitlab_id, "456")
        self.assertIsNone(project_id.organization)
        
        # Cas avec données minimales
        gitlab_data = {'id': 789}
        project_id = ProjectIdentifier.from_gitlab_project(gitlab_data)
        
        self.assertEqual(project_id.name, "")  # Nom vide
        self.assertEqual(project_id.gitlab_id, "789")
        self.assertIsNone(project_id.organization)


if __name__ == '__main__':
    unittest.main()
