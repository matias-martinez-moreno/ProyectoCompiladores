# slr1.py
# contains functions for building lr(0) items/states, slr(1) tables, and the slr(1) parser.
from grammar import Grammar
from collections import deque

def closure(initial_item_set,grammar_object,augmented_productions_list):
    closure_set_result =   set(initial_item_set)
    processing_queue =  deque(list(initial_item_set))
    while processing_queue:
        production_index,dot_position = processing_queue.popleft()
        nonterminal_head,rhs_tuple = augmented_productions_list[production_index]
        if dot_position <len(rhs_tuple) and rhs_tuple != ('e',):
            symbol_after_dot = rhs_tuple[dot_position]
            if symbol_after_dot in grammar_object.nonterminals:
                for p_index, (p_nonterminal, _) in enumerate(augmented_productions_list):
                    if p_nonterminal == symbol_after_dot:
                        new_item_to_add = (p_index, 0)
                        if new_item_to_add not in closure_set_result:
                            closure_set_result.add(new_item_to_add)
                            processing_queue.append(new_item_to_add)
    return frozenset(closure_set_result)

def goto(item_set,transition_symbol, grammar_object, augmented_productions_list):
    next_state_kernel_items = set()
    for production_index, dot_position in item_set:
        nonterminal_head, rhs_tuple = augmented_productions_list[production_index]
        if dot_position < len(rhs_tuple) and rhs_tuple != ('e',) and rhs_tuple[dot_position] == transition_symbol:
            next_state_kernel_items.add((production_index,dot_position + 1))
    if not next_state_kernel_items: return frozenset()
    return closure(next_state_kernel_items, grammar_object, augmented_productions_list)

def build_lr0_items(grammar_object):
    augmented_start_symbol = grammar_object.start_symbol + "'"
    augmented_production = (augmented_start_symbol, tuple([grammar_object.start_symbol]))
    augmented_list =[augmented_production] + grammar_object.original_productions_list
    initial_item =(0, 0)
    initial_state_items = closure({initial_item}, grammar_object, augmented_list)
    states_list = [initial_state_items]
    goto_transitions_map ={}
    states_to_process_queue =deque([0])
    found_states_map = {initial_state_items: 0}
    all_grammar_symbols =grammar_object.get_symbols() - {'e'}
    while states_to_process_queue:
        current_state_index =states_to_process_queue.popleft()
        current_item_set =states_list[current_state_index]
        for current_symbol in all_grammar_symbols:
            next_state_item_set = goto(current_item_set, current_symbol, grammar_object, augmented_list)
            if not next_state_item_set: continue
            if next_state_item_set not in found_states_map:
                next_state_index = len(states_list)
                states_list.append(next_state_item_set)
                found_states_map[next_state_item_set] = next_state_index
                states_to_process_queue.append(next_state_index)
                goto_transitions_map[(current_state_index, current_symbol)] = next_state_index
            else:
                goto_transitions_map[(current_state_index, current_symbol)] = found_states_map[next_state_item_set]
    return states_list, goto_transitions_map, augmented_list
#End of build_lr0_items 

