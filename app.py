from flask import Flask, render_template, redirect, url_for, request, jsonify
import solar_calc as sc

app = Flask(__name__)

@app.route("/map")
def map_route():
    return render_template('map.html')

@app.route("/map/solar", methods=["POST"])
def map_solar():
    data = request.get_json()
    polygon_points = [(point['lng'], point['lat']) for point in data.get('polygon_points')]

    heat_array = sc.get_heat_points_in_polygon(polygon_points)  # Użyj nowej funkcji

    return jsonify({'heat_array': heat_array})

@app.route("/")
def landing_page():
    return render_template('index.html')

@app.route("/about")
def about_page():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/test")
def test():
    return render_template('mapView.html')

if __name__ == "__main__":
    app.run(debug=True)
