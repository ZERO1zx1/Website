#!/usr/bin/env python3
"""
Secure Code Runner
Executes code in isolated environment with resource limits
"""

import json
import resource
import subprocess  # nosec B404
import sys
from typing import Dict


class CodeRunner:
    """Execute code with resource limits and timeout"""
    
    def __init__(self, timeout: int = 5, memory_limit_mb: int = 256):
        """
        Initialize code runner
        
        Args:
            timeout: Maximum execution time in seconds
            memory_limit_mb: Maximum memory in megabytes
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
    
    def set_resource_limits(self):
        """Set resource limits for child process"""
        # Memory limit
        memory_bytes = self.memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        # CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
        
        # File size limit (prevent disk exhaustion)
        resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
    
    def run_python(self, code: str, test_input: str = "") -> Dict:
        """
        Run Python code with test input
        
        Args:
            code: Python code to execute
            test_input: Input to provide to the code
        
        Returns:
            Dictionary with status, output, and error information
        """
        try:
            # Create subprocess with resource limits
            process = subprocess.Popen(  # nosec B603
                [sys.executable, "-c", code],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self.set_resource_limits
            )
            
            # Run with timeout
            try:
                stdout, stderr = process.communicate(input=test_input, timeout=self.timeout)
                
                if process.returncode == 0:
                    return {
                        'status': 'success',
                        'output': stdout,
                        'error': None
                    }
                else:
                    return {
                        'status': 'runtime_error',
                        'output': stdout,
                        'error': stderr
                    }
            
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'status': 'timeout',
                    'output': None,
                    'error': f'Execution exceeded {self.timeout} second timeout'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'output': None,
                'error': str(e)
            }
    
    def run_javascript(self, code: str, test_input: str = "") -> Dict:
        """
        Run JavaScript code (requires Node.js)
        
        Args:
            code: JavaScript code to execute
            test_input: Input to provide to the code
        
        Returns:
            Dictionary with status, output, and error information
        """
        try:
            process = subprocess.Popen(  # nosec B603 B607
                ["node", "-e", code],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self.set_resource_limits
            )
            
            try:
                stdout, stderr = process.communicate(input=test_input, timeout=self.timeout)
                
                if process.returncode == 0:
                    return {
                        'status': 'success',
                        'output': stdout,
                        'error': None
                    }
                else:
                    return {
                        'status': 'runtime_error',
                        'output': stdout,
                        'error': stderr
                    }
            
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'status': 'timeout',
                    'output': None,
                    'error': f'Execution exceeded {self.timeout} second timeout'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'output': None,
                'error': str(e)
            }
    
    def compare_output(self, actual: str, expected: str) -> bool:
        """
        Compare actual output with expected output
        
        Args:
            actual: Actual output from code
            expected: Expected output
        
        Returns:
            True if outputs match, False otherwise
        """
        # Strip whitespace and compare
        return actual.strip() == expected.strip()
    
    def run_test_case(self, code: str, language: str, test_input: str, 
                     expected_output: str) -> Dict:
        """
        Run code against a single test case
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript)
            test_input: Input for the test case
            expected_output: Expected output
        
        Returns:
            Dictionary with test result
        """
        # Run the code
        if language == 'python':
            result = self.run_python(code, test_input)
        elif language == 'javascript':
            result = self.run_javascript(code, test_input)
        else:
            return {
                'status': 'error',
                'passed': False,
                'message': f'Unsupported language: {language}'
            }
        
        # Check result
        if result['status'] == 'success':
            passed = self.compare_output(result['output'], expected_output)
            return {
                'status': 'completed',
                'passed': passed,
                'actual_output': result['output'],
                'expected_output': expected_output,
                'message': 'Test passed' if passed else 'Output mismatch'
            }
        else:
            return {
                'status': result['status'],
                'passed': False,
                'error': result['error'],
                'message': f'Execution error: {result["error"]}'
            }

def main():
    """Main entry point for sandbox runner"""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No input provided'}))
        sys.exit(1)
    
    try:
        # Parse input JSON
        input_data = json.loads(sys.argv[1])
        
        # Extract parameters
        code = input_data.get('code')
        language = input_data.get('language', 'python')
        test_input = input_data.get('input', '')
        expected_output = input_data.get('expected_output')
        timeout = input_data.get('timeout', 5)
        memory_limit = input_data.get('memory_limit_mb', 256)
        
        if not code:
            print(json.dumps({'error': 'No code provided'}))
            sys.exit(1)
        
        # Create runner and execute
        runner = CodeRunner(timeout=timeout, memory_limit_mb=memory_limit)
        result = runner.run_test_case(code, language, test_input, expected_output)
        
        print(json.dumps(result))
    
    except json.JSONDecodeError:
        print(json.dumps({'error': 'Invalid JSON input'}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
