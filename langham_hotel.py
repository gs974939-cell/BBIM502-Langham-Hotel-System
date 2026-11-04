import json
from datetime import datetime
from pathlib import Path

STUDENT_ID = "Studentid"
GST_RATE = 0.15
DATA_FILE = Path(f"LHMS_{STUDENT_ID}.txt")
rooms = {}
allocations = {}


def read_integer(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Please enter a valid whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Enter a number of at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Enter a number no greater than {maximum}.")
            continue
        return value


def read_positive_amount(prompt):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Please enter a valid amount.")
            continue
        if value <= 0:
            print("The amount must be greater than zero.")
            continue
        return round(value, 2)


def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def add_rooms():
    print("\nADD ROOMS")
    quantity = read_integer("How many rooms would you like to add? ", 1, 100)
    added = 0
    for position in range(quantity):
        while True:
            number = read_integer(f"Enter room number {position + 1}: ", 1)
            room_key = str(number)
            if room_key in rooms:
                print("That room number already exists. Enter another number.")
                continue
            break
        features = read_text("Enter room features: ")
        rate = read_positive_amount("Enter nightly rate (NZD): ")
        rooms[room_key] = {
            "room_number": number,
            "features": features,
            "nightly_rate": rate,
            "allocated": False,
        }
        added += 1
        print(f"Room {number} was added successfully.")
    print(f"Rooms added in this operation: {added}")
    print(f"Total registered rooms: {len(rooms)}")


def delete_room():
    print("\nDELETE ROOM")
    if not rooms:
        print("No rooms are registered. Add rooms first.")
        return
    number = read_integer("Enter the room number to delete: ", 1)
    room_key = str(number)
    if room_key not in rooms:
        print(f"Room {number} was not found.")
        return
    if rooms[room_key]["allocated"]:
        print(f"Room {number} is allocated and cannot be deleted.")
        return
    del rooms[room_key]
    print(f"Room {number} was deleted successfully.")


def display_rooms():
    print("\nROOM DETAILS")
    if not rooms:
        print("No rooms are registered. Add rooms first.")
        return
    for room_key in sorted(rooms, key=int):
        room = rooms[room_key]
        status = "Allocated" if room["allocated"] else "Available"
        print(
            f"Room {room['room_number']} | Features: {room['features']} | "
            f"Rate: NZD {room['nightly_rate']:.2f} | Status: {status}"
        )
    print(f"Total rooms displayed: {len(rooms)}")


def new_customer_number():
    while True:
        number = read_integer("Enter customer number: ", 1)
        if any(record["customer_number"] == number for record in allocations.values()):
            print("That customer number already has an active allocation.")
            continue
        return number


def allocate_rooms():
    print("\nALLOCATE ROOMS")
    available = [key for key, room in rooms.items() if not room["allocated"]]
    if not available:
        print("No rooms are currently available.")
        return
    print(f"Available rooms: {', '.join(sorted(available, key=int))}")
    quantity = read_integer("How many rooms would you like to allocate? ", 1, len(available))
    completed = 0
    for position in range(quantity):
        while True:
            number = read_integer(f"Select room for booking {position + 1}: ", 1)
            room_key = str(number)
            if room_key not in rooms:
                print("That room is not registered.")
                continue
            if rooms[room_key]["allocated"]:
                print("That room is already allocated. Select an available room.")
                continue
            break
        customer_number = new_customer_number()
        customer_name = read_text("Enter customer name: ")
        nights = read_integer("Enter number of nights: ", 1, 365)
        allocations[room_key] = {
            "room_number": number,
            "customer_number": customer_number,
            "customer_name": customer_name,
            "nights": nights,
            "nightly_rate": rooms[room_key]["nightly_rate"],
            "allocated_at": datetime.now().isoformat(timespec="seconds"),
        }
        rooms[room_key]["allocated"] = True
        completed += 1
        print(f"Room {number} was allocated to {customer_name} successfully.")
    print(f"Successful allocations: {completed}")


def display_allocations():
    print("\nROOM ALLOCATION DETAILS")
    if not allocations:
        print("There are no active room allocations.")
        return
    for room_key in sorted(allocations, key=int):
        record = allocations[room_key]
        print(
            f"Room {record['room_number']} | Customer: {record['customer_name']} | "
            f"Customer ID: {record['customer_number']} | Nights: {record['nights']} | "
            f"Nightly rate: NZD {record['nightly_rate']:.2f} | "
            f"Allocated: {record['allocated_at']}"
        )
    print(f"Active allocations: {len(allocations)}")


def billing_and_deallocate():
    print("\nBILLING AND DE-ALLOCATION")
    if not allocations:
        print("There are no active allocations to bill.")
        return
    display_allocations()
    number = read_integer("Enter the room number to check out: ", 1)
    room_key = str(number)
    if room_key not in allocations:
        print(f"Room {number} has no active allocation.")
        return
    record = allocations[room_key]
    subtotal = round(record["nights"] * record["nightly_rate"], 2)
    tax = round(subtotal * GST_RATE, 2)
    total = round(subtotal + tax, 2)
    print("\nGUEST BILL")
    print(f"Customer: {record['customer_name']}")
    print(f"Room: {number}")
    print(f"Nights: {record['nights']}")
    print(f"Subtotal: NZD {subtotal:.2f}")
    print(f"GST ({GST_RATE * 100:.0f}%): NZD {tax:.2f}")
    print(f"Total due: NZD {total:.2f}")
    del allocations[room_key]
    rooms[room_key]["allocated"] = False
    print(f"Room {number} has been released and is available for the next booking.")


def serializable_state():
    return {
        "student_id": STUDENT_ID,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "rooms": rooms,
        "allocations": allocations,
    }


def save_allocations():
    print("\nSAVE ROOM ALLOCATIONS TO FILE")
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file_handle:
            json.dump(serializable_state(), file_handle, indent=4)
        print(f"Allocation data saved to {DATA_FILE.name}.")
        print("The file was opened, updated, and closed successfully.")
    except OSError as error:
        print(f"The allocation file could not be saved: {error}")


def show_allocations_from_file():
    print("\nDISPLAY ROOM ALLOCATIONS FROM FILE")
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file_handle:
            content = file_handle.read()
        if not content.strip():
            print("The allocation file is empty.")
            return
        saved_data = json.loads(content)
        print(json.dumps(saved_data, indent=4))
        print(f"Displayed saved data from {DATA_FILE.name}.")
    except FileNotFoundError:
        print(f"File {DATA_FILE.name} was not found. Save allocations first.")
    except json.JSONDecodeError:
        print("The allocation file does not contain valid saved data.")
    except OSError as error:
        print(f"The allocation file could not be read: {error}")


def backup_and_clear_file():
    print("\nBACKUP AND CLEAR ALLOCATION FILE")
    try:
        with DATA_FILE.open("r", encoding="utf-8") as source_file:
            content = source_file.read()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_file = DATA_FILE.with_name(f"LHMS_{STUDENT_ID}_Backup_{timestamp}.txt")
        with backup_file.open("a", encoding="utf-8") as backup_handle:
            backup_handle.write(content)
            if content and not content.endswith("\n"):
                backup_handle.write("\n")
        with DATA_FILE.open("w", encoding="utf-8") as source_file:
            source_file.write("")
        print(f"Backup created: {backup_file.name}")
        print(f"The source file {DATA_FILE.name} has been cleared.")
    except FileNotFoundError:
        print(f"File {DATA_FILE.name} was not found. Save allocations first.")
    except OSError as error:
        print(f"The backup operation could not be completed: {error}")


def print_menu():
    print("\n" + "=" * 68)
    print("              LANGHAM HOTEL MANAGEMENT SYSTEM")
    print("=" * 68)
    print("1. Add Rooms")
    print("2. Delete Room")
    print("3. Display Room Details")
    print("4. Allocate Rooms")
    print("5. Display Room Allocation Details")
    print("6. Billing and De-allocation")
    print("7. Save Room Allocation to a File")
    print("8. Display Room Allocation from a File")
    print("9. Back Up and Clear the Allocation File")
    print("0. Exit Application")
    print("=" * 68)


def main():
    print("Welcome to the Langham Hotel Management System.")
    while True:
        print_menu()
        try:
            choice = int(input("Enter menu option (0-9): "))
            if choice == 0:
                print("Thank you for using Langham Hotel Management System.")
                break
            actions = {
                1: add_rooms,
                2: delete_room,
                3: display_rooms,
                4: allocate_rooms,
                5: display_allocations,
                6: billing_and_deallocate,
                7: save_allocations,
                8: show_allocations_from_file,
                9: backup_and_clear_file,
            }
            if choice not in actions:
                print("Invalid menu option. Enter a number from 0 to 9.")
                continue
            actions[choice]()
        except ValueError:
            print("Invalid numeric input. Enter a whole number from 0 to 9.")
        except EOFError:
            print("Input ended. The application is closing safely.")
            break
        except KeyboardInterrupt:
            print("\nApplication interrupted. Closing safely.")
            break
        except FileNotFoundError as error:
            print(f"Required file was not found: {error}")
        except OSError as error:
            print(f"File operation failed: {error}")
        except SyntaxError as error:
            print(f"A syntax-related operation failed: {error}")
        except ZeroDivisionError:
            print("A calculation attempted to divide by zero.")
        except IndexError:
            print("A requested list position was outside the available range.")
        except NameError as error:
            print(f"A required name was not defined: {error}")
        except TypeError as error:
            print(f"An operation received an incorrect data type: {error}")
        except OverflowError:
            print("The calculation exceeded the supported numeric range.")
        except ImportError as error:
            print(f"A required module could not be imported: {error}")
        except Exception as error:
            print(f"An unexpected error occurred: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
