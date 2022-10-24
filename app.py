from crypt import methods
import functools
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy


app=Flask(__name__)

#  connect database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mystatement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

# create model of database
class Statement(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.String(50),nullable=False)
    name = db.Column(db.String(100),nullable=False)
    amount = db.Column(db.Integer,nullable=False)
    category = db.Column(db.String(50),nullable=False)

    # create database
    with app.app_context() as app:
        db.create_all()

# to show the template filter for use at the page
# comma digit
@app.template_filter()
def commaDigit(num): 
    num = float(num)
    return "{:,.2f}".format(num)


@app.route("/addForm")
def addForm():
    return render_template("addForm.html")

# when send data use this route
@app.route("/addStatement", methods=["POST"])
def addStatement():
    # request data form frontend
    date = request.form["date"]
    name = request.form["name"]
    amount = request.form["amount"]
    category = request.form["category"]

    # add data to database
    statement = Statement(date = date, name = name, amount = amount, category = category)
    db.session.add(statement)
    db.session.commit()

    # show data when get form
    print(f"date {date} | name {name} | amount {amount} | category {category}")
    
    # redirect to main page
    return redirect("/")

#show data on database
@app.route("/")
def showData():
    statements = Statement.query.all()
    income = Statement.query.with_entities(Statement.amount).filter(Statement.category == "income").all()
    expense = Statement.query.with_entities(Statement.amount).filter(Statement.category == "expense").all()
    incomes = []
    expenses = []
    for i in income:
        for j in i:
            incomes.append(int(j))
    
    for i in expense:
        for j in i:
            expenses.append(int(j))
    
    totalIncome = functools.reduce(lambda x, y: x + y, incomes)
    totalExpense = functools.reduce(lambda x, y: x + y, expenses)
    total = totalIncome - totalExpense
    print(totalIncome, totalExpense, total)

    return render_template("statements.html", 
        statements = statements, 
        totalIncome = totalIncome,
        totalExpense = totalExpense,
        total = total
    )

# delete transaction
@app.route("/delete/<int:id>")
def deleteStatement(id):
    # only one column
    statement=Statement.query.filter_by(id=id).first()
    db.session.delete(statement)
    db.session.commit()
    return redirect("/")

# edit transaction
@app.route("/edit/<int:id>")
def editStatement(id):
    # only one column
    statement = Statement.query.filter_by(id=id).first()

    # get statement to edit page
    return render_template("editForm.html", statement=statement)

# # update transaction updateStatement
@app.route("/updateStatement",methods=['POST'])
def updateStatement():
    # request for edit 
    id = request.form["id"]
    date = request.form["date"]
    name = request.form["name"]
    amount = request.form["amount"]
    category = request.form["category"]

    # only one column and edit all
    statement=Statement.query.filter_by(id=id).first()
    statement.date=date
    statement.name=name 
    statement.amount = amount
    statement.category=category
    db.session.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)