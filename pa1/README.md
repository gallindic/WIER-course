# WIER-course

## Assignment 1

### Setting up DB with docker
1. Start Docker Desktop
2. From folder `pa1/db/docker` run `docker-compose up -d`
3. Run `docker inspect pg_container` and copy `IPAddress`
4. Visit pgAdmin on `localhost:5050`
5. Create a new server:
    - General tab: set name to "wier"
    - Connection tab: set host name/address to `IPAddress`, username to "root" and password to "root"
6. Create a new DB schema from the `crawldb.sql` file

### Setting DB connection
1. Open `pa1/db/db.ini`
2. Set host to match postgres host name/address (localhost, 172.20...)

### Installing dependencies
1. Run `pip install -r requirements.txt``

### Running crawler
1. `cd`into wier_course/pa1
2. Initialize frontier with `python main.py --initFrontier=1``
3. Run `python main.py --threads=4`