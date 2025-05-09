# main.py
import os # to work with files
# import classes and functions from other modules
from grammar import Grammar, parse_grammar_interactively, parse_grammar_from_file
from first_follow import compute_first_sets, compute_follow_sets
from ll1 import build_ll1_table, parse_ll1
from slr1 import build_lr0_items, build_slr1_table, parse_slr1

def main():
    # Print the current Working Directory (to know better the files)
    try:
        current_working_directory = os.getcwd()
        print(f"----- Current Working Directory: {current_working_directory} ---")
    except Exception as e:
        print(f" Could not get current working directory {e}")

    grammar_instance = None # Variable to hold the loaded grammar
    # Loop until a valid grammar is loaded or user quits
    while grammar_instance is None:
        print("\nChoose the grammar input method:")
        print("  A - Read from a file .txt")
        print("  B - Enter interactively")
        print("  C - Quit")
        try:
            user_choice = input("Enter choice (A / B / C): ").strip().upper()

            if user_choice == 'A': #  File as input}
                try:
                    current_working_directory = os.getcwd()
                    print(f"--- your current directory: {current_working_directory} ---")
                    print(f"--- Files(use only .txt): {os.listdir(current_working_directory)} ---")
                except Exception as e:
                    print(f"Warning:  {e}")

                # Loop to get a valid filename
                while True:
                    input_filepath = input("Enter the grammar filename : ").strip()
                    if not input_filepath:
                        print("Filename cannot be empty.")
                        continue
                    try:
                        # Attempt to parse grammar from the specified file
                        grammar_instance = parse_grammar_from_file(input_filepath)
                        print(f"Successfully read grammar from file: {input_filepath}")
                        break # Exit filename loop on success
                    except FileNotFoundError as e: # Handle file not found
                        print(f"{e}")
                        print("Please check the filename and ensure the script is run from the correct directory.")
                    except (ValueError, RuntimeError) as e: # Handle format or other read errors
                        print(f"Error processing file '{input_filepath}': {e}")

                    # trying again
                    retry_input = input("Retry filename??? (Enter V to go back to the menu or anything else to retry): ").strip().upper()
                    if retry_input == 'V':
                         break # Exit filename loop, go back to main menu

            elif user_choice == 'B': # Handle Interactive input
                grammar_instance = parse_grammar_interactively()
                if grammar_instance: print("Grammar entered interactively.")
            elif user_choice == 'C': # Handle Quit
                print("Bye"); return
            else: # Handle invalid choice
                print("Invalid choice.")
        except EOFError: 
            print("\nOperation cancelled"); return

    # -Proceed only if a grammar was successfully loade
    if grammar_instance:
        try:
            #Display the parsed grammar
            print("\n--- Parsed Grammar ---"); print(grammar_instance)

            #Compute and display First sets
            computed_first_sets = compute_first_sets(grammar_instance)
            print("\n----- First Sets -----")
            symbols_to_print_first = sorted(list(grammar_instance.nonterminals) + \
                                            list(grammar_instance.terminals - {'$'}))
            for key in symbols_to_print_first:
                 # Ensure the key exists in the computed sets (it should)
                 if key in computed_first_sets:
                     # Build and sort list of symbols in the set for display
                     display_set_list = []
                     # Include only terminals, nonterminals, or 'e' in the output set
                     for symbol in computed_first_sets[key]:
                         if symbol in grammar_instance.terminals or symbol in grammar_instance.nonterminals or symbol=='e':
                             # exclude '$' from appearing *inside* a FIRST set display
                             if symbol != '$':
                                 display_set_list.append(symbol)
                     display_set_sorted = sorted(display_set_list)
                     print(f"FIRST({key}) = {{{', '.join(display_set_sorted)}}}")

            #Compute and display Follow sets
            computed_follow_sets = compute_follow_sets(grammar_instance, computed_first_sets)
            print("\n----- Follow Sets -----")
            sorted_keys_follow = sorted(list(grammar_instance.nonterminals)) # Sort nonterminals
            for key in sorted_keys_follow:
                 # Get and sort the follow set for display
                 display_set_sorted = sorted(list(computed_follow_sets.get(key, set())))
                 print(f"FOLLOW({key}) = {{{', '.join(display_set_sorted)}}}")

            # Build LL(1) table and report if grammar is LL(1)
            ll1_parsing_table, grammar_is_ll1 = build_ll1_table(grammar_instance, computed_first_sets, computed_follow_sets)
            print(f"\nGrammar is LL(1): {'Yes' if grammar_is_ll1 else 'No'}")

            # Build LR(0) states and SLR(1) table, report if grammar is SLR(1)
            lr0_states_list, lr0_goto_map, augmented_prod_list = build_lr0_items(grammar_instance)
            slr_action_table, slr_goto_table, grammar_is_slr1 = build_slr1_table(grammar_instance, computed_follow_sets, lr0_states_list, lr0_goto_map, augmented_prod_list)
            print(f"Grammar is SLR(1): {'Yes' if grammar_is_slr1 else 'No'}")
            print("-" * 30) # Visual separator

            # --- String Parsing Interaction ---
            if grammar_is_ll1 and grammar_is_slr1:
                while True: # Loop for parser selection
                    print("\nSelect a parser (T: for LL(1), B: for SLR(1), Q: quit):")
                    try:
                        parser_selection_choice = input("> ").strip().upper()
                        selected_parser_name = ""
                        selected_parsing_function =None # Variable to hold the function to call

                        if parser_selection_choice == 'T':
                            selected_parsing_function = parse_ll1
                            selected_parser_name = "LL(1)"
                        elif parser_selection_choice == 'B':
                            selected_parsing_function = parse_slr1
                            selected_parser_name = "SLR(1)"
                        elif parser_selection_choice == 'Q': break # Exit parser selection loop
                        else: print("Invalid choice."); continue

                        # Inner loop for parsing strings with the selected parser
                        print(f"\n--- Using {selected_parser_name} parser ---")
                        print("Enter strings to parse (one per line, empty line to change parser/quit):")
                        while True:
                            string_to_parse = input("Parse> ")
                            if not string_to_parse.strip(): break # Empty line exits string input loop
                            # Call the selected parsing function with correct arguments
                            parsing_result = False # Default result
                            if selected_parser_name == "LL(1)":
                                parsing_result = selected_parsing_function(string_to_parse, grammar_instance, ll1_parsing_table)
                            elif selected_parser_name == "SLR(1)":
                                parsing_result = selected_parsing_function(string_to_parse, grammar_instance, slr_action_table, slr_goto_table)
                            # Print result
                            print("yes" if parsing_result else "no")
                    except EOFError: print("\nExiting."); break 

            elif grammar_is_ll1:
                print("\nGrammar is LL(1).")
                print("--- Using LL(1) parser ---")
                print("Enter strings to parse (one per line, empty line to quit):")
                while True: # Loop for string input
                     try:
                         string_to_parse = input("Parse> ")
                         if not string_to_parse.strip(): break
                         # Direct call to LL(1) parser
                         parsing_result = parse_ll1(string_to_parse, grammar_instance, ll1_parsing_table)
                         print("yes" if parsing_result else "no")
                     except EOFError: print("\nExiting."); break

            elif grammar_is_slr1:
                print("\nGrammar is SLR(1).")
                print("--- Using SLR(1) parser ---")
                print("Enter strings to parse (one per line, empty line to quit):")
                while True: # Loop for string input
                     try:
                         string_to_parse = input("Parse> ")
                         if not string_to_parse.strip(): break
                         # Direct call to SLR(1) parser
                         parsing_result = parse_slr1(string_to_parse, grammar_instance, slr_action_table, slr_goto_table)
                         print("yes" if parsing_result else "no")
                     except EOFError: print("\nExiting."); break

            else:
                print("\nGrammar is neither LL(1) nor SLR(1).")
                print("No parser available.")
                
        except Exception as e:
             print(f"\nAn unexpected error occurred: {e}")
             
if __name__ == "__main__":
    main() #Calling the main function