def build_slr1_table(grammar_object, follow_sets_dict, lr0_states_list, lr0_goto_map, augmented_productions_list):
    action_table = dict()
    goto_table = dict()
    is_slr1_grammar = True
    conflict_detected = False
    augmented_start_symbol = grammar_object.start_symbol + "'"

    for state_index, current_item_set in enumerate(lr0_states_list):
        for augmented_prod_index, dot_position in current_item_set:
            nonterminal_head, rhs_tuple = augmented_productions_list[augmented_prod_index]
            is_augmented_prod = (augmented_prod_index == 0)
            original_prod_index = augmented_prod_index - 1 if not is_augmented_prod else -1

            if dot_position < len(rhs_tuple) and rhs_tuple != ('e',):
                symbol_after_dot =rhs_tuple[dot_position]
                goto_lookup_key = (state_index, symbol_after_dot)
                if goto_lookup_key in lr0_goto_map:
                    target_state_index = lr0_goto_map[goto_lookup_key]
                    if symbol_after_dot in grammar_object.terminals:
                        action_table_key = (state_index, symbol_after_dot)
                        current_table_action = action_table.get(action_table_key)
                        new_action_tuple = ('shift', target_state_index)
                        if current_table_action and current_table_action != new_action_tuple:
                            is_slr1_grammar=False; conflict_detected=True; action_table[action_table_key]=('error','S/R or S/S Conflict')
                        elif not current_table_action or current_table_action[0] != 'error':
                            action_table[action_table_key] = new_action_tuple
            elif dot_position == len(rhs_tuple) or rhs_tuple == ('e',):
                if is_augmented_prod:
                     action_table_key = (state_index, '$')
                     current_table_action =action_table.get(action_table_key)
                     new_action_tuple =('accept', None)
                     if current_table_action and current_table_action != new_action_tuple:
                         is_slr1_grammar=False; conflict_detected=True; action_table[action_table_key]=('error','Accept Conflict')
                     elif not current_table_action or current_table_action[0] != 'error':
                         action_table[action_table_key] = new_action_tuple
                else:
                    follow_of_A = follow_sets_dict.get(nonterminal_head, set())
                    for lookahead_terminal in follow_of_A:
                        action_table_key =(state_index, lookahead_terminal)
                        current_table_action = action_table.get(action_table_key)
                        new_action_tuple = ('reduce', original_prod_index)
                        if current_table_action and current_table_action != new_action_tuple:
                            is_slr1_grammar=False; conflict_detected=True
                            error_type = 'S/R' if current_table_action[0]=='shift' else 'R/R'
                            action_table[action_table_key]=('error',f'{error_type} Conflict')
                        elif not current_table_action or current_table_action[0] != 'error':
                            action_table[action_table_key] = new_action_tuple

    for (from_state_index, grammar_symbol), to_state_index in lr0_goto_map.items():
        if grammar_symbol in grammar_object.nonterminals:
            goto_table[(from_state_index, grammar_symbol)] = to_state_index

    return action_table, goto_table,is_slr1_grammar and not conflict_detected

def parse_slr1(input_string, grammar_object,action_table_arg, goto_table_arg):
    token_list = []
    for char_symbol in input_string.strip():token_list.append(char_symbol)
    token_list.append('$')

    parsing_stack = [0]
    input_pointer = 0

    while True:
        if not parsing_stack: return False
        current_state = parsing_stack[-1]
        current_input_symbol = token_list[input_pointer] if input_pointer < len(token_list) else '$'
        action_table_key = (current_state, current_input_symbol)
        action_tuple = action_table_arg.get(action_table_key)

        if action_tuple is None: return False

        action_type, action_value = action_tuple[0], action_tuple[1]

        if action_type == 'shift':
            next_state_index = action_value
            parsing_stack.append(current_input_symbol)
            parsing_stack.append(next_state_index)
            input_pointer += 1
        elif action_type == 'reduce':
            production_index = action_value
            nonterminal_head, rhs_tuple = grammar_object.original_productions_list[production_index]
            pop_item_count = 0
            if rhs_tuple != ('e',):
                pop_item_count = len(rhs_tuple) * 2
            
            # Ensure stack has enough elements to pop for states and symbols
            if len(parsing_stack) < pop_item_count: # Should be at least pop_item_count elements to remove
                 return False # Stack underflow if trying to pop more than available
            
            # If pop_item_count is 0 (for A->e), stack remains, previous_state is current_state
            if pop_item_count > 0:
                parsing_stack = parsing_stack[:-pop_item_count]
            
            if not parsing_stack: return False # Should not happen if s0 is always there

            previous_state_index = parsing_stack[-1]
            
            goto_table_key = (previous_state_index, nonterminal_head)
            next_state_index = goto_table_arg.get(goto_table_key)
            
            if next_state_index is None: return False
            
            parsing_stack.append(nonterminal_head)
            parsing_stack.append(next_state_index)
        elif action_type == 'accept':
            return input_pointer == len(token_list) - 1
        elif action_type == 'error':
            return False
        else:
            return False