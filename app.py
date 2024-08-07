

from flask import Flask, render_template, url_for, json, redirect
from flask_mysqldb import MySQL
from flask import request
import os

# Citation:-- We used the app.py file 
# from https://github.com/osu-cs340-ecampus/flask-starter-app/tree/master/bsg_people_app as a reference.
# The code was primarily copied, then modified to meet the needs of our app. Resource was accessed October
# 27 through December 5 2022. 


app = Flask(__name__)

app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
app.config["MYSQL_USER"] = "cs340_kolkmank"
app.config["MYSQL_PASSWORD"] = "5740"
app.config["MYSQL_DB"] = "cs340_kolkmank"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Routes
@app.route("/")
def home():
    return render_template("home.html")


# route for members page
@app.route("/Members", methods=["POST", "GET"])
def member():
    # Separate out the request methods, in this case this is for a POST
    if request.method == "POST":
        # fire off if user presses button to add a new member
        if request.form.get("Add_Member"):
            # grab user form inputs
            member_name = request.form["member_name"]
            membership_id = request.form["membership_id"]
            signed_waiver = request.form["signed_waiver"]
            is_belay_certified = request.form["is_belay_certified"]
            
            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # mySQL query to insert the new member
            if membership_id == "0":
                query = "INSERT INTO Members(member_name, membership_id, signed_waiver, is_belay_certified) VALUES (%s, NULL, %s, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_name, signed_waiver, is_belay_certified))
                cur.close()
            else:
                query = "INSERT INTO Members(member_name, membership_id, signed_waiver, is_belay_certified) VALUES (%s, %s, %s, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_name, membership_id, signed_waiver, is_belay_certified))
                cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to members page
            return redirect("/Members")

    # Grab members data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all the members in Members
        query = "SELECT Members.member_id, Members.member_name, Memberships.membership_name, Members.signed_waiver, Members.is_belay_certified FROM Members LEFT JOIN Memberships ON Members.membership_id = Memberships.membership_id;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # mySQL query to grab membership id data 
        query1 = "SELECT membership_id FROM Memberships ORDER BY membership_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query1)
        membership_data = cur.fetchall()

        # render members page passing our query data to the members template
        return render_template("members.j2", data=data, memberships=membership_data)
       
        
# route for search functionality to search for a member, gets user input for member name 
# to complete the search
@app.route("/search_members", methods=["POST"])
def search_members():
        member_name = request.form["Search_Member"]  
        # mySQL query to get member's information
        query = "SELECT * From Members WHERE member_name = %s;"
        cur = mysql.connection.cursor()
        cur.execute(query, (member_name,))
        mysql.connection.commit()
        data = cur.fetchall()
        # render search_members page passing our query data to the template
        return render_template("search_members.j2",data=data)
        
        
# route for delete functionality, deleting a member,
# passes the id value of the member on button click
@app.route("/delete_member/<int:id>")
def delete_member(id):
    # mySQL query to delete the member with our passed id
    query = "DELETE FROM Members WHERE member_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to members page
    return redirect("/Members")  

# route for edit functionality, updates the attributes of a member
# passes the id value of the member on button click 
@app.route("/edit_member/<int:id>", methods=["POST", "GET"])
def edit_member(id):
    if request.method == "GET":
        # mySQL query to grab the info of the member with our passed id
        query = "SELECT * FROM Members WHERE member_id = '%s'" % (id)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        
        # mySQL query to grab membership id/name data for our dropdown
        query2 = "SELECT membership_id, membership_name FROM Memberships ORDER BY membership_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        membership_data = cur.fetchall()    

        # render edit__members page and passes our query data to edit_members
        return render_template("edit_members.j2", data=data, memberships=membership_data)
    
    if request.method == "POST":
        # fire off if user clicks the edit member button
        if request.form.get("Edit_Member"):
            # grab user form inputs
            member_id = request.form["member_id"]
            member_name = request.form["member_name"]
            membership_id = request.form["membership_id"]
            signed_waiver = request.form["signed_waiver"]
            is_belay_certified = request.form["is_belay_certified"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # mySQL query to update the member with the user inputs
            if membership_id == "0":
                query = "UPDATE Members SET member_name = %s, membership_id = NULL, signed_waiver = %s, is_belay_certified = %s WHERE member_id = %s"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_name, signed_waiver, is_belay_certified, member_id))
                mysql.connection.commit()
                cur.close()
            else:
                query = "UPDATE Members SET member_name = %s, membership_id = %s, signed_waiver = %s, is_belay_certified = %s WHERE member_id = %s"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_name, membership_id, signed_waiver, is_belay_certified, member_id))
                mysql.connection.commit()
                cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # redirect back to the members page after we execute the update query
            return redirect("/Members")


