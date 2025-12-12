import random
import pandas as pd

def test_assignment_logic():
    # Mock data
    participants = [
        {'Name': 'Alice', 'Email': 'alice@example.com', 'Address': 'A1'},
        {'Name': 'Bob', 'Email': 'bob@example.com', 'Address': 'B1'},
        {'Name': 'Charlie', 'Email': 'charlie@example.com', 'Address': 'C1'},
    ]
    
    print("Testing with participants:", [p['Name'] for p in participants])
    
    receivers = participants[:]
    
    # Logic from app.py
    attempts = 0
    while True:
        attempts += 1
        random.shuffle(receivers)
        valid = True
        for i, p in enumerate(participants):
            if p['Email'] == receivers[i]['Email']:
                valid = False
                break
        if valid:
            break
        if attempts > 100:
            print("Failed to find valid assignment in 100 attempts")
            return
            
    print(f"Assignment found in {attempts} attempts:")
    for giver, receiver in zip(participants, receivers):
        print(f"{giver['Name']} -> {receiver['Name']}")
        assert giver['Email'] != receiver['Email']
        
    print("\nSUCCESS: No one is their own Secret Santa.")

if __name__ == '__main__':
    test_assignment_logic()
