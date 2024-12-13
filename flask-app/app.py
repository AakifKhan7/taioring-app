from flask import send_file, render_template, redirect, url_for, flash, request, abort
from forms import *
from model import *
from database import create_app
from datetime import timedelta, datetime
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = create_app()

@app.route('/')
def home():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    form = AddClient()
    if form.validate_on_submit():
        new_client = Client(
            name=form.name.data,
            street=form.street.data,
            city=form.city.data,
            phone_number=form.phone_number.data,
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully!')
    return render_template('add_client.html', form=form)

@app.route('/client/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/client/<int:client_id>/edit', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = EditClientForm(obj=client)
    if form.validate_on_submit():
        client.name = form.name.data
        client.street = form.street.data
        client.city = form.city.data
        client.phone_number = form.phone_number.data
        db.session.commit()
        return redirect(url_for('client_info', client_id=client.id))
    return render_template('edit_client.html', form=form, client=client)

@app.route('/client/<int:client_id>')
def client_info(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template('client_info.html', client=client)

@app.route('/client/<int:client_id>/add_order', methods=['GET', 'POST'])
def add_order(client_id):
    form = AddOrder()
    client = Client.query.get_or_404(client_id)
    if form.validate_on_submit():
        order_date = datetime.utcnow()
        deadline = order_date + timedelta(days=10)
        last_order = Order.query.filter_by(client_id=client.id).order_by(Order.order_number.desc()).first()
        next_order_number = last_order.order_number + 1 if last_order else 1
        new_order = Order(
            client_id=client.id,
            product_name=form.product_name.data,
            price=form.price.data,
            quantity=form.quantity.data,
            status="Pending",
            order_date=order_date,
            deadline=deadline,
            order_number=next_order_number,
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Order added successfully!', 'success')
        return redirect(url_for('client_info', client_id=client.id))
    return render_template('add_order.html', client=client, form=form)

@app.route('/order/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('client_info', client_id=order.client_id))

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = EditOrderForm()
    if form.validate_on_submit():
        order.product_name = form.product_name.data
        order.status = form.status.data
        order.price = form.price.data
        order.order_date = form.order_date.data
        order.deadline = form.deadline.data
        db.session.commit()
        flash('Order updated successfully!', 'success')
        return redirect(url_for('client_info', client_id=order.client_id))
    form.product_name.data = order.product_name
    form.status.data = order.status
    form.price.data = order.price
    form.order_date.data = order.order_date
    form.deadline.data = order.deadline
    return render_template('edit_order.html', form=form, order=order)

@app.route('/order/<int:order_id>')
def view_order(order_id):
    order = Order.query.filter_by(id=order_id).first_or_404()
    return render_template('view_order.html', order=order)

@app.route('/pending-orders', methods=["GET", "POST"])
def pending_orders():
    pending_orders = Order.query.filter_by(status='Pending').all()
    return render_template('pending_orders.html', orders=pending_orders)

@app.route('/orders', methods=['GET'])
def orders():
    current_year = int(request.args.get('year', datetime.now().year))
    month = request.args.get('month', None)
    if month:
        month = int(month)
        orders = Order.query.filter(
            db.extract('year', Order.order_date) == current_year,
            db.extract('month', Order.order_date) == int(month),
        ).all()
        total_earnings = db.session.query(db.func.sum(Order.price * Order.quantity)).filter(
            db.extract('year', Order.order_date) == current_year,
            db.extract('month', Order.order_date) == month,
            Order.status == 'Paid'
        ).scalar() or 0
    else:
        orders = []
        total_earnings = 0
    return render_template('all_orders.html', current_year=current_year, orders=orders, month=month, total_earnings=total_earnings)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        orders = Order.query.filter(
            (Order.product_name.ilike(f"%{query}%")) |
            (Order.client.has(Client.name.ilike(f"%{query}%"))) |
            (Order.status.ilike(f"%{query}%"))
        ).all()
    else:
        orders = Order.query.all()
    return render_template('search_results.html', orders=orders)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
