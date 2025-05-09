# grammar.py
# defines the grammar class and functions to read/process grammar input.
import os
import sys
from collections import deque # needed for slr1 module

class Grammar: 
    def __init__(self):
        self.nonterminals = set() #  stores nonterminal symbols (e.g., 's')
        self.terminals = set()    # stores terminal symbols (e.g., 'a')
        self.productions_map = dict() #stores productions
        self.start_symbol = None #stores the designated start symbol
        self.productions_list = [] 
        self.original_productions_list = [] 

    def add_production(self, nonterminal_symbol, alternative_string): 
        self.nonterminals.add(nonterminal_symbol)
        # set start symbol if not already set
        if self.start_symbol is None:
            self.start_symbol = nonterminal_symbol

        rhs_symbols_list = [] # temporary list for rhs symbols
        if alternative_string == 'e':
            rhs_symbols_list = ['e'] # internal representation for epsilon
        else:
            allowed_terminals = ['+', '*', '(', ')', '$'] # allowed non-alpha terminals
            # parse rhs string char by char
            for char_symbol in alternative_string:
                if char_symbol.isupper(): # uppercase -> nonterminal
                    rhs_symbols_list.append(char_symbol)
                    self.nonterminals.add(char_symbol)
                elif char_symbol.islower() or char_symbol.isdigit() or char_symbol in allowed_terminals: # lowercase -> terminal
                    rhs_symbols_list.append(char_symbol)
                    self.terminals.add(char_symbol)
                elif char_symbol.isspace(): continue # ignore whitespace
                else: print(f"Warning: Ignoring unrecognized character '{char_symbol}'...", file=sys.stderr) 
        # skip if rhs is empty after parsing (and wasn't 'e')
        if not rhs_symbols_list:
             print(f"Warning: Skipping production {nonterminal_symbol} -> '{alternative_string}'...", file=sys.stderr)
             return

        rhs_tuple = tuple(rhs_symbols_list) # convert to immutable tuple

        # explicitly handle standard dict: initialize list if nt key is new
        if nonterminal_symbol not in self.productions_map:
            self.productions_map[nonterminal_symbol] = []

        # avoid duplicates: add only if this specific rhs tuple doesn't exist for this nt
        if rhs_tuple not in self.productions_map[nonterminal_symbol]:
            self.productions_map[nonterminal_symbol].append(rhs_tuple)
            # add to the ordered list for indexing
            self.productions_list.append((nonterminal_symbol, rhs_tuple))

    def finalize(self):
        """performs final setup after adding all productions."""
        if not self.start_symbol: raise ValueError("Could not determine start symbol.") 
        self.terminals.add('$') # add end-of-input marker
        if 'e' in self.terminals: self.terminals.remove('e') # 'e' is not a real terminal
        # save a stable copy of the production list for indexing
        self.original_productions_list = list(self.productions_list)

    def get_symbols(self):
        """returns the set of all grammar symbols (t u n)."""
        return self.nonterminals.union(self.terminals)

    def __str__(self):
        """provides a readable string representation of the grammar."""
        output_string = "Nonterminals: {}\n".format(sorted(list(self.nonterminals)))
        output_string += "Terminals: {}\n".format(sorted(list(self.terminals - {'e'})))
        output_string += "Start Symbol: {}\n".format(self.start_symbol) 
        output_string += "Productions (indexed):\n" 
        production_list_to_print = getattr(self, 'original_productions_list', self.productions_list) 
        for index, (nonterminal, rhs_tuple) in enumerate(production_list_to_print): 
             rhs_string_representation = ''.join(rhs_tuple) if rhs_tuple != ('e',) else 'e' 
             output_string += f"  {index}: {nonterminal} -> {rhs_string_representation}\n"
        return output_string

