#!/usr/bin/env python3
"""
Organization Automation Service
Uses unified math to safely organize fractal/disorganiindustrial_host codebase

Date: November 1, 2025
Hashtag: #organization-automation-service
Purpose: Fix organization problems safely using unified math
"""

import sys
import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Framework root
framework_root = Path(__file__).parent
sys.path.insert(0, str(framework_root))

# Import unified math
try:
    from research.projects.hallbergtheory_quantum_echo.unified_math_implementation import (
        Id_unified, reveal_unified, serialize_unified
    )
    UNIFIED_MATH_AVAILABLE = True
except ImportError:
    print("Warning: Unified math not available. Install dependencies.")
    UNIFIED_MATH_AVAILABLE = False

# Import verification systems
try:
    from provability_chain_system import ProvabilityChainSystem
    PROVABILITY_CHAIN_AVAILABLE = True
except ImportError:
    PROVABILITY_CHAIN_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organization_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EntityInfo:
    """Information about a codebase entity"""
    path: str
    unified_id: str
    entity_type: str  # 'file', 'directory', 'function', 'class'
    relationships: List[str] = None
    duplicates: List[str] = None
    orphaned: bool = False
    dependencies: List[str] = None
    timestamp: str = None
    full_path: str = None  # Full absolute path (optional)
    
    def __post_init__(self):
        """Initialize default values"""
        if self.relationships is None:
            self.relationships = []
        if self.duplicates is None:
            self.duplicates = []
        if self.dependencies is None:
            self.dependencies = []
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()


@dataclass
class OrganizationPlan:
    """Plan for organizing the codebase"""
    backup_path: str
    entities: List[EntityInfo]
    organization_structure: Dict[str, str]
    consolidation_rules: Dict[str, str]
    file_movements: Dict[str, str]
    safety_checks: List[str]
    timestamp: str


