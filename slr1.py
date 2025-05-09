# slr1.py
# contains functions for building lr(0) items/states, slr(1) tables, and the slr(1) parser.
from grammar import Grammar # needs grammar definition
# note: first_follow needed indirectly for build_slr1_table via follow sets
from collections import deque # deque is efficient for queue operations here

def closure(initial_item_set, grammar_object, augmented_productions_list): 
    """computes the lr(0) closure of a set of items."""
    closure_set_result = set(initial_item_set) # result set, start with kernel items
    processing_queue = deque(list(initial_item_set)) # use deque for efficient queue processing

    # process items until queue is empty
    while processing_queue:
        production_index, dot_position = processing_queue.popleft() # get item
        nonterminal_head, rhs_tuple = augmented_productions_list[production_index] # get production

        # if dot is not at the end and rhs is not epsilon: [a -> alpha . b beta]
        if dot_position < len(rhs_tuple) and rhs_tuple != ('e',):
            symbol_after_dot = rhs_tuple[dot_position] # symbol b
            # if b is a nonterminal, add its productions
            if symbol_after_dot in grammar_object.nonterminals:
                # find all productions b -> gamma
                for p_index, (p_nonterminal, _) in enumerate(augmented_productions_list):
                    if p_nonterminal == symbol_after_dot:
                        new_item_to_add = (p_index, 0) # create item [b -> . gamma]
                        # if new, add to closure set and queue
                        if new_item_to_add not in closure_set_result:
                            closure_set_result.add(new_item_to_add)
                            processing_queue.append(new_item_to_add)
    # return as frozenset (immutable, hashable for dict keys)
    return frozenset(closure_set_result)

def goto(item_set, transition_symbol, grammar_object, augmented_productions_list):
    """computes the goto function goto(i, x)."""
    next_state_kernel_items = set() # kernel items for the next state
    # find all items [a -> alpha . transition_symbol beta] in the current set
    for production_index, dot_position in item_set:
        nonterminal_head, rhs_tuple = augmented_productions_list[production_index]
        # check if dot is not at end and the symbol after dot matches transition_symbol
        if dot_position < len(rhs_tuple) and rhs_tuple != ('e',) and rhs_tuple[dot_position] == transition_symbol:
            # add item with dot moved: [a -> alpha transition_symbol . beta]
            next_state_kernel_items.add((production_index, dot_position + 1))
    # if no transitions found, return empty set
    if not next_state_kernel_items: return frozenset()
    # compute closure of the resulting kernel items to get the full target state
    return closure(next_state_kernel_items, grammar_object, augmented_productions_list)

def build_lr0_items(grammar_object): 
    """builds the canonical collection of lr(0) item sets (states) and the goto map."""
    # 1. augment grammar: add s' -> s
    augmented_start_symbol = grammar_object.start_symbol + "'"
    augmented_production = (augmented_start_symbol, tuple([grammar_object.start_symbol]))
    # full list including augmented prod at index 0
    augmented_list = [augmented_production] + grammar_object.original_productions_list

    # 2. compute initial state i0 = closure({[s' -> . s]})
    initial_item = (0, 0) # item for augmented production
    initial_state_items = closure({initial_item}, grammar_object, augmented_list)

    # 3. build states and goto map iteratively
    states_list = [initial_state_items] # list storing the states (item sets) found
    goto_transitions_map = {} # stores goto transitions: (from_state_idx, symbol) -> to_state_idx
    states_to_process_queue = deque([0]) # queue of state indices to process
    # maps item_set (frozenset) -> state_index for quick lookup of existing states
    found_states_map = {initial_state_items: 0}
    all_grammar_symbols = grammar_object.get_symbols() - {'e'} # symbols for goto transitions

    # process states from the queue
    while states_to_process_queue:
        current_state_index = states_to_process_queue.popleft() # get index of current state
        current_item_set = states_list[current_state_index] # get the item set

        # calculate goto for current state on all symbols
        for current_symbol in all_grammar_symbols:
            next_state_item_set = goto(current_item_set, current_symbol, grammar_object, augmented_list) # calculate target state
            if not next_state_item_set: continue # no transition

            # if the target state is new
            if next_state_item_set not in found_states_map:
                next_state_index = len(states_list) # assign new index
                states_list.append(next_state_item_set) # add to list of states
                found_states_map[next_state_item_set] = next_state_index # register in map
                states_to_process_queue.append(next_state_index) # add new state index to queue
                goto_transitions_map[(current_state_index, current_symbol)] = next_state_index # record goto transition
            # if target state already exists
            else:
                # just record the goto transition to the existing state's index
                goto_transitions_map[(current_state_index, current_symbol)] = found_states_map[next_state_item_set]

    return states_list, goto_transitions_map, augmented_list

