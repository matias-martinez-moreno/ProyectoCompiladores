# ll1.py
# contains functions for building the ll(1) parsing table and the ll(1) parser algorithm.
from grammar import Grammar
from first_follow import compute_first_for_string

def build_ll1_table(grammar_object, first_sets_dict, follow_sets_dict):
    """builds the ll(1) parsing table m[nonterminal][terminal] -> production index."""
    ll1_parsing_table = dict()
    is_ll1_grammar = True
    conflict_detected = False

    for production_index, (nonterminal, rhs_tuple) in enumerate(grammar_object.original_productions_list):
        first_of_alpha = compute_first_for_string(rhs_tuple, first_sets_dict, grammar_object)

        for terminal_symbol in first_of_alpha:
            if terminal_symbol == 'e': continue
            if nonterminal not in ll1_parsing_table: ll1_parsing_table[nonterminal] = {}
            if terminal_symbol in ll1_parsing_table[nonterminal]:
                if ll1_parsing_table[nonterminal][terminal_symbol] != production_index:
                    is_ll1_grammar=False; conflict_detected=True; ll1_parsing_table[nonterminal][terminal_symbol]='conflict'
            elif ll1_parsing_table[nonterminal].get(terminal_symbol) != 'conflict':
                 ll1_parsing_table[nonterminal][terminal_symbol] = production_index

        if 'e' in first_of_alpha:
            follow_of_nonterminal =follow_sets_dict.get(nonterminal, set())
            for terminal_symbol in follow_of_nonterminal:
                if nonterminal not in ll1_parsing_table: ll1_parsing_table[nonterminal] = {}
                if terminal_symbol in ll1_parsing_table[nonterminal]:
                     if ll1_parsing_table[nonterminal][terminal_symbol] != production_index:
                         is_ll1_grammar=False; conflict_detected=True; ll1_parsing_table[nonterminal][terminal_symbol]='conflict'
                elif ll1_parsing_table[nonterminal].get(terminal_symbol) != 'conflict':
                     ll1_parsing_table[nonterminal][terminal_symbol] = production_index

    return ll1_parsing_table, is_ll1_grammar and not conflict_detected

def parse_ll1(input_string, grammar_object, ll1_parsing_table):
    token_list = []
    for char_symbol in input_string.strip(): token_list.append(char_symbol)
    token_list.append('$')

    parsing_stack = ['$',grammar_object.start_symbol]
    input_pointer =0

    while len(parsing_stack) > 0:
        stack_top_symbol = parsing_stack[-1]
        current_input_token = token_list[input_pointer] if input_pointer < len(token_list) else '$'

        if stack_top_symbol == 'e': parsing_stack.pop(); continue

        if stack_top_symbol in grammar_object.terminals or stack_top_symbol == '$':
            if stack_top_symbol == current_input_token:
                parsing_stack.pop()
                input_pointer += 1
            else:
                return False
        elif stack_top_symbol in grammar_object.nonterminals:
            table_entry_value = None
            if stack_top_symbol in ll1_parsing_table and current_input_token in ll1_parsing_table[stack_top_symbol]:
                table_entry_value = ll1_parsing_table[stack_top_symbol][current_input_token]

            if table_entry_value is not None:
                if table_entry_value == 'conflict': return False
                production_index_to_use = table_entry_value
                parsing_stack.pop()
                nonterminal_head, rhs_tuple = grammar_object.original_productions_list[production_index_to_use]
                if rhs_tuple != ('e',):
                    for i in range(len(rhs_tuple) - 1, -1, -1):
                        parsing_stack.append(rhs_tuple[i])
            else:
                return False
        else:
            return False

    return input_pointer == len(token_list)