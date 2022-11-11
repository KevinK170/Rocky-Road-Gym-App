from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
import os

# We are using the bsg_people app template from https://github.com/osu-cs340-ecampus/flask-starter-app/tree/master/bsg_people_app
# Configuration

app = Flask(__name__)

app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
app.config["MYSQL_USER"] = "cs340_kolkmank"
app.config["MYSQL_PASSWORD"] = "5740"
app.config["MYSQL_DB"] = "cs340_kolkmank"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Routes
# have homepage route to /people by default for convenience, generally this will be your home route with its own template
@app.route("/")
def home():
    return redirect("/Rental_Orders")


# route for people page
@app.route("/Rental_Orders", methods=["POST", "GET"])
def rental_order():
    # Separate out the request methods, in this case this is for a POST
    # insert a person into the bsg_people entity
    if request.method == "POST":
        # fire off if user presses the Add Person button
        if request.form.get("Add_Rental_Order"):
            # grab user form inputs
            order_id = request.form["order_id"]
            rental_id = request.form["rental_id"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            query = "INSERT INTO Rental_Orders (order_id, rental_id) VALUES (%s, %s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (order_id, rental_id))
            cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to people page
            return redirect("/Rental_Orders")

    # Grab Rental_Orders data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all the orders in Rental_Orders
        query = "SELECT * FROM Rental_Orders;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # mySQL query to grab order id data for our dropdown
        query1 = "SELECT order_id FROM Orders ORDER BY order_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query1)
        order_data = cur.fetchall()

        # mySQL query to grab rental id/name data for our dropdown
        query2 = "SELECT rental_id, rental_name FROM Rental_Equipment;"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        rental_data = cur.fetchall()

        # render edit_people page passing our query data and homeworld data to the edit_people template
        return render_template("rental_orders.j2", data=data, orders = order_data, rentals=rental_data)
    

# # route for delete functionality, deleting a rental order,
# # we want to pass the 'id' value of that order on button click (see HTML) via the route
@app.route("/delete_rentalorder/<int:id>")
def delete_people(id):
    # mySQL query to delete the person with our passed id
    query = "DELETE FROM Rental_Orders WHERE rentalorder_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to people page
    return redirect("/Rental_Orders")


# # route for edit functionality, updating the attributes of a person in bsg_people
# # similar to our delete route, we want to the pass the 'id' value of that person on button click (see HTML) via the route
@app.route("/edit_rentalorder/<int:id>", methods=["POST", "GET"])
def edit_rental_order(id):
    if request.method == "GET":
        # mySQL query to grab the info of the rental order with our passed id
        query = "SELECT * FROM Rental_Orders WHERE rentalorder_id = '%s'" % (id)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        
         # mySQL query to grab order id data for our dropdown
        query1 = "SELECT order_id FROM Orders ORDER BY order_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query1)
        order_data = cur.fetchall()

        # mySQL query to grab rental id/name data for our dropdown
        query2 = "SELECT rental_id, rental_name FROM Rental_Equipment;"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        rental_data = cur.fetchall()        

        # render edit_rental_order page passing our query data to the edit_rental_order
        return render_template("rental_orders.j2", data=data, orders = order_data, rentals=rental_data)

    # meat and potatoes of our update functionality
    if request.method == "POST":
        # fire off if user clicks the 'Edit Rental Order' button
        if request.form.get("Edit_Rental_Order"):
            # grab user form inputs
            id = request.form["rentalorder_id"]
            orderID = request.form["order_id"]
            rentalID = request.form["rental_id"]
            
            query = "UPDATE Rental_Orders SET rental_id = '%s', order_id = '%s' WHERE rentalorder_id = '%s';"
            cur = mysql.connection.cursor()
            cur.execute(query, (orderID, rentalID, id))
            mysql.connection.commit()
            
            # redirect back to people page after we execute the update query
            return redirect("/Rental_Orders")

# Listener
# change the port number if deploying on the flip servers
if __name__ == "__main__":
    app.run(port=6535, debug=True)