def build_slr1_table(grammar_object, follow_sets_dict, lr0_states_list, lr0_goto_map, augmented_productions_list):  
    """builds the slr(1) action and goto tables."""
    action_table = dict() # action table: {(state, terminal): (type, value)}
    goto_table = dict()   # goto table: {(state, nonterminal): state}
    is_slr1_grammar = True # assume slr(1) until conflict
    conflict_detected = False # conflict flag

    augmented_start_symbol = grammar_object.start_symbol + "'"

    # iterate through each lr(0) state
    for state_index, current_item_set in enumerate(lr0_states_list):
        # iterate through each item in the state
        for augmented_prod_index, dot_position in current_item_set:
            nonterminal_head, rhs_tuple = augmented_productions_list[augmented_prod_index] # get production
            is_augmented_prod = (augmented_prod_index == 0) # is it s' -> s . ?
            original_prod_index = augmented_prod_index - 1 if not is_augmented_prod else -1 # index in original grammar list

            # --- determine shift actions ---
            # if item is [a -> alpha . x beta] (dot not at end)
            if dot_position < len(rhs_tuple) and rhs_tuple != ('e',):
                symbol_after_dot = rhs_tuple[dot_position] # symbol x
                goto_lookup_key = (state_index, symbol_after_dot) # key for goto map
                # if there is a goto transition on x from this state
                if goto_lookup_key in lr0_goto_map:
                    target_state_index = lr0_goto_map[goto_lookup_key] # target state j
                    # if x is a terminal, add shift action
                    if symbol_after_dot in grammar_object.terminals:
                        action_table_key = (state_index, symbol_after_dot) # key (state, terminal)
                        current_table_action = action_table.get(action_table_key) # check existing action
                        new_action_tuple = ('shift', target_state_index) # new shift action
                        # check for shift/reduce or shift/shift conflict
                        if current_table_action and current_table_action != new_action_tuple:
                            is_slr1_grammar=False; conflict_detected=True; action_table[action_table_key]=('error','S/R or S/S Conflict') 
                        # add action if no conflict or cell empty/not error
                        elif not current_table_action or current_table_action[0] != 'error':
                            action_table[action_table_key] = new_action_tuple

            # --- determine reduce or accept actions ---
            # if item is [a -> alpha .] (dot at end) or [a -> .] if alpha is e
            elif dot_position == len(rhs_tuple) or rhs_tuple == ('e',):
                # case 1: accept [s' -> s .]
                if is_augmented_prod:
                     action_table_key = (state_index, '$') # accept only on '$' lookahead
                     current_table_action = action_table.get(action_table_key)
                     new_action_tuple = ('accept', None) # new accept action
                     # check for conflict with other actions on '$'
                     if current_table_action and current_table_action != new_action_tuple:
                         is_slr1_grammar=False; conflict_detected=True; action_table[action_table_key]=('error','Accept Conflict') 
                     elif not current_table_action or current_table_action[0] != 'error':
                         action_table[action_table_key] = new_action_tuple
                # case 2: reduce [a -> alpha .] where a != s'
                else:
                    head_nonterminal_A = nonterminal_head # nonterminal a
                    follow_of_A = follow_sets_dict.get(head_nonterminal_A, set()) # get follow(a)
                    # for every terminal 'a' in follow(a)
                    for lookahead_terminal in follow_of_A:
                        action_table_key = (state_index, lookahead_terminal) # key (state, terminal)
                        current_table_action = action_table.get(action_table_key)
                        # reduce using the *original* production index
                        new_action_tuple = ('reduce', original_prod_index)
                        # check for shift/reduce or reduce/reduce conflict
                        if current_table_action and current_table_action != new_action_tuple:
                            is_slr1_grammar=False; conflict_detected=True
                            # determine conflict type for error message
                            error_type = 'S/R' if current_table_action[0]=='shift' else 'R/R'
                            action_table[action_table_key]=('error',f'{error_type} Conflict') 
                        # add action if no conflict
                        elif not current_table_action or current_table_action[0] != 'error':
                            action_table[action_table_key] = new_action_tuple
    # --- fill goto table ---
    # populate goto table using precomputed goto transitions for nonterminals
    for (from_state_index, grammar_symbol), to_state_index in lr0_goto_map.items():
        if grammar_symbol in grammar_object.nonterminals:
            goto_table[(from_state_index, grammar_symbol)] = to_state_index

    # grammar is slr(1) only if no conflicts were detected
    return action_table, goto_table, is_slr1_grammar and not conflict_detected

