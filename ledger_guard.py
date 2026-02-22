import os
import json
import shutil
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

class LedgerGuard:
    """
    XI-IO Ledger Guard (v8.9.9.9.17)
    
    Protects the Industrial Audit Ledger from corruption, especially on 
    unreliable filesystems like NTFS via FUSE.
    """
    
    def __init__(self, ledger_path: Path):
        self.path = ledger_path
        self.backup_dir = self.path.parent / "ledger_backups"
        self.max_backups = 10
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup(self) -> Optional[Path]:
        """Creates a timestamped backup of the current ledger."""
        if not self.path.exists():
            return None
            
        timestamp = int(time.time())
        backup_path = self.backup_dir / f"ledger_{timestamp}.json.bak"
        
        try:
            shutil.copy2(self.path, backup_path)
            self._rotate_backups()
            return backup_path
        except Exception as e:
            print(f" [LedgerGuard] Backup failed: {e}")
            return None

    def _rotate_backups(self):
        """Maintains only the last N backups."""
        backups = sorted(self.backup_dir.glob("ledger_*.json.bak"))
        if len(backups) > self.max_backups:
            for b in backups[:len(backups) - self.max_backups]:
                try:
                    b.unlink()
                except Exception:
                    pass

    def validate(self, path: Optional[Path] = None) -> bool:
        """Validates that the ledger at path (or current path) is valid JSON and a list."""
        check_path = path or self.path
        if not check_path.exists():
            return False
            
        try:
            with open(check_path, 'r') as f:
                data = json.load(f)
                return isinstance(data, list)
        except (json.JSONDecodeError, Exception):
            return False

    def restore(self) -> bool:
        """Restores the ledger from the most recent valid backup."""
        backups = sorted(self.backup_dir.glob("ledger_*.json.bak"), reverse=True)
        for b in backups:
            if self.validate(b):
                try:
                    shutil.copy2(b, self.path)
                    print(f" [LedgerGuard] RESTORED ledger from {b.name}")
                    return True
                except Exception:
                    pass
        return False

    def safe_write(self, ledger_data: List[Dict[str, Any]]) -> bool:
        """
        Writes ledger data using a copy-then-rename pattern with pre-backup.
        Returns True if write was successful and verified.
        """
        # 1. Backup before write
        idx_backup = self.backup()
        
        # 2. Write to temp file in the same directory
        temp_path = self.path.with_suffix(".tmp")
        try:
            with open(temp_path, 'w') as f:
                json.dump(ledger_data, f, indent=2)
                f.flush()
                # Ensure it's on disk if the filesystem supports it
                try:
                    os.fsync(f.fileno())
                except OSError: pass
            
            # 3. Validation check on temp file
            if not self.validate(temp_path):
                raise ValueError("Temp ledger validation failed")
            
            # 4. Atomic swap
            os.replace(temp_path, self.path)
            
            # 5. Final validation
            if not self.validate():
                if idx_backup:
                    self.restore()
                return False
                
            return True
            
        except Exception as e:
            print(f" [LedgerGuard] Safe write failed: {e}")
            if temp_path.exists():
                temp_path.unlink()
            if idx_backup:
                self.restore()
            return False

    def read(self) -> List[Dict[str, Any]]:
        """Reads the ledger, restoring if corrupted."""
        if not self.path.exists():
            return []
            
        if not self.validate():
            print(f" [LedgerGuard] Corruption detected in {self.path.name}!")
            if self.restore():
                # Try reading again after restore
                return self.read()
            return []
            
        try:
            with open(self.path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def chain_hash(entry_data: str, prev_hash: str = "GENESIS") -> str:
        """Compute SHA256(prev_hash + entry_data) for tamper-evident chaining."""
        payload = f"{prev_hash}:{entry_data}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def get_last_hash(self) -> str:
        """Return the chain_hash of the last entry, or 'GENESIS' if empty."""
        ledger = self.read()
        if not ledger:
            return "GENESIS"
        last = ledger[-1]
        return last.get("chain_hash", "GENESIS")

    def verify_chain(self) -> Dict[str, Any]:
        """Verify the integrity of the full hash chain.
        
        Returns dict with 'valid' (bool), 'entries_checked' (int),
        'first_broken' (int or None), and 'unchained' (int) for legacy entries.
        """
        ledger = self.read()
        if not ledger:
            return {"valid": True, "entries_checked": 0, "first_broken": None, "unchained": 0}

        prev_hash = "GENESIS"
        unchained = 0
        for i, entry in enumerate(ledger):
            stored_chain = entry.get("chain_hash")
            if stored_chain is None:
                # Legacy entry without chain_hash — skip but count
                unchained += 1
                continue
            
            # Rebuild the hash from entry data (excluding chain_hash itself)
            entry_copy = {k: v for k, v in entry.items() if k != "chain_hash"}
            expected = self.chain_hash(json.dumps(entry_copy, sort_keys=True), prev_hash)
            
            if stored_chain != expected:
                return {
                    "valid": False, 
                    "entries_checked": i + 1, 
                    "first_broken": i,
                    "unchained": unchained
                }
            prev_hash = stored_chain
        
        return {
            "valid": True, 
            "entries_checked": len(ledger), 
            "first_broken": None,
            "unchained": unchained
        }

