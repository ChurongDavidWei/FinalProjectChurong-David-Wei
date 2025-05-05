# FinalProjectChurong-David-Wei

# Discription
The project builds up an webapp on the structure of django, using alphavantage api to search for stock price, there is also a portfolio page which you can calculate you gain and loss with entering your holdings, also included a register and login system.

# How to install required libraries
run in terminal: pip install -r requirements.txt

# How to use this program
Run the following commands in terminal of the directry where manage.py is:
1. Create migration files  
python manage.py makemigrations  
2. Apply the migrations to the database   
python manage.py migrate   
3. Create a superuser for the admin site     
python manage.py createsuperuser   
4.Run the server     
python manage.py runserver

and the terminal will tell where the web app is, by default it will be 127.0.0.1:8000, open browser and go to that page

#MY WORDS
Finally I used alphavantage api but not yahoo finance, because yfinance has a strict request rate limit which will some times make the page not working porperly, but this alphavantage has a request time limit for the free version which I am using, 25 times a day.
