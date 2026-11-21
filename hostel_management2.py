import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error
import time

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',     
    'database': 'hostel_db',
    'autocommit': False
}

class HostelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PCU Hostel Manager - MySQL Edition")
        self.root.geometry("1350x750")
        self.root.configure(bg='#f0f2f5')

        self.conn = None
        self.cursor = None

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        if not self.connect_db():
            messagebox.showerror(
                "Fatal Error",
                "Cannot connect to MySQL database.\n"
                "Please check your MySQL server and credentials.\n"
                "The application will now close."
            )
            self.root.destroy()
            return

        self.create_widgets()
        self.log_sql("-- Connected to MySQL database --")
        self.setup_database()
        self.load_rooms()
        self.load_allocations()

    # Database Connection
    def connect_db(self):
        try:
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
            return True
        except Error as e:
            print(f"DB Connection Error: {e}")
            return False

    def create_widgets(self):

        self.sql_log = scrolledtext.ScrolledText(
            self.root, height=6, font=('Consolas', 9),
            bg='#1e1e2e', fg='#d4d4d4'
        )
        self.sql_log.pack(fill=tk.X, padx=10, pady=5)

        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = tk.LabelFrame(main_frame, text="Rooms Management",
                                   font=('Arial', 12, 'bold'), bg='#f0f2f5')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_frame_left = tk.Frame(left_frame)
        tree_frame_left.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        vsb_left = ttk.Scrollbar(tree_frame_left, orient="vertical")
        hsb_left = ttk.Scrollbar(tree_frame_left, orient="horizontal")
        self.rooms_tree = ttk.Treeview(tree_frame_left,
                                       columns=('ID', 'Number', 'Capacity', 'Occupants', 'SpaceLeft'),
                                       show='headings',
                                       yscrollcommand=vsb_left.set,
                                       xscrollcommand=hsb_left.set)
        vsb_left.config(command=self.rooms_tree.yview)
        hsb_left.config(command=self.rooms_tree.xview)

        self.rooms_tree.heading('ID', text='ID')
        self.rooms_tree.heading('Number', text='Room Number')
        self.rooms_tree.heading('Capacity', text='Capacity')
        self.rooms_tree.heading('Occupants', text='Occupants')
        self.rooms_tree.heading('SpaceLeft', text='Space Left')

        self.rooms_tree.column('ID', width=50)
        self.rooms_tree.column('Number', width=100)
        self.rooms_tree.column('Capacity', width=70)
        self.rooms_tree.column('Occupants', width=70)
        self.rooms_tree.column('SpaceLeft', width=80)

        self.rooms_tree.grid(row=0, column=0, sticky="nsew")
        vsb_left.grid(row=0, column=1, sticky="ns")
        hsb_left.grid(row=1, column=0, sticky="ew")
        tree_frame_left.grid_rowconfigure(0, weight=1)
        tree_frame_left.grid_columnconfigure(0, weight=1)

        room_btn_frame = tk.Frame(left_frame, bg='#f0f2f5')
        room_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(room_btn_frame, text="Add Room", command=self.add_room_dialog,
                  bg='#4caf50', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(room_btn_frame, text="Remove Room", command=self.remove_room,
                  bg='#f44336', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(room_btn_frame, text="Refresh Rooms", command=self.load_rooms,
                  bg='#2196f3', fg='white').pack(side=tk.LEFT, padx=2)

        right_frame = tk.LabelFrame(main_frame, text="Student Allocations",
                                    font=('Arial', 12, 'bold'), bg='#f0f2f5')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_frame_right = tk.Frame(right_frame)
        tree_frame_right.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        vsb_right = ttk.Scrollbar(tree_frame_right, orient="vertical")
        hsb_right = ttk.Scrollbar(tree_frame_right, orient="horizontal")

        self.alloc_tree = ttk.Treeview(tree_frame_right,
                                       columns=('ID', 'Student Name', 'Student ID', 'Room'),
                                       show='headings',
                                       yscrollcommand=vsb_right.set,
                                       xscrollcommand=hsb_right.set)
        vsb_right.config(command=self.alloc_tree.yview)
        hsb_right.config(command=self.alloc_tree.xview)

        self.alloc_tree.heading('ID', text='Alloc ID')
        self.alloc_tree.heading('Student Name', text='Student Name')
        self.alloc_tree.heading('Student ID', text='Student ID')
        self.alloc_tree.heading('Room', text='Room No.')

        self.alloc_tree.column('ID', width=70)
        self.alloc_tree.column('Student Name', width=150)
        self.alloc_tree.column('Student ID', width=130)
        self.alloc_tree.column('Room', width=80)

        self.alloc_tree.grid(row=0, column=0, sticky="nsew")
        vsb_right.grid(row=0, column=1, sticky="ns")
        hsb_right.grid(row=1, column=0, sticky="ew")
        tree_frame_right.grid_rowconfigure(0, weight=1)
        tree_frame_right.grid_columnconfigure(0, weight=1)

        alloc_btn_frame = tk.Frame(right_frame, bg='#f0f2f5')
        alloc_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(alloc_btn_frame, text="Allot Room", command=self.allot_dialog,
                  bg='#ff9800', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(alloc_btn_frame, text="Deallocate", command=self.deallocate,
                  bg='#f44336', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(alloc_btn_frame, text="Refresh Allocations", command=self.load_allocations,
                  bg='#2196f3', fg='white').pack(side=tk.LEFT, padx=2)

        #  Bottom Bar
        bottom_frame = tk.Frame(self.root, bg='#f0f2f5')
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(bottom_frame, text="Setup / Reset Database (CREATE TABLES)",
                  command=self.setup_database, bg='#9c27b0', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Reset to Minimal Default Data",
                  command=self.reset_to_minimal_defaults, bg='#ff5722', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Execute Custom SQL", command=self.custom_sql_dialog,
                  bg='#607d8b', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="Exit", command=self.exit_app,
                  bg='#555', fg='white').pack(side=tk.RIGHT, padx=5)

        status_label = tk.Label(bottom_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                                anchor=tk.W, bg='#f0f2f5', fg='#555', font=('Arial', 9))
        status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))

    def log_sql(self, sql, params=None):
        if params:
            sql_display = f"{sql}  # params: {params}"
        else:
            sql_display = sql
        self.sql_log.insert(tk.END, sql_display + "\n")
        self.sql_log.see(tk.END)
        self.root.update_idletasks()

    def execute_sql(self, sql, params=None, fetch=False):
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

    def setup_database(self):
        try:
            self.status_var.set("Setting up database...")
            self.root.update_idletasks()

            sql_rooms = """
            CREATE TABLE IF NOT EXISTS rooms (
                id INT PRIMARY KEY AUTO_INCREMENT,
                room_number VARCHAR(20) NOT NULL UNIQUE,
                capacity INT NOT NULL,
                current_occupants INT DEFAULT 0
            )
            """
            self.execute_sql(sql_rooms)

            sql_alloc = """
            CREATE TABLE IF NOT EXISTS allocations (
                id INT PRIMARY KEY AUTO_INCREMENT,
                room_id INT NOT NULL,
                student_name VARCHAR(100) NOT NULL,
                student_id VARCHAR(50) NOT NULL UNIQUE,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
            """
            self.execute_sql(sql_alloc)

            self.cursor.execute("SELECT COUNT(*) FROM rooms")
            if self.cursor.fetchone()[0] == 0:
                self._insert_minimal_default_data()

            self.status_var.set("Ready")
            messagebox.showinfo("Setup", "Database tables ready with minimal default data.")
            self.load_rooms()
            self.load_allocations()
        except Exception as e:
            self.status_var.set("Error during setup")
            messagebox.showerror("Setup Error", str(e))

    def _insert_minimal_default_data(self):
        self.log_sql("-- Inserting minimal default rooms --")
        default_rooms = [('A101',4), ('A102',4), ('B101',2), ('P101',1)]
        for rnum, cap in default_rooms:
            self.execute_sql("INSERT INTO rooms (room_number, capacity) VALUES (%s, %s)", (rnum, cap))

        self.cursor.execute("SELECT id, room_number FROM rooms")
        room_map = {rn: rid for rid, rn in self.cursor.fetchall()}

        self.log_sql("-- Inserting minimal default allocations --")
        default_allocs = [
            (room_map['A101'], 'Saksham Sharma', 'SOE24201010437'),
            (room_map['A101'], 'Vedant Vasundekar', 'SOE24201010110'),
            (room_map['A101'], 'Utkarsh Kumar', 'SOE24201010220'),
            (room_map['B101'], 'Akanksha Petkar', 'SOE24201010778'),
            (room_map['P101'], 'Arjun Varma', 'SOE24201010312')
        ]
        for rid, name, sid in default_allocs:
            self.execute_sql(
                "INSERT INTO allocations (room_id, student_name, student_id) VALUES (%s, %s, %s)",
                (rid, name, sid)
            )
            self.execute_sql(
                "UPDATE rooms SET current_occupants = current_occupants + 1 WHERE id = %s",
                (rid,)
            )
        self.log_sql("-- Minimal default data inserted --")

    def reset_to_minimal_defaults(self):
        if not messagebox.askyesno("Confirm Reset",
                                   "This will delete ALL existing data and replace it with minimal default values.\n\nProceed?"):
            return
        try:
            self.status_var.set("Resetting database...")
            self.root.update_idletasks()
            time.sleep(0.2)

            self.execute_sql("SET FOREIGN_KEY_CHECKS = 0")
            self.execute_sql("DELETE FROM allocations")
            self.execute_sql("DELETE FROM rooms")
            self.execute_sql("SET FOREIGN_KEY_CHECKS = 1")

            self.execute_sql("ALTER TABLE rooms AUTO_INCREMENT = 1")
            self.execute_sql("ALTER TABLE allocations AUTO_INCREMENT = 1")

            self._insert_minimal_default_data()

            self.load_rooms()
            self.load_allocations()
            self.status_var.set("Ready")
            messagebox.showinfo("Reset Complete", "Database has been reset to minimal default values.")
        except Exception as e:
            self.status_var.set("Reset failed")
            messagebox.showerror("Reset Error", str(e))

    def load_rooms(self):
        try:
            self.status_var.set("Loading rooms...")
            self.root.update_idletasks()
            time.sleep(0.1)

            sql = """
                SELECT r.id, r.room_number, r.capacity, 
                       COALESCE(COUNT(a.id), 0) AS occupants,
                       (r.capacity - COALESCE(COUNT(a.id), 0)) AS space_left
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
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set("Error loading rooms")
            messagebox.showerror("Load Error", str(e))

    def load_allocations(self):
        try:
            self.status_var.set("Loading allocations...")
            self.root.update_idletasks()
            time.sleep(0.1)

            sql = """
                SELECT a.id, a.student_name, a.student_id, r.room_number
                FROM allocations a
                JOIN rooms r ON a.room_id = r.id
                ORDER BY a.id
            """
            cursor = self.execute_sql(sql, fetch=True)
            rows = cursor.fetchall()
            self.alloc_tree.delete(*self.alloc_tree.get_children())
            for row in rows:
                self.alloc_tree.insert('', tk.END, values=row)
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set("Error loading allocations")
            messagebox.showerror("Load Error", str(e))

    # Room management
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
                self.status_var.set(f"Adding room {rn}...")
                self.root.update_idletasks()
                self.execute_sql("INSERT INTO rooms (room_number, capacity) VALUES (%s, %s)", (rn, int(cap)))
                self.load_rooms()
                dialog.destroy()
                self.status_var.set("Ready")
                messagebox.showinfo("Success", f"Room {rn} added")
            except Exception as e:
                self.status_var.set("Add failed")
                messagebox.showerror("Insert Error", str(e))

        tk.Button(dialog, text="Add", command=add, bg='#4caf50', fg='white').pack(pady=10)

    def remove_room(self):
        selected = self.rooms_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a room to remove.")
            return
        room_id = self.rooms_tree.item(selected[0])['values'][0]
        try:
            self.cursor.execute("SELECT current_occupants FROM rooms WHERE id = %s", (room_id,))
            occ = self.cursor.fetchone()[0]
            if occ > 0:
                messagebox.showerror("Cannot Remove", f"Room has {occ} occupant(s). Deallocate first.")
                return
            self.status_var.set(f"Removing room ID {room_id}...")
            self.root.update_idletasks()
            self.execute_sql("DELETE FROM rooms WHERE id = %s", (room_id,))
            self.load_rooms()
            self.status_var.set("Ready")
            messagebox.showinfo("Removed", "Room deleted.")
        except Exception as e:
            self.status_var.set("Remove failed")
            messagebox.showerror("Error", str(e))

    # Allocate & deallocate
    def allot_dialog(self):
        try:
            self.cursor.execute("""
                SELECT id, room_number, capacity, current_occupants 
                FROM rooms WHERE current_occupants < capacity
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
        room_combo['values'] = [f"{r[1]} (Cap: {r[2]}, Occ: {r[3]})" for r in available]
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
                self.status_var.set(f"Allotting {sname} to room...")
                self.root.update_idletasks()
                self.execute_sql("START TRANSACTION")
                self.cursor.execute("SELECT id FROM allocations WHERE student_id = %s", (sid,))
                if self.cursor.fetchone():
                    raise Exception("Student ID already has an active allotment.")

                self.cursor.execute(
                    "SELECT capacity, current_occupants FROM rooms WHERE id = %s FOR UPDATE",
                    (room_id,)
                )
                cap, occ = self.cursor.fetchone()
                if occ >= cap:
                    raise Exception("Room became full. Please refresh.")

                self.execute_sql(
                    "INSERT INTO allocations (room_id, student_name, student_id) VALUES (%s, %s, %s)",
                    (room_id, sname, sid)
                )
                self.execute_sql(
                    "UPDATE rooms SET current_occupants = current_occupants + 1 WHERE id = %s",
                    (room_id,)
                )
                self.execute_sql("COMMIT")

                self.load_rooms()
                self.load_allocations()
                dialog.destroy()
                self.status_var.set("Ready")
                messagebox.showinfo("Success", f"Allotted room to {sname}")
            except Exception as e:
                self.execute_sql("ROLLBACK")
                self.status_var.set("Allotment failed")
                messagebox.showerror("Allotment Failed", str(e))

        tk.Button(dialog, text="Allot", command=allot, bg='#ff9800', fg='white').pack(pady=15)

    def deallocate(self):
        selected = self.alloc_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select an allocation to deallocate.")
            return
        alloc_id = self.alloc_tree.item(selected[0])['values'][0]
        try:
            self.cursor.execute("SELECT room_id FROM allocations WHERE id = %s", (alloc_id,))
            result = self.cursor.fetchone()
            if not result:
                raise Exception("Allocation not found")
            room_id = result[0]

            self.status_var.set(f"Deallocating allocation ID {alloc_id}...")
            self.root.update_idletasks()
            self.execute_sql("START TRANSACTION")
            self.execute_sql("DELETE FROM allocations WHERE id = %s", (alloc_id,))
            self.execute_sql("UPDATE rooms SET current_occupants = current_occupants - 1 WHERE id = %s", (room_id,))
            self.execute_sql("COMMIT")

            self.load_rooms()
            self.load_allocations()
            self.status_var.set("Ready")
            messagebox.showinfo("Deallocated", "Student removed from room.")
        except Exception as e:
            self.execute_sql("ROLLBACK")
            self.status_var.set("Deallocation failed")
            messagebox.showerror("Error", str(e))

    def custom_sql_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Execute Custom SQL")
        dialog.geometry("700x500")
        dialog.grab_set()

        tk.Label(dialog, text="Enter SQL command(s) - multiple statements separated by ;").pack(pady=5)
        sql_text = scrolledtext.ScrolledText(dialog, height=10, font=('Consolas', 10))
        sql_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        sql_text.insert(tk.END, "-- Examples:\nSELECT * FROM rooms;\nSELECT * FROM allocations;")

        result_text = scrolledtext.ScrolledText(dialog, height=10, font=('Consolas', 9),
                                                bg='#1e1e2e', fg='#d4d4d4')
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def execute_custom():
            sql = sql_text.get("1.0", tk.END).strip()
            if not sql:
                return
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            result_text.delete("1.0", tk.END)
            self.status_var.set("Executing custom SQL...")
            self.root.update_idletasks()

            for stmt in statements:
                try:
                    self.log_sql(stmt)
                    self.cursor.execute(stmt)
                    if stmt.upper().startswith("SELECT"):
                        rows = self.cursor.fetchall()
                        if rows:
                            result_text.insert(tk.END, f"→ {stmt}\n")
                            for row in rows:
                                result_text.insert(tk.END, str(row) + "\n")
                            result_text.insert(tk.END, "\n")
                        else:
                            result_text.insert(tk.END, f"→ {stmt}\n(no rows)\n\n")
                    else:
                        self.conn.commit()
                        result_text.insert(tk.END, f"→ {stmt}\nRows affected: {self.cursor.rowcount}\n\n")
                except Exception as e:
                    result_text.insert(tk.END, f"Error in: {stmt}\n{e}\n\n")
            self.load_rooms()
            self.load_allocations()
            self.status_var.set("Ready")

        tk.Button(dialog, text="Execute", command=execute_custom, bg='#2196f3', fg='white').pack(pady=10)

    def exit_app(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = HostelApp(root)
    root.mainloop()