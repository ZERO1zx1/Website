"""
Code Executor Service
Manages Docker containers for secure code execution
"""

import docker
import json
import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {'python', 'javascript'}
MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 15
MIN_MEMORY_MB = 64
MAX_MEMORY_MB = 512
MAX_CODE_LENGTH = 100_000
MAX_TEST_CASES = 100


def _error_result(message: str) -> Dict:
    return {
        'status': 'error',
        'error': message,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }


class CodeExecutor:
    """Execute code in isolated Docker containers"""
    
    def __init__(self, image_name: str = 'code-sandbox:latest'):
        """
        Initialize code executor
        
        Args:
            image_name: Docker image name for sandbox
        """
        self.image_name = image_name
        self.client = docker.from_env()
    
    def build_image(self, dockerfile_path: str = 'sandbox/Dockerfile') -> bool:
        """
        Build Docker image for sandbox
        
        Args:
            dockerfile_path: Path to Dockerfile
        
        Returns:
            True if build successful, False otherwise
        """
        try:
            logger.info(f"Building Docker image: {self.image_name}")
            self.client.images.build(
                path='.',
                dockerfile=dockerfile_path,
                tag=self.image_name
            )
            logger.info(f"Successfully built image: {self.image_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to build Docker image: {str(e)}")
            return False
    
    def execute_code(self, code: str, language: str, test_input: str = "",
                    expected_output: str = "", timeout: int = 5,
                    memory_limit_mb: int = 256) -> Dict:
        """
        Execute code in Docker container
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript)
            test_input: Input for the code
            expected_output: Expected output
            timeout: Execution timeout in seconds
            memory_limit_mb: Memory limit in megabytes
        
        Returns:
            Dictionary with execution results
        """
        if not isinstance(code, str) or not code.strip():
            return _error_result('Code must be a non-empty string.')
        if len(code) > MAX_CODE_LENGTH:
            return _error_result(f'Code exceeds the {MAX_CODE_LENGTH} character limit.')
        if language not in SUPPORTED_LANGUAGES:
            return _error_result(
                f'Unsupported language. Choose one of: {", ".join(sorted(SUPPORTED_LANGUAGES))}.')
        try:
            timeout = int(timeout)
            memory_limit_mb = int(memory_limit_mb)
        except (TypeError, ValueError):
            return _error_result('Timeout and memory limit must be integers.')
        if not MIN_TIMEOUT_SECONDS <= timeout <= MAX_TIMEOUT_SECONDS:
            return _error_result(
                f'Timeout must be between {MIN_TIMEOUT_SECONDS} and {MAX_TIMEOUT_SECONDS} seconds.')
        if not MIN_MEMORY_MB <= memory_limit_mb <= MAX_MEMORY_MB:
            return _error_result(
                f'Memory limit must be between {MIN_MEMORY_MB} and {MAX_MEMORY_MB} MB.')

        try:
            # Prepare input data
            input_data = {
                'code': code,
                'language': language,
                'input': test_input,
                'expected_output': expected_output or '',
                'timeout': timeout,
                'memory_limit_mb': memory_limit_mb
            }

            sandbox_url = os.getenv('SANDBOX_URL')
            if sandbox_url:
                headers = {'Content-Type': 'application/json'}
                sandbox_token = os.getenv('SANDBOX_TOKEN')
                if sandbox_token:
                    headers['X-Sandbox-Token'] = sandbox_token
                response = requests.post(
                    f"{sandbox_url.rstrip('/')}/execute",
                    json=input_data,
                    headers=headers,
                    timeout=timeout + 5,
                )
                response.raise_for_status()
                result = response.json()
                result['timestamp'] = datetime.now(timezone.utc).isoformat()
                return result
            
            # Run container
            container = self.client.containers.run(
                self.image_name,
                json.dumps(input_data),
                mem_limit=f'{memory_limit_mb}m',
                memswap_limit=f'{memory_limit_mb}m',
                cpu_quota=100000,  # 0.1 CPU
                cpu_period=100000,
                network_disabled=True,
                cap_drop=['ALL'],
                security_opt=['no-new-privileges:true'],
                pids_limit=64,
                read_only=True,
                tmpfs={'/tmp': 'rw,noexec,nosuid,size=16m'},
                timeout=timeout + 5,  # Add buffer
                remove=True
            )
            
            # Parse output
            result = json.loads(container)
            result['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            return result
        
        except docker.errors.ImageNotFound:
            logger.error(f"Docker image not found: {self.image_name}")
            return _error_result('Sandbox image not found. Please build it first.')
        
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def execute_test_cases(self, code: str, language: str, test_cases: List[Dict],
                          timeout: int = 5, memory_limit_mb: int = 256) -> Dict:
        """
        Execute code against multiple test cases
        
        Args:
            code: Code to execute
            language: Programming language
            test_cases: List of test case dictionaries with 'input' and 'expected_output'
            timeout: Execution timeout per test case
            memory_limit_mb: Memory limit in megabytes
        
        Returns:
            Dictionary with results for all test cases
        """
        if not isinstance(test_cases, list):
            return _error_result('Test cases must be provided as a list.')
        if len(test_cases) > MAX_TEST_CASES:
            return _error_result(f'Test case count exceeds the {MAX_TEST_CASES} case limit.')

        results = {
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        for i, test_case in enumerate(test_cases):
            result = self.execute_code(
                code=code,
                language=language,
                test_input=test_case.get('input', ''),
                expected_output=test_case.get('expected_output', ''),
                timeout=timeout,
                memory_limit_mb=memory_limit_mb
            )
            
            result['test_number'] = i + 1
            result['is_hidden'] = test_case.get('is_hidden', False)
            
            results['test_results'].append(result)
            
            if result.get('passed'):
                results['passed_tests'] += 1
            else:
                results['failed_tests'] += 1
        
        # Calculate overall status
        if results['failed_tests'] == 0:
            results['status'] = 'accepted'
        elif results['passed_tests'] > 0:
            results['status'] = 'partial_accepted'
        else:
            results['status'] = 'wrong_answer'
        
        return results
    
    def cleanup(self):
        """Clean up Docker resources"""
        try:
            # Remove dangling containers
            containers = self.client.containers.list(all=True, filters={'status': 'exited'})
            for container in containers:
                if self.image_name in container.image.tags:
                    container.remove()
            
            logger.info("Docker cleanup completed")
        except Exception as e:
            logger.error(f"Docker cleanup failed: {str(e)}")

class SubmissionEvaluator:
    """Evaluate code submissions"""
    
    def __init__(self, executor: CodeExecutor):
        """
        Initialize evaluator
        
        Args:
            executor: CodeExecutor instance
        """
        self.executor = executor
    
    def evaluate_submission(self, submission_id: int, code: str, language: str,
                           test_cases: List[Dict], timeout: int = 5) -> Dict:
        """
        Evaluate a submission
        
        Args:
            submission_id: Submission ID
            code: Code to evaluate
            language: Programming language
            test_cases: Test cases to run
            timeout: Execution timeout
        
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating submission {submission_id}")
        
        # Execute test cases
        results = self.executor.execute_test_cases(
            code=code,
            language=language,
            test_cases=test_cases,
            timeout=timeout
        )
        
        # Add submission info
        results['submission_id'] = submission_id
        results['language'] = language
        
        # Calculate score
        if results['total_tests'] > 0:
            results['score'] = (results['passed_tests'] / results['total_tests']) * 100
        else:
            results['score'] = 0
        
        logger.info(f"Submission {submission_id} evaluation complete: {results['status']}")
        
        return results

# Singleton instance
_executor = None

def get_executor() -> CodeExecutor:
    """Get or create code executor instance"""
    global _executor
    if _executor is None:
        _executor = CodeExecutor()
    return _executor

def get_evaluator() -> SubmissionEvaluator:
    """Get submission evaluator"""
    return SubmissionEvaluator(get_executor())
