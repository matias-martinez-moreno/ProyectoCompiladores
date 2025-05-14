# first_follow.py
# contains functions to compute first and follow sets.
from grammar import Grammar

def compute_first_sets(grammar_object):
    first_sets_dict = dict()
    first_sets_dict['e'] = {'e'}
    for terminal_symbol in grammar_object.terminals:first_sets_dict[terminal_symbol] ={terminal_symbol}
    for nonterminal_symbol in grammar_object.nonterminals:first_sets_dict[nonterminal_symbol] = set()

    changed_flag = True
    while changed_flag:
        changed_flag = False
        for nonterminal_key, production_rhs_list in list(grammar_object.productions_map.items()):
            for rhs_tuple in production_rhs_list:
                if nonterminal_key not in first_sets_dict: first_sets_dict[nonterminal_key] = set()
                original_set_size = len(first_sets_dict[nonterminal_key])
                if rhs_tuple == ('e',):
                    first_sets_dict[nonterminal_key].add('e')
                else:
                    can_derive_epsilon_flag = True
                    for current_symbol in rhs_tuple:
                        if current_symbol not in first_sets_dict:
                            if current_symbol in grammar_object.terminals: first_sets_dict[current_symbol] = {current_symbol}
                            elif current_symbol in grammar_object.nonterminals:first_sets_dict[current_symbol] = set()
                            elif current_symbol == 'e': first_sets_dict[current_symbol] ={'e'}
                            else: first_sets_dict[current_symbol] = set()

                        first_of_Y = first_sets_dict[current_symbol]
                        for element in first_of_Y:
                            if element != 'e':
                                first_sets_dict[nonterminal_key].add(element)
                        if 'e' not in first_of_Y:
                            can_derive_epsilon_flag = False
                            break
                    if can_derive_epsilon_flag:
                        first_sets_dict[nonterminal_key].add('e')

                if len(first_sets_dict[nonterminal_key]) > original_set_size:
                    changed_flag = True
    return first_sets_dict

def compute_first_for_string(symbol_sequence_alpha, first_sets_dict, grammar_object):
    """calculates first(alpha) for a sequence alpha = x1 x2 ... xn."""
    result_set = set()
    can_derive_epsilon_flag = True
    if symbol_sequence_alpha == ('e',): return {'e'}
    for current_symbol in symbol_sequence_alpha:
        if current_symbol not in first_sets_dict:
             if current_symbol in grammar_object.terminals: first_sets_dict[current_symbol] = {current_symbol}
             elif current_symbol in grammar_object.nonterminals: first_sets_dict[current_symbol] = set()
             elif current_symbol == 'e': first_sets_dict[current_symbol] = {'e'}
             else: first_sets_dict[current_symbol] = set()

        first_of_Y =first_sets_dict.get(current_symbol, set())
        for element in first_of_Y:
            if element != 'e':
                result_set.add(element)
        if 'e' not in first_of_Y:
            can_derive_epsilon_flag = False
            break
    if can_derive_epsilon_flag: result_set.add('e')
    return result_set

def compute_follow_sets(grammar_object, first_sets_dict):
    follow_sets_dict = dict()
    start_sym = grammar_object.start_symbol
    if not start_sym: return follow_sets_dict

    # Initialize: FOLLOW(StartSymbol) = {$}, FOLLOW(OtherNT) = {}
    if start_sym not in follow_sets_dict: 
        follow_sets_dict[start_sym] = set()
    follow_sets_dict[start_sym].add('$')

    for nonterminal in grammar_object.nonterminals:
        if nonterminal not in follow_sets_dict: # Ensure all NTs have an entry
            follow_sets_dict[nonterminal] = set()

    changed_flag = True
    while changed_flag:
        changed_flag = False
        # Iterate through all original productions B -> alpha_head_beta
        for head_nonterminal, rhs_tuple in grammar_object.original_productions_list:
            # For Rule 3, we need FOLLOW(head_nonterminal)
            # Ensure it exists, it should by now if head_nonterminal is start_sym or was on RHS
            if head_nonterminal not in follow_sets_dict:
                follow_sets_dict[head_nonterminal] = set()

            # Iterate through symbols in RHS to find nonterminals
            for i in range(len(rhs_tuple)):
                symbol_B_in_rhs = rhs_tuple[i] #current symbol B in RHS being considered for its FOLLOW set

                if symbol_B_in_rhs in grammar_object.nonterminals:
                    # Ensure FOLLOW(symbol_B_in_rhs) entry exists before trying to get its size
                    if symbol_B_in_rhs not in follow_sets_dict:
                        follow_sets_dict[symbol_B_in_rhs] = set()
                    original_follow_B_size =len(follow_sets_dict[symbol_B_in_rhs])

                    # beta_sequence is the part of RHS after symbol_B_in_rhs
                    beta_sequence = rhs_tuple[i+1:]

                    # Rule 2: For a production A -> alpha B beta_sequence
                    # everything in FIRST(beta_sequence) except epsilon is in FOLLOW(B)
                    if beta_sequence: # If beta_sequence is not empty
                        first_of_beta = compute_first_for_string(beta_sequence, first_sets_dict, grammar_object)
                        added_to_follow_B_from_first_beta = False
                        for terminal_in_first_beta in first_of_beta:
                            if terminal_in_first_beta != 'e':
                                if terminal_in_first_beta not in follow_sets_dict[symbol_B_in_rhs]:
                                    follow_sets_dict[symbol_B_in_rhs].add(terminal_in_first_beta)
                                    added_to_follow_B_from_first_beta = True
                        
                        # Rule 3 (part 1): If epsilon is in FIRST(beta_sequence)
                        # then everything in FOLLOW(A) (head_nonterminal) is in FOLLOW(B)
                        if 'e' in first_of_beta:
                            for terminal_in_follow_head in follow_sets_dict.get(head_nonterminal, set()):
                                if terminal_in_follow_head not in follow_sets_dict[symbol_B_in_rhs]:
                                    follow_sets_dict[symbol_B_in_rhs].add(terminal_in_follow_head)
                                    # No need to set changed_flag here, will be caught by size check
                    # Rule 3 (part 2): For a production A -> alpha B (beta_sequence is empty)
                    # then everything in FOLLOW(A) (head_nonterminal) is in FOLLOW(B)
                    else:
                        for terminal_in_follow_head in follow_sets_dict.get(head_nonterminal,set()):
                            if terminal_in_follow_head not in follow_sets_dict[symbol_B_in_rhs]:
                                follow_sets_dict[symbol_B_in_rhs].add(terminal_in_follow_head)
                                # No need to set changed_flag here, will be caught by size check
                    
                    if len(follow_sets_dict[symbol_B_in_rhs]) > original_follow_B_size:
                        changed_flag =True
    return follow_sets_dict