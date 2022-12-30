def get_categories():
    return """
        SELECT
            C.name,
            COUNT(P.pid) as count,
            MIN(P.retail_price),
            AVG(P.retail_price),
            MAX(P.retail_price)
        FROM
            Product AS P
                INNER JOIN
            ProductCategory AS PC ON P.pid = PC.product
                RIGHT JOIN
            Category AS C ON c.name = PC.category
        GROUP BY C.name;
        """


def get_actual_vs_predicted_revenue():
    return """
        with S as
        (
        select P.pid, P.name, P.retail_price, Sale.quantity, date
        from Sale
        inner join Product as P on Sale.product = P.pid
        inner join ProductCategory as PC on Sale.product = PC.product
        where category = "Couches and Sofas"
        )
        select *
        from
        (
        select A.pid as id, A.name,
        A.retail_price,
        A.total_sale,
        COALESCE(B.discount_sale, 0) as dsct_sale,
        A.total_sale - (select dsct_sale) as reta_sale,
        A.retail_price * (select reta_sale) + COALESCE(DRN, 0)
        as real_revenue,
        A.retail_price * (A.total_sale - (select dsct_sale) * 0.25)
        as predict_revenue,
        (select real_revenue - predict_revenue) as diff
        from
        (
        select S.pid, S.name, S.retail_price, sum(S.quantity) as total_sale
        from S
        group by S.pid
        ) as A
        left join
        (
        select
        S.pid, sum(S.quantity) as discount_sale,
        sum(D.discount_price * S.quantity) as DRN
        from S
        inner join Discount as D on S.date = D.date and S.pid = D.product
        group by S.pid
        ) as B
        on A.pid = B.pid
        ) as T
        where abs(diff) > 5000
        order by abs(diff) desc;
        """


def get_states():
    return """
         SELECT * FROM State;
    """


def get_store_revenue(state):
    return f"""
        with S as
        (
        select store, street_address, Store.city as city_name, date,
        quantity, retail_price, product
        from Sale
        inner join Product on Sale.product = Product.pid
        inner join Store on Sale.store = Store.store_number
        -- inner join City on Store.city = City.name and Store.state = City.state
        where Store.state = "{state}"
        )
        select M.store, M.street_address, M.city_name, M.year,
        COALESCE(RRN, 0) + COALESCE(DRN, 0) as revenue
        from
        (select distinct store, street_address, city_name, year(S.date) as year
        from S) as M
        left join
        (
        select store, year(S.date) as year, sum(retail_price *
        quantity) as RRN
        from S
        where not S.date in (select date from Discount D where D.product = S.product)
        group by year, store
        ) as A
        on M.year = A.year and M.store = A.store
        left join
        (
        select store, year(S.date) as year, sum(D.discount_price *
        quantity) as DRN
        from S
        inner join Discount as D on S.date = D.date and S.product =
        D.product
        group by year, store
        ) as B
        on M.year = B.year and M.store = B.store
        order by year, revenue desc;
        """


def get_outdoor_furniture():
    return """
        with S as(
        select date, quantity
        from Sale
        inner join ProductCategory as PC on Sale.product = PC.product
        where PC.category = "Outdoor Furniture")
        select
        A.Year, OF_sum, OF_avg, OF_GroundhogDay
        from
        (select
        year(date) as Year,
		sum(quantity) as OF_sum,
        sum(quantity)/365 as OF_avg
        from S
        group by Year) as A
        inner join
        (select
        year(date) as Year,
        sum(quantity) as OF_GroundhogDay
        from S
        where month(date) = 2 and day(date) = 2
        group by Year) as B
        on A.Year = B.Year
        order by A.Year;
        """


def get_months():
    return """
        SELECT DISTINCT YEAR(date) as Y, MONTH(date) as M
        FROM Date
        order by Y, M;
        """


def get_category_stats(year, month):
    return f"""
        with S as
        (
        select
        PC.category,
        Store.state,
        sum(Sale.quantity) as stateTotal
        from Sale
        inner join ProductCategory as PC on Sale.product = PC.product
        inner join Store on Sale.store = Store.store_number
        -- inner join City on Store.city = City.name and Store.state = City.state
        where year(date) = {year} and month(date) = {month}
        group by PC.category, Store.state
        )
        select S.category, S.state, S.stateTotal
        from S
        inner join
        (
        select max(stateTotal) as max_total, category
        from S
        group by category
        ) as T
        on S.stateTotal = T.max_total and S.category = T.category
        order by category;
        """


def get_revenue_by_population():
    return """
        with S as (
        select Sale.product, Sale.date, quantity, retail_price, discount_price,
        CASE WHEN population < 3700000 THEN 'Small'
        WHEN population >= 3700000 AND population < 6700000 THEN 'Medium'
        WHEN population >= 6700000 AND population < 9000000 THEN 'Large'
        WHEN population >= 9000000 THEN 'Extra Large'
        END AS city_size,
        case
        when discount_price is null
        then quantity * retail_price
        else quantity * discount_price
        end as revenue
        from Sale
        inner join Product on Sale.product = Product.pid
        inner join Store on Sale.store = Store.store_number
        inner join City on Store.city = City.name and Store.state = City.state
        left join Discount on Sale.product = Discount.product and Sale.date = Discount.date
        )
        select
        year(date) as Year,
        city_size,
        sum(revenue)
        from S
        group by Year, city_size
        order by Year;
        """


