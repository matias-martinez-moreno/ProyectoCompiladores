# grammar.py
# defines the grammar class and functions to read/process grammar input.
import sys
import os
from collections import deque

class Grammar:
    def __init__(self):
        #initializing
        self.nonterminals = set()
        self.terminals = set()
        self.productions_map = dict()
        self.start_symbol = None
        self.productions_list = []
        self.original_productions_list = []

    def add_production(self, nonterminal_symbol, alternative_string):
        self.nonterminals.add(nonterminal_symbol)
        if self.start_symbol is None:
            self.start_symbol = nonterminal_symbol

        rhs_symbols_list = []
        if alternative_string == 'e':
            rhs_symbols_list = ['e']
        else:
            allowed_terminals = ['+', '*', '(', ')', '$']
            for char_symbol in alternative_string:
                if char_symbol.isupper():
                    rhs_symbols_list.append(char_symbol)
                    self.nonterminals.add(char_symbol)
                elif char_symbol.islower() or char_symbol.isdigit() or char_symbol in allowed_terminals:
                    rhs_symbols_list.append(char_symbol)
                    self.terminals.add(char_symbol)
                elif char_symbol.isspace(): continue
                else: print(f"Warning: '{char_symbol}'...", file=sys.stderr)
        if not rhs_symbols_list:
             print(f"Warning: Skipping production {nonterminal_symbol} -> '{alternative_string}'...", file=sys.stderr)
             return

        rhs_tuple = tuple(rhs_symbols_list)

        if nonterminal_symbol not in self.productions_map:
            self.productions_map[nonterminal_symbol] = []
        if rhs_tuple not in self.productions_map[nonterminal_symbol]:
            self.productions_map[nonterminal_symbol].append(rhs_tuple)
            self.productions_list.append((nonterminal_symbol, rhs_tuple))

    def finalize(self):
        if not self.start_symbol: raise ValueError("Could not determine start symbol.")
        self.terminals.add('$')
        if 'e' in self.terminals: self.terminals.remove('e')
        self.original_productions_list = list(self.productions_list)

    def get_symbols(self):
        #returns the set of all grammar symbols (t u n)
        return self.nonterminals.union(self.terminals)

    def __str__(self):
        #outputs the grammar
        output_string = "Nonterminals: {}\n".format(sorted(list(self.nonterminals)))
        output_string += "Terminals: {}\n".format(sorted(list(self.terminals - {'e'})))
        output_string += "Start Symbol: {}\n".format(self.start_symbol)
        output_string += "Productions (indexed):\n"
        production_list_to_print = getattr(self,'original_productions_list', self.productions_list)
        for index, (nonterminal, rhs_tuple) in enumerate(production_list_to_print):
             rhs_string_representation = ''.join(rhs_tuple) if rhs_tuple != ('e',) else 'e'
             output_string += f"  {index}: {nonterminal} -> {rhs_string_representation}\n"
        return output_string

def process_production_line(line_text, grammar_object):
    try:
        parts =line_text.split('->', 1)
        if len(parts) != 2:return False
        nonterminal = parts[0].strip()
        if not nonterminal or not nonterminal.isupper() or len(nonterminal) != 1: return False
        rhs_full_string = parts[1].strip()

        alternatives_list = []
        for alt_string in rhs_full_string.split(' '):
            if alt_string:
                alternatives_list.append(alt_string)

        if not alternatives_list: return False
        was_anything_added = False
        for current_alternative_string in alternatives_list:
            grammar_object.add_production(nonterminal, current_alternative_string)
            was_anything_added = True
        return was_anything_added
    except Exception:
        return False

def parse_grammar_interactively():
    grammar_object = Grammar()
    while True:
        try:
            num_nonterminals_str = input("Enter the number of nonterminals (n > 0): ").strip()
            if not num_nonterminals_str: continue
            num_nonterminals = int(num_nonterminals_str)
            if num_nonterminals <= 0: print("Number must be greater than 0."); continue
            break
        except ValueError: print("Invalid number.")
        except EOFError: print("\nOperation cancelled."); return None

    print(f"Enter {num_nonterminals} grammar production lines (e.g., S -> aS b | e ):")
    lines_processed_count = 0
    while lines_processed_count < num_nonterminals:
        try:
            current_line = input(f"Production {lines_processed_count + 1}: ").strip()
            if current_line:
                if process_production_line(current_line, grammar_object):
                    lines_processed_count += 1
            else: print("Production line cannot be empty.")
        except EOFError: print("\nInput terminated early.", file=sys.stderr); break

    try:
        grammar_object.finalize(); return grammar_object
    except ValueError as e: print(f"Error finalizing grammar: {e}", file=sys.stderr); return None

def parse_grammar_from_file(file_path):
    if not os.path.exists(file_path):
        absolute_path = os.path.abspath(file_path)
        raise FileNotFoundError(f"Error: File not found at relative path '{file_path}' (Absolute path checked: '{absolute_path}')")

    grammar_object = Grammar()
    try:
        with open(file_path, 'r') as file_handle:
            try:
                first_line_content = file_handle.readline()
                if not first_line_content: raise ValueError("File is empty or first line missing.")
                num_nonterminals = int(first_line_content.strip())
                if num_nonterminals <= 0: raise ValueError("Number of nonterminals must be > 0.")
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid first line (number of nonterminals): {e}")

            lines_read_count = 0
            for i, current_line in enumerate(file_handle):
                if lines_read_count >= num_nonterminals: break
                current_line = current_line.strip()
                if current_line:
                    if process_production_line(current_line, grammar_object):
                        lines_read_count += 1

            if lines_read_count < num_nonterminals:
                 print(f"Warning: Expected {num_nonterminals} productions, but only found {lines_read_count}.", file=sys.stderr)
                 if lines_read_count == 0: raise ValueError("No valid productions found in the file.")

    except Exception as e:
        if not isinstance(e,FileNotFoundError):
             raise RuntimeError(f"Error reading grammar file '{file_path}': {e}")
        else:
             raise

    grammar_object.finalize()
    return grammar_object