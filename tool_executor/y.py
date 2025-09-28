import os

def list_all_files(root_dir):
    """List all files recursively, excluding node_modules and .yarn directories"""
    all_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove excluded directories from dirnames to prevent os.walk from entering them
        dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.yarn')]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            all_files.append(file_path)
    
    return all_files

def main():
    """Main function to execute the file listing"""
    try:
        root_directory = input('Enter the root directory path: ').strip()
        
        # Check if directory exists
        if not os.path.exists(root_directory):
            print(f"Error: Directory '{root_directory}' does not exist!")
            return
        
        if not os.path.isdir(root_directory):
            print(f"Error: '{root_directory}' is not a directory!")
            return
        
        print(f"\nListing all files in '{root_directory}' (excluding node_modules and .yarn):\n")
        
        files = list_all_files(root_directory)
        
        if not files:
            print("No files found!")
        else:
            for i, file_path in enumerate(files, 1):
                print(f"{i:4d}. {file_path}")
            
            print(f"\nTotal files found: {len(files)}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
