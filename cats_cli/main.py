from pymongo import MongoClient
from contextlib import contextmanager
from functools import wraps
from colorama import Fore, Style, init

init(autoreset=True)


def is_valid_number(value):
    return value.isdigit()


def error_catcher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"{Fore.RED}Error: Invalid value provided. {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")

    return wrapper


def validate_input(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if "name" in kwargs and not kwargs["name"].strip():
                print(f"{Fore.YELLOW}Name cannot be empty.{Style.RESET_ALL}")
                return

            if "new_age" in kwargs and (
                not kwargs["new_age"] or not is_valid_number(kwargs["new_age"])
            ):
                print(
                    f"{Fore.YELLOW}Invalid input: Age must be a valid number.{Style.RESET_ALL}"
                )
                return

            if "age" in kwargs and (
                not kwargs["age"] or not is_valid_number(kwargs["age"])
            ):
                print(
                    f"{Fore.YELLOW}Invalid input: Age must be a valid number.{Style.RESET_ALL}"
                )
                return

            if "feature" in kwargs and not kwargs["feature"].strip():
                print(f"{Fore.YELLOW}Feature cannot be empty.{Style.RESET_ALL}")
                return

            return func(*args, **kwargs)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    return wrapper


@contextmanager
def create_connection(uri, db_name):
    client = None
    db = None
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print(
            f"{Fore.GREEN}Connected to MongoDB at {uri}, using database: {db_name}{Style.RESET_ALL}"
        )
        yield db
    except Exception as e:
        print(f"{Fore.RED}Error connecting to MongoDB: {e}{Style.RESET_ALL}")
        yield None
    finally:
        if client:
            client.close()
            print(f"{Fore.GREEN}MongoDB connection closed.{Style.RESET_ALL}")


class CatDatabaseManager:
    def __init__(self, uri, db_name, collection_name):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name

    @validate_input
    @error_catcher
    def insert_document(self, db, name, age, features_input):
        collection = db[self.collection_name]
        features = [
            feature.strip() for feature in features_input.split(",") if feature.strip()
        ]
        document = {"name": name, "age": int(age), "features": features}
        collection.insert_one(document)
        return f"🐈 {Fore.GREEN}name:{Style.RESET_ALL} {document['name']}, {Fore.GREEN}age:{Style.RESET_ALL} {document['age']}, {Fore.GREEN}features:{Style.RESET_ALL} {document['features']}"

    @validate_input
    @error_catcher
    def read_document(self, db, name):
        collection = db[self.collection_name]
        cat = collection.find_one({"name": name})
        if cat is None:
            return f"{Fore.RED}Cat not found{Style.RESET_ALL}"
        return f"🐈 {Fore.GREEN}name:{Style.RESET_ALL} {cat['name']}, {Fore.GREEN}age:{Style.RESET_ALL} {cat['age']}, {Fore.GREEN}features:{Style.RESET_ALL} {cat['features']}"

    @error_catcher
    def get_all_documents(self, db):
        collection = db[self.collection_name]
        result_list = []
        for document in collection.find({}):
            if document is not None:
                result_list.append(
                    {
                        "name": document.get("name"),
                        "age": document.get("age"),
                        "features": document.get("features"),
                    }
                )
        return result_list

    @validate_input
    @error_catcher
    def update_cat_age(self, db, name, new_age):
        collection = db[self.collection_name]
        result = collection.update_one({"name": name}, {"$set": {"age": int(new_age)}})
        if result.modified_count > 0:
            return f"{Fore.GREEN}Age of {name} 🐈 updated to {new_age}."
        else:
            return f"{Fore.RED}Cat with name {name} not found or no update necessary."

    @validate_input
    @error_catcher
    def append_cat_feature(self, db, name, new_feature):
        collection = db[self.collection_name]
        result = collection.update_one(
            {"name": name}, {"$addToSet": {"features": new_feature}}
        )
        if result.modified_count > 0:
            return f"{Fore.GREEN}Feature '{new_feature}' added to {name}."
        else:
            return f"{Fore.RED}Cat with name '{name}' not found or feature '{new_feature}' already exists."

    @validate_input
    @error_catcher
    def delete_cat_by_name(self, db, name):
        collection = db[self.collection_name]
        result = collection.delete_one({"name": name})
        if result.deleted_count > 0:
            return f"{Fore.GREEN}Cat with name {name} deleted."
        else:
            return f"{Fore.RED}Cat with name {name} not found."

    @error_catcher
    def delete_all_cats(self, db):
        collection = db[self.collection_name]
        result = collection.delete_many({})
        return f"{result.deleted_count} cats deleted."


def main():
    uri = "mongodb://localhost:27017/"
    db_name = "cats"
    collection_name = "cats"
    cat_manager = CatDatabaseManager(uri, db_name, collection_name)

    while True:
        print("\n--- MongoDB CLI ---")
        print(f"{Fore.CYAN}1. Insert a document{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Find a document{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Update a cat's age{Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Add a new feature to a cat{Style.RESET_ALL}")
        print(f"{Fore.CYAN}5. Delete a cat by name{Style.RESET_ALL}")
        print(f"{Fore.CYAN}6. View all cats{Style.RESET_ALL}")
        print(f"{Fore.CYAN}7. Delete all cats{Style.RESET_ALL}")
        print(f"{Fore.CYAN}8. Exit{Style.RESET_ALL}")

        choice = input(f"{Fore.YELLOW}Choose an option: {Style.RESET_ALL}").strip()
        with create_connection(uri, db_name) as db:
            if db is None:
                print(f"{Fore.RED}Failed to connect to the database.{Style.RESET_ALL}")
                continue

            match choice:
                case "1":
                    name = (
                        input(f"{Fore.YELLOW}Name: {Style.RESET_ALL}").strip().lower()
                    )

                    while True:
                        age = input(f"{Fore.YELLOW}Age: {Style.RESET_ALL}").strip()
                        if is_valid_number(age):
                            break
                        print(
                            f"{Fore.RED}Invalid input: Age must be a valid number.{Style.RESET_ALL}"
                        )

                    features = input(
                        f"{Fore.YELLOW}Enter features (comma-separated): {Style.RESET_ALL}"
                    )
                    print(cat_manager.insert_document(db, name, age, features))

                case "2":
                    name = (
                        input(f"{Fore.YELLOW}Name: {Style.RESET_ALL}").strip().lower()
                    )
                    print(cat_manager.read_document(db, name))
                case "3":
                    name = (
                        input(f"{Fore.YELLOW}Name: {Style.RESET_ALL}").strip().lower()
                    )
                    new_age = input(f"{Fore.YELLOW}New Age: {Style.RESET_ALL}").strip()
                    print(cat_manager.update_cat_age(db, name, new_age))
                case "4":
                    name = (
                        input(f"{Fore.YELLOW}Name: {Style.RESET_ALL}").strip().lower()
                    )
                    feature = input(f"{Fore.YELLOW}Feature: {Style.RESET_ALL}").strip()
                    print(cat_manager.append_cat_feature(db, name, feature))
                case "5":
                    name = (
                        input(f"{Fore.YELLOW}Name: {Style.RESET_ALL}").strip().lower()
                    )
                    print(cat_manager.delete_cat_by_name(db, name))
                case "6":
                    cats = cat_manager.get_all_documents(db)
                    if not cats:
                        print(f"{Fore.RED}No cats found.{Style.RESET_ALL}")
                    for cat in cats:
                        print(
                            f"🐈 {Fore.GREEN}name:{Style.RESET_ALL} {cat['name']}, {Fore.GREEN}age:{Style.RESET_ALL} {cat['age']}, {Fore.GREEN}features:{Style.RESET_ALL} {cat['features']}"
                        )
                case "7":
                    print(cat_manager.delete_all_cats(db))
                case "8":
                    print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                    return
                case _:
                    print(f"{Fore.RED}Invalid option.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
