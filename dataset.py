from checkpoint_structure import CheckpointADT
from ollama import chat
from ollama import ChatResponse
import json

test_problems = [
    {
        "num": 1,
        "query": "Factor 6x^2 + 11x - 10, please write out each step. Do it in this format, STEP 1:... , STEP 2: ... , etc",
        "expected": "(2x + 5)(3x - 2)",
        "type": "polynomial"
    },
    {
        "num": 2,
        "query": "Factor x^2 + 2x + 1, please write out each step. Do it in this format, STEP 1:... , STEP 2: ... , etc",
        "expected": "(x+1)(x+1)",
        "type": "polynomial"
    }
    {
        "num": 3,
        "query": "Factor x^2 + 7x + 12, please write out each step. Do it in this format, STEP 1:... , STEP 2: ... , etc",
        "expected": "(x+3)(x+4)",
        "type": "polynomial"
    },
    {
        "num": 4,
        "query": "Find the prime factorization of 5!, please write out each step. Do it in this format, STEP 1:... , STEP 2: ... , etc",
        "expected": "2^3 x 3 x 5",
        "type": "polynomial"
    },
    {
        "num": 5,
        "query": "Factor 2x^2 - 5x - 3, please write out each step. Do it in this format, STEP 1:... , STEP 2: ... , etc",
        "expected": "(2x+1)(x-3)",
        "type": "polynomial"
    }
]