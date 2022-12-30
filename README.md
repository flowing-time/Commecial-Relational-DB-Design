# CS6400 Phase 3 

## Getting started
### Essential tools
* Python 3.8 (but Python version >= 3.6 should work)
* For MacOS
    * [XCode](https://developer.apple.com/xcode/)
* One of the IDEs
    * [VS Code](https://code.visualstudio.com/)
    * [PyCharm](https://www.jetbrains.com/pycharm/)
    

### Install
Clone repo and go to `Phase_3` directory
```
git clone https://github.gatech.edu/cs6400-2021-01-spring/cs6400-2021-01-Team048.git
cd Phase_3
```
Create a virtualenv and activate it:
```
python3 -m venv venv
. venv/bin/activate
```
For Windows:
```
py -3 -m venv venv
venv\Scripts\activate.bat
```
Install requirements:
```
pip install -r requirements.txt
```

### Interact with database
You can interact with the database through a `DBService` instance.

Call ipython in a terminal (do not forget to activate the virtualenv before this):
```
ipython
```
Create a `DBSerivce` instance:
```
from lsrs.db import DBService # from the top level directory
service = DBService()
```
If you do not have `cs6400_team048` table locally, you can create one by 
passing `create_database` argument:
```
service = DBService(create_database=True)
```
and add sample data from `sql/test_data_insert.sql` by:
```
service.insert_data()
```

[If access denied](#if-access-denied).

You can execute any SQL commands with `execute()`. For example,
```
service.cursor.execute("INSERT INTO A (B, C) ...")
service.cursor.commit() # for saving 
```


#### If access denied
If got the following error, you need to `GRANT ALL PRIVILEGES` on the database. 

```(1045, "Access denied for user 'user'@'localhost' (using password: NO)")```

From a terminal, access MySQL as root (need to enter pass word):
```
mysql -u root -p
```
Then,
```
CREATE USER 'user'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost';
```

### Running the app
From the top directory:
```
python lsrs/app.py 
```
Open http://127.0.0.1:5000 in a browser.

### Code styling
We follow [PEP8](https://www.python.org/dev/peps/pep-0008/), which is a style guild for Python code

Please run the following and make sure you do not see any complaints before opening a PR
```
python -m flake8 lsrs/
```

### Unit test
To run the unit test
```
python -m unittest test/test_db.py
```