import json
import logging
import os

from flask import Flask, render_template, request, redirect

from db import DBService

from sql.queries import (
    add_childcare_limits,
    get_bottom_10_sales,
    get_actual_vs_predicted_revenue,
    get_categories,
    get_category_stats,
    get_revenue_by_population,
    get_childcare_sales_volume,
    get_childcare_categories,
    get_childcare_info,
    get_childcare_limits,
    get_holiday_names,
    get_outdoor_furniture,
    get_restaurant_impact_on_category_sales,
    get_states,
    get_store_revenue,
    get_top_10_sales,
    get_months,
    update_childcare,
    delete_childcare
)

logger = logging.getLogger(__name__)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    db_service = DBService()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.template_filter()
    def format_number(value):
        try:
            new_value = int(value)
            return "{:,}".format(new_value)
        except TypeError:
            return value

    @app.template_filter()
    def format_currency(value):
        try:
            new_value = float(value)
            return "{:,.2f}".format(new_value)
        except TypeError:
            return value

    @app.route('/')
    def main():
        return render_template('main.html')

    def get_holiday_data():
        db_service.cursor.execute("""
        SELECT * from Holiday;
        """
        )
        existing_holidays = db_service.cursor.fetchall()
        existing_holidays = [
            holiday[0].isoformat() + '/' + holiday[1].lower() for holiday in existing_holidays
        ]

        db_service.cursor.execute(get_holiday_names())
        existing_holiday_names = db_service.cursor.fetchall()
        existing_holiday_names = [
             holiday[0].lower() for holiday in existing_holiday_names
         ]
        return existing_holiday_names, existing_holidays

    @app.route('/holiday', methods=['GET', 'POST'])
    def holiday():
        existing_holiday_names, existing_holidays = get_holiday_data()
        db_service.cursor.execute("""
            SELECT max(date) max, min(date) min from Date;
            """)
        date_limit = db_service.cursor.fetchall()
        if request.method == 'POST':
            holiday_ = request.form['holiday']
            db_service.cursor.execute(f"""
            SELECT distinct date from Holiday
            where name = "{holiday_}";
            """)

            holiday_date = db_service.cursor.fetchall()

            return render_template(
                'holiday.html',
                holidayDate=holiday_date,
                holidays=existing_holiday_names,
                holiday=holiday_,
                existing_holidays=json.dumps(existing_holidays),
                date_limit=date_limit
            )

        else:
            return render_template(
                'holiday.html',
                holidays=existing_holiday_names,
                existing_holidays=json.dumps(existing_holidays),
                date_limit=date_limit
            )

    @app.route('/update-holiday', methods=['POST'])
    def update():
        if request.method == 'POST':
            datename = request.form['updated_holiday']
            holiday = request.form['old_holiday']
            db_service.cursor.execute(f"""
            UPDATE Holiday set name = "{datename}"
            where name = "{holiday}";
            """)

            db_service.connection.commit()
            return redirect('/holiday')

    @app.route('/add-holiday', methods=['POST'])
    def add_holiday():
        if request.method == 'POST':

            date = request.form['date']
            db_service.cursor.execute(get_holiday_names())

            new_holiday = request.form['new_holiday']
            db_service.cursor.execute(f"""
            INSERT INTO Holiday VALUES("{date}","{new_holiday}");
            """)
            db_service.connection.commit()
            return redirect('holiday')

    def get_childcare_data():
        db_service.cursor.execute(get_childcare_info())
        data = db_service.cursor.fetchall()

        db_service.cursor.execute(get_childcare_limits())
        limits = db_service.cursor.fetchall()
        limits = [limit[0] for limit in limits]
        limits.append(None)
        return data, limits

    @app.route('/childcare', methods=['GET', 'POST'])
    def childcare():
        data, limits = get_childcare_data()

        if request.method == "GET":
            return render_template(
                'childcare.html',
                stores=data,
                limits=limits,
                dump_limits=json.dumps(limits)
            )
        elif request.method == 'POST':

            updated_data = request.form
            new_data = []
            for store_id, limit in data:
                new_limit = updated_data[store_id] or None
                new_limit = None if new_limit == 'None' else int(new_limit)
                new_data.append([store_id, new_limit])
                if new_limit != limit:
                    # Update childcare
                    if new_limit is None:
                        db_service.cursor.execute(
                            delete_childcare(store_id)
                        )
                    else:
                        db_service.cursor.execute(
                            update_childcare(store_id, new_limit)
                        )

            db_service.connection.commit()
            return render_template(
                'childcare.html',
                stores=new_data,
                limits=limits,
                dump_limits=json.dumps(limits)
            )

    @app.route('/childcare-limit', methods=['POST'])
    def childcare_limit():
        updated_data = request.form['newLimit']
        db_service.cursor.execute(
            add_childcare_limits(int(updated_data))
        )
        db_service.connection.commit()
        data, limits = get_childcare_data()
        return render_template(
            'childcare.html', stores=data, limits=limits
        )

    @app.route('/population', methods=['GET', 'POST'])
    def population():
        db_service.cursor.execute("""
            SELECT DISTINCT NAME, STATE FROM CITY;
            """)
        cities = db_service.cursor.fetchall()
        if request.method == 'POST':
            city_state = request.form['city']

            city = city_state.split(",")[0]
            state = city_state.split(",")[1]

            db_service.cursor.execute(f"""
            select name, state, population from city
             where name = "{city}" and state = "{state}";
            """)

            city_info = db_service.cursor.fetchall()

            return render_template(
                'population.html',
                city_info=city_info,
                cities=cities,
                city=city
            )

        else:
            return render_template('population.html', cities=cities)

    @app.route('/update-population', methods=['POST'])
    def update_population():
        if request.method == 'POST':

            city = request.form['city']
            state = request.form['state']
            population_ = request.form['population']
            db_service.cursor.execute(f"""
            UPDATE City set population = {population_}
             where state = "{state}" and name = "{city}";
            """)

            db_service.connection.commit()
            return redirect('/population')

    @app.route('/stats')
    def stats():
        db_service.cursor.execute("""
            SELECT
                *
            FROM
                (SELECT COUNT(*) stores_count
            FROM
                store) a,
                (SELECT COUNT(*) stores_food_count
            FROM
                store WHERE (store.snack_bar = 1
                            OR store.restaurant = 1)) b,
                (SELECT COUNT(*) stores_childcare_count
            FROM
                Store WHERE childcare_time IS NOT NULL) c,
                (SELECT COUNT(*) products_count
            FROM
                product) d,
                (SELECT COUNT(DISTINCT name) campaigns_count
            FROM
                campaign) e;
            """)

        data = db_service.cursor.fetchall()
        return render_template('stats.html', data=data)

    @app.route('/report1')
    def report1():
        db_service.cursor.execute(get_categories())
        data = db_service.cursor.fetchall()
        return render_template('report1.html', data=data)

    @app.route('/report2')
    def report2():
        db_service.cursor.execute(get_actual_vs_predicted_revenue())

        data = db_service.cursor.fetchall()
        return render_template('report2.html', data=data)

    @app.route('/report3', methods=['GET', 'POST'])
    def report3():

        db_service.cursor.execute(get_states())
        states = db_service.cursor.fetchall()

        if request.method == 'POST':
            state = request.form['state']
            db_service.cursor.execute(get_store_revenue(state))

            data = db_service.cursor.fetchall()
            return render_template('report3.html',
                                   states=states, data=data, s=state)

        else:
            return render_template('report3.html', states=states)

    @app.route('/report4')
    def report4():
        db_service.cursor.execute(get_outdoor_furniture())

        data = db_service.cursor.fetchall()
        return render_template('report4.html', data=data)

    @app.route('/report5', methods=['GET', 'POST'])
    def report5():
        db_service.cursor.execute(get_months())
        months = db_service.cursor.fetchall()

        if request.method == 'POST':
            year, month = request.form['year_month'].split("/")
            db_service.cursor.execute(get_category_stats(year, month))

            data = db_service.cursor.fetchall()
            return render_template('report5.html', data=data, months=months,
                                   y=int(year), m=int(month))

        else:
            return render_template(
                'report5.html', months=months, y=None, m=None
            )

    @app.route('/report6')
    def report6():
        db_service.cursor.execute(get_revenue_by_population())
        data = db_service.cursor.fetchall()

        # For purpose of tabular data displayed in html
        small = 0
        medium = 0
        large = 0
        extra_large = 0
        tabular_data = []
        for i in range(len(data)):
            city_size = data[i][1]
            if city_size == "Small":
                small = data[i][2]
            elif city_size == "Medium":
                medium = data[i][2]
            elif city_size == "Large":
                large = data[i][2]
            else:
                extra_large = data[i][2]
            if i+1 == len(data):
                year_data = [data[i][0], small, medium, large, extra_large]
                tabular_data.append(year_data)
            elif data[i][0] != data[i+1][0]:
                year_data = [data[i][0], small, medium, large, extra_large]
                tabular_data.append(year_data)
                small = 0
                medium = 0
                large = 0
                extra_large = 0

        return render_template('report6.html', data=tabular_data)

    @app.route('/report7')
    def report7():
        db_service.cursor.execute(get_childcare_sales_volume())
        data = db_service.cursor.fetchall()
        db_service.cursor.execute(get_childcare_categories())
        category = db_service.cursor.fetchall()

        # For purpose of tabular data displayed in html
        category_list = []
        for row in category:
            category_list.append(row[0])
        tabular_data = []
        month_data = [0] * (len(category_list)+1)
        for i in range(len(data)):
            month_data[category_list.index(data[i][1])+1] = data[i][2]
            if i+1 == len(data):
                month_data[0] = data[i][0]
                tabular_data.append(month_data)
            elif data[i][0] != data[i+1][0]:
                month_data[0] = data[i][0]
                tabular_data.append(month_data)
                month_data = [0] * (len(category_list)+1)

        return render_template('report7.html', data=tabular_data,
                               category=category_list)

    @app.route('/report8')
    def report8():
        db_service.cursor.execute(get_restaurant_impact_on_category_sales())
        data = db_service.cursor.fetchall()

        # For purpose of row-span data displayed in html
        non_restaurant = 0
        restaurant = 0
        tabular_data = []
        for i in range(len(data)):
            if data[i][1] == "Non-restaurant":
                non_restaurant = data[i][2]
            else:
                restaurant = data[i][2]
            if i+1 == len(data):
                nr_list = ["Non-restaurant", non_restaurant]
                r_list = ["Restaurant", restaurant]
                category_data = [data[i][0], nr_list, r_list]
                tabular_data.append(category_data)
            elif data[i][0] != data[i+1][0]:
                nr_list = ["Non-restaurant", non_restaurant]
                r_list = ["Restaurant", restaurant]
                category_data = [data[i][0], nr_list, r_list]
                tabular_data.append(category_data)
                non_restaurant = 0
                restaurant = 0

        return render_template('report8.html', data=tabular_data)

    @app.route('/report9')
    def report9():
        db_service.cursor.execute(get_bottom_10_sales())
        bottom_10 = db_service.cursor.fetchall()
        db_service.cursor.execute(get_top_10_sales())
        top_10 = db_service.cursor.fetchall()

        return render_template('report9.html', bottom_data=bottom_10,
                               top_data=top_10)

    return app


if __name__ == '__main__':
    lsrs = create_app()
    lsrs.run()
