# first_follow.py
# contains functions to compute first and follow sets.
from grammar import Grammar # import the grammar class definition

def compute_first_sets(grammar_object): 
    """calculates first sets for all grammar symbols."""
    first_sets_dict = dict() # use standard dict: symbol -> set of terminals
    # initialization: first(e) = {e}, first(t) = {t}, first(n) = {}
    first_sets_dict['e'] = {'e'}
    for terminal_symbol in grammar_object.terminals: first_sets_dict[terminal_symbol] = {terminal_symbol}
    for nonterminal_symbol in grammar_object.nonterminals: first_sets_dict[nonterminal_symbol] = set()

    changed_flag = True # flag to control fixed-point iteration
    # repeat until no changes occur in a full pass
    while changed_flag:
        changed_flag = False
        # review each production a -> x1 x2 ... xk
        # iterate over a copy of items in case dict is modified
        for nonterminal_key, production_rhs_list in list(grammar_object.productions_map.items()):
            for rhs_tuple in production_rhs_list:
                # ensure nt key exists in first dict
                if nonterminal_key not in first_sets_dict: first_sets_dict[nonterminal_key] = set()
                original_set_size = len(first_sets_dict[nonterminal_key]) # store current size

                # case: epsilon production a -> e
                if rhs_tuple == ('e',):
                    first_sets_dict[nonterminal_key].add('e')
                # case: non-epsilon production a -> y1 y2 ... yk
                else:
                    can_derive_epsilon_flag = True # assume rhs can derive epsilon
                    # iterate over y1, y2, ...
                    for current_symbol in rhs_tuple:
                        # ensure first(sim) is initialized
                        if current_symbol not in first_sets_dict:
                            if current_symbol in grammar_object.terminals: first_sets_dict[current_symbol] = {current_symbol}
                            elif current_symbol in grammar_object.nonterminals: first_sets_dict[current_symbol] = set()
                            elif current_symbol == 'e': first_sets_dict[current_symbol] = {'e'}
                            else: first_sets_dict[current_symbol] = set() # initialize if unknown

                        first_of_Y = first_sets_dict[current_symbol] # get first(yi)
                        # add first(yi) - {e} to first(a) using a loop
                        for element in first_of_Y:
                            if element != 'e':
                                first_sets_dict[nonterminal_key].add(element)
                        # if yi cannot derive epsilon, stop for this rhs
                        if 'e' not in first_of_Y:
                            can_derive_epsilon_flag = False
                            break
                    # if all yi...yk could derive epsilon, add e to first(a)
                    if can_derive_epsilon_flag:
                        first_sets_dict[nonterminal_key].add('e')

                # check if first(nt) grew
                if len(first_sets_dict[nonterminal_key]) > original_set_size:
                    changed_flag = True # if it grew, another full iteration is needed
    return first_sets_dict

def compute_first_for_string(symbol_sequence_alpha, first_sets_dict, grammar_object):
    """calculates first(alpha) for a sequence alpha = x1 x2 ... xn."""
    result_set = set() # the resulting first set for alpha
    can_derive_epsilon_flag = True # flag: can alpha derive epsilon?
    if symbol_sequence_alpha == ('e',): return {'e'} # base case: first(e) = {e}
    # iterate over symbols x1, x2... in alpha
    for current_symbol in symbol_sequence_alpha:
        # ensure first(sim) is initialized (defensive)
        if current_symbol not in first_sets_dict:
             if current_symbol in grammar_object.terminals: first_sets_dict[current_symbol] = {current_symbol}
             elif current_symbol in grammar_object.nonterminals: first_sets_dict[current_symbol] = set()
             elif current_symbol == 'e': first_sets_dict[current_symbol] = {'e'}
             else: first_sets_dict[current_symbol] = set() # initialize if unknown

        # use .get() for safe access in case symbol was missed
        first_of_Y = first_sets_dict.get(current_symbol, set()) # get first(xi)
        # add first(xi) - {e} to the result set using a loop
        for element in first_of_Y:
            if element != 'e':
                result_set.add(element)
        # if xi cannot derive epsilon, stop
        if 'e' not in first_of_Y:
            can_derive_epsilon_flag = False
            break
    # if all xi could derive epsilon, add e to the result set
    if can_derive_epsilon_flag: result_set.add('e')
    return result_set

def compute_follow_sets(grammar_object, first_sets_dict): 
    """calculates follow sets for all nonterminals."""
    follow_sets_dict = dict() # use standard dict: nonterminal -> set of terminals
    start_sym = grammar_object.start_symbol
    if not start_sym: return follow_sets_dict # cannot compute without start symbol

    # rule 1: add $ to follow(startsymbol)
    follow_sets_dict[start_sym] = {'$'}
    # initialize follow(n) = {} for other nonterminals
    for nonterminal in grammar_object.nonterminals:
        if nonterminal != start_sym: follow_sets_dict[nonterminal] = set()

    changed_flag = True # flag for fixed-point iteration
    # loop until no changes occur
    while changed_flag:
        changed_flag = False
        # review each production b -> alpha
        for head_nonterminal, rhs_tuple in grammar_object.original_productions_list:
            if rhs_tuple == ('e',): continue # ignore a -> e

            # iterate over symbols in rhs: alpha = ... a beta ...
            for i in range(len(rhs_tuple)):
                symbol_A = rhs_tuple[i] # current symbol a being considered
                # only interested if a is a nonterminal
                if symbol_A in grammar_object.nonterminals:
                    # ensure follow(a) exists in the dictionary
                    if symbol_A not in follow_sets_dict: follow_sets_dict[symbol_A] = set()
                    # beta is the sequence following a in this production
                    beta_sequence = rhs_tuple[i+1:]
                    original_set_size = len(follow_sets_dict[symbol_A]) # store current size

                    # rule 2: if b -> alpha a beta (beta is not empty)
                    if beta_sequence:
                        first_of_beta = compute_first_for_string(beta_sequence, first_sets_dict, grammar_object)
                        # add first(beta) - {e} to follow(a) using a loop
                        for element in first_of_beta:
                            if element != 'e':
                                follow_sets_dict[symbol_A].add(element)
                        # rule 3 (part 1): if e is in first(beta)...
                        if 'e' in first_of_beta:
                            # ...add follow(b) to follow(a) using a loop and .get()
                            for element in follow_sets_dict.get(head_nonterminal, set()):
                                follow_sets_dict[symbol_A].add(element)
                    # rule 3 (part 2): if b -> alpha a (beta is empty)
                    else:
                        # add follow(b) to follow(a) using a loop and .get()
                        for element in follow_sets_dict.get(head_nonterminal, set()):
                            follow_sets_dict[symbol_A].add(element)

                    # check if follow(a) grew
                    if len(follow_sets_dict[symbol_A]) > original_set_size:
                        changed_flag = True # need another iteration
    return follow_sets_dict