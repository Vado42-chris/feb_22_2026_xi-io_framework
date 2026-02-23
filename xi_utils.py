#!/usr/bin/env python3
"""
XI CLI Utility Commands
Real tools that actually do things
"""
import os
import json
import subprocess
import hashlib
import tempfile
import shutil
from pathlib import Path

# Industrial Root Imports
try:
    from framework import HardwareGuard, ActionReceipt
except ImportError:
    # Fallback for standalone tests
    class HardwareGuard:
        @staticmethod
        def verify_io(path, hash=None): return True
    class ActionReceipt:
        @staticmethod
        def create(op, path, ok, **kwargs): return json.dumps({"op": op, "path": path, "ok": ok, **kwargs})

class XIUtils:
    """Utility commands that actually work"""
    
    def __init__(self, working_dir, context_manager=None):
        self.working_dir = working_dir
        self.context_manager = context_manager

    def _get_path(self, filename):
        """Standardized Path Resolution (v8.9.9.9.16)"""
        if isinstance(filename, Path):
            return filename
        
        # Expand user home
        if filename.startswith('~'):
            return Path(os.path.expanduser(filename))
            
        # Handle absolute paths
        target = Path(filename)
        if target.is_absolute():
            return target
            
        # Default: relative to working_dir
        return Path(self.working_dir) / filename

    def _is_in_bounds(self, filename):
        """
        POLICY A: Strict Workspace Boundary Enforcement
        - No symlink traversal allowed on any component
        - Must be rooted in working_dir OR be explicitly declared as a Historical Sovereign Point (~/.xi-io)
        """
        try:
            abs_working_dir = Path(self.working_dir).resolve(strict=True)
            target_path = self._get_path(filename)
            
            # Historical Sovereign Point Exemption (~/.xi-io)
            home_xi = Path(os.path.expanduser("~/.xi-io"))
            if home_xi in target_path.parents or target_path == home_xi:
                return True

            # Standard Workspace Boundary Check (v8.9.9.9.17)
            # Before resolution, check if any parent or the file itself is a symlink
            # and if it attempts to escape the root
            
            # 1. Normalize the path without following symlinks
            # This is tricky in Python, we'll manually check parts
            norm_target = target_path.absolute()
            
            # 2. Check for symlinks in the path components *relative to working_dir*
            try:
                rel_path = norm_target.relative_to(abs_working_dir)
            except ValueError:
                # Outside working_dir
                return False
                
            # 3. Component-wise symlink detection
            check_path = abs_working_dir
            for part in rel_path.parts:
                check_path = check_path / part
                if check_path.is_symlink():
                    return False # Reject ANY symlink traversal
            
            # 4. Final verify: resolve and ensure it's still inside
            abs_target = norm_target.resolve()
            return abs_working_dir in abs_target.parents or abs_target == abs_working_dir
        except Exception:
            return False

    def _is_safe(self, path):
        """Check if path is safe from quarantine and within boundaries (Policy A)"""
        if not self._is_in_bounds(path):
            return False
        if not self.context_manager:
            return True # Industrial Anchor v8.9.9.9.17
        return not self.context_manager.is_quarantined(str(path))

    def _get_file_info(self, filepath):
        """Get Tool-Truth metrics (length, hash)"""
        import os
        try:
            content = filepath.read_bytes()
            return {
                'length': len(content),
                'sha256': hashlib.sha256(content).hexdigest(),
                'mtime': os.path.getmtime(filepath)
            }
        except:
            return None
    
    def list_files(self, pattern="*"):
        """List files in working directory"""
        files = list(Path(self.working_dir).glob(pattern))
        return sorted([f.name for f in files if f.is_file() and self._is_safe(f)])
    
    def search_files(self, text):
        """Search for text in files (Industrial Search)"""
        results = []
        try:
            # Shift the heavy lifting to rg
            result = subprocess.run(
                ['rg', '-n', '--smart-case', text, str(self.working_dir)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Format: path/to/file:line:content
                current_file = None
                current_lines = []
                for line in result.stdout.splitlines():
                    parts = line.split(':', 2)
                    if len(parts) >= 2:
                        filepath = parts[0]
                        line_num = int(parts[1])
                        
                        if filepath != current_file:
                            if current_file and self._is_safe(Path(current_file)):
                                results.append({'file': Path(current_file).name, 'lines': current_lines})
                            current_file = filepath
                            current_lines = [line_num]
                        else:
                            current_lines.append(line_num)
                
                # Final append
                if current_file and self._is_safe(Path(current_file)):
                    results.append({'file': Path(current_file).name, 'lines': current_lines})
                return results
        except Exception:
            pass

        # Robust Fallback (Bounded)
        for f in Path(self.working_dir).glob("*.py"):
            if f.is_file() and self._is_safe(f):
                try:
                    content = f.read_text(errors='ignore')
                    if text.lower() in content.lower():
                        line_nums = [i+1 for i, line in enumerate(content.split('\n')) 
                                    if text.lower() in line.lower()]
                        results.append({'file': f.name, 'lines': line_nums})
                except: pass
            if len(results) > 20: break # Safety cap for fallback
        return results
    
    def git_status(self):
        """Get git status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout if result.returncode == 0 else "Not a git repo"
        except:
            return "Git not available"
    
    def git_commit(self, message):
        """Quick git commit"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.working_dir, timeout=5)
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def test_file(self, filename):
        """Run tests on a file"""
        filepath = Path(self.working_dir) / filename
        if not filepath.exists():
            return f"File not found: {filename}"
        
        if filename.endswith('.py'):
            try:
                result = subprocess.run(
                    ['python3', filename],
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return "Only Python files supported"
    
    def backup_file(self, filename):
        """Backup a file"""
        src = Path(self.working_dir) / filename
        if not src.exists():
            return f"File not found: {filename}"
        
        dst = Path(self.working_dir) / f"{filename}.backup"
        try:
            dst.write_text(src.read_text())
            return f"Backed up to {dst.name}"
        except Exception as e:
            return f"Error: {e}"
    
    def diff_files(self, file1, file2):
        """Show diff between two files"""
        try:
            result = subprocess.run(
                ['diff', '-u', file1, file2],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout if result.stdout else "Files are identical"
        except:
            return "Diff not available"
    
    def count_lines(self, pattern="*.py"):
        """Count lines of code without scanning recursive/system-heavy paths."""
        total = 0
        files = 0
        ignored = ['!.git/*', '!.venv/*', '!node_modules/*', '!__pycache__/*']

        try:
            # Fast path for wide scans: use ripgrep with strict excludes.
            if pattern == "*" or pattern == "**/*":
                cmd = ['rg', '--files']
                for glob in ['*'] + ignored:
                    cmd.extend(['-g', glob])
                result = subprocess.run(
                    cmd,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=8,
                    check=False,
                )
                candidates = [
                    (Path(self.working_dir) / line).resolve()
                    for line in result.stdout.splitlines()
                    if line.strip()
                ]
                for filepath in candidates:
                    if not filepath.is_file():
                        continue
                    if self._is_safe(filepath):
                        try:
                            total += len(filepath.read_text(errors='ignore').splitlines())
                            files += 1
                        except Exception:
                            continue
                return {'files': files, 'lines': total}
        except Exception:
            pass

        # Fallback for explicit globs
        for f in Path(self.working_dir).glob(pattern):
            if f.is_file() and self._is_safe(f):
                try:
                    total += len(f.read_text(errors='ignore').splitlines())
                    files += 1
                except Exception:
                    pass
            if files > 200:  # Safety cap
                break
        return {'files': files, 'lines': total}
    
    def quick_server(self, port=8000):
        """Start a quick HTTP server"""
        try:
            print(f"Starting server on http://localhost:{port}")
            print("Press Ctrl+C to stop")
            subprocess.run(
                ['python3', '-m', 'http.server', str(port)],
                cwd=self.working_dir
            )
        except KeyboardInterrupt:
            return "Server stopped"
    
    def verify_base_hash(self, filename, expected_hash):
        """Verify that a file has the expected hash (Stale Check)"""
        filepath = Path(self.working_dir) / filename
        if not filepath.exists():
            return False
        
        info = self._get_file_info(filepath)
        return info and info['sha256'] == expected_hash

    def write_file(self, filename, content):
        """
        Write content to a file (Policy A + Atomic Write-Fsync-Replace)
        """
        filepath = self._get_path(filename)
        if not self._is_safe(filepath):
            if not self._is_in_bounds(filepath):
                return ActionReceipt.create("write", filename, False, exit_code=13, policy="blocked", reason="POLICY_A_REJECTION")
            return ActionReceipt.create("write", filename, False, exit_code=13, policy="blocked", reason="QUARANTINE_REJECTION")
        
        content_bytes = content.encode('utf-8') if isinstance(content, str) else content
        expected_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Create temp file in the same directory as the target to allow atomic replace (v8.9.9.9.17)
        target_dir = filepath.parent
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(target_dir), prefix=".xi-tmp-")
        try:
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(content_bytes)
                f.flush()
                # Ensure it's on disk
                try:
                    os.fsync(f.fileno())
                except OSError: pass # Some filesystems don't support fsync
            
            # Atomic swap
            if filepath.exists():
                self.backup_file(filename)
            
            try:
                os.replace(tmp_path, str(filepath))
            except OSError as e:
                # Fallback for Cross-device link (Errno 18)
                if e.errno == 18:
                    shutil.move(tmp_path, str(filepath))
                else:
                    raise
            
            # HardwareGuard: Post-Write Verification (Sector Guard)
            # We verify the file on disk against the *intended* hash (Tool Truth)
            if not HardwareGuard.verify_io(filepath, expected_hash):
                 return ActionReceipt.create("write", filename, False, exit_code=12, policy="allowed", reason="HARDWARE_VERIFICATION_FAILED")

            # Post-Write Tool Truth Verification
            info = self._get_file_info(filepath)
            
            if self.context_manager:
                self.context_manager.add_action_receipt("WRITE", True, info)
                
            return ActionReceipt.create("write", filename, True, bytes=info['length'], sha256=info['sha256'], mtime=info['mtime'])
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if self.context_manager:
                self.context_manager.add_action_receipt("WRITE", False, str(e))
            return ActionReceipt.create("write", filename, False, exit_code=1, reason=str(e))

    def patch_file(self, filename, find_text, replace_text):
        """Simple find-and-replace patch (Quarantine-Aware)"""
        filepath = Path(self.working_dir) / filename
        if not self._is_safe(filepath):
             if not self._is_in_bounds(filepath):
                 return ActionReceipt.create("patch", filename, False, exit_code=13, policy="blocked", reason="POLICY_A_REJECTION")
             return ActionReceipt.create("patch", filename, False, exit_code=13, policy="blocked", reason="QUARANTINE_REJECTION")
        
        try:
            old_content = filepath.read_text()
            if find_text not in old_content:
                return ActionReceipt.create("patch", filename, False, exit_code=14, reason="STALE_PLAN")
            
            new_content = old_content.replace(find_text, replace_text)
            new_content_bytes = new_content.encode('utf-8')
            expected_hash = hashlib.sha256(new_content_bytes).hexdigest()
            
            # Backup
            self.backup_file(filename)
            
            # Atomic Write
            tmp_fd, tmp_path = tempfile.mkstemp(dir=self.working_dir, prefix=".xi-tmp-patch-")
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(new_content_bytes)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(tmp_path, str(filepath))
            
            # Sector Guard verification
            if not HardwareGuard.verify_io(filepath, expected_hash):
                 return ActionReceipt.create("patch", filename, False, exit_code=12, policy="allowed", reason="HARDWARE_VERIFICATION_FAILED")

            info = self._get_file_info(filepath)
            if self.context_manager:
                self.context_manager.add_action_receipt("PATCH", True, info)
                
            return ActionReceipt.create("patch", filename, True, bytes=info['length'], sha256=info['sha256'], mtime=info['mtime'])
        except Exception as e:
            if self.context_manager:
                self.context_manager.add_action_receipt("PATCH", False, str(e))
            return ActionReceipt.create("patch", filename, False, exit_code=1, reason=str(e))

    def read_file(self, filename):
        """Read content from a file (Boundary-Checked)"""
        filepath = self._get_path(filename)
        if not self._is_safe(filepath):
            if not self._is_in_bounds(filepath):
                return ActionReceipt.create("read", filename, False, exit_code=13, policy="blocked", reason="POLICY_A_REJECTION")
            return ActionReceipt.create("read", filename, False, exit_code=13, policy="blocked", reason="QUARANTINE_REJECTION")
        
        # HardwareGuard: Read Verification
        if not HardwareGuard.verify_io(filepath):
            return ActionReceipt.create("read", filename, False, exit_code=13, policy="blocked", reason="HARDWARE_READ_FAILED")

        try:
            content = filepath.read_text()
            # If receipts mode is active, the caller handles the content. 
            # This method returns the raw content if success, or receipt if failure.
            # To maintain compatibility with existing CLI logic but support receipts, 
            # we'll let the CLI decide how to output.
            return content
        except Exception as e:
            return ActionReceipt.create("read", filename, False, exit_code=1, reason=str(e))

    def delete_file(self, filename):
        """Delete a file (Quarantine-Aware)"""
        filepath = self._get_path(filename)
        if not self._is_safe(filepath):
            if not self._is_in_bounds(filepath):
                return ActionReceipt.create("delete", filename, False, exit_code=13, policy="blocked", reason="POLICY_A_REJECTION")
            return ActionReceipt.create("delete", filename, False, exit_code=13, policy="blocked", reason="QUARANTINE_REJECTION")
        
        if not filepath.exists():
            return ActionReceipt.create("delete", filename, False, exit_code=1, reason="FileNotFound")
        
        try:
            # Backup before deleting
            self.backup_file(filename)
            filepath.unlink()
            
            # Tool-Truth
            if self.context_manager:
                self.context_manager.add_action_receipt("DELETE", True, {"deleted": filename, "exists": False})
                
            return ActionReceipt.create("delete", filename, True)
        except Exception as e:
            if self.context_manager:
                self.context_manager.add_action_receipt("DELETE", False, str(e))
            return ActionReceipt.create("delete", filename, False, exit_code=1, reason=str(e))

    def run_command(self, command):
        """Execute a shell command with full logging (Tool-Truth)"""
        try:
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                shell=isinstance(command, str),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Tool-Truth
            info = {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "stdout_len": len(result.stdout),
                "stderr_len": len(result.stderr),
                "success": result.returncode == 0
            }
            if self.context_manager:
                self.context_manager.add_action_receipt("RUN", result.returncode == 0, info)
                
            return ActionReceipt.create("run", " ".join(command) if isinstance(command, list) else command, 
                                       result.returncode == 0, **info)
        except Exception as e:
            if self.context_manager:
                self.context_manager.add_action_receipt("RUN", False, str(e))
            return ActionReceipt.create("run", str(command), False, exit_code=1, reason=str(e))

    def format_code(self, filename):
        """Format Python code"""
        filepath = Path(self.working_dir) / filename
        if not filepath.exists():
            return f"File not found: {filename}"
        
        try:
            # Simple formatting: remove trailing whitespace, ensure newline at end
            content = filepath.read_text()
            lines = [line.rstrip() for line in content.split('\n')]
            formatted = '\n'.join(lines)
            if not formatted.endswith('\n'):
                formatted += '\n'
            
            filepath.write_text(formatted)
            return f"Formatted {filename}"
        except Exception as e:
            return f"Error: {e}"
