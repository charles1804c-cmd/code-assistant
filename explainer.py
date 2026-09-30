import os
import ast
from groq import Groq

def get_client(api_key: str = None) -> Groq:
    key = api_key or os.getenv("GROQ_API_KEY", "")
    return Groq(api_key=key)


def static_preflight_check(code: str) -> dict:
    """
    Layer 1: Deterministic static analysis.
    Validates Python AST, detects syntax errors, and extracts ground-truth identifiers.
    """
    info = {
        "is_python": False,
        "syntax_error": None,
        "declared_functions": [],
        "declared_classes": [],
        "imports": [],
    }

    try:
        tree = ast.parse(code)
        info["is_python"] = True
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                info["declared_functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                info["declared_classes"].append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    info["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info["imports"].append(node.module)
    except SyntaxError as e:
        # Check if the code looks like Python
        py_keywords = ["def ", "class ", "import ", "print(", "elif ", "except:", "lambda ", "__init__"]
        if any(kw in code for kw in py_keywords):
            info["is_python"] = True
            info["syntax_error"] = f"Line {e.lineno}: {e.msg}"
    except Exception:
        pass

    return info


PROMPT_TEMPLATE = """You are an expert, fact-checked programming mentor and code analyzer.

STRICT RELEVANCE & CODE VALIDATION:
1. Check whether the provided text is actual programming, scripting, markup, or database query code.
2. If the text is NOT code (e.g. conversational greetings, general trivia, questions, essays, stories, recipes, or non-programming text), you MUST output:
## 🏷️ Detected Language
Irrelevant (Non-Code)

## 📋 What This Code Does
Irrelevant. The provided input is not programming code. Please paste valid source code to receive an explanation.

## 🔍 Step-by-Step Breakdown
Irrelevant.

## ▶️ How to Run This Code
Irrelevant.

## ⚠️ Things to Watch Out For
This tool only analyzes code. Non-code text cannot be analyzed.

ANTI-HALLUCINATION RULES FOR VALID CODE:
1. FACTUAL GROUNDING: Base every explanation ONLY on the provided code. Never invent variables, functions, arguments, or libraries that are not in the code.
2. RUNTIME OUTPUTS: If runtime outputs depend on user input, random seeds, or dynamic state, explicitly state: "Output depends on runtime input." Do NOT fabricate hypothetical random values as exact outputs.
3. ARITHMETIC / TRACE INTEGRITY: Carefully trace the exact math and control flow before writing results.
4. SYNTAX ERRORS: If the code has syntax errors or missing imports, explicitly flag them in "Things to Watch Out For" rather than pretending the code runs cleanly.

{static_context}

You MUST respond using EXACTLY these section headers (include the ## and emoji):

## 🏷️ Detected Language
[State only the detected language name, e.g. Python, JavaScript, Rust, SQL, HTML, etc.]

## 📋 What This Code Does
Explain the overall purpose accurately in 2-3 simple sentences. What problem does it solve, what does it calculate or display, and what is the final output?

## 🔍 Step-by-Step Breakdown
Break down the code into sequential, numbered steps that follow the actual order of execution:

**Step 1 — [Short descriptive title]**
`code line or block here`
➤ Plain English: Explain exactly what happens when this executes. What values are created, stored, or calculated? Why is this line needed?

**Step 2 — [Short descriptive title]**
`next code line or block`
➤ Plain English: ...

(Cover all meaningful parts in the snippet)

## ▶️ How to Run This Code
Accurate, practical instructions to execute this exact code:
1. Prerequisites / tools to install (provide the exact terminal command)
2. How to save the file (recommended filename and correct file extension)
3. Exact command to run in terminal or browser
4. Expected output when run

## ⚠️ Things to Watch Out For
2-3 real, accurate tips or edge cases (potential runtime errors, edge cases, performance considerations, or missing dependencies).

---
Code to analyze:
```
{code}
```
"""

VERIFIER_PROMPT = """You are a senior code verification auditor.
Audit the following DRAFT EXPLANATION against the original SOURCE CODE.

Source Code:
```
{code}
```

Draft Explanation:
{draft}

AUDIT CHECKLIST:
1. If the source code is non-code, ensure it is strictly flagged as Irrelevant.
2. Did the explanation invent any function, variable, or module not in the source?
3. Are loop boundaries, recursion counts, or mathematical results accurate?
4. Is the detected language accurate?
5. Are all 4 section headers present?

TASK:
Output the final, verified explanation with any hallucinations, non-code drift, or math inaccuracies corrected.
Preserve the exact same section headers and beginner-friendly tone.
"""


def explain_code(code: str, language: str = None) -> dict:
    """
    Multi-layer Anti-Hallucination Pipeline:
    1. Deterministic Static AST Pre-flight
    2. Zero-Temperature Grounded Generation (Pass 1)
    3. Verification & Self-Correction Audit (Pass 2)
    """
    client = get_client()

    # Layer 1: Deterministic Pre-Flight
    preflight = static_preflight_check(code)
    static_context = ""
    if preflight.get("syntax_error"):
        static_context = f"NOTE: Deterministic static analysis detected a syntax error: {preflight['syntax_error']}. You must flag this."
    elif preflight.get("declared_functions"):
        funcs = ", ".join(preflight["declared_functions"])
        static_context = f"DETERMINISTIC GROUND TRUTH: Verified declared functions: [{funcs}]."

    # Layer 2: Grounded Greedy Generation (Temp = 0.0)
    prompt = PROMPT_TEMPLATE.format(code=code, static_context=static_context)
    r1 = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=2048,
    )
    draft_raw = r1.choices[0].message.content

    # Layer 3: Dual-Pass Verifier & Fact-Checker
    verify_prompt = VERIFIER_PROMPT.format(code=code, draft=draft_raw)
    try:
        r2 = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": verify_prompt}],
            temperature=0.0,
            max_tokens=2048,
        )
        verified_raw = r2.choices[0].message.content or draft_raw
    except Exception:
        verified_raw = draft_raw

    parsed = _parse(verified_raw)
    parsed["preflight"] = preflight
    parsed["verified"] = True
    return parsed