# route for rental_orders page
@app.route("/Rental_Orders", methods=["POST", "GET"])
def rental_order():
    
    if request.method == "POST":
        # fire off if user presses the add rental_order button
        if request.form.get("Add_Rental_Order"):
            # grab user form inputs
            order_id = request.form["order_id"]
            rental_id = request.form["rental_id"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()
            # mySQL query to insert data into Rental_Orders
            query = "INSERT INTO Rental_Orders (order_id, rental_id) VALUES (%s, %s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (order_id, rental_id))
            cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to rental orders page
            return redirect("/Rental_Orders")

    # Grab Rental_Orders data so we can send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all of the orders in Rental_Orders
        query = "SELECT Rental_Orders.*, Rental_Equipment.rental_name FROM Rental_Orders LEFT JOIN Rental_Equipment ON Rental_Orders.rental_id = Rental_Equipment.rental_id;"
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

        # render rental orders page passing our query data to rental_orders
        return render_template("rental_orders.j2", data=data, orders = order_data, rentals=rental_data)
    

# route for delete functionality, deleting a rental order,
# passes the id value of the rental order on button click
@app.route("/delete_rentalorder/<int:id>")
def delete_rental_order(id):
    # mySQL query to delete the rental order with our passed id
    query = "DELETE FROM Rental_Orders WHERE rentalorder_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to Rental_Orders page
    return redirect("/Rental_Orders")


# route for edit functionality, updating the attributes of a rental order
# passes the id value of the rental on button click
@app.route("/edit_rentalorder/<int:id>", methods=["POST", "GET"])
def edit_rental_order(id):
    if request.method == "GET":
        # mySQL query to grab the info of the rental order with our passed id
        query = "SELECT * FROM Rental_Orders WHERE rentalorder_id = '%s'" % (id)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        
        # mySQL query to grab order id data for our dropdown
        query = "SELECT order_id FROM Orders ORDER BY order_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        order_data = cur.fetchall()

        # mySQL query to grab rental id/name data for our dropdown
        query = "SELECT rental_id, rental_name FROM Rental_Equipment;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        rental_data = cur.fetchall()        

        # render edit_rental_order page passing our query data to the edit_rentalorders page
        return render_template("edit_rentalorders.j2", data=data, orders = order_data, rentals = rental_data)
    
    if request.method == "POST":
        # fire off if user clicks the button to edit a rental order
        if request.form.get("Edit_Rental_Order"):
            # grab user form inputs
            rentalorder_id = request.form["rentalorder_id"]
            order_id = request.form["order_id"]
            rental_id = request.form["rental_id"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # mySQL query to update rental order with user form inputs
            query = "UPDATE Rental_Orders SET order_id = %s, rental_id = %s WHERE rentalorder_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (order_id, rental_id, rentalorder_id))
            mysql.connection.commit()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # redirect back to Rental_Orders page after we execute the update query
            return redirect("/Rental_Orders")

# route for memberships page
@app.route("/Memberships", methods=["POST", "GET"])
def membership():
    # Separate out the request methods, in this case this is for a POST

    if request.method == "POST":
        # fire off if user presses the button to add a membership
        if request.form.get("Add_Membership"):
            # grab user form inputs
            membership_name = request.form["membership_name"]
            membership_cost = request.form["membership_cost"]
            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()
            
            # mySQL query to insert a membership into the Memberhips entity
            query = "INSERT INTO Memberships (membership_name, membership_cost) VALUES (%s, %s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (membership_name, membership_cost))
            cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to Memberships page
            return redirect("/Memberships")

    # Grab membership data so to sent to template to display
    if request.method == "GET":
        # mySQL query to grab all the memberhips
        query = "SELECT * FROM Memberships;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # render memberships page passing our query data
        return render_template("memberships.j2", data=data)
    

# route for delete functionality, deleting a membership,
# we want to pass the id value of that membership on button click 
@app.route("/delete_membership/<int:id>")
def delete_membership(id):
    # mySQL query to delete the membership with our passed id
    query = "DELETE FROM Memberships WHERE membership_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to the Memberships page
    return redirect("/Memberships")


# route for employees page
@app.route("/Employees", methods=["POST", "GET"])
def employee():
    # insert a person into the Employees entity
    if request.method == "POST":
        # fire off if user presses the button to add an employee
        if request.form.get("Add_Employee"):
            # grab user form inputs
            employee_name = request.form["employee_name"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()
            # mySQL query to add an employee with the user input
            query = "INSERT INTO Employees (employee_name) VALUES (%s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (employee_name,))
            cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to Employees page
            return redirect("/Employees")

    # Grab Employees data so we can send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all of the Employees
        query = "SELECT * FROM Employees;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # render employees page passing our query data
        return render_template("employees.j2", data=data)
    

# route for delete functionality, deleting a rental order,
# passes ID value of that employee on button click 
@app.route("/delete_employee/<int:id>")
def delete_employee(id):
    # mySQL query to delete the employee with our passed id
    query = "DELETE FROM Employees WHERE employee_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to the Employees page
    return redirect("/Employees")


# route for rental_equipment page
@app.route("/Rental_Equipment", methods=["POST", "GET"])
def rental_equipment():
    # insert rental equipment into the Rental_Equipment entity
    if request.method == "POST":
        # fire off if user presses the button to add equipment
        if request.form.get("Add_Rental_Equipment"):
            # grab user form inputs
            rental_name = request.form["rental_name"]
            rental_cost = request.form["rental_cost"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()
            # mySQL query to insert new rental_equipment with user inputs
            query = "INSERT INTO Rental_Equipment (rental_name, rental_cost) VALUES (%s,%s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (rental_name, rental_cost))
            cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to Rental_Equipment page
            return redirect("/Rental_Equipment")

    # Grab Rental_Equipment data so we send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all of the data from Rental_Equipment
        query = "SELECT * FROM Rental_Equipment;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # render rental_equipment page passing our query data
        return render_template("rental_equipment.j2", data=data)
    

# route for delete functionality, deleting a rental equipment,
# passes the id value of that rental equipment on button click
@app.route("/delete_rental_equipment/<int:id>")
def delete_rental_equipment(id):
    # mySQL query to delete the rental equipment with our passed id
    query = "DELETE FROM Rental_Equipment WHERE rental_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to the Rental_Equipment page
    return redirect("/Rental_Equipment")


# route for the Orders page
@app.route("/Orders", methods=["POST", "GET"])
def order():
    if request.method == "POST":
        # fire off if user presses the button to add an order
        if request.form.get("Add_Order"):
            # grab user form inputs
            member_id = request.form["member_id"]
            membership_id = request.form["membership_id"]
            employee_id = request.form["employee_id"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()
            # mySQL query to add a new order with the user inputs 
            if membership_id == "0":
                query = "INSERT INTO Orders (member_id, membership_id, employee_id) VALUES (%s, NULL, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_id, employee_id))
                cur.close()
            else:
                query = "INSERT INTO Orders (member_id, membership_id, employee_id) VALUES (%s, %s, %s);"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_id, membership_id, employee_id))
                cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            mysql.connection.commit()

            # redirect back to the Orders page
            return redirect("/Orders")

    # Grab Orders data so we can send it to our template to display
    if request.method == "GET":
        # mySQL query to grab all the orders in Orders
        query = "SELECT Orders.order_id, Members.member_name, Memberships.membership_name, Employees.employee_name FROM Orders LEFT JOIN Memberships ON Orders.membership_id = Memberships.membership_id LEFT JOIN Members ON Orders.member_id = Members.member_id LEFT JOIN Employees ON Orders.employee_id = Employees.employee_id;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # mySQL query to grab member id/name data for our dropdown
        query1 = "SELECT member_id, member_name FROM Members ORDER BY member_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query1)
        member_data = cur.fetchall()

        # mySQL query to grab membership id/name data for our dropdown
        query2 = "SELECT membership_id, membership_name FROM Memberships ORDER BY membership_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        membership_data = cur.fetchall()

        # mySQL query to grab employee id/name data for our dropdown
        query3 = "SELECT * FROM Employees ORDER BY employee_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query3)
        employee_data = cur.fetchall()

        # render orders page passing our query data and additional datas to the order template
        return render_template("orders.j2", data=data, members = member_data, memberships=membership_data, employees=employee_data)
    
# a route to expand order info
@app.route("/view_order/<int:id>")
def view_order(id):
    # mySQL query to select expanded order info based on id
    query = "SELECT Orders.*, Members.member_name, Memberships.membership_name, Memberships.membership_cost, Employees.employee_name FROM Orders LEFT JOIN Memberships ON Orders.membership_id = Memberships.membership_id LEFT JOIN Members ON Orders.member_id = Members.member_id LEFT JOIN Employees ON Orders.employee_id = Employees.employee_id WHERE Orders.order_id = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    data = cur.fetchall()
    return render_template("view_orders.j2", data = data)

#  route for delete functionality, deleting an order,
#  passes the ID value of that order on button click 
@app.route("/delete_order/<int:id>")
def delete_order(id):
    # mySQL query to delete the order with our passed id
    query = "DELETE FROM Orders WHERE order_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    # redirect back to the Orders page
    return redirect("/Orders")

# route for edit functionality, updating the attributes of an order in orders
# passes the ID value of that order on button click
@app.route("/edit_order/<int:id>", methods=["POST", "GET"])
def edit_order(id):
    if request.method == "GET":
        # mySQL query to grab the info of the order with our passed id
        query = "SELECT * FROM Orders WHERE order_id = '%s'" % (id)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        
        # mySQL query to grab member id/name data for our dropdown
        query1 = "SELECT member_id, member_name FROM Members ORDER BY member_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query1)
        member_data = cur.fetchall()

        # mySQL query to grab membership id/name data for our dropdown
        query2 = "SELECT membership_id, membership_name FROM Memberships ORDER BY membership_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        membership_data = cur.fetchall()

        # mySQL query to grab employee id/name data for our dropdown
        query3 = "SELECT * FROM Employees ORDER BY employee_id ASC;"
        cur = mysql.connection.cursor()
        cur.execute(query3)
        employee_data = cur.fetchall()       

        # render edit__order page passing our query data to the edit_orders page
        return render_template("edit_orders.j2", data=data, members = member_data, memberships=membership_data, employees=employee_data)
    
    if request.method == "POST":
        # fire off if user clicks button to edit and order
        if request.form.get("Edit_Order"):
            # grab user form inputs
            order_id = request.form["order_id"]
            member_id = request.form["member_id"]
            membership_id = request.form["membership_id"]
            employee_id = request.form["employee_id"]

            query = "SET FOREIGN_KEY_CHECKS=0;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # mySQL query to edit an order with the user form inputs
            if membership_id == "0":
                query = "UPDATE Orders SET member_id = %s, membership_id = NULL, employee_id = %s WHERE order_id = %s"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_id, employee_id, order_id))
                mysql.connection.commit()
                cur.close()
            else:
                query = "UPDATE Orders SET member_id = %s, membership_id = %s, employee_id = %s WHERE order_id = %s"
                cur = mysql.connection.cursor()
                cur.execute(query, (member_id, membership_id, employee_id, order_id))
                mysql.connection.commit()
                cur.close()

            query = "SET FOREIGN_KEY_CHECKS=1;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            cur.close()

            # redirect back to orders page after we execute the update query
            return redirect("/Orders")

# Listener
# change the port number if deploying on the flip servers
if __name__ == "__main__":
    app.run(port=8976, debug=True)
