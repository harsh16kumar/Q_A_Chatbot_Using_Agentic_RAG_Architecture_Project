def print_state(state):
    print("\n--- CURRENT STATE ---")
    for k, v in state.items():
        print(f"{k}: {v}")
    print("---------------------\n")
    return state
