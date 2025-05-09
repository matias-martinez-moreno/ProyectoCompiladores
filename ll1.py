# ll1.py
# contains functions for building the ll(1) parsing table and the ll(1) parser algorithm.
from grammar import Grammar # needs grammar definition
from first_follow import compute_first_for_string # needs to compute first(rhs)

def build_ll1_table(grammar_object, first_sets_dict, follow_sets_dict): 
    """builds the ll(1) parsing table m[nonterminal][terminal] -> production index."""
    ll1_parsing_table = dict() # use standard dict: {nt: {terminal: index}}
    is_ll1_grammar = True # flag to check if grammar is ll(1)
    conflict_detected = False # flag for conflicts

    # iterate through each production (a -> alpha) with its index
    for production_index, (nonterminal, rhs_tuple) in enumerate(grammar_object.original_productions_list):
        # calculate first(alpha)
        first_of_alpha = compute_first_for_string(rhs_tuple, first_sets_dict, grammar_object)

        # apply rule 1 of algorithm 4.31
        # for each terminal 't' in first(alpha)
        for terminal_symbol in first_of_alpha:
            if terminal_symbol == 'e': continue # epsilon handled by rule 2
            # ensure inner dictionary exists for nt
            if nonterminal not in ll1_parsing_table: ll1_parsing_table[nonterminal] = {}
            # check for conflict: cell already filled with a different production?
            if terminal_symbol in ll1_parsing_table[nonterminal]:
                if ll1_parsing_table[nonterminal][terminal_symbol] != production_index: # conflict detected!
                    is_ll1_grammar=False; conflict_detected=True; ll1_parsing_table[nonterminal][terminal_symbol]='conflict'
            # add production index if no conflict or cell not marked as conflict
            elif ll1_parsing_table[nonterminal].get(terminal_symbol) != 'conflict':
                 ll1_parsing_table[nonterminal][terminal_symbol] = production_index

        # apply rule 2 of algorithm 4.31
        # if epsilon is in first(alpha)
        if 'e' in first_of_alpha:
            # get follow(a)
            follow_of_nonterminal = follow_sets_dict.get(nonterminal, set())
            # for each terminal 'b' (or '$') in follow(a)
            for terminal_symbol in follow_of_nonterminal:
                # ensure inner dictionary exists for nt
                if nonterminal not in ll1_parsing_table: ll1_parsing_table[nonterminal] = {}
                # check for conflict
                if terminal_symbol in ll1_parsing_table[nonterminal]:
                     if ll1_parsing_table[nonterminal][terminal_symbol] != production_index: # conflict detected!
                         is_ll1_grammar=False; conflict_detected=True; ll1_parsing_table[nonterminal][terminal_symbol]='conflict'
                # add production index if no conflict
                elif ll1_parsing_table[nonterminal].get(terminal_symbol) != 'conflict':
                     ll1_parsing_table[nonterminal][terminal_symbol] = production_index

    # grammar is ll(1) only if flag is true and no conflict was explicitly marked
    return ll1_parsing_table, is_ll1_grammar and not conflict_detected

def parse_ll1(input_string, grammar_object, ll1_parsing_table): 
    """performs ll(1) parsing using the table."""
    # convert input string to list of tokens + '$'
    token_list = []
    for char_symbol in input_string.strip(): token_list.append(char_symbol)
    token_list.append('$')

    # initialize stack with '$' and start symbol
    parsing_stack = ['$', grammar_object.start_symbol]
    input_pointer = 0 # input pointer

    # main parser loop
    while len(parsing_stack) > 0: # loop until stack is empty
        stack_top_symbol = parsing_stack[-1] # symbol at stack top
        current_input_token = token_list[input_pointer] if input_pointer < len(token_list) else '$'

        # ignore internal epsilon placeholder if it reaches stack top
        if stack_top_symbol == 'e': parsing_stack.pop(); continue

        # case 1: top is terminal or $
        if stack_top_symbol in grammar_object.terminals or stack_top_symbol == '$':
            if stack_top_symbol == current_input_token: # match!
                parsing_stack.pop() # pop stack
                input_pointer += 1   # advance input
            else: # mismatch -> error
                return False
        # case 2: top is nonterminal
        elif stack_top_symbol in grammar_object.nonterminals:
            # lookup m[top, current] in the table
            table_entry_value = None
            # explicitly check keys before accessing nested dict
            if stack_top_symbol in ll1_parsing_table and current_input_token in ll1_parsing_table[stack_top_symbol]:
                table_entry_value = ll1_parsing_table[stack_top_symbol][current_input_token]

            if table_entry_value is not None: # entry found
                if table_entry_value == 'conflict': return False # error if conflict
                production_index_to_use = table_entry_value # get production index
                parsing_stack.pop() # pop the nonterminal
                nonterminal_head, rhs_tuple = grammar_object.original_productions_list[production_index_to_use] # get production a -> rhs
                # push rhs symbols onto stack in reverse order (if not epsilon)
                if rhs_tuple != ('e',):
                    # use explicit loop to push symbols
                    for i in range(len(rhs_tuple) - 1, -1, -1):
                        parsing_stack.append(rhs_tuple[i])
            else: # no entry in table -> error
                return False
        # case 3: invalid symbol on stack (should not happen)
        else:
            return False # error

    # accept if stack is empty and input pointer reached the end ($ was consumed)
    return input_pointer == len(token_list)