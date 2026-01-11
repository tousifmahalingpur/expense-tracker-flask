from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from MySQLdb import IntegrityError

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- MySQL Configuration ----------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tousif@953862'
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

# ---------------- Test DB Connection ----------------
@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()
        return f"✅ Database connected successfully: {db}"
    except Exception as e:
        return f"❌ Database connection failed: {e}"

# ---------------- Register ----------------
@app.route('/', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                (name, email, password)
            )
            mysql.connection.commit()
            return redirect('/login')

        except IntegrityError:
            msg = "Email already exists!"

    return render_template('register.html', msg=msg)

# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            return redirect('/dashboard')
        else:
            msg = "Invalid email or password"

    return render_template('login.html', msg=msg)

# ---------------- Dashboard ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=%s",
        (session['user_id'],)
    )
    expenses = cursor.fetchall()

    cursor.execute(
        "SELECT IFNULL(SUM(amount), 0) AS total FROM expenses WHERE user_id=%s",
        (session['user_id'],)
    )
    total = cursor.fetchone()['total']

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total
    )

# ---------------- Add Expense ----------------
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        desc = request.form['description']

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, expense_date, description) VALUES (%s,%s,%s,%s,%s)",
            (session['user_id'], amount, category, date, desc)
        )
        mysql.connection.commit()
        return redirect('/dashboard')

    return render_template('add_expense.html')

# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)
