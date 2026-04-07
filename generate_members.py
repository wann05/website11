import sqlite3
import os
import re

DATABASE = 'database.sqlite'
HTML_FILE = 'members.html'

def generate_table_html():
    if not os.path.exists(DATABASE):
        return '<div class="no-data">The database is currently missing or empty.</div>'
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
    if not cursor.fetchone():
        conn.close()
        return '<div class="no-data">The database is currently empty. No members have registered yet.</div>'
    
    cursor.execute('SELECT * FROM members ORDER BY appliedAt DESC')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return '<div class="no-data">The database is currently empty. No members have registered yet.</div>'
        
    html = '''
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Full Name</th>
                                    <th>Student ID</th>
                                    <th>Email</th>
                                    <th>Applied At</th>
                                </tr>
                            </thead>
                            <tbody>
'''
    
    for row in rows:
        html += f'''
                                <tr>
                                    <td>{row[0]}</td>
                                    <td>{row[1]}</td>
                                    <td>{row[2]}</td>
                                    <td>{row[4]}</td>
                                    <td>{row[6]}</td>
                                </tr>
'''
        
    html += '''
                            </tbody>
                        </table>
'''
    return html

def update_html_file(table_html):
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return
        
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = r'(<!-- MEMBERS_TABLE_START -->)([\s\S]*?)(<!-- MEMBERS_TABLE_END -->)'
    
    def replacer(match):
        return f"{match.group(1)}\n{table_html}                        {match.group(3)}"
        
    if not re.search(pattern, content):
        print("Error: Could not find template markers in members.html.")
        return
        
    new_content = re.sub(pattern, replacer, content)
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Successfully updated members.html with the latest database records!")

if __name__ == '__main__':
    table_content = generate_table_html()
    update_html_file(table_content)
