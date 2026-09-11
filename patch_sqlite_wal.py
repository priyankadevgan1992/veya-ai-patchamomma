import os
import glob

def patch_db_connections():
    search_dirs = ["veya_agents", "veya_data", "veya_server"]
    for d in search_dirs:
        for file in glob.glob(os.path.join(d, "*.py")):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find definitions that look like this:
            # def get_db():
            #     conn = sqlite3.connect(...)
            #     conn.row_factory = sqlite3.Row
            #     return conn
            
            if "PRAGMA journal_mode=WAL;" not in content and "def get_db" in content:
                # Add WAL mode after sqlite3.connect
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    new_lines.append(line)
                    if "conn = sqlite3.connect(" in line:
                        indent = line.split("conn =")[0]
                        new_lines.append(f"{indent}conn.execute('PRAGMA journal_mode=WAL;')")
                
                new_content = '\n'.join(new_lines)
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Patched {file} with WAL pragma")

    # Also do get_db_connection in tools.py
    tools_file = "veya_agents/tools.py"
    if os.path.exists(tools_file):
        with open(tools_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if "PRAGMA journal_mode=WAL;" not in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if "conn = sqlite3.connect(" in line:
                    indent = line.split("conn =")[0]
                    new_lines.append(f"{indent}conn.execute('PRAGMA journal_mode=WAL;')")
            
            with open(tools_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print("Patched tools.py with WAL pragma")

if __name__ == "__main__":
    patch_db_connections()
