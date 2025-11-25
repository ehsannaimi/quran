import os

def main():
    folder = "quran_pages"
    files = sorted(os.listdir(folder))

    with open("pages_list.txt", "w", encoding="utf-8") as f:
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                f.write(file + "\n")

    print("pages_list.txt created successfully!")

if __name__ == "__main__":
    main()
