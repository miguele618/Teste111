import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from random_word import RandomWords

# Define the directory to save the files
save_directory = r'C:\Users\mdpau\Documents\Projetos\ASCII_ART\ARTA'

async def fetch_art(session, word):
    url = f'https://emojicombos.com/{word}-text-art'
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return word, None

            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            art_elements = soup.find_all('div', class_='emojis')
            if not art_elements:
                return word, None

            ascii_art = '\n\n'.join(art_div.get_text(strip=True) for art_div in art_elements)
            return word, ascii_art
    except Exception as e:
        print(f"Error fetching art for '{word}': {e}")
        return word, None

async def fetch_arts(words):
    arts = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_art(session, word) for word in words]
        for task in asyncio.as_completed(tasks):
            word, ascii_art = await task
            if ascii_art:
                arts[word] = ascii_art
    return arts

def calculate_size(ascii_art):
    return len(ascii_art.encode('utf-8')) / (1024 * 1024)

def main():
    # Ensure the save directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Initialize the RandomWords object
    r = RandomWords()

    # Ask the user how many random words they want to generate
    try:
        num_words = int(input("How many random words do you want to generate? "))
    except ValueError:
        print("Invalid number entered. Please enter a valid integer.")
        return

    # Use a set to keep track of already stored files
    existing_files = set(os.path.splitext(f)[0] for f in os.listdir(save_directory))

    # Create a list to store words to be processed
    words_to_process = []
    tried_words_count = 0  # Counter for tried words

    while len(words_to_process) < num_words:
        word = r.get_random_word()
        tried_words_count += 1
        # Print count of attempted words on the same line
        print(f"\rAttempted words so far: {tried_words_count}", end='')

        if word not in existing_files and word not in words_to_process:
            words_to_process.append(word)
        # Adding a small sleep to avoid too many rapid requests
        asyncio.sleep(0.1)

    # Fetch art asynchronously
    arts = asyncio.run(fetch_arts(words_to_process))

    # Check if we have the required number of files
    while len(arts) < num_words:
        additional_words_needed = num_words - len(arts)
        additional_words = []
        while len(additional_words) < additional_words_needed:
            word = r.get_random_word()
            tried_words_count += 1
            # Print count of attempted words on the same line
            print(f"\rAttempted words so far: {tried_words_count}", end='')

            if word not in existing_files and word not in words_to_process and word not in additional_words:
                additional_words.append(word)
        # Adding a small sleep to avoid too many rapid requests
        asyncio.sleep(0.1)

        # Fetch additional words
        additional_arts = asyncio.run(fetch_arts(additional_words))
        arts.update(additional_arts)

    # Estimate the total size of all files
    total_size_mb = sum(calculate_size(ascii_art) for ascii_art in arts.values())

    # Print the total estimated size and ask for user confirmation
    print(f"\nTotal estimated size of all files: {total_size_mb:.2f} MB")
    user_input = input("Do you want to proceed with saving these files? (yes/no): ").strip().lower()
    if user_input != 'yes':
        print("Operation canceled by the user.")
        return

    # Save all the ASCII art files
    saved_files_count = 0
    for word, ascii_art in arts.items():
        file_path = os.path.join(save_directory, f'{word}.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(ascii_art)
        saved_files_count += 1

    print(f"Saved {saved_files_count} file(s).")

if __name__ == "__main__":
    main()