def get_childcare_sales_volume():
    return """
        WITH StoreSale AS (
            SELECT
                store_id,
                product_id,
                quantity,
                CASE WHEN discount_price IS NULL
                THEN retail_price
                ELSE discount_price
                END AS price,
                month
            FROM
            (
                SELECT
                    Sale.store AS store_id,
                    Sale.product AS product_id,
                    Sale.quantity,
                    Product.retail_price,
                    Discount.discount_price,
                    DATE_FORMAT(Sale.date, '%Y-%m') AS month
                FROM
                    Sale
                JOIN Product ON Sale.product = Product.pid
                LEFT JOIN Discount ON Sale.product = Discount.product
                AND Sale.date = Discount.date
                WHERE
                    Sale.date >= DATE_SUB(
                    (
                        SELECT
                            max(date)
                        FROM
                            date
                    ),
                        INTERVAL 11 MONTH
                    )
            ) AS t1
        )
        SELECT
            StoreSale.month,
            CASE WHEN childcare_time IS NULL
            THEN 'No childcare'
            ELSE childcare_time
            END AS category,
            SUM(StoreSale.quantity * StoreSale.price) AS total_sales
        FROM
            StoreSale
        INNER JOIN Store ON StoreSale.store_id = Store.store_number
        GROUP BY
            category,
            month
        ORDER BY
            month DESC,
            category;
        """


def get_childcare_categories():
    return """
        SELECT
            DISTINCT(
                CASE WHEN childcare_time IS NULL
                THEN 'No childcare'
                ELSE childcare_time END
            ) AS category
        FROM
            Store
        ORDER BY
            CAST(category AS UNSIGNED)
        """


def get_restaurant_impact_on_category_sales():
    return """
        SELECT 
            pc.category,
            CASE WHEN st.restaurant = 0 THEN 'Non-restaurant'
            ELSE 'Restaurant' END AS store_type,
            SUM(s.quantity) AS qty_sold
        FROM 
            Sale s
        INNER JOIN Product p ON s.product = p.pid
        INNER JOIN ProductCategory pc ON p.pid = pc.product
        INNER JOIN Store st ON s.store = st.store_number
        GROUP BY 
            pc.category, 
            st.restaurant
        ORDER BY 
            pc.category;
        """


def get_bottom_10_sales():
    return """
        with S as (
        select 
        Sale.product as product_id,
        store, Sale.date, quantity,
        DC.date as campaign_date
        from Sale 
        inner join Discount on Sale.date = Discount.date and Sale.product = Discount.product
        left join (select distinct date from Campaign) as DC on Sale.date = DC.date
        )
        select
        M.product_id,
        Product.name,
        coalesce(in_campaign, 0) as Sold_in_campaign,
        coalesce(out_campaign, 0) as Sold_out_campaign,
        coalesce(in_campaign, 0) - coalesce(out_campaign, 0) as Diff
        from (select distinct product_id from S) as M
        inner join Product on M.product_id = Product.pid
        left join
        (select
        product_id,
        sum(quantity) as out_campaign
        from S
        where campaign_date is null
        group by product_id
        ) as A
        on M.product_id = A.product_id
        left join
        (select
        product_id,
        sum(quantity) as in_campaign
        from S
        where not campaign_date is null
        group by product_id
        ) as B
        on M.product_id = B.product_id
        order by Diff
        limit 10;
        """


def get_top_10_sales():
    return """
        with S as (
        select 
        Sale.product as product_id,
        store, Sale.date, quantity,
        DC.date as campaign_date
        from Sale 
        inner join Discount on Sale.date = Discount.date and Sale.product = Discount.product
        left join (select distinct date from Campaign) as DC on Sale.date = DC.date
        )
        select
        M.product_id,
        Product.name,
        coalesce(in_campaign, 0) as Sold_in_campaign,
        coalesce(out_campaign, 0) as Sold_out_campaign,
        coalesce(in_campaign, 0) - coalesce(out_campaign, 0) as Diff
        from (select distinct product_id from S) as M
        inner join Product on M.product_id = Product.pid
        left join
        (select
        product_id,
        sum(quantity) as out_campaign
        from S
        where campaign_date is null
        group by product_id
        ) as A
        on M.product_id = A.product_id
        left join
        (select
        product_id,
        sum(quantity) as in_campaign
        from S
        where not campaign_date is null
        group by product_id
        ) as B
        on M.product_id = B.product_id
        order by Diff Desc
        limit 10;
        """


def get_childcare_info():
    return """SELECT
        s.store_number, s.childcare_time
        FROM
        Store s;
        """


def get_childcare_limits():
    return """
        SELECT time_limit FROM Childcare;
    """


def update_childcare(store_id, limit):
    return f"""
        UPDATE Store
        SET
        childcare_time = {limit} Where store_number = '{store_id}';
    """


def delete_childcare(store_id):
    return f"""
        UPDATE Store
        SET
        childcare_time = NULL Where store_number = '{store_id}';
    """
    

def add_childcare_limits(limit):
    return f"""
        Insert into Childcare (time_limit)
        values ({limit});
    """


def get_holiday_names():
    return """
        SELECT DISTINCT name FROM Holiday
    """


def get_holiday_dates():
    return """
      SELECT distinct date from Holiday;
      """