def parse_slr1(input_string, grammar_object, action_table_arg, goto_table_arg):
    """performs slr(1) parsing using action and goto tables."""
    # prepare input tokens
    token_list = []
    for char_symbol in input_string.strip(): token_list.append(char_symbol)
    token_list.append('$')

    # initialize stack with initial state 0
    parsing_stack = [0]
    input_pointer = 0 # pointer to current input token

    # main slr parsing loop
    while True:
        if not parsing_stack: return False # error if stack becomes empty unexpectedly
        current_state = parsing_stack[-1] # current state is top of stack
        current_input_symbol = token_list[input_pointer] if input_pointer < len(token_list) else '$' # current lookahead symbol
        action_table_key = (current_state, current_input_symbol) # key for action table lookup

        action_tuple = action_table_arg.get(action_table_key) # lookup action

        # no action defined -> syntax error
        if action_tuple is None: return False

        action_type, action_value = action_tuple[0], action_tuple[1] # get action type and value

        # perform action
        if action_type == 'shift':
            # shift action: push terminal and target state onto stack
            next_state_index = action_value
            parsing_stack.append(current_input_symbol) # push terminal
            parsing_stack.append(next_state_index)   # push next state
            input_pointer += 1 # advance input pointer
        elif action_type == 'reduce':
            # reduce action: pop 2*|beta| items, push a and goto state
            production_index = action_value # index of production a -> beta
            # get the production details
            nonterminal_head, rhs_tuple = grammar_object.original_productions_list[production_index]
            pop_item_count = 0 # number of items (state + symbol) to pop
            # calculate pop count (0 for a -> e)
            if rhs_tuple != ('e',): pop_item_count = len(rhs_tuple) * 2

            # check for stack underflow before popping
            if len(parsing_stack) < pop_item_count + 1: return False
            # pop items using slicing
            parsing_stack = parsing_stack[:-pop_item_count]
            if not parsing_stack: return False # stack should not be empty here

            # state exposed after popping
            previous_state_index = parsing_stack[-1]
            # lookup goto[previous_state, a]
            goto_table_key = (previous_state_index, nonterminal_head)
            next_state_index = goto_table_arg.get(goto_table_key) # get target state
            # if no goto entry -> error
            if next_state_index is None: return False
            # push the nonterminal a and the target state
            parsing_stack.append(nonterminal_head) # push nonterminal (lhs) - mainly for debugging/clarity
            parsing_stack.append(next_state_index) # push target state
        elif action_type == 'accept':
            # accept action: success if input pointer is at '$'
            return input_pointer == len(token_list) - 1
        elif action_type == 'error':
            # explicit error entry in table (conflict) -> error
            return False
        else: # unknown action type -> error
            return False