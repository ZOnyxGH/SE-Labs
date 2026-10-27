# Reflection

The supplied handout describes reflection as a deliverable but does not include the four reflection questions it refers to. These responses address four relevant reflection themes from the lab; replace them with the instructor's exact questions if they are provided separately.

### 1. What did static analysis help identify?

The tools found both visible quality issues and security risks without executing the program. Pylint and Flake8 highlighted the shared mutable default, swallowed exception, naming and formatting problems, and unused code. Bandit identified dynamic code execution, a weak PIN hash, predictable randomness, shell execution, and a token-like hard-coded string.

### 2. Which finding mattered most, and why?

The `eval` call was the most concerning because the function accepted an expression string and executed it as Python code. It was unnecessary for the feature: accepting a numeric bonus rate provides the same calculation without allowing arbitrary code execution.

### 3. What was challenging about fixing the findings?

Some findings required preserving the program's purpose while changing its interface or behavior. For example, replacing `eval` meant changing the bonus input from an expression string to a numeric rate. The original handout also points to reflection questions that are not present in its supplied pages, so these answers use themes from the stated objectives.

### 4. How will static analysis affect future work?

I would run these tools during development and before submitting changes. Their output is most useful when interpreted alongside the program's intended behavior: a clean report is valuable, but it does not prove every business rule is correct or that all runtime behavior is safe.
