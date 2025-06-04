from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Estimate, Material, MaterialType, AdditionalCost  # Use absolute import for direct execution
import os
import io  # Add this import at the top
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estimates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'
db.init_app(app)

@app.route('/')
def index():
    estimates = Estimate.query.all()
    estimate_totals = {}
    
    for estimate in estimates:
        materials_total = sum(
            type.quantity * type.unit_price 
            for material in estimate.materials 
            for type in material.types
        )
        additional_costs_total = sum(cost.amount for cost in estimate.additional_costs)
        estimate_totals[estimate.id] = {
            'materials': materials_total,
            'additional_costs': additional_costs_total,
            'total': materials_total + additional_costs_total + estimate.labor_cost
        }
    
    return render_template('index.html', estimates=estimates, estimate_totals=estimate_totals)

@app.route('/create', methods=['GET', 'POST'])
def create_estimate():
    if request.method == 'POST':
        try:
            new_estimate = Estimate(
                project_title=request.form['project_title'],
                project_manager=request.form['project_manager'],
                project_location=request.form['project_location'],
                client_name=request.form['client_name'],
                project_address=request.form['project_address'],
                labor_cost=float(request.form['labor_cost']),
                estimate_date=datetime.now()
            )
            db.session.add(new_estimate)
            db.session.flush()

            materials = {}  # Dictionary to group materials
            items = request.form.getlist('item[]')
            colors = request.form.getlist('color[]')
            types = request.form.getlist('type[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')

            for i in range(len(items)):
                if items[i].strip():
                    item_name = items[i].strip()
                    if item_name not in materials:
                        material = Material(
                            name=item_name,
                            estimate_id=new_estimate.id
                        )
                        db.session.add(material)
                        db.session.flush()
                        materials[item_name] = material

                    material_type = MaterialType(
                        color=colors[i].strip(),
                        type=types[i].strip(),
                        quantity=int(quantities[i]),
                        unit_price=float(unit_prices[i]),
                        material_id=materials[item_name].id
                    )
                    db.session.add(material_type)

            # Add additional costs
            descriptions = request.form.getlist('cost_description[]')
            amounts = request.form.getlist('cost_amount[]')

            for desc, amount in zip(descriptions, amounts):
                if desc.strip() and amount:
                    cost = AdditionalCost(
                        description=desc.strip(),
                        amount=float(amount),
                        estimate_id=new_estimate.id
                    )
                    db.session.add(cost)

            db.session.commit()
            return redirect(url_for('view_estimate', estimate_id=new_estimate.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error creating estimate: {e}")
            return f"Error creating estimate: {str(e)}", 500

    return render_template('create_estimate.html')

@app.route('/view_estimate/<int:estimate_id>')
def view_estimate(estimate_id):
    estimate = Estimate.query.get_or_404(estimate_id)
    materials_total = sum(
        type.quantity * type.unit_price 
        for material in estimate.materials 
        for type in material.types
    )
    additional_costs_total = sum(cost.amount for cost in estimate.additional_costs)
    return render_template('view_estimate.html', 
                         estimate=estimate, 
                         materials_total=materials_total,
                         additional_costs_total=additional_costs_total)

@app.route('/download/<int:estimate_id>')
def download_pdf(estimate_id):
    estimate = Estimate.query.get_or_404(estimate_id)
    materials_total = sum(
        type.quantity * type.unit_price 
        for material in estimate.materials 
        for type in material.types
    )
    additional_costs_total = sum(cost.amount for cost in estimate.additional_costs)
    
    return render_template('print_view.html', 
                         estimate=estimate, 
                         materials_total=materials_total,
                         additional_costs_total=additional_costs_total,
                         single_estimate=True)

@app.route('/print_all')
def print_all_estimates():
    estimates = Estimate.query.all()
    estimate_totals = {}
    
    for estimate in estimates:
        materials_total = sum(
            type.quantity * type.unit_price 
            for material in estimate.materials 
            for type in material.types
        )
        additional_costs_total = sum(cost.amount for cost in estimate.additional_costs)
        estimate_totals[estimate.id] = {
            'materials': materials_total,
            'additional_costs': additional_costs_total,
            'total': materials_total + additional_costs_total + estimate.labor_cost
        }
    
    return render_template('print_view.html', 
                         estimates=estimates, 
                         estimate_totals=estimate_totals,
                         single_estimate=False)

@app.route('/delete_material/<int:material_id>')
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    estimate_id = material.estimate_id
    db.session.delete(material)
    db.session.commit()
    return redirect(url_for('view_estimate', estimate_id=estimate_id))

@app.route('/delete_material_type/<int:type_id>')
def delete_material_type(type_id):
    material_type = MaterialType.query.get_or_404(type_id)
    material_id = material_type.material_id
    material = Material.query.get(material_id)
    estimate_id = material.estimate_id
    
    db.session.delete(material_type)
    # If this was the last type for this material, delete the material too
    if len(material.types) <= 1:
        db.session.delete(material)
    
    db.session.commit()
    return redirect(url_for('view_estimate', estimate_id=estimate_id))

@app.route('/edit/<int:estimate_id>', methods=['GET', 'POST'])
def edit_estimate(estimate_id):
    estimate = Estimate.query.get_or_404(estimate_id)
    
    if request.method == 'POST':
        try:
            print("Form data received:", request.form)  # Debug logging
            
            # Update estimate details
            estimate.project_title = request.form.get('project_title', '')
            estimate.project_manager = request.form.get('project_manager', '')
            estimate.project_location = request.form.get('project_location', '')
            estimate.client_name = request.form.get('client_name', '')
            estimate.project_address = request.form.get('project_address', '')
            estimate.labor_cost = float(request.form.get('labor_cost', 0))

            # Delete existing material types and materials
            for material in estimate.materials:
                for type in material.types:
                    db.session.delete(type)
                db.session.delete(material)
            
            db.session.flush()

            # Add new materials
            materials = {}
            items = request.form.getlist('item[]')
            colors = request.form.getlist('color[]')
            types = request.form.getlist('type[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')

            print("Materials data:", list(zip(items, colors, types, quantities, unit_prices)))  # Debug logging

            for i in range(len(items)):
                if items[i].strip():
                    item_name = items[i].strip()
                    if item_name not in materials:
                        material = Material(
                            name=item_name,
                            estimate_id=estimate.id
                        )
                        db.session.add(material)
                        db.session.flush()
                        materials[item_name] = material

                    material_type = MaterialType(
                        color=colors[i].strip(),
                        type=types[i].strip(),
                        quantity=int(quantities[i]),
                        unit_price=float(unit_prices[i]),
                        material_id=materials[item_name].id
                    )
                    db.session.add(material_type)

            # Update additional costs
            for cost in estimate.additional_costs:
                db.session.delete(cost)

            descriptions = request.form.getlist('cost_description[]')
            amounts = request.form.getlist('cost_amount[]')

            for desc, amount in zip(descriptions, amounts):
                if desc.strip() and amount:
                    cost = AdditionalCost(
                        description=desc.strip(),
                        amount=float(amount),
                        estimate_id=estimate.id
                    )
                    db.session.add(cost)

            db.session.commit()
            return redirect(url_for('view_estimate', estimate_id=estimate.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating estimate: {e}")  # Debug logging
            return f"Error updating estimate: {str(e)}", 500

    # Calculate materials total for display
    materials_total = sum(
        type.quantity * type.unit_price 
        for material in estimate.materials 
        for type in material.types
    )
    
    return render_template('edit_estimate.html', estimate=estimate, materials_total=materials_total)

@app.route('/save_signature/<int:estimate_id>', methods=['POST'])
def save_signature(estimate_id):
    try:
        data = request.get_json()
        estimate = Estimate.query.get_or_404(estimate_id)
        estimate.signature = data['signature']
        estimate.signature_date = datetime.now()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")