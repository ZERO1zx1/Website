"""
Submission Evaluator Service
Evaluates code submissions and manages results
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.db import db
from backend.services.code_executor import SubmissionEvaluator, get_executor

logger = logging.getLogger(__name__)

_DATABASE_STATUS = {
    'accepted': 'accepted',
    'partial_accepted': 'partial_accepted',
    'wrong_answer': 'rejected',
    'rejected': 'rejected',
    'error': 'error',
    'pending': 'pending',
    'running': 'running',
}

class SubmissionProcessor:
    """Process and evaluate code submissions"""
    
    def __init__(self):
        self.evaluator = SubmissionEvaluator(get_executor())
    
    def process_submission(self, submission_id: int, user_id: int, problem_id: int,
                          code: str, language: str = 'python') -> Dict:
        """
        Process a code submission
        
        Args:
            submission_id: Submission ID
            user_id: User ID
            problem_id: Problem ID
            code: Code to evaluate
            language: Programming language
        
        Returns:
            Evaluation results
        """
        try:
            logger.info(f"Processing submission {submission_id}")
            
            # Get problem and test cases
            problem = db.get_problem(problem_id)
            if not problem:
                results = {'submission_id': submission_id, 'status': 'error', 'message': 'Problem not found'}
                self.store_results(submission_id, results)
                return results
            
            # Get test cases
            test_cases = db.get_test_cases(problem_id, include_hidden=True)
            if not test_cases:
                results = {'submission_id': submission_id, 'status': 'error', 'message': 'No test cases found'}
                self.store_results(submission_id, results)
                return results
            
            # Evaluate submission using the problem's language unless explicitly supplied.
            results = self.evaluator.evaluate_submission(
                submission_id=submission_id,
                code=code,
                language=language or problem.get('language', 'python'),
                test_cases=test_cases
            )
            
            # Store results in database
            self.store_results(submission_id, results)
            
            # Update mastery
            self.update_mastery(user_id, problem_id, results)
            
            logger.info(f"Submission {submission_id} processed successfully")
            
            return results
        
        except Exception:
            logger.exception("Failed to process submission %s", submission_id)
            results = {
                'submission_id': submission_id,
                'status': 'error',
                'message': 'Submission evaluation failed'
            }
            self.store_results(submission_id, results)
            return results
    
    def store_results(self, submission_id: int, results: Dict):
        """Store evaluation results in database"""
        try:
            # Store overall submission result using the database constraint vocabulary.
            status = _DATABASE_STATUS.get(results.get('status'), 'error')
            db.client.table('submissions').update({
                'status': status,
                'score': max(0, min(100, float(results.get('score', 0) or 0))),
                'evaluated_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', submission_id).execute()
            
            # Store individual test results
            for test_result in results.get('test_results', []):
                db.client.table('submission_results').insert({
                    'submission_id': submission_id,
                    'test_number': test_result.get('test_number'),
                    'status': test_result.get('status'),
                    'passed': test_result.get('passed', False),
                    'actual_output': test_result.get('actual_output'),
                    'expected_output': test_result.get('expected_output'),
                    'error': test_result.get('error'),
                    'is_hidden': test_result.get('is_hidden', False)
                }).execute()
            
            logger.info(f"Results stored for submission {submission_id}")
        
        except Exception as e:
            logger.error(f"Failed to store results: {str(e)}")
    
    def update_mastery(self, user_id: int, problem_id: int, results: Dict):
        """Update user mastery based on submission results"""
        try:
            score = results.get('score', 0)
            status = results.get('status')
            
            # Get problem skills
            problem_skills = db.client.table('problem_skills').select('*').eq('problem_id', problem_id).execute()
            
            if not problem_skills.data:
                logger.warning(f"No skills associated with problem {problem_id}")
                return
            
            # Calculate mastery increase based on score and status
            mastery_increase = 0
            
            if status == 'accepted':
                mastery_increase = 10  # Full points for accepted
            elif status == 'partial_accepted':
                mastery_increase = (score / 100) * 5  # Partial points
            else:
                mastery_increase = 0  # No points for wrong answer
            
            # Update mastery for each skill
            for skill_link in problem_skills.data:
                skill_id = skill_link['skill_id']
                
                # Get current mastery
                mastery_records = db.client.table('mastery_snapshots').select('*').eq(
                    'user_id', user_id
                ).eq('skill_id', skill_id).execute()
                
                current_score = 0
                if mastery_records.data:
                    current_score = mastery_records.data[0].get('mastery_score', 0)
                
                # Update mastery (cap at 100)
                new_score = min(100, current_score + mastery_increase)
                
                # Upsert mastery record
                db.client.table('mastery_snapshots').upsert({
                    'user_id': user_id,
                    'skill_id': skill_id,
                    'mastery_score': new_score,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }).execute()
                
                logger.info(f"Updated mastery for user {user_id}, skill {skill_id}: {new_score}")
        
        except Exception as e:
            logger.error(f"Failed to update mastery: {str(e)}")
    
    def get_submission_feedback(self, submission_id: int) -> Dict:
        """Get feedback for a submission"""
        try:
            submission = db.get_submission(submission_id)
            if not submission:
                return {'error': 'Submission not found'}
            
            # Get test results
            results = db.client.table('submission_results').select('*').eq(
                'submission_id', submission_id
            ).execute()
            
            # Get teacher feedback if available
            feedback = db.client.table('teacher_feedback').select('*').eq(
                'submission_id', submission_id
            ).execute()
            
            # Generate AI feedback if available
            ai_feedback = self.generate_ai_feedback(submission, results.data)
            
            return {
                'submission': submission,
                'test_results': results.data if results.data else [],
                'teacher_feedback': feedback.data if feedback.data else [],
                'ai_feedback': ai_feedback
            }
        
        except Exception as e:
            logger.error(f"Failed to get feedback: {str(e)}")
            return {'error': str(e)}
    
    def generate_ai_feedback(self, submission: Dict, test_results: List) -> Optional[str]:
        """Generate AI feedback for a submission"""
        try:
            # Placeholder for AI feedback generation
            # In production, this would call an LLM API
            
            passed_tests = len([t for t in test_results if t.get('passed')])
            total_tests = len(test_results)
            
            if passed_tests == total_tests:
                return "Great job! All tests passed. Consider optimizing your solution for better performance."
            elif passed_tests > 0:
                return f"Good progress! You passed {passed_tests}/{total_tests} tests. Review the failing tests to improve."
            else:
                return "Keep trying! Review the problem statement and test cases to understand what's expected."
        
        except Exception as e:
            logger.error(f"Failed to generate AI feedback: {str(e)}")
            return None

# Singleton instance
_processor = None

def get_processor() -> SubmissionProcessor:
    """Get or create submission processor instance"""
    global _processor
    if _processor is None:
        _processor = SubmissionProcessor()
    return _processor
