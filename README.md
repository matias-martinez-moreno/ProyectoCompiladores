# LL(1) and SLR(1) Parser Implementation ⚙️
- **STUDENTS**
  - Matías Martínez Moreno
  - Samuel Orozco Valencia
---
> **Referencees:** Aho, Alfred V. et al. Compilers: Principles, Techniques, and Tools (2nd Edition). USA: Addison-Wesley Longman Publishing Co., Inc., 2006. ISBN: 0321486811" 
---
## About this Project 🚀👍
This project implements algorithms in Python to analyze a given CFG and determine its suitability for LL(1) and SLR(1) parsing. It then allows parsing input strings using the appropriate generated parser.
1.  **Grammar Input & Analysis:**
    -   Reads a CFG definition either interactively or from a specified file format.
    -   Calculates the FIRST and FOLLOW sets 
    -   Attempts to build the LL(1) predictive parsing table, detecting any LL(1) conflicts
    -   Attempts to build the LR(0) item sets and the SLR(1) ACTION/GOTO parsing tables, detecting any Shift/Reduce or Reduce/Reduce conflicts.
    -   Reports whether the grammar is LL(1) and/or SLR(1).
2.  **String Parsing:**
    -   If the grammar is both LL(1) and SLR(1), the user can choose which parser to use.
    *   If the grammar is only LL(1) or only SLR(1), the corresponding parser is used automatically.
    *   If the grammar is neither, no parsing is offered.
    -   For each input string, the program outputs `yes` if the string is accepted by the parser (belongs to the language) or `no` otherwise.

---
## Tools Used 💻
- **Operating System:**
  - Windows 11 
- **Programming Language:**
  - Python 3.13.3
- **Required Tools:**
  - Python 3 Interpreter
  - Visual Studio Code (IDE)
  - Command Terminal
- **Libraries Used:**
  - `sys`: For system interaction 
  - `os`: For OS interaction (file paths, directory listing)
  - `collections.deque`: For efficient queue management in LR(0) state construction
---
## Project File Structure 📁

-   **`grammar.py`**: Defines the `Grammar` class and functions for reading/processing grammar input (`parse_grammar_interactively`, `parse_grammar_from_file`).
-   **`first_follow.py`**: Contains functions for computing FIRST and FOLLOW sets (`compute_first_sets`, `compute_follow_sets`, `compute_first_for_string`).
-   **`ll1.py`**: Contains functions for LL(1) table construction (`build_ll1_table`) and parsing (`parse_ll1`).
-   **`slr1.py`**: Contains functions for LR(0) item/state construction (`closure`, `goto`, `build_lr0_items`), SLR(1) table construction (`build_slr1_table`), and parsing (`parse_slr1`).
-   **`main.py`**: The main execution script that imports the other modules,,

---

## How to Run the Project ❓❓❓

1.  **Preparation:**
    -   Place all five `.py` files (`main.py`, `grammar.py`, `first_follow.py`, `ll1.py`, `slr1.py`) in the same directoryy

2.  **Execution:**
    -   Open  Terminal.
    -   Navigate  to the directory containing the source files.
    -   Run the main script using:
        ```bash
        python main.py
        ```

3.  **Interaction:**
    -   **Input Method:** The program will first prompt you to choose the grammar input method:
        -   `A`: Read from a file.
        -   `B`: Enter the grammar by yoursellf.
        -   `C`: Quit.
    -   **Grammar Input:** Follow the prompts either to enter the filename or to enter the grammar line by line.
    -   **Results:** The program will output the parsed grammar details, the computed FIRST and FOLLOW sets, and whether the grammar is LL(1) and/or SLR(1).
    -   **Parsing Strings:** Depending on the analysis results, you will be prompted to enter strings for parsing.
        -   If both parsers are available, you'll first select `T` (LL(1)) or `B` (SLR(1)).
        -   Enter one string per line at the `Parse>` prompt.
        -   An empty line will either let you switch parsers (if applicable) or quit the parsing loop.
        -   The program will output `yes` or `no` for each parsed string.

