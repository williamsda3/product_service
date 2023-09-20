from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'  # SQLite database
db = SQLAlchemy(app)

# Define a Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    last_transaction = db.Column(db.Integer, nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'last_transaction' : self.last_transaction
        }

# Initialize the database
with app.app_context():
    db.create_all()

# Routes
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.as_dict() for product in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.as_dict())

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    product = Product(name=data['name'], price=data['price'], quantity=data['quantity'], last_transaction=data['last_transaction'])
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201

@app.route('/products/<int:product_id>/reduce/<int:quantity>', methods=['POST'])
def reduce_product(product_id, quantity):
    product = Product.query.get_or_404(product_id)
    if product:
        if quantity <= product.quantity:
            product.quantity -= quantity
            product.last_transaction = quantity
            db.session.commit()
            return jsonify(product.as_dict()), 200
        else:
            product.last_transaction = product.quantity
            product.quantity = 0
            db.session.commit()
            return jsonify({'message': f'Can only remove {product.quantity}'}), 201
    else:
        return jsonify({'error': 'Could not reduce product quantity'}), 400


    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
