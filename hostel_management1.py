import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # change to your MySQL user
    'password': 'root',          # change to your MySQL password
    'database': 'hostel_db',
    'autocommit': False
}

class HostelApp:

    def connect_db(self):
        """Establish MySQL connection. Returns True if successful."""
        try:
            # First connect without database to create it if needed
            temp_conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            temp_cursor.close()
            temp_conn.close()

            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            # DO NOT LOG HERE – sql_log not created yet
            return True
        except Error as e:
            print(f"DB Connection Error: {e}")
            return False

    def __init__(self, root):
        self.root = root
        self.root.title("PCU Hostel Manager - MySQL Edition")
        self.root.geometry("1300x700")
        self.root.configure(bg='#f0f2f5')

        self.conn = None
        self.cursor = None

        # Try to connect to database first
        if not self.connect_db():
            messagebox.showerror("Fatal Error", "Cannot connect to MySQL database.\n"
                                 "Please check your MySQL server and credentials.\n"
                                 "The application will now close.")
            self.root.destroy()
            return  # stop further initialization

        # Now create UI widgets (connection succeeded)
        self.create_widgets()

        # Now that sql_log exists, we can log the successful connection
        self.log_sql("-- Connected to MySQL database --")

        # Initial data load
        self.setup_database()
        self.load_rooms()
        self.load_allocations()

    def create_widgets(self):
        """Create all GUI elements after successful DB connection."""
        # SQL log display
        self.sql_log = scrolledtext.ScrolledText(self.root, height=8, font=('Consolas', 9), bg='#1e1e2e', fg='#d4d4d4')
        self.sql_log.pack(fill=tk.X, padx=10, pady=5)

        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Rooms panel
        left_frame = tk.LabelFrame(main_frame, text="Rooms Management", font=('Arial', 12, 'bold'), bg='#f0f2f5')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.rooms_tree = ttk.Treeview(left_frame, columns=('ID', 'Number', 'Capacity', 'Occupants'), show='headings')
        self.rooms_tree.heading('ID', text='ID')
        self.rooms_tree.heading('Number', text='Room Number')
        self.rooms_tree.heading('Capacity', text='Capacity')
        self.rooms_tree.heading('Occupants', text='Occupants')
        self.rooms_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        room_btn_frame = tk.Frame(left_frame, bg='#f0f2f5')
        room_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(room_btn_frame, text="Add Room", command=self.add_room_dialog, bg='#4caf50', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(room_btn_frame, text="Remove Room", command=self.remove_room, bg='#f44336', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(room_btn_frame, text="Refresh Rooms", command=self.load_rooms, bg='#2196f3', fg='white').pack(side=tk.LEFT, padx=2)

        # Right: Allocations panel
        right_frame = tk.LabelFrame(main_frame, text="Student Allocations", font=('Arial', 12, 'bold'), bg='#f0f2f5')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.alloc_tree = ttk.Treeview(right_frame, columns=('ID', 'Student Name', 'Student ID', 'Room', 'Check-in'), show='headings')
        self.alloc_tree.heading('ID', text='Alloc ID')
        self.alloc_tree.heading('Student Name', text='Student Name')
        self.alloc_tree.heading('Student ID', text='Student ID')
        self.alloc_tree.heading('Room', text='Room No.')
        self.alloc_tree.heading('Check-in', text='Check-in Date')
        self.alloc_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        alloc_btn_frame = tk.Frame(right_frame, bg='#f0f2f5')
        alloc_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(alloc_btn_frame, text="Allot Room", command=self.allot_dialog, bg='#ff9800', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(alloc_btn_frame, text="Deallocate", command=self.deallocate, bg='#f44336', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(alloc_btn_frame, text="Refresh Allocations", command=self.load_allocations, bg='#2196f3', fg='white').pack(side=tk.LEFT, padx=2)

        # Bottom: Utility buttons
        bottom_frame = tk.Frame(self.root, bg='#f0f2f5')
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(bottom_frame, text="Setup / Reset Database (CREATE TABLES)", command=self.setup_database, bg='#9c27b0', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Execute Custom SQL", command=self.custom_sql_dialog, bg='#607d8b', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Exit", command=self.exit_app, bg='#555', fg='white').pack(side=tk.RIGHT, padx=5)

    # ---------- All other methods (log_sql, execute_sql, setup_database, load_rooms, etc.) remain unchanged ----------
    # (Copy them exactly as in the previous code block, but ensure the indentation is correct)

    def log_sql(self, sql, params=None):
        """Display SQL command in the log area."""
        if params:
            sql_display = f"{sql}  # params: {params}"
        else:
            sql_display = sql
        self.sql_log.insert(tk.END, sql_display + "\n")
        self.sql_log.see(tk.END)
        self.root.update_idletasks()

    def execute_sql(self, sql, params=None, fetch=False):
        """Execute SQL and log it. Returns cursor if fetch, else None."""
        try:
            self.log_sql(sql, params)
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            if fetch:
                return self.cursor
            else:
                self.conn.commit()
                return None
        except Error as e:
            self.conn.rollback()
            messagebox.showerror("SQL Error", f"{e}\n\nSQL: {sql}")
            raise

    # ---------- Database Setup (CREATE TABLE) ----------
    def setup_database(self):
        """Create tables if they don't exist (shows CREATE TABLE commands)."""
        try:
            # Rooms table
            sql_rooms = """
            CREATE TABLE IF NOT EXISTS rooms (
                id INT PRIMARY KEY AUTO_INCREMENT,
                room_number VARCHAR(20) NOT NULL UNIQUE,
                capacity INT NOT NULL,
                current_occupants INT DEFAULT 0
            )
            """
            self.execute_sql(sql_rooms)

            # Allocations table
            sql_alloc = """
            CREATE TABLE IF NOT EXISTS allocations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                room_id INT NOT NULL,
                student_name VARCHAR(100) NOT NULL,
                student_id VARCHAR(50) NOT NULL UNIQUE,
                check_in_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
            """
            self.execute_sql(sql_alloc)

            # Optional: Insert default rooms if empty
            self.cursor.execute("SELECT COUNT(*) FROM rooms")
            if self.cursor.fetchone()[0] == 0:
                self.log_sql("-- Seeding default rooms --")
                default_rooms = [
                    ('A101',6), ('A102',6), ('A103',6), ('A104',6), ('A105',6),
                    ('A201',4), ('A202',4), ('A203',4), ('A204',4), ('A205',4),
                    ('B101',4), ('B102',4), ('B103',4), ('B201',2), ('B202',2), ('B203',2),
                    ('P101',1), ('P102',1), ('P103',1), ('P104',1), ('P201',1)
                ]
                for rnum, cap in default_rooms:
                    self.execute_sql("INSERT INTO rooms (room_number, capacity) VALUES (%s, %s)", (rnum, cap))
                self.log_sql("-- Default rooms inserted --")

            # Seed some allocations if empty
            self.cursor.execute("SELECT COUNT(*) FROM allocations")
            if self.cursor.fetchone()[0] == 0:
                self.log_sql("-- Seeding default allocations --")
                # Need to map room numbers to IDs
                self.cursor.execute("SELECT id, room_number FROM rooms")
                room_map = {rn: rid for rid, rn in self.cursor.fetchall()}
                default_allocs = [
                    (room_map['A101'], 'Saksham Sharma', 'SOE24201010437'),
                    (room_map['A101'], 'Vedant Vasundekar', 'SOE24201010110'),
                    (room_map['A101'], 'Utkarsh Kumar', 'SOE24201010220'),
                    (room_map['A101'], 'Gaurav Borse', 'SOE24201010438'),
                    (room_map['B101'], 'Akanksha Petkar', 'SOE24201010778'),
                    (room_map['B101'], 'Ananya Sharma', 'SOE24201010998'),
                    (room_map['B101'], 'Ishita Iyer', 'SOE24201010202'),
                    (room_map['B101'], 'Sanya Malhotra', 'SOE24201010535'),
                    (room_map['P101'], 'Arjun Varma', 'SOE24201010312'),
                    (room_map['P102'], 'Sia Singhania', 'SOE24201010945'),
                    (room_map['P103'], 'Reyansh Das', 'SOE24201010108'),
                    (room_map['P104'], 'Ananya Hegde', 'SOE24201010567'),
                    (room_map['P201'], 'Ishaan Malhotra', 'SOE24201010223')
                ]
                for rid, name, sid in default_allocs:
                    self.execute_sql(
                        "INSERT INTO allocations (room_id, student_name, student_id) VALUES (%s, %s, %s)",
                        (rid, name, sid)
                    )
                    # Update room occupants count
                    self.execute_sql("UPDATE rooms SET current_occupants = current_occupants + 1 WHERE id = %s", (rid,))
                self.log_sql("-- Default allocations seeded --")

            messagebox.showinfo("Setup", "Database tables ready and seeded with default data.")
            self.load_rooms()
            self.load_allocations()
        except Exception as e:
            messagebox.showerror("Setup Error", str(e))

    # ---------- CRUD Operations (with SQL) ----------
    def load_rooms(self):
        """SELECT rooms with current occupant count."""
        try:
            sql = """
                SELECT r.id, r.room_number, r.capacity, 
                       COALESCE(COUNT(a.id), 0) AS occupants
                FROM rooms r
                LEFT JOIN allocations a ON r.id = a.room_id
                GROUP BY r.id
                ORDER BY r.id
            """
            cursor = self.execute_sql(sql, fetch=True)
            rows = cursor.fetchall()
            self.rooms_tree.delete(*self.rooms_tree.get_children())
            for row in rows:
                self.rooms_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def load_allocations(self):
        """SELECT allocations with room number."""
        try:
            sql = """
                SELECT a.id, a.student_name, a.student_id, r.room_number, 
                       DATE_FORMAT(a.check_in_timestamp, '%%Y-%%m-%%d %%H:%%i') AS checkin
                FROM allocations a
                JOIN rooms r ON a.room_id = r.id
                ORDER BY a.id
            """
            cursor = self.execute_sql(sql, fetch=True)
            rows = cursor.fetchall()
            self.alloc_tree.delete(*self.alloc_tree.get_children())
            for row in rows:
                self.alloc_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def add_room_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Room")
        dialog.geometry("300x200")
        dialog.grab_set()

        tk.Label(dialog, text="Room Number:").pack(pady=5)
        room_num = tk.Entry(dialog)
        room_num.pack(pady=5)

        tk.Label(dialog, text="Capacity:").pack(pady=5)
        capacity = tk.Entry(dialog)
        capacity.pack(pady=5)

        def add():
            rn = room_num.get().strip()
            cap = capacity.get().strip()
            if not rn or not cap.isdigit():
                messagebox.showerror("Error", "Valid room number and numeric capacity required")
                return
            try:
                sql = "INSERT INTO rooms (room_number, capacity) VALUES (%s, %s)"
                self.execute_sql(sql, (rn, int(cap)))
                self.load_rooms()
                dialog.destroy()
                messagebox.showinfo("Success", f"Room {rn} added")
            except Exception as e:
                messagebox.showerror("Insert Error", str(e))

        tk.Button(dialog, text="Add", command=add, bg='#4caf50', fg='white').pack(pady=10)

    def remove_room(self):
        selected = self.rooms_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a room to remove.")
            return
        room_id = self.rooms_tree.item(selected[0])['values'][0]
        # Check if room has occupants
        try:
            self.cursor.execute("SELECT current_occupants FROM rooms WHERE id = %s", (room_id,))
            occ = self.cursor.fetchone()[0]
            if occ > 0:
                messagebox.showerror("Cannot Remove", f"Room has {occ} occupant(s). Deallocate first.")
                return
            sql = "DELETE FROM rooms WHERE id = %s"
            self.execute_sql(sql, (room_id,))
            self.load_rooms()
            messagebox.showinfo("Removed", "Room deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def allot_dialog(self):
        # Get list of available rooms (not full)
        try:
            self.cursor.execute("""
                SELECT id, room_number, capacity, current_occupants 
                FROM rooms 
                WHERE current_occupants < capacity
            """)
            available = self.cursor.fetchall()
            if not available:
                messagebox.showwarning("No Rooms", "No available rooms with free capacity.")
                return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Allot Room")
        dialog.geometry("400x300")
        dialog.grab_set()

        tk.Label(dialog, text="Select Room:").pack(pady=5)
        room_var = tk.StringVar()
        room_combo = ttk.Combobox(dialog, textvariable=room_var, width=40)
        room_options = [f"{r[1]} (Cap: {r[2]}, Occ: {r[3]})" for r in available]
        room_combo['values'] = room_options
        room_combo.pack(pady=5)

        tk.Label(dialog, text="Student Name:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack(pady=5)

        tk.Label(dialog, text="Student ID (unique):").pack(pady=5)
        sid_entry = tk.Entry(dialog, width=40)
        sid_entry.pack(pady=5)

        def allot():
            if not room_combo.get() or not name_entry.get().strip() or not sid_entry.get().strip():
                messagebox.showerror("Error", "All fields required")
                return
            idx = room_combo.current()
            if idx == -1:
                return
            room_id = available[idx][0]
            sname = name_entry.get().strip()
            sid = sid_entry.get().strip()

            try:
                # Begin transaction
                self.execute_sql("START TRANSACTION")
                # Check if student already allocated
                self.cursor.execute("SELECT id FROM allocations WHERE student_id = %s", (sid,))
                if self.cursor.fetchone():
                    raise Exception("Student ID already has an active allotment.")
                # Check room capacity again
                self.cursor.execute("SELECT capacity, current_occupants FROM rooms WHERE id = %s FOR UPDATE", (room_id,))
                cap, occ = self.cursor.fetchone()
                if occ >= cap:
                    raise Exception("Room became full. Please refresh.")
                # Insert allocation
                self.execute_sql(
                    "INSERT INTO allocations (room_id, student_name, student_id) VALUES (%s, %s, %s)",
                    (room_id, sname, sid)
                )
                # Update room occupants
                self.execute_sql("UPDATE rooms SET current_occupants = current_occupants + 1 WHERE id = %s", (room_id,))
                self.execute_sql("COMMIT")
                self.load_rooms()
                self.load_allocations()
                dialog.destroy()
                messagebox.showinfo("Success", f"Allotted room to {sname}")
            except Exception as e:
                self.execute_sql("ROLLBACK")
                messagebox.showerror("Allotment Failed", str(e))

        tk.Button(dialog, text="Allot", command=allot, bg='#ff9800', fg='white').pack(pady=15)

    def deallocate(self):
        selected = self.alloc_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select an allocation to deallocate.")
            return
        alloc_id = self.alloc_tree.item(selected[0])['values'][0]
        try:
            # Get room_id from allocation
            self.cursor.execute("SELECT room_id FROM allocations WHERE id = %s", (alloc_id,))
            result = self.cursor.fetchone()
            if not result:
                raise Exception("Allocation not found")
            room_id = result[0]

            # Transaction
            self.execute_sql("START TRANSACTION")
            self.execute_sql("DELETE FROM allocations WHERE id = %s", (alloc_id,))
            self.execute_sql("UPDATE rooms SET current_occupants = current_occupants - 1 WHERE id = %s", (room_id,))
            self.execute_sql("COMMIT")
            self.load_rooms()
            self.load_allocations()
            messagebox.showinfo("Deallocated", "Student removed from room.")
        except Exception as e:
            self.execute_sql("ROLLBACK")
            messagebox.showerror("Error", str(e))

    def custom_sql_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Execute Custom SQL")
        dialog.geometry("600x400")
        dialog.grab_set()

        tk.Label(dialog, text="Enter SQL command(s) - multiple statements separated by ;").pack(pady=5)
        sql_text = scrolledtext.ScrolledText(dialog, height=10, font=('Consolas', 10))
        sql_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        sql_text.insert(tk.END, "-- Example: SELECT * FROM rooms;")

        result_text = scrolledtext.ScrolledText(dialog, height=8, font=('Consolas', 9), bg='#1e1e2e', fg='#d4d4d4')
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def execute_custom():
            sql = sql_text.get("1.0", tk.END).strip()
            if not sql:
                return
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            result_text.delete("1.0", tk.END)
            for stmt in statements:
                try:
                    self.log_sql(stmt)
                    self.cursor.execute(stmt)
                    if stmt.upper().startswith("SELECT"):
                        rows = self.cursor.fetchall()
                        if rows:
                            for row in rows:
                                result_text.insert(tk.END, str(row) + "\n")
                        else:
                            result_text.insert(tk.END, "(no rows)\n")
                    else:
                        self.conn.commit()
                        result_text.insert(tk.END, f"Executed: {stmt}\nRows affected: {self.cursor.rowcount}\n\n")
                except Exception as e:
                    result_text.insert(tk.END, f"Error in: {stmt}\n{e}\n\n")
            self.load_rooms()
            self.load_allocations()

        tk.Button(dialog, text="Execute", command=execute_custom, bg='#2196f3', fg='white').pack(pady=10)

    def exit_app(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HostelApp(root)
    root.mainloop()