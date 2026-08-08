"""
Code Executor Service
Manages Docker containers for secure code execution
"""

import docker
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

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
        try:
            # Prepare input data
            input_data = {
                'code': code,
                'language': language,
                'input': test_input,
                'expected_output': expected_output,
                'timeout': timeout,
                'memory_limit_mb': memory_limit_mb
            }
            
            # Run container
            container = self.client.containers.run(
                self.image_name,
                json.dumps(input_data),
                mem_limit=f'{memory_limit_mb}m',
                memswap_limit=f'{memory_limit_mb}m',
                cpu_quota=100000,  # 0.1 CPU
                cpu_period=100000,
                timeout=timeout + 5,  # Add buffer
                remove=True
            )
            
            # Parse output
            result = json.loads(container)
            result['timestamp'] = datetime.utcnow().isoformat()
            
            return result
        
        except docker.errors.ImageNotFound:
            logger.error(f"Docker image not found: {self.image_name}")
            return {
                'status': 'error',
                'error': f'Sandbox image not found. Please build it first.',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
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
        results = {
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': [],
            'timestamp': datetime.utcnow().isoformat()
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
