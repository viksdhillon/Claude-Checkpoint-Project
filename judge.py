from ollama import chat

class Judge:
    def __init__(self):
        self.judges = {
            'F': {
                'name': 'factorization',
                'model': 'llama3.2:3b',
                'system_prompt': 'You are a factorization specialist. Factor polynomials step-by-step.',
                'verify_prompt': 'You verify factorization by expanding factors.',
                'verification_hint': 'Expand the factors to verify.'
            },
            'C': {
                'name': 'calculus',
                'model': 'llama3.2:3b',
                'system_prompt': 'You are a calculus specialist. Solve derivatives, integrals, and limits step-by-step.',
                'verify_prompt': 'You verify calculus by applying inverse operations.',
                'verification_hint': 'Apply the inverse operation to verify.'
            },
            'E': {
                'name': 'elementary',
                'model': 'llama3.2:1b',
                'system_prompt': 'You are an elementary math teacher. Solve basic arithmetic clearly.',
                'verify_prompt': 'You verify arithmetic by using inverse operations.',
                'verification_hint': 'Use the inverse operation to check.'
            },
            'N': {
                'name': 'general',
                'model': 'llama3.2:3b',
                'system_prompt': 'You are a general math expert. Solve problems step-by-step.',
                'verify_prompt': 'You verify answers by checking logic and substitution.',
                'verification_hint': 'Check by substitution or logical verification.'
            }
        }

        self.router_model = 'llama3.2:3b'

    def classify(self, problem):
        response = chat(
            model=self.router_model,
            messages=[{'role': 'user', 'content':f'Classify: {problem}\nF=Factorization, C=Calculus, E=Elementary, N=general\nReply with ONE letter (F, C, E, N)'}]
        )
        result = response['message']['content'].strip().upper()

        if 'F' in result:
            return 'F'
        elif 'C' in result:
            return 'C'
        elif 'E' in result:
            return 'E'
        else:
            return 'N'

    def solve(self, problem, judge_type=None):
        if judge_type is None:
            judge_type = self.classify(problem)
        
        config = self.judges[judge_type]
        response = chat(
            model=config['model'],
            messages=[
                {'role': 'system', 'content':config['system_prompt']},
                {'role': 'user', 'content':f'Solve: {problem}'}
            ]
        )

        return {
            'answer': response['message']['content'],
            'judge_type': config['name']
        }

    def verify(self, solver_answer, actual_answer, judge_type):
        config = self.judges[judge_type]
        response = chat(
            model = config['model'],
            messages=[
                {'role': 'system', 'content': config['system_prompt']},
                {'role': 'user', 'content': f'Actual answer: {actual_answer}\nSolver answer: {solver_answer}\n REPLY WITH: CORRECT or INCORRECT?'}
            ]
        )
        return 'CORRECT' in response['message']['content'].upper()

    def generate_verification(self,problem, answer,judge_type):
        config = self.judges[judge_type]
        response = chat(
            model=config['model'],
            messages = [
                {'role': 'system', 'content': config['system_prompt']},
                {'role': 'user', 'content': f'The problem is {problem}\n. The answer: {answer}.\n Generate ONE verification question to ask the smaller llm, so it can check understanding and evaluate if it has gone wrong. Be precise and clear.'}
            ]
        )

        return response['message']['content']