def process_production_line(line_text, grammar_object): 
    """parses a single line of production input( "s -> a s b | e")."""
    try:
        parts = line_text.split('->', 1) # split into lhs and rhs
        if len(parts) != 2: return False
        nonterminal = parts[0].strip()
        # basic validation: nt should be a single uppercase letter
        if not nonterminal or not nonterminal.isupper() or len(nonterminal) != 1: return False
        rhs_full_string = parts[1].strip()

        # split rhs alternatives by space
        alternatives_list = [] 
        for alt_string in rhs_full_string.split(' '): 
            if alt_string: # avoid empty strings from multiple spaces
                alternatives_list.append(alt_string)

        if not alternatives_list: return False # no valid alternatives found
        was_anything_added = False 
        # add each found alternative using the grammar's method
        for current_alternative_string in alternatives_list: 
            grammar_object.add_production(nonterminal, current_alternative_string)
            was_anything_added = True
        return was_anything_added
    except Exception:
        return False

def parse_grammar_interactively(): 
    """handles interactive grammar input from the user."""
    grammar_object = Grammar() 
    # get number of nonterminals (determines how many lines to read)
    while True:
        try:
            num_nonterminals_str = input("Enter the number of nonterminals (n > 0): ").strip() 
            if not num_nonterminals_str: continue # ask again if empty
            num_nonterminals = int(num_nonterminals_str) 
            if num_nonterminals <= 0: print("Number must be greater than 0."); continue 
            break # valid number entered
        except ValueError: print("Invalid number.") 
        except EOFError: print("\nOperation cancelled."); return None 

    print(f"Enter {num_nonterminals} grammar production lines (e.g., S -> aS b | e ):") 
    lines_processed_count = 0 
    # read the specified number of production lines
    while lines_processed_count < num_nonterminals:
        try:
            current_line = input(f"Production {lines_processed_count + 1}: ").strip()  
            if current_line:
                # process line and increment count if valid production added
                if process_production_line(current_line, grammar_object):
                    lines_processed_count += 1
            else: print("Production line cannot be empty.") 
        except EOFError: print("\nInput terminated early.", file=sys.stderr); break 

    # finalize and return the grammar object
    try:
        grammar_object.finalize(); return grammar_object
    except ValueError as e: print(f"Error finalizing grammar: {e}", file=sys.stderr); return None 

def parse_grammar_from_file(file_path): 
    """reads grammar from a specified file according to the project format."""
    # check if file exists before opening
    if not os.path.exists(file_path):
        absolute_path = os.path.abspath(file_path) 
        raise FileNotFoundError(f"Error: File not found at relative path '{file_path}' (Absolute path checked: '{absolute_path}')") # Kept English

    grammar_object = Grammar()
    try:
        with open(file_path, 'r') as file_handle: 
            # read first line: number of nonterminals
            try:
                first_line_content = file_handle.readline() 
                if not first_line_content: raise ValueError("File is empty or first line missing.") 
                num_nonterminals = int(first_line_content.strip())
                if num_nonterminals <= 0: raise ValueError("Number of nonterminals must be > 0.") 
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid first line (number of nonterminals): {e}") 

            # read the production lines
            lines_read_count = 0 
            for i, current_line in enumerate(file_handle): 
                if lines_read_count >= num_nonterminals: break # ignore extra lines
                current_line = current_line.strip()
                if current_line: # process non-empty lines
                    if process_production_line(current_line, grammar_object):
                        lines_read_count += 1

            # check if enough valid lines were found
            if lines_read_count < num_nonterminals:
                 print(f"Warning: Expected {num_nonterminals} productions, but only found {lines_read_count}.", file=sys.stderr) # Kept English
                 if lines_read_count == 0: raise ValueError("No valid productions found in the file.") 

    except Exception as e: # catch other file reading/processing errors
        if not isinstance(e, FileNotFoundError):
             raise RuntimeError(f"Error reading grammar file '{file_path}': {e}") 
        else:
             raise 

    # finalize grammar after reading
    grammar_object.finalize()
    return grammar_object