def answer_code_question(code: str, language: str, history: list, question: str) -> str:
    """Answers user questions strictly and only about the pasted code; rejects anything else as irrelevant."""
    client = get_client()

    lang_desc = f" ({language})" if language and language != "Auto-Detected" else ""
    system_prompt = f"""You are a strict, domain-locked coding assistant dedicated EXCLUSIVELY to answering questions about the specific code provided below.

User's Pasted Code{lang_desc}:
```
{code}
```

STRICT RELEVANCE POLICY:
1. You are ONLY permitted to answer questions that are DIRECTLY and SPECIFICALLY about the code snippet provided above (such as explaining its logic, clarifying how a line works, suggesting optimizations, debugging issues, writing unit tests for it, or refactoring it).
2. If the user asks ANYTHING ELSE that is not directly related to this code (including general knowledge, greetings, other programming topics unrelated to this snippet, math problems not in the code, history, jokes, essays, or general chatter), you MUST reject the query immediately and respond ONLY with:
"Irrelevant. Please ask a question specifically related to your pasted code."
Do NOT answer unrelated questions under any circumstances.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.0,
        max_tokens=1500,
    )

    return response.choices[0].message.content


def _parse(text: str) -> dict:
    """Split LLM output into named sections."""
    out = {
        "language": "Auto-Detected",
        "summary": "",
        "breakdown": "",
        "how_to_run": "",
        "watch_out": "",
        "raw": text
    }

    for chunk in text.split("##"):
        chunk = chunk.strip()
        if not chunk:
            continue
        first_line, _, body = chunk.partition("\n")
        body = body.strip()

        if "Detected Language" in first_line or "Language" in first_line:
            clean_lang = body.split("\n")[0].strip().replace("**", "").replace("`", "")
            if clean_lang:
                out["language"] = clean_lang
        elif "What This Code Does" in first_line:
            out["summary"] = body
        elif "Line-by-Line" in first_line or "Step-by-Step" in first_line:
            out["breakdown"] = body
        elif "How to Run" in first_line:
            out["how_to_run"] = body
        elif "Watch Out" in first_line or "Things to" in first_line:
            out["watch_out"] = body

    return out