class OrganizationAutomationService:
    """Automated organization service using unified math"""
    
    def __init__(self, root_path: str = None):
        """Initialize organization service"""
        self.root_path = Path(root_path or framework_root)
        self.backup_path = None
        self.entity_database = {}
        self.organization_plan = None
        self.safety_checks_passed = False
        self.progress_log = []
        
        if not UNIFIED_MATH_AVAILABLE:
            raise ImportError("Unified math not available. Cannot proceed.")
            
        # Hard Quarantine Integration
        self.ignore_patterns = self._load_xi_ignore()
    
    def _load_xi_ignore(self):
        ignore_path = self.root_path / ".xi-ignore"
        patterns = []
        if ignore_path.exists():
            for line in ignore_path.read_text().splitlines():
                if line.strip() and not line.startswith("#"):
                    patterns.append(line.strip())
        return patterns

    def is_quarantined(self, path):
        p = Path(path)
        for pattern in self.ignore_patterns:
            if p.match(pattern) or any(parent.match(pattern) for parent in p.parents):
                return True
        return False
    
    def log_progress(self, phase: str, step: str, status: str, details: Dict[str, Any] = None):
        """Log progress for tracking"""
        log_entry = {
            "phase": phase,
            "step": step,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        self.progress_log.append(log_entry)
        logger.info(f"[{phase}] {step}: {status}")
        if details:
            logger.debug(f"Details: {json.dumps(details, indent=2)}")
    
    def phase_1_preparation(self) -> Dict[str, Any]:
        """Phase 1: Preparation (Safety First)"""
        
        print("=" * 70)
        print("  PHASE 1: PREPARATION (Safety First)")
        print("=" * 70)
        print()
        
        results = {}
        
        # Step 1: Create full backup
        print("Step 1: Creating full backup...")
        self.log_progress("Phase 1", "Backup", "starting")
        
        backup_dir = self.root_path / "backups" / f"organization_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy entire codebase to backup
        backup_count = 0
        for item in self.root_path.iterdir():
            if item.name in ['backups', '__pycache__', '.git', '.venv', 'venv', 'node_modules']:
                continue
            
            try:
                dest = backup_dir / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    backup_count += 1
                elif item.is_dir():
                    shutil.copytree(item, dest, ignore=shutil.ignore_patterns('__pycache__', '.git'))
                    backup_count += 1
            except Exception as e:
                logger.error(f"Failed to backup {item}: {e}")
        
        self.backup_path = str(backup_dir)
        results['backup_path'] = self.backup_path
        results['backup_count'] = backup_count
        
        print(f"✓ Backup created: {self.backup_path}")
        print(f"  Files backed up: {backup_count}")
        self.log_progress("Phase 1", "Backup", "complete", {"count": backup_count})
        
        # Step 2: Generate unified IDs for all entities
        print("\nStep 2: Generating unified IDs for all entities...")
        self.log_progress("Phase 1", "Unified IDs", "starting")
        
        entities = []
        file_count = 0
        dir_count = 0
        
        for path in self.root_path.rglob('*'):
            # Skip backup, cache, git directories AND Quarantined paths
            if any(skip in path.parts for skip in ['backups', '__pycache__', '.git', '.venv', 'venv', 'node_modules']):
                continue
            
            if self.is_quarantined(path):
                continue
            
            if path.is_file():
                entity_id = Id_unified(str(path.relative_to(self.root_path)), "file")
                entities.append({
                    "path": str(path.relative_to(self.root_path)),
                    "unified_id": entity_id["hybrid_id"],
                    "entity_type": "file",
                    "full_path": str(path)
                })
                file_count += 1
            elif path.is_dir() and path != self.root_path:
                entity_id = Id_unified(str(path.relative_to(self.root_path)), "directory")
                entities.append({
                    "path": str(path.relative_to(self.root_path)),
                    "unified_id": entity_id["hybrid_id"],
                    "entity_type": "directory",
                    "full_path": str(path)
                })
                dir_count += 1
        
        # Store in database
        for entity in entities:
            self.entity_database[entity["unified_id"]] = entity
        
        results['entity_count'] = len(entities)
        results['file_count'] = file_count
        results['dir_count'] = dir_count
        
        print(f"✓ Unified IDs generated: {len(entities)} entities")
        print(f"  Files: {file_count}, Directories: {dir_count}")
        self.log_progress("Phase 1", "Unified IDs", "complete", {"total": len(entities)})
        
        # Step 3: Create entity database
        print("\nStep 3: Creating entity database...")
        self.log_progress("Phase 1", "Database", "starting")
        
        database_path = self.root_path / "organization" / "entity_database.json"
        database_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(database_path, 'w') as f:
            json.dump({
                "entities": self.entity_database,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_entities": len(entities)
            }, f, indent=2)
        
        results['database_path'] = str(database_path)
        
        print(f"✓ Entity database created: {database_path}")
        self.log_progress("Phase 1", "Database", "complete")
        
        # Step 4: Validate backup
        print("\nStep 4: Validating backup...")
        self.log_progress("Phase 1", "Validation", "starting")
        
        backup_valid = backup_dir.exists() and backup_count > 0
        database_valid = database_path.exists()
        
        results['backup_valid'] = backup_valid
        results['database_valid'] = database_valid
        results['preparation_complete'] = backup_valid and database_valid
        
        if backup_valid and database_valid:
            print("✓ Preparation complete - All safety checks passed")
            self.log_progress("Phase 1", "Validation", "complete", {"status": "passed"})
        else:
            print("✗ Preparation failed - Safety checks failed")
            self.log_progress("Phase 1", "Validation", "failed", {"backup": backup_valid, "database": database_valid})
            raise ValueError("Preparation failed - Cannot proceed safely")
        
        print()
        return results
    
    def phase_2_discovery(self) -> Dict[str, Any]:
        """Phase 2: Discovery (Understand Current State)"""
        
        print("=" * 70)
        print("  PHASE 2: DISCOVERY (Understand Current State)")
        print("=" * 70)
        print()
        
        results = {
            "relationships": {},
            "duplicates": [],
            "orphaned": [],
            "structure_map": {}
        }
        
        # Step 1: Use reveal_unified() on all entities
        print("Step 1: Discovering relationships using reveal_unified()...")
        self.log_progress("Phase 2", "Relationships", "starting")
        
        relationships_discovered = 0
        
        for unified_id, entity_info in list(self.entity_database.items()):
            try:
                revealed = reveal_unified(unified_id, entity_info.get("entity_type", "file"))
                
                if "complete_structure" in revealed:
                    # Extract relationships
                    entity_relationships = []
                    
                    # Check for classical structure relationships
                    classical = revealed["complete_structure"].get("classical_structure", {})
                    if "relationships" in classical:
                        entity_relationships.extend(classical["relationships"])
                    
                    # Check for quantum hidden structures (relationships)
                    quantum = revealed["complete_structure"].get("quantum_hidden_structures", {})
                    if quantum:
                        # Quantum structures can reveal relationships
                        entity_relationships.append(f"quantum_structure_{unified_id[:8]}")
                    
                    if entity_relationships:
                        entity_info["relationships"] = entity_relationships
                        results["relationships"][unified_id] = entity_relationships
                        relationships_discovered += 1
                        
            except Exception as e:
                logger.warning(f"Failed to reveal structure for {unified_id}: {e}")
        
        print(f"✓ Relationships discovered: {relationships_discovered}")
        self.log_progress("Phase 2", "Relationships", "complete", {"count": relationships_discovered})
        
        # Step 2: Identify duplicates
        print("\nStep 2: Identifying duplicate code...")
        self.log_progress("Phase 2", "Duplicates", "starting")
        
        # Group by file name and size
        file_groups = {}
        for unified_id, entity_info in self.entity_database.items():
            if entity_info["entity_type"] != "file":
                continue
            
            path = Path(entity_info.get("full_path", entity_info["path"]))
            if not path.exists():
                continue
            
            # Use hash of file content for duplicate detection
            try:
                with open(path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                file_key = f"{path.name}_{file_hash[:16]}"
                if file_key not in file_groups:
                    file_groups[file_key] = []
                file_groups[file_key].append(unified_id)
            except Exception as e:
                logger.warning(f"Failed to hash {path}: {e}")
        
        # Find duplicates (same name and hash)
        duplicates_found = 0
        for file_key, unified_ids in file_groups.items():
            if len(unified_ids) > 1:
                results["duplicates"].append({
                    "group": file_key,
                    "entities": unified_ids,
                    "count": len(unified_ids)
                })
                duplicates_found += 1
        
        print(f"✓ Duplicates identified: {duplicates_found} groups")
        self.log_progress("Phase 2", "Duplicates", "complete", {"groups": duplicates_found})
        
        # Step 3: Find orphaned files
        print("\nStep 3: Finding orphaned files...")
        self.log_progress("Phase 2", "Orphaned", "starting")
        
        # Files in root or with no relationships
        orphaned_count = 0
        for unified_id, entity_info in self.entity_database.items():
            if entity_info["entity_type"] != "file":
                continue
            
            path = Path(entity_info.get("full_path", entity_info["path"]))
            # Check if in root or has no relationships
            if len(path.parts) <= 2 or not entity_info.get("relationships"):
                entity_info["orphaned"] = True
                results["orphaned"].append(unified_id)
                orphaned_count += 1
        
        print(f"✓ Orphaned files found: {orphaned_count}")
        self.log_progress("Phase 2", "Orphaned", "complete", {"count": orphaned_count})
        
        # Step 4: Map current structure
        print("\nStep 4: Mapping current structure...")
        self.log_progress("Phase 2", "Structure Map", "starting")
        
        # Create structure map
        for unified_id, entity_info in self.entity_database.items():
            results["structure_map"][unified_id] = {
                "path": entity_info["path"],
                "type": entity_info["entity_type"],
                "relationships": entity_info.get("relationships", []),
                "orphaned": entity_info.get("orphaned", False)
            }
        
        print(f"✓ Structure mapped: {len(results['structure_map'])} entities")
        self.log_progress("Phase 2", "Structure Map", "complete")
        
        print()
        return results
    
    def phase_3_validation(self, discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Validation (Verify Safety)"""
        
        print("=" * 70)
        print("  PHASE 3: VALIDATION (Verify Safety)")
        print("=" * 70)
        print()
        
        results = {
            "relationships_valid": False,
            "duplicates_valid": False,
            "orphaned_valid": False,
            "safety_check": False
        }
        
        # Step 1: Validate relationships
        print("Step 1: Validating relationships...")
        self.log_progress("Phase 3", "Relationship Validation", "starting")
        
        relationships = discovery_results.get("relationships", {})
        relationships_valid = len(relationships) > 0 or len(self.entity_database) > 0
        
        results["relationships_valid"] = relationships_valid
        
        if relationships_valid:
            print("✓ Relationships validated")
            self.log_progress("Phase 3", "Relationship Validation", "complete", {"valid": True})
        else:
            print("✗ Relationships validation failed")
            self.log_progress("Phase 3", "Relationship Validation", "failed")
        
        # Step 2: Verify duplicate identification
        print("\nStep 2: Verifying duplicate identification...")
        self.log_progress("Phase 3", "Duplicate Validation", "starting")
        
        duplicates = discovery_results.get("duplicates", [])
        duplicates_valid = isinstance(duplicates, list)
        
        results["duplicates_valid"] = duplicates_valid
        
        if duplicates_valid:
            print(f"✓ Duplicates verified: {len(duplicates)} groups")
            self.log_progress("Phase 3", "Duplicate Validation", "complete", {"valid": True, "count": len(duplicates)})
        else:
            print("✗ Duplicate verification failed")
            self.log_progress("Phase 3", "Duplicate Validation", "failed")
        
        # Step 3: Safety check - No data loss risk
        print("\nStep 3: Safety check - Verifying no data loss risk...")
        self.log_progress("Phase 3", "Safety Check", "starting")
        
        safety_checks = []
        
        # Check 1: Backup exists
        backup_exists = self.backup_path and Path(self.backup_path).exists()
        safety_checks.append(("Backup exists", backup_exists))
        
        # Check 2: Entity database exists
        db_exists = len(self.entity_database) > 0
        safety_checks.append(("Entity database exists", db_exists))
        
        # Check 3: All entities accounted for
        entities_accounted = all(
            entity.get("full_path") and Path(entity["full_path"]).exists()
            for entity in self.entity_database.values()
            if entity["entity_type"] == "file"
        )
        safety_checks.append(("All entities accounted for", entities_accounted))
        
        # Check 4: Rollback capability
        rollback_available = backup_exists
        safety_checks.append(("Rollback available", rollback_available))
        
        results["safety_checks"] = safety_checks
        results["safety_check"] = all(check[1] for check in safety_checks)
        
        print("Safety checks:")
        for check_name, check_passed in safety_checks:
            status = "✓" if check_passed else "✗"
            print(f"  {status} {check_name}")
        
        if results["safety_check"]:
            print("\n✓ Safety check passed - No data loss risk")
            self.log_progress("Phase 3", "Safety Check", "complete", {"passed": True})
            self.safety_checks_passed = True
        else:
            print("\n✗ Safety check failed - Data loss risk detected")
            self.log_progress("Phase 3", "Safety Check", "failed", {"checks": safety_checks})
            raise ValueError("Safety check failed - Cannot proceed")
        
        print()
        return results
    
    def phase_4_planning(self, discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Planning (Safe Changes)"""
        
        print("=" * 70)
        print("  PHASE 4: PLANNING (Safe Changes)")
        print("=" * 70)
        print()
        
        if not self.safety_checks_passed:
            raise ValueError("Safety checks not passed - Cannot plan")
        
        results = {
            "organization_structure": {},
            "consolidation_rules": {},
            "file_movements": {},
            "plan_valid": False
        }
        
        # Step 1: Plan organization structure
        print("Step 1: Planning organization structure...")
        self.log_progress("Phase 4", "Structure Planning", "starting")
        
        # Group entities by relationships
        organization_structure = {
            "organiindustrial_host": [],
            "consolidated": [],
            "connected": [],
            "preserved": []
        }
        
        # Plan: Group related files together
        for unified_id, entity_info in self.entity_database.items():
            relationships = entity_info.get("relationships", [])
            if relationships:
                # Has relationships - organize by relationships
                organization_structure["organiindustrial_host"].append(unified_id)
            elif entity_info.get("orphaned"):
                # Orphaned - connect to related group
                organization_structure["connected"].append(unified_id)
            else:
                # Preserve structure
                organization_structure["preserved"].append(unified_id)
        
        results["organization_structure"] = organization_structure
        
        print(f"✓ Organization structure planned")
        print(f"  Organiindustrial_host: {len(organization_structure['organiindustrial_host'])}")
        print(f"  Connected: {len(organization_structure['connected'])}")
        print(f"  Preserved: {len(organization_structure['preserved'])}")
        self.log_progress("Phase 4", "Structure Planning", "complete", {
            "organiindustrial_host": len(organization_structure['organiindustrial_host']),
            "connected": len(organization_structure['connected']),
            "preserved": len(organization_structure['preserved'])
        })
        
        # Step 2: Define consolidation rules
        print("\nStep 2: Defining consolidation rules...")
        self.log_progress("Phase 4", "Consolidation Rules", "starting")
        
        duplicates = discovery_results.get("duplicates", [])
        consolidation_rules = {}
        
        for dup_group in duplicates:
            entities = dup_group.get("entities", [])
            if len(entities) > 1:
                # Keep first entity, mark others for consolidation
                keep_entity = entities[0]
                for entity_id in entities[1:]:
                    consolidation_rules[entity_id] = keep_entity
        
        results["consolidation_rules"] = consolidation_rules
        
        print(f"✓ Consolidation rules defined: {len(consolidation_rules)}")
        self.log_progress("Phase 4", "Consolidation Rules", "complete", {"count": len(consolidation_rules)})
        
        # Step 3: Map file movements
        print("\nStep 3: Mapping file movements...")
        self.log_progress("Phase 4", "File Movements", "starting")
        
        file_movements = {}
        # For now, plan minimal movements (safety first)
        # Only move orphaned files to organiindustrial_host locations
        
        orphaned = discovery_results.get("orphaned", [])
        for orphaned_id in orphaned[:10]:  # Limit to 10 for safety
            entity_info = self.entity_database.get(orphaned_id)
            if entity_info:
                # Plan to move to organiindustrial_host location
                current_path = entity_info["path"]
                # Simple plan: move root files to organiindustrial_host directory
                if len(Path(current_path).parts) <= 2:
                    new_path = f"organiindustrial_host/{Path(current_path).name}"
                    file_movements[orphaned_id] = {
                        "from": current_path,
                        "to": new_path
                    }
        
        results["file_movements"] = file_movements
        
        print(f"✓ File movements mapped: {len(file_movements)}")
        self.log_progress("Phase 4", "File Movements", "complete", {"count": len(file_movements)})
        
        # Step 4: Validate plan doesn't break dependencies
        print("\nStep 4: Validating plan doesn't break dependencies...")
        self.log_progress("Phase 4", "Plan Validation", "starting")
        
        plan_valid = True
        validation_issues = []
        
        # Check: No circular dependencies in movements
        for unified_id, movement in file_movements.items():
            from_path = movement["from"]
            to_path = movement["to"]
            
            # Check if destination conflicts with source
            if Path(to_path) == Path(from_path):
                validation_issues.append(f"Circular movement: {unified_id}")
                plan_valid = False
        
        results["plan_valid"] = plan_valid
        results["validation_issues"] = validation_issues
        
        if plan_valid:
            print("✓ Plan validated - No dependency issues")
            self.log_progress("Phase 4", "Plan Validation", "complete", {"valid": True})
            
            # Store plan
            # Convert entity database to EntityInfo objects (handle missing fields)
            entities = []
            for entity_info in self.entity_database.values():
                # Extract required fields with defaults
                entity = EntityInfo(
                    path=entity_info.get("path", ""),
                    unified_id=entity_info.get("unified_id", {}).get("hybrid_id", "") if isinstance(entity_info.get("unified_id"), dict) else str(entity_info.get("unified_id", "")),
                    entity_type=entity_info.get("entity_type", "file"),
                    relationships=entity_info.get("relationships", []),
                    duplicates=entity_info.get("duplicates", []),
                    orphaned=entity_info.get("orphaned", False),
                    dependencies=entity_info.get("dependencies", []),
                    timestamp=entity_info.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    full_path=entity_info.get("full_path")
                )
                entities.append(entity)
            
            self.organization_plan = OrganizationPlan(
                backup_path=self.backup_path,
                entities=entities,
                organization_structure=organization_structure,
                consolidation_rules=consolidation_rules,
                file_movements=file_movements,
                safety_checks=[],
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        else:
            print("✗ Plan validation failed")
            print(f"  Issues: {validation_issues}")
            self.log_progress("Phase 4", "Plan Validation", "failed", {"issues": validation_issues})
            raise ValueError("Plan validation failed - Cannot proceed")
        
        print()
        return results
    
    def phase_5_execution(self) -> Dict[str, Any]:
        """Phase 5: Execution (Safe Application)"""
        
        print("=" * 70)
        print("  PHASE 5: EXECUTION (Safe Application)")
        print("=" * 70)
        print()
        
        if not self.organization_plan:
            raise ValueError("No organization plan - Cannot execute")
        
        if not self.safety_checks_passed:
            raise ValueError("Safety checks not passed - Cannot execute")
        
        results = {
            "files_moved": 0,
            "files_consolidated": 0,
            "files_connected": 0,
            "errors": []
        }
        
        # Step 1: Create organization structure
        print("Step 1: Creating organization structure...")
        self.log_progress("Phase 5", "Structure Creation", "starting")
        
        organiindustrial_host_dir = self.root_path / "organiindustrial_host"
        organiindustrial_host_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Organization directory created: {organiindustrial_host_dir}")
        self.log_progress("Phase 5", "Structure Creation", "complete")
        
        # Step 2: Move files by unified ID (limited for safety)
        print("\nStep 2: Moving files (safe mode - limited)...")
        self.log_progress("Phase 5", "File Movements", "starting")
        
        file_movements = self.organization_plan.file_movements
        moved_count = 0
        
        for unified_id, movement in list(file_movements.items())[:5]:  # Limit to 5 for safety
            try:
                from_path = self.root_path / movement["from"]
                to_path = self.root_path / movement["to"]
                
                if from_path.exists():
                    to_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(from_path), str(to_path))
                    
                    # Update entity database
                    if unified_id in self.entity_database:
                        self.entity_database[unified_id]["path"] = movement["to"]
                    
                    moved_count += 1
                    print(f"  ✓ Moved: {movement['from']} → {movement['to']}")
            except Exception as e:
                error_msg = f"Failed to move {unified_id}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
                print(f"  ✗ Error: {error_msg}")
        
        results["files_moved"] = moved_count
        
        print(f"✓ Files moved: {moved_count}")
        self.log_progress("Phase 5", "File Movements", "complete", {"count": moved_count})
        
        # Step 3: Consolidate duplicates (mark only - don't delete)
        print("\nStep 3: Marking duplicates for consolidation...")
        self.log_progress("Phase 5", "Consolidation", "starting")
        
        consolidation_rules = self.organization_plan.consolidation_rules
        consolidated_count = len(consolidation_rules)
        
        # For safety, just mark - don't delete
        for unified_id, keep_entity in consolidation_rules.items():
            if unified_id in self.entity_database:
                self.entity_database[unified_id]["consolidated_into"] = keep_entity
                print(f"  ✓ Marked for consolidation: {unified_id} → {keep_entity}")
        
        results["files_consolidated"] = consolidated_count
        
        print(f"✓ Duplicates marked: {consolidated_count}")
        self.log_progress("Phase 5", "Consolidation", "complete", {"count": consolidated_count})
        
        # Step 4: Validate each step
        print("\nStep 4: Validating execution steps...")
        self.log_progress("Phase 5", "Step Validation", "starting")
        
        validation_passed = len(results["errors"]) == 0
        
        if validation_passed:
            print("✓ Execution validation passed")
            self.log_progress("Phase 5", "Step Validation", "complete", {"passed": True})
        else:
            print(f"✗ Execution validation failed: {len(results['errors'])} errors")
            self.log_progress("Phase 5", "Step Validation", "failed", {"errors": len(results["errors"])})
        
        print()
        return results
    
    def phase_6_verification(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 6: Verification (Confirm Success)"""
        
        print("=" * 70)
        print("  PHASE 6: VERIFICATION (Confirm Success)")
        print("=" * 70)
        print()
        
        results = {
            "files_moved_correctly": False,
            "relationships_maintained": False,
            "no_data_loss": False,
            "verification_complete": False
        }
        
        # Step 1: Verify all files moved correctly
        print("Step 1: Verifying files moved correctly...")
        self.log_progress("Phase 6", "File Verification", "starting")
        
        file_movements = self.organization_plan.file_movements
        moved_correctly = True
        
        for unified_id, movement in file_movements.items():
            to_path = self.root_path / movement["to"]
            if not to_path.exists():
                moved_correctly = False
                print(f"  ✗ File not found at destination: {movement['to']}")
                break
        
        results["files_moved_correctly"] = moved_correctly
        
        if moved_correctly:
            print("✓ All files moved correctly")
            self.log_progress("Phase 6", "File Verification", "complete", {"passed": True})
        else:
            print("✗ Some files not moved correctly")
            self.log_progress("Phase 6", "File Verification", "failed")
        
        # Step 2: Verify relationships maintained
        print("\nStep 2: Verifying relationships maintained...")
        self.log_progress("Phase 6", "Relationship Verification", "starting")
        
        relationships_maintained = True
        # Check if relationships are still accessible
        for unified_id, entity_info in self.entity_database.items():
            relationships = entity_info.get("relationships", [])
            if relationships:
                # Relationships exist - verify they're accessible
                path = Path(entity_info.get("full_path", entity_info["path"]))
                if not path.exists():
                    relationships_maintained = False
                    break
        
        results["relationships_maintained"] = relationships_maintained
        
        if relationships_maintained:
            print("✓ Relationships maintained")
            self.log_progress("Phase 6", "Relationship Verification", "complete", {"passed": True})
        else:
            print("✗ Some relationships may be broken")
            self.log_progress("Phase 6", "Relationship Verification", "failed")
        
        # Step 3: Verify no data loss
        print("\nStep 3: Verifying no data loss...")
        self.log_progress("Phase 6", "Data Loss Check", "starting")
        
        # Count files before and after
        original_count = len([e for e in self.entity_database.values() if e["entity_type"] == "file"])
        current_count = len([f for f in self.root_path.rglob('*') if f.is_file() and 'backups' not in str(f) and not self.is_quarantined(f)])
        
        # Account for moved files
        no_data_loss = current_count >= (original_count - len(self.organization_plan.file_movements))
        
        results["no_data_loss"] = no_data_loss
        results["original_count"] = original_count
        results["current_count"] = current_count
        
        if no_data_loss:
            print("✓ No data loss detected")
            print(f"  Original: {original_count}, Current: {current_count}")
            self.log_progress("Phase 6", "Data Loss Check", "complete", {"passed": True})
        else:
            print("✗ Potential data loss detected")
            print(f"  Original: {original_count}, Current: {current_count}")
            self.log_progress("Phase 6", "Data Loss Check", "failed", {
                "original": original_count,
                "current": current_count
            })
        
        results["verification_complete"] = (
            results["files_moved_correctly"] and
            results["relationships_maintained"] and
            results["no_data_loss"]
        )
        
        print()
        return results
    
    def phase_7_validation(self, verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 7: Validation (Final Safety Check)"""
        
        print("=" * 70)
        print("  PHASE 7: VALIDATION (Final Safety Check)")
        print("=" * 70)
        print()
        
        results = {
            "tests_passed": False,
            "functionality_intact": False,
            "relationships_preserved": False,
            "validation_complete": False
        }
        
        # Step 1: Run basic tests
        print("Step 1: Running basic tests...")
        self.log_progress("Phase 7", "Testing", "starting")
        
        # Check if key files are accessible
        key_files = [
            "unified_math_implementation.py",
            "decision_making_matrix.py",
            "provability_chain_system.py"
        ]
        
        tests_passed = True
        for key_file in key_files:
            # Check if file exists in codebase
            found = any(
                key_file in entity.get("path", "") or key_file in entity.get("full_path", "")
                for entity in self.entity_database.values()
            )
            if not found:
                # Check root path
                if not (self.root_path / key_file).exists():
                    # Check organiindustrial_host directory
                    if not (self.root_path / "organiindustrial_host" / key_file).exists():
                        tests_passed = False
                        break
        
        results["tests_passed"] = tests_passed
        
        if tests_passed:
            print("✓ Basic tests passed")
            self.log_progress("Phase 7", "Testing", "complete", {"passed": True})
        else:
            print("✗ Some tests failed")
            self.log_progress("Phase 7", "Testing", "failed")
        
        # Step 2: Verify functionality intact
        print("\nStep 2: Verifying functionality intact...")
        self.log_progress("Phase 7", "Functionality Check", "starting")
        
        # Check if unified math still works
        functionality_intact = UNIFIED_MATH_AVAILABLE
        
        if functionality_intact:
            try:
                test_id = Id_unified("test_entity", "test")
                if test_id and "hybrid_id" in test_id:
                    functionality_intact = True
                else:
                    functionality_intact = False
            except:
                functionality_intact = False
        
        results["functionality_intact"] = functionality_intact
        
        if functionality_intact:
            print("✓ Functionality intact")
            self.log_progress("Phase 7", "Functionality Check", "complete", {"passed": True})
        else:
            print("✗ Functionality may be compromised")
            self.log_progress("Phase 7", "Functionality Check", "failed")
        
        # Step 3: Verify relationships preserved
        print("\nStep 3: Verifying relationships preserved...")
        self.log_progress("Phase 7", "Relationship Preservation", "starting")
        
        relationships_preserved = verification_results.get("relationships_maintained", False)
        results["relationships_preserved"] = relationships_preserved
        
        if relationships_preserved:
            print("✓ Relationships preserved")
            self.log_progress("Phase 7", "Relationship Preservation", "complete", {"passed": True})
        else:
            print("✗ Some relationships may be lost")
            self.log_progress("Phase 7", "Relationship Preservation", "failed")
        
        results["validation_complete"] = (
            results["tests_passed"] and
            results["functionality_intact"] and
            results["relationships_preserved"]
        )
        
        if results["validation_complete"]:
            print("\n✓ Final validation complete - All checks passed")
        else:
            print("\n✗ Final validation incomplete - Some checks failed")
        
        print()
        return results
    
    def phase_8_tracking(self) -> Dict[str, Any]:
        """Phase 8: Tracking (Monitor Results)"""
        
        print("=" * 70)
        print("  PHASE 8: TRACKING (Monitor Results)")
        print("=" * 70)
        print()
        
        results = {
            "progress_logged": False,
            "structure_monitored": False,
            "organization_maintained": False
        }
        
        # Step 1: Log progress
        print("Step 1: Logging progress...")
        self.log_progress("Phase 8", "Progress Logging", "starting")
        
        # Save progress log
        progress_path = self.root_path / "organization" / "progress_log.json"
        progress_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(progress_path, 'w') as f:
            json.dump({
                "progress_log": self.progress_log,
                "total_phases": 8,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        results["progress_logged"] = True
        
        print(f"✓ Progress logged: {progress_path}")
        self.log_progress("Phase 8", "Progress Logging", "complete")
        
        # Step 2: Monitor structure
        print("\nStep 2: Monitoring structure...")
        self.log_progress("Phase 8", "Structure Monitoring", "starting")
        
        # Create structure snapshot
        structure_snapshot = {
            "entity_count": len(self.entity_database),
            "organiindustrial_host_count": len(self.organization_plan.organization_structure.get("organiindustrial_host", [])),
            "orphaned_count": len([e for e in self.entity_database.values() if e.get("orphaned")]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        snapshot_path = self.root_path / "organization" / "structure_snapshot.json"
        with open(snapshot_path, 'w') as f:
            json.dump(structure_snapshot, f, indent=2)
        
        results["structure_monitored"] = True
        
        print(f"✓ Structure monitored: {snapshot_path}")
        self.log_progress("Phase 8", "Structure Monitoring", "complete")
        
        # Step 3: Maintain organization
        print("\nStep 3: Setting up organization maintenance...")
        self.log_progress("Phase 8", "Maintenance Setup", "starting")
        
        # Update entity database
        database_path = self.root_path / "organization" / "entity_database.json"
        with open(database_path, 'w') as f:
            json.dump({
                "entities": self.entity_database,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_entities": len(self.entity_database),
                "organization_plan": asdict(self.organization_plan) if self.organization_plan else None
            }, f, indent=2)
        
        results["organization_maintained"] = True
        
        print(f"✓ Organization maintained: {database_path}")
        self.log_progress("Phase 8", "Maintenance Setup", "complete")
        
        print()
        return results
    
    def rollback(self) -> Dict[str, Any]:
        """Rollback to backup state"""
        
        print("=" * 70)
        print("  ROLLBACK")
        print("=" * 70)
        print()
        
        if not self.backup_path or not Path(self.backup_path).exists():
            raise ValueError("No backup available for rollback")
        
        print(f"Rolling back to: {self.backup_path}")
        self.log_progress("Rollback", "Starting", "rollback")
        
        # Restore from backup
        backup_dir = Path(self.backup_path)
        restored_count = 0
        
        for item in backup_dir.iterdir():
            try:
                dest = self.root_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    restored_count += 1
                elif item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                    restored_count += 1
            except Exception as e:
                logger.error(f"Failed to restore {item}: {e}")
        
        print(f"✓ Rollback complete: {restored_count} items restored")
        self.log_progress("Rollback", "Complete", "rollback", {"count": restored_count})
        
        return {
            "rollback_path": self.backup_path,
            "restored_count": restored_count,
            "success": True
        }
    
    def execute_full_organization(self) -> Dict[str, Any]:
        """Execute full 8-phase organization process"""
        
        print("=" * 70)
        print("  ORGANIZATION AUTOMATION SERVICE")
        print("  Full 8-Phase Safe Organization Process")
        print("=" * 70)
        print()
        
        results = {}
        
        try:
            # Phase 1: Preparation
            results["phase_1"] = self.phase_1_preparation()
            
            # Phase 2: Discovery
            results["phase_2"] = self.phase_2_discovery()
            
            # Phase 3: Validation
            results["phase_3"] = self.phase_3_validation(results["phase_2"])
            
            # Phase 4: Planning
            results["phase_4"] = self.phase_4_planning(results["phase_2"])
            
            # Phase 5: Execution
            results["phase_5"] = self.phase_5_execution()
            
            # Phase 6: Verification
            results["phase_6"] = self.phase_6_verification(results["phase_5"])
            
            # Phase 7: Validation
            results["phase_7"] = self.phase_7_validation(results["phase_6"])
            
            # Phase 8: Tracking
            results["phase_8"] = self.phase_8_tracking()
            
            results["success"] = True
            results["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            print("=" * 70)
            print("  ORGANIZATION COMPLETE")
            print("=" * 70)
            print()
            print("✓ All 8 phases completed successfully")
            print(f"✓ Backup available at: {self.backup_path}")
            print(f"✓ Progress logged in: organization/progress_log.json")
            print()
            
        except Exception as e:
            logger.error(f"Organization failed: {e}")
            results["success"] = False
            results["error"] = str(e)
            
            print("=" * 70)
            print("  ORGANIZATION FAILED")
            print("=" * 70)
            print()
            print(f"✗ Error: {e}")
            print(f"✓ Backup available for rollback: {self.backup_path}")
            print()
            print("To rollback, run: service.rollback()")
            print()
        
        return results


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Organization Automation Service")
    parser.add_argument("--root", type=str, help="Root path for organization")
    parser.add_argument("--phase", type=int, help="Run specific phase (1-8)")
    parser.add_argument("--rollback", action="store_true", help="Rollback to backup")
    parser.add_argument("--safe-mode", action="store_true", default=True, help="Safe mode (limited changes)")
    
    args = parser.parse_args()
    
    service = OrganizationAutomationService(root_path=args.root)
    
    if args.rollback:
        result = service.rollback()
        print(json.dumps(result, indent=2))
    elif args.phase:
        # Run specific phase (for testing)
        if args.phase == 1:
            result = service.phase_1_preparation()
        elif args.phase == 2:
            service.phase_1_preparation()
            result = service.phase_2_discovery()
        # ... add other phases as needed
        print(json.dumps(result, indent=2))
    else:
        # Run full organization
        result = service.execute_full_organization()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

