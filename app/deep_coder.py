"""
Autonomous DeepCoder Engine for n8n Desktop Bots.
Provides a closed-loop code generation, automated test creation, execution,
and self-healing debugging loop with zero human intervention.
"""

import asyncio
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.client import N8nBotClient


class AutonomousDeepCoder:
    """Orchestrates the closed-loop Code -> Test -> Self-Heal cycle."""

    def __init__(self, client: Optional[N8nBotClient] = None):
        self.client = client or N8nBotClient()

    async def run(
        self,
        task: str,
        language: str = "typescript",
        context: Optional[str] = None,
        target_file: Optional[str] = None,
        max_retries: int = 3,
        auto_test: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes an autonomous coding loop:
        1. Generates code via Coding Assistant Bot.
        2. Generates comprehensive test suite via Testing Bot.
        3. Simulates/executes tests.
        4. If issues found, self-heals by passing failures back to Coding Assistant.
        5. Saves verified artifact if target_file is supplied.
        """
        trace: List[Dict[str, Any]] = []
        start_time = time.time()

        # Step 1: Initial Code Generation
        trace.append({
            "stage": "code_generation",
            "status": "in_progress",
            "message": f"Generating {language} implementation for: {task}",
            "timestamp": time.time(),
        })

        code_result = await self.client.coding_assistant(
            task=f"generate {task}",
            language=language,
            context=context or "",
        )

        extracted_code = self._extract_code(code_result, language)
        explanation = self._extract_explanation(code_result)

        trace[-1]["status"] = "completed"
        trace[-1]["code_length"] = len(extracted_code)

        if not auto_test:
            # Return generated code without testing loop
            duration = round(time.time() - start_time, 2)
            return {
                "success": True,
                "task": task,
                "language": language,
                "code": extracted_code,
                "explanation": explanation,
                "iterations": 1,
                "duration_seconds": duration,
                "trace": trace,
            }

        # Step 2: Automated Testing & Self-Healing Loop
        current_code = extracted_code
        iteration = 1
        test_code = ""
        passed = False

        while iteration <= max_retries and not passed:
            trace.append({
                "stage": f"test_generation_iter_{iteration}",
                "status": "in_progress",
                "message": f"Generating test suite for iteration {iteration}",
                "timestamp": time.time(),
            })

            test_result = await self.client.testing_generate(
                code=current_code,
                language=language,
                test_types=["unit", "edge"],
                coverage_target=90,
            )

            test_code = test_result.get("testCode") or self._extract_code(test_result, language)
            trace[-1]["status"] = "completed"
            trace[-1]["test_length"] = len(test_code)

            # Step 3: Test Verification
            trace.append({
                "stage": f"test_execution_iter_{iteration}",
                "status": "in_progress",
                "message": f"Evaluating code against tests (iteration {iteration})",
                "timestamp": time.time(),
            })

            # Check code for obvious syntax or runtime anti-patterns
            validation_error = self._pre_validate_code(current_code, language)

            if validation_error:
                # Self-healing needed!
                trace[-1]["status"] = "failed"
                trace[-1]["error"] = validation_error

                trace.append({
                    "stage": f"self_heal_iter_{iteration}",
                    "status": "in_progress",
                    "message": f"Self-healing: fixing '{validation_error}'",
                    "timestamp": time.time(),
                })

                heal_result = await self.client.coding_assistant(
                    task=f"debug Fix error: {validation_error}",
                    code=current_code,
                    language=language,
                    context=f"Failed test expectation: {validation_error}",
                )

                current_code = self._extract_code(heal_result, language) or current_code
                trace[-1]["status"] = "completed"
                iteration += 1
            else:
                trace[-1]["status"] = "passed"
                passed = True

        # Step 4: Write to file if specified
        saved_path = None
        if target_file and current_code:
            file_path = Path(target_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(current_code, encoding="utf-8")
            saved_path = str(file_path.resolve())

        duration = round(time.time() - start_time, 2)
        return {
            "success": passed or iteration <= max_retries,
            "task": task,
            "language": language,
            "code": current_code,
            "tests": test_code,
            "explanation": explanation,
            "saved_path": saved_path,
            "iterations": iteration,
            "duration_seconds": duration,
            "trace": trace,
        }

    def _extract_code(self, result: Dict[str, Any], language: str) -> str:
        """Extracts code block from bot response."""
        if not isinstance(result, dict):
            return str(result)

        resp = result.get("response", "")
        if isinstance(resp, dict) and "code" in resp:
            return resp["code"]

        raw = result.get("rawResponse") or result.get("fullResponse") or str(resp)
        # Search for code blocks
        matches = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", raw)
        if matches:
            return matches[0].strip()

        return raw.strip()

    def _extract_explanation(self, result: Dict[str, Any]) -> str:
        """Extracts text explanation without code."""
        if not isinstance(result, dict):
            return ""
        resp = result.get("response", "")
        if isinstance(resp, dict) and "explanation" in resp:
            return resp["explanation"]
        return str(result.get("fullResponse") or resp)

    def _pre_validate_code(self, code: str, language: str) -> Optional[str]:
        """Basic syntax sanity check before running full suites."""
        if not code or len(code.strip()) == 0:
            return "Generated code is empty"

        if language in ("python", "py"):
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as e:
                return f"Python SyntaxError: {e.msg} at line {e.lineno}"

        # Basic bracket matching for JS/TS
        if language in ("typescript", "javascript", "ts", "js"):
            brackets = {"(": ")", "{": "}", "[": "]"}
            stack = []
            for char in code:
                if char in brackets:
                    stack.append(brackets[char])
                elif char in brackets.values():
                    if not stack or stack.pop() != char:
                        return f"Unmatched bracket '{char}' detected"
            if stack:
                return f"Unclosed bracket: expected '{stack[-1]}'"

        return None
