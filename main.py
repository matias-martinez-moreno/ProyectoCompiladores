# main.py
# main driver script for the parser project
import sys
import os
# import classes and functions from other modules
from grammar import Grammar, parse_grammar_interactively, parse_grammar_from_file
from first_follow import compute_first_sets, compute_follow_sets
from ll1 import build_ll1_table, parse_ll1
from slr1 import build_lr0_items, build_slr1_table, parse_slr1

def main():
    # try to print the current working directory for context
    try:
        current_working_directory = os.getcwd()
        print(f"Current Working Directory: {current_working_directory} ---")
    except Exception as e:
        print(f"Could not get current working directory: {e}")

    grammar_instance = None
    # loop until a valid grammar is successfully loaded or the user quits
    while grammar_instance is None:
        print("\nChoose grammar input method:")
        print("  A - Read from file")
        print("  B - Enter interactively")
        print("  C - Quit")
        try:
            user_choice =input("Enter choice (A/B/C): ").strip().upper()

            if user_choice == 'A':#read from the file
                try:
                    current_working_directory = os.getcwd()
                    print(f"CWD before asking for filename: {current_working_directory} ---")
                    print(f" Files/Dirs in CWD: {os.listdir(current_working_directory)} ---")
                except Exception as e:
                    print(f"Warning: {e}")
                    #ask for the filename
                while True:
                    input_filepath = input("Enter the grammar filename: ").strip()
                    if not input_filepath:
                        print("Filename cannot be empty.")
                        continue
                    try:
                        # attempt to parse the grammar from the specified file
                        grammar_instance = parse_grammar_from_file(input_filepath)
                        print(f"Successfully read grammar from file: {input_filepath}")
                        break
                    except FileNotFoundError as e:
                        print(f"{e}")
                    except (ValueError, RuntimeError) as e:
                        print(f"Error processing file '{input_filepath}': {e}")
                    # retry entering the filename or go baack
                    retry_input = input("Retry filename? (Enter V to go back, anything else to retry): ").strip().upper()
                    if retry_input == 'V':
                         break

            elif user_choice == 'B': #enter interactively
                grammar_instance = parse_grammar_interactively()
                if grammar_instance: print("Grammar entered interactively.")
            elif user_choice == 'C': #quit
                print("Exiting......."); return
            else:
                print("Invalid choice.")
        except EOFError:
            print("\nOperation cancelled. Exiting."); return
#proceed with analysis
    if grammar_instance:
        try:
            #display the grammar details
            print("\n----- Parsed Grammar -----"); print(grammar_instance)
            #first sets
            computed_first_sets = compute_first_sets(grammar_instance)
            print("\n--- First Sets ---")
            #create a sorted list of symbols
            symbols_to_print_first = sorted(list(grammar_instance.nonterminals) + \
                                            list(grammar_instance.terminals - {'$'}))
            for key in symbols_to_print_first:
                 if key in computed_first_sets:
                     display_set_list = []
                     for symbol in computed_first_sets[key]:
                         if symbol in grammar_instance.terminals or symbol in grammar_instance.nonterminals or symbol=='e':
                             if symbol != '$':#avoid addingg $ to the set
                                 display_set_list.append(symbol)
                     display_set_sorted = sorted(display_set_list)
                     print(f"FIRST({key}) = {{{', '.join(display_set_sorted)}}}")
            #compute follow sets
            computed_follow_sets = compute_follow_sets(grammar_instance, computed_first_sets)
            print("\n---- Follow Sets ----")
            sorted_keys_follow = sorted(list(grammar_instance.nonterminals))#only for nonterminals
            for key in sorted_keys_follow:
                 display_set_sorted = sorted(list(computed_follow_sets.get(key, set())))
                 print(f"FOLLOW({key}) = {{{', '.join(display_set_sorted)}}}")
            #build ll1 table and report if grammar is ll1
            ll1_parsing_table, grammar_is_ll1 = build_ll1_table(grammar_instance, computed_first_sets, computed_follow_sets)
            print(f"\nGrammar is LL(1): {'Yes' if grammar_is_ll1 else 'No'}")
            #lr 0 states and slr1 table
            lr0_states_list, lr0_goto_map, augmented_prod_list = build_lr0_items(grammar_instance)
            slr_action_table, slr_goto_table, grammar_is_slr1 = build_slr1_table(grammar_instance, computed_follow_sets, lr0_states_list, lr0_goto_map, augmented_prod_list)
            print(f"Grammar is SLR(1): {'Yes' if grammar_is_slr1 else 'No'}")
            print("-" * 30)
            #handling the output cases
            if grammar_is_ll1 and grammar_is_slr1:
                while True:
                    print("\nSelect a parser (T: for LL(1), B: for SLR(1), Q: quit):")
                    try:
                        parser_selection_choice = input("> ").strip().upper()
                        selected_parser_name = ""
                        selected_parsing_function = None

                        if parser_selection_choice == 'T':
                            selected_parsing_function = parse_ll1
                            selected_parser_name = "LL(1)"
                        elif parser_selection_choice == 'B':
                            selected_parsing_function = parse_slr1
                            selected_parser_name = "SLR(1)"
                        elif parser_selection_choice == 'Q': break
                        else: print("Invalid choice."); continue

                        print(f"\n--- Using {selected_parser_name} parser ---")
                        print("Enter strings to parse (one per line, empty line to change parser/quit):")
                        while True:
                            string_to_parse = input("Parse> ")
                            if not string_to_parse.strip(): break
                            parsing_result = False
                            if selected_parser_name == "LL(1)":
                                parsing_result = selected_parsing_function(string_to_parse, grammar_instance, ll1_parsing_table)
                            elif selected_parser_name == "SLR(1)":
                                parsing_result = selected_parsing_function(string_to_parse, grammar_instance, slr_action_table, slr_goto_table)
                            print("yes" if parsing_result else "no")
                    except EOFError: print("\nExiting."); break

            elif grammar_is_ll1:
                print("\nGrammar is LL(1).")
                print("--- Using LL(1) parser ---")
                print("Enter strings to parse (one per line, empty line to quit):")
                while True:
                     try:
                         string_to_parse = input("Parse> ")
                         if not string_to_parse.strip(): break
                         parsing_result = parse_ll1(string_to_parse, grammar_instance, ll1_parsing_table)
                         print("yes" if parsing_result else "no")
                     except EOFError: print("\nExiting."); break

            elif grammar_is_slr1:
                print("\nGrammar is SLR(1).")
                print("--- Using SLR(1) parser ---")
                print("Enter strings to parse (one per line, empty line to quit):")
                while True:
                     try:
                         string_to_parse = input("Parse> ")
                         if not string_to_parse.strip(): break
                         parsing_result = parse_slr1(string_to_parse, grammar_instance, slr_action_table, slr_goto_table)
                         print("yes" if parsing_result else "no")
                     except EOFError: print("\nExiting."); break

            else:
                print("\nGrammar is neither LL(1) nor SLR(1).")
                print("No parser available.")        
        except Exception as e:
             print(f"\nAn unexpected error occurred: {e}")
if __name__ == "__main__":
    main()